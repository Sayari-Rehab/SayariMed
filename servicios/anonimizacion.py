"""
servicios/anonimizacion.py
--------------------------
Generación de IDs anónimos y export de datos para investigación.

Reglas:
- Cada paciente tiene UN id anónimo único.
- El ID no contiene información personal (no es hash del DNI).
- El export de investigación EXCLUYE: nombre, documento, teléfono, correo, dirección.
"""

import random
import string
from io import BytesIO
from datetime import date
from typing import Optional

import pandas as pd

from core.database import get_session
from modelos import Paciente
from repositorios.pacientes_repo import listar_pacientes
from repositorios.sesiones_repo import listar_por_paciente as listar_sesiones


PREFIJO = "SAY"


# ============================================================
# GENERAR ID ANÓNIMO
# ============================================================
def generar_id_anonimo() -> str:
    """Genera un ID único tipo SAY-A7F3B2."""
    chars = string.ascii_uppercase + string.digits
    while True:
        codigo = "".join(random.choices(chars, k=6))
        id_anon = f"{PREFIJO}-{codigo}"
        # Verificar que no exista
        with get_session() as db:
            existe = db.query(Paciente).filter(Paciente.id_anonimo == id_anon).first()
            if not existe:
                return id_anon


def asignar_id_anonimo(paciente_id: int) -> Optional[str]:
    """Asigna un ID anónimo a un paciente si no lo tiene."""
    with get_session() as db:
        paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
        if not paciente:
            return None
        if paciente.id_anonimo:
            return paciente.id_anonimo
        nuevo_id = generar_id_anonimo()
        paciente.id_anonimo = nuevo_id
        return nuevo_id


def asignar_a_todos() -> int:
    """Asigna IDs anónimos a todos los pacientes que no los tengan."""
    with get_session() as db:
        pacientes = db.query(Paciente).filter(Paciente.id_anonimo.is_(None)).all()
        contador = 0
        for p in pacientes:
            p.id_anonimo = generar_id_anonimo()
            contador += 1
    return contador


# ============================================================
# EXPORT DE INVESTIGACIÓN (ANONIMIZADO)
# ============================================================
def export_investigacion_excel(terapeuta_id: Optional[int] = None) -> bytes:
    """
    Genera un Excel con datos anonimizados para investigación.

    Columnas incluidas:
    - ID anónimo
    - Edad, Sexo, Ocupación
    - Categoría patológica, Diagnóstico
    - N° de sesiones, EVA inicial, EVA final, Mejora total
    """
    pacientes = listar_pacientes(terapeuta_id=terapeuta_id, incluir_inactivos=True)

    filas = []
    for p in pacientes:
        # Asegurar id anónimo
        if not p.id_anonimo:
            id_anon = asignar_id_anonimo(p.id)
        else:
            id_anon = p.id_anonimo

        sesiones = listar_sesiones(p.id)

        eva_inicial = None
        eva_final = None
        if sesiones:
            # Primera sesión con EVA pre
            for s in sesiones:
                if s.eva_pre is not None:
                    eva_inicial = s.eva_pre
                    break
            # Última sesión con EVA post
            for s in reversed(sesiones):
                if s.eva_post is not None:
                    eva_final = s.eva_post
                    break

        mejora = None
        if eva_inicial is not None and eva_final is not None:
            mejora = round(eva_inicial - eva_final, 1)

        filas.append({
            "ID_anonimo": id_anon,
            "Edad": p.edad,
            "Sexo": p.sexo,
            "Ocupacion": p.ocupacion,
            "Categoria": p.categoria_patologica,
            "Vino_con_diagnostico": "Sí" if p.vino_con_diagnostico else "No",
            "Diagnostico": p.diagnostico_medico or "",
            "Total_sesiones": len(sesiones),
            "EVA_inicial": eva_inicial,
            "EVA_final": eva_final,
            "Mejora_EVA": mejora,
            "Estado": p.estado,
        })

    df = pd.DataFrame(filas)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Investigacion", index=False)
    output.seek(0)
    return output.getvalue()


# ============================================================
# EXPORT DE SESIONES ANONIMIZADAS
# ============================================================
def export_sesiones_anonimas_excel(terapeuta_id: Optional[int] = None) -> bytes:
    """Export de todas las sesiones con ID anónimo (sin datos personales)."""
    pacientes = listar_pacientes(terapeuta_id=terapeuta_id, incluir_inactivos=True)

    filas = []
    for p in pacientes:
        if not p.id_anonimo:
            id_anon = asignar_id_anonimo(p.id)
        else:
            id_anon = p.id_anonimo

        sesiones = listar_sesiones(p.id)
        for s in sesiones:
            filas.append({
                "ID_anonimo": id_anon,
                "Numero_sesion": s.numero_sesion,
                "Fecha": s.fecha_sesion,
                "EVA_pre": s.eva_pre,
                "EVA_post": s.eva_post,
                "Mejora": round(s.mejora_dolor, 1),
                "Procedimientos": s.procedimientos or "",
                "Tolerancia": s.tolerancia or "",
            })

    df = pd.DataFrame(filas)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Sesiones_anonimas", index=False)
    output.seek(0)
    return output.getvalue()


def nombre_archivo_anon(extension: str) -> str:
    """Nombre de archivo para exports anónimos."""
    hoy = date.today().strftime("%Y-%m-%d")
    return f"investigacion_anonimo_{hoy}.{extension}"