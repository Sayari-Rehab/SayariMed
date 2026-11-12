"""
repositorios/usuarios_repo.py
-----------------------------
Operaciones CRUD sobre la tabla usuarios.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from core.database import get_session
from modelos import Usuario
from config.constants import ROL_TERAPEUTA, ESTADO_USUARIO_ACTIVO


# ============================================================
# LEER
# ============================================================
def listar_usuarios(solo_terapeutas: bool = False) -> List[Usuario]:
    """Devuelve todos los usuarios. Si solo_terapeutas=True, filtra."""
    with get_session() as db:
        query = db.query(Usuario)
        if solo_terapeutas:
            query = query.filter(Usuario.rol == ROL_TERAPEUTA)
        usuarios = query.order_by(Usuario.fecha_creacion.desc()).all()
        for u in usuarios:
            db.expunge(u)
        return usuarios


def buscar_por_username(username: str) -> Optional[Usuario]:
    """Busca un usuario por su username exacto."""
    with get_session() as db:
        usuario = db.query(Usuario).filter(
            Usuario.username == username.strip().lower()
        ).first()
        if usuario:
            db.expunge(usuario)
        return usuario


def buscar_por_id(usuario_id: int) -> Optional[Usuario]:
    """Busca un usuario por su ID."""
    with get_session() as db:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if usuario:
            db.expunge(usuario)
        return usuario


def listar_colegiaturas_pendientes() -> List[Usuario]:
    """Devuelve los terapeutas con colegiatura pendiente."""
    with get_session() as db:
        usuarios = (
            db.query(Usuario)
            .filter(
                Usuario.rol == ROL_TERAPEUTA,
                Usuario.colegiatura_pendiente == True,  # noqa: E712
            )
            .all()
        )
        for u in usuarios:
            db.expunge(u)
        return usuarios


# ============================================================
# VALIDACIONES DE UNICIDAD
# ============================================================
def existe_username(username: str) -> bool:
    """True si ya existe un usuario con ese username."""
    if not username:
        return False
    with get_session() as db:
        return db.query(Usuario).filter(
            Usuario.username == username.strip().lower()
        ).first() is not None


def existe_email(email: str) -> bool:
    """True si ya existe un usuario con ese email."""
    if not email:
        return False
    with get_session() as db:
        return db.query(Usuario).filter(
            Usuario.email == email.strip().lower()
        ).first() is not None


def existe_dni(dni: str) -> bool:
    """True si ya existe un usuario con ese DNI."""
    if not dni:
        return False
    with get_session() as db:
        return db.query(Usuario).filter(
            Usuario.dni == dni.strip()
        ).first() is not None


def existe_colegiatura(colegiatura: str) -> bool:
    """True si ya existe un usuario con esa colegiatura."""
    if not colegiatura:
        return False
    with get_session() as db:
        return db.query(Usuario).filter(
            Usuario.colegiatura == colegiatura.strip()
        ).first() is not None


# ============================================================
# CREAR
# ============================================================
def crear_terapeuta(
    username: str,
    password_hash: str,
    nombre_completo: str,
    dni: Optional[str] = None,
    colegiatura: Optional[str] = None,
    colegiatura_pendiente: bool = False,
    email: Optional[str] = None,
    telefono: Optional[str] = None,
    titulo: Optional[str] = None,
    especialidad: Optional[str] = None,
    foto_url: Optional[str] = None,
    creado_por_id: Optional[int] = None,
) -> Usuario:
    """Crea un nuevo terapeuta con todos los campos."""
    with get_session() as db:
        nuevo = Usuario(
            username=username.strip().lower(),
            password_hash=password_hash,
            nombre_completo=nombre_completo.strip(),
            dni=dni.strip() if dni else None,
            colegiatura=colegiatura.strip() if colegiatura else None,
            colegiatura_pendiente=colegiatura_pendiente,
            email=email.strip() if email else None,
            telefono=telefono.strip() if telefono else None,
            titulo=titulo.strip() if titulo else None,
            especialidad=especialidad.strip() if especialidad else None,
            foto_url=foto_url,
            rol=ROL_TERAPEUTA,
            estado=ESTADO_USUARIO_ACTIVO,
            activo=True,
            creado_por_id=creado_por_id,
        )
        db.add(nuevo)
        db.flush()
        db.expunge(nuevo)
        return nuevo


# ============================================================
# ACTUALIZAR
# ============================================================
def cambiar_estado(usuario_id: int, activo: bool) -> bool:
    """Activa o desactiva un usuario."""
    with get_session() as db:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            return False
        usuario.activo = activo
        usuario.estado = ESTADO_USUARIO_ACTIVO if activo else "inactivo"
        return True


def activar_modo_practicantes(usuario_id: int, activo: bool) -> bool:
    """
    Activa o desactiva la opción "puede tener practicantes" para un terapeuta.

    ⚠️ Solo debe llamarse desde el panel admin.
    """
    with get_session() as db:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            return False
        usuario.puede_tener_practicantes = activo
        return True
def actualizar_terapeuta(usuario_id: int, **campos) -> bool:
    """Actualiza cualquier campo de un terapeuta."""
    with get_session() as db:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            return False
        for key, value in campos.items():
            if hasattr(usuario, key):
                setattr(usuario, key, value)
        return True