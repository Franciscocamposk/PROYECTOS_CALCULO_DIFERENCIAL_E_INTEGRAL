# Proyecto 2 — Cafeína, atención y sueño en semana de exámenes

![Proyecto](https://img.shields.io/badge/Proyecto%202-2-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--09-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** Kendall Fabricio Villalobos Villalta  
**Código:** C-09  
**Modalidad:** individual

## Pregunta de decisión

¿Cuántas tomas, de qué bebida y hasta qué hora conviene consumir cafeína para tener más horas de atención sin afectar el sueño?

## Objetivo y desarrollo

Modelar los efectos de la cafeína mediante integración, comparar bebidas y horarios, y recomendar una estrategia compatible con la atención y el descanso.

## Modelo matemático

Las horas acumuladas de atención durante el periodo de estudio se representan por:

$$
A(a,b)=\int_a^b a(t)\,dt
$$

La estrategia recomendada maximiza la atención respetando la restricción sobre el sueño:

$$
x^*=\mathrm{arg\,max}_{x\in\mathcal{D}}A(x),
\qquad
S(x)\geq S_{\min}
$$

## Archivos

- [Informe PDF](P02_C-09_VILLALOBOS.pdf)
- [Datos y cálculos](P02_C-09_VILLALOBOS.xlsx)

## Cómo revisar

Leer el informe y comparar la estrategia recomendada con las tablas y fórmulas del archivo `.xlsx`.
