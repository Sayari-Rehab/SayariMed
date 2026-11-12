"""
modelos/evaluacion.py
---------------------
Modelo de Evaluación: registro de un test clínico aplicado a un paciente.

Cada fila representa "se aplicó el test X al paciente Y en la fecha Z".
Los resultados detallados (puntajes, ítems) se agregarán en sesiones futuras.
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


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    # ------------------------------------------------------------
    # Identificación
    # ------------------------------------------------------------
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relaciones
    paciente_id = Column(
        Integer, ForeignKey("pacientes.id"), nullable=False, index=True
    )
    aplicado_por_id = Column(
        Integer, ForeignKey("usuarios.id"), nullable=True
    )

    # ------------------------------------------------------------
    # Datos del test
    # ------------------------------------------------------------
    test_id = Column(String(50), nullable=False, index=True)     # ej: "tinetti"
    test_nombre = Column(String(200), nullable=False)             # ej: "Escala de Tinetti"
    categoria = Column(String(50), nullable=True)                 # ej: "Neurológica"

    # ------------------------------------------------------------
    # Estado de aplicación
    # ------------------------------------------------------------
    aplicado = Column(Boolean, nullable=False, default=False)
    fecha_aplicacion = Column(Date, default=date.today, nullable=False)

    # ------------------------------------------------------------
    # Resultado (opcional por ahora)
    # ------------------------------------------------------------
    resultado = Column(Text, nullable=True)      # ej: "24/28 puntos"
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
    paciente = relationship("Paciente", backref="evaluaciones")

    # ------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<Evaluacion(id={self.id}, paciente_id={self.paciente_id}, "
            f"test='{self.test_nombre}', aplicado={self.aplicado})>"
        )