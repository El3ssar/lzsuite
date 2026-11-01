"""Validate source documentation, runnable guide snippets, and the built site."""

from __future__ import annotations

import ast
import inspect
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

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
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
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


def check_site():
    """Check all local assets/anchors and the complete generated public reference."""
    site = ROOT / "site"
    pages = {path.resolve(): Page(path) for path in site.rglob("*.html")}
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
        "analysis": ("h", "complexity", "factorization", "emc", "lz76"),
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
    assert (figures / "provenance.json").is_file()
    assert (site / "assets/favicon.png").is_file()
    print(
        f"Validated {len(pages)} HTML pages, {links} local references, "
        "API anchors, and 14 figure pairs."
    )


if __name__ == "__main__":
    {"source": check_source, "site": check_site}[sys.argv[1]]()
