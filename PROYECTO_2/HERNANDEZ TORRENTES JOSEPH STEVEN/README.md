# Proyecto 8 — Energía de las olas para una boya frente a Pavones

![Proyecto](https://img.shields.io/badge/Proyecto%202-8-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--04-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** Joseph Steven Hernandez Torrentes  
**Código:** C-04  
**Modalidad:** individual

## Pregunta de decisión

¿Qué combinación de convertidor y batería, al menor costo, mantiene la boya funcionando al menos el 99 % del tiempo?

## Objetivo y desarrollo

Estimar la energía acumulada de las olas mediante integración y comparar combinaciones de convertidor y batería para la boya.

## Modelo matemático

La varianza de la elevación del mar, la altura significativa y la potencia de las olas son:

$$
\sigma^2=\frac{1}{T}\int_0^T\eta(t)^2\,dt,
\qquad
H_s=4\sigma,
\qquad
J=\frac{\rho g^2}{64\pi}H_s^2T_e
$$

La potencia generada por el convertidor y la energía almacenada en la batería se modelan como:

$$
P_g=\min\{P_{\mathrm{nom}},\varepsilon wJ\}
$$

$$
B(t)=\min\{B_{\max},\max\{0,B_0+\int_0^t[P_g(u)-P_c]du\}\}
$$

Se elige la combinación de menor costo que mantiene la boya operativa al menos el 99\% del tiempo.

## Archivos

- [Informe PDF](P08_C-04_HERNANDEZ.pdf)
- [Datos y cálculos](P08_C-04_HERNANDEZ.xlsx)

## Cómo revisar

Leer el informe y contrastar la combinación recomendada con las tablas de la hoja de cálculo.
