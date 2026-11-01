# Built-in discretizers

Select these methods with `lzs.discretize(data, method="...")` or the
`discretization` argument of an analysis function. Method options are passed
directly to `discretize`, or through `discretization_kwargs` in array calls.

## Mean (`mean`)

::: lzsuite._discretization.binarize_mean
    options:
      show_root_heading: false
      show_signature: false

## Median (`median`)

::: lzsuite._discretization.binarize_median
    options:
      show_root_heading: false
      show_signature: false

## Equal-width bins (`bins`)

::: lzsuite._discretization.bin_equal_width
    options:
      show_root_heading: false
      show_signature: false

## Quantile bins (`quantile`)

::: lzsuite._discretization.bin_quantile
    options:
      show_root_heading: false
      show_signature: false

## Ordinal patterns (`permutation`)

::: lzsuite._discretization.permutation
    options:
      show_root_heading: false
      show_signature: false
