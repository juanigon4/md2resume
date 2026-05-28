"""PDF and DOCX export backends."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from md2resume.constants import PageSize

def export_pdf_pandoc(md_path: Path, output_path: Path) -> None:
    subprocess.run(
        ["pandoc", str(md_path), "-o", str(output_path)],
        check=True,
        capture_output=True,
    )


def export_pdf_weasyprint(html: str, output_path: Path) -> None:
    from weasyprint import HTML

    HTML(string=html).write_pdf(str(output_path))


def export_pdf(
    html: str,
    output_path: Path,
    md_path: Path,
    page_size: PageSize,
) -> str:
    """Try PDF backends in order; return which backend succeeded."""
    errors: list[str] = []

    try:
        export_pdf_playwright(html, output_path, page_size)
        return "playwright (Chromium)"
    except Exception as err:
        errors.append(f"playwright: {err}")

    try:
        export_pdf_weasyprint(html, output_path)
        return "weasyprint"
    except ImportError:
        errors.append("weasyprint: not installed (pip install weasyprint)")
    except Exception as err:
        errors.append(f"weasyprint: {err}")

    if shutil.which("pandoc"):
        try:
            export_pdf_pandoc(md_path, output_path)
            return "pandoc"
        except subprocess.CalledProcessError as err:
            errors.append(f"pandoc: {err.stderr.decode() if err.stderr else err}")

    hint = (
        "Install Chromium for PDF export: pip install playwright && playwright install chromium"
    )
    raise RuntimeError(f"Could not generate PDF.\n{hint}\n\n" + "\n".join(errors))


def export_pdf_playwright(html: str, output_path: Path, page_size: PageSize) -> None:
    from playwright.sync_api import sync_playwright

    pdf_format = "Letter" if page_size == "letter" else "A4"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(
            path=str(output_path),
            format=pdf_format,
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()


def export_docx_htmldocx(html: str, output_path: Path) -> None:
    from htmldocx import HtmlToDocx

    parser = HtmlToDocx()
    # htmldocx expects body fragment; strip full document wrapper
    body_match = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
    fragment = body_match.group(1) if body_match else html
    parser.parse_html_string(fragment)
    parser.doc.save(str(output_path))


def export_docx_pandoc(md_path: Path, output_path: Path, reference_docx: Path | None) -> bool:
    if not shutil.which("pandoc"):
        return False
    cmd = [
        "pandoc",
        str(md_path),
        "-f",
        "markdown",
        "-t",
        "docx",
        "-o",
        str(output_path),
    ]
    if reference_docx and reference_docx.is_file():
        cmd.extend(["--reference-doc", str(reference_docx)])
    subprocess.run(cmd, check=True, capture_output=True)
    return True
