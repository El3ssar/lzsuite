"""All-pairs distances within an array, or corresponding pairs between arrays."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ._arrays import prepare
from ._discretization import Discretization
from ._encoding import encode_shared
from ._execution import calculate_many


def distance(
    data: ArrayLike,
    other: ArrayLike | None = None,
    *,
    axis: int = 0,
    discretization: Discretization = None,
    discretization_kwargs: Mapping[str, Any] | None = None,
    n_jobs: int = 4,
) -> float | NDArray:
    """Calculate all-pairs or corresponding-pair LZ76 information distances.

    Parameters
    ----------
    data : array_like
        Real numeric, boolean, Unicode-string, or byte-string array. Each
        position outside ``axis`` identifies one sequence. Floats default
        to per-sequence mean binarization; other supported dtypes are symbols.
    other : array_like, optional
        Omit for all pairs within ``data``. Otherwise compare corresponding
        sequences; shapes outside ``axis`` must match exactly. Observation
        counts may differ, including after discretization.
    axis : int, default=0
        Axis containing successive observations. Negative axes are accepted.
    discretization : str or callable, optional
        Registered method name or function applied to each numeric sequence.
        Overrides automatic mean binarization. Strings cannot be discretized.
    discretization_kwargs : mapping of str to object, optional
        Keyword arguments passed to the selected discretizer. Custom methods
        receive an input copy and may return a different sequence length.
    n_jobs : int, default=4
        Maximum worker processes, capped by available CPUs and calculation
        count. Use 1 for inline execution or -1 for all available CPUs.

    Returns
    -------
    distances : float or numpy.ndarray
        With one input, an M-by-M float matrix for M sequences, including
        actual self-distances. Matrix order is C-order flattening of the
        dimensions outside ``axis``. A single 1D input returns shape (1, 1).
        With two 1D inputs, a Python float. Otherwise an array shaped like
        either input with ``axis`` removed. No broadcasting is performed.

    Raises
    ------
    TypeError
        If dtypes are unsupported, numeric and string categories are mixed,
        string representations differ, or a parameter type is invalid.
    ValueError
        If batch shapes differ, an axis is invalid, observations are empty
        or nonfinite, or discretization/execution settings are invalid.

    Warns
    -----
    RuntimeWarning
        If the shared vocabulary exceeds 256 categories. Labels then merge
        modulo 256 and the original alphabet is not faithfully represented.

    Notes
    -----
    For factor count C, the backend computes
    max(C(XY) - C(X), C(YX) - C(Y)) / max(C(X), C(Y)).
    The result is symmetric but finite-sequence self-distance can be nonzero.
    There is no clipping or forced zero diagonal. A shared codebook preserves
    category meanings across all inputs; independent codebooks would not.
    The logarithm base does not enter this ratio.

    For float data, thresholds or bin edges are fitted separately to each
    sequence unless a custom fixed-rule discretizer is supplied. The same
    method is used for both operands. ``nid`` is an alias for this function.

    Preparation and discretization run in the caller. Native calculations
    use reusable joblib processes, with one Rayon thread per worker. The
    caller's Rayon configuration is unchanged. A single calculation runs
    inline. Use ``n_jobs=1`` when process overhead outweighs useful work.

    See Also
    --------
    nid : Alias for this function.
    h : Entropy density for individual sequences.

    Examples
    --------
    >>> import numpy as np
    >>> import lzsuite as lzs
    >>> data = np.array([[0, 0], [1, 1], [0, 1], [1, 0]] * 32)
    >>> lzs.distance(data, n_jobs=1).shape
    (2, 2)
    >>> lzs.distance(data, data, n_jobs=1).shape
    (2,)
    >>> isinstance(lzs.nid(data[:, 0], data[:, 1]), float)
    True
    """
    first, shape = prepare(data, axis, discretization, discretization_kwargs)
    if other is None:
        encoded = encode_shared(first)
        pairs = [(i, j) for i in range(len(first)) for j in range(i, len(first))]
        tasks = [("nid", (encoded[i], encoded[j]), {}) for i, j in pairs]
        values = calculate_many(tasks, n_jobs)
        output = np.empty((len(first), len(first)), dtype=float)
        for (i, j), value in zip(pairs, values, strict=True):
            output[i, j] = output[j, i] = value
        return output

    second, other_shape = prepare(other, axis, discretization, discretization_kwargs)
    if shape != other_shape:
        raise ValueError(f"Shapes outside the sequence axis must match: {shape} != {other_shape}.")
    encoded = encode_shared(first + second)
    count = len(first)
    tasks = [("nid", (encoded[i], encoded[count + i]), {}) for i in range(count)]
    results = calculate_many(tasks, n_jobs)
    return float(results[0]) if not shape else np.asarray(results, dtype=float).reshape(shape)


nid = distance
