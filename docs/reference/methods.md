# Built-in method rules

These entries document the implementation rules, but the functions themselves
are private implementation details. Invoke them through the public
`lzs.discretize(data, method="...")` API or a calculation's `discretization`
argument. Importing private modules is not needed for normal use.

## Mean (`mean`)

::: lzsuite._discretization.binarize_mean
    options:
      show_root_heading: false

## Median (`median`)

::: lzsuite._discretization.binarize_median
    options:
      show_root_heading: false

## Equal-width bins (`bins`)

::: lzsuite._discretization.bin_equal_width
    options:
      show_root_heading: false

## Quantile bins (`quantile`)

::: lzsuite._discretization.bin_quantile
    options:
      show_root_heading: false

## Ordinal patterns (`permutation`)

::: lzsuite._discretization.permutation
    options:
      show_root_heading: false
