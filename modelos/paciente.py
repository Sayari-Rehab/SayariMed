"""
modelos/paciente.py
-------------------
Modelo de Paciente: ficha de filiación, clasificación patológica y gestión.

Un Paciente pertenece a UN terapeuta (asignación).
Un terapeuta puede tener MUCHOS pacientes.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Date,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from core.database import Base
from config.constants import (
    ESTADO_PACIENTE_ACTIVO,
    CATEGORIA_OTRAS,
)


class Paciente(Base):
    __tablename__ = "pacientes"

    # ------------------------------------------------------------
    # Identificación
    # ------------------------------------------------------------
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Documento de identidad (DNI en Perú). Único por paciente.
    documento = Column(String(30), unique=True, nullable=False, index=True)
        # ID anónimo para investigación (ej: SAY-A7F3B2). Único.
    id_anonimo = Column(String(20), unique=True, nullable=True, index=True)

    # ------------------------------------------------------------
    # Filiación
    # ------------------------------------------------------------
    nombre_completo = Column(String(200), nullable=False, index=True)
    edad = Column(Integer, nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    sexo = Column(String(10), nullable=True)
    telefono = Column(String(30), nullable=True)
    correo = Column(String(120), nullable=True)
    ocupacion = Column(String(120), nullable=True)
    direccion = Column(String(255), nullable=True)

    # ------------------------------------------------------------
    # Clasificación patológica
    # ------------------------------------------------------------
    categoria_patologica = Column(
        String(50), nullable=False, default=CATEGORIA_OTRAS, index=True
    )

    # ¿El paciente llegó con diagnóstico médico previo?
    vino_con_diagnostico = Column(Boolean, nullable=False, default=False)

    # Diagnóstico médico textual (si vino con uno)
    diagnostico_medico = Column(Text, nullable=True)

    # Motivo de consulta en palabras del paciente
    motivo_consulta = Column(Text, nullable=True)

    # Antecedentes / cuadro sintomatológico inicial
    antecedentes = Column(Text, nullable=True)

    # Observaciones de ingreso del terapeuta
    observaciones_ingreso = Column(Text, nullable=True)

    # ------------------------------------------------------------
    # Gestión
    # ------------------------------------------------------------
    # Terapeuta asignado (FK a usuarios.id)
    terapeuta_id = Column(
        Integer, ForeignKey("usuarios.id"), nullable=False, index=True
    )

    # Quién registró al paciente (puede ser admin o el propio terapeuta)
    registrado_por_id = Column(
        Integer, ForeignKey("usuarios.id"), nullable=True
    )

    estado = Column(
        String(20), nullable=False, default=ESTADO_PACIENTE_ACTIVO, index=True
    )
    activo = Column(Boolean, nullable=False, default=True)

    # ------------------------------------------------------------
    # Fechas
    # ------------------------------------------------------------
    fecha_ingreso = Column(Date, default=date.today, nullable=False)
    fecha_alta = Column(Date, nullable=True)

    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ------------------------------------------------------------
    # Relaciones
    # ------------------------------------------------------------
    # Terapeuta asignado
    terapeuta = relationship(
        "Usuario",
        back_populates="pacientes",
        foreign_keys=[terapeuta_id],
    )
    # Relación para diagnósticos secundarios
    patologias_asociadas = relationship(
        "PacientePatologia", 
        back_populates="paciente", 
        cascade="all, delete-orphan"
    )
    # ------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<Paciente(id={self.id}, doc='{self.documento}', "
            f"nombre='{self.nombre_completo}')>"
        )

    @property
    def nombre_corto(self) -> str:
        """Primer nombre + primer apellido para mostrar en listas."""
        partes = self.nombre_completo.split()
        if len(partes) >= 2:
            return f"{partes[0]} {partes[1]}"
        return self.nombre_completo

    @property
    def tiene_diagnostico(self) -> bool:
        return bool(self.vino_con_diagnostico and self.diagnostico_medico)