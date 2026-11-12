"""
modelos/__init__.py
-------------------
Importa TODOS los modelos.
"""

from modelos.usuario import Usuario
from modelos.paciente import Paciente
from modelos.evaluacion import Evaluacion
from modelos.sesion import Sesion
from modelos.patologia import Patologia
from modelos.paciente_patologia import PacientePatologia
from modelos.escalas import Escala, Seccion, Item, PatologiaEscala
# Agrégalos a la lista __all__

__all__ = ["Usuario", "Paciente", "Evaluacion", "Sesion", "Patologia", "PacientePatologia"]