---
description: How to convert a Facebook Fanpage data export into a static Astro blog
---

# Facebook Fanpage → Astro Blog

This workflow converts a Facebook fanpage data export (JSON + media) into a fully-functional static blog built with [Astro](https://astro.build).

## Prerequisites

- **Node.js** ≥ 22 and **npm**
- **Python** ≥ 3.10
- A **Facebook data export** in JSON format (from Facebook's "Download Your Information" tool for a Page)

## Reference Implementation

The first implementation of this workflow was done for the **Pincho** fanpage at `/Volumes/MAC OS/backup/pincho.vn/`. All file references below are relative to that project as a template.

---

## Step 1: Understand the Facebook Export Structure

The Facebook export has a predictable structure. Verify it matches this pattern:

```
facebook.fanpage.backup/
└── this_profiles_activity_across_facebook/   (or this_profile's_...)
    └── posts/
        ├── profile_posts_1.json              ← Main posts data
        └── media/
            ├── Photos_<ID>/                  ← Photo attachments (JPG)
            ├── videos/                       ← Video attachments (MP4)
            ├── Coverphotos_<ID>/
            ├── Profilepictures_<ID>/
            └── ...
```

### JSON Structure per Post

Each post entry in the JSON array has this shape:

```json
{
  "timestamp": 1774011718,
  "attachments": [{
    "data": [{
      "media": {
        "uri": "this_profile's_activity_across_facebook/posts/media/Photos_<ID>/<filename>.jpg",
        "creation_timestamp": 1774011718,
        "media_metadata": { ... }
      }
    }]
  }],
  "data": [{
    "post": "<encoded post text>"
  }],
  "title": "Page Name added 4 new photos."
}
```

### Key Technical Details

> [!IMPORTANT]
> **Text Encoding**: Facebook exports UTF-8 text encoded as Latin-1 code points. You MUST decode it:
> ```python
> text.encode("latin-1").decode("utf-8")
> ```
> Example: `\u00c3\u00a1` in the JSON → `á` after decoding.

> [!WARNING]
> **Media Path Mismatch**: The JSON uses `this_profile's_activity_across_facebook` (curly quote) but the filesystem may use `this_profiles_activity_across_facebook` (no quote). The extraction script must handle both variants.

### Post Types to Handle

| Title Pattern | Type | Action |
|---|---|---|
| "...added N new photos." | Photo post | ✅ Extract text + photos |
| "...added a new photo." | Single photo post | ✅ Extract text + photo |
| "...added a new video." | Video post | ✅ Extract text (skip video) |
| "...shared a link." | Link share | ⏭️ Skip |
| "...shared a post." | Shared post | ⏭️ Skip |

---

## Step 2: Analyze the Fanpage Export

Run a quick analysis to understand the data before writing the script:

```bash
python3 -c "
import json, datetime
with open('<PATH_TO>/profile_posts_1.json', 'r') as f:
    data = json.load(f)
print(f'Total posts: {len(data)}')
with_content = sum(1 for p in data if any(d.get('post') for d in p.get('data',[])))
print(f'Posts with content: {with_content}')
timestamps = [p['timestamp'] for p in data]
print(f'Date range: {datetime.datetime.fromtimestamp(min(timestamps))} to {datetime.datetime.fromtimestamp(max(timestamps))}')
# Show a sample decoded post
for p in data:
    for d in p.get('data',[]):
        if d.get('post'):
            text = d['post'].encode('latin-1').decode('utf-8')
            print(f'Sample post:\n{text[:200]}')
            break
    else: continue
    break
"
```

This tells you:
- How many posts you're dealing with
- The date range
- Whether the text decoding works correctly
- What boilerplate footer patterns to strip (address, phone, slogan, hashtags)

---

## Step 3: Create the Python Extraction Script

Create `extract_fb_posts.py` in the project root. The script must handle:

### 3a. Configuration (customize per fanpage)

```python
# ─── CUSTOMIZE THESE PER FANPAGE ──────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
FB_BACKUP_DIR = SCRIPT_DIR / "facebook.fanpage.backup"
POSTS_JSON = FB_BACKUP_DIR / "this_profiles_activity_across_facebook" / "posts" / "profile_posts_1.json"
MEDIA_BASE = FB_BACKUP_DIR

ASTRO_DIR = SCRIPT_DIR / "blog"
CONTENT_DIR = ASTRO_DIR / "src" / "content" / "posts"
IMAGES_DIR = ASTRO_DIR / "public" / "images" / "posts"

# Boilerplate footer patterns to strip — CUSTOMIZE THESE per fanpage
FOOTER_PATTERNS = [
    r"Let['']s Party.*$",      # Page slogan
    r"_{2,}.*$",               # Divider lines
    r"PageName\s*-\s*.*$",     # Page name line
    r"▫️.*$",                  # Bullet points in footer
    r"Address:.*$",            # Physical address
    r"Hotline:.*$",            # Phone number
    r"#\w+.*$",                # Hashtag lines
]
```

### 3b. Core Functions (reusable as-is)

These functions are **page-agnostic** and should work without modification:

1. **`decode_fb_text(text)`** — Fixes Facebook's broken UTF-8 encoding
2. **`slugify(text)`** — Converts titles to URL-safe slugs
3. **`extract_hashtags(text)`** — Pulls `#tags` from post text
4. **`escape_yaml_string(s)`** — Escapes strings for YAML frontmatter
5. **`extract_title_and_body(text)`** — Splits first line as title, rest as body
6. **`generate_markdown(post_data)`** — Creates `.md` file with YAML frontmatter

### 3c. Post Processing (reusable with minor tweaks)

The `process_post()` function extracts:
- Timestamp → formatted date
- Post text → decoded, split into title + body
- Photo URIs → mapped to `/images/posts/<filename>.jpg`
- Hashtags → extracted as tags
- Slug → `YYYY-MM-DD-<slugified-title>`

### 3d. Image Copy Logic (reusable as-is)

Must handle the curly-quote vs straight-quote directory name mismatch, with fallback to filename-based search.

### 3e. Frontmatter Schema

Each generated `.md` file follows this format:

```yaml
---
title: "POST TITLE"
date: YYYY-MM-DD
description: "First ~150 chars of body text..."
images:
  - "/images/posts/<filename1>.jpg"
  - "/images/posts/<filename2>.jpg"
tags: ["tag1", "tag2"]
---

Body text of the post goes here.
```

**Reference**: See `/Volumes/MAC OS/backup/pincho.vn/extract_fb_posts.py` for the complete working implementation.

---

## Step 4: Create the Astro Project

// turbo
```bash
npx -y create-astro@latest ./blog --template minimal --install --no-git --skip-houston --yes
```

If dependencies fail to install:
// turbo
```bash
cd blog && npm install
```

---

## Step 5: Set Up Content Collection

Create `blog/src/content.config.ts`:

```typescript
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/posts' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    description: z.string().optional().default(''),
    images: z.array(z.string()).optional().default([]),
    tags: z.array(z.string()).optional().default([]),
  }),
});

export const collections = { posts };
```

This schema matches the frontmatter generated by the Python script.

---

## Step 6: Create Blog Theme

The blog needs these files, each customized with the fanpage's branding:

### 6a. `src/styles/global.css`

Dark-themed design system with:
- CSS custom properties for colors, fonts, spacing
- Warm accent color (gold/amber works well for restaurants)
- Glassmorphism sticky header
- Post card grid with hover animations
- Image gallery with responsive grid (1/2/3/4 column layouts)
- Lightbox overlay for full-screen image viewing
- Responsive breakpoints (768px, 480px)

### 6b. `src/layouts/BaseLayout.astro`

**Customize per fanpage:**
- Default title, description (line 11-13)
- Logo text and accent (line 39)
- Navigation links including Facebook URL (line 43)
- Footer content: name, address, phone (lines 56-58)
- `<html lang="">` attribute (line 20)

### 6c. `src/pages/index.astro`

**Customize per fanpage:**
- Hero `<h1>` text and subtitle (lines 23-28)

### 6d. `src/pages/posts/[slug].astro`

Post detail page with:
- Dynamic `getStaticPaths()` from content collection
- Adaptive image gallery grid (1-4 columns)
- Lightbox with keyboard navigation (Esc, ←, →)
- Previous/Next post navigation
- **Reusable as-is** — no per-fanpage customization needed

### 6e. `src/pages/tags/[tag].astro`

Tag filtering page — **reusable as-is**.

### 6f. `public/favicon.svg`

Simple SVG favicon with page initial:
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#1c1917"/>
  <text x="16" y="22" text-anchor="middle" font-family="Georgia, serif"
        font-weight="700" font-size="18" fill="#f59e0b">P</text>
</svg>
```

**Reference**: See `/Volumes/MAC OS/backup/pincho.vn/blog/src/` for all complete file implementations.

---

## Step 7: Run the Extraction

```bash
python3 extract_fb_posts.py
```

Expected output:
```
📖 Reading posts from: .../profile_posts_1.json
   Found <N> raw entries

✅ Done!
   📝 <N> posts written to: blog/src/content/posts
   🖼️  <N> images copied to: blog/public/images/posts
   ⏭️  <N> entries skipped (link shares, empty posts)
```

---

## Step 8: Build and Verify

// turbo
```bash
cd blog && npm run build
```

The build should show all pages generated (posts + tags + homepage) with zero errors.

```bash
cd blog && npm run dev
```

Open `http://localhost:4321` and verify:
- [ ] Homepage hero and header render with correct branding
- [ ] Post grid shows cards with images, dates, titles, and tags
- [ ] Vietnamese/non-ASCII text renders correctly
- [ ] Individual post pages show image gallery and content
- [ ] Lightbox opens on image click, keyboard navigation works
- [ ] Tag pages filter posts correctly
- [ ] Previous/Next navigation works between posts

---

## Per-Fanpage Customization Checklist

When reusing this workflow for a new fanpage, customize these:

| File | What to Change |
|---|---|
| `extract_fb_posts.py` | `FB_BACKUP_DIR` path, `FOOTER_PATTERNS` regex list |
| `BaseLayout.astro` | Title, description, logo text, Facebook URL, footer info, `lang` attr |
| `index.astro` | Hero heading, subtitle text |
| `global.css` | Accent color (`--color-accent`), font choice |
| `favicon.svg` | Initial letter, brand color |
| `astro.config.mjs` | `site` URL |

Everything else (content schema, post page, tag page, lightbox, extraction logic) is **reusable without changes**.
