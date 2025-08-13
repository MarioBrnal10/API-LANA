from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from DB.conexion import get_db

routerGrafica = APIRouter()

@routerGrafica.get("/grafica/{usuario_id}", tags=["Grafica"]) 
def obtener_grafica_por_categoria(usuario_id: int, db: Session = Depends(get_db)):
    resultados = db.execute(text("""
        SELECT c.nombre AS nombre, c.tipo AS tipo, SUM(t.monto) AS total
        FROM transacciones t
        JOIN categorias c ON t.categoria_id = c.id
        WHERE t.usuario_id = :usuario_id
        GROUP BY c.id, c.nombre, c.tipo
    """), {"usuario_id": usuario_id})

    data = {"ingresos": [], "egresos": []}

    for row in resultados:
        item = {"categoria": row.nombre, "total": float(row.total)}
        if row.tipo == "ingreso":
            data["ingresos"].append(item)
        else:
            data["egresos"].append(item)

    return data
