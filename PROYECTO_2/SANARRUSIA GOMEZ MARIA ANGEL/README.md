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

El flujo de dióxido de azufre se obtiene integrando el perfil de la pluma y multiplicándolo por el viento:

$$
\Phi(t)=u(t)\,\kappa\int_{-L}^{L}c(x,t)\,dx
$$

La masa emitida y la concentración estimada en el mirador se calculan como:

$$
M(a,b)=\int_a^b\Phi(t)\,dt,
\qquad
X(t)=\frac{\Phi(t)}{u(t)}\max\left\{0,\cos\left(\theta(t)-\theta_m\right)\right\}
$$

$$
\widehat{C}_m(t)=\beta X(t),
\qquad
\beta=\frac{\int C_m\,dt}{\int X\,dt}
$$

## Archivos

- [Informe PDF](P04_C-07_SANARRUSIA.pdf)
- [Datos y cálculos](P04_C-07_SANARRUSIA.xlsx)

## Cómo revisar

Leer el informe y revisar los cálculos que fundamentan la regla recomendada.
