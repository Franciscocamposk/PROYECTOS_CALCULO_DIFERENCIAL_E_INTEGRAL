
"""Punto de entrada de Streamlit Cloud para el Proyecto 8."""

from pathlib import Path
import runpy
import sys

# Raíz del repositorio GitHub.
RAIZ = Path(__file__).resolve().parent.parent

# Carpeta individual donde está la aplicación original.
PROYECTO = (
    RAIZ
    / "PROYECTO_2"
    / "HERNANDEZ TORRENTES JOSEPH STEVEN"
)

# Permitir que la aplicación importe sus módulos src.
sys.path.insert(0, str(PROYECTO))

# Ejecutar la aplicación original.
runpy.run_path(
    str(PROYECTO / "app.py"),
    run_name="__main__",
)
