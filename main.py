from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import models, schemas, crud, auth
from database import SessionLocal, engine

logging.basicConfig(level=logging.DEBUG)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
# 📦 DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔐 Auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
@app.get("/", response_class=HTMLResponse)
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_usuario_por_username(db, username)
    if user is None:
        raise credentials_exception
    return user

def verificar_admin(current_user: schemas.UsuarioOut = Depends(get_current_user)):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden realizar esta acción")
    return current_user

# 👤 Registro y Login
@app.post("/register", response_model=schemas.UsuarioOut)
def register(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    if crud.get_usuario_por_username(db, usuario.username):
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return crud.crear_usuario(db, usuario)

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_usuario_por_username(db, form_data.username)
    if not user or not auth.verificar_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = auth.crear_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# 🛍 Productos
@app.get("/productos", response_model=list[schemas.ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    return crud.get_productos(db)

@app.post("/productos", response_model=schemas.ProductoOut)
def crear_producto(
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(verificar_admin)
):
    return crud.create_producto(db, producto)

# ⚙️ Admin utils
@app.get("/hacer_admin/{username}")
def hacer_admin(username: str, db: Session = Depends(get_db)):
    user = crud.get_usuario_por_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.rol = "admin"
    db.commit()
    return {"mensaje": f"{username} ahora es admin"}

# 🛒 Carrito
@app.post("/carrito", response_model=schemas.CarritoItemOut)
def agregar_al_carrito(
    item: schemas.CarritoItemCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    return crud.agregar_item_carrito(db, current_user.id, item)

@app.get("/carrito", response_model=list[schemas.CarritoItemOut])
def ver_carrito(
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    return crud.get_carrito_usuario(db, current_user.id)

@app.delete("/carrito/{producto_id}")
def eliminar_carrito_item(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    return crud.eliminar_item_carrito(db, current_user.id, producto_id)

@app.delete("/carrito")
def vaciar_carrito(
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    return crud.vaciar_carrito(db, current_user.id)

@app.post("/comprar", response_model=schemas.CompraOut)
def comprar(
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    return crud.realizar_compra(db, current_user.id)

@app.get("/compras", response_model=list[schemas.CompraConItemsOut])
def historial_compras(
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    return crud.get_historial_compras(db, current_user.id)

@app.get("/productos/html", response_class=HTMLResponse)
def ver_productos(request: Request):
    return templates.TemplateResponse("productos.html", {"request": request})

@app.get("/api/productos")
def get_productos(db: Session = Depends(get_db)):
    return crud.get_all_productos(db)
