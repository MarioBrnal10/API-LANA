from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, Date, Text, Enum, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String(255), nullable=False)
    correo_electronico = Column(String(255), unique=True, nullable=False)
    telefono = Column(String(15), unique=True)
    contrasena_hash = Column(Text, nullable=False)
    verificado = Column(Boolean, default=False)
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    categorias = relationship('Categoria', back_populates='usuario')
    cuentas = relationship('Cuenta', back_populates='usuario')
    transacciones = relationship('Transaccion', back_populates='usuario')

class Categoria(Base):
    __tablename__ = 'categorias'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(Enum('ingreso', 'egreso'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'))
    categoria_padre_id = Column(Integer, ForeignKey('categorias.id', ondelete='SET NULL'), nullable=True)
    es_sistema = Column(Boolean, default=False)
    creado_en = Column(TIMESTAMP, server_default=func.now())

    usuario = relationship('Usuario', back_populates='categorias')
    categoria_padre = relationship('Categoria', remote_side=[id])



class Cuenta(Base):
    __tablename__ = 'cuentas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    nombre = Column(String(100), nullable=False)
    tipo = Column(Enum('efectivo', 'cuenta_bancaria', 'tarjeta_credito', 'tarjeta_debito', 'inversion', 'ahorro', 'otro'), nullable=False)
    saldo_actual = Column(DECIMAL(15, 2), nullable=False, default=0)
    moneda = Column(String(3), default='MXN')
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", back_populates="cuentas")

class Transaccion(Base):
    __tablename__ = 'transacciones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    cuenta_id = Column(Integer, ForeignKey('cuentas.id', ondelete='CASCADE'), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.id', ondelete='SET NULL'))
    monto = Column(DECIMAL(15, 2), nullable=False)
    tipo = Column(Enum('ingreso', 'egreso', 'transferencia'), nullable=False)
    descripcion = Column(Text)
    fecha = Column(Date, nullable=False)
    creado_en = Column(TIMESTAMP, server_default=func.now())

    usuario = relationship("Usuario", back_populates="transacciones")
    cuenta = relationship("Cuenta")
    categoria = relationship("Categoria", backref="transacciones")

class Transferencia(Base):
    __tablename__ = 'transferencias'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    transaccion_origen_id = Column(Integer, ForeignKey('transacciones.id', ondelete='CASCADE'), nullable=False)
    transaccion_destino_id = Column(Integer, ForeignKey('transacciones.id', ondelete='CASCADE'), nullable=False)
    monto = Column(DECIMAL(15, 2), nullable=False)
    fecha = Column(Date, nullable=False)

    usuario = relationship("Usuario", backref="transferencias")
    transaccion_origen = relationship("Transaccion", foreign_keys=[transaccion_origen_id])
    transaccion_destino = relationship("Transaccion", foreign_keys=[transaccion_destino_id])

class Presupuesto(Base):
    __tablename__ = 'presupuestos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.id', ondelete='CASCADE'), nullable=False)
    mes = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)
    monto = Column(DECIMAL(15, 2), nullable=False)
    monto_actual = Column(DECIMAL(15, 2), default=0)
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", backref="presupuestos")
    categoria = relationship("Categoria", backref="presupuestos")

class PagoFijo(Base):
    __tablename__ = 'pagos_fijos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    cuenta_id = Column(Integer, ForeignKey('cuentas.id', ondelete='CASCADE'), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.id', ondelete='CASCADE'), nullable=False)
    descripcion = Column(String(255), nullable=False)
    monto = Column(DECIMAL(15, 2), nullable=False)
    tipo_recurrencia = Column(Enum('diaria', 'semanal', 'quincenal', 'mensual', 'bimestral', 'trimestral', 'semestral', 'anual'), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    proxima_fecha = Column(Date, nullable=False)
    activo = Column(Boolean, default=True)
    creado_en = Column(TIMESTAMP, server_default=func.now())

    usuario = relationship("Usuario", backref="pagos_fijos")
    cuenta = relationship("Cuenta")
    categoria = relationship("Categoria")

class Meta(Base):
    __tablename__ = 'metas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    nombre = Column(String(255), nullable=False)
    monto_objetivo = Column(DECIMAL(15, 2), nullable=False)
    monto_actual = Column(DECIMAL(15, 2), default=0)
    fecha_inicio = Column(Date)
    fecha_objetivo = Column(Date)
    completada = Column(Boolean, default=False)
    creado_en = Column(TIMESTAMP, server_default=func.now())

    usuario = relationship("Usuario", backref="metas")

class TransaccionRecurrente(Base):
    __tablename__ = 'transacciones_recurrentes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    descripcion = Column(String(255))
    monto = Column(DECIMAL(15, 2), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.id', ondelete='SET NULL'))
    cuenta_id = Column(Integer, ForeignKey('cuentas.id', ondelete='SET NULL'))
    tipo = Column(Enum('ingreso', 'egreso'), nullable=False)
    tipo_recurrencia = Column(Enum('diaria', 'semanal', 'mensual', 'anual'))
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    activa = Column(Boolean, default=True)

    usuario = relationship("Usuario", backref="transacciones_recurrentes")
    categoria = relationship("Categoria")
    cuenta = relationship("Cuenta")

class HistorialAlerta(Base):
    __tablename__ = 'historial_alertas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    tipo_alerta = Column(Enum('exceso_presupuesto', 'pago_proximo', 'saldo_bajo'))
    mensaje = Column(Text)
    fecha = Column(TIMESTAMP, server_default=func.now())
    leida = Column(Boolean, default=False)

    usuario = relationship("Usuario", backref="historial_alertas")
