
#! MAP_GRID - Cuadrícula del mapa y estado de casillas

from entities import Muro, Base, Torre, Unidad

FILAS = 12
COLS  = 14

#* Posición fija de la base central
BASE_FILA = FILAS // 2
BASE_COL  = 1

#* Columna de spawn de unidades atacantes (lado derecho)
SPAWN_COL = COLS - 1


class MapaJuego:
    """
    Mantiene el estado de todas las casillas.
    Cada casilla puede contener: None / Muro / Torre / Unidad / Base
    """

    def __init__(self):
        self.grid: list[list] = [[None] * COLS for _ in range(FILAS)]
        self.base = Base(BASE_FILA, BASE_COL)
        self.grid[BASE_FILA][BASE_COL] = self.base
        self.torres: list[Torre] = []
        self.muros: list[Muro] = []
        self.unidades: list[Unidad] = []

    #! CONSULTAS

    def casilla_libre(self, fila: int, col: int) -> bool:
        """True si la casilla existe y no tiene nada (o solo tiene un objeto ya destruido)."""
        if not self._en_limites(fila, col):
            return False
        obj = self.grid[fila][col]
        if obj is None:
            return True
        #TODO Casilla con unidad muerta o estructura destruida = transitable
        if hasattr(obj, 'esta_muerta') and obj.esta_muerta():
            return True
        if hasattr(obj, 'esta_destruido') and obj.esta_destruido():
            return True
        if hasattr(obj, 'esta_destruida') and obj.esta_destruida():
            return True
        return False

    def _en_limites(self, fila: int, col: int) -> bool:
        return 0 <= fila < FILAS and 0 <= col < COLS

    def obtener_casilla(self, fila: int, col: int):
        if not self._en_limites(fila, col):
            return None
        return self.grid[fila][col]

    #! COLOCACIÓN

    def colocar_torre(self, torre: Torre) -> bool:
        if not self.casilla_libre(torre.fila, torre.col):
            return False
        #TODO Las torres solo se pueden colocar en las primeras 6 columnas (zona defensora)
        if torre.col > COLS // 2:
            return False
        self.grid[torre.fila][torre.col] = torre
        self.torres.append(torre)
        return True

    def colocar_muro(self, muro: Muro) -> bool:
        if not self.casilla_libre(muro.fila, muro.col):
            return False
        #TODO Los muros solo se pueden colocar en las primeras 6 columnas (zona defensora)
        if muro.col > COLS // 2:
            return False
        self.grid[muro.fila][muro.col] = muro
        self.muros.append(muro)
        return True

    def colocar_unidad(self, unidad: Unidad) -> bool:
        """Las unidades se colocan en la columna de spawn o la adyacente."""
        fila = unidad.fila
        col  = unidad.col
        #TODO Buscar casilla libre en la zona de spawn (columnas 10-13)
        for c in range(COLS - 1, COLS - 5, -1):
            if self.casilla_libre(fila, c):
                unidad.col = c
                self.grid[fila][c] = unidad
                self.unidades.append(unidad)
                return True
        return False

    #! ELIMINACIÓN

    def eliminar_torre(self, torre: Torre):
        self.grid[torre.fila][torre.col] = None
        if torre in self.torres:
            self.torres.remove(torre)

    def eliminar_muro(self, muro: Muro):
        self.grid[muro.fila][muro.col] = None
        if muro in self.muros:
            self.muros.remove(muro)

    def eliminar_unidad(self, unidad: Unidad):
        self.grid[unidad.fila][unidad.col] = None
        if unidad in self.unidades:
            self.unidades.remove(unidad)

    def actualizar_posicion_unidad(self, unidad: Unidad, nueva_fila: int, nueva_col: int):
        """Mueve la referencia en el grid."""
        self.grid[unidad.fila][unidad.col] = None
        unidad.fila = nueva_fila
        unidad.col  = nueva_col
        self.grid[nueva_fila][nueva_col] = unidad

    #! RESET ENTRE RONDAS

    def limpiar_ronda(self):
        """Elimina unidades y restaura la base. Torres/muros permanecen."""
        for u in list(self.unidades):
            self.grid[u.fila][u.col] = None
        self.unidades.clear()
        self.base.vida = self.base.vida_max
        self.grid[BASE_FILA][BASE_COL] = self.base

    def reiniciar_completo(self):
        """Limpia todo para una nueva partida."""
        self.grid = [[None] * COLS for _ in range(FILAS)]
        self.base = Base(BASE_FILA, BASE_COL)
        self.grid[BASE_FILA][BASE_COL] = self.base
        self.torres.clear()
        self.muros.clear()
        self.unidades.clear()
