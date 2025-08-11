from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Literal
from datetime import datetime

from DB.conexion import get_db

# 🧠 SQLAlchemy models (ajusta el import a tu proyecto)
from models.modelsDB import Categoria as CategoriaDB  # Modelo SQLAlchemy

# 🧠 Pydantic models (el que tú ya tienes)
from modelsPydantic import Categoria as CategoriaSchema  # tu schema mostrado

routercategorias = APIRouter()

# 🔹 Obtener todas las categorías (con filtros opcionales)
@routercategorias.get("/categorias", response_model=List[CategoriaSchema], tags=["Categorias"])
def listar_categorias(
    db: Session = Depends(get_db),
    usuario_id: Optional[int] = Query(None, description="Filtra por usuario"),
    tipo: Optional[Literal["ingreso", "egreso"]] = Query(None, description="Filtra por tipo"),
):
    try:
        query = db.query(CategoriaDB)
        if usuario_id is not None:
            query = query.filter(CategoriaDB.usuario_id == usuario_id)
        if tipo is not None:
            query = query.filter(CategoriaDB.tipo == tipo)
        return query.order_by(CategoriaDB.id.desc()).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar categorías: {str(e)}")
    finally:
        db.close()

# 🔹 Obtener categoría por ID
@routercategorias.get("/categorias/{id}", response_model=CategoriaSchema, tags=["Categorias"])
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
    finally:
        db.close()

# 🔹 Crear nueva categoría
@routercategorias.post("/categorias", response_model=CategoriaSchema, tags=["Categorias"])
def crear_categoria(data: CategoriaSchema, db: Session = Depends(get_db)):
    try:
        nueva = CategoriaDB(
            nombre=data.nombre.strip(),
            tipo=data.tipo,
            usuario_id=data.usuario_id,
            categoria_padre_id=data.categoria_padre_id,
            es_sistema=bool(data.es_sistema) if data.es_sistema is not None else False,
            creado_en=datetime.now(),
        )
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return nueva
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear categoría: {str(e)}")
    finally:
        db.close()

# 🔹 Actualizar categoría
@routercategorias.put("/categorias/{id}", response_model=CategoriaSchema, tags=["Categorias"])
def actualizar_categoria(id: int, data: CategoriaSchema, db: Session = Depends(get_db)):
    try:
        cat = db.query(CategoriaDB).filter(CategoriaDB.id == id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        # Solo actualiza campos provistos (tu schema los trae opcionales)
        if data.nombre is not None:
            cat.nombre = data.nombre.strip()
        if data.tipo is not None:
            cat.tipo = data.tipo
        if data.usuario_id is not None:
            cat.usuario_id = data.usuario_id
        if data.categoria_padre_id is not None:
            cat.categoria_padre_id = data.categoria_padre_id
        if data.es_sistema is not None:
            cat.es_sistema = bool(data.es_sistema)

        db.commit()
        db.refresh(cat)
        return cat
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar categoría: {str(e)}")
    finally:
        db.close()

# 🔹 Eliminar categoría
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
    finally:
        db.close()
