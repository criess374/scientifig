"""figstylepy: consistent fontsizes across LaTeX full/half-width figures and slides."""

from .figstyle import (
    use_style,
    scale_fonts,
    scaled_sizes,
    current_scale,
    set_background,
    THEMES,
    WIDTHS,
    BACKGROUNDS,
)

__version__ = "0.1.0"

__all__ = [
    "use_style",
    "scale_fonts",
    "scaled_sizes",
    "current_scale",
    "set_background",
    "THEMES",
    "WIDTHS",
    "BACKGROUNDS",
]
