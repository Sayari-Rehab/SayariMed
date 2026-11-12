"""
core/database.py
----------------
Conexión única a la base de datos de Sayari Med.

Este es el ÚNICO archivo que sabe cómo conectarse a la base de datos.
Todos los demás le piden a él.

Si mañana migramos de SQLite a Postgres, SOLO se cambia este archivo.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

from config.settings import DATABASE_URL


# ============================================================
# MOTOR DE LA BASE DE DATOS
# ============================================================
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


# ============================================================
# SESIONES
# ============================================================
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ============================================================
# BASE DE LOS MODELOS
# ============================================================
Base = declarative_base()


# ============================================================
# FUNCIONES DE USO
# ============================================================
def get_db():
    """Generador de sesiones. Se usa en FastAPI y scripts."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_session():
    """Context manager para usar en scripts y Streamlit."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def crear_tablas():
    """
    Crea todas las tablas en la base de datos.
    Se llama UNA vez al inicio (o cuando se agrega un modelo nuevo).
    """
    # Importamos TODOS los modelos para que SQLAlchemy los registre
    from modelos import usuario, paciente, evaluacion, sesion, patologia  # noqa: F401
    
    Base.metadata.create_all(bind=engine)


def drop_tablas():
    """
    ⚠️ PELIGROSO: borra TODAS las tablas y sus datos.
    Solo se usa en desarrollo o para pruebas.
    """
    from modelos import usuario, paciente, evaluacion, sesion, patologia  # noqa: F401

    Base.metadata.drop_all(bind=engine)