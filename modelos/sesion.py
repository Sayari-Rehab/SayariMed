"""
modelos/sesion.py
-----------------
Modelo de Sesión de rehabilitación.

Cada fila representa una sesión de fisioterapia aplicada a un paciente.
Registra:
- Número correlativo de sesión (1, 2, 3... por paciente).
- Fecha y hora.
- EVA pre y post (dolor 0-10).
- Procedimientos aplicados (texto con lista separada por comas).
- Respuesta del paciente.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Date,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import relationship

from core.database import Base


class Sesion(Base):
    __tablename__ = "sesiones"

    # ------------------------------------------------------------
    # Identificación
    # ------------------------------------------------------------
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relaciones
    paciente_id = Column(
        Integer, ForeignKey("pacientes.id"), nullable=False, index=True
    )
    terapeuta_id = Column(
        Integer, ForeignKey("usuarios.id"), nullable=False, index=True
    )

    # ------------------------------------------------------------
    # Datos de la sesión
    # ------------------------------------------------------------
    numero_sesion = Column(Integer, nullable=False, default=1)
    fecha_sesion = Column(Date, default=date.today, nullable=False)

    # EVA (Escala Visual Analógica): 0 a 10
    eva_pre = Column(Float, nullable=True)
    eva_post = Column(Float, nullable=True)

    # Procedimientos (lista separada por comas)
    procedimientos = Column(Text, nullable=True)

    # Evaluación subjetiva
    respuesta_paciente = Column(Text, nullable=True)
    tolerancia = Column(String(50), nullable=True)   # "Buena", "Regular", "Mala"
    observaciones = Column(Text, nullable=True)

    # ------------------------------------------------------------
    # Auditoría
    # ------------------------------------------------------------
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ------------------------------------------------------------
    # Relaciones ORM
    # ------------------------------------------------------------
    paciente = relationship("Paciente", backref="sesiones")

    # ------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<Sesion(id={self.id}, paciente_id={self.paciente_id}, "
            f"num={self.numero_sesion}, fecha={self.fecha_sesion})>"
        )

    @property
    def mejora_dolor(self) -> float:
        """Cuánto mejoró el dolor en esta sesión (positivo = mejora)."""
        if self.eva_pre is None or self.eva_post is None:
            return 0.0
        return self.eva_pre - self.eva_post