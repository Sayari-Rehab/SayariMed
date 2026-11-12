"""
config/constants.py
-------------------
Listas fijas y contenido clínico de Sayari Med.

Si necesitas agregar un test, una categoría o un procedimiento nuevo,
lo haces SOLO aquí y toda la app lo verá.
"""

# ============================================================
# ROLES DE USUARIO
# ============================================================

ROL_ADMIN = "admin"
ROL_TERAPEUTA = "terapeuta"
ROL_PRACTICANTE = "practicante"

ROLES_VALIDOS = [ROL_ADMIN, ROL_TERAPEUTA, ROL_PRACTICANTE]

ETIQUETAS_ROL = {
    ROL_ADMIN: "Administrador",
    ROL_TERAPEUTA: "Licenciado(a)",
    ROL_PRACTICANTE: "Practicante",
}


# ============================================================
# ESTADOS DE USUARIO (contratación)
# ============================================================

ESTADO_USUARIO_ACTIVO = "activo"
ESTADO_USUARIO_INACTIVO = "inactivo"

ESTADOS_USUARIO = [ESTADO_USUARIO_ACTIVO, ESTADO_USUARIO_INACTIVO]


# ============================================================
# CATEGORÍAS PATOLÓGICAS (Ramas de la Fisioterapia)
# ============================================================

CATEGORIA_NEUROLOGICA = "Neurológica"
CATEGORIA_TRAUMATOLOGICA = "Traumatológica"
CATEGORIA_REUMATOLOGICA = "Reumatológica"
CATEGORIA_CARDIORESPIRATORIA = "Cardiorrespiratoria"
CATEGORIA_PEDIATRICA = "Pediátrica"
CATEGORIA_UROGINECOLOGICA = "Uroginecológica"
CATEGORIA_DEPORTIVA = "Deportiva"
CATEGORIA_OTRAS = "Otras / Preventivas"

CATEGORIAS_PATOLOGICAS = [
    CATEGORIA_NEUROLOGICA,
    CATEGORIA_TRAUMATOLOGICA,
    CATEGORIA_REUMATOLOGICA,
    CATEGORIA_CARDIORESPIRATORIA,
    CATEGORIA_PEDIATRICA,
    CATEGORIA_UROGINECOLOGICA,
    CATEGORIA_DEPORTIVA,
    CATEGORIA_OTRAS,
]

ICONOS_CATEGORIA = {
    CATEGORIA_NEUROLOGICA: "🧠",
    CATEGORIA_TRAUMATOLOGICA: "🦴",
    CATEGORIA_REUMATOLOGICA: "🦵",
    CATEGORIA_CARDIORESPIRATORIA: "🫁",
    CATEGORIA_PEDIATRICA: "👶",
    CATEGORIA_UROGINECOLOGICA: "🚺",
    CATEGORIA_DEPORTIVA: "⚽",
    CATEGORIA_OTRAS: "🩺",
}


# ============================================================
# TESTS CLÍNICOS POR CATEGORÍA
# (el corazón del motor de recomendaciones)
# ============================================================

# Estructura de cada test:
#   id:        identificador único interno (sin tildes ni espacios)
#   nombre:    cómo se muestra al terapeuta
#   prioridad: 1 = siempre, 2 = recomendado, 3 = opcional
#   descripcion: breve explicación clínica

TESTS_POR_CATEGORIA = {
    CATEGORIA_NEUROLOGICA: [
        {
            "id": "tinetti",
            "nombre": "Escala de Tinetti",
            "prioridad": 1,
            "descripcion": "Equilibrio y marcha. Riesgo de caídas.",
        },
        {
            "id": "ashworth",
            "nombre": "Escala de Ashworth Modificada",
            "prioridad": 1,
            "descripcion": "Medición de espasticidad muscular.",
        },
        {
            "id": "barthel",
            "nombre": "Test de Barthel / FIM",
            "prioridad": 2,
            "descripcion": "Independencia en actividades de la vida diaria.",
        },
        {
            "id": "tug",
            "nombre": "Timed Up and Go (TUG)",
            "prioridad": 1,
            "descripcion": "Movilidad funcional y agilidad.",
        },
    ],
    CATEGORIA_TRAUMATOLOGICA: [
        {
            "id": "eva",
            "nombre": "Escala Visual Analógica (EVA)",
            "prioridad": 1,
            "descripcion": "Intensidad del dolor (0 a 10).",
        },
        {
            "id": "goniometria",
            "nombre": "Goniometría articular",
            "prioridad": 1,
            "descripcion": "Rango de movimiento (ROM) activo/pasivo.",
        },
        {
            "id": "daniels",
            "nombre": "Fuerza Muscular (Daniels / MRC)",
            "prioridad": 1,
            "descripcion": "Balance muscular (0 a 5).",
        },
        {
            "id": "dash",
            "nombre": "Cuestionario DASH",
            "prioridad": 3,
            "descripcion": "Discapacidad de miembro superior.",
        },
        {
            "id": "koos",
            "nombre": "Cuestionario KOOS / IKDC",
            "prioridad": 3,
            "descripcion": "Evaluación funcional de rodilla.",
        },
        {
            "id": "oswestry",
            "nombre": "Índice de Oswestry",
            "prioridad": 3,
            "descripcion": "Discapacidad por lumbalgia.",
        },
    ],
    CATEGORIA_REUMATOLOGICA: [
        {
            "id": "eva",
            "nombre": "Escala Visual Analógica (EVA)",
            "prioridad": 1,
            "descripcion": "Intensidad del dolor (0 a 10).",
        },
        {
            "id": "goniometria",
            "nombre": "Goniometría articular",
            "prioridad": 1,
            "descripcion": "Rango de movimiento (ROM).",
        },
        {
            "id": "daniels",
            "nombre": "Fuerza Muscular (Daniels / MRC)",
            "prioridad": 2,
            "descripcion": "Balance muscular (0 a 5).",
        },
    ],
    CATEGORIA_OTRAS: [
        {
            "id": "eva",
            "nombre": "Escala Visual Analógica (EVA)",
            "prioridad": 1,
            "descripcion": "Intensidad del dolor (0 a 10).",
        },
        {
            "id": "goniometria",
            "nombre": "Goniometría articular",
            "prioridad": 2,
            "descripcion": "Rango de movimiento (ROM).",
        },
    ],
}

# Test adicional recomendado para adultos mayores (>= 65 años)
TEST_ADULTO_MAYOR = {
    "id": "chair_stand",
    "nombre": "30-second Chair Stand",
    "prioridad": 2,
    "descripcion": "Fuerza funcional en miembros inferiores.",
}

EDAD_ADULTO_MAYOR = 65


# ============================================================
# PROCEDIMIENTOS DE FISIOTERAPIA
# (lo que se aplica en cada sesión)
# ============================================================

PROCEDIMIENTOS = [
    "Cinesiterapia",
    "Electroterapia",
    "Terapia Manual",
    "Ejercicio Terapéutico",
    "Ultrasonido",
    "Termoterapia",
    "Crioterapia",
    "Tracción",
    "Vendaje Funcional",
    "Punción Seca",
    "Masoterapia",
    "Reeducación Postural",
]


# ============================================================
# ESTADOS DE PACIENTE
# ============================================================

ESTADO_PACIENTE_ACTIVO = "activo"
ESTADO_PACIENTE_ALTA = "alta"
ESTADO_PACIENTE_INACTIVO = "inactivo"

ESTADOS_PACIENTE = [
    ESTADO_PACIENTE_ACTIVO,
    ESTADO_PACIENTE_ALTA,
    ESTADO_PACIENTE_INACTIVO,
]


# ============================================================
# SEXO
# ============================================================

SEXO_MASCULINO = "M"
SEXO_FEMENINO = "F"
SEXO_OTRO = "Otro"

SEXOS = [SEXO_MASCULINO, SEXO_FEMENINO, SEXO_OTRO]