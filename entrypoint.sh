#!/bin/bash
set -e

show_help() {
    echo "照片视频整理归档工具"
    echo ""
    echo "用法: docker run [选项] ghcr.io/username/repo [命令]"
    echo ""
    echo "命令:"
    echo "  organize    执行整理（默认）"
    echo "  preview     预览模式（不实际执行）"
    echo "  help        显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  INPUT_FOLDER    输入目录（默认: /data/input）"
    echo "  OUTPUT_FOLDER   输出目录（默认: /data/output）"
    echo "  BACKUP_FOLDER   备份目录（默认: /data/backup，空则不备份）"
    echo "  DRY_RUN         预览模式 true/false（默认: false）"
    echo ""
    echo "示例:"
    echo "  docker run -v /本地/照片:/data/input -v /本地/输出:/data/output ghcr.io/username/repo organize"
    echo ""
}

case "${1:-}" in
    help|--help|-h)
        show_help
        exit 0
        ;;
    preview|--preview|-n)
        echo "🔍 预览模式"
        export DRY_RUN=true
        python /app/organize_media.py
        ;;
    organize|--organize|"")
        echo "🚀 执行整理..."
        python /app/organize_media.py
        ;;
    *)
        exec "$@"
        ;;
esac
