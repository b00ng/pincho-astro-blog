#!/usr/bin/env python3
"""
Extract Facebook fanpage posts from exported JSON and generate
Astro-compatible Markdown content files with frontmatter.

Usage:
    python3 extract_fb_posts.py

Reads:  facebook.fanpage.backup/this_profiles_activity_across_facebook/posts/profile_posts_1.json
Writes: blog/src/content/posts/*.md + blog/public/images/posts/*.jpg
"""

import json
import os
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent.resolve()
FB_BACKUP_DIR = SCRIPT_DIR / "facebook.fanpage.backup"
POSTS_JSON = FB_BACKUP_DIR / "this_profiles_activity_across_facebook" / "posts" / "profile_posts_1.json"
MEDIA_BASE = FB_BACKUP_DIR  # URIs in JSON are relative to this

ASTRO_DIR = SCRIPT_DIR / "blog"
CONTENT_DIR = ASTRO_DIR / "src" / "content" / "posts"
IMAGES_DIR = ASTRO_DIR / "public" / "images" / "posts"

# Boilerplate footer patterns to strip from post body
FOOTER_PATTERNS = [
    r"Let['']s Party.*$",
    r"_{2,}.*$",
    r"Pincho\s*-\s*Tapas\s*kitchen.*$",
    r"Pincho\s*-\s*thu.*$",
    r"Pincho\s*-\s*một trong.*$",
    r"▫️.*$",
    r"Address:.*$",
    r"Hotline:.*$",
    r"#\w+.*$",
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def decode_fb_text(text: str) -> str:
    """Facebook exports UTF-8 text encoded as Latin-1 code points. Decode it."""
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text


def slugify(text: str) -> str:
    """Convert a string to a URL-friendly slug."""
    # Normalize unicode and convert to ASCII-friendly form
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text[:60].strip("-") or "post"


def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags from text, return as lowercase tag list."""
    tags = re.findall(r"#(\w+)", text)
    return list(dict.fromkeys(t.lower() for t in tags))  # dedupe, preserve order


def clean_body(text: str) -> str:
    """Strip boilerplate footer content from post body."""
    lines = text.split("\n")
    cleaned = []
    stop = False
    for line in lines:
        stripped = line.strip()
        # Check if this line starts the boilerplate footer
        for pattern in FOOTER_PATTERNS:
            if re.match(pattern, stripped, re.IGNORECASE | re.DOTALL):
                stop = True
                break
        if stop:
            break
        cleaned.append(line)

    # Remove trailing empty lines
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()

    return "\n".join(cleaned)


def extract_title_and_body(text: str) -> tuple[str, str]:
    """
    Split post text into title (first non-empty line) and body (rest).
    Many Pincho posts start with an English title on the first line.
    """
    lines = text.strip().split("\n")
    title = ""
    body_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped:
            title = stripped
            body_start = i + 1
            break

    # Skip blank lines between title and body
    while body_start < len(lines) and not lines[body_start].strip():
        body_start += 1

    body = "\n".join(lines[body_start:])
    return title, body


def escape_yaml_string(s: str) -> str:
    """Escape a string for YAML double-quoted values."""
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    return s


# ─── Post Processing ─────────────────────────────────────────────────────────

def process_post(post: dict) -> dict | None:
    """
    Process a single Facebook post entry.
    Returns a dict with extracted fields, or None if the post should be skipped.
    """
    timestamp = post.get("timestamp", 0)
    dt = datetime.fromtimestamp(timestamp)

    # Extract post text
    raw_text = ""
    for d in post.get("data", []):
        if d.get("post"):
            raw_text = decode_fb_text(d["post"])
            break

    # Extract media URIs (photos only for blog)
    photo_uris = []
    video_uris = []
    for attachment in post.get("attachments", []):
        for item in attachment.get("data", []):
            media = item.get("media", {})
            uri = media.get("uri", "")
            if uri.endswith(".jpg") or uri.endswith(".png") or uri.endswith(".jpeg"):
                photo_uris.append(uri)
            elif uri.endswith(".mp4"):
                video_uris.append(uri)

    # Check for external link shares (skip these)
    has_external = any(
        "external_context" in item
        for attachment in post.get("attachments", [])
        for item in attachment.get("data", [])
    )

    # Skip posts with no real content
    if not raw_text and not photo_uris:
        return None
    if has_external and not raw_text and not photo_uris:
        return None
    # Skip pure link-shares with no content
    if has_external and not photo_uris:
        return None

    # Extract hashtags before cleaning
    tags = extract_hashtags(raw_text) if raw_text else []

    # Extract title and body
    if raw_text:
        title, body = extract_title_and_body(raw_text)
        body = clean_body(body)
    else:
        title = f"Post from {dt.strftime('%B %d, %Y')}"
        body = ""

    # Generate description (first ~150 chars of body)
    desc_text = body.replace("\n", " ").strip()
    description = desc_text[:150].rsplit(" ", 1)[0] + "..." if len(desc_text) > 150 else desc_text

    # Build slug from date + title
    slug = f"{dt.strftime('%Y-%m-%d')}-{slugify(title)}"

    # Map photo URIs to destination paths
    images = []
    for uri in photo_uris:
        filename = os.path.basename(uri)
        images.append(f"/images/posts/{filename}")

    return {
        "slug": slug,
        "title": title,
        "date": dt.strftime("%Y-%m-%d"),
        "datetime": dt,
        "description": description,
        "body": body,
        "images": images,
        "photo_uris": photo_uris,  # source paths for copying
        "video_uris": video_uris,
        "tags": tags,
    }


# ─── Markdown Generation ─────────────────────────────────────────────────────

def generate_markdown(post_data: dict) -> str:
    """Generate an Astro-compatible Markdown file with frontmatter."""
    lines = ["---"]
    lines.append(f'title: "{escape_yaml_string(post_data["title"])}"')
    lines.append(f'date: {post_data["date"]}')
    lines.append(f'description: "{escape_yaml_string(post_data["description"])}"')

    if post_data["images"]:
        lines.append("images:")
        for img in post_data["images"]:
            lines.append(f'  - "{img}"')

    if post_data["tags"]:
        tag_str = ", ".join(f'"{t}"' for t in post_data["tags"])
        lines.append(f"tags: [{tag_str}]")

    lines.append("---")
    lines.append("")

    if post_data["body"]:
        lines.append(post_data["body"])
        lines.append("")

    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"📖 Reading posts from: {POSTS_JSON}")
    with open(POSTS_JSON, "r", encoding="utf-8") as f:
        posts = json.load(f)

    print(f"   Found {len(posts)} raw entries")

    # Create output directories
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    processed = []
    skipped = 0
    seen_slugs = set()

    for post in posts:
        result = process_post(post)
        if result is None:
            skipped += 1
            continue

        # Handle duplicate slugs
        slug = result["slug"]
        if slug in seen_slugs:
            counter = 2
            while f"{slug}-{counter}" in seen_slugs:
                counter += 1
            slug = f"{slug}-{counter}"
            result["slug"] = slug
        seen_slugs.add(slug)

        processed.append(result)

    # Sort by date (newest first in the list, but file naming is chronological)
    processed.sort(key=lambda p: p["datetime"])

    # Write markdown files and copy images
    images_copied = 0
    for post_data in processed:
        # Write markdown
        md_path = CONTENT_DIR / f"{post_data['slug']}.md"
        md_content = generate_markdown(post_data)
        md_path.write_text(md_content, encoding="utf-8")

        # Copy images
        for uri in post_data["photo_uris"]:
            # The URI in JSON uses curly quotes: "this_profile's_activity_across_facebook/..."
            # but the actual filesystem uses a straight quote
            src = MEDIA_BASE / uri
            if not src.exists():
                # Try with the directory name as it appears on disk
                alt_uri = uri.replace(
                    "this_profile's_activity_across_facebook",
                    "this_profiles_activity_across_facebook"
                )
                src = MEDIA_BASE / alt_uri
            if not src.exists():
                # Try finding by filename directly
                filename = os.path.basename(uri)
                # Search in known media directories
                for search_dir in [
                    MEDIA_BASE / "this_profiles_activity_across_facebook" / "posts" / "media",
                    MEDIA_BASE / "this_profile's_activity_across_facebook" / "posts" / "media",
                ]:
                    if search_dir.exists():
                        for root, _, files in os.walk(search_dir):
                            if filename in files:
                                src = Path(root) / filename
                                break
                    if src.exists():
                        break

            dst = IMAGES_DIR / os.path.basename(uri)
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
                images_copied += 1
            elif not src.exists():
                print(f"   ⚠️  Image not found: {uri}")

    print(f"\n✅ Done!")
    print(f"   📝 {len(processed)} posts written to: {CONTENT_DIR}")
    print(f"   🖼️  {images_copied} images copied to: {IMAGES_DIR}")
    print(f"   ⏭️  {skipped} entries skipped (link shares, empty posts)")
    print(f"\n   Next: cd blog && npm install && npm run dev")


if __name__ == "__main__":
    main()
