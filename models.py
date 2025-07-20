from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from database import Base
from sqlalchemy.orm import relationship


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    precio = Column(Float)
    stock = Column(Integer)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rol = Column(String, default="cliente") # 👈 agregamos el rol
    carrito = relationship("CarritoItem", back_populates="usuario")
    compras = relationship("Compra", back_populates="usuario")


class CarritoItem(Base):
    __tablename__ = "carrito_items"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, default=1)
    usuario = relationship("Usuario", back_populates="carrito")
    producto = relationship("Producto")  # Esto está bien, no requiere back_populates si no lo usás desde Producto

class Compra(Base):
    __tablename__ = "compras"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha = Column(String)
    total = Column(Float)

    usuario = relationship("Usuario", back_populates="compras")
    items = relationship("CompraItem", back_populates="compra")


class CompraItem(Base):
    __tablename__ = "compra_items"
    id = Column(Integer, primary_key=True, index=True)
    compra_id = Column(Integer, ForeignKey("compras.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer)
    precio_unitario = Column(Float)

    compra = relationship("Compra", back_populates="items")
    producto = relationship("Producto")

