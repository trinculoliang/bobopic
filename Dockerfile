# 方案 B：Debian-based（版本更稳定）
# ==================== 构建阶段 ====================
FROM python:3.11.8-slim-bookworm AS builder

ARG PILLOW_VERSION=10.2.0

# Debian 软件包版本更稳定
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc=4:12.2.0-3 \
    libjpeg-dev=1:2.1.5-2 \
    zlib1g-dev=1:1.2.13.dfsg-1 \
    libtiff-dev=4.5.0-6+deb12u1 \
    libfreetype6-dev=2.12.1+dfsg-5 \
    liblcms2-dev=2.14-2 \
    libopenjp2-7-dev=2.5.0-2 \
    libwebp-dev=1.2.4-0.2+deb12u1 \
    libpng-dev=1.6.39-2 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir pillow==${PILLOW_VERSION}

# ==================== 运行阶段 ====================
FROM python:3.11.8-slim-bookworm AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo=1:2.1.5-2 \
    zlib1g=1:1.2.13.dfsg-1 \
    libtiff6=4.5.0-6+deb12u1 \
    libfreetype6=2.12.1+dfsg-5 \
    liblcms2-2=2.14-2 \
    libopenjp2-7=2.5.0-2 \
    libwebp7=1.2.4-0.2+deb12u1 \
    libpng16-16=1.6.39-2 \
    && rm -rf /var/lib/apt/lists/*

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
