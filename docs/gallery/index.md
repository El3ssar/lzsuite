# Examples

Worked examples with synthetic data, executable Python snippets, and measured
results. Each figure is available as SVG and PNG, with separate light and dark
versions. Select a figure to open its SVG at full size.

| Topic | Contents |
|---|---|
| [Thresholds and bins](discretization.md) | Mean and median binarization, equal-width bins, quantile bins |
| [Ordinal patterns](permutations.md) | Sliding windows, permutation ranks, ties, and label counts |
| [Entropy and complexity](structure.md) | h and E, fitted profiles, estimator choice, and sequence length |
| [Distance matrices](distances.md) | All-pairs NID and comparisons of corresponding sequences |
| [Array calculations](workflows.md) | Axis selection, custom thresholds, parallel agreement, and factorization |
| [Figure generation](reproduce.md) | Source, random seeds, numerical provenance, and exports |

## Discretization

[![Mean and median thresholds and their binary labels for a sequence containing one outlier.](../assets/figures/thresholds.svg){ .plot }](../assets/figures/thresholds.svg "Open full-size figure")

[![Mean and median thresholds and their binary labels for a sequence containing one outlier.](../assets/figures/dark/thresholds.svg){ .plot }](../assets/figures/dark/thresholds.svg "Open full-size figure")

[Threshold and bin examples](discretization.md) compare how discretization rules
assign symbols to the same observations.

## Information distance

[![An eight-by-eight normalized information-distance matrix for periodic sequences, noisy variants, and independent sequences.](../assets/figures/distance-matrix.svg){ .plot }](../assets/figures/distance-matrix.svg "Open full-size figure")

[![An eight-by-eight normalized information-distance matrix for periodic sequences, noisy variants, and independent sequences.](../assets/figures/dark/distance-matrix.svg){ .plot }](../assets/figures/dark/distance-matrix.svg "Open full-size figure")

[Distance examples](distances.md) describe the input sequences, matrix ordering,
and finite-length self-distances.
