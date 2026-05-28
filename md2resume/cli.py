"""Command-line interface."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

import questionary
from rich.panel import Panel

from md2resume.builder import build_html_document
from md2resume.constants import Density, FormatChoice, PageSize
from md2resume.console import console
from md2resume.exporters import export_docx_htmldocx, export_docx_pandoc, export_pdf
from md2resume.header import configure_header_options
from md2resume.paths import resolve_output_paths, run_setup
from md2resume.presets import DENSITY_PRESETS, PAGE_SIZES
from md2resume.styles import STYLES, LEGACY_STYLE_MAP, resolve_style_id

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a Markdown resume to DOCX and/or PDF.",
    )
    parser.add_argument(
        "markdown_file",
        type=Path,
        nargs="?",
        help="Path to the .md resume file",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for output files (default: same folder as input)",
    )
    style_choices = list(STYLES.keys()) + list(LEGACY_STYLE_MAP.keys())
    parser.add_argument(
        "--style",
        "--theme",
        dest="style",
        choices=style_choices,
        help="Document style / layout (skips style prompt when --no-interactive)",
    )
    parser.add_argument(
        "--density",
        choices=list(DENSITY_PRESETS.keys()),
        help="Spacing preset: compact, standard, or spacious",
    )
    parser.add_argument(
        "--page-size",
        choices=list(PAGE_SIZES.keys()),
        dest="page_size",
        help="Paper size: letter or a4",
    )
    parser.add_argument(
        "--format",
        choices=["docx", "pdf", "both"],
        dest="output_format",
        help="Output format(s)",
    )
    parser.add_argument(
        "-n",
        "--output-name",
        "--basename",
        dest="output_name",
        metavar="NAME",
        help="Output file name (stem, or path; .pdf/.docx optional for single-format export)",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Use defaults or only CLI flags (no prompts)",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Install Playwright Chromium (required once for PDF export)",
    )
    parser.add_argument(
        "--photo",
        type=Path,
        metavar="PATH",
        help="Profile photo (jpg, png, webp)",
    )
    parser.add_argument(
        "--no-photo",
        action="store_true",
        help="Do not include a profile photo",
    )
    parser.add_argument(
        "--qr",
        choices=["none", "linkedin", "github", "custom"],
        help="QR code target (URLs taken from markdown links when omitted)",
    )
    parser.add_argument(
        "--qr-url",
        metavar="URL",
        help="Custom URL for QR code (use with --qr custom)",
    )
    return parser.parse_args()


def interactive_config(
    args: argparse.Namespace,
    default_stem: str,
    md_text: str,
) -> dict:
    console.print(
        Panel(
            "[bold]Resume export[/bold]\n"
            "Choose a layout (placement) with a restrained navy / gray palette.",
            border_style="blue",
        )
    )

    style_id = resolve_style_id(args.style)
    if not args.style:
        choices = [
            questionary.Choice(
                title=f"{s.label} — {s.description}",
                value=s.id,
            )
            for s in STYLES.values()
        ]
        style_id = questionary.select("Document style:", choices=choices).ask()
        if style_id is None:
            sys.exit(0)

    density: Density = args.density or questionary.select(
        "Spacing:",
        choices=[
            questionary.Choice("Compact — fit more on one page", "compact"),
            questionary.Choice("Standard — balanced", "standard"),
            questionary.Choice("Spacious — easier to scan", "spacious"),
        ],
    ).ask()
    if density is None:
        sys.exit(0)

    page_size: PageSize = args.page_size or questionary.select(
        "Paper size:",
        choices=[
            questionary.Choice("US Letter", "letter"),
            questionary.Choice("A4", "a4"),
        ],
    ).ask()
    if page_size is None:
        sys.exit(0)

    output_format: FormatChoice = args.output_format or questionary.select(
        "Output format:",
        choices=[
            questionary.Choice("PDF only", "pdf"),
            questionary.Choice("Word (.docx) only", "docx"),
            questionary.Choice("Both PDF and Word", "both"),
        ],
    ).ask()
    if output_format is None:
        sys.exit(0)

    output_name = args.output_name
    if not output_name:
        output_name = questionary.text(
            "Output file name:",
            default=default_stem,
            instruction="stem or path; add .pdf/.docx for single-format export",
        ).ask()
        if output_name is None:
            sys.exit(0)
        output_name = output_name.strip() or default_stem

    use_pandoc = False
    if output_format in ("docx", "both") and shutil.which("pandoc"):
        use_pandoc = questionary.confirm(
            "Pandoc is installed. Use it for DOCX? (Often better fidelity; styling comes from the HTML/CSS path if you decline)",
            default=True,
        ).ask()
        if use_pandoc is None:
            sys.exit(0)

    header_options = configure_header_options(args, md_text, interactive=True)

    return {
        "style_id": style_id,
        "density": density,
        "page_size": page_size,
        "output_format": output_format,
        "output_name": output_name,
        "use_pandoc_docx": use_pandoc,
        "header_options": header_options,
    }


def main() -> int:
    args = parse_args()
    if args.setup:
        return run_setup()

    if not args.markdown_file:
        console.print("[red]Error:[/red] markdown_file is required.")
        return 1

    md_path = args.markdown_file.expanduser().resolve()

    if not md_path.is_file():
        console.print(f"[red]File not found:[/red] {md_path}")
        return 1
    if md_path.suffix.lower() != ".md":
        console.print("[yellow]Warning:[/yellow] input is not a .md file; continuing anyway.")

    default_stem = md_path.stem
    md_text = md_path.read_text(encoding="utf-8")

    config = (
        non_interactive_config(args, md_text)
        if args.no_interactive
        else interactive_config(args, default_stem, md_text)
    )

    style_id = resolve_style_id(config["style_id"])
    if style_id not in STYLES:
        console.print(f"[red]Unknown style:[/red] {style_id}")
        return 1
    style = STYLES[style_id]
    density: Density = config["density"]
    page_size: PageSize = config["page_size"]
    output_format: FormatChoice = config["output_format"]
    output_name: str | None = config.get("output_name")
    header_options: HeaderOptions = config["header_options"]

    output_dir = (args.output_dir or md_path.parent).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    title_match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else default_stem

    try:
        html = build_html_document(
            md_text, style, density, page_size, title, header_options
        )
    except (FileNotFoundError, ValueError) as err:
        console.print(f"[red]Error:[/red] {err}")
        return 1

    pdf_path, docx_path = resolve_output_paths(
        output_name,
        default_stem,
        output_dir,
        output_format,
    )

    extras: list[str] = []
    if header_options.photo_path:
        extras.append("photo")
    if header_options.qr_choice != "none":
        extras.append(f"QR→{header_options.qr_choice}")
    extras_note = f"  [dim]Extras:[/dim] {', '.join(extras)}" if extras else ""

    console.print(
        f"\n[dim]Style:[/dim] {style.label}  [dim]Spacing:[/dim] {density}  "
        f"[dim]Paper:[/dim] {page_size}{extras_note}"
    )
    if pdf_path:
        console.print(f"[dim]PDF:[/dim] {pdf_path}")
    if docx_path:
        console.print(f"[dim]DOCX:[/dim] {docx_path}")

    try:
        if output_format in ("pdf", "both"):
            console.print("[cyan]Generating PDF…[/cyan]")
            pdf_backend = export_pdf(html, pdf_path, md_path, page_size)
            console.print(f"  [green]✓[/green] {pdf_path} [dim]({pdf_backend})[/dim]")

        if output_format in ("docx", "both"):
            console.print("[cyan]Generating DOCX…[/cyan]")
            wrote_docx = False
            if config["use_pandoc_docx"]:
                try:
                    wrote_docx = export_docx_pandoc(md_path, docx_path, reference_docx=None)
                    if wrote_docx:
                        console.print(f"  [green]✓[/green] {docx_path} [dim](via pandoc)[/dim]")
                except subprocess.CalledProcessError as err:
                    console.print(f"  [yellow]Pandoc failed ({err}); falling back to HTML→DOCX[/yellow]")
                    wrote_docx = False

            if not wrote_docx:
                export_docx_htmldocx(html, docx_path)
                console.print(f"  [green]✓[/green] {docx_path} [dim](styled HTML→DOCX)[/dim]")

    except RuntimeError as err:
        console.print(f"[red]Error:[/red] {err}")
        return 1
    except Exception as err:
        console.print(f"[red]Export failed:[/red] {err}")
        return 1

    console.print("\n[bold green]Done.[/bold green] Ready to attach or upload.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


def non_interactive_config(args: argparse.Namespace, md_text: str) -> dict:
    return {
        "style_id": resolve_style_id(args.style),
        "density": args.density or "standard",
        "page_size": args.page_size or "letter",
        "output_format": args.output_format or "both",
        "output_name": args.output_name,
        "use_pandoc_docx": bool(shutil.which("pandoc")),
        "header_options": configure_header_options(args, md_text, interactive=False),
    }
