# py-orden-y-progres

Colección de scripts en Python para ordenar el bondi digital.

Este repositorio reúne pequeños proyectos prácticos construidos con librerías de Python
que ayudan a automatizar tareas del día a día y que no siempre son las primeras que se
mencionan cuando se habla de Python.

Por ahora incluye:

- [`watchdog`](https://pypi.org/project/watchdog/): automatización basada en cambios en el sistema de archivos.
- [`typer`](https://typer.tiangolo.com/): creación de CLIs modernas y tipadas.

La idea es ir sumando ejemplos con otras librerías útiles como `rich`, `pyautogui`,
`invoke`, etc.

---

## 1. Organizador automático de Descargas con watchdog

Script: `02_watchdog_descargas.py`

Organiza automáticamente la carpeta **Descargas** de Windows utilizando `watchdog` para
reaccionar a la creación de nuevos archivos.

### Características

- Recorre los archivos existentes en la carpeta Descargas y los mueve a subcarpetas.
- Vigila en tiempo real nuevas descargas y las organiza automáticamente.
- Clasifica por **tipo de archivo**, **año**, **mes (en español)** y **quincena (1-15, 16-31)**.
- Mantiene un archivo de log con todas las operaciones realizadas.

### Estructura de carpetas generada

Dentro de `Descargas` se crean subcarpetas con la siguiente estructura:

```text
Descargas/
  _watchdog_descargas.log
  datos/AAAA/mes/1-15/
  documentos/AAAA/mes/1-15/
  imagenes/AAAA/mes/1-15/
  videos/AAAA/mes/1-15/
  comprimidos/AAAA/mes/1-15/
  scripts/AAAA/mes/1-15/
  otros/AAAA/mes/1-15/
```

#### Categorías principales

- `datos`: archivos de datos, bases de datos y dumps (`.xls`, `.xlsx`, `.csv`, `.sql`, `.db`, `.parquet`, etc.).
- `documentos`: documentos de texto y Office (`.pdf`, `.txt`, `.doc`, `.docx`, `.ppt`, `.pptx`).
- `imagenes`: formatos de imagen (`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`).
- `videos`: formatos de vídeo (`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`).
- `comprimidos`: archivos comprimidos (`.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`, `.xz`).
- `scripts`: código y scripts (`.py`, `.ipynb`, `.js`, `.ts`, `.rs`, `.c`, `.cpp`, `.html`, `.css`, `.sh`, `.bat`, `.ps1`, etc.).
- `otros`: cualquier archivo cuya extensión no entre en las categorías anteriores.

### Requisitos

- Python 3.8+ (probado en Windows).
- Librería `watchdog` instalada:

```bash
python -m pip install watchdog
```

### Uso

1. Clona o copia este proyecto en tu máquina.
2. Asegúrate de tener `watchdog` instalado.
3. Ejecuta el script desde la carpeta del proyecto:

```bash
python 02_watchdog_descargas.py
```

Al arrancar, el script:

1. Comprueba que exista la carpeta `Descargas` del usuario actual.
2. Recorre los archivos **ya existentes** en `Descargas` (solo la raíz) y los mueve a las carpetas correspondientes.
3. Empieza a vigilar en tiempo real la carpeta `Descargas` y organiza cada nuevo archivo que se descargue.

El archivo de log `_watchdog_descargas.log` queda en la propia carpeta `Descargas`.

### Notas

- El script utiliza la **fecha de modificación** del archivo para decidir el año, mes y quincena.
- Una vez que un archivo es movido a su subcarpeta, el script **ya no lo vuelve a tocar**, aunque luego sea modificado.
- Está pensado como una herramienta personal de organización; úsalo bajo tu propia responsabilidad y, si quieres, haz primero una copia de seguridad de tu carpeta Descargas.

---

## 2. Organizador de carpetas con Typer

Script: `03_typer_organizador.py`

Una CLI construida con [`typer`](https://typer.tiangolo.com/) que permite organizar
cualquier carpeta por tipo de archivo y fecha en una sola corrida, sin necesidad de
tener un proceso en ejecución permanente.

### Requisitos

- Python 3.8+.
- Librería `typer` instalada:

```bash
python -m pip install "typer[all]"
```

### Uso básico

Organizar la carpeta Descargas del usuario actual:

```bash
python 03_typer_organizador.py organizar
```

Simular qué haría sin mover archivos (`dry-run`):

```bash
python 03_typer_organizador.py organizar --dry-run
```

Organizar otra carpeta (por ejemplo `D:\datos_brutos`) incluyendo subcarpetas:

```bash
python 03_typer_organizador.py organizar -c "D:\\datos_brutos" --recursivo
```

La lógica de clasificación es la misma que en el organizador de Descargas
basado en `watchdog`.

---

## Licencia

Este proyecto es de uso personal/educativo. Ajusta la licencia según prefieras antes de publicarlo en GitHub.
