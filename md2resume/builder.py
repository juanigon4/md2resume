"""Markdown to HTML resume builder."""

from __future__ import annotations

import markdown

from md2resume.constants import Density, PageSize
from md2resume.header import extract_profile_links, inject_header_extras, normalize_html_attributes
from md2resume.layouts import structure_resume_html, wrap_contact_block
from md2resume.models import HeaderOptions, ResumeStyle
from md2resume.template import render_document


def build_html_document(
    md_text: str,
    style: ResumeStyle,
    density: Density,
    page_size: PageSize,
    title: str,
    header_options: HeaderOptions,
) -> str:
    body_html = markdown_to_html(md_text, style, header_options)
    return render_document(body_html, style, density, page_size, title)

def markdown_to_html(
    md_text: str,
    style: ResumeStyle,
    header_options: HeaderOptions,
) -> str:
    profile_links = extract_profile_links(md_text)
    body = markdown.markdown(
        md_text,
        extensions=["extra", "nl2br", "sane_lists"],
    )
    body = normalize_html_attributes(wrap_contact_block(body))
    body = inject_header_extras(body, header_options, profile_links)
    return structure_resume_html(body, style.layout)
