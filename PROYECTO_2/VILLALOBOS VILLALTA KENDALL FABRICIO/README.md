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

La concentración de cafeína después de una toma se modela mediante absorción y eliminación:

$$
C(t)=\frac{Dk_a}{V(k_a-k)}(e^{-kt}-e^{-k_at})
$$

El área bajo la curva y la concentración de un plan con varias tomas son:

$$
AUC=\int_0^{\infty}C(t)\,dt=\frac{D}{Vk},
\qquad
C_{\mathrm{plan}}(t)=\sum_j C(t-t_j;D_j)
$$

Las horas con efecto durante la jornada se calculan como:

$$
H_{\mathrm{ef}}=\int_8^{20}\mathbf{1}[C_{\mathrm{plan}}(t)\geq c_{\mathrm{ef}}]dt
$$

Se elige el plan con más horas de atención, respetando el umbral de sueño y el máximo diario.

## Archivos

- [Informe PDF](P02_C-09_VILLALOBOS.pdf)
- [Datos y cálculos](P02_C-09_VILLALOBOS.xlsx)

## Cómo revisar

Leer el informe y comparar la estrategia recomendada con las tablas y fórmulas del archivo `.xlsx`.
