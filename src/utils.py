import os
import logging
from pathlib import Path

# ==========================================
# Logging Configuration
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================
# Normalize Score
# ==========================================

def normalize_score(score):
    return max(0, min(score, 100))


# ==========================================
# Percentage Format
# ==========================================

def percentage(score):
    return f"{score:.2f}%"


# ==========================================
# Headings
# ==========================================
def success(message):
    print(f"[SUCCESS] {message}")


def error(message):
    print(f"[ERROR] {message}")
def print_heading(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_data_path(filename):
    return PROJECT_ROOT / "data" / filename

