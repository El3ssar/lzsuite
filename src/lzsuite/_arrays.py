"""Extract sequence views and prepare labels without losing axis information."""

from __future__ import annotations

import operator
from collections.abc import Mapping
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .discretization import Discretization, discretize


def prepare(
    data: ArrayLike,
    axis: int,
    discretization: Discretization,
    discretization_kwargs: Mapping[str, Any] | None,
) -> tuple[list[NDArray], tuple[int, ...]]:
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
    """Keep each tuple/list/dict as one entry instead of expanding its dimensions."""
    output = np.empty(len(results), dtype=object)
    for i, result in enumerate(results):
        output[i] = result
    return output.reshape(shape)
