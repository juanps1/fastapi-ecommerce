from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Modelo base
class Producto(BaseModel):
    nombre: str
    precio: float
    stock: int

# Simulación de base de datos en memoria
productos: List[Producto] = []

# ✅ GET - Listar productos
@app.get("/productos")
def listar_productos():
    return productos

# ✅ POST - Crear producto
@app.post("/productos")
def crear_producto(producto: Producto):
    productos.append(producto)
    return {"mensaje": "Producto agregado", "producto": producto}

# ✅ PUT - Editar producto (por índice)
@app.put("/productos/{indice}")
def actualizar_producto(indice: int, producto: Producto):
    if indice >= len(productos):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    productos[indice] = producto
    return {"mensaje": "Producto actualizado", "producto": producto}

# ✅ DELETE - Eliminar producto
@app.delete("/productos/{indice}")
def eliminar_producto(indice: int):
    if indice >= len(productos):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    eliminado = productos.pop(indice)
    return {"mensaje": "Producto eliminado", "producto": eliminado}
