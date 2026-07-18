---
name: Olimazi
description: A personal working lab for showing what one person can build with AI.
colors:
  graph-paper: "#D9DEDC"
  graph-paper-deep: "#BFD5CC"
  surface: "#EEF3F1"
  ink: "#303737"
  ink-muted: "#56615E"
  mint-accent: "#70C9AA"
  mint-deep: "#2A745D"
  mint-text: "#226D57"
  field-olive: "#46534F"
  field-sand: "#AAB8B3"
  button-text: "#F4F8F6"
  dark-graph-paper: "#282E2D"
  dark-graph-paper-deep: "#34463F"
  dark-surface: "#313A37"
  dark-ink: "#E4ECE9"
  dark-ink-muted: "#B5C1BD"
  dark-mint-text: "#8DE0C1"
  dark-field-olive: "#A8C1B7"
  dark-field-sand: "#65736E"
typography:
  display:
    fontFamily: "Satoshi, Segoe UI, system-ui, sans-serif"
    fontSize: "clamp(54px, 9vw, 96px)"
    fontWeight: 900
    lineHeight: 0.98
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Satoshi, Segoe UI, system-ui, sans-serif"
    fontSize: "clamp(26px, 3.6vw, 40px)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Satoshi, Segoe UI, system-ui, sans-serif"
    fontSize: "clamp(30px, 4.4vw, 48px)"
    fontWeight: 700
    lineHeight: 1.02
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Satoshi, Segoe UI, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 500
    lineHeight: 1.75
  label:
    fontFamily: "IBM Plex Mono, Consolas, monospace"
    fontSize: "10px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.14em"
rounded:
  control: "2px"
  card: "20px"
spacing:
  xs: "10px"
  sm: "14px"
  md: "20px"
  gutter: "28px"
  lg: "40px"
  section-head: "54px"
  section: "96px"
components:
  button-primary:
    backgroundColor: "{colors.mint-deep}"
    textColor: "{colors.button-text}"
    rounded: "{rounded.control}"
    padding: "15px 38px"
    height: "50px"
  button-ghost:
    backgroundColor: "{colors.graph-paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "7px 12px"
    height: "35px"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "20px 22px 24px"
  chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.field-olive}"
    rounded: "{rounded.control}"
    padding: "4px 9px"
---

# Design System: Olimazi

## Overview

**Creative North Star: "The Working Lab Notebook"**

Olimazi looks like an active working surface: cool graph paper, hand-drawn formulas and diagrams, precise mono annotations, decisive sans-serif headlines, and real project imagery. The system is deliberately personal and process-visible. It should feel like someone opened a useful notebook and showed the evidence, not like a software company assembled a marketing template.

The visual system supports the locked “personal concept” framing and the line “proof over pitch.” Dense background notation supplies curiosity and continuity; strong type and ruled sections keep the page legible; photographs and screenshots make claims concrete. The site must never drift into a generic AI landing page, a subscription-bookkeeping SaaS sales page, or a falsely finished product story.

**Key Characteristics:**

- Cool mint graph-paper palette with a functional light/dark pair.
- Satoshi-led hierarchy, mono operational labels, and handwritten background notation.
- Image-first project narratives with visible process and evidence.
- Ruled, asymmetric layouts rather than repetitive card grids.
- Flat working surfaces with selective lift for featured imagery and dialogs.

## Colors

The active palette is the single root token set in `index.html`; light and dark values are paired deliberately and must travel together.

### Primary

- **Working Mint:** The main accent for emphasis, the marquee, active marks, and selected brand moments.
- **Deep Mint:** Primary actions and strong interactive states.
- **Mint Text:** Accessible accent copy and links on the graph-paper surfaces.

### Neutral

- **Graph Paper:** The default page canvas and source of the notebook character.
- **Graph Paper Deep:** Secondary strips, carousel controls, and tonal separation.
- **Surface:** Cards, captions, fields, and contained reading surfaces.
- **Ink:** Headlines, primary copy, hard rules, and the closing-section ground.
- **Muted Ink:** Supporting copy, metadata, and captions.
- **Field Olive / Field Sand:** Quiet operational labels and supporting neutral detail.

**The Paired Theme Rule.** Any new semantic color must be resolved for both the active light and dark themes before it ships.

**The Existing Tokens Rule.** Use the CSS custom properties already defined in `index.html`; do not introduce a parallel palette.

## Typography

**Display Font:** Satoshi (with Segoe UI and system sans fallbacks)

**Body Font:** Satoshi (with Segoe UI and system sans fallbacks)

**Label/Mono Font:** IBM Plex Mono (with Consolas and monospace fallbacks)

**Annotation Font:** Architects Daughter (with Segoe Print and cursive fallbacks)

**Character:** Satoshi provides direct, modern confidence; IBM Plex Mono makes operational detail feel recorded and inspectable; Architects Daughter is reserved for the background working-notebook layer.

### Hierarchy

- **Display** (900, fluid display scale, 0.98): Hero statements only.
- **Headline** (700, fluid headline scale, 1.15): Section titles and major narrative turns.
- **Title** (700, fluid title scale, 1.02): Featured project titles.
- **Body** (500, 15px baseline, 1.75): Explanations and project context; keep readable measures near the existing 560–690px caps.
- **Label** (600, 10px, 0.14em, uppercase): Navigation, keys, statuses, captions, and compact operational metadata.

**The Three-Voice Rule.** Satoshi carries the story, IBM Plex Mono records the evidence, and Architects Daughter stays in the background notation. Do not swap their jobs.

## Elevation

The system is flat by default and uses lines, tonal surfaces, clipped corners, and slight rotation to establish hierarchy. Lift is selective: featured media uses the shared ambient shadow, hover adds a soft drop-shadow response, and native dialogs use the strongest elevation.

### Shadow Vocabulary

- **Featured media:** The shared `--shadow` token lifts carousels and important image surfaces.
- **Interactive media hover:** A soft drop shadow appears when a project carousel is hovered or focused.
- **Dialog:** The strongest shadow is reserved for modal content over a dark backdrop.

**The Evidence Gets Lift Rule.** Shadows belong to screenshots, imagery, and dialogs—not routine text sections.

## Components

### Buttons

- **Shape:** Precise, nearly square controls (2px radius).
- **Primary:** Deep mint with light button text, a 50px minimum height, and generous horizontal padding.
- **Hover / Focus:** Darken or shift to ink, lift by 2px where already defined, and preserve the 3px mint focus outline with 4px offset.
- **Secondary / Ghost:** Transparent or graph-paper controls with a one-pixel line and mono uppercase labels.

### Chips

- **Style:** Small mono uppercase labels with a one-pixel olive outline and 2px radius.
- **State:** Informational only in the current site; do not imply selection behavior that does not exist.

### Cards / Containers

- **Corner Style:** Featured personal cards use 20px foundations with deliberate asymmetric corner variants; project carousels use clipped corners.
- **Background:** Surface tokens over graph paper.
- **Shadow Strategy:** Cards remain mostly flat; featured project media receives ambient lift.
- **Border:** One-pixel shared line tokens.
- **Internal Padding:** Compact 20–24px card padding; larger narrative sections rely on whitespace rather than nested cards.

### Inputs / Fields

- **Style:** Native select controls use the surface color, a one-pixel light border, 2px radius, and 50px minimum height.
- **Focus:** Preserve the global visible focus outline.
- **Error / Disabled:** No custom states exist; do not invent them without a scoped packet.

### Navigation

The fixed navigation uses a translucent graph-paper background, one-pixel bottom rule, and restrained blur. The wordmark is Satoshi; links and controls use compact mono labels. At smaller widths the text links disappear while Contact and Theme remain available.

### Project Carousel

Project carousels are the signature evidence component: real imagery or screenshots, mono captions, explicit previous/next controls, a live status count, clipped corners, and a subtle resting rotation that straightens on hover or focus.

## Do's and Don'ts

### Do:

- **Do** lead with real screenshots, photographs, artifacts, and traceable context.
- **Do** use the active mint CSS custom properties and preserve both theme variants.
- **Do** keep project narratives image-first and operational details easy to scan.
- **Do** preserve keyboard controls, visible focus, reduced-motion behavior, semantic structure, and alt text.
- **Do** use ruled sections, graph-paper texture, and selective asymmetry to maintain the working-notebook character.

### Don't:

- **Don't** turn Olimazi into “a tools platform or finished product company.”
- **Don't** make the tracker section resemble “a subscription-bookkeeping SaaS sales page.”
- **Don't** build “a pitch-led AI landing page that substitutes claims for working evidence.”
- **Don't** present “a polished success story that hides constraints, uncertainty, or unfinished learning.”
- **Don't** introduce new colors, fonts, dependencies, decorative gradients, glassmorphism, or repetitive identical card grids without explicit packet scope.
