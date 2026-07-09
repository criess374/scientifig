"""scientifig: consistent fontsizes across LaTeX full/half-width figures and slides.

Workflow
--------
    import scientifig

    scientifig.use_style("paper", width="half")   # once, e.g. at the top of a notebook

    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.plot(...)
    scientifig.scale_fonts(fig)                   # once per figure, right before saving/showing

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
from typing import Any

import matplotlib.pyplot as plt

try:
    from cartopy.mpl.gridliner import Gridliner
except ImportError:  # cartopy not installed in this environment
    Gridliner = None


STYLE_DIR = Path(__file__).parent / "mplstyle"

# Assumed LaTeX \linewidth in inches (used to convert the width fraction to inches).
_LINEWIDTH_IN = 15.0

# Theme: mplstyle file. Base sizes are read from the mplstyle via rcParams after plt.style.use().
THEMES: dict[str, dict] = {
    "paper": {
        "mplstyle": STYLE_DIR / "paper.mplstyle",
    },
    "presentation": {
        "mplstyle": STYLE_DIR / "presentation.mplstyle",
    },
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
    width: float
    base_figsize: tuple[float, float]
    sizes: dict[str, float]
    background: str | None


_active: _ActiveStyle | None = None


def use_style(
    theme: str = "paper", width: float = 1.0, background: str | None = None
) -> None:
    """Activate a theme/width/background combination. Call once, e.g. at the top of a notebook.

    Parameters
    ----------
    theme : "paper" or "presentation"
    width : fraction of \\linewidth the figure will occupy in the document (0.01–1.0).
            1.0 = full width, 0.5 = half width.
    background : "transparent", "white", "black", or None to leave the mplstyle's default
    """
    global _active

    if theme not in THEMES:
        raise ValueError(f"Unknown theme {theme!r}; choose from {sorted(THEMES)}")
    if not (0.01 <= width <= 1.0):
        raise ValueError(f"width must be between 0.01 and 1.0, got {width!r}")
    if background is not None and background not in BACKGROUNDS:
        raise ValueError(
            f"Unknown background {background!r}; choose from {sorted(BACKGROUNDS)} or None"
        )

    cfg = THEMES[theme]
    plt.style.use(cfg["mplstyle"])

    if background == "black":
        plt.rcParams.update(
            {
                "figure.facecolor": "black",
                "axes.facecolor": "black",
                "savefig.facecolor": "black",
                "savefig.edgecolor": "black",
                "text.color": "white",
                "axes.labelcolor": "white",
                "xtick.color": "white",
                "ytick.color": "white",
                "axes.edgecolor": ".3",
            }
        )
    elif background == "white":
        plt.rcParams.update(
            {
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "savefig.facecolor": "white",
            }
        )
    elif background == "transparent":
        plt.rcParams.update(
            {
                "figure.facecolor": "none",
                "savefig.facecolor": "none",
            }
        )

    sizes = {
        "title": float(plt.rcParams["axes.titlesize"]),
        "label": float(plt.rcParams["axes.labelsize"]),
        "tick": float(plt.rcParams["xtick.labelsize"]),
        "legend": float(plt.rcParams["legend.fontsize"]),
        "line": float(plt.rcParams["lines.linewidth"]),
        "marker": float(plt.rcParams["lines.markersize"]),
    }

    _active = _ActiveStyle(
        theme=theme,
        width=width,
        base_figsize=(_LINEWIDTH_IN * width, 8.0),
        sizes=sizes,
        background=background,
    )


def create_figure(
    figsize: tuple[float, float],
    nrows: int = 1,
    ncols: int = 1,
    **subplots_kwargs: Any,
) -> tuple[plt.Figure, Any]:
    """Create a figure with scaled font/line sizes already set in rcParams.

    Sizes are scaled for `figsize` relative to the active style's reference width,
    so all artists created during plotting automatically use the correct sizes.
    Manual overrides (e.g. ax.set_title(..., fontsize=20)) are fully preserved.

    Parameters
    ----------
    figsize : (width, height) in inches
    nrows, ncols : passed to plt.subplots
    **subplots_kwargs : additional kwargs forwarded to plt.subplots
    """
    style = _require_active()
    base_w, _ = style.base_figsize
    scale = figsize[0] / base_w

    plt.rcParams.update(
        {
            "axes.titlesize": style.sizes["title"] * scale,
            "axes.labelsize": style.sizes["label"] * scale,
            "xtick.labelsize": style.sizes["tick"] * scale,
            "ytick.labelsize": style.sizes["tick"] * scale,
            "legend.fontsize": style.sizes["legend"] * scale,
            "lines.linewidth": style.sizes["line"] * scale,
            "lines.markersize": style.sizes["marker"] * scale,
        }
    )

    return plt.subplots(nrows, ncols, figsize=figsize, **subplots_kwargs)


def _require_active() -> _ActiveStyle:
    if _active is None:
        raise RuntimeError(
            "No style active. Call scientifig.use_style(theme, width) first."
        )
    return _active


def current_scale(fig: plt.Figure) -> float:
    """Scale factor for `fig` given its actual size vs. the active style's reference size."""
    style = _require_active()
    base_w, _ = style.base_figsize
    fig_w, _ = fig.get_size_inches()
    return fig_w / base_w


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

    bg_color = BACKGROUNDS[choice]
    is_dark = choice == "black"
    alpha = 0.0 if choice == "transparent" else 1.0

    if is_dark:
        text_color = "white"
        label_color = "white"
        tick_color = "white"
        spine_color = ".3"
    else:
        text_color = plt.rcParams["text.color"]
        label_color = plt.rcParams["axes.labelcolor"]
        tick_color = plt.rcParams["xtick.color"]
        spine_color = plt.rcParams["axes.edgecolor"]

    fig.patch.set_facecolor(bg_color)
    fig.patch.set_alpha(alpha)
    for ax in fig.axes:
        ax.patch.set_facecolor(bg_color)
        ax.patch.set_alpha(alpha)
        ax.title.set_color(text_color)
        ax.xaxis.label.set_color(label_color)
        ax.yaxis.label.set_color(label_color)
        ax.tick_params(colors=tick_color)
        for spine in ax.spines.values():
            spine.set_color(spine_color)
        legend = ax.get_legend()
        if legend is not None:
            _color_legend(legend, text_color)

    for legend in getattr(fig, "legends", []):
        _color_legend(legend, text_color)


def scale_fonts(fig: plt.Figure, background: str | None = None) -> None:
    """Apply background color and cartopy gridliner sizes to `fig`.

    Font and line sizes are already set via rcParams when `create_figure()` is
    called, so this function only handles things rcParams cannot cover:
    background/foreground colors and cartopy gridliner label sizes.

    Call this once per figure, after plotting, before saving/showing.
    """
    set_background(fig, background=background)

    if Gridliner is not None:
        sizes = scaled_sizes(fig)
        for ax in fig.axes:
            for artist in getattr(ax, "_gridliners", []):
                if isinstance(artist, Gridliner):
                    artist.xlabel_style = {"size": sizes["tick"]}
                    artist.ylabel_style = {"size": sizes["tick"]}


def savefig(
    fig: plt.Figure,
    filename: str | Path,
    background: str | None = None,
    dpi: int | None = None,
    bbox_inches: str = "tight",
    **kwargs: Any,
) -> Path:
    """Apply background, scale cartopy gridliners, and save `fig`.

    The output filename is auto-suffixed with the active theme, background,
    and width fraction: ``{stem}_{theme}_{background}_{width}.png``.

    Parameters
    ----------
    fig : figure to save
    filename : base filename (extension and suffix are added automatically)
    background : override the active style's background for this save
    dpi : dots per inch (defaults to the mplstyle's savefig.dpi)
    bbox_inches : passed to fig.savefig (default "tight")
    **kwargs : additional kwargs forwarded to fig.savefig

    Returns
    -------
    Path of the saved file.
    """
    style = _require_active()
    scale_fonts(fig, background=background)

    effective_bg = background if background is not None else style.background
    bg_label = effective_bg if effective_bg is not None else "default"
    width_label = f"{style.width:.2f}".replace(".", "p")

    base = Path(filename).with_suffix("")
    out_path = base.parent / f"{base.name}_{style.theme}_{bg_label}_{width_label}.png"

    save_kwargs: dict[str, Any] = {"bbox_inches": bbox_inches}
    if dpi is not None:
        save_kwargs["dpi"] = dpi
    if effective_bg == "transparent":
        save_kwargs["transparent"] = True
    save_kwargs.update(kwargs)

    fig.savefig(out_path, **save_kwargs)
    return out_path


def _style_legend(legend, sizes: dict[str, float]) -> None:
    for text in legend.get_texts():
        text.set_fontsize(sizes["legend"])
    if legend.get_title() is not None:
        legend.get_title().set_fontsize(sizes["legend"])


def _color_legend(legend, color: str) -> None:
    for text in legend.get_texts():
        text.set_color(color)
    if legend.get_title() is not None:
        legend.get_title().set_color(color)
