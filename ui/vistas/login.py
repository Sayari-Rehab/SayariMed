"""
ui/vistas/login.py
------------------
Pantalla de inicio de sesión de Sayari Med.

Es lo primero que ve el usuario al abrir la app.
Si las credenciales son válidas, guarda al usuario en la sesión
y recarga la página para que el router principal muestre el dashboard.
"""

import streamlit as st
from pathlib import Path
from PIL import Image

from servicios.auth import (
    autenticar,
    iniciar_sesion,
    esta_logueado,
)
from config.settings import APP_NAME, APP_VERSION


def render() -> None:
    """Dibuja la pantalla de login."""

    # Si ya está logueado, no mostrar login
    if esta_logueado():
        st.rerun()
        return

    # ---------- Espacio en blanco arriba ----------
    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- Tarjeta de login ----------
    col_izq, col_centro, col_der = st.columns([1, 2, 1])

    with col_centro:
        # Logo principal (arriba del todo)
        ruta_logo = Path(__file__).resolve().parent.parent.parent / "assets" / "logo_principal.png"
        if ruta_logo.exists():
            col_logo_a, col_logo_b, col_logo_c = st.columns([1, 2, 1])
            with col_logo_b:
                st.image(str(ruta_logo), use_container_width=True)

        # Subtítulo debajo del logo
        st.markdown(
            """
            <div class="login-subtitle" style="margin-bottom: 2rem;">
                Sistema Integral de Gestión Clínica & Fisioterapia
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ---------- Formulario ----------
        with st.form("form_login", clear_on_submit=False):
            username = st.text_input(
                "👤 Usuario",
                placeholder="Escribe tu usuario",
                key="login_username",
            )
            password = st.text_input(
                "🔒 Contraseña",
                type="password",
                placeholder="Escribe tu contraseña",
                key="login_password",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                enviado = st.form_submit_button(
                    "Ingresar",
                    use_container_width=True,
                    type="primary",
                )

        # ---------- Lógica ----------
        if enviado:
            if not username or not password:
                st.warning("⚠️ Completa usuario y contraseña.")
            else:
                with st.spinner("Verificando credenciales..."):
                    usuario = autenticar(username, password)

                if usuario:
                    iniciar_sesion(usuario)
                    st.success(f"✅ Bienvenido, {usuario.nombre_completo}")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")

        # ---------- Pie de página ----------
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="text-align:center; color:#6B7280; font-size:0.85rem;">
                {APP_NAME} v{APP_VERSION} — Acceso restringido al personal autorizado
            </div>
            """,
            unsafe_allow_html=True,
        )