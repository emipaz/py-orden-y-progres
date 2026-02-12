"""Organizador automático de la carpeta Descargas usando watchdog.

Este script:

- Recorre los archivos ya existentes en la carpeta Descargas y los mueve
    a subcarpetas según tipo de archivo, año, mes y quincena usando la fecha
    de creación.
- Mantiene un fichero de log con todas las operaciones realizadas.
- Se queda vigilando Descargas y organiza automáticamente cada nueva descarga.

Está pensado como herramienta personal para mantener Descargas limpia y
facilitar encontrar archivos históricos por tipo y fecha.
"""

import time
import shutil
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Carpeta de descargas por defecto en Windows
CARPETA_DESCARGAS = Path.home() / "Downloads"
# Carpeta base donde se van a ordenar los archivos (directamente en Descargas)
CARPETA_ORDENADA = CARPETA_DESCARGAS
# Fichero de log (único archivo suelto en Descargas)
FICHERO_LOG = CARPETA_DESCARGAS / "_watchdog_descargas.log"

# Extensiones temporales típicas de navegadores (para no mover descargas a medio hacer)
EXTENSIONES_TEMPORALES = {".crdownload", ".part", ".tmp"}


# Conjuntos de extensiones populares por categoría
EXT_DOCS = {".pdf", ".txt", ".doc", ".docx", ".ppt", ".pptx", ".vtt", ".odt", ".rtf", ".epub", ".md", ".srt"}
EXT_IMG = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
EXT_VIDEO = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"}
EXT_COMP = {".zip", ".rar", ".7z", ".gz", ".tar", ".bz2", ".xz"}

# Datos, bases de datos y dumps
EXT_DATOS = {
    ".xls", ".xlsx", ".xlsm", ".ods",  # hojas de cálculo
    ".csv", ".tsv",                        # texto tabular
    ".sql", ".sqlite", ".db", ".mdb", ".accdb",  # bases de datos
    ".dump", ".bak",                      # backups / dumps
    ".parquet", ".feather", ".orc",     # formatos analíticos
}

# Scripts y código fuente
EXT_SCRIPTS = {
    ".py", ".ipynb",       # Python
    ".js", ".ts",".json",      # JavaScript / TypeScript
    ".rs",                   # Rust
    ".c", ".cpp", ".cxx", ".h", ".hpp",  # C / C++
    ".html", ".htm", ".css",               # Frontend
    ".sh", ".bat", ".ps1",                 # Scripts de shell / Windows
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

    Las categorías posibles son: "datos", "documentos", "imagenes",
    "videos", "comprimidos", "scripts" u "otros".

    Args:
        sufijo: Extensión del archivo, con o sin punto (por ejemplo ".pdf" o "pdf").

    Returns:
        Nombre de la categoría en minúsculas.
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


def escribir_log(mensaje: str) -> None:
    """Escribe una línea en el fichero de log con marca de tiempo.

    El log se guarda en ``FICHERO_LOG`` dentro de la carpeta Descargas.

    Args:
        mensaje: Texto a registrar en el log.
    """
    try:
        FICHERO_LOG.parent.mkdir(parents=True, exist_ok=True)
        with FICHERO_LOG.open("a", encoding="utf-8") as f:
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{ahora}] {mensaje}\n")
    except Exception:
        # Si el log falla, no queremos romper el script principal
        pass


class ManejadorDescargas(FileSystemEventHandler):
    def _procesar_archivo_nuevo(self, ruta_archivo: Path) -> None:
        """Aplica las comprobaciones y organiza un archivo recién disponible.

        Se usa tanto para on_created como para on_moved, ya que muchos
        navegadores descargan primero con extensión temporal y luego
        renombran al archivo definitivo.
        """

        # No mover el propio fichero de log
        if ruta_archivo == FICHERO_LOG:
            return

        # Ignorar archivos temporales de descarga
        if ruta_archivo.suffix.lower() in EXTENSIONES_TEMPORALES:
            return

        # Esperar un poco por si el archivo todavía se está escribiendo
        time.sleep(1)

        try:
            self.mover_y_organizar(ruta_archivo)
        except Exception as e:
            print(f"[ERROR] No se pudo mover {ruta_archivo}: {e}")

    def on_created(self, event):
        """Maneja la creación de un archivo nuevo en Descargas.

        Ignora carpetas, el propio fichero de log y archivos temporales
        de descarga, y delega la organización en ``mover_y_organizar``.

        Args:
            event: Evento de watchdog asociado a la creación del archivo.
        """
        if event.is_directory:
            return

        ruta_archivo = Path(event.src_path)
        self._procesar_archivo_nuevo(ruta_archivo)

    def on_moved(self, event):
        """Maneja renombrados dentro de Descargas.

        Navegadores como Chrome/Edge descargan primero con extensión
        temporal (.crdownload, .part, ...) y luego renombran al nombre
        final. Ese renombrado genera un evento on_moved, no on_created,
        así que aquí tratamos el destino como un archivo "nuevo".
        """

        if event.is_directory:
            return

        ruta_destino = Path(event.dest_path)
        self._procesar_archivo_nuevo(ruta_destino)

    def mover_y_organizar(self, ruta_archivo: Path) -> None:
        """Mueve un archivo a su carpeta de tipo/año/mes/quincena.

        Usa la fecha de creación del archivo para determinar año, mes y
        quincena, y la extensión para decidir la categoría.

        Args:
            ruta_archivo: Ruta absoluta del archivo a mover.
        """
        if not ruta_archivo.exists():
            return
        
        sufijo = ruta_archivo.suffix.lower()

        categoria = categoria_para_extension(sufijo)

        # Usamos la fecha de modificación del archivo (st_mtime)
        fecha = datetime.fromtimestamp(ruta_archivo.stat().st_mtime).date()

        anio = str(fecha.year)
        nombre_mes = MESES_ES[fecha.month - 1]
        quincena = "1-15" if fecha.day <= 15 else "16-31"

        # Carpeta destino: Downloads/_ordenado/documentos/2026/enero/1-15/
        carpeta_destino = CARPETA_ORDENADA / categoria / anio / nombre_mes / quincena
        carpeta_destino.mkdir(parents=True, exist_ok=True)

        destino = carpeta_destino / ruta_archivo.name

        # Evitar sobrescribir archivos: añadir sufijo si ya existe
        contador = 1
        while destino.exists():
            destino = carpeta_destino / f"{ruta_archivo.stem}_{contador}{ruta_archivo.suffix}"
            contador += 1

        mensaje = f"MOVER {ruta_archivo} -> {destino}"
        print(f"[MOVER] {ruta_archivo} -> {destino}")
        escribir_log(mensaje)
        shutil.move(str(ruta_archivo), str(destino))


def procesar_archivos_existentes(manejador: ManejadorDescargas) -> None:
    """Organiza los archivos que ya existen en la carpeta Descargas.

    Recorre solo archivos en la raíz de Descargas (no subcarpetas),
    ignorando el fichero de log y archivos temporales de descarga.

    Args:
        manejador: Instancia de ``ManejadorDescargas`` usada para mover archivos.
    """
    print("\n[INICIO] Procesando archivos existentes en Descargas...")

    total_encontrados = 0
    total_movidos = 0

    for ruta in CARPETA_DESCARGAS.iterdir():
        # Ignorar carpetas (incluida _ordenado) y el propio log
        if ruta.is_dir():
            continue
        if ruta == FICHERO_LOG:
            continue
        # Ignorar temporales de descarga
        if ruta.suffix.lower() in EXTENSIONES_TEMPORALES:
            continue

        total_encontrados += 1

        try:
            manejador.mover_y_organizar(ruta)
            total_movidos += 1
        except Exception as e:
            print(f"[ERROR] No se pudo mover existente {ruta}: {e}")
            escribir_log(f"ERROR al mover existente {ruta}: {e}")

    print(f"[FIN] Archivos existentes encontrados: {total_encontrados}, movidos: {total_movidos}\n")


def main():
    """Punto de entrada del script.

    Comprueba la existencia de la carpeta Descargas, organiza primero los
    archivos ya presentes y después inicia el observador de watchdog para
    procesar automáticamente las nuevas descargas.

    Returns:
        None
    """
    if not CARPETA_DESCARGAS.exists():
        print(f"La carpeta de descargas no existe: {CARPETA_DESCARGAS}")
        return

    print(f"Vigilando la carpeta de descargas: {CARPETA_DESCARGAS}")
    print("Los archivos se organizarán en subcarpetas por tipo, año, mes y quincena dentro de Descargas.")
    print("Primero se organizarán los archivos que ya están en Descargas y luego se vigilarán los nuevos.\n")

    manejador = ManejadorDescargas()

    # Pasada inicial: ordenar lo que ya existe en Descargas
    procesar_archivos_existentes(manejador)

    observador = Observer()
    observador.schedule(manejador, str(CARPETA_DESCARGAS), recursive=False)
    observador.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando observador...")
        observador.stop()

    observador.join()


if __name__ == "__main__":
    main()
