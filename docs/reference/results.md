# Result conventions and validation

Return types, field definitions, validation rules, and finite-sequence parsing
conventions.

## Scalar and array results

1D analysis inputs return ordinary Python values: float h, integer complexity,
a factorization tuple, an E tuple, or a full-result dictionary. Batch dimensions
are never automatically squeezed. Empty batch collections preserve their empty
shape when the observation axis is nonempty.

All-pairs distance always returns a square matrix, even for one 1D input. A pair
of 1D operands returns a float. Two batch operands require exactly matching
shapes outside the sequence axis and return that batch shape.

## Factor count versus boundaries

The count includes completed phrases. Boundaries can also include an unfinished
final copied tail. For `banana`, count is 3 and boundaries are `[0, 1, 2, 3, 7]`.
Clamp ends to the prepared length when displaying pieces. Constant sequences
have count 1 and boundaries `[0, 1, n]`.

Empty sequences are rejected by lzsuite, avoiding the backend's unusual empty
count/boundary convention. A single-symbol observation has h = 0.

## Full-result dictionary

| Key | Meaning |
|---|---|
| `complexity` | Completed LZ76 factor count |
| `h` | Normalized LZ76 entropy-rate estimate |
| `factors` | Boundary positions in the prepared sequence |
| `emc` | Method, fitted value/increments, actual range, raw first contrast |
| `epsilon` | Finite-size diagnostic formula |
| `factors_stddev` | Backend factor-dispersion diagnostic |
| `normal_error`, `poison_error` | Backend algebraic error diagnostics; spelling preserved |
| `extras` | Ratios based on the whole and two half-sequence counts |

The `extras` fields are `rajski_distance`, `redundancy`, `fh_uncertainty`,
`lh_uncertainty`, and `pearson_coefficient`. These field names and formulas are
inherited from the backend. Treat them as diagnostics, not general uncertainty
estimates or replacements for repeated scientific observations.

## Representation and warnings

Supported dtype families are real numeric, boolean, Unicode strings, and byte
strings. Object arrays, complex values, scalar arrays, NaN, and infinity are
rejected. Each string element is a category; UTF-8 characters are not implicitly
split inside a multi-character array element.

Above 256 distinct categories, encoding emits standard `RuntimeWarning` and
continues with codes modulo 256. Some categories merge. This is explicit degraded
behavior, not a wide-alphabet analysis. Default h/E normalization still uses the
original prepared symbol count, minimum two. Distances warn based on the shared
union vocabulary.

## Determinism and units

Identical prepared bytes and settings give deterministic native results. Symbol
encodings can matter to content-seeded shuffle calculations, even when a
one-to-one relabeling preserves ordinary LZ76 factor counts. lzsuite uses
canonical sorted codes for individual-sequence analyses and one first-occurrence
shared codebook for distance collections.

Changing log base changes h/E units. Changing requested bins only changes the
default base if the number of actually observed prepared categories changes.
NID uses factor-count ratios and has no log-base argument. Its diagonal is not
forced to zero.
