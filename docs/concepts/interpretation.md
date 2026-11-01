# Interpret the measurement you actually made

lzsuite makes a sequence-analysis workflow convenient. It does not remove the
need to choose a meaningful observation, control preprocessing, or assess
finite-sample uncertainty.

## Representation defines the observation

A binary threshold preserves high/low states. Quantile bins preserve relative
levels under a fitted empirical distribution. Ordinal patterns preserve local
orderings. A temporal sequence at one channel differs from a spatial sequence
across channels at one instant. State which axis, sampling scheme, and
symbolization define your observations.

Float defaults are conveniences, not recommendations for every dataset. Compare
per-sequence mean fitting with shared physical thresholds when absolute levels
matter. Handle missing samples before analysis according to a domain-appropriate
protocol; silently dropping them changes which observations are neighbors.

## Finite samples and normalization

The LZ76 normalized count is an entropy-rate estimator for a symbolic sequence.
Asymptotic source interpretations require assumptions, including appropriate
stationarity and ergodicity. Finite-length values depend on phrase-count
conventions, representation, and sample length. h can exceed one and is not clipped.

The default log base follows the *observed prepared alphabet*. Two samples can
therefore have different default units if one lacks some categories. Use an
explicit common base when that better matches the comparison.

See the upstream [LZ76 implementation guide](https://pleros-ai.github.io/lzcomplexity/concepts/lz76/)
and [entropy-density discussion](https://pleros-ai.github.io/lzcomplexity/concepts/entropy-density/).
The original parsing reference is Lempel and Ziv (1976),
[On the Complexity of Finite Sequences](https://doi.org/10.1109/TIT.1976.1055501).

## E is a finite-range estimator

Chao–Shen uses overlapping-window histograms, an LZ rate contribution, and a
nonnegative isotonic fit. Shuffle uses deterministic surrogate sequences and a
different contrast formula. Their scores are operational estimates, not identical
methods with interchangeable values. Keep method and range explicit.

Automatic caps change with sample length and alphabet. To study length alone,
first use a fixed cap. For sparsely observed blocks, entropy estimation remains
limited; an all-singleton histogram uses a plug-in fallback. An appealing E
curve is not evidence by itself for a particular dynamical mechanism.

The backend's [E documentation](https://pleros-ai.github.io/lzcomplexity/concepts/emc/)
and [implementation details](https://pleros-ai.github.io/lzcomplexity/concepts/implementation/)
provide the exact formulas and conventions.

## NID is not an ordinary samplewise distance

LZ76 NID compares concatenation factor counts. It is symmetric but can have
nonzero self-distance for finite sequences. It does not compare amplitudes,
align observations, or compute edit distance. Shared encodings are necessary.
Avoid treating a visually grouped matrix as proof of a causal relationship.

## Diagnostics are not general confidence intervals

`epsilon`, `normal_error`, `poison_error`, `factors_stddev`, and the half-sequence
extras are backend diagnostic formulas. They are not replacements for sampling
uncertainty from repeated trials, independent realizations, or a resampling
scheme that respects temporal dependence.

## A reproducible result includes its choices

Record at least:

- Input or a fingerprint, sampling interval, window boundaries, and sequence axis.
- Discretization rule, fitted thresholds/edges when relevant, and tie policy.
- Prepared length and observed alphabet; shared codebook when comparing categories.
- Logarithm base, E estimator, requested/actual range, and package versions.
- Repetition or uncertainty protocol and any downstream matrix transformations.

Identical prepared bytes and settings give deterministic calculations. Repeating
an identical call measures execution stability, not scientific sampling variation.
