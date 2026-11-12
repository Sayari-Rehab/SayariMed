from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.database import Base

# 1. La Escala General (Ej: Test de Adams)
class Escala(Base):
    __tablename__ = "escalas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(200), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=True) # Neurología, Trauma, etc.
    imagen_url = Column(String(500), nullable=True) # Para la foto de referencia
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    es_universal = Column(Boolean, default=False) # True si se aplica a todos los pacientes
    secciones = relationship("Seccion", back_populates="escala", cascade="all, delete-orphan")

# 2. Las Secciones (Ej: Equilibrio, Marcha - o "Única" si no tiene divisiones)
class Seccion(Base):
    __tablename__ = "escala_secciones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    escala_id = Column(Integer, ForeignKey("escalas.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    orden = Column(Integer, default=1) # Para saber cuál va primero

    escala = relationship("Escala", back_populates="secciones")
    items = relationship("Item", back_populates="seccion", cascade="all, delete-orphan")

# 3. Los Ítems (Ej: "Equilibrio sentado" con puntaje de 0 a 2)
class Item(Base):
    __tablename__ = "escala_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    seccion_id = Column(Integer, ForeignKey("escala_secciones.id"), nullable=False)
    nombre = Column(String(200), nullable=False)
    puntaje_maximo = Column(Integer, default=0) # Ej: 2 o 3
    tipo_entrada = Column(String(50), default="manual") # Opciones: "manual", "numero", "iot"
    orden = Column(Integer, default=1)

    seccion = relationship("Seccion", back_populates="items")

# 4. Tabla Puente: Qué escalas son obligatorias para qué patología
class PatologiaEscala(Base):
    __tablename__ = "patologias_escalas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patologia_id = Column(Integer, ForeignKey("patologias.id"), nullable=False)
    escala_id = Column(Integer, ForeignKey("escalas.id"), nullable=False)
    
    # ¡ESTA ES LA LÍNEA QUE FALTA!
    tipo_requerimiento = Column(String(20), default="Sugerida") 

    patologia = relationship("Patologia")
    escala = relationship("Escala")

def listar_escalas_universales() -> List[Escala]:
    """Devuelve las escalas que se aplican a TODOS los pacientes."""
    with get_session() as db:
        escalas = db.query(Escala).filter(Escala.es_universal == True).all()
        for e in escalas: 
            db.expunge(e)
        return escalas
# ============================================================
# NUEVAS TABLAS: LA CAPA DE "EVALUACIONES"
# ============================================================
class EvaluacionMaestra(Base):
    __tablename__ = "evaluaciones_maestras"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(200), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

class EvaluacionMaestraEscala(Base):
    __tablename__ = "evaluacion_maestra_escalas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluacion_id = Column(Integer, ForeignKey("evaluaciones_maestras.id"), nullable=False)
    escala_id = Column(Integer, ForeignKey("escalas.id"), nullable=False)
    
    evaluacion = relationship("EvaluacionMaestra", backref="escalas_vinculadas")
    escala = relationship("Escala")

class PatologiaEvaluacionMaestra(Base):
    __tablename__ = "patologia_evaluacion_maestra"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patologia_id = Column(Integer, ForeignKey("patologias.id"), nullable=False)
    evaluacion_id = Column(Integer, ForeignKey("evaluaciones_maestras.id"), nullable=False)
    tipo_requerimiento = Column(String(20), default="Obligatoria")

    patologia = relationship("Patologia")
    evaluacion = relationship("EvaluacionMaestra")