"""
modelos/patologia.py
--------------------
Modelo de Patología: biblioteca clínica de referencia.

Cada patología tiene:
- Nombre (ej: "ACV isquémico").
- Categoría (Neurológica, Traumatológica, etc.).
- Resumen clínico (definición breve).
- Cuadro clínico (síntomas comunes).
- Enfoque fisioterapéutico (objetivos, técnicas).
- Tests recomendados (IDs separados por coma).
- Referencias (opcional).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from core.database import Base


class Patologia(Base):
    __tablename__ = "patologias"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nombre = Column(String(200), unique=True, nullable=False, index=True)
    categoria = Column(String(50), nullable=False, index=True)

    resumen = Column(Text, nullable=True)
    cuadro_clinico = Column(Text, nullable=True)
    enfoque_fisio = Column(Text, nullable=True)

    # Tests recomendados, separados por coma: "tinetti,ashworth,barthel"
    tests_recomendados = Column(Text, nullable=True)

    referencias = Column(Text, nullable=True)

    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Patologia(id={self.id}, nombre='{self.nombre}', cat='{self.categoria}')>"

    @property
    def lista_tests(self) -> list:
        """Devuelve la lista de IDs de tests recomendados."""
        if not self.tests_recomendados:
            return []
        return [t.strip() for t in self.tests_recomendados.split(",") if t.strip()]