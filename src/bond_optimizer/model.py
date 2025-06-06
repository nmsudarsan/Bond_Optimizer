# src/bond_optimizer/model.py
# Core optimization logic for constructing a bond portfolio given various constraints.

import cvxpy as cp
import numpy as np
from .config import SECTOR_BOUNDS, DURATION_BOUNDS, MIN_SAME_DAY, MAX_RATING_NUM


def build_and_solve(
    df,
    sector_bounds: dict = None,
    duration_bounds: tuple = None,
    solver: str = "ECOS"
):
    """
    Solve the bond-portfolio optimization problem using CVXPY.

    Parameters
    ----------
    df : pandas.DataFrame
        Asset-level data, containing required columns:
          - 'yield'
          - 'duration'
          - 'quality_num'
          - 'asset_level_min_weight'
          - 'asset_level_max_weight'
          - 'sector'
          - 'liquidity_label'

    sector_bounds : dict, optional
        Overrides default SECTOR_BOUNDS when provided. Format: {sector_name: (min_cap, max_cap)}.

    duration_bounds : tuple, optional
        Overrides default DURATION_BOUNDS when provided. Format: (min_duration, max_duration).

    solver : str, default "ECOS"
        Name of the CVXPY solver to apply (e.g. "ECOS", "SCS", "OSQP", "CVXOPT").

    Returns
    -------
    weights : numpy.ndarray
        Optimal portfolio weight vector (length equals row count of df).

    diag : dict
        Diagnostics including:
          - 'yield_'     : float, computed portfolio yield
          - 'duration'   : float, computed portfolio duration
          - 'rating_num' : float, average quality rating numeric
    """
    # 1) Choose bounds: user-provided overrides take precedence over defaults
    effective_sector = sector_bounds if sector_bounds is not None else SECTOR_BOUNDS
    effective_duration = duration_bounds if duration_bounds is not None else DURATION_BOUNDS

    # 2) Extract relevant numpy arrays from DataFrame for vectorized computations
    y = df['yield'].values                    # yield per bond
    dur = df['duration'].values               # duration per bond
    qnum = df['quality_num'].values           # numeric credit rating per bond
    liq = df['liquidity_label'].values        # liquidity label per bond
    wmin = df['asset_level_min_weight'].values  # per-asset minimum weight
    wmax = df['asset_level_max_weight'].values  # per-asset maximum weight
    sect = df['sector'].values                # sector label per bond
    same_day_mask = (liq == "Same Day")      # boolean mask for 'Same Day' liquidity

    n = len(df)                               # number of assets
    w = cp.Variable(n)                        # decision variable: weight for each asset

    # 3) Base constraints list
    constraints = [
        w >= wmin,                           # enforce asset-level minimum weight
        w <= wmax,                           # enforce asset-level maximum weight
        cp.sum(w) == 1,                      # full allocation constraint (weights sum to 1)
        dur @ w >= effective_duration[0],    # portfolio duration ≥ minimum duration
        dur @ w <= effective_duration[1],    # portfolio duration ≤ maximum duration
        qnum @ w <= MAX_RATING_NUM,         # average credit rating numeric ≤ maximum allowed
        cp.sum(w[same_day_mask]) >= MIN_SAME_DAY  # enforce minimum allocation to 'Same Day' liquidity
    ]

    # 4) Add sector-level constraints (each sector has its own lower/upper bounds)
    for s, (lo, hi) in effective_sector.items():
        mask = (sect == s)  # boolean mask for assets belonging to sector 's'
        if lo > 0:
            constraints.append(cp.sum(w[mask]) >= lo)  # enforce sector minimum if specified
        constraints.append(cp.sum(w[mask]) <= hi)      # enforce sector maximum

    # 5) Define objective: maximize total portfolio yield
    objective = cp.Maximize(y @ w)
    prob = cp.Problem(objective, constraints)

    # Dynamically select solver based on string name (e.g., cp.ECOS)
    chosen_solver = getattr(cp, solver)
    prob.solve(solver=chosen_solver)

    # 6) Extract solution: weight vector and key diagnostics
    weights = np.array(w.value).round(10)  # round weights for numerical stability
    diag = {
        'yield_': float(y @ weights),
        'duration': float(dur @ weights),
        'rating_num': float(qnum @ weights)
    }

    return weights, diag
