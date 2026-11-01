"""Execute prepared byte calculations serially or in separate processes."""

from __future__ import annotations

import operator
import os
from typing import Any

import numpy as np
from joblib import Parallel, cpu_count, delayed, parallel_config


def _initialize_worker() -> None:
    # Each worker owns a separate native pool. Keep the total CPU budget at
    # n_jobs instead of starting a full Rayon pool in every process.
    """Limit each child process to one native Rayon worker thread.

    Notes
    -----
    Runs before the child's first native calculation. Only the child process
    environment is modified; the caller's Rayon configuration is preserved.
    """
    os.environ["RAYON_NUM_THREADS"] = "1"


def _calculate(task: tuple[str, tuple[bytes, ...], dict[str, Any]]) -> Any:
    """Run one prepared byte-sequence task using the native backend.

    Parameters
    ----------
    task : tuple
        ``(operation, sequence_bytes_tuple, keyword_options)``. Complexity
        selects only the factor count from the native factorization result.

    Returns
    -------
    result : object
        Native scalar, tuple, list, or dictionary for the selected operation.

    Notes
    -----
    The extension is imported lazily after worker initialization, ensuring
    its Rayon pool sees the worker-specific environment.
    """
    import lzcomplexity as lz

    operation, sequences, kwargs = task
    if operation == "complexity":
        return lz.factorization(sequences[0], **kwargs)[0]
    return getattr(lz, operation)(*sequences, **kwargs)


def calculate_many(
    tasks: list[tuple[str, tuple[bytes, ...], dict[str, Any]]], n_jobs: int
) -> list[Any]:
    """Execute prepared native tasks inline or in bounded reusable processes.

    Parameters
    ----------
    tasks : list of tuple
        Tasks accepted by ``_calculate``, in desired output order.
    n_jobs : int
        Maximum worker count, or -1 for available CPUs. Booleans and other
        nonpositive integers are rejected.

    Returns
    -------
    results : list
        Task results in input order. An empty task collection yields [].

    Raises
    ------
    TypeError
        If n_jobs is boolean or does not support integer indexing.
    ValueError
        If n_jobs is nonpositive and not -1. Task exceptions propagate too.

    Notes
    -----
    The actual pool size is capped by available CPUs and task count. Zero
    or one worker uses the inline path. Loky supports scripts, IPython and
    notebooks and reuses processes across calls. Each process has one Rayon
    thread and one thread for other managed native pools; the parent is
    not reconfigured. Preparation and discretization are not done here.
    """
    if isinstance(n_jobs, (bool, np.bool_)):
        raise TypeError("n_jobs must be a positive integer or -1 for available CPUs.")
    n_jobs = operator.index(n_jobs)
    if n_jobs != -1 and n_jobs < 1:
        raise ValueError("n_jobs must be a positive integer or -1 for available CPUs.")
    available = cpu_count()
    workers = min(available if n_jobs == -1 else n_jobs, available, len(tasks))
    if workers < 2:
        return [_calculate(task) for task in tasks]
    # Loky supports interactive sessions and reuses workers across calls.
    # Initializers run in children only, before the first backend import.
    with parallel_config(
        backend="loky",
        n_jobs=workers,
        inner_max_num_threads=1,
        initializer=_initialize_worker,
    ):
        return Parallel()(delayed(_calculate)(task) for task in tasks)
