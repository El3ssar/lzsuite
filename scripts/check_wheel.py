"""Smoke-test an installed distribution; run with an isolated Python interpreter."""

import numpy as np

import lzsuite as lzs


def main():
    values = np.random.default_rng(42).normal(size=(256, 4))
    assert type(lzs.h(values[:, 0])) is float
    assert type(lzs.complexity(values[:, 0])) is int
    assert type(lzs.factorization(values[:, 0])) is tuple
    assert type(lzs.lz76(values[:, 0])) is dict
    score, profile = lzs.emc(values[:, 0], max_block_size=4)
    assert type(score) is float and type(profile) is list
    assert type(lzs.distance(values[:, 0], values[:, 1])) is float
    np.testing.assert_array_equal(lzs.h(values), lzs.h(values, n_jobs=1))
    assert lzs.distance(values).shape == (4, 4)
    assert lzs.distance(values, values).shape == (4,)
    assert all(callable(getattr(lzs, name)) for name in lzs.__all__)
    print(f"Installed lzsuite {lzs.__version__}: scalar, array, and parallel checks passed.")


if __name__ == "__main__":
    main()
