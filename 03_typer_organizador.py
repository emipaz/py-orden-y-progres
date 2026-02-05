"""CLI de organización de archivos usando Typer.

Este script muestra cómo usar Typer para construir una interfaz de
línea de comandos sencilla que organiza archivos en una carpeta
(por defecto, Descargas) clasificándolos por tipo y fecha.

No usa watchdog: está pensado como una pasada manual controlada
por el usuario, complementando el script de watchdog continuo.
"""

from datetime import datetime
from pathlib import Path
import shutil
from typing import Iterable

import typer

app = typer.Typer(help="Organizador de archivos por tipo y fecha usando Typer.")


# Extensiones temporales típicas de navegadores (para no mover descargas a medio hacer)
EXTENSIONES_TEMPORALES = {".crdownload", ".part", ".tmp"}

# Conjuntos de extensiones populares por categoría
EXT_DOCS = {".pdf", ".txt", ".doc", ".docx", ".ppt", ".pptx"}
EXT_IMG = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
EXT_VIDEO = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"}
EXT_COMP = {".zip", ".rar", ".7z", ".gz", ".tar", ".bz2", ".xz"}

# Datos, bases de datos y dumps
EXT_DATOS = {
    ".xls",
    ".xlsx",
    ".xlsm",
    ".ods",  # hojas de cálculo
    ".csv",
    ".tsv",  # texto tabular
    ".sql",
    ".sqlite",
    ".db",
    ".mdb",
    ".accdb",  # bases de datos
    ".dump",
    ".bak",  # backups / dumps
    ".parquet",
    ".feather",
    ".orc",  # formatos analíticos
}

# Scripts y código fuente
EXT_SCRIPTS = {
    ".py",
    ".ipynb",  # Python
    ".js",
    ".ts",  # JavaScript / TypeScript
    ".rs",  # Rust
    ".c",
    ".cpp",
    ".cxx",
    ".h",
    ".hpp",  # C / C++
    ".html",
    ".htm",
    ".css",  # Frontend
    ".sh",
    ".bat",
    ".ps1",  # Scripts de shell / Windows
}

MESES_ES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


def categoria_para_extension(sufijo: str) -> str:
    """Obtiene la categoría de organización para una extensión de archivo.

    Args:
        sufijo: Extensión del archivo, con punto (por ejemplo ".pdf").

    Returns:
        Nombre de la categoría: "datos", "documentos", "imagenes",
        "videos", "comprimidos", "scripts" u "otros".
    """

    sufijo = sufijo.lower()

    if sufijo in EXT_DATOS:
        return "datos"
    if sufijo in EXT_DOCS:
        return "documentos"
    if sufijo in EXT_IMG:
        return "imagenes"
    if sufijo in EXT_VIDEO:
        return "videos"
    if sufijo in EXT_COMP:
        return "comprimidos"
    if sufijo in EXT_SCRIPTS:
        return "scripts"
    return "otros"


def iterar_archivos(carpeta: Path, recursivo: bool) -> Iterable[Path]:
    """Devuelve un generador de archivos dentro de una carpeta.

    Args:
        carpeta: Carpeta base a recorrer.
        recursivo: Si es True, incluye subcarpetas.

    Returns:
        Un iterable de objetos Path apuntando a archivos.
    """

    if recursivo:
        yield from (p for p in carpeta.rglob("*") if p.is_file())
    else:
        yield from (p for p in carpeta.iterdir() if p.is_file())


def destino_para_archivo(archivo: Path, carpeta_base: Path) -> Path:
    """Calcula la carpeta destino para un archivo.

    Se usa la fecha de modificación del archivo para decidir año, mes y
    quincena, y la extensión para decidir la categoría.

    Args:
        archivo: Archivo a clasificar.
        carpeta_base: Carpeta raíz donde se crearán las subcarpetas.

    Returns:
        Ruta completa de la carpeta donde debería ubicarse el archivo.
    """

    sufijo = archivo.suffix.lower()
    categoria = categoria_para_extension(sufijo)

    fecha = datetime.fromtimestamp(archivo.stat().st_mtime).date()
    anio = str(fecha.year)
    nombre_mes = MESES_ES[fecha.month - 1]
    quincena = "1-15" if fecha.day <= 15 else "16-31"

    return carpeta_base / categoria / anio / nombre_mes / quincena


@app.command()
def organizar(
    carpeta: Path = typer.Option(
        Path.home() / "Downloads",
        "--carpeta",
        "-c",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Carpeta que se va a organizar (por defecto, Descargas).",
    ),
    recursivo: bool = typer.Option(
        False,
        "--recursivo",
        "-r",
        help="Incluir también archivos dentro de subcarpetas.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Mostrar lo que se haría sin mover realmente los archivos.",
    ),
):
    """Organiza archivos en una carpeta por tipo y fecha.

    Recorre la carpeta indicada (por defecto, Descargas del usuario
    actual) y mueve los archivos a subcarpetas según tipo de archivo,
    año, mes y quincena. Se pueden incluir subcarpetas y también
    ejecutar en modo simulación (dry-run).
    """

    typer.echo(f"Carpeta base: {carpeta}")
    if dry_run:
        typer.echo("Modo: simulación (no se moverán archivos)")
    if recursivo:
        typer.echo("Recorrido: recursivo (incluye subcarpetas)")

    total = 0
    movidos = 0

    for archivo in iterar_archivos(carpeta, recursivo=recursivo):
        # Ignorar temporales de descarga
        if archivo.suffix.lower() in EXTENSIONES_TEMPORALES:
            continue

        total += 1
        carpeta_destino = destino_para_archivo(archivo, carpeta)
        carpeta_destino.mkdir(parents=True, exist_ok=True)

        destino = carpeta_destino / archivo.name
        contador = 1
        while destino.exists():
            destino = carpeta_destino / f"{archivo.stem}_{contador}{archivo.suffix}"
            contador += 1

        if dry_run:
            typer.echo(f"[SIMULAR] {archivo} -> {destino}")
        else:
            typer.echo(f"[MOVER] {archivo} -> {destino}")
            shutil.move(str(archivo), str(destino))
            movidos += 1

    typer.echo(f"\nArchivos analizados: {total}")
    if dry_run:
        typer.echo(f"Movimientos simulados: {total}")
    else:
        typer.echo(f"Archivos movidos: {movidos}")


if __name__ == "__main__":
    app()
