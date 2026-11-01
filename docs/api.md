# API reference

Import public functions from `lzsuite`. In Python, `help(lzs.h)` displays the
same source docstring used to generate the function reference.

## Measurements

| Function | One 1D sequence | Batch input |
|---|---|---|
| [`h`](reference/h.md#lzsuite.h) | `float` | Float ndarray |
| [`complexity`](reference/complexity.md#lzsuite.complexity) | `int` | Integer ndarray |
| [`factorization`](reference/factorization.md#lzsuite.factorization) | `(count, boundaries)` | Object ndarray of tuples |
| [`emc`](reference/emc.md#lzsuite.emc) | `(score, increments)` | Score ndarray plus object ndarray of lists |
| [`lz76`](reference/lz76.md#lzsuite.lz76) | Dictionary | Object ndarray of dictionaries |

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

## Discretization

| Function | Purpose |
|---|---|
| [`discretize`](reference/discretization.md#lzsuite.discretize) | Apply a named or callable 1D discretizer |
| [`available_discretizers`](reference/discretization.md#lzsuite.available_discretizers) | Sorted tuple of registered names |
| [`register_discretizer`](reference/discretization.md#lzsuite.register_discretizer) | Register directly or as a decorator |

See [built-in rules](reference/methods.md), [result conventions](reference/results.md),
and the [full guides](guide/quickstart.md) for contracts and examples.
