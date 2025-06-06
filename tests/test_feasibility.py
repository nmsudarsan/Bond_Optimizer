# test_feasibility.py
# Pytest suite to validate feasibility of the optimized bond portfolio against baseline constraints

import numpy as np
import pytest
from bond_optimizer.data_io import load_assets
from bond_optimizer.model import build_and_solve
from bond_optimizer.config import SECTOR_BOUNDS, MIN_SAME_DAY


@pytest.fixture(scope="module")
def solved():
    """
    Fixture to run the optimization once per test module.
    Loads default asset data, solves the optimization, and returns the dataframe and weights.
    """
    df = load_assets()            # Load sample asset universe
    w, d = build_and_solve(df)   # Solve for optimal weights (ignoring diagnostics here)
    return df, w


def test_weights_sum_to_one(solved):
    """
    Verify that the sum of all asset weights in the portfolio equals 1 (full allocation).
    """
    df, w = solved
    total_weight = np.sum(w)
    # Allow tiny numerical tolerance when checking sum-to-one constraint
    assert abs(total_weight - 1) < 1e-8, f"Total weight {total_weight} is not ~1"


def test_same_day_liquidity(solved):
    """
    Ensure that the allocation to "Same Day" liquidity assets meets the minimum threshold.
    """
    df, w = solved
    # Sum weights for assets labeled as "Same Day" liquidity
    same_day_weight = w[df['liquidity_label'] == "Same Day"].sum()

    # Confirm that we meet or exceed the configured minimum
    assert same_day_weight >= MIN_SAME_DAY - 1e-6, \
        f"Allocated {same_day_weight}, but minimum required is {MIN_SAME_DAY}"


def test_sector_caps(solved):
    """
    Check that the total weight per sector stays within configured lower and upper bounds.
    """
    df, w = solved
    for sector, (lo, hi) in SECTOR_BOUNDS.items():
        # Compute total weight for all assets in this sector
        sector_weight = w[df['sector'] == sector].sum()

        # Assert total weight does not exceed upper bound
        assert sector_weight <= hi + 1e-6, \
            f"Sector {sector} weight {sector_weight} exceeds upper cap {hi}"

        # Assert total weight is not below lower bound
        assert sector_weight >= lo - 1e-6, \
            f"Sector {sector} weight {sector_weight} falls below lower bound {lo}"
