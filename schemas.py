from pydantic import BaseModel

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

class Token(BaseModel):
    access_token: str
    token_type: str
