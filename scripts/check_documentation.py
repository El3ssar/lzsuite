"""Validate source documentation, runnable guide snippets, and the built site."""

from __future__ import annotations

import ast
import hashlib
import inspect
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def check_source():
    """Check NumPy sections against signatures and execute Python guide blocks."""
    from numpydoc.docscrape import NumpyDocString

    import lzsuite

    count = 0
    for path in (ROOT / "src/lzsuite").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                assert doc, f"{path}:{node.lineno}: missing docstring"
                parsed = NumpyDocString(doc)
                params = [arg.arg for arg in (*node.args.posonlyargs, *node.args.args)]
                params += [arg.arg for arg in node.args.kwonlyargs]
                if node.args.vararg:
                    params.append("*" + node.args.vararg.arg)
                if node.args.kwarg:
                    params.append("**" + node.args.kwarg.arg)
                documented = [p.name for p in parsed["Parameters"]]
                assert params == documented, (path.name, node.name, params, documented)
                count += 1
    for name in lzsuite.__all__:
        function = getattr(lzsuite, name)
        parsed = NumpyDocString(inspect.getdoc(function))
        assert parsed["Returns"], f"{name}: missing Returns"
        assert parsed["Examples"], f"{name}: missing Examples"

    blocks = 0
    for path in sorted((ROOT / "docs").rglob("*.md")):
        namespace = {"__name__": "__docs_example__"}
        for match in re.finditer(
            r"^```python\n(.*?)^```", path.read_text(encoding="utf-8"), re.M | re.S
        ):
            code = match.group(1)
            try:
                exec(compile(code, str(path), "exec"), namespace)
            except Exception as error:
                raise RuntimeError(
                    f"Failed snippet in {path.relative_to(ROOT)}:\n{code}"
                ) from error
            blocks += 1
    print(f"Validated {count} function docstrings and executed {blocks} Python guide snippets.")


class Page(HTMLParser):
    """Collect local references, anchors, and images without a browser dependency."""

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.ids = set()
        self.references = []
        self.social = {}
        self.in_head = False
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "head":
            self.in_head = True
        if tag == "meta":
            key = attrs.get("property", attrs.get("name", ""))
            if key.startswith(("og:", "twitter:")):
                assert self.in_head, f"{self.path}: social metadata must be in the head"
                assert key not in self.social, f"{self.path}: duplicate social tag {key}"
                self.social[key] = attrs.get("content", "")
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag in {"a", "link", "img", "script"}:
            ref = attrs.get("href" if tag in {"a", "link"} else "src")
            if ref:
                self.references.append(ref)
        if tag == "img":
            assert "alt" in attrs, f"{self.path}: image missing alt attribute"
            if "/figures/" in attrs.get("src", ""):
                assert attrs["alt"].strip(), f"{self.path}: plot needs descriptive alt text"

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False


def check_site():
    """Check all local assets/anchors and the complete generated public reference."""
    site = ROOT / "site"
    pages = {path.resolve(): Page(path) for path in site.rglob("*.html")}
    from PIL import Image

    poster = site / "assets/social/lzsuite.png"
    with Image.open(poster) as card:
        assert card.format == "PNG" and card.size == (1200, 630)
        card.verify()
    origin = "https://el3ssar.github.io/lzsuite/"
    digest = hashlib.sha256(poster.read_bytes()).hexdigest()[:12]
    image_url = urljoin(origin, f"assets/social/lzsuite.png?v={digest}")
    for path, page in pages.items():
        if path.name == "404.html":
            continue
        relative = path.relative_to(site).as_posix().removesuffix("index.html")
        assert page.social["og:url"] == urljoin(origin, relative), path
        assert page.social["og:type"] == "website", path
        assert page.social["og:image"] == page.social["twitter:image"] == image_url, path
        assert page.social["og:image:type"] == "image/png", path
        assert page.social["og:image:width"] == "1200", path
        assert page.social["og:image:height"] == "630", path
        assert page.social["twitter:card"] == "summary_large_image", path
        assert page.social["og:title"] == page.social["twitter:title"], path
        assert page.social["og:description"] == page.social["twitter:description"], path
        for key in ("og:title", "og:description", "og:image:alt", "twitter:image:alt"):
            assert page.social[key].strip(), (path, key)
    assert pages[(site / "index.html").resolve()].social["og:title"] == (
        "lzsuite — Lempel–Ziv analysis for NumPy"
    )
    links = 0
    for path, page in pages.items():
        for ref in page.references:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            target = unquote(url.path)
            if target.startswith("/lzsuite/"):
                target = target[len("/lzsuite/") :]
                resolved = site / target
            elif target.startswith("/"):
                resolved = site / target.lstrip("/")
            else:
                resolved = path.parent / target if target else path
            resolved = resolved.resolve()
            if resolved.is_dir():
                resolved /= "index.html"
            assert resolved.is_file(), f"{path.relative_to(site)}: missing target {ref}"
            if url.fragment and resolved in pages:
                anchor = unquote(url.fragment)
                assert anchor in pages[resolved].ids, (
                    f"{path.relative_to(site)}: missing anchor {ref}"
                )
            links += 1
    public = {
        **{name: (name,) for name in ("h", "complexity", "factorization", "emc", "lz76")},
        "distance": ("distance",),
        "discretization": ("discretize", "available_discretizers", "register_discretizer"),
    }
    for page, names in public.items():
        ids = pages[(site / "reference" / page / "index.html").resolve()].ids
        for name in names:
            assert f"lzsuite.{name}" in ids, f"Missing API entry for {name}"
    figures = site / "assets/figures"
    assert len(list(figures.glob("*.svg"))) == 14
    assert len(list(figures.glob("*.png"))) == 14
    for figure in figures.glob("*.svg"):
        assert (figures / "dark" / figure.name).is_file(), figure.name
        assert (figures / "dark" / figure.with_suffix(".png").name).is_file(), figure.name
    assert (figures / "provenance.json").is_file()
    assert (site / "assets/favicon.png").is_file()
    print(
        f"Validated {len(pages)} HTML pages, {links} local references, "
        "API anchors, social previews, and 14 figures in both themes."
    )


if __name__ == "__main__":
    {"source": check_source, "site": check_site}[sys.argv[1]]()
