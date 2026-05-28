"""Convert Markdown resumes to styled PDF and DOCX."""

__version__ = "1.0.0"

from md2resume.builder import build_html_document
from md2resume.styles import STYLES, resolve_style_id

__all__ = ["STYLES", "build_html_document", "resolve_style_id", "__version__"]
