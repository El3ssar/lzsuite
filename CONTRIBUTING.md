# Development

```sh
uv sync --locked
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
uv run pytest --cov=lzsuite
uv run ruff check .
uv run ruff format --check .
uv build
uv run twine check dist/*
```

Tests compare calculations against the installed lzcomplexity backend, check
array shapes and symbol encodings, and compare serial with process execution.
CI tests Python 3.10–3.14 on Linux and Python 3.12 on macOS and Windows.
Add regression tests when changing numerical behavior or public contracts.

Update dependencies deliberately with `uv lock --upgrade`, and commit `uv.lock`.
The lockfile reproduces development installations; published package metadata
uses the compatible dependency ranges in `pyproject.toml`.

## Commits and releases

Use Conventional Commit subjects, for example:

```text
feat(discretization): add a fixed-threshold method
fix(distance): preserve symbol meanings across inputs
docs: explain sequence axes
feat!: change distance result shapes
```

`feat` triggers a minor release, `fix`/`perf` trigger a patch, and `!` or a
`BREAKING CHANGE:` footer marks a breaking change. The initial release is
configured as 0.1.0. Releases are proposed as PRs; tags are created when those
PRs merge, rather than on every commit. The optional local commit hook checks
subjects, and CI checks PR titles (use squash merging to retain those titles).

The release workflow follows lzcomplexity's release-please setup, using its
Python strategy to update the package version and changelog. An extra TOML
update keeps the local project's version in `uv.lock` in sync. The runtime
version is read from installed package metadata, so there is one source of
package version truth in `pyproject.toml`.

The lockfile JSONPath uses `name.value` because release-please's TOML updater
wraps parsed scalar values with location metadata. A plain `name` comparison
does not match; this path has been checked against its actual updater.

When this repository is hosted on GitHub:

1. Use `main` as the default branch.
2. Enable GitHub Actions and allow Actions to create pull requests under
   Settings → Actions → General. The release workflow requests content and PR
   write permissions.
3. Use squash merging with Conventional Commit PR titles.
4. Merge release-please's release PR to create the tag/release. Its built
   wheel and sdist are retained as workflow artifacts.

GitHub's default Actions token does not trigger other workflows from bot-created
PRs. Release artifacts are therefore checked and built directly in the release
workflow. If required PR checks must run automatically on release PRs, configure
a GitHub App token or narrowly scoped token as `RELEASE_PLEASE_TOKEN`; the workflow
uses it when available and otherwise uses `GITHUB_TOKEN`.

There is no remote configured by this scaffold and no PyPI upload workflow.
Before publication, confirm name availability, fill in project URLs/authorship,
and configure PyPI trusted publishing. Those external steps are intentionally
left for the first actual release.
