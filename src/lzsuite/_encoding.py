"""Map labels to bytes; distances share a codebook across both operands."""

from __future__ import annotations

import warnings

import numpy as np
from numpy.typing import NDArray


def _warn_large(size: int) -> None:
    if size > 256:
        warnings.warn(
            f"Found {size} distinct symbols; lzcomplexity supports 256. "
            "Labels are mapped modulo 256, merging different symbols. "
            "Results do not faithfully describe the original alphabet.",
            RuntimeWarning,
            stacklevel=4,
        )


def encode(sequence: NDArray) -> tuple[bytes, int]:
    vocabulary, labels = np.unique(sequence, return_inverse=True)
    size = vocabulary.size
    _warn_large(size)
    return (labels % 256).astype(np.uint8).tobytes(), max(2, size)


def encode_shared(sequences: list[NDArray]) -> list[bytes]:
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
