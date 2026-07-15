"""scientifig: consistent fontsizes across LaTeX full/half-width figures and slides."""

from .scientifig import (
    use_style,
    reset_style,
    create_figure,
    apply_style,
    savefig,
    scaled_sizes,
    current_scale,
    set_background,
    THEMES,
    BACKGROUNDS,
)

__version__ = "0.1.0"

__all__ = [
    "use_style",
    "reset_style",
    "create_figure",
    "apply_style",
    "savefig",
    "scaled_sizes",
    "current_scale",
    "set_background",
    "THEMES",
    "BACKGROUNDS",
]
