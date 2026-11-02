#!/usr/bin/env python3
"""Prepare the legacy-site crawls for serving (standard library only).

The crawler turned URLs like  more_news.php?cid=208  into files named
more_news.php?cid=208.html.  Windows cannot store "?" in a name, so the
backup holds U+F03F (a private-use stand-in) instead.  Neither form is
portable, so this script stores the character as "_q_" and nginx.conf
rewrites incoming requests to match:

    more_news.php?cid=208.html  ->  more_news.php_q_cid=208.html

Usage
    python tools/prepare.py                    # rename names already under sites/
    python tools/prepare.py --zip backup.zip   # extract both sites from the zip, then rename
    python tools/prepare.py --zip backup.zip --site admin-division2.immigration.go.th
"""
import argparse
import shutil
import sys
import zipfile
from pathlib import Path

SITES = Path(__file__).resolve().parent.parent / "sites"
ALL_SITES = ["admin-division2.immigration.go.th", "division2.immigration.go.th"]
QUESTION_MARKS = ("", "?")


def safe(name: str) -> str:
    for q in QUESTION_MARKS:
        name = name.replace(q, "_q_")
    return name


def extract(zip_path: Path, wanted: list) -> int:
    count = 0
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            parts = info.filename.replace("\\", "/").split("/")
            # The zip is laid out as backup/<site>/<files...>
            for i, part in enumerate(parts[:2]):
                if part in wanted:
                    rest = parts[i + 1:]
                    break
            else:
                continue
            if not rest or any(p in ("", ".", "..") for p in rest):
                continue  # refuse odd or escaping paths
            target = SITES.joinpath(part, *[safe(p) for p in rest])
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst, 1024 * 1024)
            count += 1
            if count % 500 == 0:
                print(f"  extracted {count} files...", flush=True)
    return count


def normalise(root: Path) -> int:
    renamed = 0
    # deepest paths first, so renaming a folder never invalidates a pending path
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        new = safe(path.name)
        if new != path.name:
            target = path.with_name(new)
            if target.exists():
                print(f"skip (target exists): {path}", file=sys.stderr)
                continue
            path.rename(target)
            renamed += 1
    return renamed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zip", type=Path, help="original backup.zip to extract from")
    ap.add_argument("--site", action="append", help="site folder to extract (repeatable); default: both")
    args = ap.parse_args()

    SITES.mkdir(exist_ok=True)
    if args.zip:
        wanted = args.site or ALL_SITES
        print(f"Extracting {', '.join(wanted)} from {args.zip} ...")
        print(f"  {extract(args.zip, wanted)} files written")
    print(f"Renamed {normalise(SITES)} names containing '?'")
    for site in ALL_SITES:
        have = (SITES / site).is_dir()
        print(f"  {site}: {'present' if have else 'MISSING'}")


if __name__ == "__main__":
    main()
