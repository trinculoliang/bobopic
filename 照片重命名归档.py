#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
照片视频整理归档脚本
功能：按时间排序、重命名并归档到年月目录

使用说明：
1. 安装依赖: pip install Pillow
2. 修改下方【配置区域】的 INPUT_FOLDER、OUTPUT_FOLDER 和 BACKUP_FOLDER
3. 运行: python organize_media.py
4. 预览模式: 设置 DRY_RUN = True 后运行

文件名格式：
- 照片: Bobo_YYYYMMDD_IMG_001.jpg
- 视频: Bobo_YYYYMMDD_VID_001.mp4

目录结构：
输出目录/
├── 2023/
│   ├── 10/
│   └── 11/
└── 2024/
    └── 01/

备份目录/
├── IMG_1234.jpg
├── VID_0001.mp4
└── ...
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
import argparse

# ==================== 依赖检查 ====================

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    print("❌ 错误：缺少必要的依赖库 Pillow")
    print("")
    print("请安装 Pillow：")
    print("   pip install Pillow")
    print("")
    print("或使用国内镜像加速：")
    print("   pip install Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple")
    print("")
    print("安装完成后重新运行脚本。")
    sys.exit(1)

# ==================== 配置区域（修改这里）====================

# 输入文件夹：照片、视频所在目录
# 示例: "/Users/bobo/Downloads/相机照片" 或 r"c:\Users\liang\Downloads\1"
INPUT_FOLDER = r"c:\Users\liang\Downloads\1"

# 输出文件夹：年份文件夹的上级目录（如不存在则自动创建）
# 示例: "/Users/bobo/照片库" 或 r"c:\Users\liang\Downloads\2"
OUTPUT_FOLDER = r"c:\Users\liang\Downloads\2"

# 备份文件夹：重命名前将原文件复制到此目录（如不存在则自动创建）
# 设置为 None 或空字符串表示不备份
# 示例: "/Users/bobo/备份" 或 r"c:\Users\liang\Downloads\backup"
BACKUP_FOLDER = r"c:\Users\liang\Downloads\bak"

# 预览模式：设置为 True 只预览不执行，False 则实际执行
DRY_RUN = False

# ==================== 格式配置（可选修改）====================

# 支持的图片格式
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', 
    '.gif', '.webp', '.heic', '.heif', '.raw', '.cr2', 
    '.nef', '.arw', '.orf', '.rw2'
}

# 支持的视频格式
VIDEO_EXTENSIONS = {
    '.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', 
    '.m4v', '.3gp', '.mts', '.m2ts', '.ts', '.webm', 
    '.mpg', '.mpeg', '.mxf'
}

# ==================== 核心函数 ====================

def get_exif_datetime(file_path):
    """
    从图片EXIF数据中提取拍摄日期时间（精确到秒）
    优先级: DateTimeOriginal > DateTime > DateTimeDigitized
    返回: datetime对象 或 None
    """
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        
        if exif_data:
            # 按优先级查找日期时间标签
            datetime_tags = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
            
            for tag_name in datetime_tags:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == tag_name:
                        try:
                            # EXIF日期时间格式: "2023:10:15 14:30:00"
                            return datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
                        except:
                            continue
        return None
    except Exception:
        return None


def get_file_timestamps(file_path):
    """
    获取文件的所有时间戳
    返回: (创建时间, 修改时间) 的 datetime 元组，无法获取的返回 None
    """
    try:
        stat = os.stat(file_path)
        
        # 获取创建时间（平台相关）
        creation_time = None
        if hasattr(stat, 'st_birthtime'):
            creation_time = datetime.fromtimestamp(stat.st_birthtime)
        elif hasattr(stat, 'st_ctime'):
            creation_time = datetime.fromtimestamp(stat.st_ctime)
        
        # 修改时间（所有平台通用）
        modification_time = datetime.fromtimestamp(stat.st_mtime)
        
        return creation_time, modification_time
        
    except Exception:
        return None, None


def get_earliest_file_datetime(file_path):
    """
    获取文件时间中的最早时间（修改时间 vs 创建时间）
    返回: (datetime对象, 来源描述字符串) 或 (None, None)
    """
    creation_time, modification_time = get_file_timestamps(file_path)
    
    # 收集所有可用的时间
    available_times = []
    
    if modification_time:
        available_times.append((modification_time, '文件修改时间'))
    
    if creation_time:
        available_times.append((creation_time, '文件创建时间'))
    
    if not available_times:
        return None, None
    
    # 返回最早的时间
    earliest = min(available_times, key=lambda x: x[0])
    return earliest[0], earliest[1]


def get_file_datetime(file_path):
    """
    获取文件日期时间（精确到秒，综合策略）
    优先级: 1.EXIF日期时间(仅图片) 2.文件时间中的最早时间（修改时间/创建时间）
    返回: (datetime对象, 日期来源字符串) 或 (None, None)
    """
    ext = Path(file_path).suffix.lower()
    
    # 第一步：图片文件优先读取EXIF（精确到秒）
    if ext in IMAGE_EXTENSIONS:
        exif_datetime = get_exif_datetime(file_path)
        if exif_datetime:
            return exif_datetime, 'EXIF'
    
    # 第二步：获取文件时间中的最早时间（精确到秒）
    earliest_datetime, time_source = get_earliest_file_datetime(file_path)
    if earliest_datetime:
        return earliest_datetime, time_source
    
    return None, None


def get_file_type(file_path):
    """判断文件类型: 'image' | 'video' | None"""
    ext = Path(file_path).suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    elif ext in VIDEO_EXTENSIONS:
        return 'video'
    return None


def generate_new_filename(date, file_type, sequence_num):
    """
    生成新文件名（不含扩展名）
    格式: Bobo_YYYYMMDD_IMG_001 或 Bobo_YYYYMMDD_VID_001
    """
    date_str = date.strftime('%Y%m%d')
    seq_str = f"{sequence_num:03d}"
    
    type_code = 'IMG' if file_type == 'image' else 'VID'
    return f"Bobo_{date_str}_{type_code}_{seq_str}"


def ensure_dir(path):
    """确保目录存在，不存在则递归创建"""
    path.mkdir(parents=True, exist_ok=True)


# ==================== 主逻辑 ====================

def organize_files(input_folder, output_folder, backup_folder=None, dry_run=False):
    """
    主整理函数
    
    流程：
    1. 扫描所有文件，获取精确到秒的日期时间
    2. 按时间先后排序（从早到晚）
    3. 重命名前复制原文件到备份目录（如果配置了备份）
    4. 按日期分组，每天的照片和视频分别编号
    5. 移动并重命名到目标目录
    
    Args:
        input_folder: 输入文件夹路径（照片、视频所在目录）
        output_folder: 输出文件夹路径（年份文件夹的上级目录）
        backup_folder: 备份文件夹路径（重命名前复制原文件，None表示不备份）
        dry_run: 是否为预览模式（只显示不执行）
    """
    input_path = Path(input_folder).resolve()
    output_path = Path(output_folder).resolve()
    
    # 处理备份目录
    backup_path = None
    if backup_folder and str(backup_folder).strip():
        backup_path = Path(backup_folder).resolve()
    
    # 验证输入文件夹
    if not input_path.exists():
        print(f"❌ 错误：输入文件夹 '{input_folder}' 不存在")
        return
    
    if not input_path.is_dir():
        print(f"❌ 错误：'{input_folder}' 不是有效的文件夹")
        return
    
    # 确保输出文件夹存在（如果不存在则创建）
    if not output_path.exists():
        if dry_run:
            print(f"📂 [预览] 将创建输出目录: {output_path}")
        else:
            ensure_dir(output_path)
            print(f"📂 创建输出目录: {output_path}")
    
    # 确保备份文件夹存在（如果配置了备份）
    if backup_path:
        if not backup_path.exists():
            if dry_run:
                print(f"💾 [预览] 将创建备份目录: {backup_path}")
            else:
                ensure_dir(backup_path)
                print(f"💾 创建备份目录: {backup_path}")
        print(f"💾 备份目录: {backup_path}")
    
    print(f"📥 输入目录: {input_path}")
    print(f"📤 输出目录: {output_path}")
    print(f"🔍 正在扫描文件并获取精确时间信息...")
    
    # 第一步：收集所有媒体文件信息（包含精确到秒的时间）
    media_files = []
    
    for file_path in input_path.iterdir():
        if not file_path.is_file():
            continue
            
        file_type = get_file_type(str(file_path))
        if not file_type:
            continue  # 跳过不支持的格式
            
        # 获取精确的日期时间信息
        file_datetime, datetime_source = get_file_datetime(str(file_path))
        if not file_datetime:
            print(f"⚠️  跳过（无日期信息）: {file_path.name}")
            continue
            
        media_files.append({
            'original_path': file_path,
            'datetime': file_datetime,           # 精确到秒的datetime对象
            'datetime_source': datetime_source,  # 'EXIF' 或 '文件修改时间' 或 '文件创建时间'
            'file_type': file_type,              # 'image' 或 'video'
            'extension': file_path.suffix.lower()
        })
    
    if not media_files:
        print("❌ 未找到任何照片或视频文件")
        return
    
    # 第二步：按时间先后排序（精确到秒，从早到晚）
    media_files.sort(key=lambda x: x['datetime'])
    
    print(f"✅ 已按时间排序（精确到秒），共 {len(media_files)} 个文件")
    
    # 第三步：生成目标路径和文件名（按天分组编号）
    daily_counters = {}  # 用于每天独立编号 {(date, type): count}
    operations = []      # 存储所有操作记录
    
    print(f"\n{'='*70}")
    print(f"{'📋 [预览模式]' if dry_run else '🚀 [执行模式]'}")
    print(f"{'='*70}")
    print(f"文件处理顺序（已按时间排序）：\n")
    
    for idx, item in enumerate(media_files, 1):
        date_key = item['datetime'].date()
        file_type = item['file_type']
        counter_key = (date_key, file_type)
        
        # 每日每类型独立计数
        daily_counters[counter_key] = daily_counters.get(counter_key, 0) + 1
        
        # 生成新文件名（使用日期部分，顺序号按天重置）
        new_name = generate_new_filename(
            item['datetime'], 
            file_type, 
            daily_counters[counter_key]
        )
        new_filename = new_name + item['extension']
        
        # 构建目标目录: output_folder/YYYY/MM/
        year_str = item['datetime'].strftime('%Y')   # 四位年份: 2023
        month_str = item['datetime'].strftime('%m')  # 两位月份: 01-12
        
        year_dir = output_path / year_str
        month_dir = year_dir / month_str
        final_path = month_dir / new_filename
        
        # 处理文件名冲突（如果目标已存在）
        conflict_counter = 1
        while final_path.exists() and final_path != item['original_path']:
            new_filename = f"{new_name}_{conflict_counter:02d}{item['extension']}"
            final_path = month_dir / new_filename
            conflict_counter += 1
        
        # 构建备份路径（如果配置了备份）
        backup_file_path = None
        if backup_path:
            backup_file_path = backup_path / item['original_path'].name
        
        # 记录操作
        operations.append({
            'source': item['original_path'],
            'target': final_path,
            'backup': backup_file_path,
            'month_dir': month_dir,
            'item': item,
            'order': idx
        })
        
        # 显示预览（包含精确时间和排序序号）
        icon = "🖼️ " if file_type == 'image' else "🎬"
        
        # 日期来源显示
        if item['datetime_source'] == 'EXIF':
            source_type = "📷EXIF"
        elif '修改时间' in item['datetime_source']:
            source_type = "📝修改时间"
        elif '创建时间' in item['datetime_source']:
            source_type = "📄创建时间"
        else:
            source_type = "📄文件时间"
        
        # 格式化时间显示
        time_str = item['datetime'].strftime('%Y-%m-%d %H:%M:%S')
        
        # 计算相对路径用于显示
        try:
            rel_source = item['original_path'].relative_to(input_path)
        except:
            rel_source = item['original_path'].name
        
        # 显示排序序号、时间、来源和目标
        print(f"{idx:3d}. {icon} [{source_type}] {time_str}")
        print(f"     {str(rel_source):40s}")
        if backup_file_path:
            print(f"     💾 备份: {backup_file_path.name}")
        print(f"     └─> 📁 {year_str}/{month_str}/{new_filename}")
    
    # 预览模式：显示统计并退出
    if dry_run:
        print(f"\n{'='*70}")
        print("📂 将创建以下目录结构:")
        dirs = sorted(set(op['month_dir'] for op in operations))
        for d in dirs:
            try:
                rel_dir = d.relative_to(output_path)
                print(f"   {output_path.name}/{rel_dir}")
            except:
                print(f"   {d}")
        if backup_path:
            print(f"\n💾 将备份 {len(operations)} 个文件到: {backup_path}")
        print(f"{'='*70}")
        print(f"\n💡 预览完成，共 {len(operations)} 个文件")
        print("   将 DRY_RUN 设为 False 以实际执行")
        return
    
    # 第四步：实际执行备份、移动和重命名
    print(f"\n{'='*70}")
    print("🚀 开始执行...")
    print(f"{'='*70}\n")
    
    stats = {
        'processed': 0, 
        'image': 0, 
        'video': 0, 
        'exif': 0, 
        'file_modify': 0,
        'file_create': 0,
        'backup_copied': 0,
        'errors': 0
    }
    
    for op in operations:
        try:
            # 1. 先备份原文件（如果配置了备份目录）
            if op['backup']:
                shutil.copy2(str(op['source']), str(op['backup']))
                stats['backup_copied'] += 1
            
            # 2. 创建目标目录（如果不存在）
            ensure_dir(op['month_dir'])
            
            # 3. 移动文件到目标位置（重命名）
            shutil.move(str(op['source']), str(op['target']))
            
            # 统计
            stats['processed'] += 1
            stats[op['item']['file_type']] += 1
            
            # 按日期来源统计
            if op['item']['datetime_source'] == 'EXIF':
                stats['exif'] += 1
            elif '修改时间' in op['item']['datetime_source']:
                stats['file_modify'] += 1
            elif '创建时间' in op['item']['datetime_source']:
                stats['file_create'] += 1
                
        except Exception as e:
            print(f"❌ 错误: {op['source'].name} -> {e}")
            stats['errors'] += 1
    
    # 打印最终统计
    print(f"\n{'='*70}")
    print("✅ 处理完成！")
    print(f"{'='*70}")
    print(f"  📊 成功处理: {stats['processed']} 个")
    if backup_path:
        print(f"  💾 已备份: {stats['backup_copied']} 个")
    print(f"  🖼️  图片: {stats['image']} 个")
    print(f"  🎬 视频: {stats['video']} 个")
    print(f"  📷 EXIF日期: {stats['exif']} 个")
    print(f"  📝 文件修改时间: {stats['file_modify']} 个")
    print(f"  📄 文件创建时间: {stats['file_create']} 个")
    if stats['errors'] > 0:
        print(f"  ❌ 失败: {stats['errors']} 个")
    print(f"{'='*70}\n")


# ==================== 程序入口 ====================

if __name__ == '__main__':
    # 检查配置是否已修改
    if INPUT_FOLDER == r"c:\Users\liang\Downloads\12" and OUTPUT_FOLDER == r"c:\Users\liang\Downloads\22":
        # 如果使用的是默认路径，检查是否真的是用户想要的
        print("⚠️  正在使用默认路径配置")
        print(f"   输入: {INPUT_FOLDER}")
        print(f"   输出: {OUTPUT_FOLDER}")
        print(f"   备份: {BACKUP_FOLDER if BACKUP_FOLDER else '未配置'}")
        print("")
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            print("已取消。请修改脚本中的配置区域。")
            sys.exit(0)
    
    # 检查输入输出路径是否相同
    input_path = Path(INPUT_FOLDER).resolve()
    output_path = Path(OUTPUT_FOLDER).resolve()
    
    if input_path == output_path:
        print("❌ 错误：输入文件夹和输出文件夹不能相同")
        sys.exit(1)
    
    # 检查备份路径是否与输入或输出路径冲突
    if BACKUP_FOLDER and str(BACKUP_FOLDER).strip():
        backup_path = Path(BACKUP_FOLDER).resolve()
        if backup_path == input_path:
            print("❌ 错误：备份文件夹不能与输入文件夹相同")
            sys.exit(1)
        if backup_path == output_path:
            print("❌ 错误：备份文件夹不能与输出文件夹相同")
            sys.exit(1)
    
    # 执行整理
    organize_files(INPUT_FOLDER, OUTPUT_FOLDER, BACKUP_FOLDER, DRY_RUN)