"""Discretization and array-oriented Lempel–Ziv analysis."""

from importlib.metadata import version

from . import discretization
from ._encoding import AlphabetSizeWarning
from .analysis import complexity, emc, factorization, h, lz76
from .discretization import available_discretizers, discretize, register_discretizer
from .distance import distance, nid

__version__ = version("lzsuite")

__all__ = [
    "AlphabetSizeWarning",
    "available_discretizers",
    "complexity",
    "discretization",
    "discretize",
    "distance",
    "emc",
    "factorization",
    "h",
    "lz76",
    "nid",
    "register_discretizer",
]
