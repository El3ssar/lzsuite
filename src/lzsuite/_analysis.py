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
    """Prepare sequences and dispatch one native analysis task per sequence.

    Parameters
    ----------
    data : array_like
        Supported input observations or categorical labels.
    operation : str
        Backend operation name, or ``complexity`` for the factor count.
    axis : int
        Sequence axis in the input array.
    discretization : str or callable or None
        Numeric symbolization method; None selects dtype-dependent defaults.
    discretization_kwargs : mapping or None
        Options for the selected discretizer.
    n_jobs : int
        Process budget, or -1 for available CPUs.
    log_base : int, optional
        Explicit normalization base; None uses the prepared symbol count.
    **kwargs : dict
        Additional keyword arguments for the native operation.

    Returns
    -------
    results : list
        Native results in C order over the batch dimensions.
    shape : tuple of int
        Input dimensions after removing the sequence axis.

    Raises
    ------
    TypeError
        If parameter types or input values are unsupported.
    ValueError
        If the base, axis, sequence, or discretization settings are invalid.
    """
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
    n_jobs: int = 4,
    log_base: int | None = None,
) -> float | NDArray:
    """Estimate normalized LZ76 entropy density along an array axis.

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
    n_jobs : int, default=4
        Maximum worker processes, capped by available CPUs and calculation
        count. Use 1 for inline execution or -1 for all available CPUs.
    log_base : int, optional
        Logarithm base, at least 2. Defaults to the distinct-symbol count in
        each prepared sequence, with a minimum of 2 for constant data.

    Returns
    -------
    entropy : float or numpy.ndarray
        Python float for a 1D input; otherwise a float array with ``axis``
        removed. Singleton batch dimensions are preserved.

    Raises
    ------
    TypeError
        If the dtype, discretizer output, or parameter type is unsupported.
    ValueError
        If the sequence axis is empty, values are nonfinite, the axis or
        settings are invalid, or a custom discretizer returns no labels.

    Warns
    -----
    RuntimeWarning
        If more than 256 categories must be reduced to the byte alphabet.
        Categories then merge and results no longer faithfully represent
        the original alphabet.

    Notes
    -----
    For factor count C and prepared length n, h = C * log_b(n) / n.
    This is a finite-sequence entropy-rate estimate, not a symbol-histogram
    entropy. Finite-sample estimates can exceed 1; values are not clipped.
    Compare matched lengths, symbolizations, and logarithm units.

    Preparation and discretization run in the caller. Native calculations
    use reusable joblib processes, with one Rayon thread per worker. The
    caller's Rayon configuration is unchanged. A single calculation runs
    inline. Use ``n_jobs=1`` when process overhead outweighs useful work.

    See Also
    --------
    complexity : Unnormalized LZ76 factor count.
    emc : Effective measure complexity and scale increments.
    lz76 : Complete analysis dictionary.

    Examples
    --------
    >>> import numpy as np
    >>> import lzsuite as lzs
    >>> lzs.h([0, 1, 0, 1, 0, 1, 0, 1])
    0.75
    >>> recordings = np.tile([0, 1], (128, 1))
    >>> lzs.h(recordings, n_jobs=1).shape
    (2,)
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
    return float(results[0]) if not shape else np.asarray(results, dtype=float).reshape(shape)


def complexity(
    data: ArrayLike,
    *,
    axis: int = 0,
    discretization: Discretization = None,
    discretization_kwargs: Mapping[str, Any] | None = None,
    n_jobs: int = 4,
) -> int | NDArray:
    """Count completed LZ76 phrases along an array axis.

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
    n_jobs : int, default=4
        Maximum worker processes, capped by available CPUs and calculation
        count. Use 1 for inline execution or -1 for all available CPUs.

    Returns
    -------
    counts : int or numpy.ndarray
        Python int for a 1D input; otherwise an integer array with ``axis``
        removed. Counts follow the backend's completed-phrase convention.

    Raises
    ------
    TypeError
        If the dtype, discretizer output, or parameter type is unsupported.
    ValueError
        If the sequence axis is empty, values are nonfinite, the axis or
        settings are invalid, or a custom discretizer returns no labels.

    Warns
    -----
    RuntimeWarning
        If more than 256 categories must be reduced to the byte alphabet.
        Categories then merge and results no longer faithfully represent
        the original alphabet.

    Notes
    -----
    Constant sequences have count 1. A final copied tail can appear in
    factor boundaries without adding to the count. Raw counts depend on
    sequence length and encoding; ``h`` provides entropy-rate normalization.

    Preparation and discretization run in the caller. Native calculations
    use reusable joblib processes, with one Rayon thread per worker. The
    caller's Rayon configuration is unchanged. A single calculation runs
    inline. Use ``n_jobs=1`` when process overhead outweighs useful work.

    See Also
    --------
    factorization : Factor count and boundary positions.
    h : Normalized entropy density.

    Examples
    --------
    >>> import numpy as np
    >>> import lzsuite as lzs
    >>> lzs.complexity(np.array(list("banana")))
    3
    >>> lzs.complexity(np.ones((32, 2), dtype=int), n_jobs=1).tolist()
    [1, 1]
    """
    results, shape = _analyze(
        data,
        "complexity",
        axis=axis,
        discretization=discretization,
        discretization_kwargs=discretization_kwargs,
        n_jobs=n_jobs,
    )
    return int(results[0]) if not shape else np.asarray(results, dtype=np.int64).reshape(shape)


def factorization(
    data: ArrayLike,
    *,
    axis: int = 0,
    discretization: Discretization = None,
    discretization_kwargs: Mapping[str, Any] | None = None,
    n_jobs: int = 4,
) -> tuple[int, list[int]] | NDArray:
    """Return LZ76 factor counts and phrase boundaries.

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
    n_jobs : int, default=4
        Maximum worker processes, capped by available CPUs and calculation
        count. Use 1 for inline execution or -1 for all available CPUs.

    Returns
    -------
    result : tuple of (int, list of int) or numpy.ndarray
        For 1D input, ``(count, boundaries)`` directly. For higher-dimensional
        input, an object array of those tuples, with ``axis`` removed.

    Raises
    ------
    TypeError
        If the dtype, discretizer output, or parameter type is unsupported.
    ValueError
        If the sequence axis is empty, values are nonfinite, the axis or
        settings are invalid, or a custom discretizer returns no labels.

    Warns
    -----
    RuntimeWarning
        If more than 256 categories must be reduced to the byte alphabet.
        Categories then merge and results no longer faithfully represent
        the original alphabet.

    Notes
    -----
    Boundaries index the prepared symbolic sequence, whose length may
    change during discretization. The final attempted phrase boundary can
    extend beyond the input. A copied tail does not contribute to the
    completed-factor count, so count need not equal len(boundaries) - 1.
    Clamp end positions to sequence length when displaying visible phrases.

    Preparation and discretization run in the caller. Native calculations
    use reusable joblib processes, with one Rayon thread per worker. The
    caller's Rayon configuration is unchanged. A single calculation runs
    inline. Use ``n_jobs=1`` when process overhead outweighs useful work.

    See Also
    --------
    complexity : Return only the factor count.
    lz76 : Factorization and all other measures.

    Examples
    --------
    >>> import numpy as np
    >>> import lzsuite as lzs
    >>> count, boundaries = lzs.factorization(np.array(list("banana")))
    >>> count, boundaries
    (3, [0, 1, 2, 3, 7])
    """
    results, shape = _analyze(
        data,
        "factorization",
        axis=axis,
        discretization=discretization,
        discretization_kwargs=discretization_kwargs,
        n_jobs=n_jobs,
    )
    return results[0] if not shape else object_array(results, shape)


def emc(
    data: ArrayLike,
    *,
    axis: int = 0,
    discretization: Discretization = None,
    discretization_kwargs: Mapping[str, Any] | None = None,
    n_jobs: int = 4,
    log_base: int | None = None,
    max_block_size: int = -1,
    method: str = "chao-shen",
) -> tuple[float, list[float]] | tuple[NDArray, NDArray]:
    """Estimate effective measure complexity E and its scale increments.

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
    n_jobs : int, default=4
        Maximum worker processes, capped by available CPUs and calculation
        count. Use 1 for inline execution or -1 for all available CPUs.
    log_base : int, optional
        Logarithm base, at least 2. Defaults to the distinct-symbol count in
        each prepared sequence, with a minimum of 2 for constant data.
    max_block_size : int, default=-1
        Maximum byte-window range for E. Nonpositive values select the
        backend's automatic range; a positive value keeps that full range.
    method : {'chao-shen', 'shuffle'}, default='chao-shen'
        E estimator. This option is independent of ``discretization``.

    Returns
    -------
    scores : float or numpy.ndarray
        Python float for 1D input; otherwise a float array with ``axis``
        removed. E is the final level of the fitted scale profile.
    profiles : list of float or numpy.ndarray
        For 1D input, a list of nonnegative increments summing to E. Otherwise
        an object array of lists with the same shape as ``scores``. Profile
        lengths can differ when the range is selected automatically.

    Raises
    ------
    TypeError
        If the dtype, discretizer output, or parameter type is unsupported.
    ValueError
        If the sequence axis is empty, values are nonfinite, the axis or
        settings are invalid, or a custom discretizer returns no labels.

    Warns
    -----
    RuntimeWarning
        If more than 256 categories must be reduced to the byte alphabet.
        Categories then merge and results no longer faithfully represent
        the original alphabet.

    Notes
    -----
    Chao-Shen estimates block entropy from overlapping windows, subtracts
    l times the LZ76 rate estimate, then fits a nonnegative, nondecreasing
    profile. Automatic range selection uses the observed alphabet and stops
    at the earliest raw-profile maximum. A positive cap includes the whole
    requested range. Shuffle uses deterministic block-swapped surrogates
    and a different raw-profile formula. The estimators are not interchangeable.
    Keep encoding, length, base, method, and range consistent across comparisons.

    Preparation and discretization run in the caller. Native calculations
    use reusable joblib processes, with one Rayon thread per worker. The
    caller's Rayon configuration is unchanged. A single calculation runs
    inline. Use ``n_jobs=1`` when process overhead outweighs useful work.

    See Also
    --------
    h : LZ76 entropy-rate estimate.
    lz76 : Includes the actual range and E-method metadata.

    Examples
    --------
    >>> import lzsuite as lzs
    >>> periodic = [0, 0, 0, 1, 0, 1, 1, 1] * 256
    >>> score, increments = lzs.emc(periodic, max_block_size=6)
    >>> score >= 0 and abs(sum(increments) - score) < 1e-12
    True
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
    if not shape:
        return results[0]
    scores = np.asarray([result[0] for result in results], dtype=float).reshape(shape)
    return scores, object_array([result[1] for result in results], shape)


def lz76(
    data: ArrayLike,
    *,
    axis: int = 0,
    discretization: Discretization = None,
    discretization_kwargs: Mapping[str, Any] | None = None,
    n_jobs: int = 4,
    log_base: int | None = None,
    max_block_size: int = -1,
    method: str = "chao-shen",
) -> dict[str, Any] | NDArray:
    """Calculate the complete LZ76 analysis for each sequence.

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
    n_jobs : int, default=4
        Maximum worker processes, capped by available CPUs and calculation
        count. Use 1 for inline execution or -1 for all available CPUs.
    log_base : int, optional
        Logarithm base, at least 2. Defaults to the distinct-symbol count in
        each prepared sequence, with a minimum of 2 for constant data.
    max_block_size : int, default=-1
        Maximum byte-window range for E. Nonpositive values select the
        backend's automatic range; a positive value keeps that full range.
    method : {'chao-shen', 'shuffle'}, default='chao-shen'
        E estimator. This option is independent of ``discretization``.

    Returns
    -------
    result : dict or numpy.ndarray
        Dictionary for 1D input; otherwise an object array of dictionaries,
        with ``axis`` removed. Keys are ``complexity``, ``h``, ``factors``,
        ``emc``, ``epsilon``, ``factors_stddev``, ``normal_error``,
        ``poison_error``, and ``extras``. The ``emc`` dictionary records
        ``method``, ``value``, ``summands``, ``max_block_size``, and
        ``multi_information``. Backend field names are preserved.

    Raises
    ------
    TypeError
        If the dtype, discretizer output, or parameter type is unsupported.
    ValueError
        If the sequence axis is empty, values are nonfinite, the axis or
        settings are invalid, or a custom discretizer returns no labels.

    Warns
    -----
    RuntimeWarning
        If more than 256 categories must be reduced to the byte alphabet.
        Categories then merge and results no longer faithfully represent
        the original alphabet.

    Notes
    -----
    The backend reuses the whole-sequence factorization for several
    measures and also analyzes two halves for the extras. Diagnostic fields
    are algebraic formulas, not general confidence intervals. Estimate
    sampling uncertainty from suitable repeated observations or resampling.
    Use targeted functions when you only need one measure.

    Preparation and discretization run in the caller. Native calculations
    use reusable joblib processes, with one Rayon thread per worker. The
    caller's Rayon configuration is unchanged. A single calculation runs
    inline. Use ``n_jobs=1`` when process overhead outweighs useful work.

    See Also
    --------
    h : Entropy density only.
    complexity : Factor count only.
    emc : E and its increments only.

    Examples
    --------
    >>> import lzsuite as lzs
    >>> result = lzs.lz76([0, 1] * 128, max_block_size=4)
    >>> result["complexity"] == lzs.complexity([0, 1] * 128)
    True
    >>> result["emc"]["method"]
    'chao-shen'
    """
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
    return results[0] if not shape else object_array(results, shape)
