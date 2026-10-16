# Proyecto 10 — Ruido de embarcaciones y ballenas jorobadas en el Golfo Dulce

![Proyecto](https://img.shields.io/badge/Proyecto%202-10-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--08-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** Isaac Alexander Vega Orozco  
**Código:** C-08  
**Modalidad:** individual

## Pregunta de decisión

¿Qué medida reduce la energía sonora recibida por las ballenas, con el menor costo para la temporada?

## Objetivo y desarrollo

Analizar la energía sonora acumulada mediante integración, comparar medidas de control y recomendar la alternativa de menor costo y mayor reducción.

## Modelo matemático

La presión acústica al cuadrado y la energía sonora de un paso se modelan como:

$$
p^2(t)=\frac{S(v)}{d^2+v^2t^2}
$$

$$
E=\int_{-\infty}^{\infty}p^2(t)\,dt=\frac{\pi S(v)}{dv}
$$

Para un intervalo truncado y para la temporada completa:

$$
\int_{-T}^{T}p^2(t)\,dt=\frac{2S(v)}{dv}\arctan\left(\frac{vT}{d}\right)
$$

$$
S(v)=S_0\left(\frac{v}{v_0}\right)^n,
\qquad
E_{\mathrm{temp}}=\sum_k\frac{\pi S(v_k)}{d_kv_k}
$$

La medida elegida cumple la reducción mínima de energía con el menor costo de temporada.

## Archivos

- [Informe PDF](P10_C-08_VEGA.pdf)
- [Datos y cálculos](P10_C-08_VEGA.xlsx)

## Cómo revisar

Leer el informe para conocer el caso y contrastar sus resultados con la hoja de cálculo.
