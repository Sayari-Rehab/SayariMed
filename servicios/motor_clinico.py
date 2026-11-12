"""
servicios/motor_clinico.py
--------------------------
Motor de recomendación de tests clínicos.

Estrategia:
1. Si el paciente tiene diagnóstico, buscamos coincidencia en la tabla `patologias`.
2. Si hay coincidencia, usamos los tests específicos de esa patología.
3. Si NO hay coincidencia (o no hay diagnóstico), caemos al respaldo por categoría.

100% puro Python para la parte de categorías. La parte de patologías consulta la BD.
"""

from typing import List, Dict, Optional
from difflib import SequenceMatcher

from config.constants import (
    TESTS_POR_CATEGORIA,
    TEST_ADULTO_MAYOR,
    EDAD_ADULTO_MAYOR,
)


# ============================================================
# RESPALDO POR CATEGORÍA (siempre disponible)
# ============================================================
def recomendar_tests_por_categoria(
    categoria_patologica: str,
    edad: int = 0,
) -> List[Dict]:
    """Devuelve tests sugeridos SOLO por categoría."""
    tests = list(TESTS_POR_CATEGORIA.get(categoria_patologica, []))

    if edad >= EDAD_ADULTO_MAYOR:
        ids_actuales = {t["id"] for t in tests}
        if TEST_ADULTO_MAYOR["id"] not in ids_actuales:
            tests.append(TEST_ADULTO_MAYOR.copy())

    tests.sort(key=lambda t: t.get("prioridad", 99))
    return tests


# ============================================================
# BUSCAR PATOLOGÍA POR DIAGNÓSTICO
# ============================================================
def _similitud(a: str, b: str) -> float:
    """Devuelve el % de similitud entre dos textos (0 a 1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def buscar_patologia_por_diagnostico(diagnostico: str) -> Optional[object]:
    """
    Busca la patología exacta en la base de datos por su nombre.
    Como ahora usamos un selectbox, el nombre viene exacto.
    """
    if not diagnostico or not diagnostico.strip():
        return None

    from repositorios.patologias_repo import buscar_por_nombre
    
    # Hacemos la búsqueda exacta en la base de datos
    return buscar_por_nombre(diagnostico)


# ============================================================
# CONVERTIR IDS DE TESTS A DICT COMPLETO
# ============================================================
def _ids_a_tests(tests_ids: List[str], categoria: str) -> List[Dict]:
    """
    Convierte una lista de IDs ["tinetti", "ashworth"] a la estructura
    completa que usa la vista.
    """
    # Armar un índice de todos los tests disponibles
    indice = {}
    for cat, lista in TESTS_POR_CATEGORIA.items():
        for t in lista:
            indice[t["id"]] = t.copy()
    indice[TEST_ADULTO_MAYOR["id"]] = TEST_ADULTO_MAYOR.copy()

    resultado = []
    for tid in tests_ids:
        if tid in indice:
            resultado.append(indice[tid])
        else:
            # Test no encontrado → crear entrada genérica
            resultado.append({
                "id": tid,
                "nombre": tid.replace("_", " ").title(),
                "prioridad": 2,
                "descripcion": "Test recomendado por patología.",
            })
    return resultado


# ============================================================
# FUNCIÓN PRINCIPAL (la que usa la vista)
# ============================================================
def recomendar_tests(
    categoria_patologica: str,
    edad: int = 0,
    vino_con_diagnostico: bool = False,
    diagnostico: Optional[str] = None,
) -> List[Dict]:
    """
    Función principal del motor.

    Estrategia:
    1. Si hay diagnóstico → buscar patología específica.
    2. Si la patología existe → usar sus tests específicos.
    3. Si no → caer al respaldo por categoría.
    """
    # ---- PASO 1: Buscar patología específica ----
    if vino_con_diagnostico and diagnostico:
        patologia = buscar_patologia_por_diagnostico(diagnostico)
        if patologia and patologia.lista_tests:
            tests = _ids_a_tests(patologia.lista_tests, patologia.categoria)
            # Sumar Chair Stand si es adulto mayor
            if edad >= EDAD_ADULTO_MAYOR:
                ids_actuales = {t["id"] for t in tests}
                if TEST_ADULTO_MAYOR["id"] not in ids_actuales:
                    tests.append(TEST_ADULTO_MAYOR.copy())
            tests.sort(key=lambda t: t.get("prioridad", 99))
            return tests

    # ---- PASO 2: Respaldo por categoría ----
    return recomendar_tests_por_categoria(categoria_patologica, edad)


def agrupar_tests_por_prioridad(tests: List[Dict]) -> Dict[int, List[Dict]]:
    """Agrupa tests por nivel de prioridad."""
    grupos: Dict[int, List[Dict]] = {1: [], 2: [], 3: []}
    for t in tests:
        prioridad = t.get("prioridad", 3)
        grupos.setdefault(prioridad, []).append(t)
    return grupos


def etiqueta_prioridad(prioridad: int) -> str:
    """Devuelve la etiqueta legible de una prioridad."""
    return {
        1: "🔴 Obligatorio",
        2: "🟡 Recomendado",
        3: "🟢 Opcional",
    }.get(prioridad, "⚪ Sin prioridad")

def obtener_escalas_dinamicas_por_patologia(nombre_patologia: str) -> list:
    """Busca las Evaluaciones vinculadas a una patología y extrae sus escalas."""
    from repositorios.patologias_repo import buscar_por_nombre
    from repositorios.escalas_repo import (
        listar_evaluaciones_de_patologia, listar_escalas_de_evaluacion, 
        listar_secciones, listar_items
    )
    
    if not nombre_patologia: return []
    patologia = buscar_por_nombre(nombre_patologia)
    if not patologia: return []

    evaluaciones_vinculadas = listar_evaluaciones_de_patologia(patologia.id)
    resultado = []
    
    for ev_data in evaluaciones_vinculadas:
        ev_maestra = ev_data["evaluacion"]
        tipo_req = ev_data["tipo_requerimiento"]
        
        # Aquí agrupamos todas las escalas que pertenecen a esta Evaluación Maestra
        escalas_de_esta_evaluacion = []
        for esc in listar_escalas_de_evaluacion(ev_maestra.id):
            secciones = listar_secciones(esc.id)
            esc_dict = {"escala": esc, "secciones": []}
            for sec in secciones:
                items = listar_items(sec.id)
                esc_dict["secciones"].append({"seccion": sec, "items": items})
            escalas_de_esta_evaluacion.append(esc_dict)
            
        resultado.append({
            "evaluacion_maestra": ev_maestra,
            "tipo": tipo_req,
            "escalas": escalas_de_esta_evaluacion
        })
        
    return resultado

def obtener_escalas_universales() -> list:
    """Busca y estructura las escalas universales (Signos vitales, EVA, etc)."""
    from repositorios.escalas_repo import listar_escalas_universales, listar_secciones, listar_items
    
    escalas = listar_escalas_universales()
    resultado = []
    
    for esc in escalas:
        secciones = listar_secciones(esc.id)
        esc_dict = {"escala": esc, "tipo": "Universal", "secciones": []}
        
        for sec in secciones:
            items = listar_items(sec.id)
            esc_dict["secciones"].append({"seccion": sec, "items": items})
            
        resultado.append(esc_dict)
    return resultado