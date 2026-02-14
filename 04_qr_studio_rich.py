"""QR Studio CLI para generar y leer QRs en consola.

Incluye un menu interactivo con Rich, soporte de colores, logos y lectura
desde imagenes, pensando en usuarios no tecnicos.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Optional

import segno
import typer
import pyperclip

from PIL import Image, ImageDraw, ImageFont
from pyzbar.pyzbar import decode
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

app = typer.Typer(
    add_completion=False,
    help=(
        "QR Studio con Rich. Modo interactivo sin subcomando y modo CLI con subcomandos."
    ),
    name="QRStudio",
    epilog=(
        """Ejemplos:\n
QRStudio generar \"https://tusitio.com\" --template ocean --salida mi_qr.png\n
QRStudio generar \"Mi QR\" --dark \"#0b0b0b\" --light \"#f2efe8\" --salida qr_custom\n
QRStudio leer mi_qr.png"""
    ),
)
console = Console()

TEMPLATES = {
    "ocean" : {"dark": "#0e3a5d", "light": "#d7f0ff"},
    "sunset": {"dark": "#5c1e1e", "light": "#ffe3c1"},
    "forest": {"dark": "#1f3b2f", "light": "#e7f3ea"},
    "mono"  : {"dark": "#111111", "light": "#ffffff"},
}

DARK_CHOICES = [
    ("Usar template", None),
    ("Negro #111111", "#111111"),
    ("Azul oceano #0e3a5d", "#0e3a5d"),
    ("Rojo sunset #5c1e1e", "#5c1e1e"),
    ("Verde forest #1f3b2f", "#1f3b2f"),
    ("Grafito #2c2c2c", "#2c2c2c"),
    ("Personalizado...", "custom"),
]

LIGHT_CHOICES = [
    ("Usar template", None),
    ("Blanco #ffffff", "#ffffff"),
    ("Celeste #d7f0ff", "#d7f0ff"),
    ("Durazno #ffe3c1", "#ffe3c1"),
    ("Verde claro #e7f3ea", "#e7f3ea"),
    ("Marfil #f2efe8", "#f2efe8"),
    ("Personalizado...", "custom"),
]

SCALE_CHOICES  = [6, 8, 10, 12]
BORDER_CHOICES = [1, 2, 3, 4]
LOGO_DIR       = Path("logos")
PANEL_MIN_WIDTH = 28
PANEL_MAX_WIDTH = 60
MENU_MIN_WIDTH = 28
MENU_MAX_WIDTH = 48


def _panel_width_for_text(text: str, min_width: int, max_width: int) -> int:
    lines = text.splitlines() or [""]
    content_width = max(len(line) for line in lines) + 4
    return min(max(content_width, min_width), max_width)


def _select_from_menu(title: str, options: list[str], msvcrt) -> int:
    """Renderiza un menu con Rich y devuelve la opcion elegida.

    Args:
        title   : Titulo del panel del menu.
        options : Lista de opciones visibles para el usuario.
        msvcrt  : Modulo msvcrt si esta disponible en Windows, o None.

    Returns:
        Indice de la opcion seleccionada.
    """
    selected = 0

    while True:
        console.clear()
        header = Panel(
            Text("QR Studio", style="bold white"),
            style="bold blue",
            width=MENU_MAX_WIDTH,
        )
        console.print(header)

        content_width = max([len(title)] + [len(opt) for opt in options]) + 4
        menu_width = min(max(content_width, MENU_MIN_WIDTH), MENU_MAX_WIDTH)

        menu = Table(show_header=False, box=None, pad_edge=False)
        for idx, label in enumerate(options):
            style  = "bold yellow" if idx == selected else "white"
            prefix = ">" if idx == selected else " "
            menu.add_row(f"{prefix} {label}", style=style)
        console.print(Panel(menu, title=title, border_style="green", width=menu_width))
        console.print("Usa flechas y Enter para elegir.")

        if msvcrt is None:
            choice = input("Elegi opcion (1-{max_opt}): ".format(max_opt=len(options))).strip()
            if choice.isdigit():
                selected = max(0, min(int(choice) - 1, len(options) - 1))
                return selected
            continue

        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):
            arrow = msvcrt.getch()
            if arrow == b"H":
                selected = (selected - 1) % len(options)
            elif arrow == b"P":
                selected = (selected + 1) % len(options)
        elif ch in (b"\r", b"\n"):
            return selected


def _ensure_logo_dir() -> Path:
    """Crea y devuelve el directorio de logos.

    Returns:
        Ruta de la carpeta donde se guardan los logos.
    """
    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    return LOGO_DIR


def _list_logo_files(logo_dir: Path) -> list[Path]:
    """Lista logos soportados dentro de una carpeta.

    Args:
        logo_dir: Carpeta donde se buscan logos.

    Returns:
        Lista de rutas a archivos con extensiones soportadas.
    """
    return sorted(
        [
            p
            for p in logo_dir.iterdir()
            if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"}
        ],
        key=lambda p: p.name.lower(),
    )


def _get_clipboard_text() -> str:
    """Obtiene texto del portapapeles de forma segura.

    Returns:
        Texto del portapapeles o cadena vacia si no esta disponible.
    """
    try:
        text = pyperclip.paste()
    except pyperclip.PyperclipException:
        return ""
    if not text:
        return ""
    return text.strip()


def _prompt_text_or_clipboard(msvcrt) -> str:
    """Permite elegir entre pegar del portapapeles o escribir manualmente.

    Args:
        msvcrt: Modulo msvcrt si esta disponible en Windows, o None.

    Returns:
        Texto final para el QR.
    """
    choice = ["Pegar del portapapeles", "Escribir texto/URL"]
    selected = _select_from_menu("Texto o URL", choice, msvcrt)
    if choice[selected] == "Pegar del portapapeles":
        clip_text = _get_clipboard_text()
        if not clip_text:
            console.print(
                Panel(
                    "Portapapeles vacio o inaccesible.",
                    border_style="red",
                    width=PANEL_MAX_WIDTH,
                )
            )
            return Prompt.ask("Texto o URL")
        preview = clip_text if len(clip_text) <= 200 else clip_text[:200] + "..."
        preview_width = _panel_width_for_text(preview, PANEL_MIN_WIDTH, PANEL_MAX_WIDTH)
        console.print(Panel(preview, title="Preview", border_style="cyan", width=preview_width))
        confirm = _select_from_menu("Usar este texto?", ["Si", "No"], msvcrt)
        if confirm == 0:
            return clip_text
    return Prompt.ask("Texto o URL")


def _ensure_png_extension(path: Path) -> Path:
    """Asegura extension PNG si falta en la salida.

    Args:
        path: Ruta de salida.

    Returns:
        Ruta con extension .png si faltaba.
    """
    if path.suffix:
        return path
    return path.with_suffix(".png")


def _interactive_menu(ctx: typer.Context) -> None:
    """Menu principal interactivo para generar o leer QRs.

    Args:
        ctx: Contexto de Typer para mostrar ayuda cuando se necesita.
    """
    try:
        import msvcrt
    except ImportError:
        msvcrt = None

    options = ["Generar QR", "Leer QR", "Ayuda", "Salir"]

    info = Text()
    info.append("Modos disponibles\n", style="bold")
    info.append("- Interactivo: ejecutar sin subcomando\n")
    info.append("- CLI: usar generar/leer\n\n")
    info.append("Ejemplo CLI:\n", style="bold")
    info.append("  QRStudio generar \"https://tusitio.com\" --salida mi_qr.png\n")
    info.append("  QRStudio leer mi_qr.png\n")
    info_width = _panel_width_for_text(info.plain, PANEL_MIN_WIDTH, PANEL_MAX_WIDTH)
    console.print(Panel(info, title="Ayuda rapida", border_style="yellow", width=info_width))
    input("Enter para abrir el menu...")

    while True:
        selected = _select_from_menu("Menu", options, msvcrt)

        if options[selected] == "Generar QR":
            texto = _prompt_text_or_clipboard(msvcrt)
            salida = typer.prompt("Salida", default="qr_output.png")

            template_idx = _select_from_menu("Template", list(TEMPLATES.keys()), msvcrt)
            template = list(TEMPLATES.keys())[template_idx]

            dark_idx = _select_from_menu("Color oscuro", [label for label, _ in DARK_CHOICES], msvcrt)
            dark_value = DARK_CHOICES[dark_idx][1]
            if dark_value == "custom":
                dark_value = typer.prompt("Color oscuro (hex)")

            light_idx = _select_from_menu("Color claro", [label for label, _ in LIGHT_CHOICES], msvcrt)
            light_value = LIGHT_CHOICES[light_idx][1]
            if light_value == "custom":
                light_value = typer.prompt("Color claro (hex)")

            logo_dir = _ensure_logo_dir()
            logo_files = _list_logo_files(logo_dir)
            logo_option = ["Placeholder", "Sin logo"] + [f"Logo: {p.name}" for p in logo_files]
            logo_idx = _select_from_menu("Logo", logo_option, msvcrt)
            if logo_option[logo_idx] == "Sin logo":
                logo_path = None
                sin_logo = True
            elif logo_option[logo_idx] == "Placeholder":
                logo_path = None
                sin_logo = False
            else:
                logo_path = logo_files[logo_idx - 2]
                sin_logo = False

            scale_idx = _select_from_menu("Escala", [str(x) for x in SCALE_CHOICES], msvcrt)
            escala = SCALE_CHOICES[scale_idx]

            border_idx = _select_from_menu("Borde", [str(x) for x in BORDER_CHOICES], msvcrt)
            borde = BORDER_CHOICES[border_idx]

            generar(
                texto    = texto,
                salida   =_ensure_png_extension(Path(salida)),
                template = template,
                dark     = dark_value,
                light    = light_value,
                logo     = logo_path,
                borde    = borde,
                escala   = escala,
                sin_logo = sin_logo,
            )
            input("Enter para volver al menu...")
        elif options[selected] == "Leer QR":
            imagen = typer.prompt("Ruta de imagen")
            leer(imagen=Path(imagen))
            input("Enter para volver al menu...")
        elif options[selected] == "Ayuda":
            console.print(ctx.get_help())
            input("Enter para volver al menu...")
        else:
            return


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Callback principal que abre el menu si no hay subcomando.

    Args:
        ctx: Contexto de Typer.
    """
    if ctx.invoked_subcommand is None:
        _interactive_menu(ctx)


def _resolve_colors(template: str, dark: Optional[str], light: Optional[str]) -> tuple[str, str]:
    """Resuelve colores finales segun template y overrides.

    Args:
        template : Nombre del template predefinido.
        dark     : Color oscuro opcional.
        light    : Color claro opcional.

    Returns:
        Tupla (dark, light) con los colores finales.
    """
    if template in TEMPLATES:
        colors = TEMPLATES[template]
        return dark or colors["dark"], light or colors["light"]
    return dark or "#111111", light or "#ffffff"


def _build_placeholder_logo(size: int) -> Image.Image:
    """Crea un logo simple de placeholder.

    Args:
        size: Tamano cuadrado del logo.

    Returns:
        Imagen RGBA con un placeholder basico.
    """
    logo = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(logo)
    
    draw.rectangle((0, 0, size - 1, size - 1), outline=(20, 20, 20, 255), width=3)
    
    font = ImageFont.load_default()
    text = "QR"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(((size - text_w) / 2, (size - text_h) / 2), text, fill=(20, 20, 20, 255), font=font)
    return logo


def _add_logo(qr_img: Image.Image, logo_path: Optional[Path], use_logo: bool) -> Image.Image:
    """Agrega el logo (o placeholder) al centro del QR.

    Args:
        qr_img: Imagen del QR en formato RGBA.
        logo_path: Ruta al logo elegido o None para placeholder.
        use_logo: Si es False, no se agrega logo.

    Returns:
        Imagen del QR con el logo aplicado.
    """
    if not use_logo:
        return qr_img

    qr_size = min(qr_img.size)
    logo_size = max(40, int(qr_size * 0.2))

    if logo_path and logo_path.exists():
        logo = _load_logo_image(logo_path)
        if logo is None:
            logo = _build_placeholder_logo(logo_size)
    else:
        logo = _build_placeholder_logo(logo_size)

    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
    pos = ((qr_img.size[0] - logo_size) // 2, (qr_img.size[1] - logo_size) // 2)
    qr_img.paste(logo, pos, logo)
    return qr_img


def _load_logo_image(logo_path: Path) -> Optional[Image.Image]:
    """Carga un logo desde PNG/JPG/WEBP o SVG si hay Cairo.

    Args:
        logo_path: Ruta del archivo de logo.

    Returns:
        Imagen RGBA cargada o None si falla.
    """
    try:
        if logo_path.suffix.lower() == ".svg":
            try:
                import cairosvg
            except Exception:
                console.print(
                    Panel(
                        "No se pudo cargar SVG porque falta Cairo. Usa PNG/JPG o instala Cairo.",
                        border_style = "red",
                        width        = PANEL_MAX_WIDTH,
                    )
                )
                return None
            png_bytes = cairosvg.svg2png(url=str(logo_path))
            return Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        return Image.open(logo_path).convert("RGBA")
    except Exception:
        console.print(
            Panel(
                "No se pudo cargar el logo. Se usara placeholder.",
                border_style = "red",
                width        = PANEL_MAX_WIDTH,
            )
        )
        return None


def _render_generate_dashboard(data: str, output_path: Path, dark: str, light: str, logo_path: Optional[Path]) -> None:
    """Renderiza el dashboard de generacion.

    Args:
        data        : Texto o URL codificado en el QR.
        output_path : Ruta de salida del QR generado.
        dark        : Color oscuro final.
        light       : Color claro final.
        logo_path   : Ruta del logo seleccionado o None.
    """
    layout = Layout()
    layout.split_column(Layout(name="header", size=3), Layout(name="body"))

    header_text = Text("QR Studio", style="bold white")
    layout["header"].update(Panel(header_text, style="bold blue", width=PANEL_MAX_WIDTH))

    table = Table(show_header=False, box=None)
    table.add_row("Texto", data)
    table.add_row("Salida", str(output_path))
    table.add_row("Colores", f"dark={dark}, light={light}")
    table.add_row("Logo", str(logo_path) if logo_path else "placeholder")
    layout["body"].update(Panel(table, title="Generacion", border_style="green", width=PANEL_MAX_WIDTH))

    console.print(layout)


def _render_read_dashboard(image_path: Path, results: list[str]) -> None:
    """Renderiza el dashboard de lectura.

    Args:
        image_path : Imagen analizada.
        results    : Lista de resultados decodificados.
    """
    layout = Layout()
    layout.split_column(Layout(name="header", size=3), Layout(name="body"))

    header_text = Text("QR Studio", style="bold white")
    layout["header"].update(Panel(header_text, style="bold magenta", width=PANEL_MAX_WIDTH))

    table = Table(show_header=True, header_style="bold")
    table.add_column("Imagen")
    table.add_column("Contenido")

    if results:
        for item in results:
            table.add_row(str(image_path), item)
    else:
        table.add_row(str(image_path), "No se encontraron QRs")

    layout["body"].update(Panel(table, title="Lectura", border_style="cyan", width=PANEL_MAX_WIDTH))

    console.print(layout)


@app.command(
    help=(
        "Genera un QR con colores, escala, borde y logo opcional.\n\n"
        "Ejemplos:\n"
        "  QRStudio generar \"https://tusitio.com\" --template ocean --salida mi_qr.png\n"
        "  QRStudio generar \"Mi QR\" --dark \"#0b0b0b\" --light \"#f2efe8\" --salida qr_custom\n"
        "  QRStudio generar \"Texto\" --borde 3 --escala 10 --sin-logo\n"
    )
)
def generar(
    texto: str           = typer.Argument(...,  help="Texto o URL para el QR."),
    salida: Path         = typer.Option(Path("qr_output.png"), "--salida", "-s", help="Ruta de salida PNG."),
    template: str        = typer.Option("mono", help = "Plantilla de color: ocean, sunset, forest, mono."),
    dark: Optional[str]  = typer.Option(None,   help = "Color oscuro (hex o nombre)."),
    light: Optional[str] = typer.Option(None,   help = "Color claro (hex o nombre)."),
    logo: Optional[Path] = typer.Option(None,   help = "Ruta a logo PNG con transparencia."),
    borde: int           = typer.Option(2,      help = "Borde del QR."),
    escala: int          = typer.Option(8,      help = "Escala del QR."),
    sin_logo: bool       = typer.Option(False, "--sin-logo", help="No agregar logo."),
) -> None:
    """Genera un QR con estilo, logo opcional y salida PNG.

    Args:
        texto    : Texto o URL a codificar.
        salida   : Ruta de salida del PNG.
        template : Template de colores predefinido.
        dark     : Color oscuro override.
        light    : Color claro override.
        logo     : Ruta del logo opcional.
        borde    : Borde del QR.
        escala   : Escala del QR.
        sin_logo : Si es True, no agrega logo.
    """
    salida = _ensure_png_extension(salida)
    dark_color, light_color = _resolve_colors(template, dark, light)

    try:
        qr = segno.make(texto, error="h")
    except segno.DataOverflowError:
        console.print(
            Panel(
                "El texto es demasiado largo para un QR. Probá acortarlo o usar un enlace mas corto.",
                border_style="red",
                title="Texto muy largo",
                width=PANEL_MAX_WIDTH,
            )
        )
        return
    buffer = io.BytesIO()
    qr.save(buffer, kind="png", scale=escala, border=borde, dark=dark_color, light=light_color)
    buffer.seek(0)

    img = Image.open(buffer).convert("RGBA")
    img = _add_logo(img, logo, not sin_logo)

    salida.parent.mkdir(parents=True, exist_ok=True)
    img.save(salida)

    _render_generate_dashboard(texto, salida, dark_color, light_color, logo)


@app.command(
    help=(
        "Lee un QR desde una imagen y muestra el contenido.\n\n"
        "Ejemplos:\n"
        "  QRStudio leer mi_qr.png\n"
        "  QRStudio leer .\\carpeta\\qr_custom.png\n"
    )
)
def leer(
    imagen: Path = typer.Argument(..., help="Imagen PNG/JPG con QR."),
) -> None:
    """Lee QRs desde una imagen y muestra el resultado.

    Args:
        imagen: Ruta de la imagen a analizar.
    """
    if not imagen.exists():
        raise typer.BadParameter("La imagen no existe.")

    img = Image.open(imagen).convert("RGB")
    decoded = decode(img)
    results = [item.data.decode("utf-8", errors="replace") for item in decoded]

    _render_read_dashboard(imagen, results)


if __name__ == "__main__":
    app(prog_name="QRStudio")
