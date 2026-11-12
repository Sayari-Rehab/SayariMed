"""
config/settings.py
------------------
Configuración central de Sayari Med.
Aquí se define TODO lo global: nombre de la app, ruta de la base de datos,
clave secreta, etc.

Si necesitas cambiar algo global, lo cambias SOLO aquí.
"""

from pathlib import Path


# ============================================================
# RUTAS DEL PROYECTO
# ============================================================

# Carpeta raíz del proyecto (sayari_med/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Carpeta donde vivirán los datos (base de datos, exports, etc.)
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)  # Se crea automáticamente si no existe


# ============================================================
# INFORMACIÓN DE LA APP
# ============================================================

APP_NAME = "Sayari Med"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Sistema Integral de Gestión Clínica & Fisioterapia"


# ============================================================
# BASE DE DATOS
# ============================================================

# Por ahora SQLite (un solo archivo local).
# En el futuro, cuando migremos a la nube, esta línea cambiará a:
# DATABASE_URL = "postgresql://usuario:clave@servidor/sayari"
DATABASE_URL = f"sqlite:///{DATA_DIR / 'sayari.db'}"


# ============================================================
# SEGURIDAD
# ============================================================

# Clave para firmar tokens de sesión. En producción se cambia por una larga
# y aleatoria. Por ahora es temporal.
SECRET_KEY = "cambiar-esta-clave-en-produccion-sayari-med-2026"

# Tiempo de expiración de sesión (minutos)
SESSION_EXPIRE_MINUTES = 60 * 8  # 8 horas


# ============================================================
# COLORES CORPORATIVOS SAYARI
# ============================================================

COLOR_PRIMARIO = "#112240"       # Azul marino profundo
COLOR_FONDO = "#F8F9FA"          # Gris claro
COLOR_TEXTO = "#1A1A1A"          # Casi negro
COLOR_ACENTO = "#4A90E2"         # Azul medio (para botones/highlights)
COLOR_EXITO = "#27AE60"          # Verde
COLOR_ALERTA = "#E74C3C"         # Rojo