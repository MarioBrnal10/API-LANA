from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from DB.conexion import get_db  # debe estar configurado en tu app

routercategorias = APIRouter()

from models import Transaccion, Categoria, Presupuesto  # tus modelos SQLAlchemy
