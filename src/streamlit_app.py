# streamlit_app.py
# Streamlit web app to optimize a bond portfolio based on adjustable sector and duration constraints.

import streamlit as st
import pandas as pd
import numpy as np
import copy

from bond_optimizer.data_io import load_assets
from bond_optimizer.model import build_and_solve
from bond_optimizer.config import SECTOR_BOUNDS, DURATION_BOUNDS

# Immutable copies of default configuration bounds to ensure slider ranges remain constant
ORIGINAL_SECTOR_BOUNDS = copy.deepcopy(SECTOR_BOUNDS)
ORIGINAL_DURATION_BOUNDS = tuple(DURATION_BOUNDS)

# ── Sidebar Configuration: File Upload and Parameter Sliders ───────────────────────────────────────────
st.sidebar.title("⚙️  Settings")

# File uploader widget for user-provided Excel workbook; defaults if none uploaded
xls_file = st.sidebar.file_uploader(
    "Excel workbook",
    type=["xlsx"],
    help="If blank, falls back to default sample"
)

# Load asset data from uploaded Excel workbook or default embedded dataset
if xls_file:
    df_assets = load_assets(xls_file)
else:
    df_assets = load_assets()

# Sidebar sliders for adjusting maximum allowed weight for each sector
st.sidebar.subheader("Sector caps (0 to 1)")
caps_user = {}
for sec, (lo, hi) in ORIGINAL_SECTOR_BOUNDS.items():
    # Slider range fixed at 0.0–1.0; default thumb set to original sector upper bound
    caps_user[sec] = st.sidebar.slider(
        sec,
        min_value=0.0,
        max_value=1.0,
        value=hi,
        step=0.05,
        format="%.2f"
    )

# Sidebar slider to adjust the duration band (minimum and maximum duration in years)
st.sidebar.subheader("Duration band (yrs)")
dur_min, dur_max = st.sidebar.slider(
    "Duration band (yrs)",
    min_value=1.0,                   # Lower bound set to 1 year
    max_value=20.0,                  # Upper bound set to 20 years
    value=(
        float(ORIGINAL_DURATION_BOUNDS[0]),  # Default lower bound (originally 2 years)
        float(ORIGINAL_DURATION_BOUNDS[1])   # Default upper bound (originally 8 years)
    ),
    step=0.5
)

# ── Main Panel: Portfolio Optimization Execution ───────────────────────────────────────
st.title("Bond Portfolio Optimizer")

# Execute optimization logic when "Optimize" button is pressed
if st.button("🚀 Optimize"):
    # Define override dictionaries for sector and duration based on user input
    override_sector = {sec: (0.0, caps_user[sec]) for sec in caps_user}
    override_duration = (dur_min, dur_max)

    # Call the optimization solver with user-defined parameters
    w_opt, diag = build_and_solve(
        df_assets,
        sector_bounds=override_sector,
        duration_bounds=override_duration,
        solver="ECOS"  # Solver can be replaced with "SCS", "OSQP", etc.
    )

    # Assign optimal weights back to asset dataframe
    df_assets['weight'] = w_opt

    # Display portfolio key performance indicators (KPIs)
    st.success(
        f"Portfolio yield {diag['yield_']:,.2f}%  "
        f"duration {diag['duration']:.2f} yrs  "
        f"avg rating num {diag['rating_num']:.2f}"
    )

    # Display asset-level details in a DataFrame
    st.dataframe(
        df_assets[['asset', 'sector', 'yield', 'duration', 'weight']].round(4)
    )

    # Generate and display pie chart for sector allocation
    sect = (
        df_assets
        .groupby('sector')['weight']
        .sum()
        .sort_values(ascending=False)
    )

    st.subheader("Sector allocation")
    st.pyplot(
        sect.plot(
            kind='pie',
            autopct='%1.1f%%',
            ylabel='',
            figsize=(4, 4)
        ).figure
    )

else:
    # Informative message prompting user action
    st.info("Select parameters on the left, then hit **Optimize**")
