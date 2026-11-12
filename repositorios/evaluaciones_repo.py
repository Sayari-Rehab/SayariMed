"""
repositorios/evaluaciones_repo.py
---------------------------------
Operaciones sobre la tabla evaluaciones.
"""

from typing import List, Dict, Optional
from datetime import date

from core.database import get_session
from modelos import Usuario, Paciente, Evaluacion, Sesion, Patologia  # noqa: F401


# ============================================================
# LEER
# ============================================================
def listar_por_paciente(paciente_id: int) -> List[Evaluacion]:
    """Devuelve todas las evaluaciones de un paciente."""
    with get_session() as db:
        evaluaciones = (
            db.query(Evaluacion)
            .filter(Evaluacion.paciente_id == paciente_id)
            .order_by(Evaluacion.fecha_creacion.desc())
            .all()
        )
        for e in evaluaciones:
            db.expunge(e)
        return evaluaciones


def obtener_por_paciente_y_test(
    paciente_id: int,
    test_id: str,
) -> Optional[Evaluacion]:
    """Busca la evaluación de un test específico para un paciente."""
    with get_session() as db:
        ev = (
            db.query(Evaluacion)
            .filter(
                Evaluacion.paciente_id == paciente_id,
                Evaluacion.test_id == test_id,
            )
            .first()
        )
        if ev:
            db.expunge(ev)
        return ev


def tests_aplicados_ids(paciente_id: int) -> set:
    """Devuelve un set con los IDs de tests ya aplicados a un paciente."""
    with get_session() as db:
        resultados = (
            db.query(Evaluacion.test_id)
            .filter(
                Evaluacion.paciente_id == paciente_id,
                Evaluacion.aplicado == True,  # noqa: E712
            )
            .all()
        )
        return {r[0] for r in resultados}


# ============================================================
# CREAR / ACTUALIZAR
# ============================================================
def guardar_evaluaciones_masivo(
    paciente_id: int,
    aplicado_por_id: int,
    tests_marcados: List[Dict],
) -> int:
    """
    Guarda el estado (aplicado o no) de varios tests para un paciente.

    `tests_marcados` es una lista de dicts:
        [
            {"test_id": "tinetti", "test_nombre": "Escala de Tinetti",
             "categoria": "Neurológica", "aplicado": True,
             "resultado": "24/28", "observaciones": "sin dificultad"},
            ...
        ]

    Para cada test:
    - Si NO existe evaluación previa → crea una nueva.
    - Si YA existe → actualiza el estado `aplicado` y los campos.

    Devuelve cuántas evaluaciones se guardaron/actualizaron.
    """
    contador = 0

    with get_session() as db:
        for t in tests_marcados:
            existente = (
                db.query(Evaluacion)
                .filter(
                    Evaluacion.paciente_id == paciente_id,
                    Evaluacion.test_id == t["test_id"],
                )
                .first()
            )

            if existente:
                existente.aplicado = t.get("aplicado", False)
                existente.resultado = t.get("resultado") or None
                existente.observaciones = t.get("observaciones") or None
                if t.get("aplicado"):
                    existente.fecha_aplicacion = date.today()
            else:
                nueva = Evaluacion(
                    paciente_id=paciente_id,
                    aplicado_por_id=aplicado_por_id,
                    test_id=t["test_id"],
                    test_nombre=t["test_nombre"],
                    categoria=t.get("categoria"),
                    aplicado=t.get("aplicado", False),
                    resultado=t.get("resultado") or None,
                    observaciones=t.get("observaciones") or None,
                )
                db.add(nueva)

            contador += 1

    return contador


def eliminar_evaluacion(evaluacion_id: int) -> bool:
    """Elimina una evaluación por su ID."""
    with get_session() as db:
        ev = db.query(Evaluacion).filter(Evaluacion.id == evaluacion_id).first()
        if not ev:
            return False
        db.delete(ev)
        return True


def contar_por_paciente(paciente_id: int) -> int:
    """Cuenta cuántos tests se han aplicado a un paciente."""
    with get_session() as db:
        return (
            db.query(Evaluacion)
            .filter(
                Evaluacion.paciente_id == paciente_id,
                Evaluacion.aplicado == True,  # noqa: E712
            )
            .count()
        )