"""
ui/vistas/pacientes.py
----------------------
Módulo de Pacientes.
"""

import streamlit as st
import pandas as pd
from datetime import date

# --- NUEVOS IMPORTS PARA AMARU / LIENZO / MATEMÁTICAS ---
import math
import io # <--- NUEVO
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from pathlib import Path
import time
# --------------------------------------------------------

from servicios.auth import usuario_actual, es_admin
from servicios.motor_clinico import (
    recomendar_tests, agrupar_tests_por_prioridad, etiqueta_prioridad,
    obtener_escalas_dinamicas_por_patologia,
    obtener_escalas_universales,
)
from repositorios.pacientes_repo import (
    listar_pacientes, buscar_paciente, crear_paciente, existe_documento,
    obtener_por_id, agregar_patologia_a_paciente, listar_patologias_de_paciente,
    remover_patologia_de_paciente,
)
from repositorios.evaluaciones_repo import (
    guardar_evaluaciones_masivo, tests_aplicados_ids, listar_por_paciente,
)
from repositorios.patologias_repo import listar_patologias, buscar_por_nombre, crear_patologia
from config.constants import CATEGORIAS_PATOLOGICAS, ICONOS_CATEGORIA, SEXOS


# ============================================================
# HELPERS
# ============================================================
def _filtro_terapeuta():
    u = usuario_actual()
    return None if es_admin() else (u["id"] if u else None)


# ============================================================
# VISTA: LISTA DE PACIENTES
# ============================================================
def _render_lista():
    st.subheader("🧑‍🦽 Mis pacientes")
    col_busq, col_btn = st.columns([3, 1])
    with col_busq:
        termino = st.text_input("🔍 Buscar por DNI o nombre", placeholder="Escribe documento o nombre...", key="pac_busqueda")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Nuevo paciente", use_container_width=True, type="primary"):
            st.session_state["vista_pacientes"] = "nuevo"
            st.rerun()

    terr_id = _filtro_terapeuta()
    pacientes = buscar_paciente(termino, terapeuta_id=terr_id) if termino.strip() else listar_pacientes(terapeuta_id=terr_id)

    if not pacientes:
        st.info("No se encontraron pacientes o aún no tienes registrados.")
        return

    datos = []
    for p in pacientes:
        icono = ICONOS_CATEGORIA.get(p.categoria_patologica, "🩺")
        datos.append({
            "ID": p.id, "Documento": p.documento, "Nombre": p.nombre_corto,
            "Edad": p.edad or "—", "Sexo": p.sexo or "—",
            "Categoría": f"{icono} {p.categoria_patologica}",
            "Diagnóstico": "✅ Sí" if p.tiene_diagnostico else "❌ No",
            "Estado": "✅ Activo" if p.activo else "⛔ Inactivo",
        })
    st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)

    st.markdown("#### 🔧 Acciones rápidas")
    for p in pacientes:
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.markdown(f"**{p.nombre_completo}** — Doc: `{p.documento}`")
        with col_b:
            if st.button("👁️ Ver", key=f"ver_pac_{p.id}", use_container_width=True):
                st.session_state["paciente_detalle_id"] = p.id
                st.session_state["vista_pacientes"] = "detalle"
                st.rerun()


# ============================================================
# VISTA: DETALLE DEL PACIENTE
# ============================================================
def _render_detalle():
    paciente_id = st.session_state.get("paciente_detalle_id")
    if not paciente_id:
        st.error("No se encontró el paciente.")
        if st.button("⬅️ Volver"): st.session_state["vista_pacientes"] = "lista"; st.rerun()
        return

    paciente = obtener_por_id(paciente_id)
    if not paciente:
        st.error("Paciente no encontrado.")
        if st.button("⬅️ Volver"): st.session_state["vista_pacientes"] = "lista"; st.rerun()
        return

    col_volver, col_sesiones, _ = st.columns([1, 1, 2])
    with col_volver:
        if st.button("⬅️ Volver al listado", use_container_width=True):
            st.session_state["vista_pacientes"] = "lista"; st.rerun()
    with col_sesiones:
        if st.button("📅 Ver sesiones", use_container_width=True, type="primary"):
            st.session_state["paciente_actual_id"] = paciente.id
            st.session_state["vista_clinica"] = "sesiones"
            st.session_state.pop("vista_pacientes", None)
            st.rerun()

    st.markdown("---")
    st.markdown(f"### {paciente.nombre_completo} (`{paciente.documento}`)")
    
    with st.expander("📋 Datos completos", expanded=True):
        st.markdown(f"**Edad:** {paciente.edad or '—'} | **Sexo:** {paciente.sexo or '—'} | **Teléfono:** {paciente.telefono or '—'}")
        if paciente.diagnostico_medico:
            st.markdown(f"**Diagnóstico Principal:** {paciente.diagnostico_medico}")

    with st.expander("🏷️ Otros Diagnósticos / Patologías Asociadas", expanded=False):
        patologias_actuales = listar_patologias_de_paciente(paciente.id)
        if patologias_actuales:
            for p_act in patologias_actuales:
                col_p, col_btn = st.columns([4, 1])
                with col_p: st.markdown(f"- {ICONOS_CATEGORIA.get(p_act.categoria, '🩺')} **{p_act.nombre}**")
                with col_btn:
                    if st.button("🗑️ Quitar", key=f"rm_pat_{p_act.id}"):
                        remover_patologia_de_paciente(paciente.id, p_act.id); st.rerun()
        else:
            st.info("No hay patologías secundarias registradas.")

        st.markdown("---")
        patologias_disponibles = [p for p in listar_patologias() if p.id not in [pa.id for pa in patologias_actuales]]
        if patologias_disponibles:
            opciones = {f"{p.nombre} ({p.categoria})": p.id for p in patologias_disponibles}
            seleccion = st.selectbox("Agregar patología de la biblioteca:", options=list(opciones.keys()))
            if st.button("➕ Enlazar Patología"):
                agregar_patologia_a_paciente(paciente.id, opciones[seleccion]); st.rerun()

    st.markdown("---")

    # ============================================================
    # ESCALAS UNIVERSALES Y DINÁMICAS (SIN st.form PARA AMARU)
    # ============================================================
    escalas_universales = obtener_escalas_universales()
    escalas_personalizadas = obtener_escalas_dinamicas_por_patologia(paciente.diagnostico_medico) if paciente.diagnostico_medico else []
    
    if escalas_universales or escalas_personalizadas:
        st.markdown("### 📊 Evaluaciones Clínicas")
        
        # Diccionario para acumular resultados antes de guardar
        resultados_escalas = {}
        
        # --- 1. BLOQUE UNIVERSAL ---
        if escalas_universales:
            st.markdown("#### 🌍 Evaluaciones Universales (Aplican a todos)")
            for esc_data in escalas_universales:
                escala = esc_data["escala"]
                with st.expander(f"📋 {escala.nombre}", expanded=True):
                    puntaje_total = 0
                    for sec_data in esc_data["secciones"]:
                        for item in sec_data["items"]:
                            if item.puntaje_maximo > 0:
                                val = st.number_input(f"{item.nombre} (Max {item.puntaje_maximo})", min_value=0, max_value=item.puntaje_maximo, value=0, key=f"univ_{paciente.id}_{escala.id}_{item.id}")
                                puntaje_total += val
                            else:
                                st.text_input(f"{item.nombre}", key=f"univ_txt_{paciente.id}_{escala.id}_{item.id}")
                    if puntaje_total > 0:
                        st.info(f"Puntaje: {puntaje_total} pts")
                    resultados_escalas[escala.nombre] = str(puntaje_total)
            st.markdown("---")

            # --- 2. BLOQUE POR PATOLOGÍA (Nueva Jerarquía) ---
            if escalas_personalizadas:
                grupos_ev = {"Obligatoria": [], "Sugerida": [], "Adicional": []}
                for e in escalas_personalizadas:
                    grupos_ev[e["tipo"]].append(e)

                meta_ev = {
                    "Obligatoria": ("🔴 Evaluaciones Obligatorias", "Debes aplicar estas pruebas por protocolo."),
                    "Sugerida": ("🟡 Evaluaciones Sugeridas", "Recomendadas para una evaluación completa."),
                    "Adicional": ("🟢 Evaluaciones Adicionales", "Opcionales, según el tiempo disponible.")
                }

                for tipo in ["Obligatoria", "Sugerida", "Adicional"]:
                    if not grupos_ev[tipo]: continue
                    titulo, desc = meta_ev[tipo]
                    st.markdown(f"#### {titulo}")
                    st.caption(desc)
                    
                    for ev_data in grupos_ev[tipo]:
                        ev_maestra = ev_data["evaluacion_maestra"]
                        
                        # El paraguas principal (La Evaluación)
                        with st.expander(f"📑 {ev_maestra.nombre}", expanded=(tipo == "Obligatoria")):
                            if ev_maestra.descripcion:
                                st.caption(ev_maestra.descripcion)
                                
                            # Iteramos por cada escala dentro de esta evaluación
                            for esc_data in ev_data["escalas"]:
                                escala = esc_data["escala"]
                                st.markdown(f"**🔹 {escala.nombre}**")
                                
                                puntaje_total = 0
                                for sec_data in esc_data["secciones"]:
                                    for item in sec_data["items"]:
                                        col_res, col_cam = st.columns([3, 1])
                                        
                                        with col_res:
                                            if item.puntaje_maximo > 0:
                                                val = st.number_input(f"{item.nombre} (Max {item.puntaje_maximo})", min_value=0, max_value=item.puntaje_maximo, value=0, key=f"pat_{paciente.id}_{escala.id}_{item.id}")
                                                puntaje_total += val
                                            else:
                                                st.text_input(f"{item.nombre}", key=f"pat_txt_{paciente.id}_{escala.id}_{item.id}", placeholder="Escribe el resultado...")
                                                
                                        with col_cam:
                                            if getattr(item, 'tipo_entrada', 'manual') == "camara":
                                                st.button("📷 Próximamente", key=f"cam_btn_{paciente.id}_{escala.id}_{item.id}", disabled=True)
                                
                                if puntaje_total > 0:
                                    st.info(f"Puntaje en {escala.nombre}: {puntaje_total} pts")
                                resultados_escalas[escala.nombre] = str(puntaje_total)
                            st.markdown("---")

    # ============================================================
    # MOTOR CLÍNICO GENERAL (Oculto por defecto)
    # ============================================================
    with st.expander("⚙️ Ver Tests Clínicos Generales (Legacy)", expanded=False):
        st.caption("Estos son tests genéricos por categoría. Para un control más preciso, usa el Gestor de Escalas.")
        
        tests = recomendar_tests(paciente.categoria_patologica, paciente.edad or 0, paciente.vino_con_diagnostico, paciente.diagnostico_medico)
        if tests:
            grupos = agrupar_tests_por_prioridad(tests)
            aplicados_ids = tests_aplicados_ids(paciente.id)
            
            with st.form("form_eval_general"):
                estado_tests = {}
                for prioridad in sorted(grupos.keys()):
                    if not grupos[prioridad]: continue
                    st.markdown(f"#### {etiqueta_prioridad(prioridad)}")
                    for t in grupos[prioridad]:
                        col_check, col_nombre, col_res = st.columns([1, 3, 2])
                        with col_check: 
                            marcado = st.checkbox("Aplicado", value=(t["id"] in aplicados_ids), key=f"check_{paciente.id}_{t['id']}", label_visibility="collapsed")
                        with col_nombre: 
                            st.markdown(f"**{t['nombre']}**")
                            st.caption(t.get("descripcion", ""))
                        with col_res: 
                            resultado = st.text_input("Resultado", value="", key=f"res_{paciente.id}_{t['id']}", label_visibility="collapsed", placeholder="Ej: 24/28")
                        
                        estado_tests[t["id"]] = {
                            "test_id": t["id"], "test_nombre": t["nombre"], 
                            "categoria": paciente.categoria_patologica, 
                            "aplicado": marcado, "resultado": resultado
                        }
                
                if st.form_submit_button("💾 Guardar Evaluaciones Generales", type="primary"):
                    u = usuario_actual()
                    guardar_evaluaciones_masivo(paciente.id, u["id"] if u else None, list(estado_tests.values()))
                    st.success("Evaluaciones guardadas.")
                    st.rerun()

    # Historial
    st.markdown("### 📊 Historial")
    aplicadas = [e for e in listar_por_paciente(paciente.id) if e.aplicado]
    if aplicadas:
        st.dataframe(pd.DataFrame([{"Test": e.test_nombre, "Fecha": e.fecha_aplicacion, "Resultado": e.resultado or "—"} for e in aplicadas]), use_container_width=True, hide_index=True)
    else:
        st.info("No hay evaluaciones previas.")

# ============================================================
# VISTA: FORMULARIO NUEVO PACIENTE
# ============================================================
def _render_formulario():
    if st.button("⬅️ Volver al listado"):
        st.session_state["vista_pacientes"] = "lista"; st.rerun()
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        documento = st.text_input("📄 DNI *", key="nuevo_doc")
        nombre_completo = st.text_input("👤 Nombre completo *", key="nuevo_nombre")
        edad = st.number_input("🎂 Edad", 0, 120, 30, key="nuevo_edad")
        sexo = st.selectbox("⚧ Sexo", ["—"] + SEXOS, key="nuevo_sexo")
        telefono = st.text_input("📱 Teléfono", key="nuevo_tel")
    with col2:
        correo = st.text_input("📧 Correo", key="nuevo_correo")
        ocupacion = st.text_input("💼 Ocupación", key="nuevo_ocup")
        motivo_consulta = st.text_area("💬 Motivo de consulta", height=80, key="nuevo_motivo")

    st.markdown("---")
    vino_con_diagnostico = st.radio("¿Vino con diagnóstico médico?", [True, False], format_func=lambda x: "✅ Sí" if x else "❌ No", horizontal=True, key="nuevo_vino")
    
    diagnostico_medico = ""
    if vino_con_diagnostico:
        st.caption("Busca el diagnóstico en tu biblioteca. Si no existe, puedes crearlo aquí mismo.")
        
        patologias_db = listar_patologias()
        opciones_diagnostico = ["— Seleccionar patología existente —", "➕ Crear nueva patología..."] + [p.nombre for p in patologias_db]
        
        seleccion_diag = st.selectbox(
            "Escribe o selecciona el diagnóstico:", 
            options=opciones_diagnostico,
            index=0,
            key="nuevo_diag"
        )
        
        if seleccion_diag == "— Seleccionar patología existente —":
            diagnostico_medico = ""
        elif seleccion_diag == "➕ Crear nueva patología...":
            st.info("💡 Asegúrate de escribirla sin errores ortográficos, ya que quedará guardada en tu biblioteca.")
            diagnostico_medico = st.text_input("Escribe el nombre de la nueva patología:", key="nuevo_diag_texto")
        else:
            diagnostico_medico = seleccion_diag

    # Lógica para autoseleccionar la categoría si la patología ya existe
    indice_categoria = 0 
    cat_sugerida = "Neurológica" 
    
    if vino_con_diagnostico and seleccion_diag not in ["— Seleccionar patología existente —", "➕ Crear nueva patología..."]:
        pat_encontrada = next((p for p in patologias_db if p.nombre == seleccion_diag), None)
        if pat_encontrada and pat_encontrada.categoria in CATEGORIAS_PATOLOGICAS:
            cat_sugerida = pat_encontrada.categoria
            indice_categoria = CATEGORIAS_PATOLOGICAS.index(cat_sugerida)

    categoria = st.selectbox(
        "Categoría principal:", 
        options=CATEGORIAS_PATOLOGICAS, 
        index=indice_categoria,
        format_func=lambda c: f"{ICONOS_CATEGORIA.get(c, '')} {c}", 
        key=f"nuevo_cat_{cat_sugerida}"
    )
    antecedentes = st.text_area("📝 Antecedentes", height=80, key="nuevo_ante")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("✅ Registrar paciente", type="primary", use_container_width=True):
        if not documento.strip() or not nombre_completo.strip():
            st.error("DNI y Nombre son obligatorios.")
        elif existe_documento(documento):
            st.error("Ya existe un paciente con ese DNI.")
        elif vino_con_diagnostico and not diagnostico_medico.strip():
            st.error("Debes escribir el diagnóstico.")
        else:
            if vino_con_diagnostico and diagnostico_medico.strip():
                diag_limpio = diagnostico_medico.strip().capitalize()
                if not buscar_por_nombre(diag_limpio):
                    crear_patologia(nombre=diag_limpio, categoria=categoria)
                diagnostico_medico = diag_limpio

            u = usuario_actual()
            nuevo = crear_paciente(
                documento=documento, nombre_completo=nombre_completo, terapeuta_id=u["id"], registrado_por_id=u["id"],
                edad=int(edad), sexo=None if sexo == "—" else sexo, telefono=telefono, correo=correo,
                ocupacion=ocupacion, categoria_patologica=categoria, vino_con_diagnostico=vino_con_diagnostico,
                diagnostico_medico=diagnostico_medico if vino_con_diagnostico else None,
                motivo_consulta=motivo_consulta, antecedentes=antecedentes,
            )
            st.success(f"✅ Paciente **{nuevo.nombre_completo}** registrado.")
            st.balloons()
            import time; time.sleep(1.5)
            st.session_state["vista_pacientes"] = "lista"; st.rerun()


# ============================================================
# RENDER PRINCIPAL
# ============================================================
def render() -> None:
    vista = st.session_state.get("vista_pacientes", "lista")
    if vista != "lista":
        if st.button("← Atrás"): st.session_state["vista_pacientes"] = "lista"; st.rerun()
    
    st.title("🧑‍🦽 Módulo de Pacientes")
    st.markdown("---")
    
    if vista == "nuevo": _render_formulario()
    elif vista == "detalle": _render_detalle()
    else: _render_lista()