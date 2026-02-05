Typer es una librería ideal para construir CLIs (Command Line Interfaces)
modernas en Python, con anotaciones de tipos y ayuda automática al estilo
FastAPI.

Aquí la estás usando para crear una herramienta de organización de
carpetas por tipo de archivo y fecha.

**1. ¿Qué es Typer (muy corto)?**  
- Es un framework para crear aplicaciones de línea de comandos usando
  funciones normales de Python y type hints.  
- Genera automáticamente `--help`, validación de tipos, opciones con
  nombres largos y cortos, etc.

**2. Script de ejemplo que ya tienes creado**  
Archivo principal:  
- 03_typer_organizador.py

Este script define una aplicación Typer con un comando principal
`organizar` que:

- Recorre una carpeta (por defecto, Descargas del usuario actual).  
- Clasifica cada archivo por categoría (`datos`, `documentos`, `imagenes`,
  `videos`, `comprimidos`, `scripts`, `otros`).  
- Usa la fecha de modificación para crear subcarpetas
  `AAAA/mes/1-15` o `AAAA/mes/16-31`.  
- Opcionalmente recorre subcarpetas y puede funcionar en modo "simulación"
  sin mover nada.

**3. Instalación de Typer**  
Desde tu entorno de Python:

```bash
python -m pip install "typer[all]"
```

**4. Comandos básicos para probarlo**  


1) Ver la ayuda general:

```bash
python 03_typer_organizador.py --help
```

2) Organizar la carpeta Descargas (no recursivo):

```bash
python 03_typer_organizador.py organizar
```

3) Simular sin mover archivos (dry-run):

```bash
python 03_typer_organizador.py organizar --dry-run
```

4) Organizar una carpeta concreta e incluir subcarpetas:

```bash
python 03_typer_organizador.py organizar -c "D:\datos_brutos" --recursivo
```

**5. Qué ideas puedes extender con Typer**  
- Crear varias "tareas" (comandos) para distintos tipos de organización
  usando el mismo ejecutable.  
- Añadir opciones como `--solo-extension .pdf` o `--mover-a OTRA_RUTA`.  
- Construir pequeñas herramientas internas que puedas compartir con tu
equipo simplemente pasando un script `.py`.

Con Typer, cada script deja de ser solo "un archivo de Python" y pasa a
sentirse como una herramienta de línea de comandos bien diseñada.
