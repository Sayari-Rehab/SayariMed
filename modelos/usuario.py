"""
modelos/usuario.py
------------------
Modelo de Usuario: admin, terapeutas y (futuro) practicantes.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from core.database import Base
from config.constants import (
    ROL_ADMIN,
    ROL_TERAPEUTA,
    ESTADO_USUARIO_ACTIVO,
)


class Usuario(Base):
    __tablename__ = "usuarios"

    # ------------------------------------------------------------
    # Identificación
    # ------------------------------------------------------------
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=True, index=True)

    # ------------------------------------------------------------
    # Documentos oficiales
    # ------------------------------------------------------------
    dni = Column(String(8), unique=True, nullable=True, index=True)
    colegiatura = Column(String(20), unique=True, nullable=True, index=True)
    colegiatura_pendiente = Column(Boolean, nullable=False, default=False)

    # ------------------------------------------------------------
    # Seguridad
    # ------------------------------------------------------------
    password_hash = Column(String(255), nullable=False)

    # ------------------------------------------------------------
    # Datos personales
    # ------------------------------------------------------------
    nombre_completo = Column(String(150), nullable=False)
    telefono = Column(String(30), nullable=True)
    titulo = Column(String(50), nullable=True)
    especialidad = Column(Text, nullable=True)
    foto_url = Column(String(500), nullable=True)

    # ------------------------------------------------------------
    # Rol y estado
    # ------------------------------------------------------------
    rol = Column(String(20), nullable=False, default=ROL_TERAPEUTA)
    estado = Column(String(20), nullable=False, default=ESTADO_USUARIO_ACTIVO)
    activo = Column(Boolean, nullable=False, default=True)

    # ------------------------------------------------------------
    # Practicantes (preparado para futuro)
    # ------------------------------------------------------------
    es_practicante = Column(Boolean, nullable=False, default=False)
    tutor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    puede_tener_practicantes = Column(Boolean, nullable=False, default=False)

    # ------------------------------------------------------------
    # Auditoría
    # ------------------------------------------------------------
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # ------------------------------------------------------------
    # Relaciones
    # ------------------------------------------------------------
    pacientes = relationship(
        "Paciente",
        back_populates="terapeuta",
        foreign_keys="Paciente.terapeuta_id",
    )

    # ------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------
    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, username='{self.username}', rol='{self.rol}')>"

    @property
    def es_admin(self) -> bool:
        return self.rol == ROL_ADMIN

    @property
    def es_terapeuta(self) -> bool:
        return self.rol == ROL_TERAPEUTA

    @property
    def esta_activo(self) -> bool:
        return self.activo and self.estado == ESTADO_USUARIO_ACTIVO

    @property
    def nombre_con_titulo(self) -> str:
        """Devuelve 'Lic. Juan Pérez' o 'Dr. Juan Pérez'."""
        titulo_corto = {
            "Licenciado(a)": "Lic.",
            "Magíster": "Mg.",
            "Doctor(a)": "Dr(a).",
        }.get(self.titulo or "", "")
        if titulo_corto:
            return f"{titulo_corto} {self.nombre_completo}"
        return self.nombre_completo

    @property
    def lista_especialidades(self) -> list:
        """Devuelve la lista de especialidades."""
        if not self.especialidad:
            return []
        return [e.strip() for e in self.especialidad.split(",") if e.strip()]

    @property
    def tiene_colegiatura(self) -> bool:
        """True si tiene N° de colegiatura válido."""
        return bool(self.colegiatura) and not self.colegiatura_pendiente