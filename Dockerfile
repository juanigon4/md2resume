FROM python:3.12-bookworm

ENV PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# System libraries for Playwright Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium

COPY md2resume/ /app/md2resume/

ENV PYTHONPATH=/app

# Mount this directory: put resume.md, photos, and receive PDF/DOCX here
WORKDIR /data
VOLUME ["/data"]

ENTRYPOINT ["python", "-m", "md2resume"]
CMD ["--help"]
