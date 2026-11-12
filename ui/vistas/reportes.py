"""
ui/vistas/reportes.py
---------------------
Módulo de Reportes y Exportación.
"""

import streamlit as st

from servicios.auth import usuario_actual, es_admin
from repositorios.pacientes_repo import listar_pacientes
from servicios.reportes import (
    pacientes_a_excel,
    pacientes_a_csv,
    sesiones_a_excel,
    reporte_completo_paciente,
    nombre_archivo,
)


def render() -> None:
    st.title("📈 Reportes y Exportación")
    st.caption("Descarga de datos en Excel y CSV.")
    st.markdown("---")

    u = usuario_actual()
    terr_id = None if es_admin() else u["id"]

    # ============================================================
    # SECCIÓN 1: EXPORTAR PACIENTES
    # ============================================================
    st.subheader("📋 Listado de pacientes")

    if es_admin():
        st.info("🔓 Como **admin** puedes descargar TODOS los pacientes de la clínica.")
    else:
        st.info("🔒 Solo puedes descargar TUS pacientes.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Descargar Excel (.xlsx)", use_container_width=True, type="primary", key="btn_pac_excel"):
            st.session_state["preparar_pac_excel"] = True

    with col2:
        if st.button("📥 Descargar CSV", use_container_width=True, key="btn_pac_csv"):
            st.session_state["preparar_pac_csv"] = True

    if st.session_state.get("preparar_pac_excel"):
        try:
            data = pacientes_a_excel(terapeuta_id=terr_id)
            st.download_button(
                label="💾 Guardar Excel de pacientes",
                data=data,
                file_name=nombre_archivo("pacientes", "xlsx"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_pac_excel",
            )
        except Exception as e:
            st.error(f"Error generando Excel: {e}")

    if st.session_state.get("preparar_pac_csv"):
        try:
            data = pacientes_a_csv(terapeuta_id=terr_id)
            st.download_button(
                label="💾 Guardar CSV de pacientes",
                data=data,
                file_name=nombre_archivo("pacientes", "csv"),
                mime="text/csv",
                use_container_width=True,
                key="dl_pac_csv",
            )
        except Exception as e:
            st.error(f"Error generando CSV: {e}")

    st.markdown("---")

    # ============================================================
    # SECCIÓN 2: REPORTE INDIVIDUAL POR PACIENTE
    # ============================================================
    st.subheader("🧑‍🦽 Reporte completo por paciente")
    st.caption("Incluye ficha del paciente + sesiones + evaluaciones en un solo Excel.")

    pacientes = listar_pacientes(terapeuta_id=terr_id, incluir_inactivos=True)

    if not pacientes:
        st.info("No hay pacientes registrados todavía.")
        return

    opciones = {f"{p.nombre_corto} ({p.documento})": p.id for p in pacientes}
    seleccion = st.selectbox("Selecciona un paciente:", options=list(opciones.keys()))

    paciente_id = opciones[seleccion]
    paciente = next((p for p in pacientes if p.id == paciente_id), None)

    if paciente and st.button("📥 Generar reporte completo", type="primary", use_container_width=True, key="btn_rep_completo"):
        try:
            data = reporte_completo_paciente(paciente)
            st.download_button(
                label=f"💾 Guardar reporte de {paciente.nombre_corto}",
                data=data,
                file_name=nombre_archivo(f"reporte_{paciente.documento}", "xlsx"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_rep_completo",
            )
        except Exception as e:
            st.error(f"Error generando reporte: {e}")

    st.markdown("---")

    # ============================================================
    # SECCIÓN 3: SESIONES DE UN PACIENTE
    # ============================================================
    st.subheader("📅 Sesiones de un paciente")
    st.caption("Descarga solo el historial de sesiones en Excel.")

    opciones2 = {f"{p.nombre_corto} ({p.documento})": p.id for p in pacientes}
    seleccion2 = st.selectbox("Selecciona un paciente:", options=list(opciones2.keys()), key="sel_sesiones_pac")

    if st.button("📥 Generar Excel de sesiones", use_container_width=True, key="btn_ses_excel"):
        try:
            data = sesiones_a_excel(opciones2[seleccion2])
            st.download_button(
                label="💾 Guardar Excel de sesiones",
                data=data,
                file_name=nombre_archivo("sesiones", "xlsx"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_ses_excel",
            )
        except Exception as e:
            st.error(f"Error generando Excel: {e}")