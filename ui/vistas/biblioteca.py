"""
ui/vistas/biblioteca.py
-----------------------
Biblioteca clínica de patologías.

- Lista de patologías por categoría.
- Buscador por nombre o síntoma.
- Ficha completa de cada patología.
"""

import streamlit as st
import pandas as pd

from servicios.auth import es_admin
from repositorios.patologias_repo import (
    listar_patologias,
    obtener_por_id,
    buscar_por_texto,
    contar_patologias,
)
from config.constants import (
    CATEGORIAS_PATOLOGICAS,
    ICONOS_CATEGORIA,
    TESTS_POR_CATEGORIA,
)


def _nombre_test(test_id: str) -> str:
    """Devuelve el nombre legible de un test por su ID."""
    for cat, tests in TESTS_POR_CATEGORIA.items():
        for t in tests:
            if t["id"] == test_id:
                return t["nombre"]
    # Búsqueda en test adulto mayor
    from config.constants import TEST_ADULTO_MAYOR
    if test_id == TEST_ADULTO_MAYOR["id"]:
        return TEST_ADULTO_MAYOR["nombre"]
    return test_id


# ============================================================
# VISTA: LISTA
# ============================================================
def _render_lista():
    st.subheader("📖 Biblioteca Clínica")
    st.caption("Repaso rápido de patologías y su enfoque fisioterapéutico.")

    # ---------- Buscador ----------
    col_busq, col_cat = st.columns([2, 1])

    with col_busq:
        termino = st.text_input(
            "🔍 Buscar patología o síntoma",
            placeholder="Ej: ACV, temblor, lumbalgia...",
            key="bib_busqueda",
        )

    with col_cat:
        categoria_filtro = st.selectbox(
            "Filtrar por categoría:",
            options=["Todas"] + CATEGORIAS_PATOLOGICAS,
            key="bib_categoria",
        )

    st.markdown("---")

    # ---------- Cargar datos ----------
    if termino.strip():
        patologias = buscar_por_texto(termino)
    else:
        cat = None if categoria_filtro == "Todas" else categoria_filtro
        patologias = listar_patologias(categoria=cat)

    # Filtrar por categoría si hay búsqueda + filtro
    if termino.strip() and categoria_filtro != "Todas":
        patologias = [p for p in patologias if p.categoria == categoria_filtro]

    # ---------- Estado vacío ----------
    if not patologias:
        if termino.strip():
            st.info("No se encontraron patologías con ese criterio.")
        else:
            st.info(
                "📚 La biblioteca está vacía. "
                "Pídele al admin que cargue patologías o ejecuta el seed."
            )
        return

    # ---------- Tabla resumen ----------
    st.markdown(f"**{len(patologias)} patología(s) encontrada(s)**")

    for p in patologias:
        icono = ICONOS_CATEGORIA.get(p.categoria, "🩺")
        with st.container():
            col_a, col_b = st.columns([4, 1])

            with col_a:
                st.markdown(f"### {icono} {p.nombre}")
                st.caption(f"Categoría: **{p.categoria}**")
                if p.resumen:
                    # Mostrar solo primeras 150 letras
                    preview = p.resumen[:150] + ("..." if len(p.resumen) > 150 else "")
                    st.markdown(f"_{preview}_")

            with col_b:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("👁️ Ver ficha", key=f"ver_pat_{p.id}", use_container_width=True):
                    st.session_state["patologia_detalle_id"] = p.id
                    st.rerun()

            st.markdown("---")


# ============================================================
# VISTA: FICHA COMPLETA
# ============================================================
def _render_detalle():
    patologia_id = st.session_state.get("patologia_detalle_id")
    if not patologia_id:
        st.error("No se encontró la patología.")
        if st.button("← Volver"):
            st.session_state.pop("patologia_detalle_id", None)
            st.rerun()
        return

    patologia = obtener_por_id(patologia_id)
    if not patologia:
        st.error("Patología no encontrada.")
        if st.button("← Volver"):
            st.session_state.pop("patologia_detalle_id", None)
            st.rerun()
        return

    # ---------- Botón volver ----------
    if st.button("← Volver a la biblioteca", key=f"volver_pat_{patologia.id}"):
        st.session_state.pop("patologia_detalle_id", None)
        st.rerun()

    st.markdown("---")

    # ---------- Encabezado ----------
    icono = ICONOS_CATEGORIA.get(patologia.categoria, "🩺")
    st.markdown(f"# {icono} {patologia.nombre}")
    st.caption(f"Categoría: **{patologia.categoria}**")

    st.markdown("---")

    # ---------- Secciones ----------
    if patologia.resumen:
        st.markdown("### 📋 Resumen")
        st.markdown(patologia.resumen)

    if patologia.cuadro_clinico:
        st.markdown("### 🩺 Cuadro clínico")
        st.markdown(patologia.cuadro_clinico)

    if patologia.enfoque_fisio:
        st.markdown("### 🎯 Enfoque fisioterapéutico")
        st.markdown(patologia.enfoque_fisio)

    # ---------- Tests recomendados ----------
    st.markdown("### 🧠 Tests recomendados")
    tests_ids = patologia.lista_tests

    if not tests_ids:
        st.info("Aún no se han definido tests específicos para esta patología.")
    else:
        for test_id in tests_ids:
            nombre = _nombre_test(test_id)
            st.markdown(f"- **{nombre}**")

    # ---------- Referencias ----------
    if patologia.referencias:
        st.markdown("### 📚 Referencias")
        st.markdown(patologia.referencias)

    # ---------- Botón admin ----------
    if es_admin():
        st.markdown("---")
        st.caption("🔧 Solo admin:")
        if st.button("✏️ Editar esta patología", disabled=True, key=f"edit_pat_{patologia.id}"):
            pass  # Próximamente
        st.caption("(Edición disponible en la próxima sesión.)")


# ============================================================
# RENDER PRINCIPAL
# ============================================================
def render() -> None:
    """Muestra la lista o el detalle de una patología."""
    st.title("📖 Biblioteca Clínica")
    st.markdown("---")

    if st.session_state.get("patologia_detalle_id"):
        _render_detalle()
    else:
        _render_lista()