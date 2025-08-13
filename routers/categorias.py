from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Literal

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

# Listar con filtros opcionales
@routercategorias.get("/categorias", response_model=List[CategoriaOut], tags=["Categorias"]) 
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
    finally:
        db.close()

@routercategorias.post("/categorias", response_model=CategoriaOut, tags=["Categorias"]) 
def crear_categoria(data: CategoriaCreate, db: Session = Depends(get_db)):
    try:
        nueva = CategoriaDB(
            nombre=data.nombre.strip(),
            tipo=data.tipo,
            usuario_id=None,
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
    finally:
        db.close()

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
