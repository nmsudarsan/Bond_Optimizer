
# Bond Portfolio Optimizer

A Streamlit-based web application and command-line tool to construct an optimal bond portfolio based on yield maximization while respecting constraints on duration, sector exposure, liquidity, and credit quality.

##  Features

- **Interactive Streamlit App**: Upload your Excel workbook, adjust sector caps and duration bands, and run optimization in real-time.
- **CVXPY Solver**: Linear programming under the hood to maximize portfolio yield.
- **Sector and Duration Constraints**: Enforced using sliders or config file overrides.
- **Liquidity Floor & Rating Controls**: Ensure minimum liquidity and credit quality.
- **CLI Tool**: Run optimization and stress scenarios (+/-100bps) from the command line.
- **Tests**: Includes feasibility and scenario-based validation via `pytest`.

---

##  Project Structure

```
BOND_OPTIMIZER/
├── notebooks/                  # (Optional) for experiments and analysis
├── src/
│   └── bond_optimizer/
│       ├── __init__.py
│       ├── cli.py             # Command-line interface script
│       ├── config.py          # Default bounds and parameters
│       ├── data_io.py         # Data loading and preprocessing
│       ├── model.py           # Core optimization logic (CVXPY)
│       ├── scenario.py        # Yield bump stress testing
├── data/
│   └── Candidate Optimizer Project.xlsx  # Sample data workbook
├── tests/
│   ├── test_feasibility.py    # Unit tests for constraint satisfaction
│   ├── test_scenarios.py      # Tests for scenario performance
├── streamlit_app.py           # UI for web-based usage
├── optimized_portfolio.xlsx   # Output Excel file (generated)
├── pyproject.toml             # Project metadata
├── requirements.txt           # Dependencies
├── .gitignore                 # Files and folders to exclude from Git
└── README.md                  # Project overview (this file)
```

---

##  Optimization Overview

The objective is to **maximize portfolio yield** subject to constraints:

- Full allocation (`sum(weights) == 1`)
- Asset-level min/max weights
- Sector-level min/max caps
- Duration range (`2 to 8 years`, customizable)
- Liquidity minimum (e.g. ≥ 20% in "Same Day")
- Average credit rating numeric (≤ A+)

---

##  Streamlit App Usage

### 🔧Launch

```bash
streamlit run streamlit_app.py
```

###  Features

- Upload or use default Excel workbook
- Customize sector caps (0–100%)
- Adjust duration range (1–20 yrs)
- View optimized weights and sector pie chart

---

## 🖥 CLI Usage

Run from terminal:

```bash
python -m bond_optimizer.cli --xls path/to/your_data.xlsx --out result.xlsx --scenario
```

### Flags

- `--xls`: Path to input Excel file
- `--out`: Filename for optimized output (default: optimized_portfolio.xlsx)
- `--scenario`: Also run +/-100bps yield shift simulations

---

##  Running Tests

Install pytest and run tests:

```bash
pip install -r requirements.txt
pytest tests/
```

---

##  Excel Format Requirements

The input workbook must contain:

**Sheet 1**: Sample Data  
Columns: `asset`, `sector`, `yield`, `duration`, `quality`, `liquidity_tier`, `asset_level_min_weight`, `asset_level_max_weight`

**Sheet 2**: Data Key  
Columns:  
- A/B: Credit Quality, Numeric  
- D/E: Liquidity Tier, Translation  

---

##  Installation

```bash
# Clone repo
git clone https://github.com/your-username/bond-optimizer.git
cd bond-optimizer

# Create environment (optional)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

---

##  Technologies Used

- Python 3.8+
- Streamlit – UI
- CVXPY – Convex optimization
- Pandas / NumPy – Data processing
- Pytest – Testing framework

---

##  Author

**Sudarsan Nallur Murali**  
 nmsudarsan@gmail.edu

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 💡 Future Enhancements

- Constraint toggling (e.g., optional sector exclusions)
- Support for stochastic scenarios
- Enhanced dashboard visualizations
- PDF export of optimization summary
