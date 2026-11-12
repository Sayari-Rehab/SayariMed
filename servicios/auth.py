"""
servicios/auth.py
-----------------
Lógica de autenticación de Sayari Med.

Centraliza TODO lo relacionado con:
- Hasheo y verificación de contraseñas (bcrypt).
- Login contra la base de datos.
- Manejo de sesión con st.session_state.
- Validaciones de rol (admin / terapeuta).

IMPORTANTE: este archivo NO sabe nada de la base de datos directamente.
Usa las funciones del repositorio de usuarios (que crearemos luego).
Por ahora, hace la consulta directa para no agregar más capas.
"""

from typing import Optional
import streamlit as st
from passlib.context import CryptContext

from core.database import get_session
from modelos import Usuario  # Importa y registra TODOS los modelos
from config.constants import ROL_ADMIN, ROL_TERAPEUTA


# ============================================================
# CIFRADO DE CONTRASEÑAS
# ============================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano a hash seguro."""
    return pwd_context.hash(password)


def verificar_password(password: str, hash_guardado: str) -> bool:
    """Verifica si una contraseña coincide con el hash guardado."""
    try:
        return pwd_context.verify(password, hash_guardado)
    except Exception:
        return False


# ============================================================
# AUTENTICACIÓN
# ============================================================
def autenticar(username: str, password: str) -> Optional[Usuario]:
    """
    Busca al usuario por username y valida la contraseña.

    Devuelve:
    - El objeto Usuario si las credenciales son correctas.
    - None si el usuario no existe, está inactivo, o la clave es incorrecta.
    """
    if not username or not password:
        return None

    with get_session() as db:
        usuario = (
            db.query(Usuario)
            .filter(Usuario.username == username.strip().lower())
            .first()
        )

        if not usuario:
            return None

        if not usuario.esta_activo:
            return None

        if not verificar_password(password, usuario.password_hash):
            return None

        # Expulsamos el usuario de la sesión de SQLAlchemy antes de devolverlo
        # para que sus atributos sigan accesibles después de cerrar la sesión.
        db.expunge(usuario)
        return usuario


# ============================================================
# SESIÓN (st.session_state)
# ============================================================
CLAVE_SESION = "usuario_actual"


def iniciar_sesion(usuario: Usuario) -> None:
    """Guarda al usuario autenticado en la sesión de Streamlit."""
    st.session_state[CLAVE_SESION] = {
        "id": usuario.id,
        "username": usuario.username,
        "nombre_completo": usuario.nombre_completo,
        "rol": usuario.rol,
        "email": usuario.email,
    }


def cerrar_sesion() -> None:
    """Borra al usuario de la sesión de Streamlit."""
    if CLAVE_SESION in st.session_state:
        del st.session_state[CLAVE_SESION]


def usuario_actual() -> Optional[dict]:
    """Devuelve el usuario logueado (como dict) o None."""
    return st.session_state.get(CLAVE_SESION)


def esta_logueado() -> bool:
    """True si hay alguien logueado."""
    return usuario_actual() is not None


# ============================================================
# VALIDACIONES DE ROL
# ============================================================
def es_admin() -> bool:
    """True si el usuario logueado es administrador."""
    u = usuario_actual()
    return bool(u and u["rol"] == ROL_ADMIN)


def es_terapeuta() -> bool:
    """True si el usuario logueado es terapeuta."""
    u = usuario_actual()
    return bool(u and u["rol"] == ROL_TERAPEUTA)