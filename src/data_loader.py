from pathlib import Path

import numpy as np
import pandas as pd


def load_dataset(csv_path: str | Path) -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
    """Load a firms-inputs-output dataset from a CSV file.

    Expected schema:
        - One column named `firm_id` (string or int identifier).
        - One or more input columns named `X1`, `X2`, ... `XM`.
        - One output column named `Y_observed`.

    Returns
    -------
    X : np.ndarray, shape (J, M)
        Input matrix (J firms, M inputs).
    Y : np.ndarray, shape (J,)
        Observed output vector.
    firm_ids : list[str]
        Firm identifiers in the same order as rows of X / Y.
    input_names : list[str]
        Input column names (e.g. ["X1", "X2"]).
    """
    df = pd.read_csv(csv_path)

    if "firm_id" not in df.columns:
        raise ValueError("CSV must contain a 'firm_id' column.")
    if "Y_observed" not in df.columns:
        raise ValueError("CSV must contain a 'Y_observed' column.")

    input_cols = [c for c in df.columns if c.startswith("X")]
    if not input_cols:
        raise ValueError("CSV must contain at least one input column (X1, X2, ...).")

    X = df[input_cols].to_numpy(dtype=float)
    Y = df["Y_observed"].to_numpy(dtype=float)

    if (X <= 0).any():
        raise ValueError("All inputs must be strictly positive (logarithm is taken).")
    if (Y <= 0).any():
        raise ValueError("All outputs must be strictly positive (logarithm is taken).")

    firm_ids = df["firm_id"].astype(str).tolist()
    return X, Y, firm_ids, input_cols
