"""Shared constants and type aliases."""

from typing import Literal

QrChoice = Literal["none", "linkedin", "github", "custom"]
FormatChoice = Literal["docx", "pdf", "both"]
PageSize = Literal["letter", "a4"]
Density = Literal["compact", "standard", "spacious"]

PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

LayoutType = Literal[
    "classic",
    "split_header",
    "sidebar_left",
    "enhancv_sidebar",
    "timeline",
    "minimal",
    "header_bar",
    "photo_header",
    "ats_sections",
]

SIDEBAR_SECTION_KEYWORDS = (
    "education",
    "certification",
    "technologies",
    "skills",
    "technical",
    "competenc",
    "languages",
    "profile",
)
