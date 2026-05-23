"""Render the LP-pipeline flowchart for the efficiency analysis.

The instructor (Prof. Amirteimoori, 14 May 2026 lecture) explicitly asked
students to "draw a flow chart, then write the code" for the performance
evaluation homework. This script produces ``figures/pipeline_flowchart.png``.

Run from the project root:
    python scripts/draw_flowchart.py
"""
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = PROJECT_ROOT / "figures"

NODE_FACECOLOR = "#ecf3fb"
NODE_EDGECOLOR = "#2980b9"
DECISION_FACECOLOR = "#fdf2e3"
DECISION_EDGECOLOR = "#e67e22"
TERMINAL_FACECOLOR = "#e8f6ee"
TERMINAL_EDGECOLOR = "#27ae60"
ARROW_COLOR = "#34495e"
TEXT_COLOR = "#1f2d3d"


def add_box(ax, x, y, w, h, text, *, kind="process"):
    if kind == "terminal":
        face, edge = TERMINAL_FACECOLOR, TERMINAL_EDGECOLOR
        boxstyle = "round,pad=0.02,rounding_size=0.25"
    elif kind == "decision":
        face, edge = DECISION_FACECOLOR, DECISION_EDGECOLOR
        boxstyle = "round,pad=0.02,rounding_size=0.05"
    else:
        face, edge = NODE_FACECOLOR, NODE_EDGECOLOR
        boxstyle = "round,pad=0.02,rounding_size=0.08"

    box = mpatches.FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle=boxstyle,
        linewidth=1.6,
        facecolor=face,
        edgecolor=edge,
        zorder=2,
    )
    ax.add_patch(box)
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=9.5,
        color=TEXT_COLOR,
        zorder=3,
    )


def add_arrow(ax, start, end, *, label=None, label_offset=(0.0, 0.0)):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=14,
        linewidth=1.4,
        color=ARROW_COLOR,
        zorder=1,
    )
    ax.add_patch(arrow)
    if label is not None:
        mx = (start[0] + end[0]) / 2 + label_offset[0]
        my = (start[1] + end[1]) / 2 + label_offset[1]
        ax.text(
            mx,
            my,
            label,
            ha="center",
            va="center",
            fontsize=8.5,
            color=ARROW_COLOR,
            style="italic",
            bbox=dict(
                facecolor="white",
                edgecolor="none",
                pad=1.5,
            ),
            zorder=3,
        )


def main() -> None:
    fig, ax = plt.subplots(figsize=(9, 12))

    w, h = 4.6, 0.7

    nodes = {
        "start": (5.0, 11.5, "Start: J firms, M inputs, single output"),
        "load": (5.0, 10.4, "Load CSV  →  X (J×M),  Y (J,)"),
        "validate": (5.0, 9.3, "Validate:  X > 0  and  Y > 0"),
        "log": (5.0, 8.2, "Transform:  ln(X),  ln(Y)"),
        "build_lp": (
            5.0,
            7.0,
            "Build LP\n"
            "min Σ D_j   s.t.   D_j = ln(K) + Σ α_i·ln(X_ij) − ln(Y_j)\n"
            "D_j ≥ 0,   α_i ≥ 0,   ln(K) free",
        ),
        "solve": (5.0, 5.6, "Solve LP with CBC (PuLP)"),
        "decision": (5.0, 4.5, "Status == Optimal ?"),
        "recover": (
            5.0,
            3.4,
            "Recover  K = exp(ln K),  α = (α₁,…,α_M),  D = (D₁,…,D_J)",
        ),
        "kpi": (
            5.0,
            2.3,
            "Compute  Y_optimal_j = K·∏ X_ij^α_i\n"
            "KPI_j = Y_obs_j / Y_opt_j ∈ (0, 1]",
        ),
        "classify": (
            5.0,
            1.2,
            "Classify firm j  →  efficient (D_j ≈ 0)  or  inefficient",
        ),
        "end": (5.0, 0.2, "End: parameters table, summary table, figures"),
        "fail": (9.7, 3.4, "Raise RuntimeError"),
    }

    for key, (x, y, text) in nodes.items():
        if key in ("start", "end"):
            kind = "terminal"
        elif key == "decision":
            kind = "decision"
        elif key == "fail":
            kind = "terminal"
        else:
            kind = "process"
        bw = w
        bh = h
        if key in ("build_lp", "kpi"):
            bh = 1.0
        if key == "fail":
            bw = 2.4
        add_box(ax, x, y, bw, bh, text, kind=kind)

    sequence = [
        ("start", "load"),
        ("load", "validate"),
        ("validate", "log"),
        ("log", "build_lp"),
        ("build_lp", "solve"),
        ("solve", "decision"),
        ("decision", "recover"),
        ("recover", "kpi"),
        ("kpi", "classify"),
        ("classify", "end"),
    ]

    for src, dst in sequence:
        sx, sy, _ = nodes[src]
        dx, dy, _ = nodes[dst]
        src_half = 0.5 if src in ("build_lp", "kpi") else 0.35
        dst_half = 0.5 if dst in ("build_lp", "kpi") else 0.35
        start = (sx, sy - src_half)
        end = (dx, dy + dst_half)
        label = "Yes" if (src, dst) == ("decision", "recover") else None
        add_arrow(ax, start, end, label=label, label_offset=(0.25, 0.0))

    dec_x, dec_y, _ = nodes["decision"]
    fail_x, fail_y, _ = nodes["fail"]
    add_arrow(
        ax,
        (dec_x + 2.3, dec_y - 0.1),
        (fail_x - 1.2, fail_y + 0.3),
        label="No",
        label_offset=(0.2, 0.35),
    )

    ax.set_xlim(0, 11.2)
    ax.set_ylim(-0.5, 12.2)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.set_title(
        "Efficiency Analysis  —  LP Pipeline Flowchart",
        fontsize=12,
        color=TEXT_COLOR,
        pad=10,
    )

    legend_handles = [
        mpatches.Patch(
            facecolor=TERMINAL_FACECOLOR, edgecolor=TERMINAL_EDGECOLOR, label="Start / End"
        ),
        mpatches.Patch(
            facecolor=NODE_FACECOLOR, edgecolor=NODE_EDGECOLOR, label="Process step"
        ),
        mpatches.Patch(
            facecolor=DECISION_FACECOLOR,
            edgecolor=DECISION_EDGECOLOR,
            label="Decision",
        ),
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower left",
        frameon=True,
        fontsize=8.5,
        bbox_to_anchor=(0.0, 0.0),
    )

    FIGURES_DIR.mkdir(exist_ok=True)
    out_path = FIGURES_DIR / "pipeline_flowchart.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
