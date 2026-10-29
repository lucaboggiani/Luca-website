# lucaboggiani.netlify.app — website source

Everything you normally change lives in **`content.yaml`**. Python turns it into the site.

```
content.yaml   ← text, projects, experience, skills, colours, font
template.html  ← layout & styling (only touch for design changes)
assets/        ← CV PDF and any other files (copied to the site as-is)
build.py       ← builds the site into dist/
```

## 1. Setup (once)
```bash
pip install -r requirements.txt
```

## 2. Edit and preview
```bash
python build.py --watch
```
Open http://localhost:8000. Every time you save `content.yaml` the site rebuilds; refresh the browser to see it.
If you make a typo (bad indentation, unknown project link, missing CV…) the terminal tells you exactly what to fix.

## 3. Common edits
| I want to… | Do this in `content.yaml` |
|---|---|
| Add a project | Copy an existing block under `projects:`, give it a new `slug`. Set `featured: true` to show it on the home page. |
| Link GitHub code | Add `code: https://github.com/...` to the project |
| Change the status line / intro | `home: status:` / `home: intro:` |
| Add a news item | Add an entry at the top of `updates:` (optionally `project: <slug>` to link it) |
| Update the CV | Replace `assets/Boggiani_Luca_CV.pdf` (same name) |
| Change colours | `theme: light:` / `theme: dark:` (hex colours) |
| Change font | `theme: font:` any Google Font name, e.g. `Inter` |
| Bold text | Wrap in `**double stars**` |

Project icons: `ur`, `gait`, `vision`, `bci`, `arm`, `boat`, `rover`.

## 4. Publish to Netlify
**Option A, drag & drop:** run `python build.py`, then drag the `dist/` folder onto your site's *Deploys* page on app.netlify.com.

**Option B, automatic (recommended):** push this folder to a GitHub repo and link it in Netlify (*Site configuration → Build & deploy → Link repository*). `netlify.toml` already tells Netlify how to build, so every `git push` updates the site.
