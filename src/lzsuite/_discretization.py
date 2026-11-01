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
    """Validate and expose a nonempty, finite, real numeric sequence.

    Parameters
    ----------
    data : array_like
        Candidate observations; no dtype coercion is forced.

    Returns
    -------
    values : numpy.ndarray
        Validated 1D array, potentially sharing storage with the input.

    Raises
    ------
    TypeError
        If the dtype is not real numeric or boolean.
    ValueError
        If the sequence is empty, nonfinite, or not one-dimensional.
    """
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
    """Validate an integer-valued setting without accepting booleans.

    Parameters
    ----------
    value : object
        Value supporting the integer index protocol.
    name : str
        Parameter name used in error messages.

    Returns
    -------
    result : int
        Positive integer value.

    Raises
    ------
    TypeError
        If value is boolean or does not support the integer index protocol.
    ValueError
        If value is nonpositive.
    """
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
    """Binarize a sequence using its own mean.

    Parameters
    ----------
    data : array_like
        Nonempty, finite, real numeric 1D sequence. Strings, objects,
        complex values, and nonfinite observations are rejected.

    Returns
    -------
    labels : numpy.ndarray of uint8
        Array of the same length, with 1 strictly above the threshold and
        0 at or below it. Constant signals produce only zeros.

    Raises
    ------
    TypeError
        If the input dtype or parameter type is unsupported.
    ValueError
        If the input is empty, nonfinite, not 1D, or a setting is invalid.

    Notes
    -----
    Available publicly through ``discretize(data, method="mean")``.
    The threshold is fitted independently for each sequence in array calls.

    Examples
    --------
    >>> import lzsuite as lzs
    >>> lzs.discretize([0., 1., 2.], method="mean").tolist()
    [0, 0, 1]
    """
    values = _numeric_1d(data)
    return (values > np.mean(values)).astype(np.uint8)


def binarize_median(data: ArrayLike) -> NDArray:
    """Binarize a sequence using its own median.

    Parameters
    ----------
    data : array_like
        Nonempty, finite, real numeric 1D sequence. Strings, objects,
        complex values, and nonfinite observations are rejected.

    Returns
    -------
    labels : numpy.ndarray of uint8
        Array of the same length, with 1 strictly above the threshold and
        0 at or below it. Constant signals produce only zeros.

    Raises
    ------
    TypeError
        If the input dtype or parameter type is unsupported.
    ValueError
        If the input is empty, nonfinite, not 1D, or a setting is invalid.

    Notes
    -----
    Available publicly through ``discretize(data, method="median")``.
    The threshold is fitted independently for each sequence in array calls.

    Examples
    --------
    >>> import lzsuite as lzs
    >>> lzs.discretize([0., 1., 2.], method="median").tolist()
    [0, 0, 1]
    """
    values = _numeric_1d(data)
    return (values > np.median(values)).astype(np.uint8)


def bin_equal_width(data: ArrayLike, *, n_bins: int = 2) -> NDArray:
    """Discretize observations with equally spaced edges over the sequence's range.

    Parameters
    ----------
    data : array_like
        Nonempty, finite, real numeric 1D sequence. Strings, objects,
        complex values, and nonfinite observations are rejected.
    n_bins : int, default=2
        Requested number of bins; must be a positive integer.

    Returns
    -------
    labels : numpy.ndarray of integers
        One label per observation. Values exactly on internal edges enter
        the higher bin. Constant sequences produce only zeros.

    Raises
    ------
    TypeError
        If the input dtype or parameter type is unsupported.
    ValueError
        If the input is empty, nonfinite, not 1D, or a setting is invalid.

    Notes
    -----
    Available through ``discretize(data, method="bins")``. Edges are
    fitted separately to each sequence; use a custom callable for fixed edges.

    Examples
    --------
    >>> import lzsuite as lzs
    >>> lzs.discretize([0., 1., 2., 3., 4.], method="bins", n_bins=2).tolist()
    [0, 0, 1, 1, 1]
    """
    values = _numeric_1d(data)
    n_bins = _positive_integer(n_bins, "n_bins")
    edges = np.linspace(values.min(), values.max(), n_bins + 1)[1:-1]
    if values.min() == values.max():
        return np.zeros(values.size, dtype=np.int64)
    return np.searchsorted(edges, values, side="right")


def bin_quantile(data: ArrayLike, *, n_bins: int = 2) -> NDArray:
    """Discretize observations with empirical quantile edges.

    Parameters
    ----------
    data : array_like
        Nonempty, finite, real numeric 1D sequence. Strings, objects,
        complex values, and nonfinite observations are rejected.
    n_bins : int, default=2
        Requested number of bins; must be a positive integer.

    Returns
    -------
    labels : numpy.ndarray of integers
        One label per observation. Values exactly on internal edges enter
        the higher bin. Constant sequences produce only zeros.

    Raises
    ------
    TypeError
        If the input dtype or parameter type is unsupported.
    ValueError
        If the input is empty, nonfinite, not 1D, or a setting is invalid.

    Notes
    -----
    Repeated quantile edges collapse, so requested bin counts and occupied
    bin counts can differ. Quantiles use NumPy's default linear interpolation.
    Available through ``discretize(data, method="quantile")``. Edges are
    fitted separately to each sequence; use a custom callable for fixed edges.

    Examples
    --------
    >>> import lzsuite as lzs
    >>> lzs.discretize([0., 1., 2., 3., 4.], method="quantile", n_bins=2).tolist()
    [0, 0, 1, 1, 1]
    """
    values = _numeric_1d(data)
    n_bins = _positive_integer(n_bins, "n_bins")
    if values.min() == values.max():
        return np.zeros(values.size, dtype=np.int64)
    edges = np.unique(np.quantile(values, np.linspace(0, 1, n_bins + 1)[1:-1]))
    return np.searchsorted(edges, values, side="right")


def permutation(data: ArrayLike, *, order: int = 3, delay: int = 1) -> NDArray:
    """Encode delayed ordinal windows as lexicographic permutation ranks.

    Parameters
    ----------
    data : array_like
        Nonempty, finite, real numeric 1D sequence. Strings, objects,
        complex values, and nonfinite observations are rejected.
    order : int, default=3
        Number of observations per ordinal pattern, between 1 and 20. The
        upper bound ensures permutation ranks fit signed 64-bit integers.
    delay : int, default=1
        Positive spacing between observations within each window.

    Returns
    -------
    labels : numpy.ndarray of int64
        Lexicographic ranks, of length ``len(data) - (order - 1) * delay``.
        Successive windows advance by one original observation.

    Raises
    ------
    TypeError
        If the input dtype or parameter type is unsupported.
    ValueError
        If the input is empty, nonfinite, not 1D, or a setting is invalid.

    Notes
    -----
    Equal values are ordered by their positions in the window, earlier
    first. This method creates a symbolic sequence; it does not compute
    permutation entropy. A window must fit within the supplied sequence.
    The backend's byte-alphabet warning is applied during analysis, not
    here: for example order 6 admits 720 possible patterns.

    Examples
    --------
    >>> import lzsuite as lzs
    >>> lzs.discretize([3., 1., 2., 4., 0.], "permutation", order=3).tolist()
    [3, 0, 4]
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
    """Register a named discretizer directly or as a decorator.

    Parameters
    ----------
    name : str
        Nonempty registry label, used as ``discretization=name`` in analysis
        calls or ``method=name`` in ``discretize``.
    function : callable, optional
        Numeric 1D-to-integer-1D function. Omit to obtain a decorator.
        Its output may differ in length from its input.
    replace : bool, default=False
        Allow replacing an existing label, including a built-in method.

    Returns
    -------
    registered : callable
        The supplied function unchanged, or a decorator if no function was
        supplied. Registration lasts for the current Python process only.

    Raises
    ------
    TypeError
        If the supplied function is not callable.
    ValueError
        If the name is empty or already exists without ``replace=True``.

    Notes
    -----
    The callable's input/output contract is checked when it is used.
    Array preparation invokes it in the parent process before parallel
    native calculations, so locally defined functions work in IPython.

    See Also
    --------
    discretize : Invoke a registered name or a callable.
    available_discretizers : Inspect current names.

    Examples
    --------
    >>> import lzsuite as lzs
    >>> @lzs.register_discretizer("positive", replace=True)
    ... def positive(values):
    ...     return (values > 0).astype(int)
    >>> lzs.discretize([-1., 0., 2.], "positive").tolist()
    [0, 0, 1]
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("A discretizer name must be a nonempty string.")

    def register(candidate: Discretizer) -> Discretizer:
        """Store a callable under the validated registry name.

        Parameters
        ----------
        candidate : callable
            Function to register for the lifetime of this Python process.

        Returns
        -------
        candidate : callable
            The original function, preserving decorator behavior.

        Raises
        ------
        TypeError
            If candidate is not callable.
        ValueError
            If the label exists and replacement was not enabled.
        """
        if not callable(candidate):
            raise TypeError("A discretizer must be callable.")
        if name in _REGISTRY and not replace:
            raise ValueError(f"Discretizer {name!r} is already registered.")
        _REGISTRY[name] = candidate
        return candidate

    return register if function is None else register(function)


def available_discretizers() -> tuple[str, ...]:
    """List the registered discretization names in sorted order.

    Returns
    -------
    names : tuple of str
        Built-in and user-registered labels available in this Python process.

    See Also
    --------
    register_discretizer : Add or replace a named method.
    discretize : Run a method on a 1D signal.

    Examples
    --------
    >>> import lzsuite as lzs
    >>> "mean" in lzs.available_discretizers()
    True
    """
    return tuple(sorted(_REGISTRY))


def discretize(data: ArrayLike, method: str | Discretizer = "mean", **kwargs: Any) -> NDArray:
    """Apply a registered or callable discretizer to one numeric sequence.

    Parameters
    ----------
    data : array_like
        Nonempty, finite, real numeric 1D sequence. Strings, objects,
        complex values, and nonfinite observations are rejected.
    method : str or callable, default='mean'
        Registered label or function. Built-ins are ``mean``, ``median``,
        ``bins``, ``quantile``, and ``permutation``. A custom callable receives
        a copy of the numeric input and may change the output length.
    **kwargs : dict
        Keyword arguments forwarded to the selected method, such as
        ``n_bins``, ``order``, ``delay``, or a custom threshold.

    Returns
    -------
    labels : numpy.ndarray of integers
        Nonempty 1D integer or boolean labels. Original observations are
        not mutated by the method; its input is copied before invocation.

    Raises
    ------
    TypeError
        If input is not real numeric data, method is not a name/callable,
        or the method returns noninteger or multidimensional output.
    ValueError
        If input is empty, nonfinite, or not 1D, the method name is unknown,
        or its output is empty. Method-specific validation also applies.

    Notes
    -----
    There is no 256-category restriction at this stage. Analysis functions
    warn and merge categories if the prepared alphabet exceeds 256 symbols.
    Numeric labels do not need to be contiguous or start at zero.

    See Also
    --------
    available_discretizers : List registered labels.
    register_discretizer : Add a reusable custom method.
    h : Apply a method independently across an array.

    Examples
    --------
    >>> import lzsuite as lzs
    >>> lzs.discretize([0., 1., 9.], "mean").tolist()
    [0, 0, 1]
    >>> lzs.discretize([0., 1., 2., 3.], "bins", n_bins=2).tolist()
    [0, 0, 1, 1]
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
