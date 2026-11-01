import inspect
import os
from contextlib import nullcontext

import pytest

import lzsuite as lzs
from lzsuite import _execution as execution


@pytest.mark.parametrize(
    "function", [lzs.h, lzs.complexity, lzs.factorization, lzs.emc, lzs.lz76, lzs.distance]
)
def test_default_is_four_workers(function):
    assert inspect.signature(function).parameters["n_jobs"].default == 4


@pytest.mark.parametrize(
    "jobs,cpus,count,expected", [(4, 8, 10, 4), (4, 2, 10, 2), (4, 8, 2, 2), (-1, 3, 10, 3)]
)
def test_worker_budget_is_capped(monkeypatch, jobs, cpus, count, expected):
    captured = {}

    def configure(**kwargs):
        captured.update(kwargs)
        return nullcontext()

    def run_serially(tasks):
        return [function(*args, **kwargs) for function, args, kwargs in tasks]

    monkeypatch.setattr(execution, "cpu_count", lambda: cpus)
    monkeypatch.setattr(execution, "parallel_config", configure)
    monkeypatch.setattr(execution, "Parallel", lambda: run_serially)
    tasks = [("h", (bytes([0, 1] * 20),), {})] * count
    assert len(execution.calculate_many(tasks, jobs)) == count
    assert captured["n_jobs"] == expected
    assert captured["inner_max_num_threads"] == 1
    assert captured["initializer"] is execution._initialize_worker


def test_workers_use_one_rayon_thread_without_changing_parent(monkeypatch):
    monkeypatch.setenv("RAYON_NUM_THREADS", "7")
    monkeypatch.setattr(execution, "cpu_count", lambda: 2)
    original_calculate = execution._calculate

    def probe(task):
        return os.getpid(), os.environ["RAYON_NUM_THREADS"], original_calculate(task)

    monkeypatch.setattr(execution, "_calculate", probe)
    tasks = [("h", (bytes([0, 1] * 20),), {})] * 8
    results = execution.calculate_many(tasks, n_jobs=2)
    assert all(pid != os.getpid() and threads == "1" for pid, threads, value in results)
    assert os.environ["RAYON_NUM_THREADS"] == "7"


def test_single_cpu_uses_inline_path_without_changing_rayon(monkeypatch):
    monkeypatch.setattr(execution, "cpu_count", lambda: 1)
    monkeypatch.setenv("RAYON_NUM_THREADS", "7")
    tasks = [("h", (bytes([0, 1] * 20),), {})] * 2
    assert len(execution.calculate_many(tasks, n_jobs=4)) == 2
    assert os.environ["RAYON_NUM_THREADS"] == "7"
