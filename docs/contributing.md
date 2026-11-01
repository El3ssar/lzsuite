# Contribute to lzsuite

The source, documentation, and release workflow live together in
[El3ssar/lzsuite](https://github.com/El3ssar/lzsuite).

## Start locally

```sh
git clone https://github.com/El3ssar/lzsuite.git
cd lzsuite
make setup
make check
```

## Work on documentation

```sh
uv sync --locked --group docs
make docs
make docs-serve
```

The site uses MkDocs Material and mkdocstrings' NumPy docstring parser. Public
reference pages are generated from the actual source docstrings. Edit those
rather than copying parameter tables into a second reference source.

- Keep public and internal function docstrings in NumPy style.
- Document parameters, return types/shapes, validation, warnings, and conventions.
- Use small executable examples; doctests run in documentation CI.
- Regenerate figures from the checked-in script rather than editing data by hand.
- Give every plot meaningful alternative text and an interpretation caption.
- Check local links and both narrow/wide layouts before publishing.

Documentation tools are in the `docs` uv group, separate from runtime dependencies.
`make docs` regenerates plots, executes examples, validates docstrings, builds
strictly, and checks the generated site's links and assets. GitHub Pages is
published from `main` after those checks.

## Keep the public API small

Implementation modules begin with an underscore. Top-level completion should
contain only user-facing functions. A change to the public surface requires an
intentional update to the API test, docstrings, tutorials, and shape conventions.

## Changes and releases

Use Conventional Commits and a semantic PR title. CI tests supported Python
versions, operating systems, the installed wheel, numerical contracts, and the
documentation. See the full
[CONTRIBUTING.md](https://github.com/El3ssar/lzsuite/blob/main/CONTRIBUTING.md)
for source layout and development commands, or the
[maintenance guide](maintenance.md) for dependency updates and releases.

## Documentation style

Use literal topic headings, direct technical descriptions, and examples with
concrete inputs and outputs. Keep installation, usage guides, function reference,
numerical examples, and maintenance instructions in their corresponding sections.

The stylesheet defines shared color tokens for the page, navigation, code,
tables, search, and footer. Figures have separate light and dark exports;
check their labels and legends in both schemes. Check narrow layouts for page
navigation, long signatures, table scrolling, and plot readability.
