# scientifig

Consistent font and line sizes for figures across papers, presentations, and posters.

Each theme has a reference canvas width (the assumed physical width of the document column, slide area, or poster column). When you specify `width=0.5`, the reference figsize is half that canvas width. If you then create a figure at a different size, `scientifig` scales every font, line, and marker proportionally so that elements appear at the same physical size regardless of the figure dimensions.

You can choose from the built-in themes (`"paper"`, `"presentation"`, `"poster"`), set a background color (`"white"`, `"black"`, `"transparent"`), and register your own themes by adding entries to `scientifig.THEMES` pointing to a custom `.mplstyle` file.

## Installation

Clone the repository and install locally:

```bash
git clone https://github.com/criess374/scientifig.git
cd scientifig
pip install .
```

For development (includes pytest, pre-commit, etc.):

```bash
pip install -e ".[dev]"
```

## Usage

```python
import numpy as np
import scientifig

# Set theme and the fraction of \linewidth the figure will occupy (once per notebook)
scientifig.use_style("paper", width=0.5)

# Create figure — fonts and line widths are scaled automatically
fig, ax = scientifig.create_figure(figsize=(7.5, 6))
ax.plot(np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100)))

# Apply  gridliner sizes, then show/save with adjusted name
scientifig.savefig(fig, "output")  # saves with auto-suffix; or just plt.show()
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
| `width` | Fraction of total width (e.g. `1.0` = full width, `0.5` = half width) |
| `background` | `"white"`, `"black"`, `"transparent"`, or `None` |

## Optional dependency

Cartopy gridliner label sizes are scaled automatically when `cartopy` is installed:

```bash
pip install "scientifig[cartopy]"
```
