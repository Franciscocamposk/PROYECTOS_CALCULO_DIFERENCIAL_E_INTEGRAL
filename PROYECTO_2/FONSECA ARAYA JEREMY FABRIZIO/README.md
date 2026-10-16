# Proyecto 3 — Amenaza sísmica y reforzamiento del Hospital de Golfito

![Proyecto](https://img.shields.io/badge/Proyecto%202-3-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--03-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** Jeremy Fabrizio Fonseca Araya  
**Código:** C-03  
**Modalidad:** individual

## Pregunta de decisión

¿Conviene reforzar el pabellón, con cuál de las dos opciones, y cuánta pérdida anual esperada se elimina por cada colón invertido?

## Objetivo y desarrollo

Aplicar integración al análisis de la amenaza sísmica, comparar opciones de reforzamiento y evaluar su conveniencia para la infraestructura hospitalaria.

## Modelo matemático

La velocidad y el desplazamiento se obtienen integrando la aceleración, y la intensidad de Arias es:

$$
v(t)=\int_0^t a(u)\,du,
\qquad
x(t)=\int_0^t v(u)\,du,
\qquad
I_A=\frac{\pi}{2g}\int_0^T a(t)^2\,dt
$$

La tasa de sismos, la pérdida anual esperada y el valor presente neto del reforzamiento son:

$$
\lambda(m)=\lambda_3\,10^{-b(m-3)},
\qquad
PAE=V_R\int_5^8D(m)[-\lambda'(m)]\,dm
$$

$$
VPN=-C+\int_0^H\Delta PAE\,e^{-rt}\,dt
$$

## Archivos

- [Informe PDF](P03_C-03_FONSECA.pdf)
- [Datos y cálculos](P03_C-03_FONSECA.xlsx)

## Cómo revisar

Leer el informe y revisar los cálculos que sustentan la recomendación.
