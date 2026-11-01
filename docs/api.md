# API at a glance

A small top-level namespace contains only the functions users call. All
implementation modules are private. Use `help(lzs.h)` or `lzs.h?` in IPython for
the same NumPy-style parameter documentation rendered in this site.

## Measurements

| Function | One 1D sequence | Batch input |
|---|---|---|
| [`h`](reference/analysis.md#lzsuite.h) | `float` | Float ndarray |
| [`complexity`](reference/analysis.md#lzsuite.complexity) | `int` | Integer ndarray |
| [`factorization`](reference/analysis.md#lzsuite.factorization) | `(count, boundaries)` | Object ndarray of tuples |
| [`emc`](reference/analysis.md#lzsuite.emc) | `(score, increments)` | Score ndarray plus object ndarray of lists |
| [`lz76`](reference/analysis.md#lzsuite.lz76) | Dictionary | Object ndarray of dictionaries |

Common keyword arguments are `axis=0`, `discretization=None`,
`discretization_kwargs=None`, and `n_jobs=4`. h, E, and full analysis accept
`log_base=None`. E and full analysis also accept `max_block_size=-1` and
`method="chao-shen"`.

## Comparisons

| Call | Result |
|---|---|
| [`distance(data)`](reference/distance.md#lzsuite.distance) | M-by-M all-pairs matrix |
| `distance(data, other)` | Corresponding distances, batch shape preserved |
| `distance(sequence, other_sequence)` | Python float |
| `nid(...)` | Alias for `distance` |

## Representation

| Function | Purpose |
|---|---|
| [`discretize`](reference/discretization.md#lzsuite.discretize) | Apply a named or callable 1D discretizer |
| [`available_discretizers`](reference/discretization.md#lzsuite.available_discretizers) | Sorted tuple of registered names |
| [`register_discretizer`](reference/discretization.md#lzsuite.register_discretizer) | Register directly or as a decorator |

See [built-in rules](reference/methods.md), [result conventions](reference/results.md),
and the [full guides](guide/quickstart.md) for contracts and examples.
