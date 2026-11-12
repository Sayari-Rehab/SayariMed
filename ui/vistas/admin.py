"""
ui/vistas/admin.py
------------------
Panel de administración de Sayari Med.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from repositorios.usuarios_repo import (
    listar_usuarios, cambiar_estado, crear_terapeuta, actualizar_terapeuta,
    existe_username, existe_email, existe_dni, existe_colegiatura,
)
from servicios.auth import hash_password, usuario_actual
from config.constants import ROL_TERAPEUTA


# ============================================================
# HELPERS
# ============================================================
def _carpeta_fotos():
    ruta = Path(__file__).resolve().parent.parent.parent / "static" / "fotos"
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta

def _ruta_local_foto(foto_url: str) -> Path:
    base = Path(__file__).resolve().parent.parent.parent
    ruta = foto_url.replace("/app/", "")
    return base / ruta


# ============================================================
# RENDER PRINCIPAL
# ============================================================
def render() -> None:
    """Dibuja el panel de administración."""
    if st.button("← Atrás", key="btn_atras_admin"):
        st.session_state.pop("vista_admin", None)
        st.rerun()

    st.title("🛠️ Panel de Administración")
    st.caption("Gestión de terapeutas y supervisión general.")
    st.markdown("---")

    todos = listar_usuarios()
    terapeutas = [u for u in todos if u.rol == ROL_TERAPEUTA]

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total usuarios", len(todos))
    with col2: st.metric("Terapeutas", len(terapeutas))
    with col3: st.metric("Activos", sum(1 for u in terapeutas if u.activo))
    with col4: st.metric("⚠️ Sin colegiatura", sum(1 for u in terapeutas if not u.tiene_colegiatura))

    st.markdown("---")
    st.subheader("👥 Terapeutas registrados")

    if not terapeutas:
        st.info("Aún no hay terapeutas registrados.")
    else:
        datos = []
        for t in terapeutas:
            col_marca = "⚠️ Pendiente" if not t.tiene_colegiatura else (t.colegiatura or "—")
            datos.append({
                "ID": t.id, "Usuario": t.username, "Nombre": t.nombre_con_titulo,
                "DNI": t.dni or "—", "Colegiatura": col_marca,
                "Especialidades": ", ".join(t.lista_especialidades) or "—",
                "Estado": "✅ Activo" if t.activo else "⛔ Inactivo",
            })
        st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)

        st.markdown("#### 🔧 Acciones")
        for t in terapeutas:
            with st.container():
                col_foto, col_info, col_btn = st.columns([1, 4, 1])
                with col_foto:
                    if t.foto_url:
                        ruta_local = _ruta_local_foto(t.foto_url)
                        if ruta_local.exists(): st.image(str(ruta_local), width=60)
                        else: st.markdown("👤")
                    else: st.markdown("👤")
                with col_info:
                    estado_emoji = "✅" if t.activo else "⛔"
                    colegiatura_txt = " · ⚠️ Sin colegiatura" if not t.tiene_colegiatura else ""
                    st.markdown(f"{estado_emoji} **{t.nombre_con_titulo}** — @{t.username}{colegiatura_txt}")
                    if t.lista_especialidades: st.caption("🩺 " + " · ".join(t.lista_especialidades))
                with col_btn:
                    if t.activo:
                        if st.button("Desactivar", key=f"desac_{t.id}", use_container_width=True):
                            cambiar_estado(t.id, False); st.rerun()
                    else:
                        if st.button("Activar", key=f"act_{t.id}", use_container_width=True):
                            cambiar_estado(t.id, True); st.rerun()
                    if st.button("✏️ Editar", key=f"edit_{t.id}", use_container_width=True):
                        st.session_state["editar_terapeuta_id"] = t.id; st.rerun()
                st.markdown("---")

    if st.session_state.get("editar_terapeuta_id"):
        _render_edicion(st.session_state["editar_terapeuta_id"])
        return

    # Crear nuevo terapeuta
    st.subheader("➕ Crear nuevo terapeuta")
    st.caption("📌 El **usuario de login** se genera automáticamente como **DNI + primera letra del primer apellido**.")

    with st.form("form_crear_terapeuta", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre_completo = st.text_input("👤 Nombre completo *", placeholder="Ej: Juan Pérez López")
            dni = st.text_input("📄 DNI (8 dígitos) *", placeholder="Ej: 12345678", max_chars=8)
            email = st.text_input("📧 Email", placeholder="Ej: jperez@sayari.med")
            telefono = st.text_input("📱 Teléfono", placeholder="Ej: 999888777")
        with col2:
            titulo = st.selectbox("🎓 Título profesional", options=["—", "Licenciado(a)", "Magíster", "Doctor(a)"])
            colegiatura = st.text_input("🏛️ N° Colegiatura CTMP", placeholder="Ej: 12345")
            colegiatura_pendiente = st.checkbox("⏳ Aún no tiene colegiatura (regularizará después)")
            especialidad = st.text_input("🩺 Especialidades (separadas por coma)")

        st.markdown("---")
        col_foto, col_pass = st.columns(2)
        with col_foto:
            foto = st.file_uploader("📸 Foto del profesional (opcional)", type=["png", "jpg", "jpeg"])
        with col_pass:
            password = st.text_input("🔒 Contraseña temporal *", type="password")
            password_confirm = st.text_input("🔒 Confirmar contraseña *", type="password")

        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            crear = st.form_submit_button("✅ Crear terapeuta", use_container_width=True, type="primary")

    if crear:
        errores = []
        if not nombre_completo.strip(): errores.append("El nombre completo es obligatorio.")
        if not dni.strip() or not dni.strip().isdigit() or len(dni.strip()) != 8: errores.append("El DNI debe tener 8 dígitos numéricos.")
        if not password or len(password) < 6: errores.append("La contraseña debe tener al menos 6 caracteres.")
        if password != password_confirm: errores.append("Las contraseñas no coinciden.")

        username_generado = ""
        if dni.strip().isdigit() and len(dni.strip()) == 8 and nombre_completo.strip():
            partes = nombre_completo.strip().split()
            inicial = partes[1][0].upper() if len(partes) >= 2 else partes[0][0].upper()
            username_generado = f"{dni.strip()}{inicial}"

        if dni.strip() and existe_dni(dni.strip()): errores.append(f"Ya existe un usuario con el DNI '{dni}'.")
        if username_generado and existe_username(username_generado): errores.append(f"Ya existe un usuario con el login '{username_generado}'.")
        if email.strip() and existe_email(email): errores.append(f"Ya existe un usuario con el email '{email}'.")
        if colegiatura.strip() and existe_colegiatura(colegiatura): errores.append(f"Ya existe un usuario con la colegiatura '{colegiatura}'.")

        if errores:
            for err in errores: st.error(f"❌ {err}")
        else:
            foto_url = None
            if foto is not None:
                carpeta = _carpeta_fotos()
                extension = foto.name.split(".")[-1].lower()
                nombre_archivo_foto = f"user_{username_generado}.{extension}"
                ruta_foto = carpeta / nombre_archivo_foto
                with open(ruta_foto, "wb") as f: f.write(foto.getbuffer())
                foto_url = f"/app/static/fotos/{nombre_archivo_foto}"

            admin_actual = usuario_actual()
            nuevo = crear_terapeuta(
                username=username_generado, password_hash=hash_password(password),
                nombre_completo=nombre_completo, dni=dni,
                colegiatura=colegiatura if not colegiatura_pendiente else None,
                colegiatura_pendiente=colegiatura_pendiente or not colegiatura.strip(),
                email=email, telefono=telefono, titulo=None if titulo == "—" else titulo,
                especialidad=especialidad, foto_url=foto_url,
                creado_por_id=admin_actual["id"] if admin_actual else None,
            )
            st.success(f"✅ Terapeuta **{nuevo.nombre_con_titulo}** creado exitosamente.")
            st.balloons()
            st.rerun()

def _render_edicion(usuario_id: int):
    from repositorios.usuarios_repo import buscar_por_id
    usuario = buscar_por_id(usuario_id)
    if not usuario: return

    if st.button("← Volver al listado", key="btn_volver_edit"):
        st.session_state.pop("editar_terapeuta_id", None); st.rerun()

    st.markdown("---")
    st.subheader(f"✏️ Editar: {usuario.nombre_con_titulo}")
    
    with st.form("form_editar_terapeuta"):
        col1, col2 = st.columns(2)
        with col1:
            nombre_completo = st.text_input("👤 Nombre completo *", value=usuario.nombre_completo)
            email = st.text_input("📧 Email", value=usuario.email or "")
            telefono = st.text_input("📱 Teléfono", value=usuario.telefono or "")
            titulo_actual = usuario.titulo or "—"
            opciones_titulo = ["—", "Licenciado(a)", "Magíster", "Doctor(a)"]
            index_titulo = opciones_titulo.index(titulo_actual) if titulo_actual in opciones_titulo else 0
            titulo = st.selectbox("🎓 Título profesional", options=opciones_titulo, index=index_titulo)
        with col2:
            colegiatura = st.text_input("🏛️ N° Colegiatura CTMP", value=usuario.colegiatura or "")
            colegiatura_pendiente = st.checkbox("⏳ Aún no tiene colegiatura", value=usuario.colegiatura_pendiente)
            especialidad = st.text_input("🩺 Especialidades", value=usuario.especialidad or "")

        st.markdown("---")
        nueva_foto = st.file_uploader("📸 Cambiar foto (opcional)", type=["png", "jpg", "jpeg"])
        
        guardar = st.form_submit_button("💾 Guardar cambios", type="primary")

    if guardar:
        foto_url_final = usuario.foto_url
        if nueva_foto is not None:
            carpeta = _carpeta_fotos()
            extension = nueva_foto.name.split(".")[-1].lower()
            nombre_archivo_foto = f"user_{usuario.username}.{extension}"
            ruta_foto = carpeta / nombre_archivo_foto
            with open(ruta_foto, "wb") as f: f.write(nueva_foto.getbuffer())
            foto_url_final = f"/app/static/fotos/{nombre_archivo_foto}"

        actualizar_terapeuta(
            usuario.id, nombre_completo=nombre_completo.strip(),
            email=email.strip() if email else None, telefono=telefono.strip() if telefono else None,
            titulo=None if titulo == "—" else titulo,
            colegiatura=colegiatura.strip() if colegiatura.strip() else None,
            colegiatura_pendiente=colegiatura_pendiente or not colegiatura.strip(),
            especialidad=especialidad.strip() if especialidad else None, foto_url=foto_url_final,
        )
        st.success("✅ Cambios guardados correctamente.")
        import time; time.sleep(1)
        st.session_state.pop("editar_terapeuta_id", None); st.rerun()