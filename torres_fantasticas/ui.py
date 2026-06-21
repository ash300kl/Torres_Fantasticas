
#! UI - Interfaz gráfica completa en Tkinter

import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading
import random

from player import registrar_jugador, iniciar_sesion, obtener_ranking, Jugador
from factions import FACCIONES, LISTA_FACCIONES, obtener_faccion, get_color, get_etiqueta
from game import MotorJuego
from map_grid import FILAS, COLS, BASE_FILA, BASE_COL
from entities import (
    COSTOS_TORRES, COSTOS_UNIDADES, Muro,
    TorreArdiente, TorreCañonera, TorreArqueros,
    UnidadMelee, UnidadRanger, UnidadMago,
)

#! PALETA GLOBAL

COLOR_BG      = "#0d1117"
COLOR_PANEL   = "#161b22"
COLOR_BORDE   = "#30363d"
COLOR_TEXTO   = "#e6edf3"
COLOR_SUBTXT  = "#8b949e"
COLOR_ACENTO  = "#58a6ff"
COLOR_OK      = "#3fb950"
COLOR_PELIGRO = "#f85149"
COLOR_ORO     = "#d29922"

FONT_TITULO = ("Helvetica", 18, "bold")
FONT_SUB    = ("Helvetica", 12, "bold")
FONT_NORMAL = ("Helvetica", 10)
FONT_MONO   = ("Courier", 9)

CELL_SIZE = 46


#! VENTANA PRINCIPAL - CONTENEDOR

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Torres Fantásticas")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)

        #* Estado compartido entre ventanas
        self.jugadores_logueados: list[str] = []   #TODO [nombre_j1, nombre_j2]
        self.facciones_elegidas: list[str] = []    #TODO [faccion_j1, faccion_j2]
        self.roles_asignados: list[str] = []       #TODO ["defensor","atacante"] o al revés
        self.motor: MotorJuego | None = None

        self._frame_actual = None
        self.mostrar_frame(VentanaLogin)

    def mostrar_frame(self, cls, **kwargs):
        if self._frame_actual:
            self._frame_actual.destroy()
        frame = cls(self, **kwargs)
        frame.pack(fill="both", expand=True)
        self._frame_actual = frame
        #TODO Ajustar tamaño según el frame
        self.update_idletasks()


#! HELPERS DE ESTILO

def _btn(parent, texto, comando, color=COLOR_ACENTO, ancho=20):
    return tk.Button(
        parent, text=texto, command=comando,
        bg=color, fg=COLOR_BG, activebackground=color,
        font=FONT_SUB, width=ancho, relief="flat", cursor="hand2",
        padx=8, pady=6,
    )


def _lbl(parent, texto, fuente=FONT_NORMAL, color=COLOR_TEXTO, **kw):
    return tk.Label(parent, text=texto, font=fuente, bg=COLOR_PANEL,
                    fg=color, **kw)


def _entry(parent, show=None):
    e = tk.Entry(parent, bg="#21262d", fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO,
                 font=FONT_NORMAL, relief="flat", bd=4, width=24)
    if show:
        e.config(show=show)
    return e


#! VENTANA DE LOGIN / REGISTRO

class VentanaLogin(tk.Frame):
    """Permite que dos jugadores inicien sesión o se registren."""

    def __init__(self, master: App):
        super().__init__(master, bg=COLOR_BG)
        self.master: App = master
        self._sesiones: list[str] = []   #TODO jugadores ya logueados en esta sesión

        self._construir()

    def _construir(self):
        tk.Label(self, text="⚔  Torres Fantásticas  ⚔", font=("Helvetica", 22, "bold"),
                 bg=COLOR_BG, fg=COLOR_ACENTO).pack(pady=(30, 5))
        tk.Label(self, text="Juego de estrategia para dos jugadores",
                 font=FONT_NORMAL, bg=COLOR_BG, fg=COLOR_SUBTXT).pack(pady=(0, 20))

        jugador_num = len(self._sesiones) + 1
        tk.Label(self, text=f"Jugador {jugador_num} — Iniciar sesión o Registrarse",
                 font=FONT_SUB, bg=COLOR_BG, fg=COLOR_TEXTO).pack(pady=(0, 10))

        panel = tk.Frame(self, bg=COLOR_PANEL, bd=1, relief="flat", padx=30, pady=25)
        panel.pack(padx=60, pady=10, ipadx=10, ipady=5)

        _lbl(panel, "Nombre de usuario:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_nombre = _entry(panel)
        self.entry_nombre.grid(row=0, column=1, pady=5, padx=(10, 0))

        _lbl(panel, "Contraseña:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_pass = _entry(panel, show="●")
        self.entry_pass.grid(row=1, column=1, pady=5, padx=(10, 0))

        self.lbl_msg = tk.Label(panel, text="", font=FONT_NORMAL,
                                bg=COLOR_PANEL, fg=COLOR_PELIGRO)
        self.lbl_msg.grid(row=2, column=0, columnspan=2, pady=8)

        botones = tk.Frame(panel, bg=COLOR_PANEL)
        botones.grid(row=3, column=0, columnspan=2)
        _btn(botones, "Iniciar sesión", self._login, COLOR_ACENTO, 14).pack(side="left", padx=5)
        _btn(botones, "Registrarse",    self._registrar, COLOR_OK, 14).pack(side="left", padx=5)

        #TODO Botón de ranking
        tk.Button(self, text="🏆 Ver rankings", command=self._ver_ranking,
                  bg=COLOR_PANEL, fg=COLOR_ORO, font=FONT_NORMAL,
                  relief="flat", cursor="hand2").pack(pady=10)

        #TODO Mostrar jugadores ya logueados
        if self._sesiones:
            tk.Label(self, text=f"✓ {self._sesiones[0]} listo",
                     font=FONT_NORMAL, bg=COLOR_BG, fg=COLOR_OK).pack()

    def _login(self):
        nombre = self.entry_nombre.get().strip()
        pwd    = self.entry_pass.get().strip()
        if nombre in self._sesiones:
            self.lbl_msg.config(text="Este jugador ya inició sesión.")
            return
        ok, msg = iniciar_sesion(nombre, pwd)
        if ok:
            self._sesiones.append(nombre)
            self._siguiente_o_continuar()
        else:
            self.lbl_msg.config(text=msg)

    def _registrar(self):
        nombre = self.entry_nombre.get().strip()
        pwd    = self.entry_pass.get().strip()
        ok, msg = registrar_jugador(nombre, pwd)
        if ok:
            self.lbl_msg.config(text=msg, fg=COLOR_OK)
        else:
            self.lbl_msg.config(text=msg, fg=COLOR_PELIGRO)

    def _siguiente_o_continuar(self):
        if len(self._sesiones) < 2:
            #TODO Refrescar para el segundo jugador
            self.master.jugadores_logueados = list(self._sesiones)
            nueva = VentanaLogin(self.master)
            nueva._sesiones = list(self._sesiones)
            self.master.mostrar_frame(lambda m: nueva)
            self.destroy()
            nueva.pack(fill="both", expand=True)
            self.master._frame_actual = nueva
        else:
            self.master.jugadores_logueados = list(self._sesiones)
            self.master.mostrar_frame(VentanaSeleccionFaccion)

    def _ver_ranking(self):
        VentanaRanking(self.master)


#! VENTANA SELECCIÓN DE FACCIÓN

class VentanaSeleccionFaccion(tk.Frame):
    def __init__(self, master: App):
        super().__init__(master, bg=COLOR_BG)
        self.master: App = master
        self.elecciones: list[str | None] = [None, None]
        self._construir()

    def _construir(self):
        tk.Label(self, text="Selección de Facción", font=FONT_TITULO,
                 bg=COLOR_BG, fg=COLOR_ACENTO).pack(pady=(20, 5))
        tk.Label(self, text="Cada jugador debe elegir una facción distinta.",
                 font=FONT_NORMAL, bg=COLOR_BG, fg=COLOR_SUBTXT).pack(pady=(0, 15))

        contenedor = tk.Frame(self, bg=COLOR_BG)
        contenedor.pack(padx=30)

        for idx in range(2):
            nombre = self.master.jugadores_logueados[idx]
            col_frame = tk.Frame(contenedor, bg=COLOR_PANEL, bd=1, relief="flat",
                                 padx=15, pady=15)
            col_frame.grid(row=0, column=idx, padx=20, pady=10, sticky="n")

            tk.Label(col_frame, text=f"Jugador {idx+1}: {nombre}",
                     font=FONT_SUB, bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(0, 10))

            var = tk.StringVar(value="")
            for clave in LISTA_FACCIONES:
                fac = FACCIONES[clave]
                rb = tk.Radiobutton(
                    col_frame,
                    text=f"{fac['nombre']} — {fac['descripcion']}",
                    variable=var, value=clave,
                    bg=COLOR_PANEL, fg=COLOR_TEXTO,
                    selectcolor="#1f2937",
                    activebackground=COLOR_PANEL,
                    font=FONT_NORMAL,
                    command=lambda i=idx, v=var: self._elegir(i, v.get()),
                )
                rb.pack(anchor="w", pady=3)

            #TODO Guardar referencia al var
            setattr(self, f"_var_{idx}", var)

        self.lbl_msg = tk.Label(self, text="", font=FONT_NORMAL,
                                bg=COLOR_BG, fg=COLOR_PELIGRO)
        self.lbl_msg.pack(pady=8)

        _btn(self, "Comenzar partida ▶", self._iniciar, COLOR_OK, 22).pack(pady=10)

    def _elegir(self, idx: int, clave: str):
        self.elecciones[idx] = clave

    def _iniciar(self):
        f1, f2 = self.elecciones
        if not f1 or not f2:
            self.lbl_msg.config(text="Ambos jugadores deben elegir una facción.")
            return
        if f1 == f2:
            self.lbl_msg.config(text="Los jugadores no pueden usar la misma facción.")
            return
        self.master.facciones_elegidas = [f1, f2]

        #TODO Asignación aleatoria de roles
        roles = ["defensor", "atacante"]
        random.shuffle(roles)
        self.master.roles_asignados = roles

        nombres = self.master.jugadores_logueados
        rol_j1, rol_j2 = roles[0], roles[1]
        icono = {"defensor": "🛡", "atacante": "⚔"}
        messagebox.showinfo(
            "Roles asignados aleatoriamente",
            f"🎲 ¡Los roles han sido sorteados!\n\n"
            f"  {icono[rol_j1]} {nombres[0]}  →  {rol_j1.upper()}\n"
            f"  {icono[rol_j2]} {nombres[1]}  →  {rol_j2.upper()}"
        )
        self.master.mostrar_frame(VentanaJuego)


#! VENTANA PRINCIPAL DEL JUEGO

class VentanaJuego(tk.Frame):
    TICK_MS = 500   #TODO milisegundos por tick de combate (ajustable para velocidad)

    def __init__(self, master: App):
        super().__init__(master, bg=COLOR_BG)
        self.master: App = master

        nombres   = master.jugadores_logueados
        facciones = master.facciones_elegidas
        roles     = master.roles_asignados  #TODO ["defensor","atacante"] o al revés

        #TODO Crear jugadores según el rol sorteado
        j0 = Jugador(nombres[0], roles[0], facciones[0])
        j1 = Jugador(nombres[1], roles[1], facciones[1])

        #TODO Identificar quién es defensor y quién es atacante
        if roles[0] == "defensor":
            defensor, atacante    = j0, j1
            self.faccion_def      = facciones[0]
            self.faccion_atk      = facciones[1]
        else:
            defensor, atacante    = j1, j0
            self.faccion_def      = facciones[1]
            self.faccion_atk      = facciones[0]

        self.motor = MotorJuego(defensor, atacante)
        master.motor = self.motor

        self._seleccion_tipo: str | None = None   #TODO tipo seleccionado del panel
        self._combate_activo = False

        self._construir()
        self._iniciar_ronda()

    #! CONSTRUCCIÓN DE LA UI

    def _construir(self):
        #TODO Barra superior de estado
        self.barra = tk.Frame(self, bg=COLOR_PANEL, pady=8)
        self.barra.pack(fill="x", padx=0)

        self.lbl_ronda   = tk.Label(self.barra, text="Ronda 1", font=FONT_SUB,
                                     bg=COLOR_PANEL, fg=COLOR_ACENTO)
        self.lbl_ronda.pack(side="left", padx=20)

        self.lbl_marcador = tk.Label(self.barra, text="", font=FONT_SUB,
                                      bg=COLOR_PANEL, fg=COLOR_TEXTO)
        self.lbl_marcador.pack(side="left", padx=20)

        self.lbl_fase = tk.Label(self.barra, text="", font=FONT_NORMAL,
                                  bg=COLOR_PANEL, fg=COLOR_ORO)
        self.lbl_fase.pack(side="left", padx=20)

        self.lbl_base = tk.Label(self.barra, text="", font=FONT_NORMAL,
                                  bg=COLOR_PANEL, fg=COLOR_PELIGRO)
        self.lbl_base.pack(side="right", padx=20)

        #TODO Cuerpo central: panel izquierdo + mapa + panel derecho
        cuerpo = tk.Frame(self, bg=COLOR_BG)
        cuerpo.pack(fill="both", expand=True, padx=10, pady=8)

        self.panel_izq = tk.Frame(cuerpo, bg=COLOR_PANEL, width=200, padx=10, pady=10)
        self.panel_izq.pack(side="left", fill="y", padx=(0, 8))
        self.panel_izq.pack_propagate(False)

        #TODO Canvas del mapa
        ancho_canvas = COLS * CELL_SIZE
        alto_canvas  = FILAS * CELL_SIZE
        self.canvas = tk.Canvas(cuerpo, width=ancho_canvas, height=alto_canvas,
                                 bg=COLOR_BG, highlightthickness=1,
                                 highlightbackground=COLOR_BORDE)
        self.canvas.pack(side="left")
        self.canvas.bind("<Button-1>", self._click_mapa)

        self.panel_der = tk.Frame(cuerpo, bg=COLOR_PANEL, width=240, padx=10, pady=10)
        self.panel_der.pack(side="left", fill="y", padx=(8, 0))
        self.panel_der.pack_propagate(False)

        #TODO Log de combate
        self.log_frame = tk.Frame(self, bg=COLOR_PANEL, height=140, padx=10, pady=6)
        self.log_frame.pack(fill="x", padx=10, pady=(0, 8))
        self.log_frame.pack_propagate(False)

        tk.Label(self.log_frame, text="Log de combate", font=FONT_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_SUBTXT).pack(anchor="w")
        self.log_text = tk.Text(self.log_frame, height=6, bg="#0d1117", fg=COLOR_TEXTO,
                                 font=FONT_MONO, state="disabled", relief="flat",
                                 wrap="word")
        self.log_text.pack(fill="both", expand=True)
        sb = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=sb.set)

    #! PANELES LATERALES

    def _rebuild_panel_izq(self):
        for w in self.panel_izq.winfo_children():
            w.destroy()
        fase = self.motor.fase
        defensor = self.motor.defensor

        tk.Label(self.panel_izq, text=f"🛡 {defensor.nombre}",
                 font=FONT_SUB, bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(0, 4))
        tk.Label(self.panel_izq, text=f"💰 {defensor.dinero} monedas",
                 font=FONT_NORMAL, bg=COLOR_PANEL, fg=COLOR_ORO).pack(pady=2)
        tk.Label(self.panel_izq, text=f"⭐ Rondas: {defensor.rondas_ganadas}/3",
                 font=FONT_NORMAL, bg=COLOR_PANEL, fg=COLOR_ACENTO).pack(pady=2)

        if fase == "construccion":
            tk.Label(self.panel_izq, text="── Construir ──",
                     font=FONT_NORMAL, bg=COLOR_PANEL, fg=COLOR_SUBTXT).pack(pady=(10, 4))

            opciones = [
                ("ardiente",  f"🔥 Ardiente [{COSTOS_TORRES['ardiente']}]"),
                ("cañonera",  f"💣 Cañonera  [{COSTOS_TORRES['cañonera']}]"),
                ("arqueros",  f"🏹 Arqueros  [{COSTOS_TORRES['arqueros']}]"),
                ("muro",      f"🧱 Muro       [{Muro.COSTO}]"),
            ]
            self._var_tipo_def = tk.StringVar(value="")
            for val, texto in opciones:
                rb = tk.Radiobutton(
                    self.panel_izq, text=texto,
                    variable=self._var_tipo_def, value=val,
                    bg=COLOR_PANEL, fg=COLOR_TEXTO,
                    selectcolor="#1f2937",
                    activebackground=COLOR_PANEL,
                    font=FONT_NORMAL,
                    command=lambda v=val: self._seleccionar_tipo(v),
                )
                rb.pack(anchor="w", pady=2)

            tk.Label(self.panel_izq, text="Haz clic en el mapa\npara colocar.",
                     font=FONT_NORMAL, bg=COLOR_PANEL, fg=COLOR_SUBTXT,
                     justify="left").pack(pady=8)

            _btn(self.panel_izq, "Terminar construcción",
                 self._terminar_construccion, COLOR_ORO, 18).pack(pady=6)

    def _rebuild_panel_der(self):
        for w in self.panel_der.winfo_children():
            w.destroy()
        fase = self.motor.fase
        atacante = self.motor.atacante

        tk.Label(self.panel_der, text=f"⚔ {atacante.nombre}",
                 font=FONT_SUB, bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(0, 4))
        tk.Label(self.panel_der, text=f"💰 {atacante.dinero} monedas",
                 font=FONT_NORMAL, bg=COLOR_PANEL, fg=COLOR_ORO).pack(pady=2)
        tk.Label(self.panel_der, text=f"⭐ Rondas: {atacante.rondas_ganadas}/3",
                 font=FONT_NORMAL, bg=COLOR_PANEL, fg=COLOR_ACENTO).pack(pady=2)

        if fase == "ataque":
            tk.Label(self.panel_der, text="── Desplegar unidades ──",
                     font=FONT_NORMAL, bg=COLOR_PANEL, fg=COLOR_SUBTXT).pack(pady=(10, 4))

            opciones = [
                ("melee",  f"⚔ Melee  [{COSTOS_UNIDADES['melee']}]"),
                ("ranger", f"🏹 Ranger [{COSTOS_UNIDADES['ranger']}]"),
                ("mago",   f"🪄 Mago   [{COSTOS_UNIDADES['mago']}]"),
            ]
            self._var_tipo_atk = tk.StringVar(value="")
            for val, texto in opciones:
                rb = tk.Radiobutton(
                    self.panel_der, text=texto,
                    variable=self._var_tipo_atk, value=val,
                    bg=COLOR_PANEL, fg=COLOR_TEXTO,
                    selectcolor="#1f2937",
                    activebackground=COLOR_PANEL,
                    font=FONT_NORMAL,
                    command=lambda v=val: self._seleccionar_tipo(v),
                )
                rb.pack(anchor="w", pady=2)

            tk.Label(self.panel_der,
                     text="Haz clic en el mapa\n(zona derecha) para\ndesplegar.",
                     font=FONT_NORMAL, bg=COLOR_PANEL, fg=COLOR_SUBTXT,
                     justify="left").pack(pady=8)

            _btn(self.panel_der, "¡Iniciar combate! ⚔",
                 self._iniciar_combate, COLOR_PELIGRO, 18).pack(pady=6)

    #! MAPA / CANVAS

    def _dibujar_mapa(self):
        self.canvas.delete("all")
        mapa = self.motor.mapa

        #TODO Colores base del mapa según facción defensora
        color_libre  = get_color(self.faccion_def, "celda_libre")
        color_borde  = get_color(self.faccion_def, "celda_borde")

        for f in range(FILAS):
            for c in range(COLS):
                x0 = c * CELL_SIZE
                y0 = f * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE

                obj = mapa.grid[f][c]

                #TODO Color de fondo de la celda
                if c >= COLS // 2:
                    bg = "#1a0a0a"   #TODO zona atacante (rojo oscuro)
                else:
                    bg = color_libre

                self.canvas.create_rectangle(x0, y0, x1, y1,
                                              fill=bg, outline=color_borde, width=1)

                if obj is None:
                    continue

                tipo = getattr(obj, "tipo", "")

                if tipo == "base":
                    color = get_color(self.faccion_def, "base")
                    label = get_etiqueta(self.faccion_def, "base_label")
                    self._celda(x0, y0, color, label,
                                subtexto=f"♥{obj.vida}")

                elif tipo == "muro":
                    color = get_color(self.faccion_def, "muro")
                    label = get_etiqueta(self.faccion_def, "muro_label")
                    self._celda(x0, y0, color, label,
                                subtexto=f"♥{obj.vida}")

                elif tipo == "torre":
                    clave = f"torre_{obj.subtipo}"
                    color = get_color(self.faccion_def, clave)
                    label = get_etiqueta(self.faccion_def, f"{clave}_label")
                    self._celda(x0, y0, color, label,
                                subtexto=f"♥{obj.vida}")

                elif tipo == "unidad":
                    clave = f"unidad_{obj.subtipo}"
                    color = get_color(self.faccion_atk, clave)
                    label = get_etiqueta(self.faccion_atk, f"{clave}_label")
                    self._celda(x0, y0, color, label,
                                subtexto=f"♥{obj.vida}")

        #TODO Línea divisoria entre zonas
        mid_x = (COLS // 2) * CELL_SIZE
        self.canvas.create_line(mid_x, 0, mid_x, FILAS * CELL_SIZE,
                                 fill="#ff4444", width=2, dash=(4, 4))

    def _celda(self, x0, y0, color, emoji, subtexto="", opacidad=1.0):
        x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
        self.canvas.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2,
                                      fill=color, outline="", width=0)
        self.canvas.create_text(x0 + CELL_SIZE // 2, y0 + CELL_SIZE // 2 - 5,
                                 text=emoji, font=("Helvetica", 14), fill="white")
        if subtexto:
            self.canvas.create_text(x0 + CELL_SIZE // 2, y1 - 8,
                                     text=subtexto, font=("Helvetica", 7), fill="white")

    def _click_mapa(self, event):
        col = event.x // CELL_SIZE
        fila = event.y // CELL_SIZE
        fase = self.motor.fase
        tipo = self._seleccion_tipo

        if fase == "construccion" and tipo:
            if tipo == "muro":
                ok, msg = self.motor.defensor_colocar_muro(fila, col)
            else:
                ok, msg = self.motor.defensor_colocar_torre(tipo, fila, col)
            self._log_ui(msg)
            self._actualizar_ui()

        elif fase == "ataque" and tipo:
            ok, msg = self.motor.atacante_comprar_unidad(tipo, fila)
            self._log_ui(msg)
            self._actualizar_ui()

    def _seleccionar_tipo(self, val: str):
        self._seleccion_tipo = val

    #! FLUJO DE RONDAS

    def _iniciar_ronda(self):
        self.motor.iniciar_fase_construccion()
        self._seleccion_tipo = None
        self._actualizar_ui()
        self._log_ui(f"── Ronda {self.motor.numero_ronda} iniciada ──")

    def _terminar_construccion(self):
        self.motor.terminar_fase_construccion()
        self._seleccion_tipo = None
        self._actualizar_ui()
        self._log_ui("Fase de construcción terminada. Turno del atacante.")

    def _iniciar_combate(self):
        ok, msg = self.motor.terminar_fase_ataque()
        if not ok:
            self._log_ui(f"⚠ {msg}")
            return
        self._combate_activo = True
        self._actualizar_ui()
        self._tick_combate()

    def _tick_combate(self):
        if not self._combate_activo:
            return

        resultado = self.motor.tick_combate(dt=1.0)
        for ev in resultado.get("eventos", []):
            self._log_ui(ev)
        self._actualizar_ui()

        if resultado["fin"]:
            self._combate_activo = False
            self._procesar_fin_oleada(resultado["resultado"])
        else:
            self.after(self.TICK_MS, self._tick_combate)

    def _procesar_fin_oleada(self, resultado_oleada: str):
        """Maneja el resultado de una oleada (puede ser nueva oleada o fin de ronda)."""
        info = self.motor.resolver_fin_oleada(resultado_oleada)
        self._actualizar_ui()

        if info["tipo"] == "nueva_oleada":
            oleada = self.motor.turno_oleada
            max_o  = self.motor.TURNOS_POR_OLEADA
            messagebox.showinfo(
                f"Oleada {oleada}/{max_o} superada",
                f"🛡 El defensor sobrevivió la oleada {oleada}.\n"
                f"El atacante puede comprar más unidades.\n\n"
                f"Faltan {max_o - oleada} oleada(s) para que gane el defensor."
            )
            self._seleccion_tipo = None
            #TODO Volver a la fase de compra del atacante (sin reconstruir torres)
            self._rebuild_panel_izq()
            self._rebuild_panel_der()
        else:
            self._fin_ronda(info["ganador_ronda"])

    def _fin_ronda(self, ganador_rol: str):
        self.motor.resolver_fin_ronda(ganador_rol)
        self._actualizar_ui()

        if self.motor.fase == "fin_partida":
            self._mostrar_fin_partida()
        else:
            ganador_nombre = (self.motor.defensor.nombre
                              if ganador_rol == "defensor"
                              else self.motor.atacante.nombre)
            messagebox.showinfo(
                "Fin de ronda",
                f"{'🛡' if ganador_rol == 'defensor' else '⚔'} ¡{ganador_nombre} gana la ronda!\n"
                f"Marcador: {self.motor.defensor.nombre} {self.motor.defensor.rondas_ganadas} "
                f"— {self.motor.atacante.rondas_ganadas} {self.motor.atacante.nombre}"
            )
            self._iniciar_ronda()

    def _mostrar_fin_partida(self):
        ganador = self.motor.ganador_partida
        messagebox.showinfo(
            "¡Fin de la partida!",
            f"🏆 ¡{ganador} gana la partida!\n\n"
            f"Marcador final:\n"
            f"  {self.motor.defensor.nombre} (defensor): {self.motor.defensor.rondas_ganadas}\n"
            f"  {self.motor.atacante.nombre} (atacante): {self.motor.atacante.rondas_ganadas}"
        )
        self.master.mostrar_frame(VentanaLogin)

    #! ACTUALIZACIÓN DE UI

    def _actualizar_ui(self):
        estado = self.motor.estado_resumen()
        oleada_txt = (f"  •  Oleada {estado['turno_oleada'] + 1}/{estado['turnos_max']}"
                      if estado["fase"] in ("combate", "ataque") else "")
        self.lbl_ronda.config(text=f"Ronda {estado['ronda']}{oleada_txt}")
        self.lbl_marcador.config(
            text=f"{estado['defensor']['nombre']} {estado['defensor']['rondas']} "
                 f"— {estado['atacante']['rondas']} {estado['atacante']['nombre']}"
        )
        fase_textos = {
            "construccion": "🛡 Fase de construcción",
            "ataque":       "⚔ Fase de compra",
            "combate":      "💥 ¡COMBATE!",
            "fin_ronda":    "Fin de ronda",
            "fin_partida":  "Fin de partida",
        }
        self.lbl_fase.config(text=fase_textos.get(estado["fase"], ""))
        self.lbl_base.config(
            text=f"Base: ♥{estado['base_vida']}/500  "
                 f"Torres: {estado['torres_activas']}  "
                 f"Unidades: {estado['unidades_vivas']}"
        )
        self._dibujar_mapa()
        self._rebuild_panel_izq()
        self._rebuild_panel_der()

    def _log_ui(self, msg: str):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")


#! VENTANA DE RANKINGS

class VentanaRanking(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("🏆 Rankings")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        self._construir()

    def _construir(self):
        tk.Label(self, text="🏆 Rankings de jugadores", font=FONT_TITULO,
                 bg=COLOR_BG, fg=COLOR_ORO).pack(pady=(20, 15))

        contenedor = tk.Frame(self, bg=COLOR_BG)
        contenedor.pack(padx=30, pady=10)

        for rol, titulo, idx in [("defensor", "Top Defensores 🛡", 0),
                                  ("atacante",  "Top Atacantes  ⚔", 1)]:
            panel = tk.Frame(contenedor, bg=COLOR_PANEL, padx=20, pady=15)
            panel.grid(row=0, column=idx, padx=15, sticky="n")

            tk.Label(panel, text=titulo, font=FONT_SUB,
                     bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(0, 10))

            ranking = obtener_ranking(rol, top=5)
            if not ranking:
                tk.Label(panel, text="Sin datos aún.", font=FONT_NORMAL,
                         bg=COLOR_PANEL, fg=COLOR_SUBTXT).pack()
            else:
                for i, entry in enumerate(ranking, 1):
                    color = COLOR_ORO if i == 1 else COLOR_TEXTO
                    tk.Label(panel,
                             text=f"{i}. {entry['nombre']}  —  {entry['victorias']} victorias",
                             font=FONT_NORMAL, bg=COLOR_PANEL, fg=color).pack(anchor="w", pady=2)

        _btn(self, "Cerrar", self.destroy, COLOR_PANEL, 12).pack(pady=15)
