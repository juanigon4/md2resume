"""HTML document template."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from md2resume.constants import Density, PageSize
from md2resume.models import HeaderOptions, ResumeStyle
from md2resume.presets import DENSITY_PRESETS, PAGE_SIZES

_TEMPLATE_PATH = Path(__file__).parent / "templates" / "document.html"
HTML_TEMPLATE = Template(_TEMPLATE_PATH.read_text(encoding="utf-8"))


def render_document(
    body_html: str,
    style: ResumeStyle,
    density: Density,
    page_size: PageSize,
    title: str,
) -> str:
    return HTML_TEMPLATE.render(
        title=title,
        body_html=body_html,
        style=style,
        density=DENSITY_PRESETS[density],
        page_size=PAGE_SIZES[page_size],
        page_margin=DENSITY_PRESETS[density]["page_margin"],
    )
