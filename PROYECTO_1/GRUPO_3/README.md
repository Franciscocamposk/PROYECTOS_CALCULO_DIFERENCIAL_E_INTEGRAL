# Grupo 3

**Tema asignado: Tarifas por Tramos y Demanda de un Servicio Digital**

## Integrantes

- Jeremy Fonseca
- Luis Altamirano

## Tema asignado

Tarifas por Tramos y Demanda de un Servicio Digital. Recomendar la tarifa que maximiza el ingreso esperado cuando la demanda cambia al cruzar un precio crítico.

## Objetivo

Recomendar una tarifa de un servicio digital que maximice el ingreso esperado sin reducir de más la cantidad de clientes, cuando hay una promoción, un descuento o un cambio de tarifa en un precio crítico.

Completen aquí el servicio, la persona usuaria (mercadeo o ventas) y el precio crítico $p_c$ que usaron.

## Desarrollo

La demanda $D(p)$ depende del precio y cambia de tramo en el precio crítico $p_c$. El ingreso es $R(p) = p\,D(p)$.

Deben quedar calculados y explicados:

- Dos límites laterales de la demanda o del ingreso en $p = p_c$.
- Continuidad o discontinuidad de $D(p)$ y de $R(p)$.
- Derivada $R'(p)$.
- Intervalos de crecimiento y decrecimiento del ingreso.
- Punto crítico y precio que maximiza el ingreso, dentro de un intervalo de precios viable.

Funciones del programa: `demanda`, `ingreso` y `recomendar_precio`.

## Resultados

- Gráficas de $D(p)$ y $R(p)$, con el precio crítico y el precio recomendado marcados.
- Tabla con al menos 15 precios.
- Comparación de precio bajo, precio recomendado y precio alto.
- Mensaje con el precio recomendado, la demanda estimada y el ingreso esperado.

Escriban aquí los valores obtenidos y la recomendación. Los datos van en `demanda.csv`, o el README indica la semilla y los parámetros del generador simulado.

## Conclusiones

Indiquen qué tarifa conviene cobrar, qué ocurre al cruzar el precio crítico y qué limitaciones tiene el modelo.

## Cómo revisar el trabajo

1. Abrir `informe.pdf`.
2. En esta carpeta, con `demanda.csv` junto al programa, ejecutar:

```bash
python tarifas.py
```

Si la entrega es un notebook de Google Colab, sustituyan este comando por el enlace público.
