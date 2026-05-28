# md2resume

Convert a Markdown resume to styled **PDF** and/or **DOCX**. Choose a document layout, spacing, paper size, optional profile photo, and optional QR code (LinkedIn, GitHub, or custom URL).

## Table of contents

- [Requirements](#requirements)
- [Install (local)](#install-local)
- [Quick start](#quick-start)
- [Command reference](#command-reference)
- [Interactive mode](#interactive-mode)
- [Non-interactive mode](#non-interactive-mode)
- [Document styles](#document-styles)
- [Profile photo](#profile-photo)
- [QR code](#qr-code)
- [Output files](#output-files)
- [Export engines](#export-engines)
- [Markdown format](#markdown-format)
- [Docker](#docker)
  - [Interactive CLI in Docker](#interactive-cli-in-docker)
  - [Shell inside the container](#shell-inside-the-container)
  - [Non-interactive Docker](#non-interactive-docker)
  - [Docker Compose](#docker-compose)
- [Project layout](#project-layout)
- [Troubleshooting](#troubleshooting)

---

## Requirements

- **Python 3.9+** (local install)
- **Chromium** for PDF export — installed via `python -m md2resume --setup` (Playwright)
- **Optional:** [Pandoc](https://pandoc.org/) for an alternate DOCX path (better structural fidelity, less CSS styling)

---

## Install (local)

```bash
cd md2resume
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m md2resume --setup        # one-time: downloads Chromium for PDF
```

---

## Quick start

**Interactive** (prompts for style, format, photo, QR, etc.):

```bash
python -m md2resume path/to/resume.md
```

**Non-interactive** (all options on the command line):

```bash
python -m md2resume resume.md \
  --no-interactive \
  --style enhancv_it \
  --format pdf \
  --photo headshot.jpg \
  --qr linkedin \
  -n My_Resume
```

---

## Command reference

```
usage: md2resume [-h] [-o OUTPUT_DIR] [--style STYLE] [--density {compact,standard,spacious}]
                 [--page-size {letter,a4}] [--format {docx,pdf,both}] [-n NAME]
                 [--no-interactive] [--setup] [--photo PATH] [--no-photo]
                 [--qr {none,linkedin,github,custom}] [--qr-url URL]
                 [markdown_file]
```

| Argument / flag | Description |
|-----------------|-------------|
| `markdown_file` | Path to the input `.md` resume. Required except when using `--setup`. |
| `-h`, `--help` | Show help and exit. |
| `--setup` | Install Playwright Chromium (PDF). Does not require `markdown_file`. |
| `--no-interactive` | Skip all prompts; use CLI flags and [non-interactive defaults](#non-interactive-defaults). |
| `--style`, `--theme` | Document style ID (see [Document styles](#document-styles)). In interactive mode, skips the style prompt if set. |
| `--density` | Page spacing: `compact`, `standard`, or `spacious`. |
| `--page-size` | Paper size: `letter` (US) or `a4`. |
| `--format` | Output type: `pdf`, `docx`, or `both`. |
| `-o`, `--output-dir` | Directory for generated files. Default: same directory as the input `.md` file. |
| `-n`, `--output-name`, `--basename` | Output base name or path (see [Output files](#output-files)). |
| `--photo` | Path to a profile photo (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`). |
| `--no-photo` | Do not include a photo (overrides interactive photo prompt). |
| `--qr` | QR code target: `none`, `linkedin`, `github`, or `custom`. |
| `--qr-url` | URL encoded in the QR when `--qr custom` (required for custom in non-interactive mode). |

**Entry points** (equivalent):

```bash
python -m md2resume [options] resume.md
```

---

## Interactive mode

Run without `--no-interactive`. You can pass some flags upfront; anything omitted is asked interactively.

**Prompt order:**

1. **Document style** — unless `--style` is set  
2. **Spacing** — `compact` / `standard` / `spacious` — unless `--density` is set  
3. **Paper size** — `letter` / `a4` — unless `--page-size` is set  
4. **Output format** — `pdf` / `docx` / `both` — unless `--format` is set  
5. **Output file name** — default: input file stem — unless `-n` is set  
6. **Pandoc for DOCX?** — only if `pandoc` is on `PATH` and format is `docx` or `both`  
7. **Include a profile photo?** — unless `--photo` or `--no-photo`  
8. **Photo path** — if yes  
9. **QR code** — `none`, LinkedIn, GitHub (if links exist in the markdown), or custom URL  

Canceling a prompt (e.g. Ctrl+C) exits cleanly.

**Example** (style preset, rest interactive):

```bash
python -m md2resume resume.md --style sidebar_navy
```

---

## Non-interactive mode

Use `--no-interactive` for scripts, CI, and Docker without a TTY.

### Non-interactive defaults

When a flag is omitted:

| Setting | Default |
|---------|---------|
| Style | `classic_navy` |
| Density | `standard` |
| Page size | `letter` |
| Format | `both` (PDF + DOCX) |
| Output name | Input file stem (e.g. `resume` from `resume.md`) |
| Output directory | Same folder as the `.md` file |
| Photo | None |
| QR | `none` |
| DOCX engine | Pandoc if installed, otherwise HTML→DOCX |

**Full example:**

```bash
python -m md2resume resume.md \
  --no-interactive \
  --style enhancv_it \
  --density compact \
  --page-size letter \
  --format both \
  -o ./output \
  -n Juan_Gonzalez_Resume \
  --photo ./photos/me.jpg \
  --qr github
```

---

## Document styles

Each style combines a **layout** (where content sits on the page) and a **palette** (navy / charcoal / slate grays).

| Style ID | Layout | Description |
|----------|--------|-------------|
| `classic_navy` | Single column | Name on top, simple rules; navy and gray. |
| `classic_charcoal` | Single column | Traditional serif; charcoal and cool gray. |
| `split_steel` | Split header | Name and contact on one row; steel blue accents. |
| `header_navy` | Top bar | Solid navy header band with contact inside. |
| `sidebar_navy` | Two columns | Dark left panel (contact, education, skills); experience on the right. |
| `sidebar_slate` | Two columns | Gray-blue sidebar; summary and roles on the right. |
| `timeline_slate` | Single column + timeline | Experience with a left timeline rule; slate palette. |
| `minimal_gray` | Single column | No panels; thin rules and more whitespace. |
| `enhancv_it` | Two columns (Enhancv-like) | Slate sidebar `#3c5769`; photo/QR top-left; experience right. |
| `ats_section_rule` | Single column | Heavy section underlines; ATS-friendly look. |
| `photo_header_gray` | Photo header | Photo and QR top-right; single-column body. |

### Legacy style aliases

Older `--theme` names still work:

| Alias | Maps to |
|-------|---------|
| `professional` | `classic_navy` |
| `classic` | `classic_charcoal` |
| `modern` | `split_steel` |
| `tech` | `sidebar_slate` |
| `ocean` | `enhancv_it` |
| `forest` | `classic_charcoal` |
| `sunset` | `classic_navy` |
| `violet` | `minimal_gray` |
| `midnight` | `header_navy` |
| `slate` | `timeline_slate` |

### Sidebar column routing

For `sidebar_navy`, `sidebar_slate`, and `enhancv_it`, sections whose **heading** contains any of these words go in the **left** column:

`education`, `certification`, `technologies`, `skills`, `technical`, `competenc`, `languages`, `profile`

All other sections (e.g. Professional Summary, Work Experience) go in the **right** column. Work Experience also gets timeline styling where applicable.

### Spacing (`--density`)

| Value | Use case |
|-------|----------|
| `compact` | Fit more on one page; tighter margins and list spacing. |
| `standard` | Default balance. |
| `spacious` | More air between sections; easier to scan. |

---

## Profile photo

| Flag | Behavior |
|------|----------|
| `--photo PATH` | Embed photo (circular crop in most layouts). |
| `--no-photo` | Never include a photo. |
| *(interactive)* | Asked yes/no, then file path. |

**Supported formats:** `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`

**Placement by layout:**

- **Sidebar / Enhancv:** Centered at top of left column (above name/contact).  
- **Photo header:** Top-right, beside name/contact.  
- **Split header / top bar / classic:** Beside the header block when enabled.  

**Docker:** Use paths inside the container, e.g. `/data/photo.jpg` when you mount your folder to `/data`.

---

## QR code

| Flag | Behavior |
|------|----------|
| `--qr none` | No QR code. |
| `--qr linkedin` | QR points to the first `linkedin.com` link in the markdown. |
| `--qr github` | QR points to the first `github.com` link in the markdown. |
| `--qr custom` | QR points to `--qr-url` (required in non-interactive mode). |
| *(interactive)* | Choose from detected links or enter a custom URL. |

**Markdown link detection** — links in standard form are auto-detected:

```markdown
[linkedin.com/in/you](https://linkedin.com/in/you)
[github.com/you](https://github.com/you)
```

If `--qr linkedin` or `--qr github` is set but no matching link exists, non-interactive mode prints a warning and skips the QR.

**Placement:** Usually below the photo in sidebar layouts; white background on dark sidebars for scanning.

---

## Output files

Controlled by `--format`, `-o` / `--output-dir`, and `-n` / `--output-name`.

### Output directory (`-o`)

```bash
python -m md2resume resume.md -o ~/Desktop/resumes
```

Default: directory containing the input `.md` file.

### Output name (`-n`)

| `-n` value | Result (`--format both`) |
|------------|---------------------------|
| `MyResume` | `MyResume.pdf` and `MyResume.docx` in output dir |
| `~/Desktop/MyResume` | Same names on Desktop |
| `~/Desktop/out.pdf` | Exact PDF path; DOCX as `out.docx` in same folder |
| `reports/out.docx` | Exact DOCX path; PDF as `reports/out.pdf` |

With `--format pdf` only, a name ending in `.pdf` sets the PDF path exactly.

---

## Export engines

### PDF

Tried in order until one succeeds:

1. **Playwright (Chromium)** — default; matches CSS/layout best.  
2. **WeasyPrint** — optional (`pip install weasyprint`); needs system libraries on some hosts.  
3. **Pandoc** — optional; only if `pandoc` is installed.

Run `python -m md2resume --setup` once per environment for Chromium.

### DOCX

1. **Pandoc** — used in non-interactive mode if `pandoc` is on `PATH`; interactive mode asks. Converts markdown structure; styling may differ from PDF.  
2. **HTML→DOCX** — default fallback via `htmldocx`; preserves more of the HTML/CSS styling.

For best visual match between PDF and Word, prefer the HTML→DOCX path (decline Pandoc in interactive mode, or uninstall/limit `pandoc` in CI).

---

## Markdown format

Your `.md` file should follow this structure:

```markdown
# Your Full Name

City, Country  
email@example.com  
[linkedin.com/in/you](https://linkedin.com/in/you)  
[github.com/you](https://github.com/you)

---

## Professional Summary

One paragraph about you.

---

## Work Experience

### Job Title — Team or Focus
**Company** — Location  
**Start – End**

- Bullet achievement one
- Bullet achievement two

---

## Education and Certifications

- **Degree**, School — years

---

## Technologies and Programming Languages

- **Category:** skill, skill, skill
```

**Rules:**

- `#` (H1) — your name (used as document title).  
- Contact block — paragraphs and links immediately after H1, before the first `##`.  
- `##` — major sections.  
- `###` — role or job title; following paragraph is usually company/location/dates.  
- `---` — optional between sections (hidden in output).  
- `**bold**` — emphasis (company names, dates, etc.).  

---

## Docker

Build the image:

```bash
docker build -t md2resume .
```

The container working directory is **`/data`**. Mount **any folder on your machine** that contains your `.md`, photos, and where you want PDF/DOCX written. Nothing in this repo is required for that—you use your own paths.

```bash
# Example: a folder on your machine (not part of this repository)
export RESUME_DIR="$HOME/resumes"
docker run --rm -it \
  -v "$RESUME_DIR:/data" \
  md2resume \
  /data/my-resume.md
```

### Interactive CLI in Docker

You do **not** need to open a shell first. Run the CLI with a TTY and your files mounted at `/data`:

```bash
docker run --rm -it \
  -v "$HOME/resumes:/data" \
  md2resume \
  /data/resume.md
```

- `-i` — keep stdin open for prompts  
- `-t` — allocate a terminal (`questionary` needs this)  
- Pass the markdown path **after** the image name (replaces default `--help`)

Partial flags work; omitted options are prompted:

```bash
docker run --rm -it -v "$HOME/resumes:/data" md2resume \
  /data/resume.md --style enhancv_it
```

### Shell inside the container

To explore files or run multiple exports manually:

```bash
docker run --rm -it \
  -v "$HOME/resumes:/data" \
  --entrypoint bash \
  md2resume
```

Inside the container:

```bash
cd /data
ls
python -m md2resume resume.md          # interactive
python -m md2resume resume.md --no-interactive --style classic_navy --format pdf
```

`PYTHONPATH` is already set; `python -m md2resume` works from any directory if you use absolute paths.

### Non-interactive Docker

No TTY required:

```bash
docker run --rm -v "$HOME/resumes:/data" md2resume \
  /data/resume.md \
  --no-interactive \
  --style enhancv_it \
  --format both \
  --photo /data/headshot.jpg \
  --qr linkedin \
  -n my-resume
```

Outputs appear in the mounted folder on your host (e.g. `$HOME/resumes/`).

### Docker Compose

Compose does not mount a folder by default—you pass your own volume when you run:

```bash
# Non-interactive
docker compose run --rm -v "$HOME/resumes:/data" md2resume \
  /data/resume.md \
  --no-interactive \
  --style sidebar_navy \
  --format pdf \
  -n resume

# Interactive (stdin_open + tty in compose file)
docker compose run --rm -it -v "$HOME/resumes:/data" md2resume /data/resume.md
```

**Note:** Playwright/Chromium is baked into the image at build time; you do not run `--setup` inside the container unless you extend the image.

---

## Project layout

```
md2resume/
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── md2resume/              # Python package
    ├── __main__.py
    ├── cli.py
    ├── styles.py
    ├── layouts.py
    ├── header.py             # photo & QR
    ├── builder.py
    ├── exporters.py
    ├── paths.py
    ├── template.py
    └── templates/
        └── document.html
```

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| PDF fails locally | `python -m md2resume --setup` |
| Interactive prompts garbled in Docker | Add `-it` to `docker run` / `docker compose run` |
| `File not found` for photo | Use container path (`/data/...`) in Docker |
| QR missing | Ensure markdown has `[text](https://linkedin.com/...)` links; use `--qr linkedin` or pick in interactive mode |
| QR missing after fix | Upgrade to latest code; contact block HTML must use valid `class="contact"` |
| DOCX looks different from PDF | Expected with Pandoc; retry without Pandoc for HTML→DOCX |
| `No linkedin link in markdown` | Add a markdown link or use `--qr custom --qr-url URL` |

---

## License

MIT (add a `LICENSE` file when publishing your remote repository).
