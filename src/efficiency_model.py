"""Performance Optimization via the Cobb-Douglas production frontier.

Model (multiple inputs, single output):

    Y_optimal_j = K * X1j^alpha_1 * X2j^alpha_2 * ... * XMj^alpha_M

Taking the natural logarithm and introducing a non-negative slack D_j:

    ln(Y_observed_j) + D_j = ln(K) + sum_i alpha_i * ln(X_ij)

We estimate (K, alpha_1, ..., alpha_M) by solving the LP:

    min   sum_j D_j
    s.t.  D_j = [ln(K) + sum_i alpha_i * ln(X_ij)] - ln(Y_observed_j)   for all j
          D_j >= 0
          alpha_i >= 0
          ln(K) is free (then K = exp(ln(K)))

A firm j is efficient when D_j = 0 and inefficient when D_j > 0.
KPI_j = Y_observed_j / Y_optimal_j in [0, 1].
"""
from dataclasses import dataclass

import numpy as np
import pulp


@dataclass
class EfficiencyResult:
    K: float
    alphas: np.ndarray
    deviations: np.ndarray
    y_optimal: np.ndarray
    y_observed: np.ndarray
    kpi: np.ndarray
    is_efficient: np.ndarray
    firm_ids: list[str]
    input_names: list[str]


class EfficiencyModel:
    """Fits a Cobb-Douglas production frontier via linear programming."""

    EFFICIENCY_TOL = 1e-3

    def __init__(self, solver: pulp.LpSolver | None = None):
        self._solver = solver or pulp.PULP_CBC_CMD(msg=False)
        self.result_: EfficiencyResult | None = None

    def fit(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        firm_ids: list[str] | None = None,
        input_names: list[str] | None = None,
    ) -> EfficiencyResult:
        if X.ndim != 2:
            raise ValueError("X must be a 2D array (J firms x M inputs).")
        if Y.ndim != 1:
            raise ValueError("Y must be a 1D array of length J.")
        if X.shape[0] != Y.shape[0]:
            raise ValueError("X and Y must agree on the number of firms.")

        n_firms, n_inputs = X.shape
        firm_ids = firm_ids or [str(i + 1) for i in range(n_firms)]
        input_names = input_names or [f"X{i + 1}" for i in range(n_inputs)]

        ln_X = np.log(X)
        ln_Y = np.log(Y)

        prob = pulp.LpProblem("efficiency_frontier", pulp.LpMinimize)

        ln_K = pulp.LpVariable("ln_K", lowBound=None)
        alphas = [
            pulp.LpVariable(f"alpha_{i + 1}", lowBound=0) for i in range(n_inputs)
        ]
        deviations = [
            pulp.LpVariable(f"D_{j + 1}", lowBound=0) for j in range(n_firms)
        ]

        prob += pulp.lpSum(deviations), "minimize_total_deviation"

        for j in range(n_firms):
            rhs = ln_K + pulp.lpSum(alphas[i] * ln_X[j, i] for i in range(n_inputs))
            prob += deviations[j] == rhs - ln_Y[j], f"frontier_eq_firm_{j + 1}"

        status = prob.solve(self._solver)
        if pulp.LpStatus[status] != "Optimal":
            raise RuntimeError(
                f"LP did not reach an optimal solution: {pulp.LpStatus[status]}"
            )

        K = float(np.exp(ln_K.value()))
        alpha_values = np.array([a.value() for a in alphas], dtype=float)
        d_values = np.array([d.value() for d in deviations], dtype=float)
        y_optimal = K * np.prod(X ** alpha_values, axis=1)
        kpi = Y / y_optimal
        is_efficient = d_values < self.EFFICIENCY_TOL

        self.result_ = EfficiencyResult(
            K=K,
            alphas=alpha_values,
            deviations=d_values,
            y_optimal=y_optimal,
            y_observed=Y,
            kpi=kpi,
            is_efficient=is_efficient,
            firm_ids=firm_ids,
            input_names=input_names,
        )
        return self.result_

    def summary_table(self) -> "pd.DataFrame":
        import pandas as pd

        if self.result_ is None:
            raise RuntimeError("Call fit() before summary_table().")
        r = self.result_
        return pd.DataFrame(
            {
                "firm_id": r.firm_ids,
                "Y_observed": r.y_observed,
                "Y_optimal": r.y_optimal,
                "deviation_D": r.deviations,
                "KPI": r.kpi,
                "status": np.where(r.is_efficient, "efficient", "inefficient"),
            }
        )

    def parameters_table(self) -> "pd.DataFrame":
        import pandas as pd

        if self.result_ is None:
            raise RuntimeError("Call fit() before parameters_table().")
        r = self.result_
        rows = [{"parameter": "K", "value": r.K}]
        for name, value in zip(r.input_names, r.alphas):
            rows.append({"parameter": f"alpha({name})", "value": float(value)})
        return pd.DataFrame(rows)
