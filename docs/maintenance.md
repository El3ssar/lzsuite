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

## PyPI publication — next stage

No current workflow uploads to PyPI. Before enabling it:

1. Confirm package-name availability and validate author/license metadata.
2. Configure the project's GitHub Actions trusted publisher on PyPI.
3. Add a dedicated publish job using OpenID Connect, after successful tests and
   distribution validation. Use a GitHub environment for release control if desired.
4. Verify an installed wheel in a clean environment and review its README rendering.
5. Publish the chosen release, then verify installation from the index.

Do not claim a version is on PyPI merely because it has a GitHub tag.

## Zenodo registration — next stage

`CITATION.cff` contains the software authorship and repository reference, without
an invented DOI. When ready, connect this GitHub repository to Zenodo and confirm
that releases are archived with the intended title, authors and license. Add
verified DOI links to the citation and README after registration. Decide whether
the first GitHub release should be created only after that connection is enabled.

A GitHub repository, a GitHub release, a PyPI package, and a Zenodo record are
separate milestones. Check each service before reporting completion.
