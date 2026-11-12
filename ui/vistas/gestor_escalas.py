import streamlit as st
from repositorios.escalas_repo import (
    crear_escala, listar_escalas, crear_seccion, listar_secciones, 
    crear_item, listar_items, buscar_escala_por_nombre,
    eliminar_seccion, eliminar_item, eliminar_escala,
    crear_evaluacion_maestra, listar_evaluaciones_maestras, buscar_evaluacion_maestra_por_nombre,
    vincular_escala_a_evaluacion, listar_escalas_de_evaluacion,
    vincular_evaluacion_a_patologia, listar_evaluaciones_de_patologia,
    listar_escalas_por_patologia, desvincular_escala_de_patologia
)
from repositorios.patologias_repo import (
    listar_patologias, crear_patologia, actualizar_patologia, buscar_por_nombre
)
from config.constants import CATEGORIAS_PATOLOGICAS

def render():
    if st.button("← Volver al Panel Admin"):
        st.session_state.pop("vista_admin", None)
        st.rerun()

    st.title("📊 Gestor Clínico")
    
    # Solo 4 pestañas ahora
    tab_crear, tab_patologias, tab_inventario, tab_evaluaciones = st.tabs([
        "🛠️ Crear Escala", "🧠 Patologías", "📋 Inventario General", "📑 Evaluaciones"
    ])

    # ============================================================
    # TAB 1: CREAR ESCALA
    # ============================================================
    with tab_crear:
        st.subheader("1. Crear la Escala")
        with st.form("form_crear_escala", clear_on_submit=True):
            nombre_escala = st.text_input("Nombre de la Escala (Ej: Test de Adams)")
            categoria_escala = st.selectbox("Categoría", options=CATEGORIAS_PATOLOGICAS)
            desc_escala = st.text_area("Descripción / Instrucciones para el terapeuta")
            
            es_universal = st.checkbox("🌍 Marcar como evaluación UNIVERSAL (se aplica a todos los pacientes)")
            
            guardar_escala = st.form_submit_button("Guardar Escala Base")
            
            if guardar_escala and nombre_escala:
                if buscar_escala_por_nombre(nombre_escala):
                    st.error("⚠️ Ya existe una escala con ese nombre. Usa uno diferente.")
                else:
                    crear_escala(nombre=nombre_escala, categoria=categoria_escala, descripcion=desc_escala, es_universal=es_universal)
                    st.success("Escala creada. Ahora agrégale sus secciones abajo.")
                    st.rerun()

        st.markdown("---")
        st.subheader("2. Agregar Secciones e Ítems")
        
        escalas = listar_escalas()
        if escalas:
            opciones_escalas = {e.nombre: e.id for e in escalas}
            escala_sel = st.selectbox("Selecciona una escala para editarla:", options=list(opciones_escalas.keys()), key="sel_escala_editar")
            escala_id = opciones_escalas[escala_sel]

            if st.button(f"🗑️ Eliminar Escala '{escala_sel}' permanentemente", type="primary"):
                if eliminar_escala(escala_id):
                    st.success("Escala eliminada correctamente.")
                    st.rerun()

            # Crear Sección
            with st.expander("➕ Agregar Sección"):
                with st.form(f"form_sec_{escala_id}", clear_on_submit=True):
                    nombre_sec = st.text_input("Nombre de la sección (Ej: Equilibrio):")
                    if st.form_submit_button("Crear Sección"):
                        if nombre_sec:
                            resultado = crear_seccion(escala_id=escala_id, nombre=nombre_sec)
                            if resultado:
                                st.success("Sección creada exitosamente.")
                            else:
                                st.warning("⚠️ Esa sección ya existe en esta escala.")

            # Listar Secciones y sus Ítems
            secciones = listar_secciones(escala_id)
            if not secciones:
                st.info("Esta escala aún no tiene secciones.")
            
            for sec in secciones:
                with st.expander(f"📂 {sec.nombre}", expanded=True):
                    if st.button("🗑️ Borrar Sección Completa", key=f"del_sec_{sec.id}"):
                        eliminar_seccion(sec.id)
                        st.success("Sección eliminada.")
                        st.rerun()

                    items = listar_items(sec.id)
                    if items:
                        for item in items:
                            col_item, col_del = st.columns([4, 1])
                            with col_item:
                                st.markdown(f"- {item.nombre} (Max: {item.puntaje_maximo} pts)")
                            with col_del:
                                if st.button("🗑️", key=f"del_item_{item.id}", help="Eliminar este ítem"):
                                    eliminar_item(item.id)
                                    st.rerun()
                    
                    with st.form(f"form_item_{sec.id}", clear_on_submit=True):
                        st.markdown("**Agregar nuevo ítem:**")
                        col_a, col_b, col_c = st.columns([2, 1, 1])
                        with col_a:
                            nombre_item = st.text_input("Nombre del ítem:")
                        with col_b:
                            puntaje = st.number_input("Puntaje Máx", min_value=0, max_value=10, value=0)
                        with col_c:
                            tipo = st.selectbox("Entrada", ["manual", "camara"])
                        
                        if st.form_submit_button("Agregar Ítem"):
                            if nombre_item:
                                resultado = crear_item(sec.id, nombre_item, puntaje, tipo)
                                if resultado:
                                    st.success("Ítem agregado correctamente.")
                                else:
                                    st.warning("⚠️ Ese ítem ya existe en esta sección.")

    # ============================================================
    # TAB 2: GESTOR DE PATOLOGÍAS
    # ============================================================
    with tab_patologias:
        st.subheader("🧠 Gestor de Patologías")
        st.caption("Crea y edita los diagnósticos que usarás en tu clínica.")

        with st.form("form_nueva_patologia", clear_on_submit=True):
            st.markdown("**Crear nueva patología:**")
            col1, col2 = st.columns(2)
            with col1:
                nombre_pat = st.text_input("Nombre (Ej: Escoliosis, ACV)")
            with col2:
                cat_pat = st.selectbox("Categoría", options=CATEGORIAS_PATOLOGICAS)
            
            if st.form_submit_button("Guardar Patología", type="primary"):
                if nombre_pat.strip():
                    if buscar_por_nombre(nombre_pat):
                        st.error("Ya existe una patología con ese nombre.")
                    else:
                        crear_patologia(nombre=nombre_pat, categoria=cat_pat)
                        st.success("✅ Patología creada.")
                        st.rerun()

        st.markdown("---")
        
        st.markdown("**Patologías registradas:**")
        patologias_db = listar_patologias()
        
        if not patologias_db:
            st.info("No hay patologías en la biblioteca. Crea la primera arriba.")
        else:
            for p in patologias_db:
                with st.expander(f"📌 {p.nombre} ({p.categoria})"):
                    
                    with st.form(f"edit_pat_{p.id}"):
                        nuevo_nombre = st.text_input("Nombre", value=p.nombre, key=f"n_{p.id}")
                        idx_cat = CATEGORIAS_PATOLOGICAS.index(p.categoria) if p.categoria in CATEGORIAS_PATOLOGICAS else 0
                        nueva_cat = st.selectbox("Categoría", options=CATEGORIAS_PATOLOGICAS, index=idx_cat, key=f"c_{p.id}")
                        nueva_desc = st.text_area("Descripción / Resumen clínico", value=p.resumen or "", key=f"d_{p.id}")
                        
                        if st.form_submit_button("💾 Actualizar Datos"):
                            if nuevo_nombre.strip() != p.nombre and buscar_por_nombre(nuevo_nombre):
                                st.error("Ya existe otra patología con ese nombre.")
                            else:
                                actualizar_patologia(
                                    p.id, 
                                    nombre=nuevo_nombre.strip(), 
                                    categoria=nueva_cat,
                                    resumen=nueva_desc.strip() if nueva_desc else None
                                )
                                st.success("Patología actualizada.")
                                st.rerun()
                    
                    st.markdown("---")
                    
                    st.markdown("**🔗 Evaluaciones asociadas a esta patología:**")
                    pruebas_asociadas = listar_evaluaciones_de_patologia(p.id)
                    
                    if not pruebas_asociadas:
                        st.info("Esta patología aún no tiene evaluaciones asociadas. Ve a la pestaña 'Evaluaciones'.")
                    else:
                        for item in pruebas_asociadas:
                            ev = item["evaluacion"]
                            tipo = item["tipo_requerimiento"]
                            
                            icono = "🔴" if tipo == "Obligatoria" else ("🟡" if tipo == "Sugerida" else "🟢")
                            
                            col_esc, col_tipo = st.columns([3, 2])
                            with col_esc:
                                st.markdown(f"{icono} **{ev.nombre}**")
                            with col_tipo:
                                st.caption(f"Tipo: {tipo}")

    # ============================================================
    # TAB 3: INVENTARIO GENERAL
    # ============================================================
    with tab_inventario:
        st.subheader("📋 Inventario General")
        st.caption("Vista rápida de todas tus escalas y su relación con las patologías.")
        
        col_escalas, col_patologias = st.columns(2)
        
        with col_escalas:
            st.markdown("### 📈 Escalas Creadas")
            escalas = listar_escalas()
            if not escalas:
                st.info("Aún no hay escalas creadas.")
            else:
                for e in escalas:
                    icono_univ = " 🌍" if e.es_universal else ""
                    st.markdown(f"- **{e.nombre}** ({e.categoria}){icono_univ}")
                    
        with col_patologias:
            st.markdown("### 🩺 Patologías y sus Evaluaciones")
            patologias = listar_patologias()
            if not patologias:
                st.info("Aún no hay patologías creadas.")
            else:
                for p in patologias:
                    with st.expander(f"📌 {p.nombre} ({p.categoria})"):
                        relaciones = listar_evaluaciones_de_patologia(p.id)
                        if not relaciones:
                            st.caption("No tiene evaluaciones asignadas aún.")
                        else:
                            for rel in relaciones:
                                ev = rel["evaluacion"]
                                tipo = rel["tipo_requerimiento"]
                                icono = "🔴" if tipo == "Obligatoria" else ("🟡" if tipo == "Sugerida" else "🟢")
                                st.markdown(f"{icono} {ev.nombre} — *{tipo}*")

    # ============================================================
    # TAB 4: EVALUACIONES MAESTRAS
    # ============================================================
    with tab_evaluaciones:
        st.subheader("📑 Gestor de Evaluaciones")
        st.caption("Agrupa varias escalas en un solo paquete (Ej: Evaluación Integral de Escoliosis).")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 1. Crear Nueva Evaluación")
            with st.form("form_crear_eval", clear_on_submit=True):
                nombre_eval = st.text_input("Nombre del Paquete (Ej: Evaluación Integral)")
                cat_eval = st.selectbox("Categoría", options=CATEGORIAS_PATOLOGICAS, key="cat_eval")
                desc_eval = st.text_area("Descripción breve")
                
                if st.form_submit_button("Guardar Evaluación", type="primary"):
                    if nombre_eval.strip():
                        if buscar_evaluacion_maestra_por_nombre(nombre_eval):
                            st.error("Ya existe una evaluación con ese nombre.")
                        else:
                            crear_evaluacion_maestra(nombre=nombre_eval, categoria=cat_eval, descripcion=desc_eval)
                            st.success("Evaluación creada.")
                            st.rerun()
                            
        with col2:
            st.markdown("### 2. Agregar Escalas al Paquete")
            evals = listar_evaluaciones_maestras()
            if evals:
                opciones_ev = {e.nombre: e.id for e in evals}
                ev_sel = st.selectbox("Selecciona la Evaluación:", options=list(opciones_ev.keys()), key="sel_ev_maestra")
                ev_id = opciones_ev[ev_sel]
                
                escalas_actuales = listar_escalas_de_evaluacion(ev_id)
                if escalas_actuales:
                    st.write("**Escalas incluidas:**")
                    for esc in escalas_actuales:
                        st.markdown(f"- {esc.nombre}")
                
                st.markdown("---")
                todas_escalas = listar_escalas()
                ids_actuales = [e.id for e in escalas_actuales]
                escalas_disponibles = [e for e in todas_escalas if e.id not in ids_actuales]
                
                if escalas_disponibles:
                    opciones_esc = {e.nombre: e.id for e in escalas_disponibles}
                    esc_sel = st.selectbox("Selecciona la Escala a añadir:", options=list(opciones_esc.keys()), key="sel_esc_anadir")
                    if st.button("➕ Añadir al Paquete"):
                        vincular_escala_a_evaluacion(ev_id, opciones_esc[esc_sel])
                        st.success("Escala añadida.")
                        st.rerun()
                else:
                    st.info("Todas las escalas creadas ya están en este paquete.")
            else:
                st.info("Primero crea una Evaluación.")

        st.markdown("---")
        st.markdown("### 3. Asignar Evaluación a una Patología")
        patologias = listar_patologias()
        if evals and patologias:
            col_pat, col_ev, col_tipo, col_btn = st.columns([2, 2, 1, 1])
            with col_pat:
                pat_sel = st.selectbox("Patología:", options=[p.nombre for p in patologias], key="sel_pat_eval_vinc")
            with col_ev:
                ev_sel2 = st.selectbox("Evaluación:", options=[e.nombre for e in evals], key="sel_ev_pat_vinc")
            with col_tipo:
                tipo_sel = st.selectbox("Nivel:", ["Obligatoria", "Sugerida", "Adicional"], key="sel_tipo_eval_vinc")
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔗 Vincular", type="primary", key="btn_vinc_eval_final"):
                    p_id = next(p.id for p in patologias if p.nombre == pat_sel)
                    e_id = next(e.id for e in evals if e.nombre == ev_sel2)
                    if vincular_evaluacion_a_patologia(p_id, e_id, tipo_sel):
                        st.success("Vinculado.")
                    else:
                        st.warning("Ya estaba vinculado.")