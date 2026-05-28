"""Output path resolution and setup."""

from __future__ import annotations

import subprocess
import sys

from pathlib import Path

from md2resume.constants import FormatChoice
from md2resume.console import console

def run_setup() -> int:
    console.print("[cyan]Installing Playwright Chromium…[/cyan]")
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
        )
    except subprocess.CalledProcessError:
        console.print("[red]Setup failed.[/red] Try: playwright install chromium")
        return 1
    console.print("[green]Setup complete.[/green] You can export PDFs now.")
    return 0


def resolve_output_paths(
    output_name: str | None,
    default_stem: str,
    output_dir: Path,
    output_format: FormatChoice,
) -> tuple[Path | None, Path | None]:
    """
    Build PDF/DOCX paths from user input.

    Accepts a stem (MyResume), a path (~/Desktop/MyResume), or a file name
    with extension when exporting a single format (MyResume.pdf).
    """
    pdf_path: Path | None = None
    docx_path: Path | None = None
    stem = default_stem
    base_dir = output_dir

    if output_name and output_name.strip():
        user_path = Path(output_name.strip()).expanduser()
        has_parent = user_path.parent != Path(".")
        base_dir = user_path.parent.resolve() if has_parent else output_dir
        suffix = user_path.suffix.lower()

        if suffix == ".pdf":
            stem = user_path.stem
            if output_format == "pdf":
                pdf_path = (
                    user_path.resolve()
                    if user_path.is_absolute()
                    else (base_dir / user_path.name).resolve()
                )
        elif suffix == ".docx":
            stem = user_path.stem
            if output_format == "docx":
                docx_path = (
                    user_path.resolve()
                    if user_path.is_absolute()
                    else (base_dir / user_path.name).resolve()
                )
        else:
            stem = user_path.name

    if pdf_path is None and output_format in ("pdf", "both"):
        pdf_path = (base_dir / f"{stem}.pdf").resolve()
    if docx_path is None and output_format in ("docx", "both"):
        docx_path = (base_dir / f"{stem}.docx").resolve()

    base_dir.mkdir(parents=True, exist_ok=True)
    if pdf_path:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if docx_path:
        docx_path.parent.mkdir(parents=True, exist_ok=True)

    return pdf_path, docx_path
