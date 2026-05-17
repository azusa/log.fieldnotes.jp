#!/usr/bin/env python3
"""
③ 画像パス置換スクリプト
ダウンロード済みの画像のみ、mdのURLをローカルパスに書き換える
② の実行後に動かすこと
"""

import re
from pathlib import Path

BLOG_DIR = Path("/workspace/docs/blog")
IMAGE_DIR = Path("/workspace/docs/public/images/blog")
HATENA_CDN = "https://cdn-ak.f.st-hatena.com"

pattern = re.compile(r'https://cdn-ak\.f\.st-hatena\.com(/[^\s")]+)')


def replace_in_file(md_file: Path) -> int:
    text = md_file.read_text(encoding="utf-8")
    replacements = 0

    def replacer(m):
        nonlocal replacements
        url_path = m.group(1)
        filename = Path(url_path).name
        local_path = IMAGE_DIR / filename
        if local_path.exists():
            replacements += 1
            return f"/images/blog/{filename}"
        return m.group(0)  # not downloaded, keep original URL

    new_text = pattern.sub(replacer, text)
    if replacements > 0:
        md_file.write_text(new_text, encoding="utf-8")
        print(f"  {md_file.relative_to(BLOG_DIR)}: {replacements} replaced")
    return replacements


def main():
    total = 0
    for md_file in sorted(BLOG_DIR.rglob("*.md")):
        total += replace_in_file(md_file)
    print(f"\nTotal: {total} URLs replaced")


if __name__ == "__main__":
    main()
