from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class PacientePatologia(Base):
    __tablename__ = "pacientes_patologias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False, index=True)
    patologia_id = Column(Integer, ForeignKey("patologias.id"), nullable=False, index=True)

    # Relaciones para poder acceder a los datos de ambas tablas
    paciente = relationship("Paciente", back_populates="patologias_asociadas")
    patologia = relationship("Patologia")