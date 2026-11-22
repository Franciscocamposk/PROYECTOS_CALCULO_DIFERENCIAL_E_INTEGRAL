# Diccionario de Datos y Bitácora de Supuestos — Proyecto 10 (C-08)

## 1. Diccionario de Variables (`P10_C-08_VEGA.xlsx`)
- **Pasos_embarcaciones (1,100 registros):**
  - `id_paso`: identificador único del cruce.
  - `fecha_hora`: marca temporal (julio a octubre de 2026).
  - `tipo`: categoría (`Lancha turística`, `Panga de pesca`, `Yate`, `Velero`).
  - `velocidad_nudos`: velocidad de navegación (`nudos`; 1 nudo = `1852/3600` m/s).
  - `distancia_minima_m`: distancia en el punto más cercano a las ballenas (`m`).
- **Hidrofono (300 registros):**
  - `pase`: número de prueba (1 a 8 nudos, 2 a 20 nudos).
  - `tiempo_s`: tiempo relativo al paso (`s`, intervalo `[-150, 150]`).
  - `presion_cuadratica_Pa2`: presión acústica al cuadrado (`Pa²`).
- **Opciones / Parametros:** límites (`nudos`, `m`), costos fijos (`CRC`), longitud de zona (`6 km`), ruido ambiental (`0.003284 Pa²`), meta (`50%`), tarifa horaria (`₡23,000/h`).

## 2. Bitácora de Limpieza y Supuestos
1. **Tratamiento de faltantes y atípicos:**
   - Velocidad faltante: 1 registro (`ID #521`, Lancha turística).
   - Velocidades físicamente imposibles: 4 registros (`ID #294`: 85.5 kts, `ID #561`: Velero a 30.5 kts, `ID #718`: 79.5 kts, `ID #1080`: 108.5 kts).
   - Distancias faltantes: 6 registros (`IDs 16, 138, 526, 843, 847, 914`).
   - **Criterio:** Imputación por la **mediana válida** de cada tipo de embarcación para no eliminar viajes ni sesgar con valores extremos.
2. **Supuestos del modelo:**
   - Trayectoria rectilínea a velocidad constante $v$ y distancia mínima $d$.
   - Propagación geométrica esférica $p^2(t) = S(v)/(d^2 + v^2t^2)$ y ley de potencia $S(v) = S_0(v/v_0)^n$.
   - Costo operativo proporcional al tiempo extra en los $L = 6\text{ km}$ sensibles.
