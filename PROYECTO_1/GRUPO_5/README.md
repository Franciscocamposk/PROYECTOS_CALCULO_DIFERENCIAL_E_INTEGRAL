# Grupo 5

**Tema asignado: Capacidad de Servidores y Costo Marginal**

## Integrantes

- Isaac
- Junior

## Tema asignado

Capacidad de Servidores y Costo Marginal. Determinar cuántos usuarios simultáneos debe soportar la plataforma para maximizar la utilidad y cuándo ampliar la infraestructura.

## Objetivo

Estimar cuántos usuarios simultáneos puede soportar una plataforma web antes de que los costos de servidores, almacenamiento, soporte y monitoreo crezcan más rápido que los beneficios.

Completen aquí la plataforma, la persona usuaria (operaciones o infraestructura) y la capacidad máxima física o contractual.

## Desarrollo

Sea $x$ la cantidad de usuarios simultáneos. Definan el costo de infraestructura $C(x)$, el ingreso $R(x)$ y la utilidad $U(x) = R(x) - C(x)$.

Deben quedar calculados y explicados:

- Costo marginal $C'(x)$, ingreso marginal $R'(x)$ y utilidad marginal $U'(x)$.
- Punto crítico de $U(x)$.
- Criterio de la primera o la segunda derivada para clasificar el extremo.
- Concavidad de la utilidad o del costo.
- Análisis cuando $x \to \infty$, para explicar por qué la capacidad no puede crecer indefinidamente.

Funciones del programa: `costo`, `ingreso`, `utilidad` y `recomendar_capacidad`. El programa debe permitir cambiar costos fijos, costo por usuario, tarifa y capacidad máxima.

## Resultados

- Valores de $C'(x)$, $R'(x)$ y $U'(x)$.
- Gráficas de costo, ingreso y utilidad, con el $x$ que maximiza la utilidad.
- Comparación de infraestructura básica, intermedia y ampliada.
- Alerta cuando la demanda proyectada supera la capacidad máxima.

Escriban aquí la capacidad recomendada. Los parámetros pueden ir en `capacidad.csv` o documentados en este README.

## Conclusiones

Indiquen cuántos usuarios simultáneos conviene soportar, en qué momento ampliar la infraestructura y qué limitaciones tiene el modelo.

## Cómo revisar el trabajo

1. Abrir `informe.pdf`.
2. En esta carpeta, ejecutar:

```bash
python capacidad.py
```

Si la entrega es un notebook de Google Colab, sustituyan este comando por el enlace público.
