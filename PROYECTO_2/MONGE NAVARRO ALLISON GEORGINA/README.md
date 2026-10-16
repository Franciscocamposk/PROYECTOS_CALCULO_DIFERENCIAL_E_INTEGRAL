# Proyecto 6 — Migración de aves rapaces sobre Këköldi, Talamanca

![Proyecto](https://img.shields.io/badge/Proyecto%202-6-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--06-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** Allison Georgina Monge Navarro  
**Código:** C-06  
**Modalidad:** individual

## Pregunta de decisión

¿Qué fechas y qué horario debe tener la campaña de voluntariado para registrar la mayor cantidad de aves migratorias?

## Objetivo y desarrollo

Modelar la migración mediante integración, analizar los periodos de mayor actividad y recomendar fechas y horarios de monitoreo.

## Modelo matemático

La cantidad esperada de aves observadas durante un intervalo se representa por:

$$
N(a,b)=\int_a^b n(t)\,dt
$$

El periodo recomendado maximiza el número esperado de registros:

$$
(a^*,b^*)=\mathrm{arg\,max}_{(a,b)\in\mathcal{D}}N(a,b)
$$

## Archivos

- [Informe PDF](P06_C-06_MONGE.pdf)
- [Datos y cálculos](P06_C-06_MONGE.xlsx)

## Cómo revisar

Leer el informe y contrastar la recomendación con las tablas y fórmulas del archivo `.xlsx`.
