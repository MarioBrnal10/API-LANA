from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from sqlalchemy import text
from DB.conexion import get_db
from models.modelsDB import Presupuesto
from modelsPydantic import Presupuesto as PresupuestoPydantic

routerPresupuestos = APIRouter()

# Obtener todos los presupuestos
@routerPresupuestos.get("/presupuestos", response_model=List[PresupuestoPydantic], tags=["Presupuestos"]) 
def get_presupuestos(db: Session = Depends(get_db)):
    return db.query(Presupuesto).all()

# Obtener por ID
@routerPresupuestos.get("/presupuestos/{id}", response_model=PresupuestoPydantic, tags=["Presupuestos"]) 
def get_presupuesto(id: int, db: Session = Depends(get_db)):
    presupuesto = db.query(Presupuesto).filter(Presupuesto.id == id).first()
    if not presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return presupuesto

# Crear
@routerPresupuestos.post("/presupuestos", response_model=PresupuestoPydantic, tags=["Presupuestos"]) 
def crear_presupuesto(data: PresupuestoPydantic, db: Session = Depends(get_db)):
    try:
        nuevo = Presupuesto(
            usuario_id=data.usuario_id,
            categoria_id=data.categoria_id,
            mes=data.mes,
            anio=data.anio,
            monto=data.monto,
            monto_actual=data.monto_actual or 0,
            creado_en=datetime.now(),
            actualizado_en=datetime.now()
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear presupuesto: {str(e)}")
    finally:
        db.close()

# Actualizar
@routerPresupuestos.put("/presupuestos/{id}", response_model=PresupuestoPydantic, tags=["Presupuestos"]) 
def actualizar_presupuesto(id: int, data: PresupuestoPydantic, db: Session = Depends(get_db)):
    try:
        presupuesto = db.query(Presupuesto).filter(Presupuesto.id == id).first()
        if not presupuesto:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

        presupuesto.usuario_id = data.usuario_id
        presupuesto.categoria_id = data.categoria_id
        presupuesto.mes = data.mes
        presupuesto.anio = data.anio
        presupuesto.monto = data.monto
        presupuesto.monto_actual = data.monto_actual or 0
        presupuesto.actualizado_en = datetime.now()

        db.commit()
        db.refresh(presupuesto)
        return presupuesto
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar presupuesto: {str(e)}")
    finally:
        db.close()

# Eliminar
@routerPresupuestos.delete("/presupuestos/{id}", tags=["Presupuestos"]) 
def eliminar_presupuesto(id: int, db: Session = Depends(get_db)):
    try:
        presupuesto = db.query(Presupuesto).filter(Presupuesto.id == id).first()
        if not presupuesto:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

        db.delete(presupuesto)
        db.commit()
        return JSONResponse(content={"message": "Presupuesto eliminado exitosamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar presupuesto: {str(e)}")
    finally:
        db.close()

# Alertas de exceso (mes/año actual)
@routerPresupuestos.get("/presupuesto-alerta/{usuario_id}", tags=["Presupuestos"]) 
def verificar_exceso_presupuesto(usuario_id: int, db: Session = Depends(get_db)):
    now = datetime.now()
    mes = now.month
    anio = now.year

    sql = text("""
        SELECT c.nombre AS categoria, p.monto, p.monto_actual
        FROM presupuestos p
        JOIN categorias c ON c.id = p.categoria_id
        WHERE p.usuario_id = :usuario_id AND p.mes = :mes AND p.anio = :anio
    """)

    resultados = db.execute(sql, {"usuario_id": usuario_id, "mes": mes, "anio": anio}).fetchall()

    alertas = []
    for r in resultados:
        if r.monto_actual > r.monto:
            alertas.append({
                "categoria": r.categoria,
                "presupuesto": float(r.monto),
                "gastado": float(r.monto_actual),
                "exceso": round(float(r.monto_actual) - float(r.monto), 2)
            })

    return {
        "alertas_exceso": alertas,
        "mensaje": "Hay exceso en algunas categorías" if alertas else "Todo está dentro del presupuesto"
    }
