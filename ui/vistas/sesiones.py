"""
ui/vistas/sesiones.py
---------------------
Módulo de Sesiones de rehabilitación.

- Registrar sesión diaria para un paciente.
- Ver historial + gráfico de evolución del dolor (EVA pre vs post).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from servicios.auth import usuario_actual
from repositorios.pacientes_repo import obtener_por_id, listar_pacientes
from repositorios.sesiones_repo import (
    listar_por_paciente,
    crear_sesion,
    contar_por_paciente,
)
from config.constants import PROCEDIMIENTOS


# ============================================================
# HELPERS
# ============================================================
def _obtener_paciente_actual():
    """Devuelve el paciente actual o None."""
    paciente_id = st.session_state.get("paciente_actual_id")
    if not paciente_id:
        return None
    return obtener_por_id(paciente_id)


# ============================================================
# VISTA: SELECCIÓN DE PACIENTE
# ============================================================
def _render_seleccion():
    st.subheader("📅 Módulo de Sesiones")
    st.caption("Selecciona un paciente para ver o registrar sus sesiones.")

    u = usuario_actual()
    terapeuta_id = None if u["rol"] == "admin" else u["id"]
    pacientes = listar_pacientes(terapeuta_id=terapeuta_id)

    if not pacientes:
        st.info("No hay pacientes registrados. Crea uno primero en el módulo Pacientes.")
        return

    # ---------- Lista de pacientes ----------
    datos = []
    for p in pacientes:
        total_ses = contar_por_paciente(p.id)
        datos.append({
            "ID": p.id,
            "Documento": p.documento,
            "Nombre": p.nombre_corto,
            "Sesiones": total_ses,
            "Estado": "✅ Activo" if p.activo else "⛔ Inactivo",
        })

    df = pd.DataFrame(datos)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ---------- Seleccionar ----------
    st.markdown("#### 👁️ Ver sesiones")
    opciones = {f"{p.nombre_corto} ({p.documento})": p.id for p in pacientes}
    seleccion = st.selectbox("Paciente:", options=list(opciones.keys()))

    if st.button("Abrir historial de sesiones", type="primary", use_container_width=True):
        st.session_state["paciente_actual_id"] = opciones[seleccion]
        st.rerun()


# ============================================================
# VISTA: HISTORIAL + REGISTRO
# ============================================================
def _render_historial():
    paciente = _obtener_paciente_actual()
    if not paciente:
        st.error("No se encontró el paciente.")
        if st.button("← Atrás"):
            st.session_state.pop("paciente_actual_id", None)
            st.rerun()
        return

    # ---------- Botón volver ----------
    if st.button("← Volver a selección"):
        st.session_state.pop("paciente_actual_id", None)
        st.rerun()

    # ---------- Encabezado ----------
    st.markdown(f"### 📅 Sesiones de {paciente.nombre_completo}")
    st.caption(f"DNI: `{paciente.documento}` · Total sesiones: {contar_por_paciente(paciente.id)}")

    st.markdown("---")

    # ---------- Tabs: Historial / Registrar ----------
    tab1, tab2 = st.tabs(["📊 Historial y evolución", "➕ Registrar nueva sesión"])

    with tab1:
        _render_tab_historial(paciente)

    with tab2:
        _render_tab_registrar(paciente)


# ============================================================
# TAB 1: HISTORIAL + GRÁFICO
# ============================================================
def _render_tab_historial(paciente):
    sesiones = listar_por_paciente(paciente.id)

    if not sesiones:
        st.info("Aún no hay sesiones registradas. Usa la pestaña **➕ Registrar nueva sesión**.")
        return

    # ---------- Gráfico de evolución del dolor ----------
    datos_graf = []
    for s in sesiones:
        if s.eva_pre is not None:
            datos_graf.append({
                "Sesión": f"#{s.numero_sesion}",
                "Fecha": s.fecha_sesion,
                "EVA": s.eva_pre,
                "Tipo": "Pre-sesión",
            })
        if s.eva_post is not None:
            datos_graf.append({
                "Sesión": f"#{s.numero_sesion}",
                "Fecha": s.fecha_sesion,
                "EVA": s.eva_post,
                "Tipo": "Post-sesión",
            })

    if datos_graf:
        df = pd.DataFrame(datos_graf)
        fig = px.line(
            df,
            x="Sesión",
            y="EVA",
            color="Tipo",
            markers=True,
            title="📉 Evolución del dolor (EVA)",
            color_discrete_map={"Pre-sesión": "#E74C3C", "Post-sesión": "#27AE60"},
        )
        fig.update_layout(
            yaxis_range=[0, 10],
            yaxis_title="EVA (0-10)",
            xaxis_title="Sesión",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------- Tabla de sesiones ----------
    st.markdown("#### 📋 Detalle de sesiones")
    datos = []
    for s in sesiones:
        datos.append({
            "N°": s.numero_sesion,
            "Fecha": s.fecha_sesion,
            "EVA pre": s.eva_pre if s.eva_pre is not None else "—",
            "EVA post": s.eva_post if s.eva_post is not None else "—",
            "Mejora": f"↓ {s.mejora_dolor:.1f}" if s.mejora_dolor > 0 else "—",
            "Tolerancia": s.tolerancia or "—",
        })
    st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)

    # ---------- Detalle expandible por sesión ----------
    st.markdown("#### 🔍 Ver detalle")
    for s in sesiones:
        with st.expander(f"Sesión #{s.numero_sesion} — {s.fecha_sesion}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**EVA pre:** {s.eva_pre if s.eva_pre is not None else '—'}")
                st.markdown(f"**EVA post:** {s.eva_post if s.eva_post is not None else '—'}")
            with col2:
                st.markdown(f"**Mejora:** {'↓ ' + str(round(s.mejora_dolor, 1)) if s.mejora_dolor > 0 else '—'}")
                st.markdown(f"**Tolerancia:** {s.tolerancia or '—'}")

            if s.procedimientos:
                st.markdown(f"**Procedimientos:** {s.procedimientos}")
            if s.respuesta_paciente:
                st.markdown(f"**Respuesta del paciente:** {s.respuesta_paciente}")
            if s.observaciones:
                st.markdown(f"**Observaciones:** {s.observaciones}")


# ============================================================
# TAB 2: REGISTRAR NUEVA SESIÓN
# ============================================================
def _render_tab_registrar(paciente):
    st.markdown("#### Registrar sesión de hoy")

    with st.form("form_nueva_sesion", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**😣 Dolor ANTES de la sesión**")
            eva_pre = st.slider(
                "EVA pre",
                min_value=0.0, max_value=10.0, value=5.0, step=0.5,
                key="eva_pre_slider",
                label_visibility="collapsed",
            )

        with col2:
            st.markdown("**😊 Dolor DESPUÉS de la sesión**")
            eva_post = st.slider(
                "EVA post",
                min_value=0.0, max_value=10.0, value=5.0, step=0.5,
                key="eva_post_slider",
                label_visibility="collapsed",
            )

        st.markdown("---")
        st.markdown("**🏋️ Procedimientos aplicados**")
        procedimientos_sel = st.multiselect(
            "Selecciona los procedimientos:",
            options=PROCEDIMIENTOS,
            default=[],
            label_visibility="collapsed",
        )

        st.markdown("---")
        col_a, col_b = st.columns(2)

        with col_a:
            tolerancia = st.selectbox(
                "Tolerancia a la carga",
                options=["—", "Buena", "Regular", "Mala"],
            )

        with col_b:
            pass  # Espacio

        respuesta_paciente = st.text_area(
            "Respuesta del paciente",
            placeholder="Ej: Refiere mejoría tras la sesión...",
            height=80,
        )

        observaciones = st.text_area(
            "Observaciones del terapeuta",
            placeholder="Ej: Buena respuesta a electroterapia...",
            height=80,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_x, col_y, col_z = st.columns([1, 2, 1])
        with col_y:
            guardar = st.form_submit_button(
                "💾 Guardar sesión",
                use_container_width=True,
                type="primary",
            )

    # ---------- Lógica ----------
    if guardar:
        u = usuario_actual()
        procedimientos_str = ", ".join(procedimientos_sel) if procedimientos_sel else None

        nueva = crear_sesion(
            paciente_id=paciente.id,
            terapeuta_id=u["id"],
            eva_pre=eva_pre,
            eva_post=eva_post,
            procedimientos=procedimientos_str,
            respuesta_paciente=respuesta_paciente or None,
            tolerancia=None if tolerancia == "—" else tolerancia,
            observaciones=observaciones or None,
        )

        st.session_state["mensaje_sesion"] = (
            f"✅ Sesión #{nueva.numero_sesion} registrada. "
            f"Mejora del dolor: ↓ {nueva.mejora_dolor:.1f} puntos."
        )
        st.rerun()

    # Mensaje persistente
    if st.session_state.get("mensaje_sesion"):
        st.success(st.session_state["mensaje_sesion"])
        del st.session_state["mensaje_sesion"]


# ============================================================
# RENDER PRINCIPAL
# ============================================================
def render() -> None:
    """Muestra selección de paciente o su historial de sesiones."""
    st.title("📅 Módulo de Sesiones")
    st.markdown("---")

    if st.session_state.get("paciente_actual_id"):
        _render_historial()
    else:
        _render_seleccion()