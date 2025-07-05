from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from datetime import datetime
from DB.conexion import get_db  # debe estar configurado en tu app
from models.modelsDB import Transaccion, Categoria, Presupuesto  # tus modelos SQLAlchemy

routerGrafica = APIRouter()


@routerGrafica.get("/grafica/{usuario_id}", tags=["Grafica"])
def obtener_grafica_por_categoria(usuario_id: int, db: Session = Depends(get_db)):
    resultados = db.execute(text("""
    SELECT c.nombre, c.tipo, SUM(t.monto) as total
    FROM transacciones t
    JOIN categorias c ON t.categoria_id = c.id
    WHERE t.usuario_id = :usuario_id
    GROUP BY c.id
"""), {"usuario_id": usuario_id})


    data = {"ingresos": [], "egresos": []}

    for row in resultados:
        if row.tipo == "ingreso":
            data["ingresos"].append({"categoria": row.nombre, "total": float(row.total)})
        else:
            data["egresos"].append({"categoria": row.nombre, "total": float(row.total)})

    return data
