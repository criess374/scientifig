# scientifig

Consistent font and line sizes across LaTeX full/half-width figures and slides.

When a figure is placed in LaTeX with `\includegraphics[width=\linewidth]{...}` or `[width=0.5\linewidth]{...}`, it is rescaled to fit the column. A figure saved at a larger `figsize` gets scaled down more, so its fonts need to be drawn proportionally larger in matplotlib to appear the same size on the page. `scientifig` handles this automatically.

You can choose from the built-in themes (`"paper"`, `"presentation"`, `"poster"`), set a background color (`"white"`, `"black"`, `"transparent"`), and register your own themes by adding entries to `scientifig.THEMES` pointing to a custom `.mplstyle` file.

## Installation

Clone the repository and install locally:

```bash
git clone https://github.com/criess374/scientifig.git
cd scientifig
pip install .
```

## Usage

```python
import numpy as np
import matplotlib.pyplot as plt
import scientifig

# Set theme and the fraction of \linewidth the figure will occupy (once per notebook)
scientifig.use_style("paper", width=0.5)

# Create figure — fonts and line widths are scaled automatically
fig, ax = scientifig.create_figure(figsize=(7.5, 6))
ax.plot(np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100)))

# Apply background and gridliner sizes, then show/save
scientifig.scale_fonts(fig)
plt.show()
```

### Themes

| Theme | Description |
|---|---|
| `"paper"` | Journal figures |
| `"presentation"` | Slide figures |
| `"poster"` | Print posters (large fonts, thick lines) |

Custom themes can be added by registering a new entry in `scientifig.THEMES` before calling `use_style`:

```python
from pathlib import Path
scientifig.THEMES["mytheme"] = {"mplstyle": Path("path/to/mytheme.mplstyle")}
scientifig.use_style("mytheme", width=1.0)
```

### `use_style` options

| Parameter | Description |
|---|---|
| `theme` | `"paper"`, `"presentation"`, or `"poster"` |
| `width` | Fraction of `\linewidth` (e.g. `1.0` = full width, `0.5` = half width) |
| `background` | `"white"`, `"black"`, `"transparent"`, or `None` |

## Optional dependency

Cartopy gridliner label sizes are scaled automatically when `cartopy` is installed:

```bash
pip install "scientifig[cartopy]"
```
