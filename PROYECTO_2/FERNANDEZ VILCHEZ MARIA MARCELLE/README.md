# Proyecto 1 — Somnolencia al volante en la ruta Golfito–San José

![Proyecto](https://img.shields.io/badge/Proyecto%202-1-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--02-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** María Marcelle Fernández Vilchez  
**Código:** C-02  
**Modalidad:** individual

## Pregunta de decisión

¿Qué umbral del índice de bandas debe usar la diadema para activar la alarma?

## Objetivo y desarrollo

Analizar la somnolencia durante el recorrido mediante un modelo de integración y determinar un umbral que apoye una decisión de seguridad vial.

## Modelo matemático

La exposición acumulada a la somnolencia durante el recorrido se modela como:

$$
S(a,b)=\int_a^b s(t)\,dt
$$

La alarma se activa cuando el índice alcanza el umbral $u$:

$$
s(t)\geq u
$$

## Archivos

- [Informe PDF](P01_C-02_FERNANDEZ.pdf)
- [Datos y cálculos](P01_C-02_FERNANDEZ.xlsx)

## Cómo revisar

Leer el informe y contrastar sus resultados con las tablas y fórmulas del archivo `.xlsx`.
