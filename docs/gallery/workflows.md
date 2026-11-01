# Array calculations

## Channel and trial dimensions

[![Four example channels and their four-by-three entropy heatmap illustrate the sequence-axis contract.](../assets/figures/axes.svg){ .plot }](../assets/figures/axes.svg "Open full-size figure")

[![Four example channels and their four-by-three entropy heatmap illustrate the sequence-axis contract.](../assets/figures/dark/axes.svg){ .plot }](../assets/figures/dark/axes.svg "Open full-size figure")

The gallery data are shaped `(2048, 4, 3)`. Only the observation axis is removed
by `h`, so each output position still identifies one channel and one trial.

```python
import numpy as np
import lzsuite as lzs

x = np.random.default_rng(42).normal(size=(2048, 4, 3))
lzs.h(x).shape  # (4, 3)
```

[SVG](../assets/figures/axes.svg) · [PNG](../assets/figures/axes.png)

## Fixed thresholds

[![A fixed threshold changes the fraction of ones and the measured LZ76 entropy in the same observations.](../assets/figures/custom-threshold.svg){ .plot }](../assets/figures/custom-threshold.svg "Open full-size figure")

[![A fixed threshold changes the fraction of ones and the measured LZ76 entropy in the same observations.](../assets/figures/dark/custom-threshold.svg){ .plot }](../assets/figures/dark/custom-threshold.svg "Open full-size figure")

```python
def fixed_threshold(values, *, level=0.0):
    return (values > level).astype(np.uint8)


lzs.h(
    x,
    discretization=fixed_threshold,
    discretization_kwargs={"level": 0.5},
)
```

The signal is unchanged; its representation changes. Record that rule alongside
your results. A shared fixed threshold preserves different information from a
mean fitted independently to each recording.

[SVG](../assets/figures/custom-threshold.svg) · [PNG](../assets/figures/custom-threshold.png)

## Serial and parallel agreement

[![Inline and two-process results overlap for twelve sequences and their pointwise differences are exactly zero.](../assets/figures/parallel-agreement.svg){ .plot }](../assets/figures/parallel-agreement.svg "Open full-size figure")

[![Inline and two-process results overlap for twelve sequences and their pointwise differences are exactly zero.](../assets/figures/dark/parallel-agreement.svg){ .plot }](../assets/figures/dark/parallel-agreement.svg "Open full-size figure")

```python
serial = lzs.h(x, n_jobs=1)
parallel = lzs.h(x, n_jobs=2)
np.testing.assert_array_equal(serial, parallel)
```

The two calls return identical entropy estimates. Runtime and memory use depend
on input size, operation, method, hardware, and process startup. See the [parallel guide](../guide/parallel.md) for the execution budget.

[SVG](../assets/figures/parallel-agreement.svg) · [PNG](../assets/figures/parallel-agreement.png)

## Factorization

[![The string banana is shown with three completed phrases and a copied tail excluded from the count.](../assets/figures/factorization.svg){ .plot }](../assets/figures/factorization.svg "Open full-size figure")

[![The string banana is shown with three completed phrases and a copied tail excluded from the count.](../assets/figures/dark/factorization.svg){ .plot }](../assets/figures/dark/factorization.svg "Open full-size figure")

```python
count, boundaries = lzs.factorization(np.array(list("banana")))
count, boundaries  # (3, [0, 1, 2, 3, 7])
```

The attempted final end is retained even beyond the sequence. See the
[result conventions](../reference/results.md) before interpreting boundary lists.

[SVG](../assets/figures/factorization.svg) · [PNG](../assets/figures/factorization.png)
