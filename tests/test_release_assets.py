"""Reject wrong releases, altered uploads, and mismatched distribution metadata."""

import hashlib
import importlib.util
import io
import tarfile
import zipfile
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "check_release_assets", Path(__file__).parents[1] / "scripts/check_release_assets.py"
)
_CHECKER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_CHECKER)


def distributions(directory, metadata_version="0.1.0"):
    metadata = f"Name: lzsuite\nVersion: {metadata_version}\n".encode()
    with zipfile.ZipFile(directory / "lzsuite-0.1.0-py3-none-any.whl", "w") as archive:
        archive.writestr("lzsuite-0.1.0.dist-info/METADATA", metadata)
    with tarfile.open(directory / "lzsuite-0.1.0.tar.gz", "w:gz") as archive:
        entry = tarfile.TarInfo("lzsuite-0.1.0/PKG-INFO")
        entry.size = len(metadata)
        archive.addfile(entry, io.BytesIO(metadata))
    return {
        "tag_name": "v0.1.0",
        "draft": False,
        "prerelease": False,
        "assets": [
            {"name": path.name, "digest": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in directory.iterdir()
        ],
    }


def test_published_release_assets_are_accepted(tmp_path):
    _CHECKER.validate_release(distributions(tmp_path), tmp_path)


@pytest.mark.parametrize("field", ["draft", "prerelease"])
def test_unpublished_or_prerelease_upload_is_rejected(tmp_path, field):
    release = distributions(tmp_path)
    release[field] = True
    with pytest.raises(ValueError, match="published stable"):
        _CHECKER.validate_release(release, tmp_path)


def test_modified_upload_is_rejected(tmp_path):
    release = distributions(tmp_path)
    with (tmp_path / "lzsuite-0.1.0-py3-none-any.whl").open("ab") as stream:
        stream.write(b"modified")
    with pytest.raises(ValueError, match="digest"):
        _CHECKER.validate_release(release, tmp_path)


def test_wrong_metadata_is_rejected_even_with_matching_digests(tmp_path):
    with pytest.raises(ValueError, match="metadata"):
        _CHECKER.validate_release(distributions(tmp_path, "9.9.9"), tmp_path)


def test_unexpected_files_are_rejected(tmp_path):
    release = distributions(tmp_path)
    (tmp_path / "other-project.whl").write_bytes(b"unrelated")
    with pytest.raises(ValueError, match="exactly"):
        _CHECKER.validate_release(release, tmp_path)


@pytest.mark.parametrize("tag", ["../main", "main", "v01.0.0", "v0.1.0rc1"])
def test_invalid_tags_are_rejected(tmp_path, tag):
    release = distributions(tmp_path)
    release["tag_name"] = tag
    with pytest.raises(ValueError, match="stable release tag"):
        _CHECKER.validate_release(release, tmp_path)
