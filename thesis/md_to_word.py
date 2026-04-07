#!/usr/bin/env python3
"""
Script chuyển Markdown → Word theo quy định UIT
Sử dụng Pandoc để convert với format chuẩn
"""

import os
import sys
import subprocess
from pathlib import Path


class Colors:
    """Màu sắc cho terminal output"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_header():
    """In header"""
    print(f"{Colors.GREEN}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║     CHUYỂN MARKDOWN → WORD (THEO QUY ĐỊNH UIT)              ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()


def check_pandoc():
    """Kiểm tra pandoc đã cài chưa"""
    try:
        result = subprocess.run(['pandoc', '--version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            return True, version
        return False, None
    except FileNotFoundError:
        return False, None


def convert_md_to_docx(md_file, output_file, use_toc=True):
    """
    Chuyển Markdown sang Word sử dụng Pandoc

    Args:
        md_file: Đường dẫn file Markdown input
        output_file: Đường dẫn file Word output
        use_toc: Có tạo Table of Contents không
    """
    cmd = [
        'pandoc',
        str(md_file),
        '--from', 'markdown',
        '--to', 'docx',
        '--output', str(output_file),
        '--standalone',
    ]

    if use_toc:
        cmd.extend(['--toc', '--toc-depth=3'])

    # Thêm syntax highlighting cho code blocks
    cmd.extend(['--highlight-style', 'tango'])

    # Kiểm tra reference doc
    script_dir = Path(__file__).parent
    ref_doc = script_dir / 'uit_reference.docx'
    if ref_doc.exists():
        cmd.extend(['--reference-doc', str(ref_doc)])

    print(f"{Colors.YELLOW}📄 File input:{Colors.NC} {md_file}")
    print(f"{Colors.YELLOW}📁 File output:{Colors.NC} {output_file}")
    print(f"{Colors.YELLOW}⏳ Đang chuyển đổi...{Colors.NC}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    return result.returncode == 0, result


def format_size(size_bytes):
    """Format kích thước file sang dạng readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def main():
    """Main function"""
    print_header()

    # Đường dẫn
    script_dir = Path(__file__).parent
    md_file = script_dir / 'luanvan_template.md'
    output_dir = script_dir / 'output'
    output_file = output_dir / 'luanvan.docx'

    # Tạo thư mục output
    output_dir.mkdir(exist_ok=True)

    # Kiểm tra file input
    if not md_file.exists():
        print(f"{Colors.RED}✗ Không tìm thấy file: {md_file}{Colors.NC}")
        sys.exit(1)

    # Kiểm tra pandoc
    has_pandoc, version = check_pandoc()
    if not has_pandoc:
        print(f"{Colors.RED}✗ Pandoc chưa được cài đặt!{Colors.NC}")
        print(f"{Colors.YELLOW}  Cài đặt: brew install pandoc{Colors.NC}")
        sys.exit(1)

    print(f"{Colors.BLUE}✓ Pandoc: {version}{Colors.NC}")
    print()

    # Chuyển đổi
    success, result = convert_md_to_docx(md_file, output_file)

    if success:
        print(f"{Colors.GREEN}✅ Chuyển đổi thành công!{Colors.NC}")
        print()

        # Kích thước file
        if output_file.exists():
            size = output_file.stat().st_size
            print(f"{Colors.GREEN}📂 File đã tạo:{Colors.NC} {output_file}")
            print(f"{Colors.GREEN}📏 Kích thước:{Colors.NC} {format_size(size)}")
        print()

        # Mở file (macOS only)
        if sys.platform == 'darwin':
            try:
                subprocess.run(['open', str(output_file)])
                print(f"{Colors.GREEN}📖 Đã mở file Word{Colors.NC}")
            except:
                pass
    else:
        print(f"{Colors.RED}✗ Chuyển đổi thất bại!{Colors.NC}")
        if result.stderr:
            print(f"{Colors.RED}Error: {result.stderr}{Colors.NC}")
        sys.exit(1)


if __name__ == '__main__':
    main()
