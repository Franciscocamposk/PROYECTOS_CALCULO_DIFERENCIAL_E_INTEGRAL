# Proyecto 10 — Ruido de embarcaciones y ballenas jorobadas en el Golfo Dulce

- **Estudiante:** Isaac Alexander Vega Orozco
- **Código:** `C-08`
- **Curso:** MA-0321 Cálculo Diferencial e Integral (Universidad de Costa Rica, Sede del Sur)

## Estructura del Proyecto
- `datos/P10_C-08_VEGA.xlsx`: Base de datos asignada (sin modificar).
- `src/limpieza.py`: Carga, validación e imputación de faltantes y atípicos.
- `src/modelo.py`: Integración numérica (`trapecio_propio`, `simpson_propio`), fórmula analítica (`energia_paso`), calibración (`estimar_fuente`) y clase `ModeloAcusticoGolfo`.
- `src/escenarios.py`: Evaluación de medidas (`evaluar_medida`) y análisis de sensibilidad.
- `src/reporte.py`: Regenera tablas y figuras reproducibles en `resultados/`.
- `tests/test_proyecto10.py`: Pruebas automáticas con `pytest` (10 pruebas).
- `codigo_proyecto10_vega.py`: Script principal de demostración en consola.
- `app.py`: Aplicación web interactiva en Streamlit.
- `presentacion/Presentacion_P10_C-08_VEGA.pdf`: Diapositivas ejecutivas (10 láminas).

## Cómo ejecutar
```bash
pip install -r requirements.txt
pytest -v
python codigo_proyecto10_vega.py
python -m src.reporte
streamlit run app.py
```
