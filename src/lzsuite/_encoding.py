"""Map labels to bytes; distances share a codebook across both operands."""

from __future__ import annotations

import warnings

import numpy as np
from numpy.typing import NDArray


def _warn_large(size: int) -> None:
    """Warn when category codes cannot fit the backend byte alphabet.

    Parameters
    ----------
    size : int
        Number of distinct categories before any modulo mapping.

    Warns
    -----
    RuntimeWarning
        If size exceeds 256. Calling code continues with merged categories.
    """
    if size > 256:
        warnings.warn(
            f"Found {size} distinct symbols; lzcomplexity supports 256. "
            "Labels are mapped modulo 256, merging different symbols. "
            "Results do not faithfully describe the original alphabet.",
            RuntimeWarning,
            stacklevel=4,
        )


def encode(sequence: NDArray) -> tuple[bytes, int]:
    """Encode a sequence with sorted category codes and report its log base.

    Parameters
    ----------
    sequence : numpy.ndarray
        Validated 1D sequence of supported discrete labels.

    Returns
    -------
    symbols : bytes
        One byte per observation; codes wrap modulo 256 if needed.
    base : int
        Original distinct-symbol count, floored at 2.

    Warns
    -----
    RuntimeWarning
        If the original vocabulary exceeds 256 categories.

    Notes
    -----
    A one-to-one relabeling preserves the LZ76 equality structure. Shuffle
    seeds also depend on byte labels, so canonical sorted codes provide
    consistent encoding for equivalent category vocabularies.
    """
    vocabulary, labels = np.unique(sequence, return_inverse=True)
    size = vocabulary.size
    _warn_large(size)
    return (labels % 256).astype(np.uint8).tobytes(), max(2, size)


def encode_shared(sequences: list[NDArray]) -> list[bytes]:
    """Encode a collection with one codebook preserving shared category meanings.

    Parameters
    ----------
    sequences : list of numpy.ndarray
        Supported 1D symbolic sequences, including both distance operands.

    Returns
    -------
    encoded : list of bytes
        Sequences encoded in input order, with shared codes assigned in
        first-occurrence order. An empty collection yields an empty list.

    Raises
    ------
    TypeError
        If numeric and string categories are mixed, or byte and Unicode
        string representations differ between sequences.

    Warns
    -----
    RuntimeWarning
        Once if the union vocabulary exceeds 256 categories.

    Notes
    -----
    Python scalar keys avoid float promotion that could merge large signed
    and unsigned integers. Alphabet overflow deliberately wraps codes modulo
    256; such results no longer preserve all original distinctions.
    """
    if not sequences:
        return []
    # Mixing numbers with text would silently turn numbers into strings and can
    # make distinct categories identical. Require the same family instead.
    kinds = {"text" if seq.dtype.kind in "US" else "number" for seq in sequences}
    if len(kinds) != 1:
        raise TypeError("Both distance inputs must use the same symbol type: numbers or strings.")
    text_kinds = {seq.dtype.kind for seq in sequences if seq.dtype.kind in "US"}
    if len(text_kinds) > 1:
        raise TypeError("Use the same string representation (Unicode or bytes) in both inputs.")
    # Build keys as Python scalars rather than concatenating arrays: promoting
    # mixed int64/uint64 inputs to float64 would lose distinct large integers.
    vocabulary: dict[object, int] = {}
    encoded = []
    for sequence in sequences:
        labels = []
        for symbol in sequence.tolist():
            if symbol not in vocabulary:
                vocabulary[symbol] = len(vocabulary)
            labels.append(vocabulary[symbol] % 256)
        encoded.append(bytes(labels))
    _warn_large(len(vocabulary))
    return encoded
