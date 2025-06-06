# scenario.py
# Functions to apply yield shocks and run multiple optimization scenarios for comparison

import numpy as np
from .model import build_and_solve


def bump_yields(df, bp=100):
    """
    Create a new DataFrame with yields bumped by a specified number of basis points (bps).

    Parameters:
    - df: pandas.DataFrame containing the bond asset data, including a 'yield' column.
    - bp: integer, number of basis points to shift the yield (e.g., +100 for +1%).

    Returns:
    - bumped: new DataFrame copy with adjusted 'yield' values.
    """
    bumped = df.copy()  # Shallow copy to avoid mutating original DataFrame
    # Convert basis points to decimal and add to existing yield
    bumped['yield'] = bumped['yield'] + bp / 10000
    return bumped


def run_scenarios(df, bps=[-100, 0, 100]):
    """
    Run the optimizer under multiple yield shock scenarios and collect diagnostics.

    Parameters:
    - df: pandas.DataFrame of the base asset universe.
    - bps: list of integers representing yield shocks in basis points to test (e.g., [-100, 0, +100]).

    Returns:
    - out: dict mapping scenario label (e.g., '+100bp') to the diagnostics output from build_and_solve.
    """
    out = {}
    for shock in bps:
        # Apply the yield shock to a fresh copy of the DataFrame
        _df = bump_yields(df, shock)
        # Solve the optimization for the bumped yields
        w, d = build_and_solve(_df)
        # Store only the diagnostic summary (e.g., total yield, duration) keyed by shock label
        out[f"{shock:+}bp"] = d
    return out
