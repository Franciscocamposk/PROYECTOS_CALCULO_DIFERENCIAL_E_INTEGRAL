# Grupo 1

**Tema asignado: Simulador de Ahorro**

## Integrantes

- Alison Navarro
- Emma Aguirre

## Tema asignado

Simulador de Ahorro. Comparar planes de ahorro o inversión (interés simple, interés compuesto y capitalización continua) y recomendar la alternativa que alcanza una meta con menor plazo o menor aporte.

## Objetivo

Ayudar a una persona a comparar alternativas financieras y elegir la que alcanza una meta con menor tiempo, mayor rendimiento o menor aporte inicial.

Completen aquí el contexto de la entidad o aplicación, la persona usuaria y la meta numérica que usaron.

## Desarrollo

El modelo compara interés simple, interés compuesto y capitalización continua:

$$
A(t) = P\left(1 + \frac{r}{n}\right)^{nt}
$$

Deben quedar calculados y explicados:

- Funciones exponenciales de cada alternativa.
- Límite al infinito del capital acumulado.
- Derivada del monto respecto del tiempo y razón de crecimiento del capital.
- Diferencial o sensibilidad ante un cambio pequeño de la tasa $r$ o del capital inicial $P$.
- Tiempo necesario para alcanzar la meta.
- Comparación de escenarios de tasa, plazo y frecuencia de capitalización.

Funciones del programa: `interes_simple`, `interes_compuesto`, `capitalizacion_continua` y `tiempo_para_meta`.

## Resultados

- Tabla comparativa de al menos tres alternativas.
- Gráfica del crecimiento del capital de cada alternativa.
- Gráfica del efecto de modificar la tasa de interés.
- Medida de sensibilidad ante un cambio pequeño de la tasa.
- Recomendación automática según la meta.

Escriban aquí los valores obtenidos y la recomendación.

## Conclusiones

Indiquen qué alternativa conviene, qué variable impacta más el resultado y qué limitaciones tiene el modelo.

## Cómo revisar el trabajo

1. Abrir `informe.pdf`.
2. En esta carpeta, ejecutar:

```bash
python simulador.py
```

El programa pide o define capital inicial, tasa, plazo, meta y frecuencia de capitalización. Si la entrega es un notebook de Google Colab, sustituyan este comando por el enlace público.
