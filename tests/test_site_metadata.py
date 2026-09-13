from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_landing_page_has_indexable_metadata() -> None:
    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    assert '<html lang="en">' in html
    assert '<meta name="description"' in html
    assert '<link rel="canonical" href="https://farukislamyt.github.io/spirt/">' in html
    assert 'property="og:title"' in html
    assert 'application/ld+json' in html
    assert '"codeRepository": "https://github.com/farukislamyt/spirt"' in html


def test_crawl_assets_exist() -> None:
    assert (ROOT / "site" / "robots.txt").is_file()
    assert (ROOT / "site" / "sitemap.xml").is_file()
