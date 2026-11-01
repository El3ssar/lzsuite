---
title: Overview
hide:
  - toc
---

# lzsuite

<p class="project-description">Lempel–Ziv analysis for multidimensional NumPy arrays.</p>

lzsuite provides sequence complexity, entropy density, effective measure
complexity, and normalized information distance using
[lzcomplexity](https://github.com/pleros-ai/lzcomplexity). It adds discretization,
array-axis handling, and parallel execution across sequences.

<div class="project-links">
<a href="guide/quickstart/">Quickstart</a>
<a href="api/">API reference</a>
<a href="https://github.com/El3ssar/lzsuite">GitHub</a>
<a href="https://pypi.org/project/lzsuite/">PyPI</a>
</div>

## Installation

Requires Python 3.10 or newer.

```sh
pip install lzsuite
```

For uv projects, use `uv add lzsuite`. See [installation](guide/installation.md)
for dependencies and development setup.

## Array analysis

Set `axis` to the dimension containing successive observations. Every position
in the remaining dimensions identifies a separate sequence.

```python
import numpy as np
import lzsuite as lzs

rng = np.random.default_rng(42)
data = rng.normal(size=(2000, 4, 3))  # samples, channels, trials

entropy = lzs.h(data, axis=0)
entropy.shape  # (4, 3)
```

Float sequences are binarized at their own mean by default. Use a registered
method or callable to select a different discretization rule. Integer, boolean,
and string arrays are treated as discrete symbols.

```python
entropy = lzs.h(data, discretization="median")
matrix = lzs.distance(data)  # (12, 12): all sequence pairs
paired = lzs.distance(data, data)  # (4, 3): corresponding pairs
```

Single-sequence measurements return Python scalars or result tuples. Batched
calculations preserve the dimensions outside the sequence axis. Independent
calculations use up to four processes by default; set `n_jobs=1` for serial
execution.

## Functions

| Measurement or operation | Functions |
|---|---|
| Entropy density | [`h`](reference/h.md) |
| LZ76 factor count and boundaries | [`complexity`](reference/complexity.md), [`factorization`](reference/factorization.md) |
| Effective measure complexity | [`emc`](reference/emc.md) |
| Complete analysis result | [`lz76`](reference/lz76.md) |
| Normalized information distance | [`distance`](reference/distance.md), `nid` |
| Discretization and registration | [`discretize`](reference/discretization.md), [`register_discretizer`](reference/discretization.md#lzsuite.register_discretizer), [`available_discretizers`](reference/discretization.md#lzsuite.available_discretizers) |

## Numerical examples

[![Entropy density and effective measure complexity for six binary sequences, each with 8192 observations.](assets/figures/measures.svg){ .plot }](assets/figures/measures.svg "Open full-size figure")

[![Entropy density and effective measure complexity for six binary sequences, each with 8192 observations.](assets/figures/dark/measures.svg){ .plot }](assets/figures/dark/measures.svg "Open full-size figure")

The examples compare constant, periodic, persistent, and independent sequences.
Effective measure complexity uses a fixed maximum block size of six.
[Entropy and complexity examples](gallery/structure.md) explain the calculations
and finite-sample behavior.

Other examples cover [thresholds and bins](gallery/discretization.md),
[ordinal patterns](gallery/permutations.md), [distance matrices](gallery/distances.md),
and [array calculations](gallery/workflows.md). All figures include source code
and downloadable exports.
