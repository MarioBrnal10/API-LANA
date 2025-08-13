# 📂 routers/transacciones.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from DB.conexion import get_db
from models.modelsDB import Transaccion
from modelsPydantic import TransaccionCreate, TransaccionUpdate, TransaccionOut

routerTransacciones = APIRouter()

# 🔹 Obtener todas las transacciones
@routerTransacciones.get("/transacciones", response_model=List[TransaccionOut], tags=["Transacciones"])
def get_transacciones(db: Session = Depends(get_db)):
    try:
        return db.query(Transaccion).order_by(Transaccion.id.desc()).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar transacciones: {str(e)}")
    finally:
        db.close()

# 🔹 Obtener transacción por ID
@routerTransacciones.get("/transacciones/{id}", response_model=TransaccionOut, tags=["Transacciones"])
def get_transaccion(id: int, db: Session = Depends(get_db)):
    try:
        transaccion = db.query(Transaccion).filter(Transaccion.id == id).first()
        if not transaccion:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        return transaccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacción: {str(e)}")
    finally:
        db.close()

# 🔹 Crear nueva transacción
@routerTransacciones.post("/transacciones", response_model=TransaccionOut, tags=["Transacciones"])
def crear_transaccion(data: TransaccionCreate, db: Session = Depends(get_db)):
    try:
        # si no mandan usuario_id desde el cliente, asigna 1 por defecto (hasta que haya login real)
        usuario_id = data.usuario_id if data.usuario_id is not None else 1
        nueva = Transaccion(
            usuario_id=usuario_id,
            cuenta_id=data.cuenta_id,
            categoria_id=data.categoria_id,
            monto=data.monto,
            tipo=data.tipo,
            descripcion=data.descripcion,
            fecha=data.fecha or date.today(),
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

# 🔹 Actualizar transacción (parcial)
@routerTransacciones.put("/transacciones/{id}", response_model=TransaccionOut, tags=["Transacciones"])
def actualizar_transaccion(id: int, data: TransaccionUpdate, db: Session = Depends(get_db)):
    try:
        transaccion = db.query(Transaccion).filter(Transaccion.id == id).first()
        if not transaccion:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")

        if data.usuario_id is not None:
            transaccion.usuario_id = data.usuario_id
        if data.cuenta_id is not None:
            transaccion.cuenta_id = data.cuenta_id
        if data.categoria_id is not None:
            transaccion.categoria_id = data.categoria_id
        if data.monto is not None:
            transaccion.monto = data.monto
        if data.tipo is not None:
            transaccion.tipo = data.tipo
        if data.descripcion is not None:
            transaccion.descripcion = data.descripcion
        if data.fecha is not None:
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
