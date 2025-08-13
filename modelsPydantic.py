from pydantic import BaseModel, EmailStr, constr, condecimal
from typing import Optional, Literal
from datetime import datetime, date

# ---------------- Usuarios ----------------

class Usuario(BaseModel):
    id: Optional[int] = None
    nombre_completo: constr(strip_whitespace=True, min_length=1)
    correo_electronico: EmailStr
    telefono: Optional[constr(min_length=8, max_length=15)]
    contrasena_hash: str
    verificado: Optional[bool] = False
    creado_en: Optional[datetime]
    actualizado_en: Optional[datetime]

    class Config:
        orm_mode = True

class UsuarioLogin(BaseModel):
    correo_electronico: EmailStr
    contrasena_hash: constr(min_length=1)

# ---------------- Categorías ----------------

# Output (respuesta)
class Categoria(BaseModel):
    id: Optional[int]
    nombre: constr(strip_whitespace=True, min_length=1)
    tipo: Literal['ingreso', 'egreso']
    usuario_id: Optional[int]
    categoria_padre_id: Optional[int]
    es_sistema: Optional[bool] = False
    creado_en: Optional[datetime]

    class Config:
        orm_mode = True

# Input (crear)
class CategoriaCreate(BaseModel):
    nombre: constr(strip_whitespace=True, min_length=1)
    tipo: Literal['ingreso', 'egreso']
    categoria_padre_id: Optional[int] = None

# Input (actualizar parcial)
class CategoriaUpdate(BaseModel):
    nombre: Optional[constr(strip_whitespace=True, min_length=1)] = None
    tipo: Optional[Literal['ingreso', 'egreso']] = None
    categoria_padre_id: Optional[int] = None

# ---------------- Cuentas ----------------

class Cuenta(BaseModel):
    id: Optional[int]
    usuario_id: int
    nombre: constr(min_length=1, strip_whitespace=True)
    tipo: Literal['efectivo', 'cuenta_bancaria', 'tarjeta_credito', 'tarjeta_debito', 'inversion', 'ahorro', 'otro']
    saldo_actual: condecimal(max_digits=15, decimal_places=2)
    moneda: Optional[constr(min_length=3, max_length=3)] = 'MXN'
    creado_en: Optional[datetime]
    actualizado_en: Optional[datetime]

    class Config:
        orm_mode = True

# ---------------- Transacciones ----------------

class Transaccion(BaseModel):
    id: Optional[int]
    usuario_id: int
    cuenta_id: int
    categoria_id: Optional[int]
    monto: condecimal(max_digits=15, decimal_places=2)
    tipo: Literal['ingreso', 'egreso', 'transferencia']
    descripcion: Optional[str]
    fecha: date
    creado_en: Optional[datetime]

    class Config:
        orm_mode = True

class Transferencia(BaseModel):
    id: Optional[int]
    usuario_id: int
    transaccion_origen_id: int
    transaccion_destino_id: int
    monto: condecimal(max_digits=15, decimal_places=2)
    fecha: date

    class Config:
        orm_mode = True

# ---------------- Presupuestos ----------------

class Presupuesto(BaseModel):
    id: Optional[int]
    usuario_id: int
    categoria_id: int
    mes: int
    anio: int
    monto: condecimal(max_digits=15, decimal_places=2)
    monto_actual: Optional[condecimal(max_digits=15, decimal_places=2)] = 0
    creado_en: Optional[datetime]
    actualizado_en: Optional[datetime]

    class Config:
        orm_mode = True

# ---------------- Pagos Fijos ----------------

class PagoFijo(BaseModel):
    id: Optional[int]
    usuario_id: int
    cuenta_id: int
    categoria_id: int
    descripcion: constr(strip_whitespace=True, min_length=1)
    monto: condecimal(max_digits=15, decimal_places=2)
    tipo_recurrencia: Literal['diaria', 'semanal', 'quincenal', 'mensual', 'bimestral', 'trimestral', 'semestral', 'anual']
    fecha_inicio: date
    proxima_fecha: date
    activo: Optional[bool] = True
    creado_en: Optional[datetime]

    class Config:
        orm_mode = True

# ---------------- Metas ----------------

class Meta(BaseModel):
    id: Optional[int]
    usuario_id: int
    nombre: constr(strip_whitespace=True, min_length=1)
    monto_objetivo: condecimal(max_digits=15, decimal_places=2)
    monto_actual: Optional[condecimal(max_digits=15, decimal_places=2)] = 0
    fecha_inicio: Optional[date]
    fecha_objetivo: Optional[date]
    completada: Optional[bool] = False
    creado_en: Optional[datetime]

    class Config:
        orm_mode = True

# ---------------- Transacciones Recurrentes ----------------

class TransaccionRecurrente(BaseModel):
    id: Optional[int]
    usuario_id: int
    descripcion: Optional[constr(strip_whitespace=True, max_length=255)]
    monto: condecimal(max_digits=15, decimal_places=2)
    categoria_id: Optional[int]
    cuenta_id: Optional[int]
    tipo: Literal['ingreso', 'egreso']
    tipo_recurrencia: Optional[Literal['diaria', 'semanal', 'mensual', 'anual']]
    fecha_inicio: date
    fecha_fin: Optional[date]
    activa: Optional[bool] = True

    class Config:
        orm_mode = True
# ---------- TRANSACCIONES ----------
class TransaccionBase(BaseModel):
    usuario_id: Optional[int] = None           # ahora opcional (lo asignamos en el backend si no viene)
    cuenta_id: Optional[int] = None            # puede ser null
    categoria_id: int                          # requerido para crear
    monto: condecimal(max_digits=15, decimal_places=2)
    tipo: Literal['ingreso', 'egreso']
    descripcion: Optional[str] = None
    fecha: Optional[date] = None               # opcional; backend usa hoy si no viene

class TransaccionCreate(TransaccionBase):
    # Igual que base para este caso (categoria_id/monto/tipo requeridos)
    pass

class TransaccionUpdate(BaseModel):
    # TODO parcial: todo opcional; actualiza solo lo presente
    usuario_id: Optional[int] = None
    cuenta_id: Optional[int] = None
    categoria_id: Optional[int] = None
    monto: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    tipo: Optional[Literal['ingreso', 'egreso']] = None
    descripcion: Optional[str] = None
    fecha: Optional[date] = None

class TransaccionOut(BaseModel):
    id: int
    usuario_id: Optional[int]
    cuenta_id: Optional[int]
    categoria_id: Optional[int]
    monto: condecimal(max_digits=15, decimal_places=2)
    tipo: Literal['ingreso', 'egreso']
    descripcion: Optional[str]
    fecha: date
    creado_en: Optional[datetime]

    class Config:
        orm_mode = True
# ---------------- Historial de Alertas ----------------

class HistorialAlerta(BaseModel):
    id: Optional[int]
    usuario_id: int
    tipo_alerta: Optional[Literal['exceso_presupuesto', 'pago_proximo', 'saldo_bajo']]
    mensaje: Optional[str]
    fecha: Optional[datetime]
    leida: Optional[bool] = False

    class Config:
        orm_mode = True
