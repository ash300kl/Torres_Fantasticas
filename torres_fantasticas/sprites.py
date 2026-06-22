
#! SPRITES - Carga y cache de imágenes (unidades atacantes y defensas)

import os
import tkinter as tk

#* Carpeta donde viven los PNG ya redimensionados (40x40)
_DIR_SPRITES = os.path.join(os.path.dirname(__file__), "assets", "sprites")

#* Cache de imágenes ya cargadas: (faccion, subtipo) -> PhotoImage | None
#* Importante: mantener las referencias vivas o Tkinter las descarta y la imagen
#* desaparece del canvas.
_cache: dict[tuple[str, str], "tk.PhotoImage | None"] = {}


def cargar_sprite_unidad(faccion: str, subtipo: str):
    """Devuelve el PhotoImage de la unidad (faccion+subtipo) o None si no existe.

    Debe llamarse después de crear la ventana raíz de Tkinter (PhotoImage lo exige).
    """
    clave = (faccion, subtipo)
    if clave in _cache:
        return _cache[clave]

    ruta = os.path.join(_DIR_SPRITES, f"{faccion}_{subtipo}.png")
    if not os.path.exists(ruta):
        _cache[clave] = None
        return None

    try:
        imagen = tk.PhotoImage(file=ruta)
    except Exception:
        #TODO Si el Tk del sistema no soporta PNG, devolvemos None y se usa el emoji
        imagen = None

    _cache[clave] = imagen
    return imagen


def cargar_sprite_defensa(faccion: str, clave: str):
    """Devuelve el PhotoImage de una defensa (base, muro o torre) o None.

    'clave' es la usada al dibujar: "base", "muro", "torre_ardiente",
    "torre_cañonera" o "torre_arqueros". La ñ se normaliza a 'n' para el archivo.
    """
    #TODO Nombres de archivo ASCII (cañonera -> canonera)
    clave_archivo = clave.replace("ñ", "n")
    ck = (faccion, clave_archivo)
    if ck in _cache:
        return _cache[ck]

    ruta = os.path.join(_DIR_SPRITES, f"{faccion}_{clave_archivo}.png")
    if not os.path.exists(ruta):
        _cache[ck] = None
        return None

    try:
        imagen = tk.PhotoImage(file=ruta)
    except Exception:
        imagen = None

    _cache[ck] = imagen
    return imagen
