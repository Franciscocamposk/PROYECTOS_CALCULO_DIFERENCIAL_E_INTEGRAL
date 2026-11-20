from pathlib import Path
import runpy
import sys
RAIZ = Path(__file__).resolve().parent.parent
PROYECTO = RAIZ / "PROYECTO_2" / "HERNANDEZ TORRENTES JOSEPH STEVEN"
sys.path.insert(0, str(PROYECTO))
runpy.run_path(str(PROYECTO / "app.py"), run_name="__main__")
