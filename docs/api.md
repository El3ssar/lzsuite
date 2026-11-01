# API reference

All functions are available directly from `import lzsuite as lzs`. Implementation
modules are private and do not belong to the supported interface.

## Calculations and return types

| Function | 1D sequence | Higher-dimensional input |
|---|---|---|
| `h(data, ...)` | Python `float` | Float ndarray |
| `complexity(data, ...)` | Python `int` | Integer ndarray |
| `factorization(data, ...)` | `(int, list[int])` | Object ndarray of those tuples |
| `emc(data, ...)` | `(float, list[float])` | `(score_array, profile_object_array)` |
| `lz76(data, ...)` | Result `dict` | Object ndarray of dictionaries |
| `distance(data, other, ...)` | Python `float` for a 1D pair | Float ndarray of corresponding pairs |
| `distance(data, ...)` | `(1, 1)` float ndarray | `(M, M)` float ndarray for M sequences |
| `nid(...)` | Alias for `distance` | Alias for `distance` |

Array calculations remove the sequence axis and preserve all other axes, including
singleton dimensions. All-pairs distance is the exception: it flattens those
positions in C order into matrix rows/columns. No output is wrapped in a 0D array.

### Shared parameters

- `axis=0`: axis containing successive observations; negative indices work.
- `discretization=None`: floats use `mean`; integer/boolean/string arrays use
  their existing symbols. Supply a registered name or callable to discretize
  numeric data explicitly. String discretization raises `TypeError`.
- `discretization_kwargs=None`: mapping passed as keyword arguments to each
  selected discretizer. Methods run separately on each sequence, in the caller.
- `n_jobs=4`: maximum worker processes, capped by available CPUs and task count.
  `1` uses inline calculation; `-1` requests all available CPUs. Other nonpositive
  values, booleans, and non-integers are rejected.

### Entropy and E options

`h`, `emc`, and `lz76` accept `log_base=None`: use each prepared sequence's
observed distinct-symbol count, minimum 2. An explicit integer base must be >=2.

`emc` and `lz76` also accept:

- `max_block_size=-1`: nonpositive values select the backend's automatic range;
  a positive value selects an explicit maximum range.
- `method="chao-shen"`: E estimator. The alternative is `"shuffle"`.

`emc` profiles contain nonnegative fitted increments summing to E, with lengths
that may differ across sequences. `lz76` returns the backend's fields:
`complexity`, `h`, `factors`, `emc`, `epsilon`, `factors_stddev`, `normal_error`,
`poison_error`, and `extras`. The nested `emc` dictionary includes its method,
value, increments, actual maximum range, and raw first-range contrast.

Factor boundaries are positions in the prepared symbolic sequence, not the
original float observations if discretization changed length. The final copied
tail can appear in boundaries without contributing to the factor count, and the
final boundary can extend beyond the sequence end.

### Distance inputs

One input calculates all unordered pairs once and mirrors them, retaining actual
self-distances. Two inputs calculate corresponding pairs only; their shapes
outside the sequence axis must match exactly. Observation counts may differ.
Both inputs must use numeric categories or both use the same string kind
(Unicode/bytes). A shared codebook preserves the same category meanings.
NID does not use logarithm units.

## Discretization and registration

`discretize(data, method="mean", **kwargs)` accepts a nonempty finite numeric 1D
sequence and returns a 1D integer-label array. Built-ins are `mean`, `median`,
`bins`, `quantile`, and `permutation`; their rules are listed in the README.
Custom methods may change length, but must return nonempty 1D integer labels.
The input is copied before invocation.

`register_discretizer(name, function=None, *, replace=False)` works as either a
function call or decorator. Names must be nonempty strings; replacing a name
requires `replace=True`. Registration is session-local.

`available_discretizers()` returns the sorted tuple of registered labels.

## Validation and limits

Supported data: real numeric/boolean arrays and Unicode/byte-string arrays.
Scalar arrays, complex/object arrays, nonfinite numeric data, and empty sequence
axes are rejected. An empty collection with a nonempty observation axis returns
an appropriately shaped empty array.

Above 256 distinct categories, a standard `RuntimeWarning` is emitted and byte
labels wrap modulo 256. Results then merge categories and must not be interpreted
as faithful measurements of the original alphabet. Distances check the shared
vocabulary. One-sequence calculations still normalize using the original
observed category count.
