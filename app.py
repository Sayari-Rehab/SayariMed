"""
app.py — Punto de entrada de Sayari Med.

Router principal: decide qué mostrar según el estado de la sesión.
"""

import streamlit as st
from pathlib import Path
from PIL import Image

from config.settings import APP_NAME
from ui.estilos import aplicar_estilos
from ui.pwa import inyectar_pwa, mostrar_banner_instalacion
from ui.vistas import login as vista_login
from ui.vistas import admin as vista_admin
from ui.vistas import pacientes as vista_pacientes
from ui.vistas import sesiones as vista_sesiones
from ui.vistas import reportes as vista_reportes
from ui.vistas import anonimizacion as vista_anonimizacion
from ui.vistas import biblioteca as vista_biblioteca
from servicios.auth import (
    esta_logueado,
    usuario_actual,
    es_admin,
    es_terapeuta,
    cerrar_sesion,
)


# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================
_ruta_favicon = Path(__file__).resolve().parent / "assets" / "logo_favicon.png"
_favicon = Image.open(_ruta_favicon) if _ruta_favicon.exists() else "🩺"

st.set_page_config(
    page_title=APP_NAME,
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# AUTO-INICIALIZACIÓN PARA LA NUBE (Turso)
# ============================================================
from core.database import crear_tablas, get_session
from modelos import Usuario
from servicios.auth import hash_password
from config.constants import ROL_ADMIN, ESTADO_USUARIO_ACTIVO

# Crear tablas si no existen
crear_tablas()

# Crear admin si no existe
with get_session() as db:
    admin = db.query(Usuario).filter_by(username="admin").first()
    if not admin:
        nuevo_admin = Usuario(
            username="admin",
            email="admin@sayari.med",
            password_hash=hash_password("Sayari2026!"),
            nombre_completo="Administrador Sayari",
            rol=ROL_ADMIN,
            estado=ESTADO_USUARIO_ACTIVO,
            activo=True,
        )
        db.add(nuevo_admin)
        print("✅ Admin creado automáticamente en Turso")

# ============================================================
# ESTILOS Y PWA
# ============================================================
aplicar_estilos()
inyectar_pwa()


# ============================================================
# ROUTER PRINCIPAL
# ============================================================
def main() -> None:
    """Decide qué mostrar según el estado de la sesión."""

    # ---------- CASO 1: NO LOGUEADO ----------
    if not esta_logueado():
        vista_login.render()
        return

    # ---------- CASO 2: LOGUEADO ----------
    usuario = usuario_actual()

    # --- Sidebar ---
    with st.sidebar:
        _ruta_sidebar_logo = Path(__file__).resolve().parent / "assets" / "logo_sidebar.png"
        if _ruta_sidebar_logo.exists():
            st.image(str(_ruta_sidebar_logo), use_container_width=True)
        else:
            st.markdown(f"### 🩺 {APP_NAME}")
        st.markdown("---")

        # Foto + nombre del usuario logueado
        _foto = usuario.get("foto_url")
        if _foto:
            _ruta_foto = Path(__file__).resolve().parent / _foto.replace("/app/", "")
            if _ruta_foto.exists():
                col_f, col_info = st.columns([1, 2])
                with col_f:
                    st.image(str(_ruta_foto), width=60)
                with col_info:
                    st.markdown(f"**{usuario['nombre_completo']}**")
                    st.caption(f"@{usuario['username']}")
            else:
                st.markdown(f"**{usuario['nombre_completo']}**")
                st.caption(f"@{usuario['username']} · {usuario['rol'].capitalize()}")
        else:
            st.markdown(f"**{usuario['nombre_completo']}**")
            st.caption(f"@{usuario['username']} · {usuario['rol'].capitalize()}")
        st.markdown("---")

        # Menú según rol
        if es_admin():
            st.markdown("#### 🛠️ Administración")
            if st.button("👥 Terapeutas", use_container_width=True, key="btn_terapeutas"):
                st.session_state["vista_admin"] = "terapeutas"
                st.session_state.pop("vista_clinica", None)
            if st.button("📊 Gestor de Escalas", use_container_width=True, key="btn_gestor_escalas"):
                st.session_state["vista_admin"] = "gestor_escalas"
                st.session_state.pop("vista_clinica", None)
            if st.button("🔬 Anonimización", use_container_width=True, key="btn_anonimizacion"):
                st.session_state["vista_admin"] = "anonimizacion"
                st.session_state.pop("vista_clinica", None)

        if es_terapeuta() or es_admin():
            st.markdown("#### 🩺 Clínica")
            if st.button("🧑‍🦽 Mis pacientes", use_container_width=True, key="btn_mis_pacientes"):
                st.session_state["vista_clinica"] = "pacientes"
                st.session_state.pop("paciente_actual_id", None)
                st.session_state.pop("vista_admin", None)
            if st.button("📅 Sesiones", use_container_width=True, key="btn_sesiones"):
                st.session_state["vista_clinica"] = "sesiones"
                st.session_state.pop("paciente_detalle_id", None)
                st.session_state.pop("vista_admin", None)
            if st.button("📈 Reportes", use_container_width=True, key="btn_reportes"):
                st.session_state["vista_clinica"] = "reportes"
                st.session_state.pop("paciente_actual_id", None)
                st.session_state.pop("paciente_detalle_id", None)
                st.session_state.pop("vista_admin", None)

        st.markdown("#### 📚 Referencia")
        if st.button("📖 Biblioteca clínica", use_container_width=True, key="btn_biblioteca"):
            st.session_state["vista_clinica"] = "biblioteca"
            st.session_state.pop("paciente_actual_id", None)
            st.session_state.pop("paciente_detalle_id", None)
            st.session_state.pop("vista_admin", None)
            st.session_state.pop("patologia_detalle_id", None)

        st.markdown("---")

        # Inicio
        if st.button("🏠 Inicio", use_container_width=True, key="btn_inicio_sidebar"):
            for key in [
                "vista_admin", "vista_clinica", "vista_pacientes",
                "paciente_detalle_id", "paciente_actual_id", "patologia_detalle_id",
            ]:
                st.session_state.pop(key, None)
            st.rerun()

        # Cerrar sesión
        if st.button("🚪 Cerrar sesión", use_container_width=True, key="btn_cerrar_sesion"):
            cerrar_sesion()
            st.rerun()

    # --- Router de vistas internas ---
    if es_admin() and st.session_state.get("vista_admin") == "terapeutas":
        vista_admin.render()
        return
    
    if es_admin() and st.session_state.get("vista_admin") == "gestor_escalas":
        from ui.vistas import gestor_escalas as vista_gestor
        vista_gestor.render()
        return

    if es_admin() and st.session_state.get("vista_admin") == "anonimizacion":
        vista_anonimizacion.render()
        return

    if st.session_state.get("vista_clinica") == "pacientes":
        vista_pacientes.render()
        return

    if st.session_state.get("vista_clinica") == "sesiones":
        vista_sesiones.render()
        return

    if st.session_state.get("vista_clinica") == "reportes":
        vista_reportes.render()
        return

    if st.session_state.get("vista_clinica") == "biblioteca":
        vista_biblioteca.render()
        return

    # --- Banner PWA ---
    mostrar_banner_instalacion()

    # --- Dashboard ---
    st.title(f"Bienvenido, {usuario['nombre_completo'].split()[0]} 👋")
    st.caption(f"Rol: **{usuario['rol'].capitalize()}** · Sesión activa")
    st.markdown("---")

    # --- Métricas ---
    from repositorios.pacientes_repo import contar_pacientes, listar_pacientes
    from repositorios.sesiones_repo import contar_por_paciente
    from repositorios.usuarios_repo import listar_usuarios
    from repositorios.patologias_repo import contar_patologias
    from config.constants import ROL_TERAPEUTA

    terr_id = None if es_admin() else usuario["id"]
    total_pac = contar_pacientes(terapeuta_id=terr_id)

    pacientes = listar_pacientes(terapeuta_id=terr_id)
    total_ses = sum(contar_por_paciente(p.id) for p in pacientes)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🧑‍🦽 Pacientes", total_pac)
    with col2:
        st.metric("📅 Sesiones", total_ses)
    with col3:
        if es_admin():
            terapeutas = [u for u in listar_usuarios() if u.rol == ROL_TERAPEUTA]
            st.metric("👨‍⚕️ Terapeutas", len(terapeutas))
        else:
            st.metric("📈 Reportes", "Disponible")
    with col4:
        st.metric("📖 Patologías", contar_patologias())

    st.markdown("---")
    st.markdown("### 🎯 Accesos rápidos")
    st.markdown(
        """
        - **🧑‍🦽 Mis pacientes** → Registra y gestiona pacientes.
        - **📅 Sesiones** → Registra sesiones diarias con EVA pre/post.
        - **📈 Reportes** → Descarga datos en Excel o CSV.
        - **📖 Biblioteca clínica** → Repaso rápido de patologías.
        """
    )

    st.markdown("---")
    st.caption("💡 **Tip:** usa los botones del sidebar para navegar. Las flechas del navegador pueden sacarte de la app.")


# ============================================================
# ARRANQUE
# ============================================================
if __name__ == "__main__":
    main()