import datetime
from http.client import HTTPException

from sqlalchemy.orm import Session

import models
import schemas
import auth
from models import CarritoItem


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
    db_usuario = models.Usuario(username=usuario.username, email=usuario.email, hashed_password=hashed_pw, rol="cliente")
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def agregar_item_carrito(db: Session, user_id: int, item: schemas.CarritoItemCreate):
    nuevo_item = models.CarritoItem(
        usuario_id=user_id,
        producto_id=item.producto_id,
        cantidad=item.cantidad
    )
    db.add(nuevo_item)
    db.commit()
    db.refresh(nuevo_item)
    return nuevo_item

def get_carrito_usuario(db: Session, usuario_id: int):
    return db.query(CarritoItem).filter(CarritoItem.usuario_id == usuario_id).all()

def eliminar_item_carrito(db: Session, user_id: int, producto_id: int):
    item = db.query(models.CarritoItem).filter_by(usuario_id=user_id, producto_id=producto_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado en el carrito")
    db.delete(item)
    db.commit()
    return {"mensaje": "Producto eliminado del carrito"}

def vaciar_carrito(db: Session, user_id: int):
    items = db.query(models.CarritoItem).filter_by(usuario_id=user_id).all()
    if not items:
        return {"mensaje": "El carrito ya está vacío"}
    for item in items:
        db.delete(item)
    db.commit()
    return {"mensaje": "Carrito vaciado correctamente"}

def realizar_compra(db: Session, usuario_id: int):
    carrito_items = db.query(models.CarritoItem).filter_by(usuario_id=usuario_id).all()
    if not carrito_items:
        raise HTTPException(status_code=400, detail="El carrito está vacío")

    total = sum(item.producto.precio * item.cantidad for item in carrito_items)

    compra = models.Compra(
        usuario_id=usuario_id,
        fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total=total
    )
    db.add(compra)
    db.flush()  # para obtener el ID

    for item in carrito_items:
        compra_item = models.CompraItem(
            compra_id=compra.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.producto.precio
        )
        db.add(compra_item)
        db.delete(item)

    db.commit()
    db.refresh(compra)
    return compra

def get_historial_compras(db: Session, usuario_id: int) -> list[schemas.CompraConItemsOut]:
    compras = db.query(models.Compra).filter(models.Compra.usuario_id == usuario_id).all()
    resultado = []

    for compra in compras:
        items_con_nombre = []
        for item in compra.items:
            producto = db.query(models.Producto).filter(models.Producto.id == item.producto_id).first()
            items_con_nombre.append(
                schemas.CompraItemConNombre(
                    producto_id=item.producto_id,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    nombre=producto.nombre
                )
            )
        resultado.append(
            schemas.CompraConItemsOut(
                id=compra.id,
                fecha=compra.fecha,
                total=compra.total,
                items=items_con_nombre
            )
        )

    return resultado
