"""
ui/estilos.py
-------------
Estilos CSS globales de Sayari Med.

- Azul marino corporativo (#112240).
- Dorado Sayari (#C9A961) como acento premium.
- Touch-friendly para iPad/móvil.
- Modo PWA-ready.
"""

import streamlit as st
from config.settings import (
    COLOR_PRIMARIO,
    COLOR_FONDO,
    COLOR_TEXTO,
    COLOR_ACENTO,
)

COLOR_DORADO = "#C9A961"
COLOR_DORADO_HOVER = "#B8935A"


def aplicar_estilos() -> None:
    """Inyecta el CSS global en la app."""
    st.markdown(
        f"""
        <style>
        /* ============================================================
           VARIABLES Y BASE
           ============================================================ */
        :root {{
            --sayari-azul: {COLOR_PRIMARIO};
            --sayari-dorado: {COLOR_DORADO};
            --sayari-dorado-hover: {COLOR_DORADO_HOVER};
            --sayari-fondo: {COLOR_FONDO};
            --sayari-acento: {COLOR_ACENTO};
        }}

        .stApp {{
            background-color: {COLOR_FONDO};
            color: {COLOR_TEXTO};
        }}

        /* ============================================================
           TIPOGRAFÍA
           ============================================================ */
        html, body, [class*="css"] {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                         "Helvetica Neue", Arial, sans-serif;
        }}
        h1, h2, h3, h4 {{
            color: {COLOR_PRIMARIO};
            letter-spacing: -0.02em;
        }}
        h1 {{
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.3rem !important;
        }}
        h2 {{
            font-size: 1.6rem !important;
            font-weight: 600 !important;
        }}
        h3 {{
            font-size: 1.25rem !important;
            font-weight: 600 !important;
        }}

        /* ============================================================
           BOTONES PRIMARIOS (azul marino Sayari)
           ============================================================ */
        button[kind="primary"],
        button[kind="primaryFormSubmit"],
        .stButton button[kind="primary"],
        .stFormSubmitButton button[kind="primary"] {{
            background-color: {COLOR_PRIMARIO} !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 3px 10px rgba(17, 34, 64, 0.25) !important;
            transition: all 0.2s ease !important;
        }}
        button[kind="primary"]:hover,
        button[kind="primaryFormSubmit"]:hover,
        .stButton button[kind="primary"]:hover,
        .stFormSubmitButton button[kind="primary"]:hover {{
            background-color: {COLOR_ACENTO} !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(17, 34, 64, 0.35) !important;
        }}
        button[kind="primary"]:active {{
            transform: translateY(0);
        }}

        /* ============================================================
           BOTONES SECUNDARIOS
           ============================================================ */
        .stButton button {{
            background-color: #FFFFFF;
            color: {COLOR_PRIMARIO};
            border: 2px solid {COLOR_PRIMARIO};
            border-radius: 10px;
            padding: 0.7rem 1.5rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.2s ease;
            min-height: 48px;
        }}
        .stButton button:hover {{
            background-color: {COLOR_PRIMARIO};
            color: #FFFFFF;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(17, 34, 64, 0.15);
        }}

        /* ============================================================
           SIDEBAR
           ============================================================ */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COLOR_PRIMARIO} 0%, #0D1A33 100%);
        }}
        section[data-testid="stSidebar"] * {{
            color: #FFFFFF !important;
        }}
        section[data-testid="stSidebar"] img {{
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }}
        section[data-testid="stSidebar"] h4 {{
            color: {COLOR_DORADO} !important;
            font-size: 0.85rem !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
        }}
        section[data-testid="stSidebar"] .stButton button {{
            background-color: rgba(255, 255, 255, 0.08);
            color: #FFFFFF;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            width: 100%;
            font-weight: 500;
            font-size: 0.95rem;
            padding: 0.6rem 1rem;
            min-height: 44px;
            text-align: left;
            transition: all 0.15s ease;
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{
            background-color: {COLOR_DORADO};
            color: {COLOR_PRIMARIO} !important;
            border-color: {COLOR_DORADO};
            transform: translateX(4px);
        }}

        /* ============================================================
           INPUTS
           ============================================================ */
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox select,
        .stTextArea textarea {{
            border-radius: 10px;
            border: 2px solid #E0E4EB;
            padding: 0.7rem;
            font-size: 1rem;
            min-height: 48px;
            background-color: #FFFFFF;
            transition: all 0.2s ease;
        }}
        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stTextArea textarea:focus {{
            border-color: {COLOR_ACENTO};
            box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.15);
            outline: none;
        }}

        /* ============================================================
           MÉTRICAS / TARJETAS
           ============================================================ */
        div[data-testid="stMetric"] {{
            background-color: #FFFFFF;
            border-left: 5px solid {COLOR_DORADO};
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 2px 12px rgba(17, 34, 64, 0.08);
            transition: all 0.2s ease;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(17, 34, 64, 0.12);
        }}
        div[data-testid="stMetricLabel"] {{
            color: #6B7280 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        div[data-testid="stMetricValue"] {{
            color: {COLOR_PRIMARIO} !important;
            font-weight: 700 !important;
        }}

        /* ============================================================
           TABS
           ============================================================ */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            border-bottom: 2px solid #E0E4EB;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent;
            border-radius: 10px 10px 0 0;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            color: #6B7280;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {COLOR_PRIMARIO} !important;
            color: #FFFFFF !important;
        }}

        /* ============================================================
           ALERTAS
           ============================================================ */
        div[data-testid="stAlert"] {{
            border-radius: 12px;
            border-left-width: 5px;
        }}

        /* ============================================================
           EXPANDERS
           ============================================================ */
        .streamlit-expanderHeader {{
            background-color: #FFFFFF;
            border-radius: 10px;
            font-weight: 600;
            color: {COLOR_PRIMARIO};
        }}

        /* ============================================================
           TABLAS
           ============================================================ */
        .stDataFrame {{
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(17, 34, 64, 0.05);
        }}

        /* ============================================================
           LOGIN
           ============================================================ */
        .login-card {{
            background-color: #FFFFFF;
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(17, 34, 64, 0.12);
            max-width: 450px;
            margin: 2rem auto;
        }}
        .login-title {{
            color: {COLOR_PRIMARIO};
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.3rem;
        }}
        .login-subtitle {{
            color: #6B7280;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 0.95rem;
        }}

        /* ============================================================
           DIVIDER
           ============================================================ */
        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #E0E4EB, transparent);
            margin: 1.5rem 0;
        }}

        /* ============================================================
           SCROLLBAR (más elegante)
           ============================================================ */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #C9CFD8;
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {COLOR_PRIMARIO};
        }}

        /* ============================================================
           RESPONSIVE (móvil/tablet)
           ============================================================ */
        @media (max-width: 768px) {{
            h1 {{ font-size: 1.7rem !important; }}
            h2 {{ font-size: 1.3rem !important; }}
            .stButton button {{ width: 100%; }}
            .login-card {{ padding: 1.5rem; margin: 1rem auto; }}
            div[data-testid="stMetric"] {{ padding: 0.8rem; }}
            .stTabs [data-baseweb="tab"] {{ padding: 0.6rem 1rem; font-size: 0.9rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )