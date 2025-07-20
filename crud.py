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
