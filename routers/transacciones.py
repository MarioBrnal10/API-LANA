from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from DB.conexion import get_db
from models.modelsDB import Transaccion
from modelsPydantic import Transaccion as TransaccionPydantic

routerTransacciones = APIRouter()

# 🔹 Obtener todas las transacciones
@routerTransacciones.get("/transacciones", response_model=List[TransaccionPydantic], tags=["Transacciones"])
def get_transacciones(db: Session = Depends(get_db)):
    return db.query(Transaccion).all()

# 🔹 Obtener transacción por ID
@routerTransacciones.get("/transacciones/{id}", response_model=TransaccionPydantic, tags=["Transacciones"])
def get_transaccion(id: int, db: Session = Depends(get_db)):
    transaccion = db.query(Transaccion).filter(Transaccion.id == id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return transaccion

# 🔹 Crear nueva transacción
@routerTransacciones.post("/transacciones", response_model=TransaccionPydantic, tags=["Transacciones"])
def crear_transaccion(data: TransaccionPydantic, db: Session = Depends(get_db)):
    try:
        nueva = Transaccion(
            usuario_id=data.usuario_id,
            cuenta_id=data.cuenta_id,
            categoria_id=data.categoria_id,
            monto=data.monto,
            tipo=data.tipo,
            descripcion=data.descripcion,
            fecha=data.fecha,
            creado_en=datetime.now()
        )
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return nueva
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear transacción: {str(e)}")
    finally:
        db.close()

# 🔹 Actualizar transacción
@routerTransacciones.put("/transacciones/{id}", response_model=TransaccionPydantic, tags=["Transacciones"])
def actualizar_transaccion(id: int, data: TransaccionPydantic, db: Session = Depends(get_db)):
    try:
        transaccion = db.query(Transaccion).filter(Transaccion.id == id).first()
        if not transaccion:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")

        transaccion.usuario_id = data.usuario_id
        transaccion.cuenta_id = data.cuenta_id
        transaccion.categoria_id = data.categoria_id
        transaccion.monto = data.monto
        transaccion.tipo = data.tipo
        transaccion.descripcion = data.descripcion
        transaccion.fecha = data.fecha

        db.commit()
        db.refresh(transaccion)
        return transaccion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar transacción: {str(e)}")
    finally:
        db.close()

# 🔹 Eliminar transacción
@routerTransacciones.delete("/transacciones/{id}", tags=["Transacciones"])
def eliminar_transaccion(id: int, db: Session = Depends(get_db)):
    try:
        transaccion = db.query(Transaccion).filter(Transaccion.id == id).first()
        if not transaccion:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        db.delete(transaccion)
        db.commit()
        return JSONResponse(content={"message": "Transacción eliminada exitosamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar transacción: {str(e)}")
    finally:
        db.close()
