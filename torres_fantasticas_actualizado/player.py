
#! PLAYER - Registro, login y persistencia de jugadores

import json
import os
import hashlib

RUTA_DATOS = os.path.join(os.path.dirname(__file__), "data", "players.json")


def _hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _cargar_datos() -> dict:
    if not os.path.exists(RUTA_DATOS):
        return {}
    with open(RUTA_DATOS, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _guardar_datos(datos: dict):
    os.makedirs(os.path.dirname(RUTA_DATOS), exist_ok=True)
    with open(RUTA_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


#! OPERACIONES DE CUENTA

def registrar_jugador(nombre: str, password: str) -> tuple[bool, str]:
    """Registra un nuevo jugador. Retorna (éxito, mensaje)."""
    if not nombre.strip() or not password.strip():
        return False, "El nombre y contraseña no pueden estar vacíos."
    datos = _cargar_datos()
    if nombre in datos:
        return False, f"El usuario '{nombre}' ya existe."
    datos[nombre] = {
        "password": _hash_pass(password),
        "victorias_defensor": 0,
        "victorias_atacante": 0,
    }
    _guardar_datos(datos)
    return True, f"Usuario '{nombre}' registrado correctamente."


def iniciar_sesion(nombre: str, password: str) -> tuple[bool, str]:
    """Verifica credenciales. Retorna (éxito, mensaje)."""
    datos = _cargar_datos()
    if nombre not in datos:
        return False, "Usuario no encontrado."
    if datos[nombre]["password"] != _hash_pass(password):
        return False, "Contraseña incorrecta."
    return True, "Sesión iniciada correctamente."


def actualizar_victoria(nombre: str, rol: str):
    """Suma una victoria al jugador según su rol ('defensor' o 'atacante')."""
    datos = _cargar_datos()
    if nombre not in datos:
        return
    clave = f"victorias_{rol}"
    datos[nombre][clave] = datos[nombre].get(clave, 0) + 1
    _guardar_datos(datos)


def obtener_ranking(rol: str, top: int = 5) -> list[dict]:
    """Retorna lista ordenada de dicts {nombre, victorias} para el rol dado."""
    datos = _cargar_datos()
    clave = f"victorias_{rol}"
    jugadores = [
        {"nombre": n, "victorias": info.get(clave, 0)}
        for n, info in datos.items()
    ]
    jugadores.sort(key=lambda x: x["victorias"], reverse=True)
    return jugadores[:top]


def obtener_stats(nombre: str) -> dict:
    """Retorna las estadísticas de un jugador o dict vacío si no existe."""
    datos = _cargar_datos()
    if nombre not in datos:
        return {}
    info = datos[nombre]
    return {
        "nombre": nombre,
        "victorias_defensor": info.get("victorias_defensor", 0),
        "victorias_atacante": info.get("victorias_atacante", 0),
    }


#! CLASE JUGADOR (estado en partida)

class Jugador:
    DINERO_INICIAL_DEFENSOR = 2000
    DINERO_INICIAL_ATACANTE = 1100
    BONO_POR_RONDA = 700

    def __init__(self, nombre: str, rol: str, faccion: str):
        self.nombre = nombre
        self.rol = rol          #* "defensor" o "atacante"
        self.faccion = faccion
        #TODO Cada rol arranca con su propia economía
        self.dinero = (self.DINERO_INICIAL_DEFENSOR if rol == "defensor"
                       else self.DINERO_INICIAL_ATACANTE)
        self.rondas_ganadas = 0

    def sumar_bono_ronda(self):
        self.dinero += self.BONO_POR_RONDA

    def ganar_ronda(self):
        self.rondas_ganadas += 1

    def gano_partida(self) -> bool:
        return self.rondas_ganadas >= 3

    def cobrar(self, cantidad: int) -> bool:
        """Descuenta dinero si hay suficiente. Retorna True si tuvo éxito."""
        if self.dinero >= cantidad:
            self.dinero -= cantidad
            return True
        return False

    def sumar_dinero(self, cantidad: int):
        self.dinero += cantidad

    def dinero_inicial(self) -> int:
        """Dinero con el que arranca el jugador según su rol."""
        return (self.DINERO_INICIAL_DEFENSOR if self.rol == "defensor"
                else self.DINERO_INICIAL_ATACANTE)

    def restaurar_dinero_minimo(self) -> bool:
        """Si el dinero quedó por debajo del inicial, lo sube al inicial.

        Retorna True si hubo que reponer (para poder registrarlo en el log).
        """
        minimo = self.dinero_inicial()
        if self.dinero < minimo:
            self.dinero = minimo
            return True
        return False

    def __repr__(self):
        return f"Jugador({self.nombre}, {self.rol}, dinero={self.dinero}, rondas={self.rondas_ganadas})"
