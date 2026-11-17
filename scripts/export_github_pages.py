"""Turon Odob-Ilm platformasini GitHub Pages uchun statik HTML/CSS/media to'plamiga eksport qiladi."""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django  # noqa: E402

django.setup()

from django.core.management import call_command  # noqa: E402
from django.test import Client  # noqa: E402

from apps.branches.models import Branch, MapLink  # noqa: E402
from apps.content.models import NewsPost  # noqa: E402

GITHUB_PAGES_ORIGIN = "https://aliyevogabek894-cmyk.github.io"
GITHUB_PAGES_BASE = f"{GITHUB_PAGES_ORIGIN}/google-maps/"
RENDER_DEPLOY_URL = "https://render.com/deploy?repo=https://github.com/aliyevogabek894-cmyk/google-maps"

ATTR_URL_RE = re.compile(
    r'(?P<attr>\b(?:href|src|data-lightbox-src))="(?P<url>/[^"]*)"'
)


def _rewrite_html(html: str, depth: int, map_targets: dict[str, str]) -> str:
    prefix = "../" * depth

    # GitHub Pages statik rejim meta belgisi va mutlaq domen yo'llari
    static_meta = '  <meta name="turon-static-mode" content="1">\n'
    if 'name="turon-static-mode"' not in html:
        html = html.replace('<meta name="viewport"', static_meta + '  <meta name="viewport"', 1)

    html = html.replace(
        f"{GITHUB_PAGES_ORIGIN}/",
        GITHUB_PAGES_BASE,
    )

    # Kuzatiladigan /xarita/ linklarini bevosita rasmiy Google/Yandex manziliga almashtirish
    for tracked_path, target_url in map_targets.items():
        html = html.replace(f'href="{tracked_path}"', f'href="{target_url}"')

    def _replace_attr(match: re.Match[str]) -> str:
        attr = match.group("attr")
        url = match.group("url")
        if url.startswith("//"):
            return match.group(0)
        if url == "/":
            target = "./" if depth == 0 else prefix
            return f'{attr}="{target}"'
        if url.startswith("/boshqaruv/") or url.startswith("/admin/"):
            return f'{attr}="{prefix}boshqaruv/kirish/"'
        rel = url.lstrip("/")
        return f'{attr}="{prefix}{rel}"'

    return ATTR_URL_RE.sub(_replace_attr, html)


def export_static_site(output_dir: Path) -> dict[str, int]:
    """Barcha ommaviy sahifalarni va media fayllarni output_dir papkasiga eksport qiladi."""
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    call_command("seed_demo")

    map_targets: dict[str, str] = {}
    for link in MapLink.objects.select_related("branch").filter(is_active=True):
        map_targets[link.get_tracked_url()] = link.target_url

    routes = [
        "/",
        "/maktab-haqida/",
        "/it-akademiya/",
        "/talim/",
        "/yangiliklar/",
        "/galereya/",
        "/qabul/",
        "/filiallar/",
        "/fikrlar/",
        "/aloqa/",
        "/maxfiylik-siyosati/",
    ]
    for branch in Branch.objects.filter(is_active=True):
        routes.append(f"/filiallar/{branch.slug}/")
    for post in NewsPost.objects.filter(is_published=True):
        routes.append(f"/yangiliklar/{post.slug}/")

    client = Client(raise_request_exception=True)
    rendered_count = 0

    for route in routes:
        res = client.get(
            route,
            HTTP_HOST="aliyevogabek894-cmyk.github.io",
            secure=True,
        )
        if res.status_code != 200:
            raise RuntimeError(f"Sahifa render qilinmadi: {route} -> HTTP {res.status_code}")

        rel_route = route.strip("/")
        depth = 0 if not rel_route else len(rel_route.split("/"))
        html = _rewrite_html(res.content.decode("utf-8"), depth=depth, map_targets=map_targets)

        out_path = output_dir / "index.html" if not rel_route else output_dir / rel_route / "index.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        rendered_count += 1

    # Boshqaruv/Admin kirish sahifasi uchun tushunarli ma'lumot sahifasi
    admin_info_dir = output_dir / "boshqaruv" / "kirish"
    admin_info_dir.mkdir(parents=True, exist_ok=True)
    (admin_info_dir / "index.html").write_text(
        f"""<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Boshqaruv paneli — Turon Odob-Ilm</title>
  <link rel="icon" type="image/png" href="../../static/official_media/logo.png">
  <link rel="stylesheet" href="../../static/css/main.css">
</head>
<body>
  <main class="section">
    <div class="container">
      <div class="card card-gold-top" style="max-width:640px; margin:24px auto; text-align:center;">
        <img class="crest-medallion" src="../../static/official_media/logo.png" alt="Turon Odob-Ilm gerbi" style="margin:0 auto 14px;">
        <h1>Xodimlar monitoring paneli</h1>
        <p style="color:var(--muted);">
          Xodimlar kirishi, arizalarni boshqarish va statistika paneli Python/Django backend serverida (Render) ishlaydi.
          GitHub Pages’da maktabning ommaviy vitrina sayti joylashgan.
        </p>
        <div class="btn-group-wrap" style="justify-content:center;">
          <a href="../../" class="btn btn-primary">Bosh sahifaga qaytish</a>
          <a href="{RENDER_DEPLOY_URL}" target="_blank" rel="noopener noreferrer" class="btn btn-gold">Render serverini ochish &nearr;</a>
        </div>
      </div>
    </div>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )

    # GitHub Pages 404 sahifasi
    home_res = client.get("/sahifa-topilmadi/", HTTP_HOST="aliyevogabek894-cmyk.github.io", secure=True)
    if home_res.status_code == 404:
        html_404 = _rewrite_html(home_res.content.decode("utf-8"), depth=0, map_targets=map_targets)
    else:
        html_404 = (
            '<!DOCTYPE html><html lang="uz"><head><meta charset="utf-8">'
            '<meta http-equiv="refresh" content="0; url=./"></head><body>'
            '<a href="./">Turon Odob-Ilm bosh sahifasiga o‘tish</a></body></html>'
        )
    (output_dir / "404.html").write_text(html_404, encoding="utf-8")

    # Statik fayllar va media nusxalash
    static_src = BASE_DIR / "static"
    if static_src.exists():
        shutil.copytree(static_src, output_dir / "static", dirs_exist_ok=True)

    media_src = BASE_DIR / "media"
    if media_src.exists():
        shutil.copytree(media_src, output_dir / "media", dirs_exist_ok=True)

    # Jekyll filtratsiyasini o'chirish (.nojekyll)
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")

    # Ichki asset havolalari mavjudligini tekshirish
    missing_assets: list[str] = []
    for html_file in output_dir.rglob("*.html"):
        rel_dir = html_file.parent
        content = html_file.read_text(encoding="utf-8")
        for m in re.finditer(r'(?:href|src|data-lightbox-src)="([^"]+)"', content):
            val = m.group(1).split("#")[0].split("?")[0]
            if not val or val.startswith(("http://", "https://", "tel:", "mailto:")):
                continue
            resolved = (rel_dir / val).resolve()
            if resolved.is_dir():
                resolved = resolved / "index.html"
            if not resolved.exists():
                missing_assets.append(f"{html_file.relative_to(output_dir)} -> {val}")

    if missing_assets:
        raise RuntimeError(f"Statik eksportda topilmagan fayllar bor: {missing_assets[:5]}")

    total_files = sum(1 for p in output_dir.rglob("*") if p.is_file())
    total_bytes = sum(p.stat().st_size for p in output_dir.rglob("*") if p.is_file())
    return {"pages": rendered_count, "files": total_files, "bytes": total_bytes}


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE_DIR / ".gh_pages_dist"
    stats = export_static_site(target)
    print(f"Eksport yakunlandi: {stats['pages']} ta sahifa, {stats['files']} ta fayl, {stats['bytes']} bayt -> {target}")
