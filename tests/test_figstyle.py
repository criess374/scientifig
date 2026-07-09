import matplotlib.pyplot as plt
import numpy as np
import figstylepy


def test_example_plot():
    figstylepy.use_style("paper", width="half")

    fig, ax = plt.subplots(figsize=(7.5, 6))
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), label="sin")
    ax.plot(x, np.cos(x), label="cos")
    ax.set_title("Example")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()

    figstylepy.scale_fonts(fig)
    plt.close(fig)
