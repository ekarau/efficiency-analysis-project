"""Render figures from a fitted efficiency model.

Produces two PNGs under ``figures/``:

1. ``<dataset>_frontier.png`` — DEA-style scatter of Y_observed vs Y_optimal
   with a 45-degree frontier line.
2. ``<dataset>_kpi_bars.png`` — Per-firm KPI bar chart with an efficiency
   threshold reference at 1.0.

Run from the project root:
    python scripts/visualize_results.py
    python scripts/visualize_results.py --dataset data/lecture_example.csv
"""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import EfficiencyModel, load_dataset  # noqa: E402


DEFAULT_DATASET = PROJECT_ROOT / "data" / "synthetic_dataset.csv"
FIGURES_DIR = PROJECT_ROOT / "figures"

EFFICIENT_COLOR = "#2980b9"
INEFFICIENT_COLOR = "#e67e22"
FRONTIER_COLOR = "#34495e"


def plot_frontier(summary, params, dataset_stem: str, save_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    eff = summary["status"] == "efficient"

    ax.scatter(
        summary.loc[eff, "Y_optimal"],
        summary.loc[eff, "Y_observed"],
        c=EFFICIENT_COLOR,
        s=90,
        label=f"Efficient ({int(eff.sum())})",
        edgecolors="black",
        linewidth=0.8,
        zorder=3,
    )
    ax.scatter(
        summary.loc[~eff, "Y_optimal"],
        summary.loc[~eff, "Y_observed"],
        c=INEFFICIENT_COLOR,
        s=90,
        label=f"Inefficient ({int((~eff).sum())})",
        edgecolors="black",
        linewidth=0.8,
        zorder=3,
    )

    lim = max(summary["Y_optimal"].max(), summary["Y_observed"].max()) * 1.05
    ax.plot(
        [0, lim],
        [0, lim],
        "--",
        color=FRONTIER_COLOR,
        linewidth=1.4,
        label="Frontier (Y_observed = Y_optimal)",
        zorder=2,
    )

    alpha_repr = ", ".join(
        f"{r.parameter.split('(')[-1].rstrip(')')}={r.value:.3f}"
        for r in params.itertuples()
        if r.parameter.startswith("alpha")
    )
    k_value = float(params.loc[params["parameter"] == "K", "value"].iloc[0])
    subtitle = f"K={k_value:.3f},  {alpha_repr}"

    ax.set_xlabel("Y_optimal  (estimated frontier output)")
    ax.set_ylabel("Y_observed  (actual output)")
    ax.set_title(f"Efficiency Frontier — {dataset_stem}\n{subtitle}", fontsize=11)
    ax.legend(loc="lower right", frameon=True)
    ax.grid(True, alpha=0.3, zorder=0)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_aspect("equal", adjustable="box")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_kpi_bars(summary, dataset_stem: str, save_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    eff = summary["status"] == "efficient"
    colors = [EFFICIENT_COLOR if e else INEFFICIENT_COLOR for e in eff]

    ax.bar(
        summary["firm_id"].astype(str),
        summary["KPI"],
        color=colors,
        edgecolor="black",
        linewidth=0.5,
        zorder=3,
    )
    ax.axhline(
        1.0,
        linestyle="--",
        color=FRONTIER_COLOR,
        linewidth=1,
        alpha=0.7,
        label="Efficient threshold (KPI = 1)",
        zorder=2,
    )

    ax.set_xlabel("Firm")
    ax.set_ylabel("KPI = Y_observed / Y_optimal")
    ax.set_title(f"Per-firm Efficiency Score — {dataset_stem}", fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.legend(loc="lower right", frameon=True)
    ax.grid(True, axis="y", alpha=0.3, zorder=0)

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()

    X, Y, firm_ids, input_names = load_dataset(args.dataset)
    model = EfficiencyModel()
    model.fit(X, Y, firm_ids=firm_ids, input_names=input_names)

    summary = model.summary_table()
    params = model.parameters_table()

    FIGURES_DIR.mkdir(exist_ok=True)
    stem = args.dataset.stem
    frontier_path = FIGURES_DIR / f"{stem}_frontier.png"
    kpi_path = FIGURES_DIR / f"{stem}_kpi_bars.png"

    plot_frontier(summary, params, stem, frontier_path)
    plot_kpi_bars(summary, stem, kpi_path)

    print(f"Wrote {frontier_path}")
    print(f"Wrote {kpi_path}")


if __name__ == "__main__":
    main()
