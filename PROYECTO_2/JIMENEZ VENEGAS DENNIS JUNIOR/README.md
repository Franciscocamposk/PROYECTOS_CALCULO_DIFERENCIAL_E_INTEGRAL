# Proyecto 7 — Estrés térmico de los arrecifes del Golfo Dulce

![Proyecto](https://img.shields.io/badge/Proyecto%202-7-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--05-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** Dennis Junior Jimenez Venegas  
**Código:** C-05  
**Modalidad:** individual

## Pregunta de decisión

¿En qué sitio conviene invertir la restauración y en qué meses deben activarse las alertas de blanqueamiento?

## Objetivo y desarrollo

Cuantificar el estrés térmico acumulado mediante integración, comparar sitios y definir una recomendación para la restauración y las alertas.

## Modelo matemático

El estrés térmico positivo y las semanas-grado de calentamiento se modelan mediante:

$$
HS(t)=\max\{0,SST(t)-MMM\}
$$

$$
DHW(t)=\int_{t-12}^{t}HS(u)\,\mathbf{1}[HS(u)\geq 1]du
$$

La supervivencia esperada de los fragmentos trasplantados se estima como:

$$
S=S_0e^{-\kappa\,\overline{DHW}_{\max}}
$$

## Archivos

- [Informe PDF](P07_C-05_JIMENEZ.pdf)
- [Datos y cálculos](P07_C-05_JIMENEZ.xlsx)

## Cómo revisar

Leer el informe y revisar las tablas, fórmulas y resultados de la hoja de cálculo.
