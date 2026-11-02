# Audit of `backup.zip` — what blog existed, and what to mock

Source: Google Drive `backup.zip` (2.31 GB, 3,942 zip entries, 3,628 files, 2.84 GB unpacked) linked from the Trello cards
"NEW WEB main บก." and "NEW WEB second บก." (comment 2026-10-08). Unpacked read-only into `extracted/`; nothing was executed.

## 1. What the backup is

A **static crawl** (HTML + PDFs + images + fonts) of two live sites. It is not a database or WordPress export, so there is
no SQL and no server code. Links were rewritten by the crawler (`more_news.php?cid=212` became `more_news.phpcid=212.html`).

| Folder | Site | Trello card | Files |
|---|---|---|---|
| `division2.immigration.go.th/` | กองบังคับการตรวจคนเข้าเมือง 2 | **NEW WEB second บก.** | 3,504 |
| `admin-division2.immigration.go.th/` | ฝ่ายอำนวยการ บก.ตม.2 | **NEW WEB main บก.** | 124 |

`division2/ewtmgnbiz/ewt/` also holds **11 more subsite crawls** of the same CMS ("EWT"): imm2 (a copy of division2), dep,
cnx, hdy, ts, dmk, arr, voa, admin (a copy of admin-division2), hkt, inv. Most carry only a handful of seeded articles.

By type: 871 HTML (1.58 GB, mostly inline base64 images), 741 PDF, 72 DOCX, 55 XLSX, ~640 JPG/PNG, fonts, CSS/JS.

## 2. Which site has the blog

| | division2 (second บก.) | admin-division2 (main บก.) |
|---|---|---|
| Articles with content | **89** (+11 empty pages) | **4** |
| Date range | 2022-09-20 .. 2026-09-18 | 2023-12-26 .. 2025-07-16 |
| Real news posts | yes (press releases, operations, meetings, ITA) | **none** |
| What the 4 are | news + static pages | static pages only: structure, commanders, ITA 2567, ethics manual |
| Homepage news sections | filled | headings with "ดูทั้งหมด" but **no items** |
| Category pages | 17 | 20 (all menu entries, nothing behind them) |

So the main (admin) site has the full blog module wired up, with its sections and menus, but no posts.
Posts per year on division2: 2022: 2, 2023: 2, 2024: 37, 2025: 9, 2026: 39.

## 3. The blog's data model (what to mock)

One flat article type, one category per article. No tags or comments were seen in the mirrored pages.

| Field | What it holds | Notes |
|---|---|---|
| `title` | headline | Thai, 1 line |
| `date` | publish date | shown in Buddhist era (`18/09/2569`); store as Gregorian |
| `category` | exactly one | see section 4 |
| `author` | always `Admin` | never varies |
| `views` | visit counter | median 81, max 6,280 |
| `body` | HTML | median 696 chars, p90 4,066, max 8,941 |
| `featured image` | **not shown** | the template has the thumbnail block commented out |
| `attachments` | PDF 17, XLSX 4, DOC 1, XLS 1 | linked from the body, not a separate field |

Body mix (89 articles): 43 text + images, 10 text only, 8 image-only posters, 7 text + file, 21 with no body text and no image
in the mirrored HTML. Image posts average about 10 images each. Extras are rare: 7 tables, 3 iframes, 1 YouTube embed.

**Listing card** = title, date, view count, category, author, "อ่านเพิ่มเติม" (read more). Listing pages showed up to 10 cards.
**Article page** = title, date, category link, body, view counter, author "Admin", share buttons.

## 4. Categories (division2)

| cid | Category | Posts | Notes |
|---|---|---|---|
| 201 | ตัวชี้วัดที่ 9 การเปิดเผยข้อมูล | 16 | ITA indicator 9, 2024; half have attached files |
| 229 | คุณธรรม ความโปร่งใส และการป้องกันการทุจริต | 11 | 2026-07 |
| 212 | ข่าวประชาสัมพันธ์ทั่วไป | 10 | general news 2024-01 .. 2026-04 |
| 202 | ผลการปฏิบัติ | 10 | operations; long posts (avg 3,148 chars) |
| 216 | ตัวชี้วัดที่ 10 การป้องกันการทุจริต | 8 | 2024-02 |
| 224 | ภารกิจผู้บังคับบัญชา | 8 | commander activities, 2026 |
| 166 | เกี่ยวกับเรา | 7 | static "about" pages |
| 198 | มาตรฐาน ITA | 4 | |
| 172 | ติดต่อเรา | 3 | static |
| 214 | ผลการปฏิบัติ ITA | 3 | |
| 223 | ประชุมบริหาร บก.ตม.2 | 3 | 2026-04 |
| 227 | ข้อมูลพื้นฐานของหน่วยงาน | 3 | |
| 210 | กฏหมาย ระเบียบ | 2 | |
| 189 | ผู้บังคับบัญชา | 1 | static |

Also have listing pages but no posts in the mirror: 203 วีดีโอแนะนำ, 205 ประกาศจัดซื้อ จัดจ้าง, 206 บริการออนไลน์ และข้อมูลความรู้.
The admin site's menu adds: ผลการจับกุม, เอกสารสำคัญ, แจ้งร้องเรียนการทุจริต, ช่องทางการติดต่อ, อัตรากำลัง, อำนาจหน้าที่/พื้นที่รับผิดชอบ.

**Two kinds of content share one table:** (a) a news feed (press releases, operations, meetings) and (b) static pages
(about, commanders, structure, ITA, laws). In WordPress these should be posts vs pages.

## 5. Static pages are single images

Vision/mission, commanders, org structure, powers/areas and staffing have **no body text**, only one or two big images.
Rebuilding them as real text and structured data (names, ranks, photos) is part of the redesign.

## 6. Homepage layout (both sites share it)

top bar (phone 02-134-0841, email) → logo + name + mega-menu → 9-slide carousel (admin: 2) → e-service banner →
news sections → videos → document downloads → contact-back form (name, surname, phone, email, message, privacy consent) →
units list (หน่วยงานในสังกัด) → footer (address, map embed, quick links). The admin site adds a popup modal on load.

Menu: เกี่ยวกับเรา (vision/mission, commanders, structure, powers, staffing) · กฎหมาย/ระเบียบ · ข่าวประชาสัมพันธ์ (commander missions,
meetings, procurement, general) · มาตรฐาน ITA (2567/2568/2569) · ติดต่อเรา (contact, corruption complaint).

## 6b. Branding and assets to fill (copied to `assets-to-reuse/`)

| Asset | Where | Notes |
|---|---|---|
| Logo `imm_2.png` | `assets-to-reuse/logo_imm2_509x602.png` | the **same file** on all 13 sites |
| Favicon | `assets-to-reuse/favicon.ico` | same size as the logo (287,496 B), probably the PNG renamed; re-export a real `.ico` |
| Map marker icon | `icon_map-marker_512.png` | footer |
| Commanders photo page | `page_commanders_1142x1433.jpg` | one image; per-person photos need re-cropping |
| Vision/mission, structure, powers, staffing, complaint | `page_*.png/jpg` | infographic-style pages |
| Carousel banners | inline base64 in `index.html` | division2: 9 slides; the page embeds 38 inline images in total (87 MB, one is 18 MB); admin: 2 slides, 23 inline images (13 MB) |
| Article images | `ewtmgnbiz/ewt/imm2/images/` | 31 in root `images/` (2024-01/02 batches) |
| Attachments | `article_attach/`, `download/article/` | 13 + 11 files; PDFs/DOCX/XLSX |

Not in the backup: the admin site's own structure/commanders images (`ewt/imm2/images/articleimg_2024012318442979217.png`
and `ewt/merit/...2023122715363927352.png` are referenced but missing), and the old WordPress `newweb/wp-content/uploads/...` images
that the structure page links to.

## 7. Data-quality notes

- Dates are Buddhist-era; convert (2569 = 2026).
- 11 article pages are empty shells; 21 have no usable body.
- The homepage weighs ~118 MB because banners are inlined as base64. Do not reuse that.
- The two Division 2 commander names differ between `bk-tm2` and `admin-tm2` (see earlier discussion); verify before publishing.
- Subsites share article ids (e.g. 169-181 appear in many), so they look like template seeds rather than separate real content (inferred, not checked article by article).
- PDFs/DOCX/XLSX were **not opened**; they could contain personal data.
