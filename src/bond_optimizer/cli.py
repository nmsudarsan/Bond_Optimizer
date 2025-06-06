# clip.py
# Command-line interface for running the bond optimizer and exporting results.

import argparse
from pathlib import Path
import pandas as pd

from .config import DEFAULT_XLS
from .data_io import load_assets
from .model import build_and_solve
from .scenario import run_scenarios


def main():
    # Set up argument parser for CLI options
    ap = argparse.ArgumentParser(description="Bond Optimizer CLI")
    ap.add_argument(
        "--xls", default=None,
        help="Path to input Excel workbook containing asset data"
    )
    ap.add_argument(
        "--out", default="optimized_portfolio.xlsx",
        help="Filename for exported results"
    )
    ap.add_argument(
        "--scenario", action="store_true",
        help="Run additional ±100 basis point yield shock scenarios"
    )
    args = ap.parse_args()

    # ------------------------------------------------------------------
    # 1. Resolve workbook path (flag overrides default location)
    # ------------------------------------------------------------------
    xls_path = Path(args.xls) if args.xls else DEFAULT_XLS
    if not xls_path.exists():
        raise SystemExit(f"Workbook not found: {xls_path}")

    # ------------------------------------------------------------------
    # 2. Load data and solve base optimization
    # ------------------------------------------------------------------
    df = load_assets(xls_path)              # Read and preprocess asset data
    weights, diag = build_and_solve(df)     # Run optimization
    df["optimal_weight"] = weights         # Attach optimal weights to DataFrame
    print("Base solution:", diag)           # Print diagnostic metrics to console

    # ------------------------------------------------------------------
    # 3. Optional: Run ±100 bp yield shock scenarios if requested
    # ------------------------------------------------------------------
    if args.scenario:
        scen = run_scenarios(df)            # Execute scenario sweep
        print("Scenarios:", scen)          # Display summarized diagnostics for each scenario

    # ------------------------------------------------------------------
    # 4. Export results to an Excel file
    # ------------------------------------------------------------------
    with pd.ExcelWriter(args.out) as wr:
        df.to_excel(wr, sheet_name="Optimal Weights", index=False)
    print("Saved", args.out)                # Notify user of successful export


if __name__ == "__main__":
    main()
