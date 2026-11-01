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
    os.environ["RAYON_NUM_THREADS"] = "1"


def _calculate(task: tuple[str, tuple[bytes, ...], dict[str, Any]]) -> Any:
    import lzcomplexity as lz

    operation, sequences, kwargs = task
    if operation == "complexity":
        return lz.factorization(sequences[0], **kwargs)[0]
    return getattr(lz, operation)(*sequences, **kwargs)


def calculate_many(
    tasks: list[tuple[str, tuple[bytes, ...], dict[str, Any]]], n_jobs: int
) -> list[Any]:
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
