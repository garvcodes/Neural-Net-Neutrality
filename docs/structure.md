# Directory structure justification


This project will accumulate data, scripts, and a small web UI. The layout below is intentionally simple and follows common conventions to make it easy for collaborators to find code and data.

- `public/` — static site content (HTML, CSS, JS, images). This is the lightweight landing site and a convenient place to host static visualizations or a single-page app build output.

- `src/` — application source (React/Vue/Svelte components, TypeScript). Separating `src` makes it clear where dynamic app code belongs versus static site assets.

- `data/` — raw and processed datasets (time-series outputs, evaluation results). Keep data under version control only for small samples; large datasets should be stored externally (S3, Zenodo) and referenced with metadata files here.

- `scripts/` — ingestion, scoring and reproducible analysis scripts (Python/Node). These scripts transform raw model outputs into scored time-series used by visualizations.

- `docs/` — design notes, methodology, and the justification you're reading. Keep experimental protocols and scoring rubrics here so results remain auditable.

- `tests/` — tests for scoring logic, data transforms, and visualization snapshots.

Why this layout?

- Clarity: static site and assets are separate from app source and data. That reduces accidental mixing and keeps deploys simple.
- Auditable: keeping scoring scripts and methodology in `scripts/` and `docs/` makes it clear how numbers were produced.
- Extensible: adding a `src/` SPA later is straightforward — the build output can target `public/`.

Security & data notes

- Do not commit large/binary datasets; use external storage and keep a `data/README.md` with pointers and access instructions.
- Keep any secret keys out of the repository — use environment variables or secret stores for integrations.

Branding note

This repository's landing page and docs now use the project name "Neural Net Neutrality" (NNN). The color palette was intentionally chosen to be neutral, low-saturation tones so the visual emphasis stays on data and methodology rather than branding color psychology.

Security & data notes

- Do not commit large/binary datasets; use external storage and keep a `data/README.md` with pointers and access instructions.
- Keep any secret keys out of the repository — use environment variables or secret stores for integrations.
