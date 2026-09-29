# Repository landing page design

## Scope and design read

Applied [design-taste-frontend](https://github.com/Leonxlnx/taste-skill) to the repository README on 2026-09-29. This is a preservation redesign of GitHub's repository landing surface, not a separate website or a change to the extractor UI.

Reading this as a repository landing page for people reviewing long videos, with a clean, product-first language using GitHub-native Markdown and the supplied product screenshots.

- `DESIGN_VARIANCE: 5`: left-aligned introduction and a visual narrative within GitHub's single-column content area.
- `MOTION_INTENSITY: 1`: static screenshots and native disclosure controls.
- `VISUAL_DENSITY: 3`: short introduction, prominent evidence, and technical detail revealed on demand.

## Audit before changes

The existing README established the purpose, upstream attribution, two real screenshots, setup, platform plans, and detailed developer documentation. Several paragraphs and a five-item workflow preceded the first image. Retrieval details repeated across the introduction and capability list. Installation internals and API details carried the same visual weight as the demo.

The app's established visual identity is warm neutral with rust accents and Geist typography. The provided screenshots preserve that identity. GitHub owns the surrounding typography, link color, spacing, focus behavior, and theme. No custom font, CSS framework, decorative generated image, or animation is appropriate to this Markdown surface. There is no custom metadata, analytics, or routing to migrate.

## Changes and preservation

- Bring the extraction screenshot into the opening section, after a short purpose statement and navigation links.
- Show the Codex result as the second visual, retaining both original screenshots without edits or duplicate embeds.
- Condense the workflow around source retrieval, manual handoff, and selective watching.
- Group current capabilities in a short comparison table, separate from the clearly planned platform adapters and extension.
- Keep quick-start commands visible; collapse setup internals, example context, API details, and development commands into native disclosures.
- Preserve all previous headings and anchors, source attribution, license, setup commands, proxy instructions, limitations, and developer documentation.

## Pre-flight review

Applicable skill checks: plain readable copy, no em-dashes, no invented metrics, meaningful alt text, real screenshots, no decorative labels or fake UI, no extra dependencies, and no claims that planned features work today. The 685-segment example is visible in the supplied screenshot. The opening description has 19 words.

GitHub provides the page's responsive layout, theme, focus controls, and disclosure interaction. No fixed-width table is used to position screenshots. Screenshots remain their authentic light-theme captures when the surrounding GitHub page is dark. Standalone-site checks for custom buttons, forms, motion, viewport heroes, and CSS tokens do not apply to a README.

Verification: GitHub's Markdown API rendered both images and all four disclosure blocks. Local image/document links, preserved heading names, balanced disclosures, whitespace, and prohibited dash characters were checked. Both screenshots were already published unchanged in the previous commit. Browser automation timed out twice, so desktop/mobile and light/dark visual review could not be completed in this session. Lighthouse was not run against GitHub's host page; its performance is outside this README's implementation.
