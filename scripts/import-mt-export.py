#!/usr/bin/env python3
"""Parse MT export file and create VitePress stub markdown files."""

import os
import re
from datetime import datetime
from pathlib import Path

EXPORT_FILE = Path(__file__).parent.parent / "tmp.fieldnotes.jp.export.txt"
BLOG_DIR = Path(__file__).parent.parent / "docs" / "blog"


def parse_mt_export(text: str) -> list[dict]:
    entries = []
    for raw in text.strip().split("--------"):
        raw = raw.strip()
        if not raw:
            continue

        parts = raw.split("-----", 1)
        header_block = parts[0]

        entry = {}
        for line in header_block.splitlines():
            if ": " in line:
                key, _, value = line.partition(": ")
                entry[key.strip()] = value.strip()

        if "TITLE" not in entry or "BASENAME" not in entry:
            continue

        entries.append(entry)
    return entries


def mt_date_to_iso(mt_date: str) -> str:
    """Convert '11/13/2025 23:02:41' to '2025-11-13'."""
    dt = datetime.strptime(mt_date, "%m/%d/%Y %H:%M:%S")
    return dt.strftime("%Y-%m-%d")


def create_stub(entry: dict) -> Path:
    basename = entry["BASENAME"]  # e.g. 2025/11/13/230241
    title = entry["TITLE"]
    date_iso = mt_date_to_iso(entry["DATE"])

    out_path = BLOG_DIR / (basename + ".md")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    escaped_title = title.replace('"', '\\"')
    content = f"""---
title: "{escaped_title}"
date: {date_iso}
---

<!-- TODO: ここに編集画面からコピーしたMarkdownを貼り付ける -->
"""
    out_path.write_text(content, encoding="utf-8")
    return out_path


def main():
    text = EXPORT_FILE.read_text(encoding="utf-8")
    entries = parse_mt_export(text)

    print(f"{len(entries)} 件のエントリを処理します\n")

    created = []
    for entry in entries:
        path = create_stub(entry)
        created.append((entry["DATE"], entry["TITLE"], path))
        print(f"  作成: {path.relative_to(Path.cwd())}")

    print(f"\n完了: {len(created)} ファイルを生成しました")
    return created


if __name__ == "__main__":
    main()
