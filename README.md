# lzsuite

Array-oriented Lempel–Ziv analysis and signal discretization, powered by
[lzcomplexity](https://github.com/pleros-ai/lzcomplexity).

Python **3.10+**. NumPy and lzcomplexity are runtime dependencies. This is an
initial local version; it has not been published to PyPI.

## Development

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
```

`uv sync` installs the package in editable mode and includes development tools.
The development interpreter is pinned to Python 3.12; the package supports 3.10+.
Use `uv run --python 3.10 pytest` to check the minimum version.
For an existing environment, `pip install -e .` also works.

## Arrays and axes

The sequence axis contains observations. Every position on the remaining axes
identifies a separate sequence. Scalar results remove the sequence axis:

```python
import numpy as np
import lzsuite as lzs

rng = np.random.default_rng(42)
data = rng.normal(size=(1000, 12, 8))
entropy = lzs.h(data)  # axis=0 by default; shape (12, 8)
counts = lzs.complexity(data)  # shape (12, 8)
scores, profiles = lzs.emc(data, max_block_size=8)
full = lzs.lz76(data, max_block_size=8)  # object array of dictionaries
print(full[0, 0]["complexity"])
```

Negative axes and noncontiguous arrays work. A 1D input produces a 0D array;
use `.item()` to extract its result. `factorization()` returns an object array
of `(count, boundaries)` tuples. `emc()` returns a float score array and an
object array of increment lists. Profiles and boundaries can have different
lengths across sequences. `lz76()` returns the backend dictionaries unchanged.

## Discretization

Float arrays default to mean binarization, separately for each sequence.
Integer, boolean, and string arrays are treated as existing symbols.
An explicit method overrides this behavior for numeric inputs; asking to
discretize strings raises `TypeError`.

```python
entropy = lzs.h(data, discretization="median")
entropy = lzs.h(data, discretization="bins", discretization_kwargs={"n_bins": 4})
labels = lzs.discretize([0.2, -0.5, 0.7, 0.1], method="permutation", order=3)
```

| Registered name | Rule and parameters |
|---|---|
| `mean` | Above the sequence mean → 1; equality and below → 0. |
| `median` | Above the sequence median → 1; equality and below → 0. |
| `bins` | Equal-width bins over the sequence range; `n_bins=2`. |
| `quantile` | Empirical quantile edges; `n_bins=2`; repeated edges collapse. |
| `permutation` | Ordinal windows; `order=3`, `delay=1`; earlier positions break ties. |

For bins, values exactly on an internal edge go to the higher bin. Constant
inputs produce zero labels. Bin edges are fitted independently to each
sequence. For shared fixed edges, pass a callable using `np.digitize`.
Permutation labels are lexicographic ranks; each successive window advances
one observation. The discretizer does not calculate permutation entropy.

### Custom methods

A discretizer receives a numeric 1D array and returns a nonempty 1D array of
integer labels. It may change the length. Its input is a copy, so in-place
operations do not mutate the caller's data. No length declaration is needed.

```python
def threshold(values, *, level=0.0):
    return (values > level).astype(np.uint8)


# Pass a callable directly.
entropy = lzs.h(data, discretization=threshold)

# Or register it by name (also usable as a decorator).
lzs.register_discretizer("threshold", threshold)
entropy = lzs.h(data, discretization="threshold", discretization_kwargs={"level": 0.5})
print(lzs.available_discretizers())
```

Registration is process-local. Existing labels require `replace=True` to
overwrite. Discretizers run in the calling process, even with `n_jobs>1`, so
locally defined functions do not need to be pickleable. There is no identity
mode for floating categories yet; explicitly map those to integer labels.

## Distances

```python
symbols = rng.integers(0, 4, size=(1000, 12, 8))
matrix = lzs.distance(symbols)  # shape (96, 96): all sequence pairs
paired = lzs.distance(symbols, symbols)  # shape (12, 8): corresponding pairs
assert np.allclose(np.diag(matrix), paired.ravel())
```

`nid` is an alias for `distance`. With one input, matrix order follows C-order
flattening of the shape after removing the sequence axis. For the example,
`(channel, trial)` maps to `channel * 8 + trial`.

With two inputs, the shapes outside the sequence axis must match exactly;
there is no broadcasting. Sequence lengths may differ, including after
discretization. A 1D pair gives a 0D distance array. Both inputs must contain
numeric symbols or both must contain strings. A shared codebook preserves
category meanings. With float inputs, the default threshold is still each
sequence's own mean. The two-input mode compares corresponding pairs, rather
than all cross-pairs.

The matrix retains actual finite-sequence self-distances, which can be nonzero.
It calculates each unordered pair once and mirrors it. No logarithm base is
needed for NID.

## Normalization, encoding, and validation

The logarithm base defaults to the number of distinct symbols in **each
discretized sequence**, with a minimum of 2 for constant sequences. Supply
`log_base=2` to use bits explicitly. Different observed alphabet sizes imply
different normalization bases. E uses Chao–Shen by default; select
`method="shuffle"` to use the alternative backend estimator.

Integer symbols are encoded as single bytes, avoiding the backend's
integer-to-decimal-string conversion. Each element of a string array is one
category, including strings containing multiple characters. This interface
accepts arrays of numeric/boolean symbols or Unicode/byte strings, not object
arrays, complex numbers, or scalar strings as sequences. To analyze characters,
pass `np.array(list("banana"))`.

Above **256 distinct symbols**, a standard `RuntimeWarning` is emitted
and execution continues. Category codes are reduced modulo 256, so different
symbols merge and results do not faithfully describe the original alphabet.
For scalar analyses the base still uses the original distinct-symbol count;
for distances the warning checks the shared vocabulary across the collection.

Empty sequences, NaN, and infinity are rejected. An empty collection with a
nonempty sequence axis returns an empty result. Factor boundaries retain
lzcomplexity's final-tail convention and can extend beyond the input length.

## Parallel calculations

Calculations run serially by default. Set `n_jobs=4` for four worker processes,
or `n_jobs=-1` for the available CPU count. Preparation/discretization is
serial; native calculations run in the workers. Each worker uses one Rayon
thread. The serial path leaves the existing Rayon configuration intact.

Use a normal Python script with a main guard when starting processes:

```python
import numpy as np
import lzsuite as lzs

if __name__ == "__main__":
    data = np.random.default_rng(42).normal(size=(10000, 16))
    print(lzs.h(data, n_jobs=4))
```

Process startup and input copies can outweigh the benefit for short sequences;
start with the default for small jobs. Spawned workers require an importable
main module; interactive shells/notebooks should use `n_jobs=1` or a script.
All-pairs distances require quadratic result storage.

## Releases

Use Conventional Commits (`feat:`, `fix:`, `docs:`, etc.). Release-please
prepares a version/changelog PR and creates a `vX.Y.Z` tag and GitHub release
when that PR is merged. This mirrors lzcomplexity's release approach.
CI builds distributions; **PyPI publication is not enabled**.
See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and release details.

## Complete example and public API

Run the commented walkthrough with `uv run python examples/overview.py`.
The public namespace contains only these user functions:
`h`, `complexity`, `factorization`, `emc`, `lz76`, `distance`, `nid`,
`discretize`, `available_discretizers`, and `register_discretizer`.
`__version__` provides the installed package version. All implementation modules
are private; use `discretize(..., method="mean")` to invoke built-in methods.
