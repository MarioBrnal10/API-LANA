from pydantic import BaseModel, EmailStr, constr, condecimal
from typing import Optional, Literal
from datetime import datetime, date

class Usuario(BaseModel):
    id: Optional[int]
    nombre_completo: constr(strip_whitespace=True, min_length=1)
    correo_electronico: EmailStr
    telefono: Optional[constr(min_length=8, max_length=15)]
    contrasena_hash: str
    verificado: Optional[bool] = False
    creado_en: Optional[datetime]
    actualizado_en: Optional[datetime]

    class Config:
        orm_mode = True

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


class Presupuesto(BaseModel):
    id: Optional[int]
    usuario_id: int
    categoria_id: int
    mes: int  # validamos rango abajo
    anio: int
    monto: condecimal(max_digits=15, decimal_places=2)
    monto_actual: Optional[condecimal(max_digits=15, decimal_places=2)] = 0
    creado_en: Optional[datetime]
    actualizado_en: Optional[datetime]

    class Config:
        orm_mode = True

    @staticmethod
    def validate_mes(mes: int):
        if not (1 <= mes <= 12):
            raise ValueError("Mes debe estar entre 1 y 12.")
        return mes


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


class HistorialAlerta(BaseModel):
    id: Optional[int]
    usuario_id: int
    tipo_alerta: Optional[Literal['exceso_presupuesto', 'pago_proximo', 'saldo_bajo']]
    mensaje: Optional[str]
    fecha: Optional[datetime]
    leida: Optional[bool] = False

    class Config:
        orm_mode = True
