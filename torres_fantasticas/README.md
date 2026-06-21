# Torres Fantásticas

Juego de estrategia por turnos para dos jugadores. Un jugador defiende una base construyendo torres y muros; el otro ataca con unidades para destruirla.

## Requisitos

- Python 3.10 o superior
- Tkinter (incluido en Python estándar)
- No requiere librerías externas para funcionar

## Ejecución

```bash
python main.py
```

## Flujo del juego

1. Ambos jugadores inician sesión o se registran.
2. Cada jugador elige una facción diferente (Robótica, Medieval, Submarina, Fantástica).
3. **Fase de construcción:** el Jugador(defensor) coloca torres y muros en el lado izquierdo del mapa.
4. **Fase de compra:** el Jugador(atacante) compra unidades que aparecen en el lado derecho.
5. **Combate:** las unidades avanzan automáticamente hacia la base. Las torres las atacan.
6. **Fin de ronda:** gana quien cumpla su condición de victoria.
7. El primero en ganar **3 rondas** gana la partida.

## Torres disponibles

|  Torre  | Costo | Vida | Daño | Alcance | Habilidad                      |
|---------|-------|------|------|---------|--------------------------------|
| Ardiente| 700   | 190  | 20   | 4       | Llamarada a 3 unidades cercanas|
| Cañonera| 550   | 200  | 80   | 6       | Elimina la unidad más cercana  |
| Arqueros| 50    | 100  | 10   | 10      | Cura 20 vida a todas las torres|
| Muro    | 50    | 300  | —    | —       | Bloquea el paso                |

## Unidades disponibles

| Unidad | Costo | Vida | Daño | Alcance | Habilidad               |
|--------|-------|------|------|---------|-------------------------|
| Melee  | 20    | 150  | 50   | 1       | Escudo +20 vida         |
| Ranger | 100   | 220  | 20   | 5       | Daño doble por 2 turnos |
| Mago   | 500   | 180  | 70   | 6       | Ataque único de 100 daño|

## Facciones

- **Robótica:** torres y muros tecnológicos, unidades mecánicas.
- **Medieval:** castillos de piedra, soldados, magos y arqueros.
- **Submarina:** corales y conchas, unidades marinas.
- **Fantástica:** Ents, troncos y gran árbol, elfos y enanos.

## Estructura del proyecto

```
torres_fantasticas/
├── main.py         # Punto de entrada
├── ui.py           # Interfaz gráfica (Tkinter)
├── game.py         # Lógica del juego, rondas y combate
├── entities.py     # Clases de torres, unidades, muro y base
├── map_grid.py     # Cuadrícula del mapa
├── player.py       # Sistema de jugadores y persistencia
├── factions.py     # Datos de las facciones
├── data/
│   └── players.json   # Base de datos de jugadores (se crea automáticamente)
└── README.md
```
