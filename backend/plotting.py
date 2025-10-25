from typing import Tuple
import io
import matplotlib.pyplot as plt


def render_compass_svg(x: float, y: float, label: str = "Model", size: int = 600) -> str:
    # simple SVG via matplotlib saved to SVG string
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axhline(0, color="#cbd5e1", lw=1)
    ax.axvline(0, color="#cbd5e1", lw=1)
    ax.set_xlim(-11, 11)
    ax.set_ylim(-11, 11)
    ax.scatter([x], [y], c="#111827", s=140, zorder=5)
    ax.text(x, y - 1.0, label, ha="center", va="top", fontsize=9)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight")
    plt.close(fig)
    svg = buf.getvalue()
    buf.close()
    return svg
