
# !MAIN - Punto de entrada de Torres Fantásticas

import os
import sys

#* Asegura que el directorio del proyecto esté en el path
sys.path.insert(0, os.path.dirname(__file__))

#* Crea carpeta de datos si no existe
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

from ui import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
