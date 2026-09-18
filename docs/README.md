# Docs sources (MindGrip AI)

Authoring sources for the **docs-web** React app.

| Path | Role |
|------|------|
| `source/*.html` | Rich pages → extracted to `docs-web/public/fragments/` |
| `source/*.mdx` | Markdown stubs / sources (glossary, directory map, …) |
| `source/optional_tooling.html` | MuJoCo + keyboard optional tooling |
| `source/policy_cheatsheet.html` | Policy cheatsheet (roadmap-style) |
| `so101_mujoco.md` | Extra MuJoCo notes (points at Optional Tooling) |

## Frontend

```bash
cd docs-web && npm install && npm run dev
# → http://localhost:8000/
```

Rebuild HTML fragments after editing `source/*.html`:

```bash
python3 docs-web/scripts/extract_fragments.py
```

Full site map: [`docs-web/README.md`](../docs-web/README.md)

Official LeRobot docs: https://huggingface.co/docs/lerobot
