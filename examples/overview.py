"""Run with: uv run python examples/overview.py"""

import numpy as np

import lzsuite as lzs


def main():
    rng = np.random.default_rng(42)

    # 512 observations, 3 channels, 2 trials: six sequences along axis 0.
    data = rng.normal(size=(512, 3, 2))
    other = rng.normal(size=(400, 3, 2))

    # Floats are binarized at EACH sequence's mean by default.
    # The logarithm base uses its distinct symbols, with a minimum of 2.
    entropy = lzs.h(data)  # shape (3, 2): the sequence axis is removed
    counts = lzs.complexity(data)  # shape (3, 2): raw LZ76 factor counts

    # Any axis works, including negative axes. These are the same sequences.
    channels_first = np.moveaxis(data, 0, -1)  # shape (3, 2, 512)
    np.testing.assert_allclose(entropy, lzs.h(channels_first, axis=-1))

    # Full factorization: each result contains (count, boundary positions).
    factors = lzs.factorization(data)  # object array, shape (3, 2)
    count, boundaries = factors[0, 0]
    # The backend can return a final boundary beyond the sequence's end.

    # E and its profile. Each profile is a list of nonnegative increments.
    scores, profiles = lzs.emc(data, max_block_size=6)
    # scores/profiles have shape (3, 2); sum(profiles[i, j]) == scores[i, j].
    shuffle_scores, _ = lzs.emc(data, method="shuffle", max_block_size=6)

    # All backend measurements together, as one dictionary per sequence.
    full = lzs.lz76(data, max_block_size=6)
    print("First sequence:", full[0, 0])

    # Discretize one 1D signal directly, separately from any calculation.
    signal = data[:, 0, 0]
    print("Available methods:", lzs.available_discretizers())
    binary = lzs.discretize(signal, method="mean")
    median = lzs.discretize(signal, method="median")
    bins = lzs.discretize(signal, method="bins", n_bins=4)
    quantiles = lzs.discretize(signal, method="quantile", n_bins=4)
    patterns = lzs.discretize(signal, method="permutation", order=3, delay=2)
    # Permutations label local orderings; here the result is shorter by 4.
    # Threshold ties go to 0; permutation ties use earlier positions first.

    # Or ask a calculation to discretize EVERY sequence with the chosen method.
    binned_entropy = lzs.h(data, discretization="bins", discretization_kwargs={"n_bins": 4})
    # An explicit base overrides the automatic normalization if desired.
    entropy_in_bits = lzs.h(data, discretization="median", log_base=2)

    # Integers and booleans are already symbols: no default discretization.
    symbols = rng.integers(0, 4, size=(512, 3, 2))
    symbol_entropy = lzs.h(symbols)
    # Explicit discretization still works on numeric inputs, including integers.
    integer_binary_entropy = lzs.h(symbols, discretization="mean")

    # A string ARRAY treats each element as one category, even a whole word.
    categories = np.array(["rest", "move", "rest", "move"] * 64)
    category_entropy = lzs.h(categories)  # 1D input -> Python float
    # Asking to discretize strings raises TypeError. Empty/nonfinite data errors too.

    # Custom methods receive a 1D numeric array and return 1D integer labels.
    # They may change the sequence length. Their input is a copy.
    def threshold(values, *, level=0.0):
        return (values > level).astype(np.uint8)

    custom = lzs.h(data, discretization=threshold)  # direct callable
    lzs.register_discretizer("threshold", threshold)  # reusable by name
    registered = lzs.h(data, discretization="threshold", discretization_kwargs={"level": 0.5})

    # Registration also supports decorators. Use replace=True to overwrite a name.
    @lzs.register_discretizer("every_other")
    def every_other(values):
        return (values[::2] > 0).astype(np.uint8)

    shortened = lzs.h(data, discretization="every_other")

    # One array: all pairs of its six sequences -> a (6, 6) matrix.
    matrix = lzs.distance(data)
    # Matrix ordering is the C-order flattening of (channel, trial).
    # Its diagonal retains actual self-distances, which can be nonzero.

    # Two arrays: corresponding pairs -> shape (3, 2), with no broadcasting.
    # The other dimensions must match; sequence lengths may differ (512 vs 400).
    paired = lzs.distance(data, other)
    np.testing.assert_allclose(paired, lzs.nid(data, other))  # nid is an alias
    # Both modes accept discretization and discretization_kwargs as above.

    # Default: up to four processes, capped by available CPUs and task count.
    # n_jobs=1 runs serially; -1 uses all available CPUs. IPython works too.
    parallel = lzs.h(data, n_jobs=2)
    np.testing.assert_allclose(entropy, parallel)

    # Above 256 distinct symbols, analysis emits RuntimeWarning and continues.
    # Labels then collide, so results do not faithfully represent that alphabet.

    print("Entropy shape:", entropy.shape, "distance shapes:", matrix.shape, paired.shape)
    print("First factorization:", count, boundaries)
    print("First E:", scores[0, 0], "increments:", profiles[0, 0])
    print("Discretized lengths:", *(len(x) for x in (binary, median, bins, quantiles, patterns)))
    print("Other calculations:", counts, shuffle_scores, binned_entropy, entropy_in_bits)
    print("Symbol results:", symbol_entropy, integer_binary_entropy, category_entropy)
    print("Custom results:", custom, registered, shortened)


if __name__ == "__main__":
    main()
