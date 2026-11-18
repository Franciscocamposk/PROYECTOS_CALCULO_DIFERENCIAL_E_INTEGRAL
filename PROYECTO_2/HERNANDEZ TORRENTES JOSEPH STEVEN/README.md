# Proyecto 8 — Energía de las olas para una boya frente a Pavones

![Proyecto](https://img.shields.io/badge/Proyecto%202-8-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--04-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** Joseph Steven Hernandez Torrentes  
**Código:** C-04  
**Modalidad:** individual

## Pregunta de decisión

¿Qué combinación de convertidor y batería, al menor costo, mantiene la boya funcionando al menos el 99 % del tiempo?

## Objetivo y desarrollo

Estimar la energía acumulada de las olas mediante integración y comparar combinaciones de convertidor y batería para la boya.

## Modelo matemático

La varianza de la elevación del mar, la altura significativa y la potencia de las olas son:

$$
\sigma^2=\frac{1}{T}\int_0^T\eta(t)^2\,dt,
\qquad
H_s=4\sigma,
\qquad
J=\frac{\rho g^2}{64\pi}H_s^2T_e
$$

La potencia generada por el convertidor y la energía almacenada en la batería se modelan como:

$$
P_g=\min\{P_{\mathrm{nom}},\varepsilon wJ\}
$$

$$
B(t)=\min\{B_{\max},\max\{0,B_0+\int_0^t[P_g(u)-P_c]du\}\}
$$

Se elige la combinación de menor costo que mantiene la boya operativa al menos el 99\% del tiempo.

## Archivos

- [Informe PDF](P08_C-04_HERNANDEZ.pdf)
- [Datos y cálculos](P08_C-04_HERNANDEZ.xlsx)

## Cómo revisar

Leer el informe y contrastar la combinación recomendada con las tablas de la hoja de cálculo.




---

# Implementación del Proyecto 8

## Energía de las olas para una boya frente a Pavones

Este proyecto desarrolla una simulación energética utilizando
960 registros horarios de oleaje proporcionados en el archivo
P08_C-04_HERNANDEZ.xlsx.

## Objetivo

Determinar la combinación de convertidor y batería de menor
costo que suministre electricidad a una estación de 300 W
durante al menos el 99 % de las horas analizadas.

Se evalúan condiciones normales y un escenario con una
reducción del 20 % en la altura significativa del oleaje.

## Metodología

1. Lectura y validación del Excel original.
2. Interpolación de cuatro alturas faltantes sobre una copia.
3. Integración numérica mediante trapecios y Simpson 1/3.
4. Cálculo de altura significativa y flujo energético.
5. Cálculo de potencia eléctrica de los convertidores.
6. Simulación horaria del almacenamiento en baterías.
7. Comparación de 12 combinaciones y sus costos.
8. Evaluación de escenarios y auditoría energética.

## Resultado principal

La combinación de menor costo que cumple el requisito
en ambos escenarios simulados es:

- Convertidor: WEC-150.
- Batería: B20 (20 kWh).
- Costo de adquisición: ₡15,990,000.
- Disponibilidad normal: 100 %.
- Disponibilidad con oleaje reducido: 100 %.
- Horas sin cobertura: 0 en ambos escenarios.

Estos resultados dependen de los datos y supuestos del modelo.

## Supuestos y limitaciones

- Consumo constante de 300 W.
- Registros consecutivos de una hora.
- Batería inicialmente cargada al 100 %.
- Eficiencia ideal de carga y descarga.
- Sin degradación de la batería.
- Sin pérdidas adicionales no especificadas.
- El escenario reducido conserva el período del oleaje.
- Los valores atípicos no se reemplazan automáticamente.

## Ejecutar el proyecto

Desde la carpeta individual del proyecto, activar el entorno
virtual e instalar las dependencias:

    python -m venv .venv
    .venv\Scripts\activate.bat
    python -m pip install -r requirements.txt

Ejecutar las pruebas:

    python -m pytest -q

Ejecutar la aplicación web:

    python -m streamlit run app.py

## Archivos principales

- src/: cálculos matemáticos, físicos y simulaciones.
- tests/: pruebas automatizadas.
- app.py: aplicación web con Streamlit.
- notebooks/analisis_energia_oleaje.ipynb: análisis académico.
- docs/bitacora_supuestos.md: decisiones y supuestos.
- P08_C-04_HERNANDEZ.xlsx: datos originales del profesor.

El archivo Excel original se utiliza únicamente para lectura.
