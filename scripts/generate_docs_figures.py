"""Generate the documentation's reproducible figures with the real library.

Run ``uv run --group docs python scripts/generate_docs_figures.py``.
All data are synthetic. Figures compare finite-sample measurements, not
universal source characteristics or performance guarantees.
"""

# The backend and cache directory must be set before pyplot imports.
# ruff: noqa: E402

from __future__ import annotations

import json
import os
import platform
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyBboxPatch

import lzsuite as lzs

OUT = ROOT / "docs" / "assets" / "figures"
SEED = 1729
INK, TEAL, CORAL, GOLD, BLUE = "#18333e", "#097d80", "#dd714f", "#c6a356", "#637ead"
COLORS = [TEAL, CORAL, BLUE, GOLD, "#8a6f98", "#83907a"]
BINARY = ListedColormap(["#e5ece8", TEAL])
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.edgecolor": "#c6d3d2",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "#fbfcfa",
        "axes.facecolor": "#fbfcfa",
        "savefig.facecolor": "#fbfcfa",
        "svg.fonttype": "none",
        "svg.hashsalt": "lzsuite-documentation",
        "lines.linewidth": 2,
    }
)


def save(fig, name):
    """Write standalone SVG and PNG exports without time-dependent SVG metadata."""
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight", metadata={"Date": None})
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", dpi=160)
    plt.close(fig)


def titled(ax, title, xlabel=None, ylabel=None):
    """Apply consistent titles, axis labels and quiet grid styling."""
    ax.set_title(title, loc="left", pad=14)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.grid(axis="y", color="#dce4e1", alpha=0.7, zorder=0)
    ax.set_axisbelow(True)


def main():
    """Create all gallery measurements, plots and provenance in one seeded run."""
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    t = np.linspace(0, 8 * np.pi, 240)
    signal = np.sin(t) + 0.28 * np.sin(3.7 * t) + 0.12 * rng.normal(size=t.size)
    labels = lzs.discretize(signal)
    fig, axes = plt.subplots(2, 1, figsize=(10, 3.2), height_ratios=[3, 1], layout="constrained")
    axes[0].plot(signal, color=TEAL)
    axes[0].axhline(signal.mean(), color=CORAL, ls="--", lw=1.4)
    axes[0].set_ylabel("Observation")
    axes[0].set_xticks([])
    axes[1].imshow(labels[None, :], aspect="auto", cmap=BINARY, interpolation="nearest")
    axes[1].set_yticks([0], ["Symbols"])
    axes[1].set_xlabel("Observation index")
    save(fig, "hero")

    # Mean and median differ visibly when a short signal has one large outlier.
    short = np.array([-0.8, -0.3, 0.1, 0.4, 0.8, 1.1, 0.7, 0.2, -0.2, -0.6, -0.4, 5.2])
    fig, axes = plt.subplots(3, 1, figsize=(10, 5), height_ratios=[3, 1, 1], layout="constrained")
    axes[0].plot(short, "o-", color=INK, ms=5)
    axes[0].axhline(short.mean(), color=TEAL, ls="--", label=f"Mean = {short.mean():.2f}")
    axes[0].axhline(np.median(short), color=CORAL, ls=":", label=f"Median = {np.median(short):.2f}")
    titled(axes[0], "The threshold is part of the observation", ylabel="Value")
    axes[0].legend(frameon=False, loc="upper left")
    for ax, method in zip(axes[1:], ["mean", "median"], strict=True):
        row = lzs.discretize(short, method)
        ax.imshow(row[None], cmap=BINARY, vmin=0, vmax=1, aspect="auto")
        ax.set_yticks([0], [method])
        ax.set_xticks(range(len(short)))
        for i, value in enumerate(row):
            ax.text(i, 0, str(value), ha="center", va="center", color="white" if value else INK)
    axes[-1].set_xlabel("Observation index")
    save(fig, "thresholds")

    skew = rng.lognormal(mean=0, sigma=0.65, size=1600)
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), layout="constrained")
    for column, method in enumerate(["bins", "quantile"]):
        edges = (
            np.linspace(skew.min(), skew.max(), 5)[1:-1]
            if method == "bins"
            else np.quantile(skew, [0.25, 0.5, 0.75])
        )
        row = lzs.discretize(skew, method, n_bins=4)
        axes[0, column].hist(skew, bins=45, color=TEAL, alpha=0.8)
        for edge in edges:
            axes[0, column].axvline(edge, color=CORAL, lw=1.6)
        titled(
            axes[0, column],
            "Equal width" if method == "bins" else "Quantile edges",
            "Value",
            "Count",
        )
        axes[1, column].bar(range(4), np.bincount(row, minlength=4), color=COLORS[:4])
        axes[1, column].set_xticks(range(4))
        titled(axes[1, column], "Occupied labels", "Label", "Observations")
    save(fig, "binning")

    ordinal_signal = np.sin(np.linspace(0, 7 * np.pi, 120)) + 0.35 * rng.normal(size=120)
    ordinal = lzs.discretize(ordinal_signal, "permutation", order=3)
    fig, axes = plt.subplots(3, 1, figsize=(10, 6), height_ratios=[2, 1, 2], layout="constrained")
    axes[0].plot(ordinal_signal, color=TEAL)
    titled(axes[0], "A window's ordering becomes its symbol", ylabel="Value")
    axes[1].imshow(ordinal[None], cmap=ListedColormap(COLORS), vmin=0, vmax=5, aspect="auto")
    axes[1].set_yticks([0], ["Pattern rank"])
    axes[1].set_xlabel("Window start index")
    axes[2].bar(range(6), np.bincount(ordinal, minlength=6), color=COLORS)
    titled(axes[2], "Order 3 admits six patterns", "Lexicographic permutation rank", "Windows")
    axes[2].set_xticks(range(6))
    save(fig, "permutations")

    # All scientific comparisons below use actual backend measurements.
    n = 8192
    constant = np.zeros(n, dtype=int)
    alternating = np.tile([0, 1], n // 2)
    period4 = np.tile([0, 0, 1, 1], n // 4)
    period8 = np.tile([0, 0, 0, 1, 0, 1, 1, 1], n // 8)
    markov = np.cumsum(rng.random(n) < 0.08).astype(int) % 2
    independent = rng.integers(0, 2, size=n)
    sequences = np.stack([constant, alternating, period4, period8, markov, independent], axis=1)
    names = ["Constant", "Alternating", "Period 4", "Period 8", "Persistent", "Independent"]
    entropy = lzs.h(sequences, n_jobs=1)
    scores, profiles = lzs.emc(sequences, max_block_size=6, n_jobs=1)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")
    for ax, values, title, unit in zip(
        axes,
        [entropy, scores],
        ["New information: h", "Finite-range organization: E"],
        ["Normalized LZ76 rate", "E, cap = 6"],
        strict=True,
    ):
        ax.barh(names, values, color=COLORS)
        ax.invert_yaxis()
        titled(ax, title, unit)
    save(fig, "measures")

    sizes = 2 ** np.arange(7, 14)
    fig, ax = plt.subplots(figsize=(10, 4.4), layout="constrained")
    for sequence, name, color in zip(
        [period8, markov, independent],
        ["Period 8", "Persistent", "Independent"],
        COLORS[:3],
        strict=True,
    ):
        estimates = [lzs.h(sequence[:size], log_base=2, n_jobs=1) for size in sizes]
        ax.plot(sizes, estimates, "o-", label=name, color=color, ms=5)
    ax.axhline(1, ls=":", color=INK, lw=1, label="Fair iid binary source: 1 bit")
    ax.set_xscale("log", base=2)
    ax.set_xticks(sizes, [str(x) for x in sizes])
    titled(ax, "A finite sample is not the infinite source", "Prefix length", "h (bits per symbol)")
    ax.legend(frameon=False, ncols=2)
    save(fig, "convergence")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3), layout="constrained")
    for index in [2, 3, 4, 5]:
        increments = np.asarray(profiles[index])
        axes[0].plot(
            np.arange(1, len(increments) + 1),
            np.cumsum(increments),
            "o-",
            label=names[index],
            color=COLORS[index],
        )
    titled(axes[0], "The fitted profile climbs to E", "Window range", "Cumulative increments")
    axes[0].legend(frameon=False)
    axes[1].bar(np.arange(1, 7), profiles[3], color=TEAL)
    titled(axes[1], "Period-8 increments", "Window range", "Contribution to E")
    save(fig, "emc-profiles")

    shuffle, _ = lzs.emc(sequences, method="shuffle", max_block_size=6, n_jobs=1)
    fig, ax = plt.subplots(figsize=(10, 4.4), layout="constrained")
    x = np.arange(6)
    ax.bar(x - 0.18, scores, width=0.36, color=TEAL, label="Chao–Shen")
    ax.bar(x + 0.18, shuffle, width=0.36, color=CORAL, label="Shuffle")
    ax.set_xticks(x, names, rotation=15, ha="right")
    titled(ax, "Different estimators, explicitly selected", ylabel="E (fixed cap = 6)")
    ax.legend(frameon=False)
    save(fig, "estimators")

    # n observations × 4 channels × 3 trials: each result position is explicit.
    time = np.linspace(0, 30 * np.pi, 2048)
    array = np.empty((2048, 4, 3))
    for channel in range(4):
        for trial in range(3):
            array[:, channel, trial] = np.sin(time * (1 + 0.1 * channel)) + (
                0.1 + 0.25 * trial + 0.05 * channel
            ) * rng.normal(size=len(time))
    axis_h = lzs.h(array, n_jobs=1)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")
    for c in range(4):
        axes[0].plot(array[:100, c, 0] + 3 * c, color=COLORS[c], lw=1.4)
    axes[0].set_yticks(np.arange(4) * 3, [f"Channel {i}" for i in range(4)])
    titled(axes[0], "Input: (2048, 4, 3), axis=0", "Observation index")
    image = axes[1].imshow(axis_h, cmap="YlGnBu", aspect="auto", vmin=0)
    axes[1].set_xticks(range(3), [f"Trial {i}" for i in range(3)])
    axes[1].set_yticks(range(4), [f"Channel {i}" for i in range(4)])
    titled(axes[1], "Output: one h per position, (4, 3)")
    for index in np.ndindex(axis_h.shape):
        axes[1].text(
            index[1],
            index[0],
            f"{axis_h[index]:.2f}",
            ha="center",
            va="center",
            color="white" if axis_h[index] > 0.6 * axis_h.max() else INK,
        )
    fig.colorbar(image, ax=axes[1], label="h (observed binary base)", shrink=0.8)
    save(fig, "axes")

    collection = np.stack(
        [
            alternating[:2048],
            alternating[:2048],
            period4[:2048],
            period4[:2048] ^ (rng.random(2048) < 0.03),
            period8[:2048],
            period8[:2048] ^ (rng.random(2048) < 0.03),
            independent[:2048],
            rng.integers(0, 2, size=2048),
        ],
        axis=1,
    )
    matrix_names = ["Alt A", "Alt copy", "P4", "P4 + noise", "P8", "P8 + noise", "iid A", "iid B"]
    distances = lzs.distance(collection, n_jobs=1)
    fig, ax = plt.subplots(figsize=(8.6, 6.7), layout="constrained")
    image = ax.imshow(distances, cmap="YlGnBu", vmin=min(0, distances.min()))
    ax.set_xticks(range(8), matrix_names, rotation=40, ha="right")
    ax.set_yticks(range(8), matrix_names)
    titled(ax, "Every sequence pair; actual diagonal retained")
    for i, j in np.ndindex(distances.shape):
        ax.text(
            j,
            i,
            f"{distances[i, j]:.2f}",
            ha="center",
            va="center",
            fontsize=8,
            color="white" if distances[i, j] > 0.58 * distances.max() else INK,
        )
    fig.colorbar(image, ax=ax, label="LZ76 NID", shrink=0.8)
    save(fig, "distance-matrix")

    other = array + rng.normal(size=array.shape) * np.array([0, 0.4, 1.0])[None, None, :]
    paired = lzs.distance(array, other, n_jobs=1)
    fig, ax = plt.subplots(figsize=(8.5, 4.4), layout="constrained")
    image = ax.imshow(paired, aspect="auto", cmap="YlGnBu", vmin=min(0, paired.min()))
    ax.set_xticks(range(3), ["No added noise", "Noise σ=0.4", "Noise σ=1.0"])
    ax.set_yticks(range(4), [f"Channel {i}" for i in range(4)])
    titled(ax, "Corresponding pairs preserve the (4, 3) layout")
    for i, j in np.ndindex(paired.shape):
        ax.text(
            j,
            i,
            f"{paired[i, j]:.2f}",
            ha="center",
            va="center",
            color="white" if paired[i, j] > 0.58 * paired.max() else INK,
        )
    fig.colorbar(image, ax=ax, label="LZ76 NID", shrink=0.8)
    save(fig, "paired-distances")

    def fixed_threshold(values, *, level=0):
        """Return binary labels above a fixed level for the custom-method example."""
        return (values > level).astype(np.uint8)

    levels = np.linspace(-1.2, 1.2, 13)
    custom_h = [
        lzs.h(
            array[:, 0, 0],
            discretization=fixed_threshold,
            discretization_kwargs={"level": level},
            n_jobs=1,
        )
        for level in levels
    ]
    balances = [np.mean(fixed_threshold(array[:, 0, 0], level=level)) for level in levels]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), layout="constrained")
    for ax, values, title, label, color in zip(
        axes,
        [balances, custom_h],
        ["What the threshold preserves", "What the parser measures"],
        ["Fraction of ones", "h (observed binary base)"],
        COLORS[:2],
        strict=True,
    ):
        ax.plot(levels, values, "o-", color=color)
        titled(ax, title, "Fixed threshold", label)
    save(fig, "custom-threshold")

    chars = np.array(list("banana"))
    count, boundaries = lzs.factorization(chars)
    fig, ax = plt.subplots(figsize=(10, 3.2), layout="constrained")
    for i, char in enumerate(chars):
        ax.text(
            i + 0.5, 0.6, char, ha="center", va="center", fontsize=28, family="DejaVu Sans Mono"
        )
        ax.text(i, -0.1, str(i), ha="center", fontsize=9, color="#627b82")
    for k, (start, stop) in enumerate(zip(boundaries[:-1], boundaries[1:], strict=True)):
        visible_stop = min(stop, len(chars))
        ax.add_patch(
            FancyBboxPatch(
                (start + 0.04, 0.2),
                visible_stop - start - 0.08,
                0.75,
                boxstyle="round,pad=0.02",
                edgecolor=COLORS[k],
                facecolor="none",
                linewidth=2,
                linestyle="--" if stop > len(chars) else "-",
            )
        )
    ax.text(3.1, 1.2, "Copied tail: boundary 7 lies beyond length 6", color=CORAL)
    ax.text(
        0, 1.65, f"{count} completed phrases · boundaries {boundaries}", weight="bold", fontsize=13
    )
    ax.set(xlim=(-0.1, 6.1), ylim=(-0.4, 2), xticks=[], yticks=[])
    for spine in ax.spines.values():
        spine.set_visible(False)
    save(fig, "factorization")

    parallel_h = lzs.h(array, n_jobs=2)
    np.testing.assert_array_equal(axis_h, parallel_h)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), layout="constrained")
    axes[0].plot(axis_h.ravel(), "o-", color=TEAL, label="Inline (n_jobs=1)")
    axes[0].plot(parallel_h.ravel(), "x", color=CORAL, ms=8, label="Processes (n_jobs=2)")
    titled(axes[0], "Same sequences, same results", "Flattened channel/trial index", "h")
    axes[0].legend(frameon=False)
    axes[1].bar(range(axis_h.size), (parallel_h - axis_h).ravel(), color=TEAL)
    axes[1].axhline(0, color=INK, lw=1)
    axes[1].set_ylim(-1e-12, 1e-12)
    titled(
        axes[1],
        "Numerical difference is zero",
        "Flattened channel/trial index",
        "Parallel − inline",
    )
    save(fig, "parallel-agreement")

    metadata = {
        "seed": SEED,
        "python": platform.python_version(),
        "versions": {
            name: version(name)
            for name in ["lzsuite", "lzcomplexity", "numpy", "matplotlib", "joblib"]
        },
        "comparison_length": n,
        "emc_cap": 6,
        "measure_names": names,
        "h": entropy.tolist(),
        "emc": scores.tolist(),
        "shuffle_emc": shuffle.tolist(),
        "distance_names": matrix_names,
        "distance_matrix": distances.tolist(),
        "axis_shape": list(array.shape),
        "axis_h": axis_h.tolist(),
        "paired_distances": paired.tolist(),
        "parallel_max_absolute_difference": float(np.max(np.abs(parallel_h - axis_h))),
        "figures": sorted(path.stem for path in OUT.glob("*.svg")),
    }
    (OUT / "provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Generated {len(metadata['figures'])} figure pairs in {OUT}")


if __name__ == "__main__":
    main()
