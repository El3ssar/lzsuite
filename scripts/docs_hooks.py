"""Version documentation assets by content so deployments invalidate browser caches."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

_ASSET = re.compile(r'((?:src|href)="(?:\.\./)*assets/)([^"?#]+)(")')


def on_post_page(output, *, page, config):
    """Append a content hash to local asset references in each rendered page."""
    assets = (Path(config.docs_dir) / "assets").resolve()

    def versioned(match):
        path = (assets / match[2]).resolve()
        if not path.is_relative_to(assets) or not path.is_file():
            return match[0]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        return f"{match[1]}{match[2]}?v={digest}{match[3]}"

    return _ASSET.sub(versioned, output)
