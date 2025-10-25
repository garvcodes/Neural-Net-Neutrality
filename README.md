
# Neural Net Neutrality — landing page (prototype)

This small prototype contains a polished landing page for Neural Net Neutrality: a project to track and visualize how large language models' political leanings change over time.

Files added:

- `public/index.html` — landing page HTML
- `public/css/styles.css` — styles and responsive layout
- `public/js/main.js` — tiny interactive enhancements
- `public/assets/logo.svg` — simple brand mark
- `docs/structure.md` — explanation and justification of directory layout

Preview locally

Open `public/index.html` in your browser, or serve with a small static server from the project root:

```bash
cd /Users/gg027/Desktop/NNN/public
python3 -m http.server 8000
# then open http://localhost:8000
```

Next steps (suggested):

- Wire up a data pipeline under `data/` and `scripts/` to ingest model outputs.
- Add a small React/Vue app under `src/` for interactive visualizations.
- Add tests for data ingestion and evaluation scoring.
