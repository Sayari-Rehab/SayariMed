"""
repositorios/sesiones_repo.py
-----------------------------
Operaciones sobre la tabla sesiones.
"""

from typing import List, Optional
from datetime import date

from sqlalchemy import func

from core.database import get_session
from modelos import Usuario, Paciente, Evaluacion, Sesion, Patologia  # noqa: F401


# ============================================================
# LEER
# ============================================================
def listar_por_paciente(paciente_id: int) -> List[Sesion]:
    """Devuelve todas las sesiones de un paciente, ordenadas por fecha."""
    with get_session() as db:
        sesiones = (
            db.query(Sesion)
            .filter(Sesion.paciente_id == paciente_id)
            .order_by(Sesion.numero_sesion.asc())
            .all()
        )
        for s in sesiones:
            db.expunge(s)
        return sesiones


def obtener_por_id(sesion_id: int) -> Optional[Sesion]:
    """Busca una sesión por su ID."""
    with get_session() as db:
        sesion = db.query(Sesion).filter(Sesion.id == sesion_id).first()
        if sesion:
            db.expunge(sesion)
        return sesion


def contar_por_paciente(paciente_id: int) -> int:
    """Cuenta cuántas sesiones tiene un paciente."""
    with get_session() as db:
        return db.query(Sesion).filter(Sesion.paciente_id == paciente_id).count()


def siguiente_numero_sesion(paciente_id: int) -> int:
    """Devuelve el siguiente número de sesión para el paciente."""
    with get_session() as db:
        max_num = (
            db.query(func.max(Sesion.numero_sesion))
            .filter(Sesion.paciente_id == paciente_id)
            .scalar()
        )
        return (max_num or 0) + 1


# ============================================================
# CREAR
# ============================================================
def crear_sesion(
    paciente_id: int,
    terapeuta_id: int,
    eva_pre: Optional[float] = None,
    eva_post: Optional[float] = None,
    procedimientos: Optional[str] = None,
    respuesta_paciente: Optional[str] = None,
    tolerancia: Optional[str] = None,
    observaciones: Optional[str] = None,
    fecha_sesion: Optional[date] = None,
) -> Sesion:
    """Crea una nueva sesión para un paciente."""
    numero = siguiente_numero_sesion(paciente_id)

    with get_session() as db:
        nueva = Sesion(
            paciente_id=paciente_id,
            terapeuta_id=terapeuta_id,
            numero_sesion=numero,
            fecha_sesion=fecha_sesion or date.today(),
            eva_pre=eva_pre,
            eva_post=eva_post,
            procedimientos=procedimientos,
            respuesta_paciente=respuesta_paciente,
            tolerancia=tolerancia,
            observaciones=observaciones,
        )
        db.add(nueva)
        db.flush()
        db.expunge(nueva)
        return nueva


# ============================================================
# ACTUALIZAR / ELIMINAR
# ============================================================
def actualizar_sesion(sesion_id: int, **campos) -> bool:
    """Actualiza campos de una sesión existente."""
    with get_session() as db:
        sesion = db.query(Sesion).filter(Sesion.id == sesion_id).first()
        if not sesion:
            return False
        for key, value in campos.items():
            if hasattr(sesion, key):
                setattr(sesion, key, value)
        return True


def eliminar_sesion(sesion_id: int) -> bool:
    """Elimina una sesión."""
    with get_session() as db:
        sesion = db.query(Sesion).filter(Sesion.id == sesion_id).first()
        if not sesion:
            return False
        db.delete(sesion)
        return True