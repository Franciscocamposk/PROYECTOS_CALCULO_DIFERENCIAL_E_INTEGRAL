# Grupo 4

**Tema asignado: Crecimiento de Usuarios y Planificación de Capacidad Digital**

## Integrantes

- Joseph Torrentes
- Mariangel Sanarrusia

## Tema asignado

Crecimiento de Usuarios y Planificación de Capacidad Digital. Estimar el crecimiento de usuarios activos y el periodo en que conviene ampliar la infraestructura antes de llegar a la capacidad máxima.

## Objetivo

Anticipar en qué periodo una plataforma digital debe ampliar servidores, soporte, almacenamiento o presupuesto de mercadeo, según el crecimiento de usuarios activos y la capacidad máxima.

Completen aquí la plataforma, la persona usuaria (datos, producto o mercadeo) y la capacidad máxima que usaron.

## Desarrollo

$N(t)$ es el número de usuarios activos en el tiempo $t$. El modelo puede ser exponencial, logístico o por tramos. Si los datos son simulados, justifiquen los parámetros.

Deben quedar calculados y explicados:

- Límite de $N(t)$ cuando $t \to \infty$.
- Derivada $N'(t)$ como tasa de crecimiento.
- Segunda derivada $N''(t)$ como aceleración o desaceleración.
- Intervalos de crecimiento y concavidad.
- Punto de inflexión, si el modelo lo permite.
- Periodo en el que se alcanza la capacidad máxima.
- Por qué no es viable proyectar un crecimiento indefinido.

Funciones del programa: `usuarios`, `tasa_crecimiento`, `aceleracion` y `proyectar_capacidad`.

## Resultados

- Al menos 20 periodos de datos, con fuente o simulación reproducible.
- Gráficas de $N(t)$, $N'(t)$ y $N''(t)$.
- Capacidad máxima y periodo estimado de saturación marcados en la gráfica.
- Alerta de ampliación de infraestructura.
- Comparación de al menos dos escenarios de crecimiento.
- Tabla de proyección semanal o mensual.

Escriban aquí el periodo recomendado para ampliar. Los datos van en `usuarios.csv`, o el README indica la semilla y los parámetros del generador simulado.

## Conclusiones

Indiquen en qué periodo conviene ampliar la infraestructura, qué escenario es más realista y qué limitaciones tiene el modelo.

## Cómo revisar el trabajo

1. Abrir `informe.pdf`.
2. En esta carpeta, con `usuarios.csv` junto al programa, ejecutar:

```bash
python crecimiento.py
```

Si la entrega es un notebook de Google Colab, sustituyan este comando por el enlace público.
