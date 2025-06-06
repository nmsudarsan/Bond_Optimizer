from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_XLS = BASE_DIR / "data" / "Candidate Optimizer Project.xlsx"

SECTOR_BOUNDS = {
    'TSY':        (0.10, 1.00),
    'ABS':        (0.00, 0.20),
    'MBS':        (0.00, 0.40),
    'Corp':       (0.00, 0.50),
    'High Yield': (0.00, 0.05),
}

DURATION_BOUNDS = (2, 8)        # years
MIN_SAME_DAY    = 0.20          # 20 %
MAX_RATING_NUM  = 5             # ≤ 5  ⇒ ≥ A+
