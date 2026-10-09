# Proyecto 1 — Cálculo Diferencial e Integral

Repositorio del **Proyecto Aplicado de Cálculo y Analítica Empresarial**.

- **Universidad:** Universidad de Costa Rica, Escuela de Matemática.
- **Curso:** MA-0321 Cálculo Diferencial e Integral, II ciclo 2026.
- **Valor:** 10 % de la nota total.
- **Modalidad:** parejas, máximo dos integrantes.
- **Defensa oral:** obligatoria para los dos integrantes. Deben explicar el problema, el modelo, las derivadas o límites, el código y la recomendación.

Este archivo explica el repositorio completo, el propósito del trabajo y cada proyecto. El `README.md` de cada carpeta explica el desarrollo de ese equipo.

## Entrega

**Fecha de entrega: viernes 25 de septiembre de 2026 (hoy).**

Cada grupo deja en su carpeta estos archivos:

| Archivo | Qué es |
| --- | --- |
| `informe.pdf` | Informe de 8 a 12 páginas, sin contar portada, referencias ni anexos. Times New Roman 12 o equivalente, interlineado 1.5. |
| `codigo.py` | Programa en Python 3.10 o superior. También vale un enlace público a Google Colab, escrito en el README del grupo. |
| `datos.csv` | Datos del modelo, o un generador de datos simulados con semilla y parámetros documentados en el README. |
| `README.md` | Cómo ejecutar el trabajo y qué resultó. |

El informe incluye portada, introducción, marco teórico, datos y supuestos, modelo matemático, resultados, implementación en Python, conclusiones con recomendación empresarial, al menos cuatro referencias en APA 7 y anexos.

## Propósito

El proyecto reúne el trabajo de los cinco grupos del curso. Cada equipo resuelve y documenta el tema de cálculo diferencial e integral que le fue asignado, en su propia carpeta, para que el repositorio quede organizado y se pueda revisar.

Este repositorio sirve para:

- Separar el trabajo de cada equipo.
- Identificar integrantes, tema y carpeta de cada proyecto.
- Dejar por escrito el objetivo, el procedimiento y los resultados.
- Consultar desde aquí el nombre y la descripción general de cada proyecto.

## Proyectos

| Grupo | Integrantes | Tema asignado | Carpeta |
| --- | --- | --- | --- |
| Grupo 1 | Alison Navarro y Emma Aguirre | Simulador de Ahorro | `GRUPO_1/` |
| Grupo 2 | Kendall Villalobos y Marcelle Fernández | Inventario Óptimo y Utilidad Neta de una Tienda Virtual | `GRUPO_2/` |
| Grupo 3 | Jeremy Fonseca y Luis Altamirano | Tarifas por Tramos y Demanda de un Servicio Digital | `GRUPO_3/` |
| Grupo 4 | Joseph Torrentes y Mariangel Sanarrusia | Crecimiento de Usuarios y Planificación de Capacidad Digital | `GRUPO_4/` |
| Grupo 5 | Isaac y Junior | Capacidad de Servidores y Costo Marginal | `GRUPO_5/` |

### Grupo 1 — `GRUPO_1/`

- **Integrantes:** Alison Navarro y Emma Aguirre.
- **Tema asignado:** Simulador de Ahorro.
- **Descripción general:** Comparan interés simple, interés compuesto y capitalización continua para recomendar qué alternativa de ahorro o inversión alcanza una meta con menor plazo o menor aporte. El detalle del trabajo se escribe en `GRUPO_1/README.md`.

### Grupo 2 — `GRUPO_2/`

- **Integrantes:** Kendall Villalobos y Marcelle Fernández.
- **Tema asignado:** Inventario Óptimo y Utilidad Neta de una Tienda Virtual.
- **Descripción general:** Determinan cuántas unidades conviene comprar o producir para maximizar la utilidad neta, después de costos, precio, descuentos, capacidad e impuesto. El detalle del trabajo se escribe en `GRUPO_2/README.md`.

### Grupo 3 — `GRUPO_3/`

- **Integrantes:** Jeremy Fonseca y Luis Altamirano.
- **Tema asignado:** Tarifas por Tramos y Demanda de un Servicio Digital.
- **Descripción general:** Recomiendan la tarifa de un servicio digital que maximiza el ingreso esperado, con una demanda que cambia al cruzar un precio crítico por promoción o tipo de cliente. El detalle del trabajo se escribe en `GRUPO_3/README.md`.

### Grupo 4 — `GRUPO_4/`

- **Integrantes:** Joseph Torrentes y Mariangel Sanarrusia.
- **Tema asignado:** Crecimiento de Usuarios y Planificación de Capacidad Digital.
- **Descripción general:** Estiman cómo crecen los usuarios activos de una plataforma y en qué periodo conviene ampliar servidores, soporte o almacenamiento antes de que la capacidad se agote. El detalle del trabajo se escribe en `GRUPO_4/README.md`.

### Grupo 5 — `GRUPO_5/`

- **Integrantes:** Isaac y Junior.
- **Tema asignado:** Capacidad de Servidores y Costo Marginal.
- **Descripción general:** Calculan cuántos usuarios simultáneos debe soportar una plataforma para maximizar la utilidad y en qué momento conviene ampliar la infraestructura. El detalle del trabajo se escribe en `GRUPO_5/README.md`.

## Estructura del repositorio

```text
PROYECTO_1_CALCULO_DIFERENCIAL_E_INTEGRAL/
├── README.md
├── GRUPO_1/
│   ├── INTEGRANTES.txt
│   ├── README.md
│   ├── informe.pdf
│   └── simulador.py
├── GRUPO_2/
│   ├── INTEGRANTES.txt
│   ├── README.md
│   ├── informe.pdf
│   ├── inventario.py
│   └── inventario.csv
├── GRUPO_3/
│   ├── INTEGRANTES.txt
│   ├── README.md
│   ├── informe.pdf
│   ├── tarifas.py
│   └── demanda.csv
├── GRUPO_4/
│   ├── INTEGRANTES.txt
│   ├── README.md
│   ├── informe.pdf
│   ├── crecimiento.py
│   └── usuarios.csv
└── GRUPO_5/
    ├── INTEGRANTES.txt
    ├── README.md
    ├── informe.pdf
    ├── capacidad.py
    └── capacidad.csv
```

## Cómo revisar cada proyecto

Desde la carpeta del grupo, con Python 3.10 o superior:

| Grupo | Comando |
| --- | --- |
| Grupo 1 | `python simulador.py` |
| Grupo 2 | `python inventario.py` |
| Grupo 3 | `python tarifas.py` |
| Grupo 4 | `python crecimiento.py` |
| Grupo 5 | `python capacidad.py` |

Si el equipo usa Google Colab, el enlace público va en el README de su carpeta, en la sección **Cómo revisar el trabajo**.

## Recordatorio para los estudiantes

**Cada grupo completa el `README.md` de su carpeta antes de entregar.** La plantilla ya trae el tema, los integrantes y la lista de cálculo y de Python que corresponde a ese proyecto. Hay que sustituir las indicaciones por los resultados del equipo.

## Reglas de trabajo

- Cada grupo modifica únicamente su carpeta.
- Los integrantes permanecen uno por línea en `INTEGRANTES.txt`.
- El `README.md` de la carpeta queda completo el día de la entrega.
- El código, las gráficas y el informe se guardan junto a ese README.
