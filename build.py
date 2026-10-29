#!/usr/bin/env python3
"""
Build Luca Boggiani's portfolio site.

    python build.py            # content.yaml + template.html  ->  dist/
    python build.py --serve    # build, then preview at http://localhost:8000
    python build.py --watch    # like --serve, and rebuild whenever you save a file

Edit content.yaml for text/projects/colours; edit template.html only for layout/style.
"""
import argparse, html, json, shutil, sys, threading, time
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: run  pip install pyyaml")

ROOT = Path(__file__).parent
CONTENT = ROOT / "content.yaml"
TEMPLATE = ROOT / "template.html"
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"
ICONS = {"ur", "gait", "vision", "bci", "arm", "boat", "rover"}


# ---------------------------------------------------------------- validation
def check(content):
    """Catch common mistakes early with readable messages."""
    errors = []
    for key in ("site", "home", "projects"):
        if key not in content:
            errors.append(f"content.yaml is missing the '{key}:' section")
    if errors:
        return errors

    slugs = [p.get("slug") for p in content["projects"]]
    for i, p in enumerate(content["projects"], 1):
        where = f"project #{i} ({p.get('title', 'untitled')})"
        for f in ("slug", "title", "kind", "summary", "abstract"):
            if not p.get(f):
                errors.append(f"{where}: missing '{f}'")
        if p.get("icon") not in ICONS:
            errors.append(f"{where}: icon '{p.get('icon')}' unknown, use one of {sorted(ICONS)}")
        for s in p.get("sections", []):
            if "title" not in s:
                errors.append(f"{where}: a section has no 'title'")
    dupes = {s for s in slugs if slugs.count(s) > 1}
    if dupes:
        errors.append(f"duplicate project slugs: {sorted(dupes)}")

    for u in content.get("updates", []):
        if u.get("project") and u["project"] not in slugs:
            errors.append(f"update '{u.get('title')}' links to unknown project '{u['project']}'")
    for e in content.get("experience", []):
        if e.get("project") and e["project"] not in slugs:
            errors.append(f"experience '{e.get('title')}' links to unknown project '{e['project']}'")

    cv = content["site"].get("cv_file")
    if cv and not (ROOT / cv).exists():
        errors.append(f"CV file not found: {cv}")
    return errors


# ---------------------------------------------------------------- build
def font_url(font):
    if font == "Archivo":  # keeps the variable-width axis the design uses
        return "https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,300..800;1,100,400&display=swap"
    return f"https://fonts.googleapis.com/css2?family={font.replace(' ', '+')}:wght@300..800&display=swap"


def css_vars(d):
    return "".join(f"--{k}:{v};" for k, v in d.items())


def build():
    content = yaml.safe_load(CONTENT.read_text(encoding="utf-8"))
    problems = check(content)
    if problems:
        print("✗ Fix these in content.yaml:")
        for p in problems:
            print("   -", p)
        return False

    site, theme = content["site"], content.get("theme", {})
    font = theme.get("font", "Archivo")
    theme.setdefault("font", font)

    # copy assets (CV, images…) next to index.html
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    if ASSETS.exists():
        shutil.copytree(ASSETS, DIST / "assets")

    site["cv_url"] = site.get("cv_file") or ""
    data = dict(content, theme=theme)

    links = [f'      <a href="mailto:{html.escape(site["email"])}">Email</a>']
    if site.get("linkedin"):
        links.append(f'      <a href="{html.escape(site["linkedin"])}">LinkedIn</a>')
    if site.get("github"):
        links.append(f'      <a href="{html.escape(site["github"])}">GitHub</a>')
    if site.get("cv_file"):
        links.append(f'      <a href="{html.escape(site["cv_file"])}" download>Download CV</a>')

    page = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "__PAGE_TITLE__": html.escape(site.get("page_title", site["name"])),
        "__DESCRIPTION__": html.escape(site.get("description", ""), quote=True),
        "__FONT_URL__": font_url(font),
        "__FONT__": font,
        "__LIGHT_VARS__": css_vars(theme.get("light", {})),
        "__DARK_VARS__": css_vars(theme.get("dark", {})),
        "__INITIALS__": html.escape(site.get("initials", "")),
        "__NAME__": html.escape(site["name"]),
        "__FOOTER__": html.escape(site.get("footer", "")),
        "__FOOTER_LINKS__": "\n".join(links),
        # JSON inside <script>: escape "</" so text can never close the tag
        "__SITE_JSON__": json.dumps(data, ensure_ascii=False).replace("</", "<\\/"),
    }
    for key, value in replacements.items():
        page = page.replace(key, value)

    (DIST / "index.html").write_text(page, encoding="utf-8")
    n = len(content["projects"])
    print(f"✓ Built dist/index.html  ({n} projects, {len(page)//1024} KB)  {time.strftime('%H:%M:%S')}")
    return True


# ---------------------------------------------------------------- preview
def serve(port):
    import functools, http.server
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    handler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"→ Preview at http://localhost:{port}  (Ctrl+C to stop)")


def watch():
    files = [CONTENT, TEMPLATE] + list(ASSETS.rglob("*"))
    stamp = lambda: [f.stat().st_mtime for f in files if f.exists()]
    last = stamp()
    while True:
        time.sleep(0.7)
        now = stamp()
        if now != last:
            last = now
            try:
                build()
            except yaml.YAMLError as e:
                print("✗ YAML error (check indentation / quotes):\n", e)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serve", action="store_true", help="preview locally after building")
    ap.add_argument("--watch", action="store_true", help="preview and rebuild on every save")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    try:
        ok = build()
    except yaml.YAMLError as e:
        sys.exit(f"✗ YAML error (check indentation / quotes):\n{e}")
    if not ok and not a.watch:
        sys.exit(1)
    if a.serve or a.watch:
        serve(a.port)
        try:
            watch() if a.watch else threading.Event().wait()
        except KeyboardInterrupt:
            print("\nbye")
