# pylint: disable=invalid-name
"""
computeSales.py

Calcula el costo total de ventas a partir de:
1) Un catálogo de precios en JSON (lista de productos con 'title' y 'price')
2) Un registro de ventas en JSON (lista de ventas con 'SALE_ID',
'Product', 'Quantity', etc.)

Requisitos clave:
- Invocación por línea de comandos con 2 archivos
- Imprime resultados en consola y en archivo
- Maneja datos inválidos: muestra errores y continúa
- Incluye tiempo de ejecución
- Cumple PEP8/flake8 y evita problemas comunes de pylint
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, TextIO, Tuple


@dataclass(frozen=True)
class SaleLine:
    """Representa una línea/registro de venta ya validada."""
    sale_id: int
    product: str
    quantity: int


class TeeOutput:
    """
    Replica todo lo que se imprime (write) a múltiples streams.
    """

    def __init__(self, streams: List[TextIO]) -> None:
        self._streams = streams

    def write(self, message: str) -> int:
        for stream in self._streams:
            stream.write(message)
            stream.flush()
        return len(message)

    def flush(self) -> None:
        for stream in self._streams:
            stream.flush()


def safe_load_json(path: Path) -> Optional[Any]:
    """
    Carga JSON de forma segura.
    - Si hay error, lo imprime y regresa None.
    """
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"[ERROR] Archivo no encontrado: {path}")
    except json.JSONDecodeError as exc:
        print(f"[ERROR] JSON inválido en {path}: {exc}")
    except OSError as exc:
        print(f"[ERROR] No se pudo leer {path}: {exc}")
    return None


def extract_tc_code(path: Path) -> str:
    """
    Obtiene el código del caso de prueba desde el nombre de archivo.
    Ejemplo: 'TC1.ProductList.json' -> 'TC1'
    Si no se detecta, regresa 'RUN'.
    """
    name = path.name
    if "." in name:
        candidate = name.split(".", maxsplit=1)[0].strip()
        return candidate or "RUN"
    return "RUN"


def build_price_catalog(raw_catalog: Any) -> Dict[str, float]:
    """
    Convierte el JSON del catálogo (lista de dicts) a un mapa: title -> price.
    Reporta entradas inválidas y continúa.
    """
    prices: Dict[str, float] = {}

    if not isinstance(raw_catalog, list):
        print(
            "[ERROR] El catálogo de precios debe ser una lista de productos."
        )
        return prices

    for idx, item in enumerate(raw_catalog, start=1):
        if not isinstance(item, dict):
            print(
                f"[ERROR] Producto #{idx}: se esperaba un objeto JSON (dict)."
            )
            continue

        title = item.get("title")
        price = item.get("price")

        if not isinstance(title, str) or not title.strip():
            print(f"[ERROR] Producto #{idx}: 'title' inválido o vacío.")
            continue

        if not isinstance(price, (int, float)):
            print(f"[ERROR] Producto '{title}': 'price' no es numérico.")
            continue

        prices[title.strip()] = float(price)

    return prices


def parse_sales(raw_sales: Any) -> List[SaleLine]:
    """
    Convierte el JSON de ventas (lista de dicts)
    a una lista validada de SaleLine.
    Reporta entradas inválidas y continúa.
    """
    parsed: List[SaleLine] = []

    if not isinstance(raw_sales, list):
        print("[ERROR] El archivo de ventas debe ser una lista de registros.")
        return parsed

    for idx, item in enumerate(raw_sales, start=1):
        if not isinstance(item, dict):
            print(f"[ERROR] Venta #{idx}: se esperaba un objeto JSON (dict).")
            continue

        sale_id = item.get("SALE_ID")
        product = item.get("Product")
        quantity = item.get("Quantity")

        if not isinstance(sale_id, int):
            print(f"[ERROR] Venta #{idx}: 'SALE_ID' inválido.")
            continue

        if not isinstance(product, str) or not product.strip():
            print(f"[ERROR] Venta #{idx}: 'Product' inválido o vacío.")
            continue

        if not isinstance(quantity, int):
            print(f"[ERROR] Venta #{idx}: 'Quantity' inválido (debe ser int).")
            continue

        if quantity < 0:
            print(
                f"[WARN] Venta #{idx}: 'Quantity' negativo ({quantity}). "
                "Se interpretará como devolución"
            )

        parsed.append(
            SaleLine(
                sale_id=sale_id,
                product=product.strip(),
                quantity=quantity,
            )
        )

    return parsed


def compute_totals(
    prices: Dict[str, float],
    sales: Iterable[SaleLine],
) -> Tuple[Dict[int, float], float]:
    """
    Calcula:
    - total por SALE_ID
    - total general
    Si un producto no existe en el catálogo, reporta error y continúa.
    """
    totals_by_sale: Dict[int, float] = {}
    grand_total = 0.0

    for line in sales:
        if line.product not in prices:
            print(
                "[ERROR] Producto no encontrado en el catálogo: "
                f"'{line.product}' (SALE_ID={line.sale_id})"
            )
            continue

        line_total = prices[line.product] * line.quantity
        totals_by_sale[line.sale_id] = (
            totals_by_sale.get(line.sale_id, 0.0) + line_total
        )
        grand_total += line_total

    return totals_by_sale, grand_total


def format_report(
    totals_by_sale: Dict[int, float],
    grand_total: float,
    elapsed_seconds: float,
) -> str:
    """
    Genera un texto legible para humanos con:
    - Totales por venta (SALE_ID)
    - Total general
    - Tiempo transcurrido
    """
    lines: List[str] = []
    lines.append("=== Sales Results ===")
    lines.append("")
    lines.append("Totales por SALE_ID:")
    if totals_by_sale:
        for sale_id in sorted(totals_by_sale.keys()):
            lines.append(
                f"  - SALE_ID {sale_id}: "
                f"${totals_by_sale[sale_id]:,.2f}"
            )
    else:
        lines.append("  (No se pudieron calcular totales por SALE_ID)")

    lines.append("")
    lines.append(f"TOTAL GENERAL: ${grand_total:,.2f}")
    lines.append(f"Tiempo transcurrido: {elapsed_seconds:.6f} segundos")
    lines.append("")
    return "\n".join(lines)


def ensure_dir(path: Path) -> None:
    """Crea el directorio si no existe."""
    path.mkdir(parents=True, exist_ok=True)


def write_text_file(path: Path, content: str) -> None:
    """Escribe texto en archivo (UTF-8) de forma segura."""
    try:
        with path.open("w", encoding="utf-8") as file:
            file.write(content)
    except OSError as exc:
        print(f"[ERROR] No se pudo escribir el archivo {path}: {exc}")


def main(argv: List[str]) -> int:
    """
    Punto de entrada.
    Devuelve código de salida:
    0 = OK (aunque haya errores recuperables de datos)
    2 = uso incorrecto / archivos no cargables
    """
    if len(argv) != 3:
        print("Uso:")
        print("  python computeSales.py priceCatalogue.json salesRecord.json")
        return 2

    catalog_path = Path(argv[1])
    sales_path = Path(argv[2])

    # Código del caso de prueba (TC1, TC2, etc.)
    # basado en el nombre del archivo.
    tc_code = extract_tc_code(catalog_path)

    results_dir = Path("results")
    ensure_dir(results_dir)

    # Archivos requeridos:
    # - SalesResults.txt (por especificación)
    # - TCx_SalesResults.txt (por tu requisito extra)
    results_file_required = results_dir / "SalesResults.txt"
    results_file_tc = results_dir / f"{tc_code}_SalesResults.txt"

    # Guardar lo impreso en consola:
    console_log_file = results_dir / f"{tc_code}_Console.txt"

    # Preparamos "tee" para que lo que se imprime salga a consola y a archivo.
    try:
        with console_log_file.open("w", encoding="utf-8") as console_file:
            original_stdout = sys.stdout
            sys.stdout = TeeOutput([original_stdout, console_file])

            start = time.perf_counter()

            raw_catalog = safe_load_json(catalog_path)
            raw_sales = safe_load_json(sales_path)

            if raw_catalog is None or raw_sales is None:
                print(
                    "[ERROR] No se pudo cargar uno o ambos "
                    "archivos de entrada."
                )
                return_code = 2
            else:
                prices = build_price_catalog(raw_catalog)
                parsed_sales = parse_sales(raw_sales)
                totals_by_sale, grand_total = (
                    compute_totals(prices, parsed_sales)
                )

                elapsed = time.perf_counter() - start
                report = format_report(totals_by_sale, grand_total, elapsed)

                # Imprimir a consola (y se irá también al Console.txt)
                print(report)

                # Escribir reportes a archivo (requerido + por TC)
                write_text_file(results_file_required, report)
                write_text_file(results_file_tc, report)

                return_code = 0

            return return_code
    finally:
        # Regresa stdout al que estaba antes.
        if "original_stdout" in locals():
            sys.stdout = original_stdout
        else:
            sys.stdout = sys.__stdout__

    # Nota: realmente nunca llega aquí por los returns dentro del try.
    # Se deja por claridad.
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
