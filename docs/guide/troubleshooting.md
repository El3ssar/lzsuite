# Troubleshooting

## Import or environment problems

Use the same interpreter for installation and execution:

```sh
python -m pip show lzsuite lzcomplexity numpy joblib
python -c "import sys, lzsuite; print(sys.executable, lzsuite.__version__)"
```

In a checkout, prefer `uv sync --locked` and `uv run ipython`. After source edits,
restart an existing REPL to clear already-imported objects. A normal PyPI install
contains the docstrings from that released version; the live docs may include
later documentation improvements from `main`.

## “My result has the wrong shape”

Check `axis`. For `(n, channels, trials)`, `axis=0` returns `(channels, trials)`.
A 1D input returns native values; `(n, 1)` retains a `(1,)` result. All-pairs
distance deliberately returns a square matrix instead of the batch shape.

## “My integer labels are larger than 255”

Their original magnitudes are fine if no more than 256 distinct categories are
present. lzsuite maps categories to byte codes. Above 256 distinct categories it
warns and merges labels modulo 256; those results no longer preserve the full
alphabet. The warning considers the union vocabulary for distances.

## “My float categories got binarized”

Float arrays default to mean thresholding. If values are categorical, explicitly
map them to integer labels first. For continuous signals, select an appropriate
method through `discretization`. A string array is already symbolic and cannot
be passed to a numeric discretizer.

## “My custom discretizer is rejected”

Return a nonempty 1D integer or boolean array. Float-valued labels are rejected,
even when numerically integral. Changing length is allowed, but returning a
matrix or empty array is not. Check that method parameters are accepted as
keyword arguments and that a registry label has been registered in this session.

## “h is above one”

This can happen for finite sequences. Values are not clipped. Check the encoding,
normalization base, and sequence length, then assess stability with more data.

## “E changes when I increase the cap”

A positive cap includes the full requested raw profile before fitting. Automatic
Chao–Shen mode instead stops at the earliest raw maximum within its ceiling.
Changing the cap changes the estimator; it does not only append fixed increments.

## “The diagonal is not zero”

That is allowed by the finite-sequence NID convention. lzsuite retains actual
self-distances. Transform a copied matrix explicitly if a downstream method
requires a zero diagonal, and record the transformation.

## “More processes did not help”

Startup, copying, preparation, and memory contention can outweigh native work.
Compare `n_jobs=1`, `2`, and `4` on representative inputs and distinguish first-call
startup from warmed repeated calls. Preparation is serial; each worker has one
Rayon thread. Measure the runtime on representative inputs before increasing
the process count.

## Reporting a reproducible problem

Open a [GitHub issue](https://github.com/El3ssar/lzsuite/issues) with a small input,
its dtype/shape, call and settings, expected/actual behavior, package versions,
Python/platform, and `n_jobs`. Include preprocessing choices when they affect
meaning. Share synthetic data instead of confidential observations where possible.
