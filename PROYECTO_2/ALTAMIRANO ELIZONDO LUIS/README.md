# Proyecto 5 — Procrastinación y entregas de tareas en Mediación Virtual

![Proyecto](https://img.shields.io/badge/Proyecto%202-5-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--10-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** Luis Altamirano Elizondo  
**Código:** C-10  
**Modalidad:** individual

## Pregunta de decisión

¿Qué estrategia contra la procrastinación debe aplicarse en todos los grupos el próximo semestre?

## Objetivo y desarrollo

Modelar el comportamiento de las entregas, aplicar integración a los datos suministrados y comparar estrategias para sustentar una recomendación académica.

## Modelo matemático

La proporción acumulada de entregas y el índice de procrastinación se definen mediante:

$$
F(t)=\int_0^t f(u)\,du,
\qquad
IP=\frac{\bar{t}}{T}=\frac{1}{T}\int_0^T\left[1-F(t)\right]dt
$$

El modelo hiperbólico de la densidad de entregas y su proporción en las últimas 24 horas son:

$$
f_k(t)=\frac{k}{\ln(1+kT)\left[1+k(T-t)\right]},
\qquad
\int_{T-24}^{T}f_k(t)\,dt=\frac{\ln(1+24k)}{\ln(1+kT)}
$$

Se recomienda la estrategia con mayor nota media, considerando también la carga docente.

## Archivos

- [Informe PDF](P05_C-10_ALTAMIRANO.pdf)
- [Datos y cálculos](P05_C-10_ALTAMIRANO.xlsx)

## Cómo revisar

Leer el informe y revisar los datos, fórmulas y resultados de la hoja de cálculo.
