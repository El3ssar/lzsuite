"""Discretization and array-oriented Lempel–Ziv analysis."""

from importlib.metadata import version as _package_version

from ._analysis import complexity, emc, factorization, h, lz76
from ._discretization import available_discretizers, discretize, register_discretizer
from ._distance import distance, nid

__version__ = _package_version("lzsuite")
del _package_version

__all__ = [
    "available_discretizers",
    "complexity",
    "discretize",
    "distance",
    "emc",
    "factorization",
    "h",
    "lz76",
    "nid",
    "register_discretizer",
]
