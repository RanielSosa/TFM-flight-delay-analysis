from config.paths import (
    DATA_DIR,
    RAW_DIR,
    FLIGHTS_DIR,
    PROCESSED_DIR,
    PROCESSED_FLIGHTS_DIR,
    REJECTED_DIR,
    INFERENCE_INPUT_DIR,
    INFERENCE_OUTPUT_DIR,
    NOTEBOOKS_DIR,
    SRC_DIR,
    MODELS_DIR,
    DASHBOARD_DIR,
    DOCS_DIR,
    SQL_DIR,
    LOGS_DIR,
    CONFIG_DIR,
)

DIRECTORIES = [
    DATA_DIR,
    RAW_DIR,
    FLIGHTS_DIR,
    PROCESSED_DIR,
    PROCESSED_FLIGHTS_DIR,
    REJECTED_DIR,
    INFERENCE_INPUT_DIR,
    INFERENCE_OUTPUT_DIR,
    NOTEBOOKS_DIR,
    SRC_DIR,
    MODELS_DIR,
    DASHBOARD_DIR,
    DOCS_DIR,
    SQL_DIR,
    LOGS_DIR,
    CONFIG_DIR,
]

for directory in DIRECTORIES:
    directory.mkdir(
        parents=True,
        exist_ok=True
    )

print("Estructura del proyecto creada.")