"""Data models for resume export."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from md2resume.constants import LayoutType, QrChoice

@dataclass(frozen=True)
class ResumeStyle:
    id: str
    label: str
    description: str
    layout: LayoutType
    primary: str
    secondary: str
    accent: str
    text: str
    muted: str
    surface: str
    border: str
    heading_font: str
    body_font: str
    h1_size: str
    h2_size: str
    h3_size: str
    body_size: str
    line_height: str
    section_uppercase: bool


@dataclass
class HeaderOptions:
    photo_path: Path | None = None
    qr_choice: QrChoice = "none"
    qr_url: str | None = None
