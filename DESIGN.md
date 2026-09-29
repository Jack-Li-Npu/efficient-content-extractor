# Frontend redesign

Applied [Taste Skill's redesign-existing-projects workflow](https://github.com/Leonxlnx/taste-skill/tree/main/skills/redesign-skill) on 2026-09-27. Taste Skill is a development aid; installing it is not required to run this application.

## Design read

A personal reading workspace for turning long YouTube conversations into usable text. Prioritize readable captions, a clear source-to-transcript relationship, and quiet tools. Preserve the existing React/Vite/Tailwind stack and caption-only backend.

## Audit and changes

- The tall hero, full-width input, large video card, and transcript were stacked vertically. Replaced the stack with a compact introduction and an asymmetric desktop workspace: source/settings on the left, transcript on the right.
- The old interface mixed navy glass panels, a logo watermark, gold gradients, and cyan accents. Replaced these with a warm neutral canvas, white reading surface, and one rust accent. Source metadata uses separators rather than nested cards.
- Font names were declared without actual font files. Added self-hosted Geist and Geist Mono through locked Fontsource dependencies. Font files are served locally; no external font-service requests are required. OFL licenses are included under `frontend/public/licenses/`.
- Simplified export around the user’s next step: one timestamped Markdown download for Codex, plus a full-transcript copy action that includes the prepared prompt. Removed the format selector, timestamp toggle, and per-line copy controls.
- Improved paragraph size and contrast, tabular timestamps, keyboard focus, touch targets, and mobile stacking.
- Search now highlights literal matches. Clear-search and no-results states keep the reader oriented. Search still filters the view only; copy and exports retain the entire transcript.
- Restyled empty, loading, and inline error states. The example action fills the URL field; New transcript resets the workspace and returns focus to the link field.

## Design rules

- Main type: Geist Variable. Timestamps and small structural labels: Geist Mono Variable.
- Background: `#f6f6f2`; surface: white; ink: `#292a26`; accent: `#b54830`.
- Radius: 8px for controls, 12px for the reading surface, smaller radii for nested details.
- Desktop content is constrained to 1440px. Below 768px, the source and reader stack; below 400px, export controls compress without horizontal scrolling.
- Motion is limited to short section entrances and loading placeholders. Caption lines have no entry delay. Reduced-motion preferences disable animations and smooth scrolling.
- Existing Lucide icons stay consistent; the favicon uses the library's captions icon.
- No new AI services, media retrieval, history persistence, or external font tracking.

## Verification

See the redesign section in [VERIFICATION.md](VERIFICATION.md) for build, browser, and responsive checks.

## Codex handoff refinement — 2026-09-27

The reading workspace now prepares source material for a separate Codex chat. The Ready for Codex section exposes the two handoff paths and the exact request to use. Caption language selection and search remain because they affect source choice and inspection. Timestamp visibility is permanent. The source panel, typography, colors, and captions-only backend are unchanged. The page does not imply automatic upload or in-browser analysis.
