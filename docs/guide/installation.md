# Installation

lzsuite requires **Python 3.10 or newer**.

## Install from PyPI

=== "pip"

    ```sh
    python -m pip install lzsuite
    ```

=== "uv"

    ```sh
    uv add lzsuite
    ```

The runtime dependencies are NumPy, joblib, and lzcomplexity. The compatible
backend range is `lzcomplexity>=3.0.0,<4`. Plotting and documentation tools are
not installed with the library.

## Check the installation

```python
import lzsuite as lzs

lzs.__version__
lzs.h([0, 1, 0, 1, 0, 1, 0, 1])  # 0.75
```

For an existing environment, use `python -m pip install --upgrade lzsuite`.
Restart an active Python or IPython session after updating the package.

## Development environment

```sh
git clone https://github.com/El3ssar/lzsuite.git
cd lzsuite
uv sync --locked
uv run ipython
```

This installs the source in editable mode and uses the development dependencies
recorded in `uv.lock`. See [contributing](../contributing.md) for tests, source
layout, documentation builds, and commit conventions.

Continue with the [quickstart](quickstart.md). For import or environment errors,
see [troubleshooting](troubleshooting.md).
