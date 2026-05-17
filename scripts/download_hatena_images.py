#!/usr/bin/env python3
"""
① 画像ダウンロードスクリプト
cdn-ak.f.st-hatena.com の画像を docs/public/ 配下にミラーリングする
"""

import os
import re
import urllib.request
import urllib.error
from pathlib import Path

BLOG_DIR = Path("/workspace/docs/blog")
IMAGE_DIR = Path("/workspace/docs/public/images/blog")
HATENA_CDN = "https://cdn-ak.f.st-hatena.com"


def collect_image_urls() -> dict[str, Path]:
    """Returns mapping of url -> local save path"""
    urls = {}
    pattern = re.compile(r'https://cdn-ak\.f\.st-hatena\.com(/[^\s")]+)')
    for md_file in BLOG_DIR.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        for m in pattern.finditer(text):
            url_path = m.group(1)
            url = HATENA_CDN + url_path
            filename = Path(url_path).name
            local_path = IMAGE_DIR / filename
            urls[url] = local_path
    return urls


def download_all():
    urls = collect_image_urls()
    print(f"{len(urls)} images to download")

    ok = 0
    skip = 0
    fail = 0

    for url, local_path in sorted(urls.items()):
        if local_path.exists():
            print(f"  SKIP {local_path.name}")
            skip += 1
            continue

        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                local_path.write_bytes(resp.read())
            print(f"  OK   {url}")
            ok += 1
        except urllib.error.HTTPError as e:
            print(f"  FAIL {url} ({e.code})")
            fail += 1
        except Exception as e:
            print(f"  FAIL {url} ({e})")
            fail += 1

    print(f"\nDone: {ok} downloaded, {skip} skipped, {fail} failed")


if __name__ == "__main__":
    download_all()
