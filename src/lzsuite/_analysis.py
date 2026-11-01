"""Lempel–Ziv measurements along an arbitrary array axis."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ._arrays import object_array, prepare
from ._discretization import Discretization
from ._encoding import encode
from ._execution import calculate_many


def _analyze(
    data: ArrayLike,
    operation: str,
    *,
    axis: int,
    discretization: Discretization,
    discretization_kwargs: Mapping[str, Any] | None,
    n_jobs: int,
    log_base: int | None = None,
    **kwargs: Any,
) -> tuple[list[Any], tuple[int, ...]]:
    if log_base is not None:
        if isinstance(log_base, (bool, np.bool_)) or not isinstance(log_base, (int, np.integer)):
            raise TypeError("log_base must be an integer of at least two, or None.")
        if log_base < 2:
            raise ValueError("log_base must be at least two.")
    sequences, shape = prepare(data, axis, discretization, discretization_kwargs)
    tasks = []
    for sequence in sequences:
        symbols, observed_base = encode(sequence)
        options = {**kwargs, "log_base": observed_base if log_base is None else int(log_base)}
        tasks.append((operation, (symbols,), options))
    return calculate_many(tasks, n_jobs), shape


def h(
    data: ArrayLike,
    *,
    axis: int = 0,
    discretization: Discretization = None,
    discretization_kwargs: Mapping[str, Any] | None = None,
    n_jobs: int = 1,
    log_base: int | None = None,
) -> NDArray:
    """Return entropy density per sequence; the result removes ``axis``.

    Floats default to mean binarization. Integers, booleans and strings are
    symbols unless a numeric discretizer is explicitly supplied. The log base
    defaults to each discretized sequence's distinct-symbol count (minimum 2).
    """
    results, shape = _analyze(
        data,
        "h",
        axis=axis,
        discretization=discretization,
        discretization_kwargs=discretization_kwargs,
        n_jobs=n_jobs,
        log_base=log_base,
    )
    return np.asarray(results, dtype=float).reshape(shape)


def complexity(
    data: ArrayLike,
    *,
    axis: int = 0,
    discretization: Discretization = None,
    discretization_kwargs: Mapping[str, Any] | None = None,
    n_jobs: int = 1,
) -> NDArray:
    """Return the LZ76 factor count per sequence, removing ``axis``."""
    results, shape = _analyze(
        data,
        "complexity",
        axis=axis,
        discretization=discretization,
        discretization_kwargs=discretization_kwargs,
        n_jobs=n_jobs,
    )
    return np.asarray(results, dtype=np.int64).reshape(shape)


def factorization(
    data: ArrayLike,
    *,
    axis: int = 0,
    discretization: Discretization = None,
    discretization_kwargs: Mapping[str, Any] | None = None,
    n_jobs: int = 1,
) -> NDArray:
    """Return an object array of ``(count, boundaries)`` entries, removing ``axis``.

    Boundaries describe the discretized sequence and retain the backend's
    final-tail convention; a final boundary may exceed the sequence length.
    """
    results, shape = _analyze(
        data,
        "factorization",
        axis=axis,
        discretization=discretization,
        discretization_kwargs=discretization_kwargs,
        n_jobs=n_jobs,
    )
    return object_array(results, shape)


def emc(
    data: ArrayLike,
    *,
    axis: int = 0,
    discretization: Discretization = None,
    discretization_kwargs: Mapping[str, Any] | None = None,
    n_jobs: int = 1,
    log_base: int | None = None,
    max_block_size: int = -1,
    method: str = "chao-shen",
) -> tuple[NDArray, NDArray]:
    """Return ``(scores, profiles)`` with both arrays shaped by removing ``axis``.

    ``profiles`` is an object array of increment lists, which can differ in
    length. ``method`` selects the backend E estimator, not the discretizer.
    """
    results, shape = _analyze(
        data,
        "emc",
        axis=axis,
        discretization=discretization,
        discretization_kwargs=discretization_kwargs,
        n_jobs=n_jobs,
        log_base=log_base,
        max_block_size=max_block_size,
        method=method,
    )
    scores = np.asarray([result[0] for result in results], dtype=float).reshape(shape)
    return scores, object_array([result[1] for result in results], shape)


def lz76(
    data: ArrayLike,
    *,
    axis: int = 0,
    discretization: Discretization = None,
    discretization_kwargs: Mapping[str, Any] | None = None,
    n_jobs: int = 1,
    log_base: int | None = None,
    max_block_size: int = -1,
    method: str = "chao-shen",
) -> NDArray:
    """Return an object array of full backend result dictionaries, removing ``axis``."""
    results, shape = _analyze(
        data,
        "lz76",
        axis=axis,
        discretization=discretization,
        discretization_kwargs=discretization_kwargs,
        n_jobs=n_jobs,
        log_base=log_base,
        max_block_size=max_block_size,
        method=method,
    )
    return object_array(results, shape)
