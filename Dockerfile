# syntax=docker/dockerfile:1.6
# ==================== 构建阶段 ====================
FROM python:3.11.8-alpine3.19 AS builder

ARG PILLOW_VERSION=10.2.0

# 安装编译依赖（不锁定具体版本，Alpine 3.19 仓库保证兼容性）
RUN apk add --no-cache \
    gcc \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    tiff-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    libwebp-dev \
    libpng-dev

# 创建虚拟环境并安装指定版本 Pillow
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir pillow==${PILLOW_VERSION}

# ==================== 运行阶段 ====================
FROM python:3.11.8-alpine3.19 AS runtime

# 运行时库（不锁定版本）
RUN apk add --no-cache \
    libjpeg-turbo \
    zlib \
    libtiff \
    freetype \
    lcms2 \
    openjpeg \
    libwebp \
    libpng \
    bash \
    coreutils

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# 复制脚本
COPY "照片重命名归档.py" /app/organize_media.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh /app/organize_media.py

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    INPUT_FOLDER=/data/input \
    OUTPUT_FOLDER=/data/output \
    BACKUP_FOLDER=/data/backup \
    DRY_RUN=false

# 创建目录
RUN mkdir -p /data/input /data/output /data/backup

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--help"]

LABEL org.opencontainers.image.title="Photo Organizer" \
      org.opencontainers.image.description="照片视频整理归档工具"
