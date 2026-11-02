# legacy-sites

Read-only copies of the two **old** Immigration Division 2 websites, so the old
structure, header/footer and content can be looked at while the new WordPress
sites are built. These are static crawls (HTML, PDFs, images). There is no
database and no PHP: nginx just serves the files.

| Site | Folder in `sites/` | Port | In git? |
|---|---|---|---|
| **admin-division2** (site one, ฝ่ายอำนวยการ บก.ตม.2), 124 files, 43 MB | `admin-division2.immigration.go.th` | **8091** | yes |
| **division2** (site two, กองบังคับการตรวจคนเข้าเมือง 2), 3,504 files, 2.9 GB | `division2.immigration.go.th` | **8090** | no, too big (see below) |

The new sites are in a separate repo (the WordPress/Elementor "foundry").

## Run it on another PC

You need Git and Docker (Docker Desktop on Windows/macOS, or Docker Engine on Linux).

```bash
git clone https://github.com/Subhavich/legacy-sites.git
cd legacy-sites
docker compose up -d
```

Open **http://localhost:8091** for the old admin-division2 site. Stop it with
`docker compose down`.

If a port is busy, pick others:
`ADMIN_PORT=18091 DIVISION2_PORT=18090 docker compose up -d`.

## Also get division2 (optional, 2.9 GB)

`sites/division2.immigration.go.th` is not in git. It comes from the original
`backup.zip` (2.3 GB, a Google Drive link on the Trello cards "NEW WEB main บก."
and "NEW WEB second บก.", comment of 2026-10-08).

You need Python 3.8+ (no extra packages):

```bash
python tools/prepare.py --zip /path/to/backup.zip
docker compose up -d
```

That extracts both sites into `sites/` and renames files as described below.
Then open **http://localhost:8090**. Add `--site division2.immigration.go.th`
to extract only that one. Allow about 3 GB of free disk space.

## Why `tools/prepare.py` and the `_q_` names

The crawler saved `more_news.php?cid=208` as a file named
`more_news.php?cid=208.html`. Windows cannot store `?` in a filename, so the
backup holds a private-use stand-in character (U+F03F). Docker Desktop on
Windows quietly maps it back, but a Mac, Linux, or a fresh Windows checkout
would answer 404 for every category and article page.

So the repo stores that character as `_q_` (`more_news.php_q_cid=208.html`) and
[nginx.conf](nginx.conf) rewrites a request for `more_news.php?cid=208.html`
(the links inside the pages say `more_news.php%3Fcid=208.html`) to that name.
If you add or re-extract crawled files by hand, run `python tools/prepare.py`
once to rename them.

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
tools/prepare.py     extract from backup.zip and rename "?" files
docs/BLOG-AUDIT.md   what is in the backup
sites/               the crawls (division2 is git-ignored)
```
