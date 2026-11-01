"""Validate the exact distributions attached to a published GitHub release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path


def validate_release(release: dict, directory: Path) -> None:
    tag = release["tag_name"]
    if not re.fullmatch(r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", tag):
        raise ValueError("A canonical stable release tag is required.")
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("Only published stable releases can be uploaded.")
    version = tag[1:]
    wheel = f"lzsuite-{version}-py3-none-any.whl"
    sdist = f"lzsuite-{version}.tar.gz"
    expected_names = {wheel, sdist}
    if {path.name for path in directory.iterdir()} != expected_names:
        raise ValueError("Expected exactly the lzsuite wheel and source archive for this tag.")
    assets = {asset["name"]: asset for asset in release["assets"]}
    for name in sorted(expected_names):
        path = directory / name
        digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        if assets.get(name, {}).get("digest") != digest:
            raise ValueError(f"GitHub asset digest does not match {name}.")

    with zipfile.ZipFile(directory / wheel) as archive:
        wheel_metadata = archive.read(f"lzsuite-{version}.dist-info/METADATA")
    with tarfile.open(directory / sdist, "r:gz") as archive:
        stream = archive.extractfile(f"lzsuite-{version}/PKG-INFO")
        if stream is None:
            raise ValueError("Source distribution metadata is missing.")
        with stream:
            sdist_metadata = stream.read()
    for metadata in (wheel_metadata, sdist_metadata):
        parsed = BytesParser().parsebytes(metadata)
        if parsed["Name"] != "lzsuite" or parsed["Version"] != version:
            raise ValueError("Distribution metadata does not match the project and release tag.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release_json", type=Path)
    parser.add_argument("distributions", type=Path)
    args = parser.parse_args()
    release = json.loads(args.release_json.read_text())
    validate_release(release, args.distributions)
    print(f"Verified {release['tag_name']}: filenames, metadata, and GitHub SHA-256 digests.")


if __name__ == "__main__":
    main()
