
#! FACTIONS - Datos visuales de las 4 facciones

#* Estructura de cada facción:
#TODO "nombre": str
#TODO "descripcion": str
#* colores:
#TODO "fondo": color del mapa
#TODO "base": color de la base central
#TODO "muro": color de los muros
#TODO "torre_ardiente" / "torre_cañonera" / "torre_arqueros"
#TODO "unidad_melee" / "unidad_ranger" / "unidad_mago"
#* etiquetas:
#TODO "base_label": texto que aparece en la celda de la base
#TODO "muro_label": etc.

FACCIONES: dict[str, dict] = {
    "robotica": {
        "nombre": "Robótica",
        "descripcion": "Torres y muros tecnológicos. Unidades mecánicas.",
        "colores": {
            "fondo":           "#0d1117",
            "base":            "#00bcd4",
            "muro":            "#455a64",
            "torre_ardiente":  "#f44336",
            "torre_cañonera":  "#9c27b0",
            "torre_arqueros":  "#2196f3",
            "unidad_melee":    "#4caf50",
            "unidad_ranger":   "#ff9800",
            "unidad_mago":     "#e91e63",
            "celda_libre":     "#1e2a38",
            "celda_borde":     "#263238",
        },
        "etiquetas": {
            "base_label":            "⚡",
            "muro_label":            "▦",
            "torre_ardiente_label":  "🔥",
            "torre_cañonera_label":  "💣",
            "torre_arqueros_label":  "📡",
            "unidad_melee_label":    "🤖",
            "unidad_ranger_label":   "🦾",
            "unidad_mago_label":     "☢",
        },
    },
    "medieval": {
        "nombre": "Medieval",
        "descripcion": "Castillos de piedra, soldados, magos y arqueros.",
        "colores": {
            "fondo":           "#2c1810",
            "base":            "#8d6e63",
            "muro":            "#795548",
            "torre_ardiente":  "#ff5722",
            "torre_cañonera":  "#607d8b",
            "torre_arqueros":  "#8bc34a",
            "unidad_melee":    "#f44336",
            "unidad_ranger":   "#4caf50",
            "unidad_mago":     "#9c27b0",
            "celda_libre":     "#3e2723",
            "celda_borde":     "#4e342e",
        },
        "etiquetas": {
            "base_label":            "🏰",
            "muro_label":            "🧱",
            "torre_ardiente_label":  "🔥",
            "torre_cañonera_label":  "⚙",
            "torre_arqueros_label":  "🏹",
            "unidad_melee_label":    "⚔",
            "unidad_ranger_label":   "🏹",
            "unidad_mago_label":     "🪄",
        },
    },
    "submarina": {
        "nombre": "Submarina",
        "descripcion": "Corales. Unidades marinas.",
        "colores": {
            "fondo":           "#01579b",
            "base":            "#00acc1",
            "muro":            "#0288d1",
            "torre_ardiente":  "#e53935",
            "torre_cañonera":  "#ab47bc",
            "torre_arqueros":  "#26c6da",
            "unidad_melee":    "#66bb6a",
            "unidad_ranger":   "#ffa726",
            "unidad_mago":     "#ec407a",
            "celda_libre":     "#0277bd",
            "celda_borde":     "#01579b",
        },
        "etiquetas": {
            "base_label":            "🐚",
            "muro_label":            "🪸",
            "torre_ardiente_label":  "🔥",
            "torre_cañonera_label":  "🫧",
            "torre_arqueros_label":  "🐠",
            "unidad_melee_label":    "🦈",
            "unidad_ranger_label":   "🐡",
            "unidad_mago_label":     "🐙",
        },
    },
    "fantastica": {
        "nombre": "Fantástica",
        "descripcion": "Objetos fantásticos. Tropas mágicas y maravillosas.",
        "colores": {
            "fondo":           "#1b5e20",
            "base":            "#2e7d32",
            "muro":            "#4e342e",
            "torre_ardiente":  "#ff8f00",
            "torre_cañonera":  "#6d4c41",
            "torre_arqueros":  "#66bb6a",
            "unidad_melee":    "#a5d6a7",
            "unidad_ranger":   "#fff176",
            "unidad_mago":     "#ce93d8",
            "celda_libre":     "#2e7d32",
            "celda_borde":     "#1b5e20",
        },
        "etiquetas": {
            "base_label":            "🌳",
            "muro_label":            "🪵",
            "torre_ardiente_label":  "🌿",
            "torre_cañonera_label":  "🪨",
            "torre_arqueros_label":  "🍃",
            "unidad_melee_label":    "🧝",
            "unidad_ranger_label":   "🏹",
            "unidad_mago_label":     "⚗",
        },
    },
}

LISTA_FACCIONES = list(FACCIONES.keys())

#! Nombres de unidades atacantes por facción
#* Orden: melee, ranger, mago
NOMBRES_UNIDADES: dict[str, dict[str, str]] = {
    "robotica": {
        "melee":  "Androide K-9",
        "ranger": "Drone Centinela",
        "mago":   "NEXUS-7",
    },
    "medieval": {
        "melee":  "Caballero Oscuro",
        "ranger": "Arquero Élite",
        "mago":   "Archibrujo",
    },
    "submarina": {
        "melee":  "Tiburón Blindado",
        "ranger": "Anguila Francotiradora",
        "mago":   "Kraken Antiguo",
    },
    "fantastica": {
        "melee":  "Ent Guerrero",
        "ranger": "Elfo Cazador",
        "mago":   "Druida Mayor",
    },
}


def obtener_faccion(clave: str) -> dict:
    return FACCIONES.get(clave, FACCIONES["medieval"])


def get_color(faccion_clave: str, elemento: str) -> str:
    fac = obtener_faccion(faccion_clave)
    return fac["colores"].get(elemento, "#888888")


def get_etiqueta(faccion_clave: str, elemento: str) -> str:
    fac = obtener_faccion(faccion_clave)
    return fac["etiquetas"].get(elemento, "?")


def get_nombre_unidad(faccion_clave: str, subtipo: str) -> str:
    """Retorna el nombre temático de una unidad según la facción del atacante."""
    return NOMBRES_UNIDADES.get(faccion_clave, {}).get(subtipo, subtipo.capitalize())
