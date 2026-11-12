"""
repositorios/patologias_repo.py
-------------------------------
Operaciones CRUD sobre la tabla patologias.
"""
from typing import List, Optional
from core.database import get_session
from modelos import Usuario, Paciente, Evaluacion, Sesion, Patologia  # noqa: F401

def listar_patologias(categoria: Optional[str] = None, solo_con_tests: bool = False) -> List[Patologia]:
    with get_session() as db:
        query = db.query(Patologia)
        if categoria: query = query.filter(Patologia.categoria == categoria)
        if solo_con_tests: query = query.filter(Patologia.tests_recomendados.isnot(None))
        patologias = query.order_by(Patologia.nombre).all()
        for p in patologias: db.expunge(p)
        return patologias

def obtener_por_id(patologia_id: int) -> Optional[Patologia]:
    with get_session() as db:
        p = db.query(Patologia).filter(Patologia.id == patologia_id).first()
        if p: db.expunge(p)
        return p

def buscar_por_nombre(nombre: str) -> Optional[Patologia]:
    """Busca por nombre. Fuerza formato Capitalizado para evitar duplicados por tipeo."""
    with get_session() as db:
        nombre_buscado = nombre.strip().capitalize()
        p = db.query(Patologia).filter(Patologia.nombre == nombre_buscado).first()
        if p: db.expunge(p)
        return p

def buscar_por_texto(termino: str) -> List[Patologia]:
    if not termino or not termino.strip(): return []
    t = f"%{termino.strip()}%"
    with get_session() as db:
        patologias = db.query(Patologia).filter(Patologia.nombre.ilike(t) | Patologia.resumen.ilike(t)).order_by(Patologia.nombre).limit(50).all()
        for p in patologias: db.expunge(p)
        return patologias

def existe_nombre(nombre: str) -> bool:
    return buscar_por_nombre(nombre) is not None

def crear_patologia(nombre: str, categoria: str, resumen: Optional[str] = None, cuadro_clinico: Optional[str] = None, enfoque_fisio: Optional[str] = None, tests_recomendados: Optional[str] = None, referencias: Optional[str] = None) -> Patologia:
    with get_session() as db:
        nueva = Patologia(
            nombre=nombre.strip().capitalize(), # <--- FORZAMOS MAYÚSCULA INICIAL
            categoria=categoria, resumen=resumen, cuadro_clinico=cuadro_clinico,
            enfoque_fisio=enfoque_fisio, tests_recomendados=tests_recomendados, referencias=referencias,
        )
        db.add(nueva); db.flush(); db.expunge(nueva)
        return nueva

def actualizar_patologia(patologia_id: int, **campos) -> bool:
    with get_session() as db:
        p = db.query(Patologia).filter(Patologia.id == patologia_id).first()
        if not p: return False
        for key, value in campos.items():
            if hasattr(p, key):
                if key == "nombre": value = value.strip().capitalize()
                setattr(p, key, value)
        return True

def eliminar_patologia(patologia_id: int) -> bool:
    with get_session() as db:
        p = db.query(Patologia).filter(Patologia.id == patologia_id).first()
        if not p: return False
        db.delete(p); return True

def contar_patologias() -> int:
    with get_session() as db: return db.query(Patologia).count()