from pathlib import Path

PROJECT_ROOT = Path(
    r"G:\My Drive\MASTER Big Data\TFM"
)

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
FLIGHTS_DIR = RAW_DIR / "Flights"

PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_FLIGHTS_DIR = (
    PROCESSED_DIR / "flights"
)

REJECTED_DIR = DATA_DIR / "rejected"

INFERENCE_DIR = DATA_DIR / "inference"
INFERENCE_INPUT_DIR = (
    INFERENCE_DIR / "input"
)
INFERENCE_OUTPUT_DIR = (
    INFERENCE_DIR / "output"
)

NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
SRC_DIR = PROJECT_ROOT / "src"
MODELS_DIR = PROJECT_ROOT / "models"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
DOCS_DIR = PROJECT_ROOT / "docs"
SQL_DIR = PROJECT_ROOT / "sql"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIG_DIR = PROJECT_ROOT / "config"