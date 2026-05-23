"""Entry point for the Performance Optimization homework.

Usage:
    python main.py                                  # runs on data/lecture_example.csv
    python main.py --dataset path/to/other.csv      # runs on a custom dataset
    python main.py --save                           # also writes results to output/
"""
import argparse
from pathlib import Path

import pandas as pd

from src import EfficiencyModel, load_dataset


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = PROJECT_ROOT / "data" / "lecture_example.csv"
OUTPUT_DIR = PROJECT_ROOT / "output"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to a CSV file with columns firm_id, X1, X2, ..., Y_observed.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Persist the summary and parameters as CSVs under output/.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(f"Loading dataset: {args.dataset}")
    X, Y, firm_ids, input_names = load_dataset(args.dataset)
    print(f"  {len(firm_ids)} firms, {len(input_names)} inputs ({', '.join(input_names)})\n")

    model = EfficiencyModel()
    model.fit(X, Y, firm_ids=firm_ids, input_names=input_names)

    params = model.parameters_table()
    summary = model.summary_table()

    pd.set_option("display.float_format", lambda v: f"{v:0.4f}")
    print("Estimated production-function parameters")
    print("-" * 42)
    print(params.to_string(index=False))
    print()

    print("Per-firm efficiency report")
    print("-" * 42)
    print(summary.to_string(index=False))
    print()

    n_efficient = int(summary["status"].eq("efficient").sum())
    print(f"Efficient firms: {n_efficient} / {len(summary)}")

    if args.save:
        OUTPUT_DIR.mkdir(exist_ok=True)
        params_path = OUTPUT_DIR / f"{args.dataset.stem}_parameters.csv"
        summary_path = OUTPUT_DIR / f"{args.dataset.stem}_summary.csv"
        params.to_csv(params_path, index=False)
        summary.to_csv(summary_path, index=False)
        print(f"\nSaved parameters to {params_path}")
        print(f"Saved summary    to {summary_path}")


if __name__ == "__main__":
    main()
