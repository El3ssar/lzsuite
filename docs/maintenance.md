# Maintaining and releasing lzsuite

## Environment and dependencies

The supported interpreter range is Python 3.10+. `.python-version` selects 3.12
for everyday development. `uv sync --locked` reproduces the development environment
from `uv.lock`, including an editable install, tests, linting, packaging tools,
and IPython. CI uses uv 0.13.6 to match the lockfile tooling used for this project.

There are three runtime dependencies:

| Dependency | Requirement | Role |
|---|---|---|
| NumPy | `>=1.24` | Arrays, axis handling, numeric discretization |
| lzcomplexity | `>=3.0.0,<4` | LZ76 calculations and numerical estimators |
| joblib | `>=1.5,<2` | Reusable process workers, including interactive sessions |

The declared ranges are used by package installers. The lockfile pins exact
versions for repeatable development and CI. It includes interpreter-specific
resolutions; installed versions may differ between Python 3.10 and 3.12 while
still using the same lockfile.

### Update the backend alone

```sh
uv lock --upgrade-package lzcomplexity
uv sync --locked
make check
make build
git diff -- pyproject.toml uv.lock
```

`make deps-backend` performs the first two steps. This stays within the declared
3.x range. Read the upstream release notes, especially estimator changes, before
accepting an update. Results are version-dependent; retain explicit regression
fixtures when a scientific result must remain stable across backend updates.

To adopt a new backend major version, first update the requirement deliberately
in `pyproject.toml`, regenerate the lockfile, inspect the input/result contracts,
and validate against that version before merging.

### Update the full environment

```sh
uv lock --upgrade
uv sync --locked
make check
make build
```

`make deps-update` performs the first two steps. Review the dependency diff and
commit it. Development-only changes should not force unrelated runtime changes.
Dependabot also proposes monthly uv and GitHub Actions updates as reviewable PRs.

## Versioning and GitHub releases

The source package version lives in `pyproject.toml`. `lzsuite.__version__` reads
installed distribution metadata. After a version update, run `uv sync --locked`
and restart existing Python sessions so their metadata and imports are fresh.

Conventional Commit types determine release bumps:

| Commit | Release effect |
|---|---|
| `fix:` / `perf:` | Patch |
| `feat:` | Minor |
| `feat!:` or `BREAKING CHANGE:` footer | Major |
| `docs:`, `test:`, `ci:`, etc. | No release on their own |

Release-please opens or updates a release PR on `main`. It updates the package
version, changelog, manifest, and only lzsuite's own version entry in `uv.lock`.
The lockfile selector uses `name.value` because the TOML updater wraps scalar
values with source-position metadata; it has been checked against release-please.

The first release is configured as 0.1.0. Before that release, the manifest uses
release-please's `0.0.0` bootstrap marker, meaning no version has been released;
the source package remains 0.1.0. The release PR replaces that marker with the
actual released version. No release tag is needed during normal development.
To cut a GitHub release:

1. Review the release PR's changelog, version and dependency lock diff.
2. Run its checks; resolve any scientific or API compatibility concerns.
3. Merge that PR. Release-please creates the version tag and GitHub release.
4. The release workflow checks out the tag, tests, builds the wheel and source
   archive, validates metadata, and attaches them to the GitHub release.

The release workflow uses the default Actions token, or `RELEASE_PLEASE_TOKEN`
when a GitHub App/fine-grained token is configured. GitHub does not automatically
run additional workflows for PRs created by the default token. Such release PRs
can be checked out locally, or CI can be dispatched manually on their branch:

```sh
gh workflow run ci.yml --ref release-please--branches--main
```

Check the actual release branch name with `gh pr list` if it differs. A dedicated
token allows automatic PR checks; do not add tokens to files or commit history.
Actions needs permission to create pull requests; that repository setting is
configured during setup. CI tests PR titles, so use squash merges with semantic
PR titles. Branch protection, if added later, must account for bot-created PRs.

## PyPI publication

Version 0.1.0 was published on November 1, 2026:
https://pypi.org/project/lzsuite/0.1.0/

PyPI trusts this exact GitHub identity:

| Setting | Value |
|---|---|
| Repository owner | `El3ssar` |
| Repository | `lzsuite` |
| Workflow filename | `release.yml` |
| GitHub environment | `pypi` |

The environment is restricted to the `main` branch. Authentication uses a
short-lived GitHub OIDC identity; there is no long-lived PyPI API token in the
repository. If the repository owner, workflow filename, or environment changes,
update the trusted publisher on PyPI to match before attempting another upload.

After release-please creates a release and its distributions, the workflow:

1. Downloads the attached wheel and source archive from that GitHub release.
2. Checks filenames, project/version metadata, and SHA-256 against GitHub's
   asset digests; no distribution is rebuilt during publication.
3. Validates metadata, smoke-tests the installed wheel, and passes the files
   to a separate publishing job with only the required OIDC permission.
4. Publishes those exact files using PyPA's publishing action.

To publish an existing stable GitHub release, or resume an interrupted upload:

```sh
gh workflow run release.yml --repo El3ssar/lzsuite --ref main -f tag=v0.1.0
```

Replace the example tag with the intended release. Manual dispatch skips release
creation and publishing uses the already-attached artifacts. Existing uploads
are skipped on retry; never overwrite or modify artifacts for a published
version. Fix package changes in a new version instead.

After publishing, verify the workflow's `publish-pypi` job succeeded, check the
PyPI project/version, compare file digests to the GitHub release, and install
from PyPI in an isolated environment. A GitHub tag alone does not prove upload.
The initial 0.1.0 upload passed those checks, including scalar, array, and default
parallel calculations on Python 3.10.

## Zenodo archiving

The repository is connected to Zenodo. Publishing a GitHub release triggers
automatic archiving through Zenodo's release webhook, independently of PyPI.
Version 0.1.0 was archived on November 1, 2026:

- Version DOI: https://doi.org/10.5281/zenodo.23858270
- Concept DOI (all versions): https://doi.org/10.5281/zenodo.23858269

The README badge and `CITATION.cff` identifier use the concept DOI. Do not replace
it with a fixed version DOI on the development branch: that would become stale
for subsequent releases. For reproducible studies, cite the specific version DOI.
After every release, verify the new Zenodo record's version, authors, license and
source archive. Keep `CITATION.cff` metadata current before making the release.

A GitHub repository, a GitHub release, a PyPI package, and a Zenodo record are
separate milestones. Check each service before reporting completion.
