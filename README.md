# A01168002_A5.2
# A5.2 – Ejercicio de programación 2 y análisis estático (computeSales)

Repositorio para la actividad **A5.2** del curso **Pruebas de software y aseguramiento de calidad**.  
Incluye la implementación del programa **computeSales.py** en Python, pruebas básicas, y el uso de herramientas de **análisis estático** (flake8 y pylint) para asegurar el cumplimiento de estándares de codificación.

---

## Objetivo del programa

El script `computeSales.py` calcula el **costo total** de un conjunto de ventas a partir de:

1. Un **catálogo de productos** en JSON (con `title` y `price`)
2. Un **registro de ventas** en JSON (con `SALE_ID`, `Product` y `Quantity`)

El programa:
- Se ejecuta por línea de comandos con **dos archivos JSON**.
- Imprime resultados en consola.
- Guarda resultados en archivos dentro de `results/`.
- Maneja entradas inválidas mostrando errores y continuando con el procesamiento.
- Incluye el **tiempo transcurrido** de ejecución.
- Cumple con **PEP8** y se valida con **flake8** y **pylint**.

---

## Estructura del repositorio

source/
computeSales.py
tests/
(test cases en JSON)
results/
(archivos de salida generados por el programa)


> Nota: Los nombres de archivos y carpetas pueden no ser estrictamente PEP8, pero el **código fuente** sí debe cumplir PEP8/flake8.

---

## Consideración importante: Cantidades negativas (devoluciones)

Si en el archivo de ventas existe una `Quantity` negativa, se interpreta como una **devolución/ajuste** y **se incluye en el total** (restando al costo total).  
El programa imprime un aviso tipo `[WARN]` cuando detecta cantidades negativas y continúa con el cálculo.

Esto permite que casos como TC2 (con devoluciones) coincidan con el total esperado.

---

## Requisitos

- Python 3.x
- Paquetes:
  - `flake8`
  - `pylint`

---

## Instalación recomendada (en entorno virtual)

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
pip install -U pip
pip install flake8 pylint
```
---

## Ejecución del programa

Desde la raíz del repositorio:

PowerShell (Windows)
python .\source\computeSales.py .\tests\TC1\TC1.ProductList.json .\tests\TC1\TC1.Sales.json
(Repite con TC2/TC3 ajustando la ruta de los archivos JSON.)

## Archivos generados (salida)

El programa genera archivos dentro de results/:

<TC>_SalesResults.txt
Resultado asociado al caso de prueba (por ejemplo: TC1_SalesResults.txt).

<TC>_Console.txt
Captura de todo lo impreso en consola durante la ejecución (por ejemplo: TC1_Console.txt).

## Análisis estático

flake8

Ejecuta validaciones de estilo PEP8 y errores comunes:

flake8 source

pylint

Ejecuta análisis más estricto de calidad/estilo:

pylint source/computeSales.py

## Notas de validación

Se recomienda ejecutar el programa con cada test case y guardar evidencia de los outputs generados en results/.

Si un producto del archivo de ventas no existe en el catálogo, el programa reporta el error y continúa con el resto de registros.

