"""Add social previews and version local documentation assets by content."""

from __future__ import annotations

import hashlib
import re
from html import escape
from pathlib import Path
from urllib.parse import urljoin

_ASSET = re.compile(r'((?:src|href)="(?:\.\./)*assets/)([^"?#]+)(")')


def social_metadata(page, config):
    """Render server-readable Open Graph and large-image card metadata."""
    poster = Path(config.docs_dir) / "assets/social/lzsuite.png"
    digest = hashlib.sha256(poster.read_bytes()).hexdigest()[:12]
    image = urljoin(config.site_url, f"assets/social/lzsuite.png?v={digest}")
    title = f"{config.site_name} — {page.title}"
    description = page.meta.get("description") or config.site_description
    alt = "lzsuite: Lempel–Ziv analysis for NumPy arrays, with a signal and its binary labels."
    properties = {
        "og:type": "website",
        "og:site_name": config.site_name,
        "og:title": title,
        "og:description": description,
        "og:url": page.canonical_url,
        "og:image": image,
        "og:image:secure_url": image,
        "og:image:type": "image/png",
        "og:image:width": "1200",
        "og:image:height": "630",
        "og:image:alt": alt,
    }
    names = {
        "twitter:card": "summary_large_image",
        "twitter:title": title,
        "twitter:description": description,
        "twitter:image": image,
        "twitter:image:alt": alt,
    }
    tags = [
        f'<meta {attribute}="{key}" content="{escape(str(value), quote=True)}">'
        for attribute, entries in (("property", properties), ("name", names))
        for key, value in entries.items()
    ]
    return "\n".join(tags)


def on_post_page(output, *, page, config):
    """Add share metadata and append content hashes to local asset references."""
    assets = (Path(config.docs_dir) / "assets").resolve()

    def versioned(match):
        path = (assets / match[2]).resolve()
        if not path.is_relative_to(assets) or not path.is_file():
            return match[0]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        return f"{match[1]}{match[2]}?v={digest}{match[3]}"

    output = _ASSET.sub(versioned, output)
    return output.replace("</head>", social_metadata(page, config) + "\n</head>", 1)
