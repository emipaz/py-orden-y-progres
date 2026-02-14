# QR Studio

QR Studio es una CLI con dos modos de uso:

- Modo interactivo: sin subcomando, con menu Rich.
- Modo CLI: usando subcomandos `generar` y `leer`.

---

## Requisitos

- Python 3.8+
- Dependencias principales:

```bash
python -m pip install rich segno pillow pyzbar pyperclip
```

- Opcional para logos SVG:

```bash
python -m pip install cairosvg
```

> En Windows, `pyzbar` puede requerir instalar ZBar. Si no decodifica, instala
> ZBar desde su release oficial y asegura el DLL en PATH.
>
> Para SVG en Windows, `cairosvg` necesita Cairo instalado en el sistema.

---

## Modo interactivo (menu)

Ejecuta sin subcomando:

```bash
python QRStudio.py
```

En el menu podes:

- Generar QR con template, colores, escala, borde y logo.
- Leer QR desde una imagen.

La entrada de texto/URL permite pegar desde el portapapeles.

---

## Modo CLI (subcomandos)

### Generar

```bash
python QRStudio.py generar "https://tusitio.com" --template ocean --salida qr_linkedin.png
```

Opciones principales:

- `--salida` / `-s`: ruta PNG de salida (si falta extension, se agrega `.png`).
- `--template`: `ocean`, `sunset`, `forest`, `mono`.
- `--dark` / `--light`: colores custom.
- `--borde`: grosor del borde.
- `--escala`: tamano del QR.
- `--sin-logo`: no agrega logo.

### Leer

```bash
python QRStudio.py leer qr_custom.png
```

---

## Logos

QR Studio busca logos en la carpeta `logos/`.

- Formatos soportados: PNG, JPG, WEBP y SVG.
- Si falta Cairo, los SVG no se podran usar y se mostrara un aviso.

Para agregar logos:

1) Crea o usa la carpeta `logos/`.
2) Copia tus archivos ahi.
3) En el menu, elige el logo por nombre.

---

## Ejemplos rapidos

Generar QR con colores custom:

```bash
python QRStudio.py generar "Mi QR" --dark "#0b0b0b" --light "#f2efe8" --salida qr_custom.png
```

Leer QR:

```bash
python QRStudio.py leer qr_custom.png
```

---

## Lanzador

`QRStudio.py` es un lanzador amigable. Internamente ejecuta el archivo
`04_qr_studio_rich.py`.
