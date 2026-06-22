
#! GAME - Motor de lógica: rondas, combate, economía

from map_grid import MapaJuego, BASE_FILA, BASE_COL, FILAS, COLS
from entities import (
    Torre, TorreArdiente, TorreCañonera, TorreArqueros,
    Unidad, UnidadMelee, UnidadRanger, UnidadMago,
    Muro, Base,
    crear_torre, crear_unidad,
    COSTOS_TORRES, COSTOS_UNIDADES,
)
from player import Jugador, actualizar_victoria
from factions import get_nombre_unidad

#! RECOMPENSAS

RECOMPENSA_ELIMINAR = {
    "melee":  15,
    "ranger": 30,
    "mago":   80,
}

RECOMPENSA_DAÑAR_TORRE   = 2
RECOMPENSA_DESTRUIR_TORRE = 50
RECOMPENSA_DAÑAR_BASE    = 5    #* por cada 10 de daño


class MotorJuego:
    RONDAS_PARA_GANAR  = 3
    TURNOS_POR_OLEADA  = 3   #* oleadas que el defensor debe sobrevivir para ganar

    def __init__(self, defensor: Jugador, atacante: Jugador):
        self.defensor = defensor
        self.atacante = atacante
        self.mapa = MapaJuego()
        self.numero_ronda = 1
        self.turno_oleada = 0           #* oleadas completadas en la ronda actual
        self.fase = "construccion"
        self.log: list[str] = []
        self.ganador_partida: str | None = None
        self._danio_base_ronda = 0

    #! FASE DE CONSTRUCCIÓN (defensor)

    def iniciar_fase_construccion(self):
        self.defensor.sumar_bono_ronda()
        self.fase = "construccion"
        self._log(f"── Ronda {self.numero_ronda}: fase de construcción del defensor ({self.defensor.nombre})")
        self._log(f"   Dinero disponible: {self.defensor.dinero} monedas")

    def defensor_colocar_torre(self, subtipo: str, fila: int, col: int) -> tuple[bool, str]:
        costo = COSTOS_TORRES.get(subtipo, 999)
        if not self.defensor.cobrar(costo):
            return False, f"Sin fondos. Necesitas {costo}, tienes {self.defensor.dinero}."
        torre = crear_torre(subtipo, fila, col)
        if not self.mapa.colocar_torre(torre):
            self.defensor.sumar_dinero(costo)  # devolver
            return False, "Casilla ocupada o fuera de la zona defensora."
        self._log(f"   Torre '{torre.nombre}' colocada en ({fila},{col}).")
        return True, f"Torre '{torre.nombre}' colocada. Costo: {costo}."

    def defensor_colocar_muro(self, fila: int, col: int) -> tuple[bool, str]:
        costo = Muro.COSTO
        if not self.defensor.cobrar(costo):
            return False, f"Sin fondos. Necesitas {costo}, tienes {self.defensor.dinero}."
        muro = Muro(fila, col)
        if not self.mapa.colocar_muro(muro):
            self.defensor.sumar_dinero(costo)
            return False, "Casilla ocupada o fuera de la zona defensora."
        self._log(f"   Muro colocado en ({fila},{col}).")
        return True, f"Muro colocado. Costo: {costo}."

    def terminar_fase_construccion(self):
        self.fase = "ataque"
        self.atacante.sumar_bono_ronda()
        self._log(f"── Fase de compra del atacante ({self.atacante.nombre})")
        self._log(f"   Dinero disponible: {self.atacante.dinero} monedas")

    #! FASE DE ATAQUE (atacante compra unidades)

    def atacante_comprar_unidad(self, subtipo: str, fila: int) -> tuple[bool, str]:
        costo = COSTOS_UNIDADES.get(subtipo, 999)
        if not self.atacante.cobrar(costo):
            return False, f"Sin fondos. Necesitas {costo}, tienes {self.atacante.dinero}."
        if not (0 <= fila < FILAS):
            self.atacante.sumar_dinero(costo)
            return False, "Fila inválida."
        unidad = crear_unidad(subtipo, fila, COLS - 1)
        # Nombre temático según la facción del atacante
        unidad.nombre = get_nombre_unidad(self.atacante.faccion, subtipo)
        if not self.mapa.colocar_unidad(unidad):
            self.atacante.sumar_dinero(costo)
            return False, "No hay casilla libre en la zona de spawn."
        self._log(f"   '{unidad.nombre}' desplegado en fila {fila}.")
        return True, f"'{unidad.nombre}' comprado. Costo: {costo}."

    def terminar_fase_ataque(self):
        if not self.mapa.unidades:
            return False, "El atacante debe desplegar al menos una unidad."
        self.fase = "combate"
        self._danio_base_ronda = 0
        self._log("── Fase de combate iniciada")
        return True, "¡Combate comenzado!"

    #! FASE DE COMBATE (un tick)

    def tick_combate(self, dt: float = 1.0) -> dict:
        """
        Procesa un tick de combate.
        dt: tiempo transcurrido en segundos (para cooldowns).
        Retorna un resumen del tick con eventos ocurridos.
        """
        if self.fase != "combate":
            return {"fin": False, "eventos": []}

        eventos = []
        #* Sets para evitar duplicados
        torres_destruidas  = set()
        muros_destruidos   = set()
        unidades_muertas   = set()

        def _marcar_unidades_muertas():
            """Detecta cualquier unidad con vida=0 y la elimina del grid inmediatamente."""
            for u in list(self.mapa.unidades):
                if u.esta_muerta() and u not in unidades_muertas:
                    unidades_muertas.add(u)
                    #* Limpiar celda del grid ahora mismo para no bloquear movimiento
                    self.mapa.grid[u.fila][u.col] = None

        #* 1. Torres atacan a unidades en rango
        for torre in list(self.mapa.torres):
            if torre.esta_destruida():
                continue
            en_rango = [u for u in self.mapa.unidades
                        if not u.esta_muerta() and u not in unidades_muertas and torre.en_rango(u)]
            if en_rango and torre.puede_atacar(dt):
                objetivo = min(en_rango,
                               key=lambda u: abs(torre.fila - u.fila) + abs(torre.col - u.col))
                torre.atacar(objetivo)
                eventos.append(f"Torre {torre.nombre} atacó a {objetivo.nombre} (vida:{objetivo.vida})")
                if objetivo.esta_muerta():
                    recomp = RECOMPENSA_ELIMINAR.get(objetivo.subtipo, 10)
                    self.defensor.sumar_dinero(recomp)
                    eventos.append(f"  → {objetivo.nombre} eliminado. Defensor +{recomp}")

            #TODO Habilidades de torre — pueden matar múltiples unidades a la vez
            activada = torre.avanzar_turno(self.mapa.unidades, self.mapa.torres)
            if activada:
                eventos.append(f"  ★ Habilidad de {torre.nombre} activada")
                #TODO Barrido post-habilidad para atrapar muertes en área
                for u in self.mapa.unidades:
                    if u.esta_muerta() and u not in unidades_muertas:
                        recomp = RECOMPENSA_ELIMINAR.get(u.subtipo, 10)
                        self.defensor.sumar_dinero(recomp)
                        eventos.append(f"  → {u.nombre} eliminado por habilidad. Defensor +{recomp}")

            #TODO Limpiar grid de muertos tras cada torre para desbloquear casillas
            _marcar_unidades_muertas()

        #* 2. Unidades se mueven y atacan
        for unidad in list(self.mapa.unidades):
            if unidad.esta_muerta() or unidad in unidades_muertas:
                continue

            objetivo_cercano = self._objetivo_mas_cercano(unidad)
            if objetivo_cercano is None:
                continue

            if unidad.en_rango(objetivo_cercano):
                if unidad.puede_atacar(dt):
                    vida_antes = objetivo_cercano.vida
                    unidad.atacar(objetivo_cercano)
                    danio_real = vida_antes - objetivo_cercano.vida
                    eventos.append(f"Unidad {unidad.nombre} atacó {getattr(objetivo_cercano,'nombre','objetivo')} (vida:{objetivo_cercano.vida})")

                    if isinstance(objetivo_cercano, Base):
                        self._danio_base_ronda += danio_real
                        recomp_base = (danio_real // 10) * RECOMPENSA_DAÑAR_BASE
                        self.atacante.sumar_dinero(recomp_base)
                    elif isinstance(objetivo_cercano, Torre):
                        self.atacante.sumar_dinero(RECOMPENSA_DAÑAR_TORRE)
                        if objetivo_cercano.esta_destruida():
                            torres_destruidas.add(objetivo_cercano)
                            self.atacante.sumar_dinero(RECOMPENSA_DESTRUIR_TORRE)
                            eventos.append(f"  → Torre {objetivo_cercano.nombre} destruida. Atacante +{RECOMPENSA_DESTRUIR_TORRE}")
                    elif isinstance(objetivo_cercano, Muro):
                        if objetivo_cercano.esta_destruido():
                            muros_destruidos.add(objetivo_cercano)
                            self.atacante.sumar_dinero(25)
                            eventos.append(f"  → Muro destruido. Atacante +25")

                activada = unidad.avanzar_turno(self._objetivos_para_habilidad())
                if activada:
                    eventos.append(f"  ★ Habilidad de {unidad.nombre} activada")
            else:
                #TODO Moverse hacia el objetivo
                prev_fila, prev_col = unidad.fila, unidad.col
                unidad.mover_hacia(objetivo_cercano.fila, objetivo_cercano.col, self.mapa)
                if unidad.fila != prev_fila or unidad.col != prev_col:
                    self.mapa.grid[prev_fila][prev_col] = None
                    self.mapa.grid[unidad.fila][unidad.col] = unidad

        #* 3. Barrido final — limpiar todo lo que quedó pendiente
        _marcar_unidades_muertas()

        #TODO Barrer torres/muros que llegaron a 0 por cualquier vía.
        for t in list(self.mapa.torres):
            if t.esta_destruida() and t not in torres_destruidas:
                torres_destruidas.add(t)
                self.atacante.sumar_dinero(RECOMPENSA_DESTRUIR_TORRE)
                eventos.append(f"  → Torre {t.nombre} destruida. Atacante +{RECOMPENSA_DESTRUIR_TORRE}")
        for m in list(self.mapa.muros):
            if m.esta_destruido() and m not in muros_destruidos:
                muros_destruidos.add(m)

        #* Eliminar definitivamente de las listas
        for u in unidades_muertas:
            if u in self.mapa.unidades:
                self.mapa.unidades.remove(u)
            #TODO El grid ya fue limpiado por _marcar_unidades_muertas
        for t in torres_destruidas:
            self.mapa.eliminar_torre(t)
        for m in muros_destruidos:
            self.mapa.eliminar_muro(m)

        #* 4. Verificar fin de ronda
        resultado = self._verificar_fin_ronda()
        self.log.extend(eventos)

        return {
            "fin": resultado is not None,
            "resultado": resultado,
            "eventos": eventos,
        }

    def _objetivo_mas_cercano(self, unidad: Unidad):
        """Encuentra el objeto más cercano (muro, torre o base) en la trayectoria."""
        candidatos = []

        #TODO Muros y torres delante de la unidad (col menor)
        for obj in self.mapa.muros + self.mapa.torres:
            destruido = (obj.esta_destruido() if hasattr(obj, 'esta_destruido')
                         else obj.esta_destruida() if hasattr(obj, 'esta_destruida') else False)
            if not destruido:
                candidatos.append(obj)

        candidatos.append(self.mapa.base)

        if not candidatos:
            return None

        return min(candidatos,
                   key=lambda o: abs(unidad.fila - o.fila) + abs(unidad.col - o.col))

    def _objetivos_para_habilidad(self):
        """Lista de objetivos que el mago puede atacar con habilidad."""
        return list(self.mapa.torres) + [self.mapa.base]

    def _verificar_fin_ronda(self) -> str | None:
        """
        Retorna 'atacante' si destruyó la base, 'oleada_superada' si el defensor
        eliminó todas las unidades, o None si el combate sigue.
        """
        if self.mapa.base.esta_destruida():
            return "atacante"
        vivas = [u for u in self.mapa.unidades if not u.esta_muerta()]
        if not vivas:
            return "oleada_superada"
        return None

    #! FIN DE OLEADA / FIN DE RONDA

    def resolver_fin_oleada(self, resultado: str) -> dict:
        """
        Procesa el resultado de una oleada.
        Retorna un dict con:
          - "tipo": "nueva_oleada" | "fin_ronda"
          - "ganador_ronda": str | None  (solo si tipo == "fin_ronda")
          - "turno_oleada": int
        """
        if resultado == "atacante":
            #TODO Base destruida → el atacante gana la ronda inmediatamente
            self._log(f"  💥 ¡Base destruida! El atacante gana la ronda.")
            return {"tipo": "fin_ronda", "ganador_ronda": "atacante"}

        #* Oleada superada por el defensor
        self.turno_oleada += 1
        self.defensor.sumar_dinero(500)
        self._log(f"  🛡 Oleada {self.turno_oleada}/{self.TURNOS_POR_OLEADA} superada. Defensor +500")

        if self.turno_oleada >= self.TURNOS_POR_OLEADA:
            #TODO Defensor aguantó todas las oleadas → gana la ronda
            self._log(f"  ✓ ¡Defensor sobrevivió {self.TURNOS_POR_OLEADA} oleadas! Gana la ronda.")
            return {"tipo": "fin_ronda", "ganador_ronda": "defensor"}

        #TODO Todavía quedan oleadas — limpiar SOLO las unidades y continuar.
        #TODO La base conserva su vida; solo se restaura al iniciar una nueva ronda.
        #TODO El defensor vuelve a construir con el dinero que le quede; al terminar,
        #TODO el atacante recibe su bono y compra (en terminar_fase_construccion).
        self.mapa.limpiar_oleada()
        self.fase = "construccion"
        self._log(f"── Oleada {self.turno_oleada + 1}: el defensor puede volver a construir")
        return {"tipo": "nueva_oleada", "ganador_ronda": None}

    def resolver_fin_ronda(self, ganador_rol: str):
        """Actualiza marcador y prepara siguiente ronda o fin de partida."""
        self.fase = "fin_ronda"
        self.turno_oleada = 0   #TODO resetear para la próxima ronda

        if ganador_rol == "defensor":
            self.defensor.ganar_ronda()
            self.defensor.sumar_dinero(1000)
            self._log(f"── Ronda {self.numero_ronda}: GANA EL DEFENSOR ({self.defensor.nombre}) (+1000)")
        else:
            self.atacante.ganar_ronda()
            self.atacante.sumar_dinero(450)
            self._log(f"── Ronda {self.numero_ronda}: GANA EL ATACANTE ({self.atacante.nombre}) (+450)")

        bono = (self._danio_base_ronda // 50) * 20
        if bono > 0:
            self.atacante.sumar_dinero(bono)

        #TODO Sin desventaja entre rondas: si alguien quedó por debajo de su
        #TODO dinero inicial (Defensor 2000 / Atacante 1300), se le repone al inicial.
        if self.defensor.restaurar_dinero_minimo():
            self._log(f"   {self.defensor.nombre} repuesto a su dinero inicial ({self.defensor.dinero}).")
        if self.atacante.restaurar_dinero_minimo():
            self._log(f"   {self.atacante.nombre} repuesto a su dinero inicial ({self.atacante.dinero}).")

        self._log(f"   Marcador: {self.defensor.nombre} {self.defensor.rondas_ganadas} - "
                  f"{self.atacante.rondas_ganadas} {self.atacante.nombre}")

        if self.defensor.gano_partida() or self.atacante.gano_partida():
            self._resolver_fin_partida()
        else:
            self.numero_ronda += 1
            self.mapa.limpiar_ronda()

    def _resolver_fin_partida(self):
        self.fase = "fin_partida"
        if self.defensor.gano_partida():
            self.ganador_partida = self.defensor.nombre
            actualizar_victoria(self.defensor.nombre, "defensor")
            self._log(f"★★★ ¡{self.defensor.nombre} gana la partida como DEFENSOR! ★★★")
        else:
            self.ganador_partida = self.atacante.nombre
            actualizar_victoria(self.atacante.nombre, "atacante")
            self._log(f"★★★ ¡{self.atacante.nombre} gana la partida como ATACANTE! ★★★")

    #! UTILIDADES

    def _log(self, mensaje: str):
        self.log.append(mensaje)

    def obtener_log_reciente(self, n: int = 10) -> list[str]:
        return self.log[-n:]

    def estado_resumen(self) -> dict:
        return {
            "ronda": self.numero_ronda,
            "turno_oleada": self.turno_oleada,
            "turnos_max": self.TURNOS_POR_OLEADA,
            "fase": self.fase,
            "defensor": {
                "nombre": self.defensor.nombre,
                "dinero": self.defensor.dinero,
                "rondas": self.defensor.rondas_ganadas,
            },
            "atacante": {
                "nombre": self.atacante.nombre,
                "dinero": self.atacante.dinero,
                "rondas": self.atacante.rondas_ganadas,
            },
            "base_vida": self.mapa.base.vida,
            "torres_activas": len([t for t in self.mapa.torres if not t.esta_destruida()]),
            "unidades_vivas": len([u for u in self.mapa.unidades if not u.esta_muerta()]),
            "ganador": self.ganador_partida,
        }
