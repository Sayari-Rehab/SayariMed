"""
scripts/init_db.py
------------------
Script de instalación inicial de Sayari Med.

Qué hace:
1. Crea el archivo sayari.db (base de datos).
2. Crea las tablas usuarios y pacientes.
3. Crea el usuario admin inicial (si no existe).
4. Muestra un resumen de lo que se hizo.

Se ejecuta UNA sola vez:
    python scripts/init_db.py

Para volver a ejecutarlo con seguridad, es idempotente:
si el admin ya existe, no lo duplica.
"""

import sys
from pathlib import Path

# Truco para poder importar desde cualquier parte del proyecto
# (agrega la carpeta raíz al path de Python)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from passlib.context import CryptContext

from core.database import crear_tablas, get_session
from modelos import Usuario, Paciente, Evaluacion, Sesion, Patologia  # noqa: F401
from config.constants import ROL_ADMIN, ESTADO_USUARIO_ACTIVO
from config.settings import APP_NAME, APP_VERSION


# ============================================================
# CONFIGURACIÓN DEL ADMIN INICIAL
# ============================================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Sayari2026!"      # ⚠️ CÁMBIALA después del primer login
ADMIN_NOMBRE   = "Administrador Sayari"
ADMIN_EMAIL    = "admin@sayari.med"


# ============================================================
# CIFRADO DE CONTRASEÑA
# ============================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano a hash seguro."""
    return pwd_context.hash(password)


def verificar_password(password: str, hash_guardado: str) -> bool:
    """Verifica si una contraseña coincide con el hash guardado."""
    return pwd_context.verify(password, hash_guardado)


# ============================================================
# CREAR ADMIN
# ============================================================
def crear_admin_inicial():
    """Crea el usuario admin si no existe."""
    with get_session() as db:
        existente = db.query(Usuario).filter_by(username=ADMIN_USERNAME).first()

        if existente:
            print(f"  ℹ️  El usuario '{ADMIN_USERNAME}' ya existe. No se duplica.")
            return existente

        admin = Usuario(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            nombre_completo=ADMIN_NOMBRE,
            rol=ROL_ADMIN,
            estado=ESTADO_USUARIO_ACTIVO,
            activo=True,
        )
        db.add(admin)
        db.flush()  # Para obtener el id antes del commit
        print(f"  ✅ Admin creado: {ADMIN_USERNAME}")
        return admin


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print(f"  🩺 {APP_NAME} — Instalación inicial v{APP_VERSION}")
    print("=" * 60)
    print()

    # 1. Crear tablas
    print("📦 Creando tablas en la base de datos...")
    crear_tablas()
    print("  ✅ Tablas creadas: usuarios, pacientes")
    print()

    # 2. Crear admin
    print("👤 Verificando usuario administrador...")
    crear_admin_inicial()
    print()

    # 3. Verificación final
    with get_session() as db:
        total_usuarios = db.query(Usuario).count()

    print("📊 Resumen:")
    print(f"  • Usuarios en la base de datos: {total_usuarios}")
    print()
    print("=" * 60)
    print("  ✅ INSTALACIÓN COMPLETA")
    print("=" * 60)
    print()
    print("🔑 Credenciales de acceso:")
    print(f"  • Usuario:    {ADMIN_USERNAME}")
    print(f"  • Contraseña: {ADMIN_PASSWORD}")
    print()
    print("⚠️  IMPORTANTE: cambia la contraseña después del primer login.")
    print()


if __name__ == "__main__":
    main()