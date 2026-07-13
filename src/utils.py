import os
import logging

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

def print_heading(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ==========================================
# Success Message
# ==========================================

def success(message):
    logger.info(message)


# ==========================================
# Error Message
# ==========================================

def error(message):
    logger.error(message)


# ==========================================
# Data Path
# ==========================================

def get_data_path(filename):
    return os.path.join("data", filename)