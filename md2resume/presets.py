"""Page layout presets."""

from md2resume.constants import Density, PageSize

DENSITY_PRESETS: dict[Density, dict[str, str]] = {
    "compact": {
        "page_margin": "0.55in 0.65in",
        "section_gap": "8pt",
        "list_gap": "1pt",
        "h1_margin_bottom": "4pt",
    },
    "standard": {
        "page_margin": "0.65in 0.75in",
        "section_gap": "11pt",
        "list_gap": "2pt",
        "h1_margin_bottom": "6pt",
    },
    "spacious": {
        "page_margin": "0.75in 0.85in",
        "section_gap": "14pt",
        "list_gap": "4pt",
        "h1_margin_bottom": "8pt",
    },
}

PAGE_SIZES: dict[PageSize, str] = {
    "letter": "letter",
    "a4": "A4",
}

