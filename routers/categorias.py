from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Literal
from sqlalchemy import or_

from DB.conexion import get_db

# SQLAlchemy
from models.modelsDB import Categoria as CategoriaDB

# Pydantic I/O
from modelsPydantic import (
    Categoria as CategoriaOut,
    CategoriaCreate,
    CategoriaUpdate,
)

routercategorias = APIRouter()


# ============================
# 📌 Listar categorías
# ============================
@routercategorias.get("/categorias", response_model=List[CategoriaOut], tags=["Categorias"])
def listar_categorias(
    db: Session = Depends(get_db),
    usuario_id: Optional[int] = Query(None, description="Filtra por usuario"),
    tipo: Optional[Literal["ingreso", "egreso"]] = Query(None, description="Filtra por tipo"),
):
    """
    Lista categorías.
    - Si se pasa usuario_id: devuelve categorías globales (es_sistema=True) + las del usuario.
    - Si no se pasa usuario_id: solo devuelve las globales.
    - Se puede filtrar por tipo: 'ingreso' o 'egreso'.
    """
    try:
        query = db.query(CategoriaDB)

        if usuario_id is not None:
            # Categorías globales + del usuario
            query = query.filter(
                or_(CategoriaDB.es_sistema == True, CategoriaDB.usuario_id == usuario_id)
            )
        else:
            # Solo globales
            query = query.filter(CategoriaDB.es_sistema == True)

        if tipo is not None:
            query = query.filter(CategoriaDB.tipo == tipo)

        return query.order_by(CategoriaDB.id.desc()).all()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar categorías: {str(e)}")


# ============================
# 📌 Obtener categoría por ID
# ============================
@routercategorias.get("/categorias/{id}", response_model=CategoriaOut, tags=["Categorias"])
def obtener_categoria(id: int, db: Session = Depends(get_db)):
    try:
        cat = db.query(CategoriaDB).filter(CategoriaDB.id == id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return cat
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener categoría: {str(e)}")


# ============================
# 📌 Crear categoría
# ============================
@routercategorias.post("/categorias", response_model=CategoriaOut, tags=["Categorias"])
def crear_categoria(data: CategoriaCreate, db: Session = Depends(get_db)):
    try:
        nueva = CategoriaDB(
            nombre=data.nombre.strip(),
            tipo=data.tipo,
            usuario_id=data.usuario_id,  # ✅ ahora soporta categorías por usuario
            categoria_padre_id=data.categoria_padre_id,
            es_sistema=False,
        )
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return nueva
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear categoría: {str(e)}")


# ============================
# 📌 Actualizar categoría
# ============================
@routercategorias.put("/categorias/{id}", response_model=CategoriaOut, tags=["Categorias"])
def actualizar_categoria(id: int, data: CategoriaUpdate, db: Session = Depends(get_db)):
    try:
        cat = db.query(CategoriaDB).filter(CategoriaDB.id == id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        if data.nombre is not None:
            cat.nombre = data.nombre.strip()
        if data.tipo is not None:
            cat.tipo = data.tipo
        if data.categoria_padre_id is not None:
            cat.categoria_padre_id = data.categoria_padre_id
        if hasattr(data, "usuario_id") and data.usuario_id is not None:
            cat.usuario_id = data.usuario_id

        db.commit()
        db.refresh(cat)
        return cat
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar categoría: {str(e)}")


# ============================
# 📌 Eliminar categoría
# ============================
@routercategorias.delete("/categorias/{id}", tags=["Categorias"])
def eliminar_categoria(id: int, db: Session = Depends(get_db)):
    try:
        cat = db.query(CategoriaDB).filter(CategoriaDB.id == id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        db.delete(cat)
        db.commit()
        return JSONResponse(content={"message": "Categoría eliminada exitosamente"})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar categoría: {str(e)}")
