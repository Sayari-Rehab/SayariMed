"""
servicios/reportes.py
---------------------
Generación de reportes en Excel, CSV y PDF.

Todas las funciones devuelven bytes para que Streamlit pueda ofrecer
el archivo como descarga.
"""

from io import BytesIO
from datetime import date
from typing import List, Optional

import pandas as pd

from modelos import Paciente, Sesion, Evaluacion
from repositorios.pacientes_repo import listar_pacientes
from repositorios.sesiones_repo import listar_por_paciente as listar_sesiones
from repositorios.evaluaciones_repo import listar_por_paciente as listar_evaluaciones


# ============================================================
# PACIENTES
# ============================================================
def pacientes_a_excel(terapeuta_id: Optional[int] = None) -> bytes:
    """Devuelve un Excel con todos los pacientes."""
    pacientes = listar_pacientes(terapeuta_id=terapeuta_id, incluir_inactivos=True)

    datos = []
    for p in pacientes:
        datos.append({
            "ID": p.id,
            "Documento": p.documento,
            "Nombre completo": p.nombre_completo,
            "Edad": p.edad,
            "Sexo": p.sexo,
            "Teléfono": p.telefono,
            "Correo": p.correo,
            "Ocupación": p.ocupacion,
            "Categoría patológica": p.categoria_patologica,
            "Vino con diagnóstico": "Sí" if p.vino_con_diagnostico else "No",
            "Diagnóstico": p.diagnostico_medico or "",
            "Estado": p.estado,
            "Fecha ingreso": p.fecha_ingreso,
        })

    df = pd.DataFrame(datos)
    return _df_a_excel(df, "Pacientes")


def pacientes_a_csv(terapeuta_id: Optional[int] = None) -> bytes:
    """Devuelve un CSV con todos los pacientes."""
    pacientes = listar_pacientes(terapeuta_id=terapeuta_id, incluir_inactivos=True)

    datos = []
    for p in pacientes:
        datos.append({
            "ID": p.id,
            "Documento": p.documento,
            "Nombre completo": p.nombre_completo,
            "Edad": p.edad,
            "Sexo": p.sexo,
            "Teléfono": p.telefono,
            "Correo": p.correo,
            "Ocupación": p.ocupacion,
            "Categoría patológica": p.categoria_patologica,
            "Diagnóstico": p.diagnostico_medico or "",
            "Estado": p.estado,
        })

    df = pd.DataFrame(datos)
    return df.to_csv(index=False).encode("utf-8-sig")  # BOM para Excel con tildes


# ============================================================
# SESIONES DE UN PACIENTE
# ============================================================
def sesiones_a_excel(paciente_id: int) -> bytes:
    """Devuelve un Excel con todas las sesiones de un paciente."""
    sesiones = listar_sesiones(paciente_id)

    datos = []
    for s in sesiones:
        datos.append({
            "N° sesión": s.numero_sesion,
            "Fecha": s.fecha_sesion,
            "EVA pre": s.eva_pre,
            "EVA post": s.eva_post,
            "Mejora": round(s.mejora_dolor, 1),
            "Procedimientos": s.procedimientos or "",
            "Tolerancia": s.tolerancia or "",
            "Respuesta paciente": s.respuesta_paciente or "",
            "Observaciones": s.observaciones or "",
        })

    df = pd.DataFrame(datos)
    return _df_a_excel(df, "Sesiones")


# ============================================================
# REPORTE COMPLETO DEL PACIENTE
# ============================================================
def reporte_completo_paciente(paciente: Paciente) -> bytes:
    """
    Devuelve un Excel con varias hojas:
    - Ficha del paciente.
    - Sesiones.
    - Evaluaciones.
    """
    # Hoja 1: Ficha
    ficha = pd.DataFrame([{
        "Documento": paciente.documento,
        "Nombre completo": paciente.nombre_completo,
        "Edad": paciente.edad,
        "Sexo": paciente.sexo,
        "Teléfono": paciente.telefono,
        "Correo": paciente.correo,
        "Ocupación": paciente.ocupacion,
        "Dirección": paciente.direccion,
        "Categoría patológica": paciente.categoria_patologica,
        "Vino con diagnóstico": "Sí" if paciente.vino_con_diagnostico else "No",
        "Diagnóstico médico": paciente.diagnostico_medico or "",
        "Motivo de consulta": paciente.motivo_consulta or "",
        "Antecedentes": paciente.antecedentes or "",
        "Fecha ingreso": paciente.fecha_ingreso,
        "Estado": paciente.estado,
    }])

    # Hoja 2: Sesiones
    sesiones = listar_sesiones(paciente.id)
    sesiones_data = [{
        "N°": s.numero_sesion,
        "Fecha": s.fecha_sesion,
        "EVA pre": s.eva_pre,
        "EVA post": s.eva_post,
        "Mejora": round(s.mejora_dolor, 1),
        "Procedimientos": s.procedimientos or "",
    } for s in sesiones]
    df_sesiones = pd.DataFrame(sesiones_data) if sesiones_data else pd.DataFrame()

    # Hoja 3: Evaluaciones
    evaluaciones = listar_evaluaciones(paciente.id)
    evals_data = [{
        "Test": e.test_nombre,
        "Categoría": e.categoria or "",
        "Aplicado": "Sí" if e.aplicado else "No",
        "Fecha": e.fecha_aplicacion,
        "Resultado": e.resultado or "",
    } for e in evaluaciones if e.aplicado]
    df_evals = pd.DataFrame(evals_data) if evals_data else pd.DataFrame()

    # Escribir todo en un solo Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        ficha.to_excel(writer, sheet_name="Ficha", index=False)
        if not df_sesiones.empty:
            df_sesiones.to_excel(writer, sheet_name="Sesiones", index=False)
        if not df_evals.empty:
            df_evals.to_excel(writer, sheet_name="Evaluaciones", index=False)

    output.seek(0)
    return output.getvalue()


# ============================================================
# HELPERS
# ============================================================
def _df_a_excel(df: pd.DataFrame, sheet_name: str) -> bytes:
    """Convierte un DataFrame a Excel (bytes)."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output.getvalue()


def nombre_archivo(prefijo: str, extension: str) -> str:
    """Genera un nombre de archivo con la fecha de hoy."""
    hoy = date.today().strftime("%Y-%m-%d")
    return f"{prefijo}_{hoy}.{extension}"