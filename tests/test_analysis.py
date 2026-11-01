import lzcomplexity as backend
import numpy as np
import pytest

import lzsuite as lzs


def reference_symbols(sequence):
    vocabulary, labels = np.unique(sequence, return_inverse=True)
    return labels.astype(np.uint8).tobytes(), max(2, len(vocabulary))


@pytest.mark.parametrize("axis", [0, 1, 2, -1, -2, -3])
def test_every_sequence_axis_matches_backend(axis):
    values = np.random.default_rng(42).integers(0, 5, size=(13, 7, 9))
    moved = np.moveaxis(values, axis, -1)
    expected = np.empty(moved.shape[:-1])
    for index in np.ndindex(expected.shape):
        symbols, base = reference_symbols(moved[index])
        expected[index] = backend.h(symbols, log_base=base)
    np.testing.assert_allclose(lzs.h(values, axis=axis), expected)


def test_noncontiguous_arrays_and_numeric_categories():
    values = np.array([[-100, 500, -100, 900, 500, 900]] * 3).T[::-1, ::2]
    expected = []
    for row in values.T:
        symbols, base = reference_symbols(row)
        expected.append(backend.h(symbols, log_base=base))
    np.testing.assert_allclose(lzs.h(values), expected)


def test_float_default_and_explicit_numeric_override():
    values = np.array([[0.0, 8.0], [1.0, 2.0], [9.0, 3.0]])
    expected = np.array([backend.h(bytes([0, 0, 1])), backend.h(bytes([1, 0, 0]))])
    np.testing.assert_allclose(lzs.h(values), expected)
    np.testing.assert_allclose(lzs.h(values.astype(int), discretization="mean"), expected)
    np.testing.assert_allclose(
        lzs.h(values, discretization="median"), lzs.h(values > np.median(values, axis=0))
    )


def test_symbols_preserve_observations_instead_of_decimal_serialization():
    values = np.array([0, 1, 10, 0, 1, 10])
    assert lzs.h(values).item() == backend.h(bytes([0, 1, 2, 0, 1, 2]))
    # Each multi-character string is one symbol, not a stream of characters.
    text = np.array(["red", "blue", "red", "green", "blue", "green"])
    symbols, base = reference_symbols(text)
    assert lzs.h(text).item() == backend.h(symbols, log_base=base)
    assert lzs.h(text).shape == ()
    with pytest.raises(TypeError, match="numeric"):
        lzs.h(text, discretization="mean")


def test_each_sequence_uses_its_own_observed_log_base():
    values = np.array([[0, 0], [1, 1], [0, 2], [1, 3]] * 30)
    for column, base in [(0, 2), (1, 4)]:
        symbols, _ = reference_symbols(values[:, column])
        assert lzs.h(values)[column] == backend.h(symbols, log_base=base)
    np.testing.assert_allclose(lzs.h(values, log_base=2), lzs.h(values) * [1, 2])
    assert lzs.h(np.zeros(16, dtype=int)).item() == backend.h(bytes(16), log_base=2)


@pytest.mark.parametrize("method", ["chao-shen", "shuffle"])
def test_all_outputs_match_native_backend(method):
    values = np.array([[0, 1, 0, 0, 1, 1, 0, 1] * 20, [0, 1, 2, 3] * 40]).T
    counts = lzs.complexity(values)
    factors = lzs.factorization(values)
    scores, profiles = lzs.emc(values, method=method, max_block_size=4)
    full = lzs.lz76(values, method=method, max_block_size=4)
    assert counts.shape == factors.shape == scores.shape == profiles.shape == full.shape == (2,)
    for i, row in enumerate(values.T):
        symbols, base = reference_symbols(row)
        options = {"method": method, "max_block_size": 4, "log_base": base}
        assert factors[i] == backend.factorization(symbols)
        assert counts[i] == factors[i][0]
        assert (scores[i], profiles[i]) == backend.emc(symbols, **options)
        assert full[i] == backend.lz76(symbols, **options)


def test_shortened_custom_outputs_and_permutations():
    data = np.arange(12).reshape(6, 2)
    shortened = lambda values: (values[::2] > 4).astype(int)  # noqa: E731
    expected = lzs.h((data[::2] > 4).astype(int))
    np.testing.assert_allclose(lzs.h(data, discretization=shortened), expected)
    assert lzs.factorization(data, discretization="permutation")[0] == (1, [0, 1, 4])


def test_overflow_warns_and_continues_with_documented_mapping():
    values = np.arange(300)
    with pytest.warns(RuntimeWarning, match="300 distinct symbols"):
        actual = lzs.h(values)
    expected = backend.h((values % 256).astype(np.uint8).tobytes(), log_base=300)
    assert actual.item() == expected
    # Exactly 256 categories needs no warning (warnings are errors in this suite).
    assert np.isfinite(lzs.h(np.arange(256)))


@pytest.mark.parametrize("values,axis", [(42, 0), (np.zeros((3, 2)), 2), (np.empty((0, 2)), 0)])
def test_invalid_shapes(values, axis):
    with pytest.raises(ValueError):
        lzs.h(values, axis=axis)


@pytest.mark.parametrize("values", [[np.nan], [np.inf], [1 + 2j], np.array([1], dtype=object)])
def test_invalid_values(values):
    with pytest.raises((ValueError, TypeError)):
        lzs.h(values)


@pytest.mark.parametrize("base", [0, 1, -2, 2.5, True])
def test_invalid_base(base):
    with pytest.raises((ValueError, TypeError)):
        lzs.h([0, 1], log_base=base)


@pytest.mark.parametrize("jobs", [0, -2, 1.5, True])
def test_invalid_jobs(jobs):
    with pytest.raises((ValueError, TypeError)):
        lzs.h([0, 1], n_jobs=jobs)


def test_empty_collections_and_backend_error_propagation():
    data = np.empty((10, 0, 3), dtype=int)
    assert lzs.h(data).shape == (0, 3)
    assert lzs.factorization(data).shape == (0, 3)
    assert lzs.lz76(data).shape == (0, 3)
    scores, profiles = lzs.emc(data)
    assert scores.shape == profiles.shape == (0, 3)
    with pytest.raises(ValueError, match="method must"):
        lzs.emc([0, 1], method="bad")
    with pytest.raises(ValueError, match="requires a discretization method"):
        lzs.h([0, 1], discretization_kwargs={"n_bins": 4})


def test_parallel_and_serial_results_agree_with_local_discretizer():
    data = np.random.default_rng(3).normal(size=(100, 3))

    def local(values):
        return (values[::2] > 0).astype(int)

    np.testing.assert_array_equal(
        lzs.h(data, discretization=local, n_jobs=2),
        lzs.h(data, discretization=local),
    )
    serial = lzs.lz76(data, max_block_size=4)
    parallel = lzs.lz76(data, max_block_size=4, n_jobs=2)
    assert parallel.tolist() == serial.tolist()


def test_auto_jobs_with_single_sequence():
    assert lzs.h([0, 1], n_jobs=-1) == lzs.h([0, 1])
