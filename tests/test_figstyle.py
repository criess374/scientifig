import matplotlib.pyplot as plt
import numpy as np
import figstylepy


def test_example_plot():
    figstylepy.use_style("paper", width=0.5)

    fig, ax = figstylepy.create_figure(figsize=(7.5, 6))
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), label="sin")
    ax.plot(x, np.cos(x), label="cos")
    ax.set_title("Example")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()

    # sizes are set in rcParams at create_figure time — verify they were applied
    sizes = figstylepy.scaled_sizes(fig)
    assert ax.title.get_fontsize() == sizes["title"]
    assert ax.xaxis.label.get_fontsize() == sizes["label"]
    assert ax.yaxis.label.get_fontsize() == sizes["label"]
    assert ax.get_legend().get_texts()[0].get_fontsize() == sizes["legend"]

    figstylepy.scale_fonts(fig)  # applies background / cartopy gridliners
    plt.close(fig)
