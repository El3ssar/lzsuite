---
hide:
  - navigation
  - toc
---

<div class="lz-home" markdown>
<div class="lz-hero">
<div>
<p class="lz-eyebrow">A Python toolkit for symbolic sequences</p>
<h1>Find the structure<br>inside your <em>signals.</em></h1>
<p class="lz-lede">Turn continuous observations into symbols. Measure randomness, explore organization, and compare patterns—across every sequence in your array.</p>
<div class="lz-actions">
<a class="lz-button" href="guide/quickstart/">Start exploring →</a>
<a class="lz-button secondary" href="gallery/">See the gallery</a>
</div>
<div class="lz-install" aria-label="Installation commands">
<div class="lz-install-tabs"><button type="button" data-command="pip install lzsuite" aria-pressed="true">pip</button><button type="button" data-command="uv add lzsuite" aria-pressed="false">uv</button></div>
<div class="lz-install-command"><code>pip install lzsuite</code><button type="button" class="lz-copy" aria-label="Copy installation command">Copy</button></div>
</div>
</div>
<div class="lz-figure-card">
<div class="lz-card-label">Continuous input. Discrete perspective.</div>
<img src="assets/figures/hero.svg" alt="A smooth oscillatory signal is transformed into a two-color row of binary symbols by mean thresholding." width="640" height="220">
<div class="lz-pipeline"><span>01 <strong>Discretize</strong></span><span>→</span><span>02 <strong>Analyze</strong></span><span>→</span><span>03 <strong>Compare</strong></span></div>
</div>
</div>

<div class="lz-statline"><span><strong>Python</strong> 3.10+</span><span><strong>NumPy</strong> arrays, any axis</span><span><strong>5</strong> built-in discretizers</span><span><strong>Rust</strong> powered by lzcomplexity</span><span><strong>MIT</strong> open source</span></div>

<div class="lz-section-head"><h2>One workflow. Many questions.</h2><p>Keep the scientific choices explicit. Let the library handle the shapes, encodings, and independent calculations.</p></div>
<div class="lz-cards">
<div class="lz-feature"><span class="number">01 / REPRESENT</span><h3>Choose your symbols</h3><p>Mean and median thresholds, equal-width and quantile bins, or ordinal patterns. Bring a custom method by name or callable.</p></div>
<div class="lz-feature"><span class="number">02 / MEASURE</span><h3>Read randomness & structure</h3><p>Use LZ76 factor counts, entropy density h, and effective measure complexity E. Inspect the phrases and scale profiles behind each result.</p></div>
<div class="lz-feature"><span class="number">03 / COMPARE</span><h3>Map shared patterns</h3><p>Build all-pairs information-distance matrices or compare corresponding sequences while preserving your array's channel and trial layout.</p></div>
</div>

<div class="lz-workbench">
<div><p class="lz-eyebrow">Array-aware by design</p><h2>Your observations have an axis.</h2><p>For data shaped <code>(1000, 4, 3)</code>, selecting <code>axis=0</code> analyzes twelve sequences of a thousand observations. Scalar results keep the remaining dimensions.</p><p>Change the axis to see how the question changes. This widget shows shapes, not computed entropy values.</p></div>
<div class="lz-axis-demo"><label for="sequence-axis">Sequence axis</label><select id="sequence-axis"><option value="0">axis = 0</option><option value="1">axis = 1</option><option value="2">axis = 2</option></select><div class="lz-axis-grid" aria-live="polite"><div><span>INPUT SHAPE</span><strong>(1000, 4, 3)</strong></div><div><span>RESULT SHAPE</span><strong id="result-shape">(4, 3)</strong></div><div><span>SEQUENCES</span><strong id="sequence-count">12</strong></div><div><span>OBSERVATIONS EACH</span><strong id="sequence-length">1,000</strong></div></div></div>
</div>

## A small API, ready for your arrays

```python
import numpy as np
import lzsuite as lzs

signal = np.sin(np.linspace(0, 40, 2000))
data = np.random.default_rng(42).normal(size=(2000, 4, 3))

lzs.h(signal)  # Python float, no .item() needed
lzs.h(data).shape  # (4, 3): one result per channel/trial
lzs.distance(data).shape  # (12, 12): every sequence pair
lzs.distance(data, data).shape  # (4, 3): corresponding pairs
```

Float data default to per-sequence mean binarization. Already-discrete integer,
boolean, and string arrays keep their category meanings. Normalization uses each
prepared sequence's observed alphabet, with a minimum base of two.

<div class="lz-section-head"><h2>Explore with real calculations.</h2><p>Seeded synthetic observations, measured with the actual backend. Every figure has reproducible source and downloadable exports.</p></div>
<div class="lz-cards">
<a class="lz-gallery-card" href="gallery/discretization/"><img src="assets/figures/thresholds.svg" alt="Mean and median thresholds produce different binary sequences for observations containing an outlier." loading="lazy"><strong>Representation changes the question</strong><span>Thresholds, bins, and category balance →</span></a>
<a class="lz-gallery-card" href="gallery/structure/"><img src="assets/figures/measures.svg" alt="Bar charts compare h and E for constant, periodic, persistent, and independent binary sequences." loading="lazy"><strong>Randomness meets organization</strong><span>Entropy, scale profiles, and finite lengths →</span></a>
<a class="lz-gallery-card" href="gallery/distances/"><img src="assets/figures/distance-matrix.svg" alt="An eight-by-eight measured information-distance matrix compares periodic and random sequences." loading="lazy"><strong>Patterns shared across sequences</strong><span>Pairwise matrices and corresponding comparisons →</span></a>
</div>

<div class="lz-bottom"><p>Built on <a href="https://github.com/pleros-ai/lzcomplexity">lzcomplexity</a>. Designed for reproducible scientific workflows, with explicit encodings and measurable behavior.</p><div class="lz-actions"><a class="lz-button secondary" href="reference/analysis/">Read the API</a><a class="lz-button secondary" href="https://github.com/El3ssar/lzsuite">View source ↗</a></div></div>
</div>
