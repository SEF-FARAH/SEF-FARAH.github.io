"""Vérifications statiques du site HECHMI.TECH. Usage : python tests/check_site.py"""
import re, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = {
    "index.html": "fr",
    "mentions-legales.html": "fr",
    "en/index.html": "en",
    "en/legal-notice.html": "en",
}
FORBIDDEN = [r"0?6\s?07\s?11\s?54\s?57", r"\+33\s?6\s?07"]  # téléphone : mentions légales uniquement
SECTIONS = ["accueil", "expertise", "references", "parcours", "technique", "contact"]


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang, self.title, self.ids, self.links, self.hreflang = None, False, set(), [], set()
        self.meta_desc = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self.title = True
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.meta_desc = True
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "link" and a.get("rel") == "alternate" and a.get("hreflang"):
            self.hreflang.add(a["hreflang"])
        for attr in ("href", "src"):
            if a.get(attr):
                self.links.append(a[attr])


def check():
    errors = []
    for rel, lang in PAGES.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"{rel}: fichier manquant")
            continue
        html = path.read_text(encoding="utf-8")
        c = Collector()
        c.feed(html)
        if c.lang != lang:
            errors.append(f"{rel}: lang={c.lang!r}, attendu {lang!r}")
        if not c.title:
            errors.append(f"{rel}: <title> manquant")
        if not c.meta_desc:
            errors.append(f"{rel}: meta description manquante")
        if not {"fr", "en"} <= c.hreflang:
            errors.append(f"{rel}: hreflang fr/en manquants")
        if rel.endswith("index.html"):
            for pat in FORBIDDEN:
                if re.search(pat, html):
                    errors.append(f"{rel}: téléphone hors mentions légales")
            for s in SECTIONS:
                if s not in c.ids:
                    errors.append(f"{rel}: section #{s} manquante")
            if "11 Allée" in html:
                errors.append(f"{rel}: adresse complète hors mentions légales")
        for link in c.links:
            if link.startswith(("http", "mailto:", "tel:", "#", "data:")):
                continue
            target = (path.parent / link.split("#")[0]).resolve()
            if not target.exists():
                errors.append(f"{rel}: lien cassé -> {link}")
    for f in ("assets/css/style.css", "robots.txt", "sitemap.xml"):
        if not (ROOT / f).exists():
            errors.append(f"{f}: fichier manquant")
    return errors


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    errs = check()
    for e in errs:
        print("FAIL", e)
    print("OK" if not errs else f"{len(errs)} erreur(s)")
    sys.exit(1 if errs else 0)
