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

La amenaza acumulada durante el intervalo de análisis se representa por:

$$
H(a,b)=\int_a^b h(t)\,dt
$$

La opción de reforzamiento se compara mediante una función de pérdida esperada $L(x)$:

$$
x^*=\operatorname*{arg\,min}_{x\in\mathcal{D}}L(x)
$$

## Archivos

- [Informe PDF](P03_C-03_FONSECA.pdf)
- [Datos y cálculos](P03_C-03_FONSECA.xlsx)

## Cómo revisar

Leer el informe y revisar los cálculos que sustentan la recomendación.
