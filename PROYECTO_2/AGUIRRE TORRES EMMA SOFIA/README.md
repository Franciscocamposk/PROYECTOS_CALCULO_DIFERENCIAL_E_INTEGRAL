# Proyecto 9 — Repotenciación de la Planta Eólica Tejona en Tilarán

![Proyecto](https://img.shields.io/badge/Proyecto%202-9-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--01-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** Emma Sofia Aguirre Torres  
**Código:** C-01  
**Modalidad:** individual

## Pregunta de decisión

¿Conviene repotenciar la planta y con cuál opción, o mantener las turbinas actuales?

## Objetivo y desarrollo

Analizar los datos de la planta mediante un modelo de integración, comparar las alternativas de repotenciación y sustentar una recomendación técnica.

## Modelo matemático

La potencia del viento, el límite de Betz y la energía generada se modelan como:

$$
P_{\mathrm{viento}}=\frac{1}{2}\rho Av^3,
\qquad
C_p=\frac{P(v)}{\frac{1}{2}\rho Av^3}\leq\frac{16}{27},
\qquad
E=\int_0^T P\big(v(t)\big)\,dt
$$

La distribución de Weibull, la potencia media y el escalamiento con la altura son:

$$
f(v)=\frac{k}{c}\left(\frac{v}{c}\right)^{k-1}e^{-(v/c)^k},
\qquad
\overline{P}=\int_0^{\infty}P(v)f(v)\,dv
$$

$$
v(H)=v(H_0)\left(\frac{H}{H_0}\right)^\alpha
$$

La energía anual y el valor presente neto de la repotenciación son:

$$
E_{\mathrm{anual}}=8760N(1-L)\overline{P}
$$

$$
VPN=-I+\left(\Delta E_{\mathrm{anual}}p-\Delta M\right)\frac{1-(1+r)^{-n}}{r}
$$

## Archivos

- [Informe PDF](P09_C-01_AGUIRRE.pdf)
- [Datos y cálculos](P09_C-01_AGUIRRE.xlsx)

## Cómo revisar

Leer el informe y contrastar sus resultados con las tablas y fórmulas del archivo `.xlsx`.
