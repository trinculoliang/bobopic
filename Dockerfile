# syntax=docker/dockerfile:1.6

# ==================== 构建阶段 ====================
FROM python:3.11.8-alpine3.19 AS builder

WORKDIR /app

# 安装编译依赖
RUN apk add --no-cache \
    gcc \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    libffi-dev

# 安装 Pillow 到标准路径（非 --user）
RUN pip install --no-cache-dir --target=/packages pillow==10.2.0

# ==================== 运行阶段 ====================
FROM python:3.11.8-alpine3.19 AS runtime

# 安装运行时库
RUN apk add --no-cache \
    libjpeg-turbo \
    zlib \
    libffi \
    bash

# 从构建阶段复制 Python 包（使用标准路径）
COPY --from=builder /packages /usr/local/lib/python3.11/site-packages

WORKDIR /app

# 复制脚本
COPY "照片重命名归档.py" /app/organize_media.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh /app/organize_media.py

# 环境变量
ENV INPUT_FOLDER=/data/input \
    OUTPUT_FOLDER=/data/output \
    BACKUP_FOLDER=/data/backup \
    DRY_RUN=false \
    PYTHONUNBUFFERED=1

# 创建目录
RUN mkdir -p /data/input /data/output /data/backup

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--help"]
