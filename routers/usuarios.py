from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
from DB.conexion import get_db
from models.modelsDB import Usuario
from modelsPydantic import Usuario as UsuarioPydantic
from modelsPydantic import UsuarioLogin

routerUsuarios = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@routerUsuarios.post("/login", tags=["Login"])
def login(usuario: UsuarioLogin, db: Session = Depends(get_db)):
    # Buscar al usuario por correo
    user = db.query(Usuario).filter(Usuario.correo_electronico == usuario.correo_electronico).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Comparar contraseña ingresada con la hashada en BD
    if not pwd_context.verify(usuario.contrasena_hash, user.contrasena_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    return JSONResponse(content={
        "mensaje": "✅ Inicio de sesión exitoso",
        "id": user.id,
        "nombre_completo": user.nombre_completo,
        "correo_electronico": user.correo_electronico,
        "telefono": user.telefono,
        "verificado": user.verificado
    })

#endpoint de registro
@routerUsuarios.post("/usuarios", tags=["Usuarios"])
def crear_usuario(usuario: UsuarioPydantic, db: Session = Depends(get_db)):
    try:
        # Verificar si ya existe el correo
        existente = db.query(Usuario).filter(Usuario.correo_electronico == usuario.correo_electronico).first()
        if existente:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")

        # Hashear la contraseña (reemplazo opcional para Laravel)
        hashed_password = pwd_context.hash(usuario.contrasena_hash).replace("$2b$", "$2y$")

        # Si se envía creado_en o actualizado_en desde el frontend, se usa; si no, se genera con datetime.now()
        creado = usuario.creado_en if usuario.creado_en else datetime.now()
        actualizado = usuario.actualizado_en if usuario.actualizado_en else datetime.now()

        nuevo_usuario = Usuario(
            nombre_completo=usuario.nombre_completo,
            correo_electronico=usuario.correo_electronico,
            telefono=usuario.telefono,
            contrasena_hash=hashed_password,
            verificado=usuario.verificado,
            creado_en=creado,
            actualizado_en=actualizado
        )

        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

        return JSONResponse(content={
            "message": "✅ Usuario creado correctamente",
            "id": nuevo_usuario.id
        })


    except Exception as e:

        db.rollback()

        print("🔥 ERROR AL CREAR USUARIO:", str(e))  # 👈 esto te dirá el error exacto en la terminal

        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")

