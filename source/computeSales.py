"""
computeSales.py

Calcula el costo total de ventas a partir de:
1) Un catálogo de precios en JSON (lista de productos con 'title' y 'price')
2) Un registro de ventas en JSON (lista de ventas con 'SALE_ID', 'Product', 'Quantity', etc.)

Requisitos clave:
- Invocación por línea de comandos con 2 archivos
- Imprime resultados en consola y en archivo
- Maneja datos inválidos: muestra errores y continúa
- Incluye tiempo de ejecución
- Cumple PEP8/flake8 y evita problemas comunes de pylint
"""

from __future__ import annotations

import json
import os
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
        print("[ERROR] El catálogo de precios debe ser una lista de productos.")
        return prices

    for idx, item in enumerate(raw_catalog, start=1):
        if not isinstance(item, dict):
            print(f"[ERROR] Producto #{idx}: se esperaba un objeto JSON (dict).")
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
    Convierte el JSON de ventas (lista de dicts) a una lista validada de SaleLine.
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

        if not isinstance(quantity, int) or quantity < 0:
            print(f"[ERROR] Venta #{idx}: 'Quantity' inválido (debe ser int >= 0).")
            continue

        parsed.append(SaleLine(sale_id=sale_id, product=product.strip(), quantity=quantity))

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
        totals_by_sale[line.sale_id] = totals_by_sale.get(line.sale_id, 0.0) + line_total
        grand_total += line_total

    return totals_by_sale, grand_total