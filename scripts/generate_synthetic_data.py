"""Generate a synthetic firms-inputs-output dataset for benchmarking.

The dataset is fully reproducible (fixed RNG seed) and follows the Cobb-Douglas
production form used in the homework:

    Y_optimal = K_TRUE * X1^ALPHA_TRUE[0] * X2^ALPHA_TRUE[1]

A configurable share of firms are placed on the frontier (efficient,
Y_observed == Y_optimal); the rest receive a random efficiency factor in
[0.55, 0.95] (inefficient).

Run from the project root:
    python scripts/generate_synthetic_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 42
N_FIRMS = 20
EFFICIENT_SHARE = 0.5
K_TRUE = 2.0
ALPHA_TRUE = np.array([0.4, 0.6])
INPUT_RANGE = (5.0, 50.0)
INEFFICIENCY_RANGE = (0.55, 0.95)

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "synthetic_dataset.csv"


def main() -> None:
    rng = np.random.default_rng(SEED)

    X = rng.uniform(low=INPUT_RANGE[0], high=INPUT_RANGE[1], size=(N_FIRMS, 2))
    X = X.round(2)

    y_optimal = K_TRUE * np.prod(X ** ALPHA_TRUE, axis=1)

    n_efficient = int(round(N_FIRMS * EFFICIENT_SHARE))
    is_efficient = np.zeros(N_FIRMS, dtype=bool)
    is_efficient[:n_efficient] = True
    rng.shuffle(is_efficient)

    efficiency_factor = rng.uniform(
        low=INEFFICIENCY_RANGE[0], high=INEFFICIENCY_RANGE[1], size=N_FIRMS
    )
    efficiency_factor[is_efficient] = 1.0

    y_observed = (y_optimal * efficiency_factor).round(4)

    df = pd.DataFrame(
        {
            "firm_id": [f"firm_{i + 1:02d}" for i in range(N_FIRMS)],
            "X1": X[:, 0],
            "X2": X[:, 1],
            "Y_observed": y_observed,
        }
    )

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    designed_efficient = int(is_efficient.sum())
    print(f"Wrote {len(df)} firms to {OUTPUT_PATH}")
    print(
        f"Ground-truth parameters: K={K_TRUE}, "
        f"alpha=({ALPHA_TRUE[0]}, {ALPHA_TRUE[1]})"
    )
    print(
        f"Designed efficient firms: {designed_efficient}/{N_FIRMS} "
        f"(seed={SEED})"
    )


if __name__ == "__main__":
    main()
