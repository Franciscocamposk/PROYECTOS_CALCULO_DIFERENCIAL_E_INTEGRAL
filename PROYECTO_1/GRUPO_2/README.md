# Grupo 2

**Tema asignado: Inventario Óptimo y Utilidad Neta de una Tienda Virtual**

## Integrantes

- Kendall Villalobos
- Marcelle Fernández

## Tema asignado

Inventario Óptimo y Utilidad Neta de una Tienda Virtual. Decidir cuántas unidades comprar o producir para maximizar la utilidad neta después de costos, precio, descuentos, capacidad e impuesto.

## Objetivo

Establecer la cantidad de inventario que maximiza la utilidad neta de una tienda virtual, después de costos, precio, descuentos, capacidad de almacenamiento e impuesto.

Completen aquí el producto, la persona usuaria (finanzas, inventario o comercio electrónico) y la pregunta de decisión con los datos usados.

## Desarrollo

Sean $q$ las unidades, $C(q)$ el costo total, $R(q)$ el ingreso total y $U(q) = R(q) - C(q)$. La utilidad neta descuenta un impuesto por tramos:

$$
U_N(q) = U(q) - T(U(q))
$$

Deben quedar calculados y explicados:

- Punto de equilibrio.
- Costo marginal $C'(q)$, ingreso marginal $R'(q)$ y utilidad marginal $U'(q)$.
- Utilidad neta e impuesto marginal.
- Crecimiento, decrecimiento y concavidad.
- Cantidad que maximiza la utilidad neta.
- Restricción de inventario máximo.

Funciones del programa: `costo`, `ingreso`, `utilidad`, `impuesto` y `recomendar_inventario`.

## Resultados

- Gráficas de costo, ingreso, utilidad antes de impuestos y utilidad neta.
- Puntos de equilibrio y cantidad óptima.
- Tabla con al menos 15 niveles de inventario.
- Comparación de tres escenarios de precio, costo variable o impuesto.
- Recomendación de inventario para el siguiente periodo.

Escriban aquí los valores obtenidos y la recomendación. Los datos van en `inventario.csv`, o el README indica la semilla y los parámetros del generador simulado.

## Conclusiones

Indiquen cuántas unidades conviene tener, por qué esa cantidad maximiza la utilidad neta y qué limitaciones tiene el modelo.

## Cómo revisar el trabajo

1. Abrir `informe.pdf`.
2. En esta carpeta, con `inventario.csv` junto al programa, ejecutar:

```bash
python inventario.py
```

Si la entrega es un notebook de Google Colab, sustituyan este comando por el enlace público.
