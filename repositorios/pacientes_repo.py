"""
repositorios/pacientes_repo.py
------------------------------
Operaciones CRUD sobre la tabla pacientes.

Reglas:
- Un terapeuta solo ve SUS pacientes.
- Un admin ve TODOS los pacientes.
"""

from typing import Optional, List
from sqlalchemy import or_

from core.database import get_session
from modelos import Usuario, Paciente, Evaluacion, Sesion, Patologia  # noqa: F401
from config.constants import ESTADO_PACIENTE_ACTIVO
from modelos import PacientePatologia, Patologia


# ============================================================
# LEER
# ============================================================
def listar_pacientes(
    terapeuta_id: Optional[int] = None,
    incluir_inactivos: bool = False,
) -> List[Paciente]:
    """
    Lista pacientes.
    - Si terapeuta_id se pasa, filtra por ese terapeuta.
    - Si es None, devuelve TODOS (uso admin).
    """
    with get_session() as db:
        query = db.query(Paciente)

        if terapeuta_id is not None:
            query = query.filter(Paciente.terapeuta_id == terapeuta_id)

        if not incluir_inactivos:
            query = query.filter(Paciente.activo == True)  # noqa: E712

        pacientes = query.order_by(Paciente.fecha_creacion.desc()).all()
        for p in pacientes:
            db.expunge(p)
        return pacientes


def buscar_paciente(
    termino: str,
    terapeuta_id: Optional[int] = None,
) -> List[Paciente]:
    """
    Busca pacientes por documento o nombre.
    Si terapeuta_id se pasa, restringe la búsqueda a sus pacientes.
    """
    if not termino or not termino.strip():
        return []

    t = f"%{termino.strip()}%"

    with get_session() as db:
        query = db.query(Paciente).filter(
            or_(
                Paciente.documento.ilike(t),
                Paciente.nombre_completo.ilike(t),
            )
        )

        if terapeuta_id is not None:
            query = query.filter(Paciente.terapeuta_id == terapeuta_id)

        pacientes = query.order_by(Paciente.nombre_completo).limit(50).all()
        for p in pacientes:
            db.expunge(p)
        return pacientes


def buscar_por_documento(documento: str) -> Optional[Paciente]:
    """Busca un paciente por su documento (DNI). Único."""
    with get_session() as db:
        paciente = db.query(Paciente).filter(
            Paciente.documento == documento.strip()
        ).first()
        if paciente:
            db.expunge(paciente)
        return paciente


def obtener_por_id(paciente_id: int) -> Optional[Paciente]:
    """Busca un paciente por su ID."""
    with get_session() as db:
        paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
        if paciente:
            db.expunge(paciente)
        return paciente


# ============================================================
# CREAR
# ============================================================
def crear_paciente(
    documento: str,
    nombre_completo: str,
    terapeuta_id: int,
    registrado_por_id: Optional[int] = None,
    edad: Optional[int] = None,
    fecha_nacimiento=None,
    sexo: Optional[str] = None,
    telefono: Optional[str] = None,
    correo: Optional[str] = None,
    ocupacion: Optional[str] = None,
    direccion: Optional[str] = None,
    categoria_patologica: Optional[str] = None,
    vino_con_diagnostico: bool = False,
    diagnostico_medico: Optional[str] = None,
    motivo_consulta: Optional[str] = None,
    antecedentes: Optional[str] = None,
    observaciones_ingreso: Optional[str] = None,
) -> Paciente:
    """Crea un nuevo paciente."""
    from config.constants import CATEGORIA_OTRAS

    with get_session() as db:
        nuevo = Paciente(
            documento=documento.strip(),
            nombre_completo=nombre_completo.strip(),
            terapeuta_id=terapeuta_id,
            registrado_por_id=registrado_por_id or terapeuta_id,
            edad=edad,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            telefono=telefono.strip() if telefono else None,
            correo=correo.strip() if correo else None,
            ocupacion=ocupacion.strip() if ocupacion else None,
            direccion=direccion.strip() if direccion else None,
            categoria_patologica=categoria_patologica or CATEGORIA_OTRAS,
            vino_con_diagnostico=vino_con_diagnostico,
            diagnostico_medico=diagnostico_medico.strip() if diagnostico_medico else None,
            motivo_consulta=motivo_consulta.strip() if motivo_consulta else None,
            antecedentes=antecedentes.strip() if antecedentes else None,
            observaciones_ingreso=observaciones_ingreso.strip() if observaciones_ingreso else None,
            estado=ESTADO_PACIENTE_ACTIVO,
            activo=True,
        )
        db.add(nuevo)
        db.flush()
        db.expunge(nuevo)
        return nuevo


def existe_documento(documento: str) -> bool:
    """True si ya existe un paciente con ese documento."""
    with get_session() as db:
        return db.query(Paciente).filter(
            Paciente.documento == documento.strip()
        ).first() is not None


# ============================================================
# ACTUALIZAR / ELIMINAR
# ============================================================
def cambiar_estado_paciente(paciente_id: int, activo: bool) -> bool:
    """Activa o desactiva a un paciente."""
    with get_session() as db:
        paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
        if not paciente:
            return False
        paciente.activo = activo
        if not activo:
            paciente.estado = "inactivo"
        else:
            paciente.estado = ESTADO_PACIENTE_ACTIVO
        return True


def contar_pacientes(terapeuta_id: Optional[int] = None) -> int:
    """Cuenta pacientes (opcionalmente filtrando por terapeuta)."""
    with get_session() as db:
        query = db.query(Paciente).filter(Paciente.activo == True)  # noqa: E712
        if terapeuta_id is not None:
            query = query.filter(Paciente.terapeuta_id == terapeuta_id)
        return query.count()

def agregar_patologia_a_paciente(paciente_id: int, patologia_id: int) -> bool:
    """Vincula una patología secundaria a un paciente."""
    with get_session() as db:
        # Verificar que no esté ya vinculada
        existe = db.query(PacientePatologia).filter_by(
            paciente_id=paciente_id, patologia_id=patologia_id
        ).first()
        if existe:
            return False
        
        nueva = PacientePatologia(paciente_id=paciente_id, patologia_id=patologia_id)
        db.add(nueva)
        return True

def listar_patologias_de_paciente(paciente_id: int) -> List[Patologia]:
    """Devuelve la lista de patologías secundarias de un paciente."""
    with get_session() as db:
        relaciones = db.query(PacientePatologia).filter_by(paciente_id=paciente_id).all()
        patologias = [rel.patologia for rel in relaciones]
        for p in patologias:
            db.expunge(p)
        return patologias

def remover_patologia_de_paciente(paciente_id: int, patologia_id: int) -> bool:
    """Elimina la vinculación de una patología secundaria."""
    with get_session() as db:
        rel = db.query(PacientePatologia).filter_by(
            paciente_id=paciente_id, patologia_id=patologia_id
        ).first()
        if rel:
            db.delete(rel)
            return True
        return False