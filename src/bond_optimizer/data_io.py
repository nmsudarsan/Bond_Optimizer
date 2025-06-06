# data_io.py
# Functions for loading and preprocessing bond asset data from an Excel source.

import pandas as pd
from .config import DEFAULT_XLS


def load_assets(xls_path=DEFAULT_XLS):
    """
    Load bond asset data from the specified Excel file and augment with numeric quality and liquidity labels.

    Parameters
    ----------
    xls_path : str, optional
        Path to the Excel workbook containing asset data. Defaults to DEFAULT_XLS from configuration.

    Returns
    -------
    df : pandas.DataFrame
        Asset-level DataFrame with normalized column names, plus two new columns:
        - 'quality_num': numeric representation of credit quality
        - 'liquidity_label': human-readable liquidity category
    """
    # Read the main "Sample Data" sheet into a DataFrame
    df = pd.read_excel(xls_path, sheet_name='Sample Data')

    # Normalize column names to lowercase with underscores, removing extra spaces
    df.columns = (
        df.columns
          .str.strip()            # trim leading/trailing whitespace
          .str.lower()            # convert to lowercase
          .str.replace(' ', '_')  # replace spaces between words with underscores
    )

    # ---------- Map credit quality to numeric values ----------
    # Load the "Data Key" sheet to get mapping of credit quality strings to numeric scores
    df_credit = pd.read_excel(
        xls_path,
        sheet_name='Data Key',
        skiprows=1,           # skip header row describing columns
        usecols='A:B'         # only read Credit Quality and Numeric columns
    ).dropna(how='all')      # drop rows that are completely empty

    # Build a dictionary: { 'AAA': 1, 'AA': 2, ... }
    qmap = dict(zip(df_credit['Credit Quality'], df_credit['Numeric']))
    # Map the textual 'quality' column from main sheet to its numeric equivalent
    df['quality_num'] = df['quality'].map(qmap)

    # ---------- Map liquidity tier codes to human-readable labels ----------
    # Again, load "Data Key" sheet to get mapping for liquidity tiers
    df_liq = pd.read_excel(
        xls_path,
        sheet_name='Data Key',
        skiprows=1,           # skip the header row
        usecols='D:E'         # read Liquidity Tier and its Translation columns
    ).dropna(how='all')      # drop completely empty rows

    # Build a dictionary: { 1: 'Same Day', 2: 'Next Day', ... }
    lmap = dict(zip(df_liq['Liquidity Tier'], df_liq['Translation']))
    # Map the numeric 'liquidity_tier' column to a descriptive 'liquidity_label'
    df['liquidity_label'] = df['liquidity_tier'].map(lmap)

    return df
