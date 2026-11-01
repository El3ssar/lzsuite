# Contributing to lzsuite

## Set up once

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
git clone https://github.com/El3ssar/lzsuite.git
cd lzsuite
uv sync --locked
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
uv run ipython
```

Or run `make setup`. Everything lives in the repository's `.venv` and uv cache;
no global Python packages or manual virtual-environment activation are needed.
The editable install reflects source edits immediately. Restart an interactive
session after changing already-imported modules.

`.python-version` selects Python 3.12 for routine development. `requires-python`
in `pyproject.toml` sets the supported minimum to 3.10. `uv.lock` records the exact
development dependency versions across supported interpreters.

## Everyday workflow

```sh
git switch -c fix/describe-the-change
# Edit source, tests, documentation, or examples.
make check
make build
git add <changed-files>
git commit -m "fix: describe the resulting behavior"
git push -u origin HEAD
```

The individual checks are:

```sh
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest --cov=lzsuite
uv build
uv run --locked twine check dist/*
```

Use `uv run ruff format .` to format edits, and `uv run ruff check . --fix` for
automatic lint fixes. Local hooks run lint/format checks and validate commit
subjects. CI also checks the PR title; use a Conventional Commit title so squash
merging preserves the release intent.

## Code map

```text
src/lzsuite/
  __init__.py          Public function exports and installed package version
  _analysis.py         Complexity, h, factorization, E, full results
  _distance.py         All-pairs and corresponding-pair NID
  _discretization.py   Built-ins, registry, callable validation
  _arrays.py           Axis handling and sequence preparation
  _encoding.py         Byte encodings and shared distance codebooks
  _execution.py        Inline execution and joblib/loky process workers
tests/                 Backend comparisons, contracts, execution, namespace
examples/overview.py   Commented executable walkthrough
docs/                  API and maintenance guides
.github/workflows/     CI and release automation
```

Keep implementation modules private. Add a top-level export only when it is a
function users should call, and update `tests/test_public_api.py` deliberately.
Avoid adding helper imports to the public namespace.

## Tests that matter

Tests compare against the real installed lzcomplexity engine, including both E
estimators. Cover scientific encoding choices, arbitrary axes, shape preservation,
1D native return types, registry behavior, warning/error cases, and agreement
between serial and parallel execution.

When changing execution, check both the result and the process/thread budget.
Workers use one Rayon thread; the caller's configuration must remain unchanged.
When changing a discretizer, include meaningful edge cases such as ties, constant
signals, and shortened output. Custom methods need no output-length declaration.

CI runs Python 3.10–3.14 on Linux and Python 3.12 on macOS and Windows. To test
another interpreter locally without replacing the default environment:

```sh
UV_PROJECT_ENVIRONMENT=.venv-py310 uv run --locked --python 3.10 pytest
UV_PROJECT_ENVIRONMENT=.venv-py314 uv run --locked --python 3.14 pytest
```

CI also checks an installed wheel and the minimum NumPy/joblib dependencies.
For interactive smoke testing, `uv run ipython` can call `lzs.h(data)` directly,
including its default parallel path.

## Dependencies and versioning

Runtime requirements live in `pyproject.toml`; reproducible development versions
live in `uv.lock`. Commit both files when a requirement changes. A lockfile pin
is not the same as a published package requirement.

Use Conventional Commits:

```text
feat(discretization): add fixed-edge binning
fix(distance): preserve category meanings across inputs
perf: reuse calculation work
refactor: simplify internal array handling
docs: explain normalization
feat!: change public result shapes
```

`feat` proposes a minor bump; `fix` and `perf` propose patch bumps. A `!` or
`BREAKING CHANGE:` footer declares a breaking change. Under the current default
policy, breaking changes bump the major version even while the version is 0.x.
Merging a normal feature PR does not publish a release: release-please prepares
a separate release PR for review.

See [docs/maintenance.md](docs/maintenance.md) for the exact dependency-update
commands, release procedure, and remaining PyPI/Zenodo setup. Do not hand-edit
versions in several files: release-please updates `pyproject.toml`, `uv.lock`,
the release manifest, and the changelog together.

## Reporting problems

Open an [issue](https://github.com/El3ssar/lzsuite/issues) with a small input,
its dtype and shape, the call and parameters, the expected/actual behavior,
Python/platform information, and the lzsuite/lzcomplexity/NumPy versions. Include
`n_jobs` when reporting parallel-execution issues. Keep scientific data private
unless you have permission to share it.
