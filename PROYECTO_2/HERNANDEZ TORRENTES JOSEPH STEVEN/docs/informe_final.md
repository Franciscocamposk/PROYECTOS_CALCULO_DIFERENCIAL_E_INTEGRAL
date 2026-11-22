# Proyecto Aplicado 2 — Proyecto 8
## Energía de las olas para una boya frente a Pavones

**Curso:** Cálculo Diferencial e Integral  
**Estudiante:** Joseph Steven Hernández Torrentes  
**Lugar de estudio:** Pavones, Costa Rica  
**Fecha:** Noviembre de 2026

---

## 1. Introducción

El aprovechamiento de la energía del oleaje representa una alternativa para suministrar electricidad a dispositivos ubicados en el mar. En este proyecto se estudia la posibilidad de alimentar una boya o estación marina con un consumo constante de 300 W mediante un convertidor de energía de olas y una batería.

El análisis utiliza 960 registros horarios proporcionados en un archivo Excel, junto con muestras de elevación de la superficie marina, características de tres convertidores y cuatro alternativas de almacenamiento.

Se implementaron métodos de integración numérica, cálculos de flujo energético, simulaciones horarias y una comparación económica para identificar el sistema de menor costo que satisface los criterios establecidos.

## 2. Objetivos

### Objetivo general

Determinar la combinación de convertidor de energía undimotriz y batería de menor costo capaz de cubrir al menos el 99 % de las horas analizadas, tanto en condiciones normales como ante una reducción del 20 % en la altura significativa del oleaje.

### Objetivos específicos

1. Leer, validar y preparar los registros de oleaje sin modificar los datos originales.
2. Implementar las reglas del trapecio compuesto y Simpson 1/3 compuesto.
3. Estimar la altura significativa del oleaje a partir de las muestras de elevación.
4. Calcular el flujo energético disponible y la potencia eléctrica generada.
5. Simular el almacenamiento y consumo de energía durante 960 horas consecutivas.
6. Comparar 12 combinaciones de convertidores y baterías según costo y disponibilidad.

## 3. Datos y metodología

Se utilizó el archivo original `P08_C-04_HERNANDEZ.xlsx`.

El conjunto principal contiene 960 registros horarios. Adicionalmente, la hoja `Muestra_elevacion` contiene 400 mediciones agrupadas en dos registros.

Se identificaron cuatro alturas significativas faltantes, que fueron estimadas mediante interpolación lineal sobre una copia de los datos. Cada valor interpolado quedó identificado con la columna `altura_estimada`.

Los valores atípicos detectados no fueron reemplazados automáticamente.

El proyecto se desarrolló en Python, utilizando funciones separadas para lectura, limpieza, integración, cálculos físicos, convertidores, baterías y evaluación de escenarios.

## 4. Fundamento matemático

### 4.1. Integración numérica

Para aproximar integrales definidas se implementaron dos métodos.

**Regla del trapecio compuesto:**

\[
\int_a^b f(x)\,dx \approx
\sum_{i=0}^{n-1}
\frac{x_{i+1}-x_i}{2}
\left[f(x_i)+f(x_{i+1})\right]
\]

**Regla de Simpson 1/3 compuesto**, para intervalos uniformes y una cantidad par de subintervalos:

\[
\int_a^b f(x)\,dx \approx
\frac{h}{3}
\left[
f(x_0)+f(x_n)
+4\sum_{\substack{i=1\\i\text{ impar}}}^{n-1}f(x_i)
+2\sum_{\substack{i=2\\i\text{ par}}}^{n-2}f(x_i)
\right]
\]

Cada muestra de elevación contiene 200 mediciones y 199 subintervalos. Para la comparación se utilizó un procedimiento híbrido: Simpson en los primeros 198 subintervalos y trapecio en el último.

### 4.2. Altura significativa

El modelo utiliza el promedio temporal del cuadrado de la elevación:

\[
\sigma^2=\frac{1}{T}\int_0^T \eta(t)^2\,dt
\]

A partir de este valor:

\[
H_s=4\sqrt{\sigma^2}
\]

La interpretación de \(\sigma^2\) como varianza supone que la elevación está referida a un nivel medio aproximadamente nulo.

### 4.3. Flujo energético de las olas

Se empleó la expresión:

\[
J=\frac{\rho g^2}{64\pi}H_s^2T_e
\]

Con:

- Densidad del agua: 1025 kg/m³.
- Gravedad: 9.81 m/s².
- Período energético: \(T_e=0.9T_p\).

El flujo energético obtenido se expresa en W/m.

### 4.4. Potencia de generación

Para cada convertidor:

\[
P_g=\min(P_{\mathrm{nom}},\eta bJ)
\]

La expresión limita la potencia eléctrica a la capacidad nominal del equipo.

### 4.5. Simulación de la batería

Cada registro representa un intervalo de una hora. Para cada intervalo se calcula la energía generada, la energía requerida por la estación, la descarga o carga de la batería y la energía no suministrada.

La batería se inicializa al 100 % de su capacidad.

Una hora se clasifica como cubierta solamente cuando se suministran los 300 Wh requeridos.

La disponibilidad se calcula mediante:

\[
D=\frac{\text{Horas cubiertas}}{\text{Horas totales}}\times100
\]

El requisito es \(D\geq99\%\).

## 5. Resultados

### 5.1. Comparación de métodos de integración

| Registro | Hs trapecio (m) | Hs híbrido (m) |
|---|---:|---:|
| 1 | 1.467543 | 1.467057 |
| 2 | 1.128478 | 1.128013 |

Las diferencias fueron inferiores a 0.0005 m. Esto muestra una alta cercanía entre las aproximaciones obtenidas, aunque no demuestra por sí mismo cuál es más exacta.

### 5.2. Preparación y flujo energético

- Registros horarios: 960.
- Alturas faltantes identificadas: 4.
- Alturas interpoladas: 4.
- Registros con flujo energético calculado: 960.
- Flujo energético medio: **9,548.039 W/m**.

### 5.3. Convertidores

| Convertidor | Potencia media (W) | Horas con generación ≥300 W |
|---|---:|---:|
| WEC-50 | 237.770 | 288 |
| WEC-100 | 433.421 | 539 |
| WEC-150 | 740.317 | 793 |

Estos valores corresponden a la generación directa, antes de considerar el almacenamiento en baterías.

### 5.4. Comparación de alternativas

Se evaluaron tres convertidores y cuatro baterías, para un total de 12 combinaciones.

En el escenario normal, la combinación de menor costo que cumplió el 99 % fue **WEC-150 + B10**, con un costo de ₡12,740,000 y una disponibilidad del 99.48 %.

Sin embargo, al reducir un 20 % la altura significativa de las olas, su disponibilidad descendió al 96.98 %. Por tanto, no cumple el criterio en ambos escenarios.

La combinación **WEC-150 + B20** alcanzó el 100 % de disponibilidad en ambos escenarios y fue la de menor costo entre las alternativas que cumplieron simultáneamente el requisito.

### 5.5. Sistema seleccionado

| Característica | Resultado |
|---|---|
| Convertidor | WEC-150 |
| Batería | B20 |
| Capacidad de almacenamiento | 20 kWh |
| Costo de adquisición | ₡15,990,000 |
| Disponibilidad normal | 100 % |
| Disponibilidad reducida | 100 % |
| Horas sin cobertura | 0 en ambos escenarios |

La auditoría energética no detectó diferencias en el balance por hora.

La energía mínima almacenada fue de aproximadamente 9.82 kWh en el escenario normal y 6.02 kWh en el escenario reducido.

## 6. Supuestos y limitaciones

Los resultados se obtuvieron bajo las siguientes condiciones:

- Consumo constante de 300 W.
- Batería inicialmente cargada al 100 %.
- Eficiencia ideal de carga y descarga.
- Sin autodescarga ni degradación.
- Sin pérdidas adicionales de conversión o mantenimiento.
- Sin fallas de los equipos.
- Período de oleaje constante al aplicar la reducción del 20 % en altura.
- Evaluación limitada a los registros disponibles.

Estas simplificaciones deben considerarse al interpretar la recomendación. El 100 % obtenido es una disponibilidad simulada, no una garantía de funcionamiento en el mar.

## 7. Verificación computacional

El proyecto dispone de pruebas automatizadas ejecutadas mediante `pytest`.

En la última comprobación local se aprobaron **74 pruebas**.

Se configuró GitHub Actions para ejecutar automáticamente las pruebas del Proyecto 8 cuando se publican cambios relevantes.

También se desarrolló una aplicación Streamlit y un notebook Jupyter para explorar los resultados y reproducir los cálculos principales.

## 8. Conclusiones

La integración numérica permitió estimar características del oleaje y comprobar la consistencia de las aproximaciones mediante trapecios y Simpson.

El procesamiento de las 960 horas permitió calcular el flujo energético, evaluar las alternativas de generación y simular el comportamiento del almacenamiento.

La comparación demostró que una combinación suficiente en condiciones normales puede dejar de cumplir el requisito cuando disminuye la altura de las olas.

**Bajo los supuestos implementados, WEC-150 + B20 es la alternativa de menor costo que satisface una disponibilidad mínima del 99 % en ambos escenarios.** Su costo de adquisición es ₡15,990,000.

Como trabajo futuro sería necesario incorporar eficiencias reales de baterías, autodescarga, degradación y otros escenarios de operación para mejorar la representatividad física del modelo.

## 9. Material complementario

- Archivo de datos original: `P08_C-04_HERNANDEZ.xlsx`.
- Código fuente: carpeta `src/`.
- Pruebas automatizadas: carpeta `tests/`.
- Aplicación interactiva: `app.py`.
- Notebook: `notebooks/analisis_energia_oleaje.ipynb`.
- Registro de decisiones: `docs/bitacora_supuestos.md`.
