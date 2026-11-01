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
    """Calculate NID with one shared symbol encoding.

    With one input, return an M×M matrix for all M sequences. Sequence order
    is C order on the input shape after removing ``axis``. Compute and retain
    actual self-distances on the diagonal.

    With two inputs, compare corresponding sequences and return an array
    shaped like the input with ``axis`` removed. Shapes outside that axis
    must match exactly; sequence lengths may differ, including after
    discretization. No broadcasting is performed.
    A pair of 1D inputs returns a Python float. A single 1D input still returns
    a 1×1 all-pairs matrix.

    Float inputs default to per-sequence mean binarization. An explicit
    discretizer is applied separately to every sequence in both arrays.
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
