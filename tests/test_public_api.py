"""Check the actual namespace and interactive completion, not just __all__."""

import rlcompleter

import lzsuite as lzs

PUBLIC_FUNCTIONS = {
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
}


def test_public_namespace_contains_only_user_functions():
    assert {name for name in vars(lzs) if not name.startswith("_")} == PUBLIC_FUNCTIONS
    assert set(lzs.__all__) == PUBLIC_FUNCTIONS
    assert all(callable(getattr(lzs, name)) for name in PUBLIC_FUNCTIONS)
    assert isinstance(lzs.__version__, str)


def test_tab_completion_contains_only_user_functions():
    completer = rlcompleter.Completer({"lzs": lzs})
    matches = set()
    index = 0
    while (match := completer.complete("lzs.", index)) is not None:
        matches.add(match.removeprefix("lzs.").rstrip("()"))
        index += 1
    assert matches == PUBLIC_FUNCTIONS
