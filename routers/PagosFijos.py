from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from sqlalchemy import text

from DB.conexion import get_db
from models.modelsDB import Presupuesto
from modelsPydantic import Presupuesto as PresupuestoPydantic

routerPagosFijos = APIRouter()


@routerPagosFijos.get("/pagos-fijos/validar-presupuesto/{usuario_id}", tags=["Presupuestos"])
def validar_pagos_fijos_contra_presupuesto(usuario_id: int, db: Session = Depends(get_db)):
    now = datetime.now()
    mes = now.month
    anio = now.year

    # Obtener todos los pagos fijos del usuario
    pagos = db.execute(text("""
        SELECT pf.id, c.nombre AS categoria, pf.monto, pf.categoria_id
        FROM pagos_fijos pf
        JOIN categorias c ON c.id = pf.categoria_id
        WHERE pf.usuario_id = :usuario_id AND pf.activo = 1
    """), {"usuario_id": usuario_id}).fetchall()

    if not pagos:
        return {"mensaje": "No hay pagos fijos programados."}

    # Obtener presupuestos activos por categoría para el mes
    presupuestos = db.execute(text("""
        SELECT categoria_id, monto, monto_actual
        FROM presupuestos
        WHERE usuario_id = :usuario_id AND mes = :mes AND anio = :anio
    """), {"usuario_id": usuario_id, "mes": mes, "anio": anio}).fetchall()

    presupuestos_dict = {p.categoria_id: p for p in presupuestos}

    respuesta = []
    for p in pagos:
        presupuesto = presupuestos_dict.get(p.categoria_id)

        if presupuesto:
            restante = presupuesto.monto - presupuesto.monto_actual
            puede_cubrir = restante >= p.monto
            estado = "cubierto" if puede_cubrir else "excede presupuesto"
        else:
            estado = "sin presupuesto definido"

        respuesta.append({
            "categoria": p.categoria,
            "pago_fijo_monto": float(p.monto),
            "estado": estado
        })

    return {
        "validacion_pagos_fijos": respuesta
    }