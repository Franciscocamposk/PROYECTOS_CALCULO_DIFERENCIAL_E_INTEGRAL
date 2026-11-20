
# Bitácora de supuestos y decisiones

## Proyecto 8 — Energía de las olas

### 1. Datos originales

Se utiliza el archivo P08_C-04_HERNANDEZ.xlsx,
entregado por el profesor.

Los datos son simulados.

El archivo original no será modificado.

### 2. Exploración inicial

La hoja Registros_oleaje contiene 960 registros
horarios, correspondientes a 40 días.

Periodo:
2026-05-01 00:00 a 2026-06-09 23:00.

Se comprobó:
- 0 fechas inválidas.
- 0 fechas repetidas.
- 0 horas sin registro.
- 0 filas completamente duplicadas.

### 3. Valores faltantes

**Tratamiento de valores faltantes — Implementado y verificado**

Se identificaron cuatro valores faltantes en la variable `altura_significativa_m`, equivalentes al 0,42 % de los registros.

Se aplicó interpolación lineal temporal sobre una copia de los datos, debido a que las cuatro observaciones estaban aisladas entre mediciones válidas y la secuencia temporal presenta intervalos de una hora, sin duplicaciones ni fechas faltantes.

Se obtuvieron las siguientes estimaciones:

- 7 de mayo, 02:00: 2,930 m.
- 9 de mayo, 21:00: 1,045 m.
- 15 de mayo, 16:00: 1,170 m.
- 1 de junio, 02:00: 1,315 m.

Se verificó que se conservaron los 960 registros, las 956 alturas originalmente disponibles y las demás columnas.

Se incorporó la variable booleana `altura_estimada` para identificar los registros tratados.

El archivo Excel original se mantiene intacto. Los valores interpolados son estimaciones matemáticas, no mediciones observadas.

**Pendiente:** evaluar la sensibilidad del modelo energético a las decisiones de tratamiento de datos.
### 4. Valores atípicos

El método IQR identificó:
- 73 posibles atípicos de altura.
- 0 posibles atípicos de periodo pico.

De los 73 valores elevados:
- 70 aparecen del 5 al 8 de mayo.
- 1 aparece el 9 de mayo.
- 1 aparece el 11 de mayo.
- 1 aparece el 29 de mayo.

### 5. Revisión de picos

9 de mayo, 06:00:
Altura registrada de 3.47 m.
Pico aislado respecto a las horas vecinas.

11 de mayo, 20:00:
Altura registrada de 2.90 m.
Pico aislado respecto a las horas vecinas.

29 de mayo, 10:00:
Altura registrada de 2.36 m.
Comportamiento coherente con las horas cercanas.

### 6. Decisiones preliminares

- Conservar provisionalmente los episodios
  de oleaje elevado que muestran continuidad.
- Mantener el registro del 29 de mayo.
- Marcar como sospechosos los picos aislados
  del 9 y 11 de mayo.
- Comparar posteriormente resultados con
  y sin tratamiento de esos dos picos.
- No eliminar registros sin justificación.

Estado: análisis exploratorio en desarrollo.



## Verificación automática del módulo de limpieza

Se utiliza pytest para comprobar el comportamiento
de las funciones del módulo src/limpieza.py.

### Resultado de las pruebas

Se ejecutaron diez pruebas automáticas y todas
finalizaron correctamente.

Las pruebas verifican:

1. Aceptación de columnas obligatorias.
2. Conteo de valores faltantes.
3. Rechazo de columnas faltantes.
4. Rechazo de fechas duplicadas.
5. Rechazo de alturas faltantes consecutivas.
6. Interpolación y conservación de datos originales.
7. Rechazo de alturas faltantes al inicio.
8. Rechazo de alturas faltantes al final.
9. Rechazo de saltos en la secuencia horaria.
10. Detección de valores atípicos mediante IQR.

Comando utilizado:

python -m pytest tests/test_limpieza.py -v

Resultado: 10 pruebas superadas.

### Tratamiento de los datos

El archivo Excel original no se modifica.

Las alturas faltantes aisladas se interpolan
linealmente en una copia de trabajo.

Los registros interpolados se identifican
mediante la columna altura_estimada.

Los valores atípicos se identifican para
revisión, pero no se eliminan automáticamente.

### Decisiones pendientes

Se mantiene pendiente de investigación la
interpretación de los picos de oleaje sospechosos.

Antes de decidir si deben conservarse o tratarse,
se requiere justificar la decisión con evidencia
y considerar su efecto sobre los resultados.



## Cierre de la etapa de limpieza

### Estado

La implementación básica del módulo de limpieza
se considera finalizada y verificada.

El módulo contiene las siguientes funciones:

- validar_columnas()
- detectar_faltantes()
- detectar_atipicos()
- preparar_copia()
- interpolar_alturas()

### Pruebas automáticas

Se ejecutaron 11 pruebas utilizando pytest.

Resultado: 11 pruebas aprobadas.

Las pruebas verifican el comportamiento de las
funciones ante datos válidos y distintos errores
de estructura, fechas y valores faltantes.

### Resultados sobre los datos de oleaje

El conjunto original contiene 960 registros horarios.

Se identificaron cuatro alturas faltantes aisladas,
que fueron estimadas mediante interpolación lineal
en una copia de trabajo.

Los valores estimados se identifican mediante
la columna altura_estimada.

El archivo Excel original no requiere modificaciones.

### Tratamiento de valores atípicos

Los valores atípicos detectados mediante IQR no se
eliminan automáticamente.

Se conservan provisionalmente los valores observados.

Queda pendiente investigar dos picos aislados
registrados el 9 y el 11 de mayo de 2026.

Se propone realizar posteriormente un análisis
de sensibilidad para evaluar el efecto de estos
valores sobre los resultados del modelo.

### Conclusión

El módulo de limpieza queda listo para utilizarse
en las siguientes etapas del proyecto.

Este cierre corresponde a la implementación básica
y no implica que todas las decisiones sobre la
calidad de los datos sean definitivas.




---

## Decisiones del modelo energético

### 1. Datos originales

Se utilizan 960 registros horarios de oleaje y 400 mediciones
de elevación, distribuidas en dos muestras.

El Excel original permanece sin modificaciones.

### 2. Valores faltantes

Se identificaron cuatro alturas significativas faltantes.

Se aplicó interpolación lineal únicamente sobre una copia
de los registros, conservando la marca `altura_estimada`.

Los valores atípicos detectados no fueron reemplazados
automáticamente.

### 3. Integración numérica

Se implementaron directamente los métodos de trapecio
compuesto y Simpson 1/3 compuesto.

Cada muestra contiene 200 mediciones, equivalentes
a 199 subintervalos.

Para comparar los métodos se utilizó Simpson sobre los
primeros 198 subintervalos y trapecio sobre el último.

### 4. Modelo físico

Se utiliza la ecuación:

J = (rho * g² / (64*pi)) * Hs² * Te

Donde Te = 0.9 * Tp.

Los parámetros rho = 1025 kg/m³ y g = 9.81 m/s²
provienen del Excel proporcionado.

### 5. Convertidores

La potencia eléctrica se calcula mediante:

Pg = min(Pnom, eficiencia * ancho * J)

Se evalúan los convertidores WEC-50, WEC-100 y WEC-150.

### 6. Baterías

Se evalúan las baterías B2, B5, B10 y B20.

Supuestos implementados:

- Consumo constante de 300 W.
- Intervalos de una hora.
- Batería inicialmente cargada al 100 %.
- Eficiencia de carga y descarga del 100 %.
- Sin degradación de la batería.
- Sin pérdidas eléctricas adicionales.

La eficiencia ideal es una simplificación del modelo,
no una característica física confirmada de las baterías.

### 7. Escenario de oleaje reducido

Se disminuye la altura significativa un 20 %.

Se mantiene constante el período pico.

Como el flujo energético depende de Hs², se utiliza:

J_reducido = 0.64 * J_original.

### 8. Criterio de selección

Se requiere una disponibilidad mínima del 99 %
de las 960 horas en ambos escenarios.

Una hora se considera cubierta cuando se suministra
la totalidad de los 300 Wh requeridos.

Se selecciona la alternativa de menor costo que cumpla
ambos escenarios.

### 9. Resultado obtenido

Convertidor: WEC-150.
Batería: B20.
Costo total: ₡15,990,000.

Disponibilidad normal: 100 %.
Disponibilidad con oleaje reducido: 100 %.

La simulación no registró horas sin cobertura
para esta combinación.

### 10. Limitaciones

Los resultados corresponden a una simulación académica.

No se modelan pérdidas por temperatura, envejecimiento,
autodescarga, mantenimiento o fallas de equipos.

Tampoco se consideran condiciones de oleaje diferentes
de las registradas ni incertidumbres adicionales.

La recomendación debe interpretarse dentro de estos
supuestos y no como garantía de operación real.
