"""Execute prepared byte calculations serially or in separate processes."""

from __future__ import annotations

import multiprocessing
import operator
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Any


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
    if isinstance(n_jobs, bool):
        raise TypeError("n_jobs must be a positive integer or -1 for available CPUs.")
    n_jobs = operator.index(n_jobs)
    if n_jobs == -1:
        n_jobs = os.cpu_count() or 1
    if n_jobs < 1:
        raise ValueError("n_jobs must be a positive integer or -1 for available CPUs.")
    if n_jobs == 1 or len(tasks) < 2:
        return [_calculate(task) for task in tasks]
    with ProcessPoolExecutor(
        max_workers=min(n_jobs, len(tasks)),
        mp_context=multiprocessing.get_context("spawn"),
        initializer=_initialize_worker,
    ) as pool:
        return list(pool.map(_calculate, tasks, chunksize=max(1, len(tasks) // (n_jobs * 4))))
