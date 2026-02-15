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
    Útil para guardar lo que sale en consola en un .txt.
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


