"""Extract sequence views and prepare labels without losing axis information."""

from __future__ import annotations

import operator
from collections.abc import Mapping
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ._discretization import Discretization, discretize


def prepare(
    data: ArrayLike,
    axis: int,
    discretization: Discretization,
    discretization_kwargs: Mapping[str, Any] | None,
) -> tuple[list[NDArray], tuple[int, ...]]:
    """Extract sequences and symbolize numeric observations along one axis.

    Parameters
    ----------
    data : array_like
        Real numeric, boolean, Unicode-string, or byte-string array. Each
        position outside ``axis`` identifies one sequence. Floats default
        to per-sequence mean binarization; other supported dtypes are symbols.
    axis : int, default=0
        Axis containing successive observations. Negative axes are accepted.
    discretization : str or callable, optional
        Registered method name or function applied to each numeric sequence.
        Overrides automatic mean binarization. Strings cannot be discretized.
    discretization_kwargs : mapping of str to object, optional
        Keyword arguments passed to the selected discretizer. Custom methods
        receive an input copy and may return a different sequence length.

    Returns
    -------
    sequences : list of numpy.ndarray
        Prepared 1D sequences in C order across the remaining dimensions.
    shape : tuple of int
        Batch dimensions, obtained by removing the sequence axis.

    Raises
    ------
    TypeError
        If the dtype or explicit string discretization is unsupported.
    ValueError
        If an axis is invalid, observations are empty/nonfinite, or
        discretization options have no selected method.

    Notes
    -----
    Extraction may return views for already-discrete data. Custom numeric
    methods receive copies through ``discretize``. Empty collections are
    valid when the observation axis itself is nonempty.
    """
    values = np.asarray(data)
    if values.ndim == 0:
        raise ValueError("Provide an array with at least one dimension.")
    axis = operator.index(axis)
    if not -values.ndim <= axis < values.ndim:
        raise ValueError(
            f"axis {axis} is out of bounds for an array with {values.ndim} dimensions."
        )
    if values.dtype.kind not in "biufUS":
        raise TypeError("Use real numeric, boolean, or string arrays.")
    if values.dtype.kind in "biuf" and not np.isfinite(values).all():
        raise ValueError("Sequences must contain only finite values (no NaN or infinity).")
    if discretization is not None and values.dtype.kind in "US":
        raise TypeError("Discretization requires numeric data; string arrays are already symbols.")
    method = discretization
    if method is None and values.dtype.kind == "f":
        method = "mean"
    if discretization_kwargs and method is None:
        raise ValueError("discretization_kwargs requires a discretization method.")
    moved = np.moveaxis(values, axis, -1)
    batch_shape = moved.shape[:-1]
    if moved.shape[-1] == 0:
        raise ValueError("The sequence axis cannot be empty.")
    rows = moved.reshape((-1, moved.shape[-1]))
    sequences = [
        discretize(row, method, **(discretization_kwargs or {})) if method is not None else row
        for row in rows
    ]
    return sequences, batch_shape


def object_array(results: list[Any], shape: tuple[int, ...]) -> NDArray:
    """Restore batch shape while preserving each structured result as one item.

    Parameters
    ----------
    results : list
        Tuple, list, or dictionary results, in flattened batch order.
    shape : tuple of int
        Desired batch shape; its size must match the result count.

    Returns
    -------
    output : numpy.ndarray of object
        Structured items stored without NumPy expanding their dimensions.

    Raises
    ------
    ValueError
        If shape is incompatible with the number of results.
    """
    output = np.empty(len(results), dtype=object)
    for i, result in enumerate(results):
        output[i] = result
    return output.reshape(shape)
