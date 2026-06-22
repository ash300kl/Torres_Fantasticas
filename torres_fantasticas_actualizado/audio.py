
#! AUDIO - Música de fondo (usa pygame solo para reproducir; es opcional)

import os

#* Ocultar el mensaje de bienvenida de pygame en consola
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

_DIR_AUDIO = os.path.join(os.path.dirname(__file__), "assets", "audio")

#* Se prueba primero OGG (pygame lo reproduce de forma confiable en todas las
#* plataformas) y, si no está, se cae al MP3.
_CANDIDATOS = ["batalla_de_bronce.ogg", "batalla_de_bronce.mp3"]

_mixer_listo = False
_pygame = None
_ya_avisado = False   #* para no repetir el aviso de error cada ronda


def _aviso(mensaje: str):
    global _ya_avisado
    if not _ya_avisado:
        print(f"[audio] {mensaje}")
        _ya_avisado = True


def _ruta_musica():
    """Devuelve la ruta del primer archivo de música que exista, o None."""
    for nombre in _CANDIDATOS:
        ruta = os.path.join(_DIR_AUDIO, nombre)
        if os.path.exists(ruta):
            return ruta
    return None


def _asegurar_mixer() -> bool:
    """Inicializa pygame.mixer una sola vez. Devuelve True si quedó listo."""
    global _mixer_listo, _pygame
    if _mixer_listo:
        return True
    try:
        import pygame
    except ImportError:
        _aviso("pygame no está instalado. Instalalo con:  pip install pygame")
        return False
    try:
        _pygame = pygame
        #TODO pre_init ajusta el mixer antes de arrancar; evita varios fallos comunes
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        _mixer_listo = True
    except Exception as e:
        _aviso(f"no se pudo iniciar el audio ({e}). El juego sigue sin música.")
        _mixer_listo = False
    return _mixer_listo


def reproducir_musica_ronda(volumen: float = 0.5):
    """Reproduce la música de fondo en bucle. No tumba el juego si algo falla.

    Si la música ya está sonando (p. ej. al pasar a una nueva ronda) NO se
    reinicia: se deja continuar para que no salte al principio cada ronda.
    """
    ruta = _ruta_musica()
    if ruta is None:
        _aviso("no se encontró el archivo de música en assets/audio/.")
        return
    if not _asegurar_mixer():
        return
    try:
        #TODO Si ya hay música sonando, no la reiniciamos
        if _pygame.mixer.music.get_busy():
            return
        _pygame.mixer.music.load(ruta)
        _pygame.mixer.music.set_volume(volumen)
        _pygame.mixer.music.play(-1)   #* -1 = bucle infinito
    except Exception as e:
        _aviso(f"no se pudo reproducir '{os.path.basename(ruta)}' ({e}).")


def detener_musica():
    if _mixer_listo and _pygame is not None:
        try:
            _pygame.mixer.music.stop()
        except Exception:
            pass
