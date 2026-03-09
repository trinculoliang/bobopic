# syntax=docker/dockerfile:1.6
FROM python:3.11.8-alpine3.19 AS builder

ARG PILLOW_VERSION=10.2.0

RUN apk add --no-cache \
    gcc=13.2.1_git20231014-r0 \
    musl-dev=1.2.4_git20230717-r4 \
    jpeg-dev=9e-r1 \
    zlib-dev=1.3-r2 \
    tiff-dev=4.6.0-r0 \
    freetype-dev=2.13.2-r0 \
    lcms2-dev=2.15-r4 \
    openjpeg-dev=2.5.0-r3 \
    libwebp-dev=1.3.2-r0 \
    libpng-dev=1.6.40-r0

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir pillow==${PILLOW_VERSION}

FROM python:3.11.8-alpine3.19 AS runtime

RUN apk add --no-cache \
    libjpeg-turbo=3.0.1-r0 \
    zlib=1.3-r2 \
    libtiff=4.6.0-r0 \
    freetype=2.13.2-r0 \
    lcms2=2.15-r4 \
    openjpeg=2.5.0-r3 \
    libwebp=1.3.2-r0 \
    libpng=1.6.40-r0 \
    bash=5.2.21-r0 \
    coreutils=9.4-r2

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY "照片重命名归档.py" /app/organize_media.py
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh /app/organize_media.py

ENV PYTHONUNBUFFERED=1
ENV INPUT_FOLDER=/data/input
ENV OUTPUT_FOLDER=/data/output
ENV BACKUP_FOLDER=/data/backup
ENV DRY_RUN=false

RUN mkdir -p /data/input /data/output /data/backup

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--help"]

LABEL org.opencontainers.image.title="Photo Organizer"
LABEL org.opencontainers.image.description="照片视频整理归档工具"
LABEL org.opencontainers.image.source="https://github.com/${GITHUB_REPOSITORY}"
LABEL org.opencontainers.image.licenses="MIT"
