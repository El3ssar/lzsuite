# lzsuite

[![CI](https://github.com/El3ssar/lzsuite/actions/workflows/ci.yml/badge.svg)](https://github.com/El3ssar/lzsuite/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://github.com/El3ssar/lzsuite/blob/main/pyproject.toml)
[![MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23858269.svg)](https://doi.org/10.5281/zenodo.23858269)

Lempel–Ziv analysis for multidimensional NumPy arrays. Choose the axis containing
observations, optionally discretize continuous signals, and calculate complexity,
entropy density, effective measure complexity, or information distances across
all remaining positions.

[lzcomplexity](https://github.com/pleros-ai/lzcomplexity) supplies the numerical
engine. lzsuite adds array handling, discretization, shared symbol encodings,
and parallel calculation across sequences.

**Early development:** the API can evolve. The repository is available on GitHub
and releases are archived on Zenodo. PyPI publication is planned separately.

## Install and try it

From the repository, using [uv](https://docs.astral.sh/uv/):

```sh
git clone https://github.com/El3ssar/lzsuite.git
cd lzsuite
uv sync --locked
uv run ipython
```

This creates a local `.venv`, installs lzsuite in editable mode, and installs the
locked development tools. No activation or global Python packages are needed.
For a regular environment without uv, use `python -m pip install .` after cloning.
Python 3.10+ is required; development defaults to Python 3.12.

## Quick start

These are separate snippets you can run in the same IPython session.

```python
import numpy as np
import lzsuite as lzs

rng = np.random.default_rng(42)
signal = rng.normal(size=1000)
data = rng.normal(size=(1000, 4, 3))  # observations × channels × trials
```

One sequence returns an ordinary Python value. No scalar extraction is needed:

```python
entropy = lzs.h(signal)  # float
count = lzs.complexity(signal)  # int
count, boundaries = lzs.factorization(signal)
score, increments = lzs.emc(signal)  # float and list
result = lzs.lz76(signal)  # dict
```

Arrays retain the dimensions outside the sequence axis, which defaults to 0:

```python
entropy = lzs.h(data)  # shape (4, 3)
counts = lzs.complexity(data)  # shape (4, 3)
scores, profiles = lzs.emc(data, max_block_size=8)
results = lzs.lz76(data, max_block_size=8)
results[0, 0]["emc"]["value"]  # first channel, first trial
```

Other axes and noncontiguous views work too:

```python
observations_last = np.moveaxis(data, 0, -1)  # shape (4, 3, 1000)
np.allclose(entropy, lzs.h(observations_last, axis=-1))  # True
```

A singleton batch dimension is preserved: input `(1000, 1)` returns shape `(1,)`.
Only a truly 1D input gets the direct Python result. See the full
[API reference](docs/api.md) for return types.

## Discretization

Float arrays use mean binarization by default, independently for each sequence.
Integers, booleans, and string-array elements are already symbols. An explicitly
selected discretizer overrides the default for numeric inputs; strings cannot
be passed to a discretizer.

```python
lzs.available_discretizers()
# ('bins', 'mean', 'median', 'permutation', 'quantile')

labels = lzs.discretize(signal, method="median")  # use a method directly
entropy = lzs.h(data, discretization="median")  # or inside a calculation
entropy = lzs.h(data, discretization="bins", discretization_kwargs={"n_bins": 4})
```

| Method | Rule | Parameters |
|---|---|---|
| `mean` | Above the sequence mean → 1; equality/below → 0 | — |
| `median` | Above the sequence median → 1; equality/below → 0 | — |
| `bins` | Equally wide bins spanning the sequence's range | `n_bins=2` |
| `quantile` | Bins using empirical quantile edges | `n_bins=2` |
| `permutation` | Labels for the ordering within delayed windows | `order=3`, `delay=1` |

Values on internal bin edges go right. Repeated quantile edges collapse, and
constant signals yield zero labels. Bin edges are fitted separately per sequence;
pass a custom method using fixed edges if comparisons require shared thresholds.
Permutation ties are ordered by position, earlier first. Permutation output has
`len(signal) - (order - 1) * delay` entries; it is a discretization, not a
permutation-entropy calculation.

### Your own methods

A method receives a numeric 1D array and returns a nonempty 1D array of integer
labels. Its output length can change. The input is copied before calling it, so
in-place changes do not modify your original data.

```python
def threshold(values, *, level=0.0):
    return (values > level).astype(np.uint8)


lzs.h(data, discretization=threshold)  # directly supplied callable
```

Register the same function for reuse by name:

```python
lzs.register_discretizer("threshold", threshold, replace=True)
lzs.h(data, discretization="threshold", discretization_kwargs={"level": 0.5})
```

Decorator registration is also supported:

```python
@lzs.register_discretizer("every_other", replace=True)
def every_other(values):
    return (values[::2] > 0).astype(np.uint8)


lzs.h(data, discretization="every_other")
```

Registration is local to the Python session. Existing names require
`replace=True` to overwrite. Discretization runs in the calling process, so
functions defined interactively work with parallel calculations too.

## Information distances

One input calculates every pair of sequences:

```python
matrix = lzs.distance(data)  # shape (12, 12)
```

Rows and columns follow C-order flattening of `(channel, trial)`. Here,
`(channel, trial)` corresponds to row `channel * 3 + trial`. The matrix is
symmetric and retains actual self-distances, which may be nonzero.

Two inputs compare corresponding sequences:

```python
other = rng.normal(size=(800, 4, 3))
paired = lzs.distance(data, other)  # shape (4, 3)
single = lzs.nid(signal, other[:, 0, 0])  # float; nid is an alias for distance
```

Shapes outside the sequence axis must match exactly; sequence lengths may differ.
There is no broadcasting. A shared codebook keeps category meanings consistent
across the inputs. The two-input mode does not compute all cross-pairs.
A single 1D input to `distance` still gives a `(1, 1)` all-pairs matrix.

Both modes accept `axis`, `discretization`, `discretization_kwargs`, and `n_jobs`.
For float inputs, the default mean threshold is fitted independently to each
sequence in each input.

## Parallel execution and Rayon

**Default: up to four worker processes**, capped by available CPUs and the number
of calculations. This works in scripts, IPython, and notebooks using joblib's
loky process runner. Workers are reused across calls to reduce repeated startup.

```python
lzs.h(data)  # up to 4 processes
lzs.h(data, n_jobs=1)  # inline calculation; no worker processes
lzs.h(data, n_jobs=2)  # up to 2 processes
lzs.distance(data, n_jobs=-1)  # all available CPUs, capped by pair count
```

Each worker uses **one Rayon thread**. Thus four worker processes share the
calculation workload without each starting a full native thread pool. Worker
configuration is local to those processes; lzsuite does not change the calling
process's `RAYON_NUM_THREADS` or initialized Rayon pool. Other common native
thread pools are also limited to one thread per worker.

The inline path (`n_jobs=1`, a single calculation, or one available CPU) preserves
the calling process's existing native configuration, so lzcomplexity can still
use Rayon internally there. Discretization, validation, and encoding happen in
the calling process before native work is distributed.

Parallelism can use more memory and is not necessarily faster for small inputs.
Use `n_jobs=1` when process startup outweighs the calculation. All-pairs matrices
require quadratic result storage.

## Scientific conventions and validation

- The logarithm base defaults to each discretized sequence's distinct-symbol
  count, with a minimum of 2. Use `log_base=2` for explicit bit units. Different
  observed alphabet sizes imply different normalization bases.
- E defaults to Chao–Shen. `method="shuffle"` selects the alternative estimator
  in `emc` and `lz76`; this option is separate from `discretization`.
- Numeric symbols are encoded as individual bytes. Each string-array element is
  one category, including multi-character strings. To analyze text characters,
  use `np.array(list("banana"))`.
- More than 256 distinct symbols emits `RuntimeWarning` and continues with
  category codes reduced modulo 256. Some categories then merge, so results do
  not faithfully describe the original alphabet. Analysis normalization still
  uses the original symbol count; distances check the shared vocabulary.
- Empty sequences, NaN, infinity, complex values, and object arrays are rejected.
  Empty collections with a nonempty sequence axis return empty arrays.
- Factor boundaries retain the backend's final-tail convention and can extend
  beyond the sequence end. NID does not force self-distance to zero.

Save the discretization settings, sequence length, log base, E method/range,
package versions, and input data or fingerprint with scientific results.

## Development and maintenance

```sh
make setup    # editable install plus local lint/commit hooks
make check    # lint, formatting, tests
make build    # wheel, source archive, package metadata checks
```

The commands are also listed individually in [CONTRIBUTING.md](CONTRIBUTING.md).
The development environment is locked in `uv.lock`; runtime compatibility ranges
are declared in `pyproject.toml`. The backend dependency is currently
`lzcomplexity>=3.0.0,<4`, preventing an unreviewed major-version upgrade. See the
[maintenance and release guide](docs/maintenance.md) for dependency updates,
versioning, GitHub releases, PyPI publication, and Zenodo archiving.

Conventional Commits drive release-please version/changelog PRs. Merging a release
PR creates the `vX.Y.Z` tag and GitHub release. CI checks Python 3.10–3.14 on Linux,
plus macOS and Windows, and builds package distributions. GitHub releases are
automatically archived through Zenodo's repository integration. **PyPI uploading
is not enabled yet.**

The public API contains only callable user functions; implementation modules are
private. `lzs.__version__` gives the installed version. A complete executable
walkthrough is in [examples/overview.py](examples/overview.py).

## License and attribution

MIT licensed; see [LICENSE](LICENSE). The LZ76 engine and estimator implementation
are provided by [lzcomplexity](https://github.com/pleros-ai/lzcomplexity), with its
own authorship and scientific references. Software citation metadata for this
wrapper is in [CITATION.cff](CITATION.cff).

Cite the [all-versions DOI](https://doi.org/10.5281/zenodo.23858269) for the project,
or the [0.1.0 DOI](https://doi.org/10.5281/zenodo.23858270) for that exact archive.
