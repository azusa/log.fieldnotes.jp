#!/bin/bash

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NOW=$(date +"%Y/%m/%d/%H%M%S")
DATE=$(date +"%Y-%m-%d")
YEAR=$(date +"%Y")
MONTH=$(date +"%m")
DAY=$(date +"%d")
TIMESTAMP=$(date +"%H%M%S")

TITLE="${1:-${DATE} の記事}"

FILE_PATH="${REPO_ROOT}/docs/blog/${YEAR}/${MONTH}/${DAY}/${TIMESTAMP}.md"
mkdir -p "$(dirname "$FILE_PATH")"

cat > "$FILE_PATH" <<EOF
---
title: "${TITLE}"
date: ${DATE}
---
EOF

# index.md のテーブルに追記（ヘッダー行の直後に挿入）
INDEX="${REPO_ROOT}/docs/blog/index.md"
LINK="./${YEAR}/${MONTH}/${DAY}/${TIMESTAMP}"
NEW_ROW="| ${DATE} | [${TITLE}](${LINK}) |"

# ヘッダー行 "|------|" の次の行に挿入
sed -i "/^|---/a ${NEW_ROW}" "$INDEX"

echo "Created: ${FILE_PATH}"
echo "Title:   ${TITLE}"
