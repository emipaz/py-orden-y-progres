"""Lanzador de QR Studio."""

from __future__ import annotations

from pathlib import Path
import runpy
import sys

SCRIPT_PATH = Path(__file__).with_name("04_qr_studio_rich.py")

if __name__ == "__main__":
    sys.argv[0] = "QRStudio"
    runpy.run_path(str(SCRIPT_PATH), run_name="__main__")
