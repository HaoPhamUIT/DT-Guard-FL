#!/bin/bash
#
# Script chuyển Markdown → Word theo quy định UIT
# Sử dụng Pandoc để convert với format chuẩn
#

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Đường dẫn
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MD_FILE="${SCRIPT_DIR}/luanvan_template.md"
OUTPUT_DIR="${SCRIPT_DIR}/output"
OUTPUT_FILE="${OUTPUT_DIR}/luanvan.docx"

# Tạo thư mục output
mkdir -p "${OUTPUT_DIR}"

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     CHUYỂN MARKDOWN → WORD (THEO QUY ĐỊNH UIT)              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Kiểm tra file input
if [ ! -f "$MD_FILE" ]; then
    echo -e "${RED}✗ Không tìm thấy file: $MD_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}📄 File input:${NC} $MD_FILE"
echo -e "${YELLOW}📁 File output:${NC} $OUTPUT_FILE"
echo ""

# Kiểm tra pandoc
if ! command -v pandoc &> /dev/null; then
    echo -e "${RED}✗ Pandoc chưa được cài đặt. Cài đặt: brew install pandoc${NC}"
    exit 1
fi

# Chuyển đổi
echo -e "${YELLOW}⏳ Đang chuyển đổi...${NC}"

pandoc "$MD_FILE" \
  --from markdown \
  --to docx \
  --output "$OUTPUT_FILE" \
  --standalone \
  --toc \
  --toc-depth=3 \
  --highlight-style=tango \
  --reference-doc="${SCRIPT_DIR}/uit_reference.docx" 2>/dev/null || \
pandoc "$MD_FILE" \
  --from markdown \
  --to docx \
  --output "$OUTPUT_FILE" \
  --standalone \
  --toc \
  --toc-depth=3

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Chuyển đổi thành công!${NC}"
    echo ""
    echo -e "${GREEN}📂 File đã tạo:${NC} $OUTPUT_FILE"

    # Hiển thị kích thước file
    SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
    echo -e "${GREEN}📏 Kích thước:${NC} $SIZE"
    echo ""

    # Mở file (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        read -p "Bạn có muốn mở file ngay không? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "$OUTPUT_FILE"
        fi
    fi
else
    echo -e "${RED}✗ Chuyển đổi thất bại!${NC}"
    exit 1
fi
