# legacy-sites

Read-only copies of the two **old** Immigration Division 2 websites, so the old
structure, header/footer and content can be looked at while the new WordPress
sites are built. These are static crawls (HTML, images, CSS). There is no
database and no PHP: nginx just serves the files.

| Site | Folder in `sites/` | Port | Size in git |
|---|---|---|---|
| **admin-division2** (site one, ฝ่ายอำนวยการ บก.ตม.2) | `admin-division2.immigration.go.th` | **8091** | 43 MB, complete |
| **division2** (site two, กองบังคับการตรวจคนเข้าเมือง 2) | `division2.immigration.go.th` | **8090** | ~450 MB, **lean copy** (see below) |

The new sites are in a separate repo (the WordPress/Elementor "foundry").

## Run it on another PC

You need Git and Docker (Docker Desktop on Windows/macOS, or Docker Engine on Linux).
Allow roughly 1 GB of disk space.

```bash
git clone https://github.com/Subhavich/legacy-sites.git
cd legacy-sites
docker compose up -d
```

- **http://localhost:8091** the old admin-division2 site
- **http://localhost:8090** the old division2 site

Stop it with `docker compose down`. If a port is busy, pick others:
`ADMIN_PORT=18091 DIVISION2_PORT=18090 docker compose up -d`.

## What "lean copy" means for division2

The original division2 crawl is 2.9 GB, too big for git. The copy in this repo
keeps every page, stylesheet, script and image, and drops the weight:

- **Inline images:** about 1.5 GB of it was the same few hundred pictures
  embedded as base64 inside ~850 HTML pages. They are now shared files in
  `sites/division2.immigration.go.th/_inline/` and the pages point at them.
- **Documents are not included:** 880 PDF / Word / Excel files (about 900 MB).
  Links to them answer 404 locally. The full list is in
  [docs/division2-omitted-files.txt](docs/division2-omitted-files.txt).
- **Big photos are downscaled** to at most 1600 px wide (73 files).

The page text, layout and structure are unchanged. Rebuild it from the original
with `python tools/slim.py --src <full division2 folder>` (needs Pillow for the
photo step).

### Getting the original files (optional)

The untouched crawl is `backup.zip` (2.3 GB), a Google Drive link on the Trello
cards "NEW WEB main บก." and "NEW WEB second บก." (comment of 2026-10-08).
Python 3.8+ is enough:

```bash
python tools/prepare.py --zip /path/to/backup.zip
```

This extracts both sites into `sites/` and **overwrites** the lean files with
the originals (heavy pages with embedded images, plus the PDFs and Word files).
Use `git checkout -- sites` to go back to the lean copy.

## Why the `_q_` names

The crawler saved `more_news.php?cid=208` as a file named
`more_news.php?cid=208.html`. Windows cannot store `?` in a filename, so the
backup holds a private-use stand-in character (U+F03F). Docker Desktop on
Windows quietly maps it back, but a Mac, Linux, or a fresh Windows checkout
would answer 404 for every category and article page.

So the repo stores that character as `_q_` (`more_news.php_q_cid=208.html`) and
[nginx.conf](nginx.conf) rewrites a request for `more_news.php?cid=208.html`
(the links inside the pages say `more_news.php%3Fcid=208.html`) to that name.
`tools/prepare.py` and `tools/slim.py` both apply the rename.

## What the old admin-division2 site has

- Top bar: phone 02-134-0841, email saraban_imm2@police.go.th, Google Translate.
- Header: crest and "ฝ่ายอำนวยการ บก.ตม.2", a white menu bar, and a pop-up banner on load.
- Menu: หน้าแรก; เกี่ยวกับเรา (วิสัยทัศน์/พันธกิจ, ผู้บังคับบัญชา, โครงสร้างองค์กร,
  อำนาจหน้าที่/พื้นที่รับผิดชอบ, อัตรากำลัง); กฎหมาย/ระเบียบ; ข่าวประชาสัมพันธ์
  (ทั่วไป, ผลการปฏิบัติงาน, ผลการปฏิบัติ ITA, จัดซื้อจัดจ้าง); มาตรฐาน ITA;
  ติดต่อเรา (ติดต่อเรา, แจ้งร้องเรียนการทุจริต, ช่องทางการติดต่อ).
- Home page: image slider, e-service cards, commanders, news / arrest results /
  videos / documents sections, and the list of affiliated units.
- Footer: address, phone, a quick-links column, a Google Map, "Copyright © 2024".
- Data: only 4 real articles (structure, commanders, ITA 2567, ethics manual).
  15 of the 20 category pages say "ไม่มีข้อมูล" (no data).

See [docs/BLOG-AUDIT.md](docs/BLOG-AUDIT.md) for the full audit of what the
backup contains, including division2's 89 articles.

## Layout

```
docker-compose.yml   nginx on ports 8090 / 8091
nginx.conf           one server block per site, plus the "?" rewrite
tools/slim.py        builds the lean division2 copy from the full crawl
tools/prepare.py     extract from backup.zip and rename "?" files
docs/                BLOG-AUDIT.md, division2-omitted-files.txt
sites/               the two crawls
```
