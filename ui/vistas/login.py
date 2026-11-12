"""
ui/vistas/login.py
------------------
Pantalla de inicio de sesión de Sayari Med.
Diseño sincronizado con la página web oficial.
"""

import streamlit as st
from pathlib import Path
from PIL import Image

from servicios.auth import autenticar, iniciar_sesion, esta_logueado
from config.settings import APP_NAME

def render() -> None:
    if esta_logueado():
        st.rerun()
        return

    st.markdown("""
    <style>
    /* 1. ELIMINAMOS EL ENCABEZADO FANTASMA Y LOS MÁRGENES */
    header, footer {
        display: none !important;
    }
    
    .block-container {
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important;
        margin-top: 2vh !important; /* Sube todo el bloque un 2% del alto de pantalla */
    }

    /* Fondo */
    .stApp {
        background-color: #050B14;
        background-image: 
            radial-gradient(circle at 50% 0%, #112240 0%, transparent 60%),
            linear-gradient(0deg, rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
        background-size: 100% 100%, 40px 40px, 40px 40px;
        background-position: center top;
    }

    /* Textos */
    .login-title {
        color: #FFFFFF;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 0.2rem;
    }
    .login-title span {
        color: #F7C948; 
    }
    .login-subtitle {
        color: #8CA3C7;
        font-size: 0.9rem;
        letter-spacing: 2px;
        text-align: center;
        margin-bottom: 2rem;
        text-transform: uppercase;
    }

    /* Etiquetas (USUARIO y CONTRASEÑA) */
    div[data-testid="stTextInput"] label {
        color: #FFFFFF !important; 
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 1px !important;
        margin-bottom: 5px !important;
    }

    /* Inputs (Cajas de texto) */
    div[data-testid="stTextInput"] input {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(140, 163, 199, 0.4) !important;
        border-radius: 8px !important;
        padding: 12px 15px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #A0B2C6 !important; 
        opacity: 1; 
    }
    div[data-testid="stTextInput"] input:focus {
        background-color: rgba(255, 255, 255, 0.12) !important;
        border-color: #F7C948 !important;
        box-shadow: 0 0 10px rgba(247, 201, 72, 0.3) !important;
    }

    /* Cristal del formulario */
    div[data-testid="stForm"] {
        background: rgba(17, 34, 64, 0.6);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    }

    /* Botón */
    button[kind="primary"] {
        background: linear-gradient(135deg, #F7C948 0%, #E6B325 100%) !important;
        color: #050B14 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        border-radius: 30px !important; 
        border: none !important;
        padding: 12px 0 !important;
        margin-top: 1rem;
        box-shadow: 0 4px 15px rgba(247, 201, 72, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(247, 201, 72, 0.7) !important;
        transform: translateY(-2px) !important;
    }

    /* =========================================
       AJUSTES PARA CELULAR (Aquí arreglamos el logo)
       ========================================= */
    @media (max-width: 768px) {
        .block-container {
            margin-top: 1vh !important;
        }
        .login-title {
            font-size: 2rem !important;
        }
        .login-subtitle {
            font-size: 0.75rem !important;
            margin-bottom: 1.5rem !important;
        }
        div[data-testid="stForm"] {
            padding: 1.5rem !important;
        }
        /* Obliga al logo a ser pequeño y centrado en móviles */
        div[data-testid="stImage"] {
            display: flex;
            justify-content: center;
        }
        div[data-testid="stImage"] img {
            max-width: 160px !important; 
        }
    }
    </style>
    """, unsafe_allow_html=True)

    col_izq, col_centro, col_der = st.columns([1, 1.2, 1])

    with col_centro:
        ruta_logo = Path(__file__).resolve().parent.parent.parent / "assets" / "logo-icono.png"
        if ruta_logo.exists():
            # Usamos columnas, pero el CSS de arriba se encargará de que en celular no se desborde
            _, col_img, _ = st.columns([1, 2, 1])
            with col_img:
                st.image(str(ruta_logo), use_container_width=True)
            
        st.markdown('<div class="login-title">SAYARI <span>MED</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Sistema Integral de Gestión Clínica</div>', unsafe_allow_html=True)

        with st.form("form_login_tech", clear_on_submit=False):
            usuario = st.text_input("USUARIO", placeholder="Ingresa tu DNI o usuario")
            password = st.text_input("CONTRASEÑA", type="password", placeholder="Ingresa tu contraseña")
            
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True, type="primary")

        if submit:
            if not usuario or not password:
                st.warning("⚠️ Por favor, ingresa tus credenciales.")
            else:
                with st.spinner("Verificando identidad..."):
                    user = autenticar(usuario, password)
                
                if user:
                    iniciar_sesion(user)
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Acceso denegado.")

        st.markdown("""
        <div style="text-align: center; color: #5C7294; font-size: 0.75rem; margin-top: 2rem;">
            SAYARI MED v1.0 · CONEXIÓN SEGURA ENCRIPTADA<br>
            © 2026 Sayari Clínica
        </div>
        """, unsafe_allow_html=True)