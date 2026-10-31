import lzcomplexity as backend
import numpy as np
import pytest

import lzsuite as lzs


def test_all_pairs_match_backend_and_keep_diagonal():
    values = np.array([[0, 1, 0, 0, 1, 1, 0, 1] * 10, [1, 0, 1, 1, 0, 0, 1, 0] * 10]).T
    matrix = lzs.distance(values)
    expected = np.array(
        [
            [
                backend.nid(a.astype(np.uint8).tobytes(), b.astype(np.uint8).tobytes())
                for b in values.T
            ]
            for a in values.T
        ]
    )
    np.testing.assert_array_equal(matrix, expected)
    np.testing.assert_array_equal(matrix, matrix.T)
    # This input happens to have zero self-distance; others do not.
    banana = np.array(list("banana"))
    assert lzs.distance(banana)[0, 0] == pytest.approx(1 / 3)
    assert lzs.nid is lzs.distance


def test_shared_codebook_does_not_make_disjoint_alphabets_identical():
    first = np.array(["a", "b", "a", "b"] * 20)
    second = np.array(["c", "d", "c", "d"] * 20)
    expected = backend.nid(bytes([0, 1] * 20), bytes([2, 3] * 20))
    assert lzs.distance(first, second).item() == expected
    assert lzs.distance(first, second).item() != lzs.distance(first, first).item()


def test_large_signed_and_unsigned_labels_do_not_lose_precision():
    first = np.array([-1, 2**63 - 1, -1, 2**63 - 1] * 20, dtype=np.int64)
    second = np.array([2**63, 2**64 - 1, 2**63, 2**64 - 1] * 20, dtype=np.uint64)
    expected = backend.nid(bytes([0, 1] * 20), bytes([2, 3] * 20))
    assert lzs.distance(first, second).item() == expected


@pytest.mark.parametrize("axis", [0, 1, 2, -1])
def test_corresponding_pairs_keep_other_axes_and_flatten_in_c_order(axis):
    values = np.random.default_rng(6).integers(0, 4, size=(10, 5, 7))
    paired = lzs.distance(values, values, axis=axis)
    matrix = lzs.distance(values, axis=axis)
    moved = np.moveaxis(values, axis, -1)
    assert paired.shape == moved.shape[:-1]
    np.testing.assert_array_equal(np.diag(matrix), paired.ravel())
    for flat, index in enumerate(np.ndindex(paired.shape)):
        a = moved[index].astype(np.uint8).tobytes()
        assert paired[index] == backend.nid(a, a)
        assert matrix[flat, flat] == paired[index]


def test_different_lengths_are_allowed_and_shape_mismatch_rejected():
    first = np.tile([0, 1], (30, 1))
    second = np.tile([1, 0], (40, 1))
    actual = lzs.distance(first, second)
    assert actual.shape == (2,)
    assert actual[0] == backend.nid(bytes(30), bytes([1] * 40))
    with pytest.raises(ValueError, match="Shapes outside"):
        lzs.distance(first, np.zeros((40, 3)))


def test_discretization_default_override_and_different_output_lengths():
    first = np.random.default_rng(8).normal(size=(100, 3))
    second = first[:80]
    expected = lzs.distance((first > first.mean(axis=0)).astype(int))
    np.testing.assert_array_equal(lzs.distance(first), expected)
    paired = lzs.distance(first, second, discretization="permutation")
    assert paired.shape == (3,)
    assert np.isfinite(paired).all()
    with pytest.raises(TypeError, match="numeric"):
        lzs.distance(np.array(["a", "b"]), discretization="mean")


def test_shared_alphabet_overflow_warns_once_and_keeps_result_shape():
    first = np.arange(150)
    second = np.arange(150, 300)
    with pytest.warns(lzs.AlphabetSizeWarning, match="300 distinct") as caught:
        actual = lzs.distance(first, second)
    assert len(caught) == 1
    expected = backend.nid(
        first.astype(np.uint8).tobytes(), (second % 256).astype(np.uint8).tobytes()
    )
    assert actual.item() == expected


def test_mixed_symbol_families_rejected():
    with pytest.raises(TypeError, match="same symbol type"):
        lzs.distance([0, 1], ["0", "1"])
    with pytest.raises(TypeError, match="same string representation"):
        lzs.distance(np.array([b"a", b"b"]), np.array(["a", "b"]))


def test_empty_collections():
    data = np.empty((10, 0), dtype=int)
    assert lzs.distance(data).shape == (0, 0)
    assert lzs.distance(data, data).shape == (0,)


def test_process_execution_matches_serial():
    data = np.random.default_rng(22).integers(0, 3, size=(100, 4))
    np.testing.assert_array_equal(lzs.distance(data, n_jobs=2), lzs.distance(data))
    np.testing.assert_array_equal(lzs.distance(data, data, n_jobs=2), lzs.distance(data, data))
