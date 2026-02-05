import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MiManejador(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            print(f"[CREADA CARPETA] {event.src_path}")
        else:
            print(f"[CREADO ARCHIVO] {event.src_path}")

    def on_modified(self, event):
        if event.is_directory:
            print(f"[MODIFICADA CARPETA] {event.src_path}")
        else:
            print(f"[MODIFICADO ARCHIVO] {event.src_path}")

    def on_deleted(self, event):
        if event.is_directory:
            print(f"[ELIMINADA CARPETA] {event.src_path}")
        else:
            print(f"[ELIMINADO ARCHIVO] {event.src_path}")

    def on_moved(self, event):
        print(f"[MOVIDO] {event.src_path} -> {event.dest_path}")


def main():
    # Carpeta a vigilar: puedes cambiarla si quieres
    carpeta = Path(__file__).parent / "carpeta_a_vigilar"
    carpeta.mkdir(exist_ok=True)

    print(f"Vigilando la carpeta: {carpeta}")
    print("Prueba crear, modificar o borrar archivos dentro de esa carpeta.")

    event_handler = MiManejador()
    observer = Observer()
    observer.schedule(event_handler, str(carpeta), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando observador...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
