"""One-dimensional discretizers and their name registry.

Custom methods receive a numeric 1D array and return a 1D array of integer
labels. They may change the length. Functions can be passed directly or
registered by name; registration is local to the current Python process.
"""

from __future__ import annotations

import operator
from collections.abc import Callable
from typing import Any, TypeAlias

import numpy as np
from numpy.typing import ArrayLike, NDArray

Discretizer: TypeAlias = Callable[..., ArrayLike]
Discretization: TypeAlias = str | Discretizer | None
_REGISTRY: dict[str, Discretizer] = {}


def _numeric_1d(data: ArrayLike) -> NDArray:
    values = np.asarray(data)
    if values.ndim != 1:
        raise ValueError("A discretizer needs a one-dimensional array.")
    if values.dtype.kind not in "biuf":
        raise TypeError("Discretization requires real numeric data, not strings or objects.")
    if values.size == 0:
        raise ValueError("Cannot discretize an empty sequence.")
    if not np.isfinite(values).all():
        raise ValueError("Sequences must contain only finite values (no NaN or infinity).")
    return values


def _positive_integer(value: Any, name: str) -> int:
    if isinstance(value, (bool, np.bool_)):
        raise TypeError(f"{name} must be a positive integer.")
    try:
        result = operator.index(value)
    except TypeError as exc:
        raise TypeError(f"{name} must be a positive integer.") from exc
    if result < 1:
        raise ValueError(f"{name} must be positive.")
    return result


def binarize_mean(data: ArrayLike) -> NDArray:
    """Return 1 above the sequence mean and 0 otherwise (including ties)."""
    values = _numeric_1d(data)
    return (values > np.mean(values)).astype(np.uint8)


def binarize_median(data: ArrayLike) -> NDArray:
    """Return 1 above the sequence median and 0 otherwise (including ties)."""
    values = _numeric_1d(data)
    return (values > np.median(values)).astype(np.uint8)


def bin_equal_width(data: ArrayLike, *, n_bins: int = 2) -> NDArray:
    """Bin the sequence's range into equal widths; an internal edge goes right."""
    values = _numeric_1d(data)
    n_bins = _positive_integer(n_bins, "n_bins")
    edges = np.linspace(values.min(), values.max(), n_bins + 1)[1:-1]
    if values.min() == values.max():
        return np.zeros(values.size, dtype=np.int64)
    return np.searchsorted(edges, values, side="right")


def bin_quantile(data: ArrayLike, *, n_bins: int = 2) -> NDArray:
    """Bin at empirical quantiles; repeated edges collapse, and ties go right."""
    values = _numeric_1d(data)
    n_bins = _positive_integer(n_bins, "n_bins")
    if values.min() == values.max():
        return np.zeros(values.size, dtype=np.int64)
    edges = np.unique(np.quantile(values, np.linspace(0, 1, n_bins + 1)[1:-1]))
    return np.searchsorted(edges, values, side="right")


def permutation(data: ArrayLike, *, order: int = 3, delay: int = 1) -> NDArray:
    """Label ordinal patterns in delayed windows, advancing one sample at a time.

    Equal values are ordered by their position in the window (earlier first).
    Pattern labels are lexicographic permutation ranks. Output length is
    ``len(data) - (order - 1) * delay``.
    """
    values = _numeric_1d(data)
    order = _positive_integer(order, "order")
    delay = _positive_integer(delay, "delay")
    # 20! fits signed int64; 21! does not. This concerns label storage, not bytes.
    if order > 20:
        raise ValueError("order must be at most 20 so permutation labels fit int64.")
    span = (order - 1) * delay + 1
    if span > values.size:
        raise ValueError("The sequence is shorter than a permutation window.")
    windows = np.lib.stride_tricks.sliding_window_view(values, span)[:, ::delay]
    ordering = np.argsort(windows, axis=1, kind="stable")
    ranks = np.zeros(ordering.shape[0], dtype=np.int64)
    for i in range(order - 1):
        smaller = np.sum(ordering[:, i + 1 :] < ordering[:, i, None], axis=1)
        ranks = (order - i) * ranks + smaller
    return ranks


def register_discretizer(
    name: str, function: Discretizer | None = None, *, replace: bool = False
) -> Any:
    """Register a callable, directly or as ``@register_discretizer('name')``.

    Existing names cannot be overwritten unless ``replace=True``.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("A discretizer name must be a nonempty string.")

    def register(candidate: Discretizer) -> Discretizer:
        if not callable(candidate):
            raise TypeError("A discretizer must be callable.")
        if name in _REGISTRY and not replace:
            raise ValueError(f"Discretizer {name!r} is already registered.")
        _REGISTRY[name] = candidate
        return candidate

    return register if function is None else register(function)


def available_discretizers() -> tuple[str, ...]:
    """Return registered names in sorted order."""
    return tuple(sorted(_REGISTRY))


def discretize(data: ArrayLike, method: str | Discretizer = "mean", **kwargs: Any) -> NDArray:
    """Apply a named or callable discretizer and validate its output contract.

    The callable receives a copy so it cannot mutate the original observations.
    """
    values = _numeric_1d(data)
    if isinstance(method, str):
        try:
            function = _REGISTRY[method]
        except KeyError as exc:
            raise ValueError(
                f"Unknown discretizer {method!r}; available: {available_discretizers()}"
            ) from exc
    elif callable(method):
        function = method
    else:
        raise TypeError("A discretizer must be a registered name or a callable.")
    labels = np.asarray(function(values.copy(), **kwargs))
    if labels.ndim != 1 or labels.dtype.kind not in "biu":
        raise TypeError("A discretizer must return a one-dimensional array of integer labels.")
    if labels.size == 0:
        raise ValueError("A discretizer returned an empty sequence.")
    return labels


for _name, _function in {
    "mean": binarize_mean,
    "median": binarize_median,
    "bins": bin_equal_width,
    "quantile": bin_quantile,
    "permutation": permutation,
}.items():
    register_discretizer(_name, _function)
