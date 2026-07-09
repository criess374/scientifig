"""figstyle: consistent fontsizes across LaTeX full/half-width figures and slides.

Workflow
--------
    import figstyle

    figstyle.use_style("paper", width="half")   # once, e.g. at the top of a notebook

    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.plot(...)
    figstyle.scale_fonts(fig)                   # once per figure, right before saving/showing

Why this works
---------------
When a figure is placed in LaTeX as \\includegraphics[width=\\linewidth]{...} or
[width=0.5\\linewidth]{...}, it gets rescaled to fit that slot. A figure saved
with a *larger* figsize (at the same DPI) ends up scaled down more by LaTeX,
so its fonts must be drawn *larger* in matplotlib to look the same size on
the page. `scale_fonts` compares the actual `fig.get_size_inches()` against
the reference figsize for the active style and scales every font/line/marker
accordingly, so you can freely change figsize without fonts drifting.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt

try:
    from cartopy.mpl.gridliner import Gridliner
except ImportError:  # cartopy not installed in this environment
    Gridliner = None


STYLE_DIR = Path(__file__).parent / "mplstyle"

# Theme: mplstyle file + base font/line/marker sizes (at the theme's reference figsize).
THEMES: dict[str, dict] = {
    "paper": {
        "mplstyle": STYLE_DIR / "paper.mplstyle",
        "sizes": {
            "title": 21.0,
            "label": 18.0,
            "tick": 15.0,
            "legend": 15.0,
            "line": 2.0,
            "marker": 8.0,
        },
        "scale_correction": 1.0,
    },
    "presentation": {
        "mplstyle": STYLE_DIR / "presentation.mplstyle",
        "sizes": {
            "title": 18.0,
            "label": 15.0,
            "tick": 13.0,
            "legend": 13.0,
            "line": 3.0,
            "marker": 8.0,
        },
        "scale_correction": 0.92,
    },
    "presentation_black": {
        "mplstyle": STYLE_DIR / "presentation_black.mplstyle",
        "sizes": {
            "title": 18.0,
            "label": 15.0,
            "tick": 13.0,
            "legend": 13.0,
            "line": 3.0,
            "marker": 8.0,
        },
        "scale_correction": 0.92,
    },
}

# Width: reference figsize that the theme's base sizes were tuned for.
# Width: reference figsize that the theme's base sizes were tuned for.
WIDTHS: dict[str, tuple[float, float]] = {
    "full": (15.0, 8.0),
    "half": (7.5, 8.0),
}

# Background option: "transparent", "white", "black", or None (leave style's default).
BACKGROUNDS = {
    "transparent": "none",
    "white": "white",
    "black": "black",
}


@dataclass
class _ActiveStyle:
    theme: str
    width: str
    base_figsize: tuple[float, float]
    sizes: dict[str, float]
    scale_correction: float
    background: str | None


_active: _ActiveStyle | None = None


def use_style(
    theme: str = "paper", width: str = "full", background: str | None = None
) -> None:
    """Activate a theme/width/background combination. Call once, e.g. at the top of a notebook.

    Parameters
    ----------
    theme : "paper", "presentation", or "presentation_black"
    width : "full" or "half" -- the reference LaTeX slot this figure is tuned for
    background : "transparent", "white", "black", or None to leave the mplstyle's default
    """
    global _active

    if theme not in THEMES:
        raise ValueError(f"Unknown theme {theme!r}; choose from {sorted(THEMES)}")
    if width not in WIDTHS:
        raise ValueError(f"Unknown width {width!r}; choose from {sorted(WIDTHS)}")
    if background is not None and background not in BACKGROUNDS:
        raise ValueError(
            f"Unknown background {background!r}; choose from {sorted(BACKGROUNDS)} or None"
        )

    cfg = THEMES[theme]
    plt.style.use(cfg["mplstyle"])

    _active = _ActiveStyle(
        theme=theme,
        width=width,
        base_figsize=WIDTHS[width],
        sizes=cfg["sizes"],
        scale_correction=cfg["scale_correction"],
        background=background,
    )


def _require_active() -> _ActiveStyle:
    if _active is None:
        raise RuntimeError(
            "No style active. Call figstyle.use_style(theme, width) first."
        )
    return _active


def current_scale(fig: plt.Figure) -> float:
    """Scale factor for `fig` given its actual size vs. the active style's reference size."""
    style = _require_active()
    base_w, _ = style.base_figsize
    width, _ = fig.get_size_inches()
    scale = width / base_w
    return scale * style.scale_correction


def scaled_sizes(fig: plt.Figure) -> dict[str, float]:
    """Font/line/marker sizes for `fig`, scaled for its actual figsize."""
    style = _require_active()
    scale = current_scale(fig)
    return {name: value * scale for name, value in style.sizes.items()}


def set_background(fig: plt.Figure, background: str | None = None) -> None:
    """Set the figure and axes background.

    `background` overrides the active style's setting for just this call;
    if omitted, the active style's `background` (from `use_style`) is used.
    Does nothing if no background is specified anywhere.

    Note: for "transparent" to actually show up in saved files, also pass
    `transparent=True` to `fig.savefig(...)` (matplotlib otherwise flattens
    the alpha channel on save unless told not to).
    """
    style = _require_active()
    choice = background if background is not None else style.background
    if choice is None:
        return
    if choice not in BACKGROUNDS:
        raise ValueError(
            f"Unknown background {choice!r}; choose from {sorted(BACKGROUNDS)} or None"
        )

    color = BACKGROUNDS[choice]
    fig.patch.set_facecolor(color)
    fig.patch.set_alpha(0.0 if choice == "transparent" else 1.0)
    for ax in fig.axes:
        ax.patch.set_facecolor(color)
        ax.patch.set_alpha(0.0 if choice == "transparent" else 1.0)


def scale_fonts(fig: plt.Figure, background: str | None = None) -> dict[str, float]:
    """Apply scaled fontsizes to everything on `fig`: axes, legends, cartopy gridliners.

    Also applies the active (or per-call override) background color.
    Call this once per figure, after plotting, before saving/showing.
    Returns the computed sizes dict in case you need it (e.g. for manual text).
    """
    sizes = scaled_sizes(fig)
    set_background(fig, background=background)

    for ax in fig.axes:
        ax.tick_params(labelsize=sizes["tick"])
        if ax.get_title():
            ax.title.set_fontsize(sizes["title"])
        ax.xaxis.label.set_fontsize(sizes["label"])
        ax.yaxis.label.set_fontsize(sizes["label"])

        legend = ax.get_legend()
        if legend is not None:
            _style_legend(legend, sizes)

        if Gridliner is not None:
            for artist in getattr(ax, "_gridliners", []):
                if isinstance(artist, Gridliner):
                    artist.xlabel_style = {"size": sizes["tick"]}
                    artist.ylabel_style = {"size": sizes["tick"]}

    fig_legend = getattr(fig, "legends", [])
    for legend in fig_legend:
        _style_legend(legend, sizes)

    return sizes


def _style_legend(legend, sizes: dict[str, float]) -> None:
    for text in legend.get_texts():
        text.set_fontsize(sizes["legend"])
    if legend.get_title() is not None:
        legend.get_title().set_fontsize(sizes["legend"])
