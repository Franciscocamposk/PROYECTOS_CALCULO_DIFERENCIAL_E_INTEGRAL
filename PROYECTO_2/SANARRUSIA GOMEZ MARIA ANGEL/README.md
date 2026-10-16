# Proyecto 4 — Gases del volcán Poás y cierre preventivo del mirador

![Proyecto](https://img.shields.io/badge/Proyecto%202-4-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--07-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** María Angel Sanarrusia Gomez  
**Código:** C-07  
**Modalidad:** individual

## Pregunta de decisión

¿Qué regla de cierre preventivo reduce más la exposición de los visitantes sin cerrar innecesariamente, y está aumentando la desgasificación del volcán?

## Objetivo y desarrollo

Analizar la exposición acumulada a los gases mediante integración, comparar reglas de cierre y sustentar una medida preventiva.

## Modelo matemático

La exposición acumulada a los gases se modela mediante:

$$
X(a,b)=\int_a^b c(t)\,dt
$$

La regla de cierre seleccionada minimiza la exposición respetando las restricciones operativas:

$$
x^*=\operatorname*{arg\,min}_{x\in\mathcal{D}}X(x)
$$

## Archivos

- [Informe PDF](P04_C-07_SANARRUSIA.pdf)
- [Datos y cálculos](P04_C-07_SANARRUSIA.xlsx)

## Cómo revisar

Leer el informe y revisar los cálculos que fundamentan la regla recomendada.
