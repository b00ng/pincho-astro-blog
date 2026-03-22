# Pincho.vn Restaurant Template — Full Multi-Page Redesign

Redesign the Pincho.vn Astro blog into a full restaurant website inspired by the ThemeFisher Restaurant Bootstrap template. The original is a single-page scrolling site; we'll expand it into **6 dedicated pages** while keeping the visual language: diagonal pinstripe overlays, parallax sections, checkerboard blog layout, warm orange accent, elegant serif + sans-serif typography.

## Design DNA (from Restaurant Bootstrap analysis)

| Element | Original | Pincho Adaptation |
|---|---|---|
| Accent color | `#FF530A` | `#E65100` (warm burnt orange) |
| Headers | `#2E2E2E` charcoal | Same |
| Body text | `#959595` medium gray | Same |
| Backgrounds | White, `#F6F6F6` | White, `#F8F7F5` warm off-white |
| Display font | Twentieth Century MT | **Playfair Display** (free serif) |
| Body font | Open Sans | **Outfit** (clean modern sans) |
| Overlay | Diagonal pinstripe PNG on black 30% opacity | CSS `repeating-linear-gradient` |
| Hero | Full-viewport bg image + overlay + centered text | Same |
| Navbar | `navbar-fixed-top`, transparent → white on scroll | Sticky, `backdrop-filter: blur()` |
| Blog | Checkerboard alternating image/text 50/50 rows | Same pattern |
| Menu | Dotted-line separator between name and price | Same |
| Animations | WOW.js + Animate.css scroll-triggered | CSS `@keyframes` + Intersection Observer |
| Contact | Form + 3-col info (contact, recent posts, gallery) | Same structure |
| Footer | Simple copyright bar | Same |

---

## Pages & File Map

### 1. HOME — [index.astro](file:///Volumes/MAC%20OS/backup/pincho.vn/blog/src/pages/index.astro) `[MODIFY]`

| Section | Description |
|---|---|
| **Hero** | Full-viewport bg image, pinstripe overlay `::before`, large Playfair heading "Tapas Kitchen & Drinks", subtitle, "Explore Menu" CTA button |
| **About Preview** | Centered chef illustration/photo, heading with `<span>` accent words, 2-3 line intro to Pincho, "Read Our Story →" link |
| **Featured Menu** | 4-6 signature dishes with name, price, short description, dotted separator — 2-column grid. "View Full Menu" CTA |
| **Blog Preview** | 4 latest posts in checkerboard pattern (alternating image-left/text-right), parallax divider between pairs. "View All Stories" CTA |
| **Newsletter CTA** | Full-width parallax bg, "Subscribe to Our Newsletter" heading, email input + teal `#7EC3BB` submit button |
| **Contact Strip** | Address, phone, hours in a horizontal bar |

### 2. ABOUT US — [about.astro](file:///Volumes/MAC%20OS/backup/pincho.vn/blog/src/pages/about.astro) `[NEW]`

| Section | Description |
|---|---|
| **Page Hero** | Parallax background with overlay, page title "About Us" centered |
| **Our Story** | 2-column: left text (Pincho's history, philosophy, fusion cuisine vision), right image (restaurant interior/chef) |
| **Stats Counter** | 4 animated counters: Years Open, Dishes Served, Happy Guests, Team Members — `bounceIn` on scroll |
| **Meet the Team** | Grid of chef/staff cards: photo, name, role — hover to reveal short bio |
| **Quote/Philosophy** | Full-width parallax section with a large italic quote from the chef |

### 3. BLOG — [posts/index.astro](file:///Volumes/MAC%20OS/backup/pincho.vn/blog/src/pages/posts/index.astro) `[NEW]`

| Section | Description |
|---|---|
| **Page Hero** | Parallax bg + overlay + title "Our Stories" |
| **Blog Grid** | Checkerboard alternating layout: odd rows = image-left/content-right, even rows = content-left/image-right. Each item: thumbnail, title, date, excerpt, "Read More" link. Speech-bubble CSS arrow pointing to image |
| **Pagination** | Previous / page numbers / Next at bottom |

> [!NOTE]
> Existing `[slug].astro` post detail page is preserved with refinements (breadcrumb, refined typography). Tag page `[tag].astro` updated to match new design.

### 4. MENU — [menu.astro](file:///Volumes/MAC%20OS/backup/pincho.vn/blog/src/pages/menu.astro) `[NEW]`

| Section | Description |
|---|---|
| **Page Hero** | Parallax bg + overlay + title "Our Menu" |
| **Category Tabs** | Horizontal filter tabs: Tapas, Main Courses, Brunch/Bruncho, Drinks, Desserts |
| **Menu Items** | Two-column list per category. Each item: dish name (left), price (right), dotted border connector, 1-line description below. Optional small food image |
| **Chef's Special** | Full-width highlight section with large image + description for a featured dish |

> [!IMPORTANT]
> Menu data will be stored in a new content collection `src/content/menu/` with YAML/MD files per category, or a single `menu.json` data file. This keeps menu items editable without touching Astro components.

### 5. NEWS — Uses Blog Collection (no separate page)

The original template's NEWS section is the same as BLOG. For Pincho, we combine news into the blog posts collection using tags to differentiate (e.g., `#news`, `#announcement`). The blog page already serves this purpose.

### 6. CONTACT — [contact.astro](file:///Volumes/MAC%20OS/backup/pincho.vn/blog/src/pages/contact.astro) `[NEW]`

| Section | Description |
|---|---|
| **Page Hero** | Parallax bg + overlay + title "Contact Us" |
| **Contact Form** | Name, Email, Message fields + "Send Your Message" button (Formspree/Netlify Forms) |
| **Info Columns** | 3-column grid: (1) Phone, Address, Email with FA icons; (2) Latest Blog posts mini-list; (3) Photo thumbnails grid + Social media icons |
| **Map** | Embedded Google Maps iframe showing 34C Cao Ba Quat, Ba Dinh, Hanoi |

---

## Shared Components & Layout

### [MODIFY] [BaseLayout.astro](file:///Volumes/MAC%20OS/backup/pincho.vn/blog/src/layouts/BaseLayout.astro)

- **Sticky Navbar**: Logo left, nav links right (Home, About, Blog, Menu, Contact). Semi-transparent white `rgba(255,255,255,0.89)` with backdrop blur. Mobile hamburger → slide-in drawer
- **Footer**: 3-column grid (Quick Links, Contact Info, Social + Gallery thumbnails) + bottom copyright bar
- **Body class prop**: Accept `bodyClass` to apply page-specific classes (e.g., `post-page` for dark theme on detail pages)
- **Fonts**: Playfair Display (headings) + Outfit (body) from Google Fonts
- **Icons**: Font Awesome 6 CDN

### [NEW] Reusable Components (`src/components/`)

| Component | Purpose |
|---|---|
| `PageHero.astro` | Parallax hero with overlay, title, optional subtitle — used on About, Blog, Menu, Contact |
| `SectionHeader.astro` | "Main Title **Accent Title**" pattern with decorative underline |
| `MenuItem.astro` | Dish name + dotted line + price + description |
| `BlogCard.astro` | Checkerboard blog card with image, title, date, excerpt, arrow |
| `ContactForm.astro` | Name/Email/Message form with submit |
| `NewsletterCTA.astro` | Parallax section with email signup |
| `StatsCounter.astro` | Animated number counters |
| `TeamCard.astro` | Staff photo + name + role |
| `MobileMenu.astro` | Hamburger icon + slide-in overlay nav |

---

## Styles

### [MODIFY] [global.css](file:///Volumes/MAC%20OS/backup/pincho.vn/blog/src/styles/global.css)

Complete rewrite with these systems:

- **Light base theme** for all public pages (white/off-white backgrounds, dark text)
- **Dark theme** preserved for post detail pages via `.post-page` body class
- **Pinstripe overlay** via CSS `repeating-linear-gradient` on `::before` pseudo-elements
- **Parallax** via `background-attachment: fixed` on hero and divider sections
- **Checkerboard grid** using `nth-child(even)` to flip image/content order
- **Speech-bubble arrow** via rotated `::before` square on content blocks
- **Dotted menu lines** via `border-bottom: 1px dotted #C9C9C9` between name/price
- **Scroll animations** via `IntersectionObserver` + CSS `@keyframes` (fadeInUp, fadeInLeft, bounceIn)
- **Hover effects**: image `scale(1.1) rotate(2deg)`, button lifts, link underline grow
- **Responsive breakpoints**: 1200px, 992px, 768px, 480px

---

## Data Layer

### [MODIFY] [content.config.ts](file:///Volumes/MAC%20OS/backup/pincho.vn/blog/src/content.config.ts)

Add a `menu` collection for menu items:

```typescript
const menu = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/menu' }),
  schema: z.object({
    category: z.string(),
    name: z.string(),
    price: z.string(),
    description: z.string().optional(),
    image: z.string().optional(),
    featured: z.boolean().optional().default(false),
    order: z.number().optional().default(0),
  }),
});
```

### [NEW] `src/content/menu/` directory

Sample menu item files (e.g., `tapas-patatas-bravas.md`):
```yaml
---
category: "Tapas"
name: "Patatas Bravas"
price: "95,000₫"
description: "Crispy potatoes with smoky aioli and spicy tomato sauce"
order: 1
---
```

---

## Verification Plan

1. Start dev server on port 4322
2. **Homepage**: Verify hero, about preview, featured menu, blog checkerboard, newsletter, contact strip
3. **About**: Verify story section, stats counter animation, team cards, quote
4. **Blog**: Verify checkerboard layout, pagination, click-through to post detail
5. **Menu**: Verify category tabs, dotted-line items, chef's special
6. **Contact**: Verify form rendering, 3-col info, embedded map
7. **Post detail**: Verify dark theme, gallery, lightbox, prev/next nav
8. **Mobile**: Resize to 375px — verify hamburger menu, stacked sections
9. **Navigation**: Test all nav links cycle through every page correctly
