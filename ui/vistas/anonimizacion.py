"""
ui/vistas/anonimizacion.py
--------------------------
Módulo de Anonimización para Investigación.

Solo accesible para ADMIN.
"""

import streamlit as st
import pandas as pd
from io import BytesIO

from repositorios.pacientes_repo import listar_pacientes
from servicios.anonimizacion import (
    asignar_a_todos,
    export_investigacion_excel,
    export_sesiones_anonimas_excel,
    nombre_archivo_anon,
)
from servicios.reportes import nombre_archivo


def render() -> None:
    st.title("🔬 Anonimización para Investigación")
    st.caption("Exporta datos clínicos sin información personal. Ideal para tesis, papers y estudios.")
    st.markdown("---")

    # ============================================================
    # ALERTA ÉTICA
    # ============================================================
    st.warning(
        "⚠️ **Importante sobre ética y privacidad:**\n"
        "- La tabla puente (Paciente ↔ ID anónimo) **solo** debe verla el administrador.\n"
        "- Los exports de investigación **NO contienen** nombre, DNI, teléfono, correo ni dirección.\n"
        "- Para publicar o compartir datos, **usa solo** los archivos anonimizados.\n"
        "- Conserva la tabla puente en un lugar seguro (Ley 29733 - Perú)."
    )

    st.markdown("---")

    # ============================================================
    # SECCIÓN 1: ESTADO DE ANONIMIZACIÓN
    # ============================================================
    st.subheader("📊 Estado de anonimización")

    pacientes = listar_pacientes(incluir_inactivos=True)
    total = len(pacientes)
    con_id = sum(1 for p in pacientes if p.id_anonimo)
    sin_id = total - con_id

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total pacientes", total)
    with col2:
        st.metric("Con ID anónimo", con_id)
    with col3:
        st.metric("Sin ID anónimo", sin_id)

    if sin_id > 0:
        st.info(f"Hay **{sin_id}** paciente(s) sin ID anónimo. Puedes asignarlos automáticamente.")
        if st.button("🔧 Asignar IDs a todos los pendientes", type="primary", use_container_width=True, key="btn_asignar_todos"):
            cantidad = asignar_a_todos()
            st.success(f"✅ Se asignaron {cantidad} IDs anónimos.")
            st.rerun()
    else:
        st.success("✅ Todos los pacientes tienen ID anónimo.")

    st.markdown("---")

    # ============================================================
    # SECCIÓN 2: TABLA PUENTE
    # ============================================================
    st.subheader("🔗 Tabla puente (solo admin)")
    st.caption("Esta tabla relaciona al paciente real con su ID anónimo. **NO compartir públicamente.**")

    if not pacientes:
        st.info("No hay pacientes registrados.")
        return

    datos = []
    for p in pacientes:
        datos.append({
            "ID anónimo": p.id_anonimo or "⚠️ Sin asignar",
            "DNI": p.documento,
            "Nombre": p.nombre_completo,
            "Edad": p.edad,
            "Categoría": p.categoria_patologica,
        })

    df = pd.DataFrame(datos)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Generar Excel de la tabla puente (pre-generado)
    output_tp = BytesIO()
    with pd.ExcelWriter(output_tp, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Tabla_puente", index=False)
    output_tp.seek(0)

    st.download_button(
        label="📥 Descargar tabla puente (uso interno)",
        data=output_tp.getvalue(),
        file_name=nombre_archivo("tabla_puente_CONFIDENCIAL", "xlsx"),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="dl_tabla_puente",
    )

    st.caption("💡 Descarga esta tabla solo para tu archivo personal. NO la incluyas en publicaciones.")

    st.markdown("---")

    # ============================================================
    # SECCIÓN 3: EXPORTS DE INVESTIGACIÓN
    # ============================================================
    st.subheader("📥 Exports para investigación")
    st.caption("Estos archivos son **seguros** para compartir con tutores, jurados o publicaciones.")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**🔬 Dataset de pacientes (anonimizado)**")
        st.caption("Incluye: ID anónimo, edad, sexo, ocupación, categoría, diagnóstico, sesiones, EVA inicial/final, mejora.")

        # Pre-generar el dataset
        try:
            data_dataset = export_investigacion_excel()
            st.download_button(
                label="📥 Descargar dataset",
                data=data_dataset,
                file_name=nombre_archivo_anon("xlsx"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_dataset",
                type="primary",
            )
        except Exception as e:
            st.error(f"Error generando dataset: {e}")

    with col_b:
        st.markdown("**📅 Dataset de sesiones (anonimizado)**")
        st.caption("Incluye: ID anónimo, N° sesión, fecha, EVA pre/post, mejora, procedimientos, tolerancia.")

        try:
            data_sesiones = export_sesiones_anonimas_excel()
            st.download_button(
                label="📥 Descargar sesiones",
                data=data_sesiones,
                file_name=nombre_archivo_anon("xlsx").replace("investigacion", "sesiones"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_sesiones_anon",
                type="primary",
            )
        except Exception as e:
            st.error(f"Error generando sesiones: {e}")

    st.markdown("---")
    st.caption(
        "📌 **Recomendación:** antes de enviar un dataset a tu tutor o jurado, "
        "ábrelo y verifica que NO contenga columnas con nombre, DNI, teléfono ni correo."
    )