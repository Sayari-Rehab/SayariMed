from typing import List, Optional
from core.database import get_session
from modelos.escalas import Escala, Seccion, Item, PatologiaEscala

# ============================================================
# ESCALAS
# ============================================================
def buscar_escala_por_nombre(nombre: str) -> Optional[Escala]:
    with get_session() as db:
        e = db.query(Escala).filter(Escala.nombre.ilike(nombre.strip())).first()
        if e: db.expunge(e)
        return e

def crear_escala(nombre: str, categoria: str, descripcion: str = None, imagen_url: str = None, es_universal: bool = False) -> Escala:
    with get_session() as db:
        nueva = Escala(nombre=nombre.strip(), categoria=categoria, descripcion=descripcion, imagen_url=imagen_url, es_universal=es_universal)
        db.add(nueva); db.flush(); db.expunge(nueva)
        return nueva

def listar_escalas() -> List[Escala]:
    with get_session() as db:
        escalas = db.query(Escala).order_by(Escala.nombre).all()
        for e in escalas: db.expunge(e)
        return escalas

def listar_escalas_universales() -> List[Escala]:
    """Devuelve las escalas que se aplican a TODOS los pacientes."""
    with get_session() as db:
        escalas = db.query(Escala).filter(Escala.es_universal == True).all()
        for e in escalas: 
            db.expunge(e)
        return escalas

def obtener_escala(escala_id: int) -> Optional[Escala]:
    with get_session() as db:
        e = db.query(Escala).filter(Escala.id == escala_id).first()
        if e: db.expunge(e)
        return e

# ============================================================
# SECCIONES
# ============================================================
def crear_seccion(escala_id: int, nombre: str, orden: int = 1) -> Seccion:
    with get_session() as db:
        existe = db.query(Seccion).filter(
            Seccion.escala_id == escala_id, 
            Seccion.nombre.ilike(nombre.strip())
        ).first()
        if existe:
            return None
            
        nueva = Seccion(escala_id=escala_id, nombre=nombre.strip(), orden=orden)
        db.add(nueva); db.flush(); db.expunge(nueva)
        return nueva

def listar_secciones(escala_id: int) -> List[Seccion]:
    with get_session() as db:
        secciones = db.query(Seccion).filter(Seccion.escala_id == escala_id).order_by(Seccion.orden).all()
        for s in secciones: db.expunge(s)
        return secciones

def eliminar_seccion(seccion_id: int) -> bool:
    with get_session() as db:
        db.query(Item).filter(Item.seccion_id == seccion_id).delete()
        sec = db.query(Seccion).filter(Seccion.id == seccion_id).first()
        if sec:
            db.delete(sec)
            return True
        return False

# ============================================================
# ÍTEMS
# ============================================================
def crear_item(seccion_id: int, nombre: str, puntaje_maximo: int = 0, tipo_entrada: str = "manual", orden: int = 1) -> Item:
    with get_session() as db:
        existe = db.query(Item).filter(
            Item.seccion_id == seccion_id, 
            Item.nombre.ilike(nombre.strip())
        ).first()
        if existe:
            return None
            
        nuevo = Item(seccion_id=seccion_id, nombre=nombre.strip(), puntaje_maximo=puntaje_maximo, tipo_entrada=tipo_entrada, orden=orden)
        db.add(nuevo); db.flush(); db.expunge(nuevo)
        return nuevo

def listar_items(seccion_id: int) -> List[Item]:
    with get_session() as db:
        items = db.query(Item).filter(Item.seccion_id == seccion_id).order_by(Item.orden).all()
        for i in items: db.expunge(i)
        return items

def eliminar_item(item_id: int) -> bool:
    with get_session() as db:
        item = db.query(Item).filter(Item.id == item_id).first()
        if item:
            db.delete(item)
            return True
        return False

# ============================================================
# PATOLOGÍAS Y ESCALAS (VÍNCULOS)
# ============================================================
def vincular_escala_a_patologia(patologia_id: int, escala_id: int, tipo: str = "Sugerida") -> bool:
    with get_session() as db:
        existe = db.query(PatologiaEscala).filter_by(patologia_id=patologia_id, escala_id=escala_id).first()
        if existe: return False
        
        nueva = PatologiaEscala(patologia_id=patologia_id, escala_id=escala_id, tipo_requerimiento=tipo)
        db.add(nueva)
        return True

def listar_escalas_por_patologia(patologia_id: int) -> List[dict]:
    with get_session() as db:
        relaciones = db.query(PatologiaEscala).filter_by(patologia_id=patologia_id).all()
        resultado = []
        for rel in relaciones:
            resultado.append({
                "escala": rel.escala,
                "tipo_requerimiento": rel.tipo_requerimiento
            })
        return resultado

def desvincular_escala_de_patologia(patologia_id: int, escala_id: int) -> bool:
    with get_session() as db:
        rel = db.query(PatologiaEscala).filter_by(
            patologia_id=patologia_id, escala_id=escala_id
        ).first()
        if rel:
            db.delete(rel)
            return True
        return False
from modelos.escalas import EvaluacionMaestra, EvaluacionMaestraEscala, PatologiaEvaluacionMaestra

# --- CRUD DE EVALUACIONES MAESTRAS ---
def crear_evaluacion_maestra(nombre: str, categoria: str, descripcion: str = None) -> EvaluacionMaestra:
    with get_session() as db:
        nueva = EvaluacionMaestra(nombre=nombre, categoria=categoria, descripcion=descripcion)
        db.add(nueva); db.flush(); db.expunge(nueva)
        return nueva

def listar_evaluaciones_maestras() -> List[EvaluacionMaestra]:
    with get_session() as db:
        evals = db.query(EvaluacionMaestra).order_by(EvaluacionMaestra.nombre).all()
        for e in evals: db.expunge(e)
        return evals

def buscar_evaluacion_maestra_por_nombre(nombre: str) -> Optional[EvaluacionMaestra]:
    with get_session() as db:
        e = db.query(EvaluacionMaestra).filter(EvaluacionMaestra.nombre.ilike(nombre.strip())).first()
        if e: db.expunge(e)
        return e

# --- ENLAZAR ESCALA A EVALUACION ---
def vincular_escala_a_evaluacion(evaluacion_id: int, escala_id: int) -> bool:
    with get_session() as db:
        existe = db.query(EvaluacionMaestraEscala).filter_by(evaluacion_id=evaluacion_id, escala_id=escala_id).first()
        if existe: return False
        nueva = EvaluacionMaestraEscala(evaluacion_id=evaluacion_id, escala_id=escala_id)
        db.add(nueva)
        return True

def listar_escalas_de_evaluacion(evaluacion_id: int) -> List[Escala]:
    with get_session() as db:
        vinculos = db.query(EvaluacionMaestraEscala).filter_by(evaluacion_id=evaluacion_id).all()
        escalas = [v.escala for v in vinculos]
        for e in escalas: db.expunge(e)
        return escalas

# --- ENLAZAR EVALUACION A PATOLOGIA ---
def vincular_evaluacion_a_patologia(patologia_id: int, evaluacion_id: int, tipo: str = "Obligatoria") -> bool:
    with get_session() as db:
        existe = db.query(PatologiaEvaluacionMaestra).filter_by(patologia_id=patologia_id, evaluacion_id=evaluacion_id).first()
        if existe: return False
        nueva = PatologiaEvaluacionMaestra(patologia_id=patologia_id, evaluacion_id=evaluacion_id, tipo_requerimiento=tipo)
        db.add(nueva)
        return True

def listar_evaluaciones_de_patologia(patologia_id: int) -> List[dict]:
    with get_session() as db:
        vinculos = db.query(PatologiaEvaluacionMaestra).filter_by(patologia_id=patologia_id).all()
        resultado = []
        for v in vinculos:
            resultado.append({
                "evaluacion": v.evaluacion,
                "tipo_requerimiento": v.tipo_requerimiento
            })
        return resultado

def eliminar_escala(escala_id: int) -> bool:
    """Elimina una escala completa, sus secciones, ítems y vínculos."""
    from modelos.escalas import EvaluacionMaestraEscala, PatologiaEscala
    with get_session() as db:
        # 1. Borrar vínculos con patologías viejas
        db.query(PatologiaEscala).filter(PatologiaEscala.escala_id == escala_id).delete()
        
        # 2. Borrar vínculos con las nuevas evaluaciones maestras
        db.query(EvaluacionMaestraEscala).filter(EvaluacionMaestraEscala.escala_id == escala_id).delete()
        
        # 3. Borrar ítems y secciones
        secciones = db.query(Seccion).filter(Seccion.escala_id == escala_id).all()
        for sec in secciones:
            db.query(Item).filter(Item.seccion_id == sec.id).delete()
            db.delete(sec)
            
        # 4. Borrar la escala
        escala = db.query(Escala).filter(Escala.id == escala_id).first()
        if escala:
            db.delete(escala)
            return True
        return False