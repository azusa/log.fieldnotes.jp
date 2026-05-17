#!/usr/bin/env python3
"""Migrate MT export from blog.fieldnotes.jp to docs/blog/"""

import os
import re
from datetime import datetime
from markdownify import markdownify as md

EXPORT_FILE = "/workspace/.tmp/blog.fieldnotes.jp.export.txt"
BLOG_DIR = "/workspace/docs/blog"
OLD_BASE_URL = "https://blog.fieldnotes.jp"
NEW_BASE_URL = "https://log.fieldnotes.jp/blog"

def clean_html(html: str) -> str:
    # Remove hatena keyword links (keep text)
    html = re.sub(r'<a[^>]+class="keyword"[^>]*>(.*?)</a>', r'\1', html, flags=re.DOTALL)
    # Convert hatena iframe embed cards to plain links using the cite tag
    html = re.sub(
        r'<iframe[^>]+class="embed-card[^"]*"[^>]*>.*?</iframe>\s*<cite[^>]*><a href="([^"]+)">[^<]*</a></cite>',
        r'<a href="\1">\1</a>',
        html,
        flags=re.DOTALL
    )
    # Remove remaining iframes
    html = re.sub(r'<iframe[^>]*>.*?</iframe>', '', html, flags=re.DOTALL)
    # Unwrap schema.org spans around images
    html = re.sub(r'<span[^>]+itemscope[^>]*>(.*?)</span>', r'\1', html, flags=re.DOTALL)
    # Remove cite.hatena-citation
    html = re.sub(r'<cite[^>]*>.*?</cite>', '', html, flags=re.DOTALL)
    return html

def html_to_md(html: str) -> str:
    html = clean_html(html)
    result = md(html, heading_style="ATX", bullets="-", code_language="")
    # Clean up excessive blank lines
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip()

def parse_mt_export(filepath: str):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    articles = []
    for raw in content.split("\n--------\n"):
        raw = raw.strip()
        if not raw:
            continue

        article = {}
        # Extract header fields (before first -----)
        parts = raw.split("\n-----\n")
        if not parts:
            continue

        # Parse header
        for line in parts[0].splitlines():
            if ": " in line:
                key, _, val = line.partition(": ")
                article[key.strip()] = val.strip()

        # Parse sections (BODY, EXCERPT, COMMENT, etc.)
        body_parts = []
        for section in parts[1:]:
            if section.startswith("BODY:\n"):
                body_parts.append(section[len("BODY:\n"):].rstrip())
            elif section.startswith("EXCERPT:\n"):
                pass  # skip
            elif section.startswith("COMMENT:\n"):
                pass  # skip comments
            # other sections ignored

        article["_body"] = "\n\n".join(body_parts)

        if article.get("STATUS") == "Publish" and article.get("TITLE"):
            articles.append(article)

    return articles

def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%m/%d/%Y %H:%M:%S")

def make_new_path(dt: datetime) -> str:
    return f"{dt.year:04d}/{dt.month:02d}/{dt.day:02d}/{dt.hour:02d}{dt.minute:02d}{dt.second:02d}"

def write_article(article: dict) -> tuple[str, str]:
    """Returns (new_path, new_url)"""
    dt = parse_date(article["DATE"])
    path = make_new_path(dt)
    basename = article.get("BASENAME", "")
    title = article["TITLE"]

    body_md = html_to_md(article["_body"])

    date_str = dt.strftime("%Y-%m-%d")
    # Escape quotes in title for YAML
    title_escaped = title.replace('"', '\\"')
    frontmatter = f'---\ntitle: "{title_escaped}"\ndate: {date_str}\n---\n'
    content = f"{frontmatter}\n# {title}\n\n{body_md}\n"

    out_path = os.path.join(BLOG_DIR, path + ".md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    old_url = f"{OLD_BASE_URL}/{basename}"
    new_url = f"{NEW_BASE_URL}/{path}"
    return old_url, new_url

def update_index(entries: list[tuple[str, str, str]]):
    """entries: list of (date_str, title, rel_path)"""
    # Sort by date descending
    entries.sort(key=lambda x: x[0], reverse=True)

    rows = "\n".join(
        f"| {date} | [{title}](./{rel_path}) |"
        for date, title, rel_path in entries
    )
    index_content = f"# Blog\n\n| 日付 | タイトル |\n|------|---------|\n{rows}\n"

    with open(os.path.join(BLOG_DIR, "index.md"), "w", encoding="utf-8") as f:
        f.write(index_content)

def main():
    articles = parse_mt_export(EXPORT_FILE)
    print(f"Found {len(articles)} articles")

    url_mappings = []
    index_entries = []

    for article in articles:
        try:
            old_url, new_url = write_article(article)
            url_mappings.append((old_url, new_url))
            dt = parse_date(article["DATE"])
            date_str = dt.strftime("%Y-%m-%d")
            path = make_new_path(dt)
            index_entries.append((date_str, article["TITLE"], path))
            print(f"  {old_url} -> {new_url}")
        except Exception as e:
            print(f"  ERROR {article.get('TITLE')}: {e}")

    # Add existing blog entries (not from MT)
    existing_entries = [
        ("2026-05-15", "devcontainerの環境を作成するためのプロンプト例", "2026/05/15/085840"),
        ("2026-05-13", "複数行コマンドをターミナルに貼れない現場の手順書問題(Claudeとの会話シリーズ)", "2026/05/13/034532"),
        ("2026-05-08", "WSL上のffmpegでiPadで撮影した動画をクリッピング", "2026/05/08/140718"),
        ("2026-05-07", "脆弱性情報に関するNISTの方針転換の方針に関する社内へのSlack案内テンプレ(続き)とClaudeとの会話", "2026/05/07/021909"),
        ("2026-05-06", "脆弱性情報に関する※NISTの方針転換の方針に関する社内へのSlack案内テンプレ", "2026/05/06/005850"),
        ("2025-11-13", "SSHのセッションからラズパイのX Windowにvlcを全画面で表示する", "2025/11/13/230241"),
        ("2025-10-22", "Joplin CLIでノートのアーカイブをimportしてmd形式でexport", "2025/10/22/160925"),
        ("2025-09-21", "Hyper-Vの内部ホスト内の仮想マシンにNATでアクセスできるようにする", "2025/09/21/230846"),
        ("2025-09-15", "大きなファイルを分割してscpで転送する", "2025/09/15/225451"),
        ("2025-09-05", "psqlコマンドのプロンプト内からSQLの結果をタブ区切りで出力する", "2025/09/05/100404"),
        ("2025-08-07", "複数のMarkdownファイルをPandocでPDF変換した後に1ファイルに連結する", "2025/08/07/155524"),
        ("2025-08-05", "CentOS Stream10でk8sセットアップ", "2025/08/05/221824"),
        ("2025-07-23", "ラズパイの動画をYouTubeとMiniDLNAの両方に送る", "2025/07/23/191814"),
    ]
    index_entries.extend(existing_entries)

    update_index(index_entries)

    # Write TSV
    tsv_path = "/workspace/.tmp/url_mapping.tsv"
    with open(tsv_path, "w", encoding="utf-8") as f:
        f.write("old_url\tnew_url\n")
        for old_url, new_url in url_mappings:
            f.write(f"{old_url}\t{new_url}\n")

    print(f"\nTSV written to {tsv_path}")
    print(f"Index updated with {len(index_entries)} entries")

if __name__ == "__main__":
    main()
