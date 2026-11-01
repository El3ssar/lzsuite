# From an array to an answer

lzsuite handles the path from observations to symbols to Lempel–Ziv measurements.
Start with one sequence, then use the same functions over your full array.

## Install

=== "pip"

    ```sh
    python -m pip install lzsuite
    ```

=== "uv"

    ```sh
    uv add lzsuite
    ```

Python 3.10 or newer is required. NumPy, lzcomplexity, and joblib are installed as
runtime dependencies. Plotting and documentation tools are optional development
extras, not dependencies for using the library.

## One sequence

Run these snippets separately in IPython or a notebook:

```python
import numpy as np
import lzsuite as lzs

signal = np.sin(np.linspace(0, 40, 2000))
```

```python
entropy = lzs.h(signal)  # float
count = lzs.complexity(signal)  # int
entropy, count
```

The float signal is binarized at its own mean. Values strictly above the mean
become 1; everything else becomes 0. The logarithm base uses the number of
observed symbols, with a minimum of 2.

```python
count, boundaries = lzs.factorization(signal)
score, increments = lzs.emc(signal, max_block_size=6)
```

```python
result = lzs.lz76(signal, max_block_size=6)
result["h"], result["emc"]["value"], result["emc"]["method"]
```

No `.item()` is needed. One sequence returns Python values directly.

## A collection of sequences

```python
rng = np.random.default_rng(42)
data = rng.normal(size=(2000, 4, 3))  # observations × channels × trials
```

```python
entropy = lzs.h(data)  # shape (4, 3)
scores, profiles = lzs.emc(data)  # both arrays have shape (4, 3)
```

`axis=0` means that each fixed channel/trial position is a separate sequence.
Scalar calculations remove that axis and preserve all other dimensions.

```python
other = rng.normal(size=(1500, 4, 3))
matrix = lzs.distance(data)  # shape (12, 12): every pair
paired = lzs.distance(data, other)  # shape (4, 3): corresponding pairs
```

## Make the representation explicit

```python
entropy = lzs.h(data, discretization="median")
entropy = lzs.h(data, discretization="bins", discretization_kwargs={"n_bins": 4})
```

Integer, boolean, and string-array elements are already symbols:

```python
symbols = rng.integers(0, 4, size=(2000, 4, 3))
lzs.h(symbols)  # no automatic thresholding
```

!!! tip "A small, inspectable example"
    `lzs.h([0, 1, 0, 1, 0, 1, 0, 1])` returns `0.75`. These integers
    are eight observations. lzsuite encodes them as individual symbols instead
    of passing an integer list to the backend's decimal-text conversion.

## Know the defaults

| Choice | Default | Override |
|---|---|---|
| Sequence axis | `0` | `axis=-1`, or another valid axis |
| Float representation | Mean binarization per sequence | `discretization=...` |
| Integer/string representation | Existing categories | Numeric inputs can be explicitly discretized |
| Logarithm base | Observed prepared alphabet, minimum 2 | `log_base=2` |
| E method | Chao–Shen | `method="shuffle"` |
| E maximum range | Automatic | `max_block_size=6`, for example |
| Process budget | Up to four | `n_jobs=1`, `2`, or `-1` |

Next, explore [arrays and axes](arrays.md), [discretization](discretization.md),
or the [visual gallery](../gallery/index.md).
