from pydantic import BaseModel

# ------------------- Productos -------------------

class ProductoBase(BaseModel):
    nombre: str
    precio: float
    stock: int

class ProductoCreate(ProductoBase):
    pass

class ProductoOut(ProductoBase):
    id: int

    class Config:
        from_attributes = True

# ------------------- Usuarios -------------------

class UsuarioCreate(BaseModel):
    username: str
    email: str
    password: str

class UsuarioOut(BaseModel):
    id: int
    username: str
    email: str
    rol: str

    class Config:
        orm_mode = True

# ------------------- Token -------------------

class Token(BaseModel):
    access_token: str
    token_type: str

# ------------------- Carrito -------------------

class CarritoItemBase(BaseModel):
    producto_id: int
    cantidad: int

class CarritoItemCreate(CarritoItemBase):
    pass

class CarritoItemOut(CarritoItemBase):
    id: int
    producto: ProductoOut

    class Config:
        from_attributes = True

# ------------------- Compras -------------------

class CompraItemOut(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float

    class Config:
        orm_mode = True

class CompraOut(BaseModel):
    id: int
    fecha: str
    total: float
    items: list[CompraItemOut]

    class Config:
        orm_mode = True

class CompraItemConNombre(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float
    nombre: str

    class Config:
        orm_mode = True

class CompraConItemsOut(BaseModel):
    id: int
    fecha: str
    total: float
    items: list[CompraItemConNombre]

    class Config:
        orm_mode = True
