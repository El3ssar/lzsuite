# User guide

## Inputs and preprocessing

| Topic | Scope |
|---|---|
| [Arrays and axes](arrays.md) | Sequence selection, batch dimensions, return shapes, and supported dtypes |
| [Discretization](discretization.md) | Mean, median, equal-width, quantile, and ordinal methods |
| [Custom discretizers](custom-methods.md) | Callable contract, registration, method parameters, and shared bin edges |

## Measurements and comparisons

| Topic | Scope |
|---|---|
| [LZ76 measurements](measures.md) | Factor count, factor boundaries, normalization, and entropy density |
| [Effective measure complexity](emc.md) | Chao–Shen and shuffle estimators, fitted profiles, and range selection |
| [Information distance](distances.md) | All-pairs matrices, corresponding comparisons, and shared symbol encoding |
| [Parallel execution](parallel.md) | Process counts, worker reuse, Rayon threads, and memory costs |

The [API reference](../api.md) documents exact signatures and return types.
[Result conventions](../reference/results.md) and
[scientific interpretation](../concepts/interpretation.md) cover finite-sample
behavior and estimator assumptions.
