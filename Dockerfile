# syntax=docker/dockerfile:1.6
FROM python:3.11.8-slim-bookworm

ARG PILLOW_VERSION=10.2.0

# 安装系统依赖（使用稳定包名，不指定版本）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libwebp-dev \
    libpng-dev \
    bash \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# 安装 Pillow
RUN pip install --no-cache-dir pillow==${PILLOW_VERSION}

WORKDIR /app
COPY "照片重命名归档.py" /app/organize_media.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh /app/organize_media.py

ENV PYTHONUNBUFFERED=1 \
    INPUT_FOLDER=/data/input \
    OUTPUT_FOLDER=/data/output \
    BACKUP_FOLDER=/data/backup \
    DRY_RUN=false

RUN mkdir -p /data/input /data/output /data/backup

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--help"]

LABEL org.opencontainers.image.title="Photo Organizer" \
      org.opencontainers.image.description="照片视频整理归档工具"
