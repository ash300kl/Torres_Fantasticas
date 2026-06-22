
#! ENTITIES - Torres, Unidades, Muro, Base central

import random

#! CLASE BASE PARA UNIDADES DEFENSIVAS

class Muro:
    COSTO = 50

    def __init__(self, fila, col):
        self.fila = fila
        self.col = col
        self.vida = 150
        self.vida_max = 150
        self.tipo = "muro"

    def recibir_daño(self, cantidad):
        self.vida -= cantidad
        if self.vida < 0:
            self.vida = 0

    def esta_destruido(self):
        return self.vida <= 0


class Base:
    def __init__(self, fila, col):
        self.fila = fila
        self.col = col
        self.vida = 1500
        self.vida_max = 1500
        self.tipo = "base"

    def recibir_daño(self, cantidad):
        self.vida -= cantidad
        if self.vida < 0:
            self.vida = 0

    def esta_destruida(self):
        return self.vida <= 0


#! TORRES DEFENSIVAS

class Torre:
    """Clase principal de torre. Cada tipo sobreescribe sus stats."""

    def __init__(self, fila, col):
        self.fila = fila
        self.col = col
        self.tipo = "torre"
        self.subtipo = "basica"

        #* Stats base (sobreescritas por subclases)
        self.nombre = "Torre"
        self.costo = 100
        self.vida = 150
        self.vida_max = 150
        self.daño = 15
        self.alcance = 3
        self.cooldown_ataque = 2.0       #* segundos entre ataques
        self.tiempo_habilidad = 5        #* turnos para activar habilidad
        self.turno_actual = 0
        self._timer_ataque = 0.0

    def recibir_daño(self, cantidad):
        self.vida -= cantidad
        if self.vida < 0:
            self.vida = 0

    def esta_destruida(self):
        return self.vida <= 0

    def en_rango(self, unidad):
        dist = abs(self.fila - unidad.fila) + abs(self.col - unidad.col)
        return dist <= self.alcance

    def puede_atacar(self, dt):
        """Retorna True si ya pasó el cooldown."""
        self._timer_ataque += dt
        if self._timer_ataque >= self.cooldown_ataque:
            self._timer_ataque = 0.0
            return True
        return False

    def atacar(self, unidad):
        """Aplica daño normal a una unidad."""
        unidad.recibir_daño(self.daño)

    def habilidad_especial(self, unidades, torres):
        """Sobreescrita por cada subclase."""
        pass

    def avanzar_turno(self, unidades, torres):
        self.turno_actual += 1
        if self.turno_actual >= self.tiempo_habilidad:
            self.turno_actual = 0
            self.habilidad_especial(unidades, torres)
            return True   #* habilidad activada
        return False


class TorreArdiente(Torre):
    """Daño constante, moderado. Habilidad: llamarada a 3 tropas cercanas."""

    def __init__(self, fila, col):
        super().__init__(fila, col)
        self.subtipo = "ardiente"
        self.nombre = "Torre Ardiente"
        self.costo = 700
        self.vida = 190
        self.vida_max = 190
        self.daño = 20
        self.alcance = 4
        self.cooldown_ataque = 2.0
        self.tiempo_habilidad = 9

    def habilidad_especial(self, unidades, torres):
        """Llamarada: quema a las 3 tropas más cercanas (30 de daño extra)."""
        en_rango = [u for u in unidades if not u.esta_muerta() and self.en_rango(u)]
        en_rango.sort(key=lambda u: abs(self.fila - u.fila) + abs(self.col - u.col))
        objetivo = en_rango[:3]
        for u in objetivo:
            u.recibir_daño(30)
        return objetivo


class TorreCañonera(Torre):
    """Muy lenta pero alto daño. Habilidad: elimina la tropa más cercana."""

    def __init__(self, fila, col):
        super().__init__(fila, col)
        self.subtipo = "cañonera"
        self.nombre = "Torre Cañonera"
        self.costo = 750
        self.vida = 200
        self.vida_max = 200
        self.daño = 60
        self.alcance = 8
        self.cooldown_ataque = 6.0
        self.tiempo_habilidad = 18

    def habilidad_especial(self, unidades, torres):
        """Proyectil especial: elimina la tropa más cercana sin importar su vida."""
        en_rango = [u for u in unidades if not u.esta_muerta() and self.en_rango(u)]
        if en_rango:
            objetivo = min(en_rango, key=lambda u: abs(self.fila - u.fila) + abs(self.col - u.col))
            objetivo.vida = 0
            return [objetivo]
        return []


class TorreArqueros(Torre):
    """Disparo rápido, daño bajo, alcance alto. Habilidad: cura todas las torres."""

    def __init__(self, fila, col):
        super().__init__(fila, col)
        self.subtipo = "arqueros"
        self.nombre = "Torre de Arqueros"
        self.costo = 80
        self.vida = 100
        self.vida_max = 100
        self.daño = 10
        self.alcance = 10
        self.cooldown_ataque = 3.0
        self.tiempo_habilidad = 8

    def habilidad_especial(self, unidades, torres):
        """Cura 10 puntos de vida a todas las torres aliadas."""
        curadas = []
        for t in torres:
            if not t.esta_destruida():
                t.vida = min(t.vida + 10, t.vida_max)
                curadas.append(t)
        return curadas


#! UNIDADES ATACANTES

class Unidad:
    """Clase base para unidades atacantes."""

    def __init__(self, fila, col):
        self.fila = fila
        self.col = col
        self.tipo = "unidad"
        self.subtipo = "melee"

        self.nombre = "Unidad"
        self.costo = 30
        self.vida = 150
        self.vida_max = 150
        self.daño = 40
        self.velocidad = 1               #* casillas por turno
        self.alcance = 1
        self.cooldown_ataque = 1.5
        self.tiempo_habilidad = 4
        self.turno_actual = 0
        self._timer_ataque = 0.0
        self._habilidad_usada = False

    def recibir_daño(self, cantidad):
        self.vida -= cantidad
        if self.vida < 0:
            self.vida = 0

    def esta_muerta(self):
        return self.vida <= 0

    def en_rango(self, objetivo):
        dist = abs(self.fila - objetivo.fila) + abs(self.col - objetivo.col)
        return dist <= self.alcance

    def puede_atacar(self, dt):
        self._timer_ataque += dt
        if self._timer_ataque >= self.cooldown_ataque:
            self._timer_ataque = 0.0
            return True
        return False

    def atacar(self, objetivo):
        objetivo.recibir_daño(self.daño)

    def mover_hacia(self, objetivo_fila, objetivo_col, mapa):
        """Mueve la unidad 'velocidad' casillas hacia el objetivo."""
        pasos = self.velocidad
        for _ in range(pasos):
            df = objetivo_fila - self.fila
            dc = objetivo_col - self.col
            if df == 0 and dc == 0:
                break
            #* Prioriza el eje con mayor distancia
            if abs(df) >= abs(dc):
                nueva_fila = self.fila + (1 if df > 0 else -1)
                nueva_col = self.col
            else:
                nueva_fila = self.fila
                nueva_col = self.col + (1 if dc > 0 else -1)
            #* Solo mover si la casilla destino está libre de muros/torres
            if mapa.casilla_libre(nueva_fila, nueva_col):
                self.fila = nueva_fila
                self.col = nueva_col

    def habilidad_especial(self, contexto):
        pass

    def avanzar_turno(self, contexto):
        self.turno_actual += 1
        if self.turno_actual >= self.tiempo_habilidad:
            self.turno_actual = 0
            self.habilidad_especial(contexto)
            return True
        return False


class UnidadMelee(Unidad):
    """Cuerpo a cuerpo, costo bajo. Habilidad: escudo temporal (+20 vida)."""

    def __init__(self, fila, col):
        super().__init__(fila, col)
        self.subtipo = "melee"
        self.nombre = "Melee"
        self.costo = 50
        self.vida = 150
        self.vida_max = 150
        self.daño = 30
        self.velocidad = 1
        self.alcance = 1
        self.cooldown_ataque = 1.5
        self.tiempo_habilidad = 5

    def habilidad_especial(self, contexto):
        """Escudo: aumenta vida máxima y vida actual en 20."""
        self.vida_max += 20
        self.vida = min(self.vida + 20, self.vida_max)


class UnidadRanger(Unidad):
    """Rango medio, disparo cada 4s. Habilidad: daño x2 por 1 turno."""

    def __init__(self, fila, col):
        super().__init__(fila, col)
        self.subtipo = "ranger"
        self.nombre = "Ranger"
        self.costo = 150
        self.vida = 180
        self.vida_max = 180
        self.daño = 20
        self.velocidad = 1
        self.alcance = 5
        self.cooldown_ataque = 4.0
        self.tiempo_habilidad = 3
        self._doble_daño = False
        self._turnos_doble = 0

    def atacar(self, objetivo):
        mult = 2 if self._doble_daño else 1
        objetivo.recibir_daño(self.daño * mult)
        if self._doble_daño:
            self._turnos_doble -= 1
            if self._turnos_doble <= 0:
                self._doble_daño = False

    def habilidad_especial(self, contexto):
        """Activa daño doble por 2 turnos."""
        self._doble_daño = True
        self._turnos_doble = 2


class UnidadMago(Unidad):
    """Movimiento lento, daño pesado. Habilidad: ataque único de 200 daño."""

    def __init__(self, fila, col):
        super().__init__(fila, col)
        self.subtipo = "mago"
        self.nombre = "Mago"
        self.costo = 540
        self.vida = 220
        self.vida_max = 220
        self.daño = 70
        self.velocidad = 1
        self.alcance = 6
        self.cooldown_ataque = 4.0
        self.tiempo_habilidad = 6
        self._habilidad_disponible = True

    def habilidad_especial(self, contexto):
        """Ataque poderoso de 200 daño al objetivo más cercano (un solo uso)."""
        if not self._habilidad_disponible:
            return
        self._habilidad_disponible = False
        #* contexto puede ser lista de torres + base
        objetivos = contexto if contexto else []
        if objetivos:
            objetivo = min(
                objetivos,
                key=lambda o: abs(self.fila - o.fila) + abs(self.col - o.col)
            )
            objetivo.recibir_daño(200)


#! FÁBRICA DE ENTIDADES

TORRES_DISPONIBLES = {
    "ardiente":  TorreArdiente,
    "cañonera":  TorreCañonera,
    "arqueros":  TorreArqueros,
}

UNIDADES_DISPONIBLES = {
    "melee":  UnidadMelee,
    "ranger": UnidadRanger,
    "mago":   UnidadMago,
}

COSTOS_TORRES = {
    "ardiente": TorreArdiente(0, 0).costo,
    "cañonera": TorreCañonera(0, 0).costo,
    "arqueros": TorreArqueros(0, 0).costo,
}

COSTOS_UNIDADES = {
    "melee":  UnidadMelee(0, 0).costo,
    "ranger": UnidadRanger(0, 0).costo,
    "mago":   UnidadMago(0, 0).costo,
}


def crear_torre(subtipo, fila, col):
    cls = TORRES_DISPONIBLES.get(subtipo)
    if cls:
        return cls(fila, col)
    return None


def crear_unidad(subtipo, fila, col):
    cls = UNIDADES_DISPONIBLES.get(subtipo)
    if cls:
        return cls(fila, col)
    return None
