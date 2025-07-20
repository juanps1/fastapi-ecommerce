from sqlalchemy.orm import Session
import models, schemas

def get_productos(db: Session):
    return db.query(models.Producto).all()

def create_producto(db: Session, producto: schemas.ProductoCreate):
    db_producto = models.Producto(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

def get_usuario_por_username(db: Session, username: str):
    return db.query(models.Usuario).filter(models.Usuario.username == username).first()

def crear_usuario(db: Session, usuario: schemas.UsuarioCreate):
    hashed_pw = auth.hashear_password(usuario.password)
    db_usuario = models.Usuario(username=usuario.username, email=usuario.email, hashed_password=hashed_pw)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario
