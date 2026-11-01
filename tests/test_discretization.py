import itertools

import numpy as np
import pytest

import lzsuite as lzs
from lzsuite import _discretization as disc


def test_thresholds_and_ties():
    values = [0.0, 1.0, 2.0]
    np.testing.assert_array_equal(disc.binarize_mean(values), [0, 0, 1])
    np.testing.assert_array_equal(disc.binarize_median(values), [0, 0, 1])
    for method in (
        disc.binarize_mean,
        disc.binarize_median,
        disc.bin_equal_width,
        disc.bin_quantile,
    ):
        np.testing.assert_array_equal(method([5, 5, 5]), [0, 0, 0])


def test_bins_include_endpoints_and_send_edge_ties_right():
    np.testing.assert_array_equal(disc.bin_equal_width([0, 1, 2, 3, 4], n_bins=4), [0, 1, 2, 3, 3])
    np.testing.assert_array_equal(disc.bin_quantile([0, 1, 2, 3, 4], n_bins=2), [0, 0, 1, 1, 1])
    # Repeated quantile edges collapse rather than leaving many empty bins.
    np.testing.assert_array_equal(disc.bin_quantile([0, 0, 0, 1], n_bins=4), [1, 1, 1, 2])
    np.testing.assert_array_equal(disc.bin_equal_width([0, 1], n_bins=1), [0, 0])


@pytest.mark.parametrize("order", [1, 2, 3, 4, 5])
def test_permutation_labels_are_lexicographic_ranks(order):
    for rank, ordering in enumerate(itertools.permutations(range(order))):
        values = np.empty(order, dtype=int)
        values[list(ordering)] = np.arange(order)
        np.testing.assert_array_equal(disc.permutation(values, order=order), [rank])


def test_permutation_delay_and_repeated_values():
    values = np.array([2, 99, 1, 88, 0, 77])
    np.testing.assert_array_equal(disc.permutation(values, order=3, delay=2), [5, 5])
    np.testing.assert_array_equal(disc.permutation([4, 4, 4, 4]), [0, 0])
    with pytest.raises(ValueError, match="shorter"):
        disc.permutation([0, 1], order=3)
    with pytest.raises(ValueError, match="20"):
        disc.permutation(np.arange(21), order=21)


def test_registry_and_callable_support_length_changes_without_mutating_input(monkeypatch):
    monkeypatch.setattr(disc, "_REGISTRY", disc._REGISTRY.copy())

    @lzs.register_discretizer("shortened")
    def shortened(values, *, stride=2):
        values[:] = values > values.mean()
        return values[::stride].astype(int)

    original = np.arange(6.0)
    np.testing.assert_array_equal(lzs.discretize(original, "shortened"), [0, 0, 1])
    np.testing.assert_array_equal(lzs.discretize(original, shortened, stride=3), [0, 1])
    np.testing.assert_array_equal(original, np.arange(6.0))
    assert "shortened" in lzs.available_discretizers()
    with pytest.raises(ValueError, match="already registered"):
        lzs.register_discretizer("shortened", shortened)
    lzs.register_discretizer("shortened", lambda x: [0], replace=True)
    np.testing.assert_array_equal(lzs.discretize(original, "shortened"), [0])


@pytest.mark.parametrize("values", [["a", "b"], [1 + 1j, 2], np.array([1, 2], dtype=object)])
def test_discretizers_reject_nonnumeric_inputs(values):
    with pytest.raises(TypeError, match="numeric"):
        lzs.discretize(values)


@pytest.mark.parametrize("values", [[], [[1, 2]], [0, np.nan], [0, np.inf]])
def test_discretizers_reject_invalid_sequences(values):
    with pytest.raises(ValueError):
        lzs.discretize(values)


@pytest.mark.parametrize("result", [[[0, 1]], [0.5, 1.0], ["a", "b"]])
def test_custom_discretizer_contract(result):
    with pytest.raises(TypeError, match="integer labels"):
        lzs.discretize([0, 1], lambda x: result)
    with pytest.raises(ValueError, match="empty sequence"):
        lzs.discretize([0, 1], lambda x: np.array([], dtype=int))


@pytest.mark.parametrize("value", [0, -1, 1.5, True])
def test_discretizer_parameter_validation(value):
    for function in (disc.bin_equal_width, disc.bin_quantile):
        with pytest.raises((TypeError, ValueError)):
            function([0, 1, 2], n_bins=value)
    with pytest.raises((TypeError, ValueError)):
        disc.permutation([0, 1, 2], order=value)


def test_registry_validation():
    with pytest.raises(ValueError, match="Unknown discretizer"):
        lzs.discretize([0, 1], "missing")
    with pytest.raises(ValueError, match="nonempty"):
        lzs.register_discretizer(" ", lambda x: x)
    with pytest.raises(TypeError, match="callable"):
        lzs.register_discretizer("bad", 42)
    with pytest.raises(TypeError, match="callable"):
        lzs.discretize([0, 1], 42)
