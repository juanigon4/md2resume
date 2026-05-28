"""HTML layout transforms."""

from __future__ import annotations

import re

from md2resume.constants import SIDEBAR_SECTION_KEYWORDS, LayoutType

def _split_sections(html: str) -> tuple[str, list[str]]:
    """Return (header before first h2, list of h2-section chunks)."""
    first_h2 = re.search(r"<h2[\s>]", html, re.IGNORECASE)
    if not first_h2:
        return html, []
    header = html[: first_h2.start()]
    rest = html[first_h2.start() :]
    sections = re.findall(r"<h2[\s>].*?(?=(?:<h2[\s>])|$)", rest, re.DOTALL | re.IGNORECASE)
    return header, sections


def apply_enhancv_sidebar_layout(html: str) -> str:
    return apply_sidebar_layout(html, layout_class="sidebar-left enhancv")


def apply_header_bar(html: str) -> str:
    pattern = _identity_block_pattern()
    match = pattern.search(html)
    if not match:
        return html
    wrapped = f'<header class="resume-header-bar">{match.group(0)}</header>'
    return html[: match.start()] + wrapped + html[match.end() :]


def apply_photo_header_layout(html: str) -> str:
    header, sections = _split_sections(html)
    if not sections:
        return html
    header = clean_header_block(header)
    body_parts = [f'<section class="resume-section">{s}</section>' for s in sections]
    return (
        '<div class="layout-photo-header">'
        f'<div class="resume-header-panel">{header}</div>'
        f'<div class="resume-body">{"".join(body_parts)}</div>'
        "</div>"
    )


def apply_classic_layout(html: str) -> str:
    header, sections = _split_sections(html)
    if not sections:
        return html
    body_parts = [f'<section class="resume-section">{s}</section>' for s in sections]
    return f'{header}<div class="resume-body">{"".join(body_parts)}</div>'


def apply_sidebar_layout(html: str, *, layout_class: str = "sidebar-left") -> str:
    header, sections = _split_sections(html)
    if not sections:
        return html

    header = clean_header_block(header)
    sidebar_parts: list[str] = []
    main_parts: list[str] = []

    for section in sections:
        h2_match = re.search(r"<h2[\s>].*?</h2>", section, re.DOTALL | re.IGNORECASE)
        h2_html = h2_match.group(0) if h2_match else ""
        wrapped = f'<section class="resume-section">{section}</section>'
        if _is_sidebar_section(h2_html):
            sidebar_parts.append(wrapped)
        else:
            if "experience" in _strip_html_tags(h2_html) or "work" in _strip_html_tags(h2_html):
                wrapped = wrapped.replace(
                    'class="resume-section"',
                    'class="resume-section timeline"',
                    1,
                )
            main_parts.append(wrapped)

    return (
        f'<div class="resume-layout {layout_class}">'
        f'<aside class="resume-sidebar"><div class="sidebar-identity">{header}</div>{"".join(sidebar_parts)}</aside>'
        f'<main class="resume-main">{"".join(main_parts)}</main>'
        "</div>"
    )


def apply_ats_sections_layout(html: str) -> str:
    header, sections = _split_sections(html)
    if not sections:
        return html
    header = clean_header_block(header)
    body_parts = [f'<section class="resume-section">{s}</section>' for s in sections]
    return f'{header}<div class="resume-body ats-sections">{"".join(body_parts)}</div>'


def _is_sidebar_section(h2_html: str) -> bool:
    title = _strip_html_tags(h2_html)
    return any(keyword in title for keyword in SIDEBAR_SECTION_KEYWORDS)


def clean_header_block(header: str) -> str:
    """Remove markdown horizontal rules from the header area."""
    return re.sub(r"\s*<hr\s*/?>\s*", "\n", header, flags=re.IGNORECASE)


def wrap_contact_block(html: str) -> str:
    """Wrap lines between <h1> and first <h2>/<hr> in a contact div."""
    pattern = re.compile(
        r"(<h1>.*?</h1>)(\s*(?:<p>.*?</p>\s*)+)(?=<h2>|<hr)",
        re.DOTALL | re.IGNORECASE,
    )
    return pattern.sub(r'\1\n<div class="contact">\2</div>\n', html, count=1)


def _strip_html_tags(fragment: str) -> str:
    return re.sub(r"<[^>]+>", "", fragment).strip().lower()


def apply_timeline_layout(html: str) -> str:
    header, sections = _split_sections(html)
    header = clean_header_block(header)
    body_parts: list[str] = []
    for section in sections:
        h2_match = re.search(r"<h2[\s>].*?</h2>", section, re.DOTALL | re.IGNORECASE)
        h2_html = h2_match.group(0) if h2_match else ""
        title = _strip_html_tags(h2_html)
        css_class = "resume-section"
        if "experience" in title or "work" in title:
            css_class += " timeline"
        body_parts.append(f'<section class="{css_class}">{section}</section>')
    return f'<div class="resume-body">{header}{"".join(body_parts)}</div>'


def structure_resume_html(html: str, layout: LayoutType) -> str:
    if layout == "split_header":
        html = apply_split_header(html)
    elif layout == "header_bar":
        html = apply_header_bar(html)
    elif layout == "sidebar_left":
        html = apply_sidebar_layout(html)
    elif layout == "enhancv_sidebar":
        html = apply_enhancv_sidebar_layout(html)
    elif layout == "photo_header":
        html = apply_photo_header_layout(html)
    elif layout == "ats_sections":
        html = apply_ats_sections_layout(html)
    elif layout == "timeline":
        html = apply_timeline_layout(html)
    elif layout == "classic":
        html = apply_classic_layout(html)
    return html


def _identity_block_pattern() -> re.Pattern[str]:
    """Match h1+contact, optionally wrapped in resume-identity."""
    return re.compile(
        r'(?:<div class="resume-identity">.*?<div class="resume-identity-text">)?'
        r'(<h1>.*?</h1>\s*<div class="contact">.*?</div>)'
        r"(?:</div>\s*</div>)?",
        re.DOTALL | re.IGNORECASE,
    )


def apply_split_header(html: str) -> str:
    """Name and contact in one row; photo/QR sits left of the name when enabled."""
    pattern = _identity_block_pattern()
    match = pattern.search(html)
    if not match:
        return html
    block_html = match.group(0)
    if "resume-identity" not in block_html:
        block_html = f'<div class="resume-identity-text">{match.group(1)}</div>'
    block = f'<div class="resume-top">{block_html}</div>'
    return html[: match.start()] + block + html[match.end() :]
