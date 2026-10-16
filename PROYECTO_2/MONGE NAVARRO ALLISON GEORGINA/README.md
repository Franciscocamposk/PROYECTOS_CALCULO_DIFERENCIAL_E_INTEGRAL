# Proyecto 6 — Migración de aves rapaces sobre Këköldi, Talamanca

![Proyecto](https://img.shields.io/badge/Proyecto%202-6-0b4f8a?style=flat-square) ![Código](https://img.shields.io/badge/Código-C--06-2e7d32?style=flat-square) ![Modalidad](https://img.shields.io/badge/Modalidad-Individual-e08a2e?style=flat-square)

**Estudiante:** Allison Georgina Monge Navarro  
**Código:** C-06  
**Modalidad:** individual

## Pregunta de decisión

¿Qué fechas y qué horario debe tener la campaña de voluntariado para registrar la mayor cantidad de aves migratorias?

## Objetivo y desarrollo

Modelar la migración mediante integración, analizar los periodos de mayor actividad y recomendar fechas y horarios de monitoreo.

## Modelo matemático

El total diario, el total de la temporada, la fracción acumulada y la fecha media se calculan como:

$$
N_d=\int_{h_i}^{h_f}r_d(x)\,dx,
\qquad
N=\int_{t_0}^{t_1}n(t)\,dt
$$

$$
F(t)=\frac{1}{N}\int_{t_0}^{t}n(u)\,du,
\qquad
\bar{t}=\frac{1}{N}\int_{t_0}^{t_1}t\,n(t)\,dt
$$

La campaña de $L$ días que inicia en $a$ captura:

$$
G(a)=\int_a^{a+L}n(t)\,dt,
\qquad
G'(a)=n(a+L)-n(a)=0
$$

## Archivos

- [Informe PDF](P06_C-06_MONGE.pdf)
- [Datos y cálculos](P06_C-06_MONGE.xlsx)

## Cómo revisar

Leer el informe y contrastar la recomendación con las tablas y fórmulas del archivo `.xlsx`.
