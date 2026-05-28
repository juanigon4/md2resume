"""Profile photo and QR code handling."""

from __future__ import annotations

import argparse
import base64
import io
import re
import sys
from pathlib import Path

import questionary

from md2resume.constants import PHOTO_EXTENSIONS, QrChoice
from md2resume.models import HeaderOptions
from md2resume.console import console

def build_media_html(options: HeaderOptions, profile_links: dict[str, str]) -> str:
    parts: list[str] = []

    if options.photo_path and options.photo_path.is_file():
        uri = image_to_data_uri(options.photo_path)
        parts.append(f'<div class="resume-photo"><img src="{uri}" alt="Profile photo"/></div>')

    qr_url = resolve_qr_url(options, profile_links)
    if qr_url:
        uri = generate_qr_data_uri(qr_url)
        label = {"linkedin": "LinkedIn", "github": "GitHub", "custom": "Profile"}.get(
            options.qr_choice, "Link"
        )
        parts.append(
            f'<div class="resume-qr">'
            f'<img src="{uri}" alt="QR code"/>'
            f'<span class="resume-qr-label">{label}</span></div>'
        )

    if not parts:
        return ""
    return f'<div class="resume-media">{"".join(parts)}</div>'


def resolve_qr_url(options: HeaderOptions, profile_links: dict[str, str]) -> str | None:
    if options.qr_choice == "none":
        return None
    if options.qr_choice == "custom":
        return options.qr_url
    return profile_links.get(options.qr_choice)


def generate_qr_data_uri(url: str) -> str:
    import qrcode

    qr = qrcode.QRCode(version=None, box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1e293b", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('ascii')}"


def configure_header_options(
    args: argparse.Namespace,
    md_text: str,
    *,
    interactive: bool,
) -> HeaderOptions:
    profile_links = extract_profile_links(md_text)

    photo_path: Path | None = None
    if args.no_photo:
        photo_path = None
    elif args.photo:
        photo_path = resolve_photo_path(args.photo)
    elif interactive:
        use_photo = questionary.confirm("Include a profile photo?", default=False).ask()
        if use_photo is None:
            sys.exit(0)
        if use_photo:
            raw = questionary.path(
                "Photo file path:",
                only_directories=False,
            ).ask()
            if raw is None:
                sys.exit(0)
            if raw.strip():
                photo_path = resolve_photo_path(Path(raw.strip()))

    qr_choice: QrChoice = "none"
    qr_url: str | None = None

    if args.qr:
        qr_choice = args.qr  # type: ignore[assignment]
        if qr_choice == "custom":
            qr_url = args.qr_url
    elif interactive:
        qr_choices = [
            questionary.Choice("No QR code", "none"),
        ]
        if profile_links.get("linkedin"):
            qr_choices.append(
                questionary.Choice(
                    f"LinkedIn — {profile_links['linkedin']}",
                    "linkedin",
                )
            )
        if profile_links.get("github"):
            qr_choices.append(
                questionary.Choice(
                    f"GitHub — {profile_links['github']}",
                    "github",
                )
            )
        qr_choices.append(questionary.Choice("Custom URL", "custom"))

        picked = questionary.select("QR code (optional):", choices=qr_choices).ask()
        if picked is None:
            sys.exit(0)
        qr_choice = picked  # type: ignore[assignment]
        if qr_choice == "custom":
            qr_url = questionary.text("QR code URL:").ask()
            if qr_url is None:
                sys.exit(0)
            qr_url = qr_url.strip() or None
    elif args.qr_url:
        qr_choice = "custom"
        qr_url = args.qr_url

    if qr_choice == "custom" and not qr_url:
        raise ValueError("Custom QR requires --qr-url or entering a URL interactively.")
    if qr_choice in ("linkedin", "github") and qr_choice not in profile_links:
        if not interactive:
            console.print(
                f"[yellow]No {qr_choice} link in markdown; QR skipped.[/yellow]"
            )
            qr_choice = "none"

    return HeaderOptions(photo_path=photo_path, qr_choice=qr_choice, qr_url=qr_url)


def extract_profile_links(md_text: str) -> dict[str, str]:
    """Find LinkedIn and GitHub URLs in markdown link syntax."""
    links: dict[str, str] = {}
    for match in re.finditer(r"\[[^\]]*\]\((https?://[^)]+)\)", md_text, re.IGNORECASE):
        url = match.group(1).strip()
        lower = url.lower()
        if "linkedin.com" in lower and "linkedin" not in links:
            links["linkedin"] = url
        elif "github.com" in lower and "github" not in links:
            links["github"] = url
    return links


def inject_header_extras(html: str, options: HeaderOptions, profile_links: dict[str, str]) -> str:
    media_html = build_media_html(options, profile_links)
    if not media_html:
        return html

    pattern = re.compile(
        r'(<h1>.*?</h1>\s*<div class="contact">.*?</div>)',
        re.DOTALL | re.IGNORECASE,
    )
    replacement = (
        '<div class="resume-identity">'
        + media_html
        + r'<div class="resume-identity-text">\1</div></div>'
    )
    return pattern.sub(replacement, html, count=1)


def resolve_photo_path(path: Path | None) -> Path | None:
    if path is None:
        return None
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Photo not found: {resolved}")
    if resolved.suffix.lower() not in PHOTO_EXTENSIONS:
        raise ValueError(
            f"Unsupported photo format: {resolved.suffix}. Use: {', '.join(PHOTO_EXTENSIONS)}"
        )
    return resolved


def normalize_html_attributes(html: str) -> str:
    """Fix accidental backslash-escaped quotes in generated HTML."""
    return html.replace('class=\\"', 'class="').replace("\\'>", "'>")


def image_to_data_uri(path: Path) -> str:
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime = mime_map.get(path.suffix.lower(), "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"
