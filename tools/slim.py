#!/usr/bin/env python3
"""Build the lean copy of the division2 crawl that is committed to git.

The original crawl is about 2.9 GB.  Most of it is the same few hundred
images embedded as base64 inside ~850 HTML pages, plus PDF/Word/Excel files.
This script reads the full crawl (left untouched) and writes a lean copy:

  1. base64 images/fonts inside .html and .css are written once to
     /_inline/<hash>.<ext> and the pages point at that file instead
  2. documents (.pdf .doc .docx .xls .xlsx .ppt .pptx .zip .rar) are skipped
     and listed in docs/division2-omitted-files.txt (they stay in backup.zip)
  3. photos larger than 500 KB are downscaled to at most 1600 px wide
     (JPEG quality 82); needs Pillow, otherwise they are copied unchanged
  4. names containing "?" / U+F03F become "_q_" (see tools/prepare.py)

Usage
    python tools/slim.py --src <path>/division2.immigration.go.th
"""
import argparse
import base64
import hashlib
import io
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # Pillow is optional
    Image = None

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "sites" / "division2.immigration.go.th"
OMITTED = ROOT / "docs" / "division2-omitted-files.txt"
DOC_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".rar"}
MIN_INLINE = 2000          # leave tiny data URIs where they are
BIG_IMAGE = 500 * 1024
MAX_WIDTH = 1600

DATA_URI = re.compile(
    rb"data:((?:image|font)/[a-z0-9.+\-]+|application/(?:font-woff2?|x-font-[a-z]+|vnd\.ms-fontobject));base64,([A-Za-z0-9+/=]{%d,})" % MIN_INLINE
)
EXT_FOR_MIME = {
    b"image/jpeg": "jpg", b"image/jpg": "jpg", b"image/png": "png", b"image/gif": "gif",
    b"image/webp": "webp", b"image/svg+xml": "svg", b"image/x-icon": "ico",
    b"image/vnd.microsoft.icon": "ico", b"font/woff2": "woff2", b"font/woff": "woff",
    b"application/font-woff": "woff", b"application/font-woff2": "woff2",
    b"font/ttf": "ttf", b"application/x-font-ttf": "ttf", b"application/x-font-woff": "woff",
    b"application/vnd.ms-fontobject": "eot",
}

stats = {"inline_refs": 0, "inline_files": 0, "resized": 0, "omitted": 0, "copied": 0}
written_inline = set()


def safe(name: str) -> str:
    return name.replace("", "_q_").replace("?", "_q_")


def shrink(data: bytes, ext: str) -> bytes:
    """Downscale a large jpg/png; keep the original if that does not help."""
    if Image is None or ext not in ("jpg", "jpeg", "png") or len(data) <= BIG_IMAGE:
        return data
    try:
        im = Image.open(io.BytesIO(data))
        if im.width <= MAX_WIDTH:
            return data
        new = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
        out = io.BytesIO()
        if ext == "png":
            new.save(out, "PNG", optimize=True)
        else:
            new.convert("RGB").save(out, "JPEG", quality=82, optimize=True, progressive=True)
        if len(out.getvalue()) < len(data):
            stats["resized"] += 1
            return out.getvalue()
    except Exception as e:  # corrupt or unusual image: keep the original
        print(f"  could not shrink an image ({e})", file=sys.stderr)
    return data


def externalise(blob: bytes) -> bytes:
    def repl(m):
        ext = EXT_FOR_MIME.get(m.group(1).lower())
        if not ext:
            return m.group(0)
        stats["inline_refs"] += 1
        try:
            raw = base64.b64decode(m.group(2) + b"=" * (-len(m.group(2)) % 4))
        except Exception:
            return m.group(0)
        name = hashlib.sha1(raw).hexdigest()[:16] + "." + ext
        if name not in written_inline:
            target = DST / "_inline" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(shrink(raw, ext))
            written_inline.add(name)
            stats["inline_files"] += 1
        return b"/_inline/" + name.encode()
    return DATA_URI.sub(repl, blob)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, required=True, help="full division2.immigration.go.th crawl")
    args = ap.parse_args()
    src = args.src.resolve()
    if not src.is_dir():
        sys.exit(f"not a folder: {src}")

    omitted = []
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(src)
        ext = path.suffix.lower()
        if ext in DOC_EXT:
            omitted.append(f"{path.stat().st_size}\t{rel.as_posix().replace(chr(0xf03f), '?')}")
            stats["omitted"] += 1
            continue
        target = DST.joinpath(*[safe(p) for p in rel.parts])
        target.parent.mkdir(parents=True, exist_ok=True)
        data = path.read_bytes()
        if ext in (".html", ".htm", ".css"):
            data = externalise(data)
        elif ext in (".jpg", ".jpeg", ".png"):
            data = shrink(data, ext.lstrip("."))
        target.write_bytes(data)
        stats["copied"] += 1
        if stats["copied"] % 500 == 0:
            print(f"  {stats['copied']} files...", flush=True)

    OMITTED.parent.mkdir(exist_ok=True)
    OMITTED.write_text(
        "# Files left out of the lean division2 copy (bytes<TAB>path). They are in backup.zip.\n"
        + "\n".join(omitted) + "\n", encoding="utf-8")
    print(stats)


if __name__ == "__main__":
    main()
