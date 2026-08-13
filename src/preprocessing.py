"""
Preprocesamiento común para el dataset de vuelos del TFM.

Este módulo concentra el esquema analítico y las transformaciones que deben
aplicarse de forma idéntica a cualquier archivo histórico que ingrese al
proyecto. Separar esta lógica del notebook evita duplicación de código y
garantiza que futuras cargas utilicen exactamente las mismas reglas.

Las funciones de este módulo NO realizan transformaciones específicas de
Machine Learning. La codificación de variables categóricas, escalado, PCA y
selección de variables se realizarán en etapas posteriores del proyecto.
"""

from __future__ import annotations

import pandas as pd


# -------------------------------------------------------------------
# Esquema esperado en los CSV originales del BTS.
# Estas son las 40 columnas descargadas directamente de la fuente.
# -------------------------------------------------------------------
EXPECTED_RAW_COLUMNS = [
    "FL_DATE",
    "MKT_UNIQUE_CARRIER",
    "OP_UNIQUE_CARRIER",
    "TAIL_NUM",
    "OP_CARRIER_FL_NUM",
    "ORIGIN_AIRPORT_ID",
    "ORIGIN",
    "ORIGIN_CITY_NAME",
    "ORIGIN_STATE_ABR",
    "DEST_AIRPORT_ID",
    "DEST",
    "DEST_CITY_NAME",
    "DEST_STATE_ABR",
    "CRS_DEP_TIME",
    "DEP_TIME",
    "DEP_DELAY",
    "DEP_DELAY_NEW",
    "DEP_DEL15",
    "DEP_TIME_BLK",
    "TAXI_OUT",
    "TAXI_IN",
    "CRS_ARR_TIME",
    "ARR_TIME",
    "ARR_DELAY",
    "ARR_DELAY_NEW",
    "ARR_DEL15",
    "ARR_TIME_BLK",
    "CANCELLED",
    "CANCELLATION_CODE",
    "DIVERTED",
    "CRS_ELAPSED_TIME",
    "ACTUAL_ELAPSED_TIME",
    "AIR_TIME",
    "DISTANCE",
    "DISTANCE_GROUP",
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY",
]

DATE_COLUMN = "FL_DATE"

# Clasificación semántica de las variables.
# Se utiliza para aplicar conversiones homogéneas y documentar su naturaleza.
CATEGORICAL_COLUMNS = [
    "MKT_UNIQUE_CARRIER",
    "OP_UNIQUE_CARRIER",
    "TAIL_NUM",
    "ORIGIN",
    "ORIGIN_CITY_NAME",
    "ORIGIN_STATE_ABR",
    "DEST",
    "DEST_CITY_NAME",
    "DEST_STATE_ABR",
    "DEP_TIME_BLK",
    "ARR_TIME_BLK",
    "CANCELLATION_CODE",
]

IDENTIFIER_COLUMNS = [
    "OP_CARRIER_FL_NUM",
    "ORIGIN_AIRPORT_ID",
    "DEST_AIRPORT_ID",
]

BINARY_COLUMNS = [
    "DEP_DEL15",
    "ARR_DEL15",
    "CANCELLED",
    "DIVERTED",
]

TIME_COLUMNS = [
    "CRS_DEP_TIME",
    "DEP_TIME",
    "CRS_ARR_TIME",
    "ARR_TIME",
]

CONTINUOUS_COLUMNS = [
    "DEP_DELAY",
    "DEP_DELAY_NEW",
    "TAXI_OUT",
    "TAXI_IN",
    "ARR_DELAY",
    "ARR_DELAY_NEW",
    "CRS_ELAPSED_TIME",
    "ACTUAL_ELAPSED_TIME",
    "AIR_TIME",
    "DISTANCE",
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY",
]

ORDINAL_COLUMNS = [
    "DISTANCE_GROUP",
]


# -------------------------------------------------------------------
# Esquema analítico final.
# Se añaden cinco variables temporales derivadas de FL_DATE.
# -------------------------------------------------------------------
FINAL_COLUMN_ORDER = [
    "FL_DATE",
    "YEAR",
    "QUARTER",
    "MONTH",
    "DAY_OF_MONTH",
    "DAY_OF_WEEK",
    "MKT_UNIQUE_CARRIER",
    "OP_UNIQUE_CARRIER",
    "TAIL_NUM",
    "OP_CARRIER_FL_NUM",
    "ORIGIN_AIRPORT_ID",
    "ORIGIN",
    "ORIGIN_CITY_NAME",
    "ORIGIN_STATE_ABR",
    "DEST_AIRPORT_ID",
    "DEST",
    "DEST_CITY_NAME",
    "DEST_STATE_ABR",
    "CRS_DEP_TIME",
    "DEP_TIME",
    "DEP_DELAY",
    "DEP_DELAY_NEW",
    "DEP_DEL15",
    "DEP_TIME_BLK",
    "TAXI_OUT",
    "TAXI_IN",
    "CRS_ARR_TIME",
    "ARR_TIME",
    "ARR_DELAY",
    "ARR_DELAY_NEW",
    "ARR_DEL15",
    "ARR_TIME_BLK",
    "CANCELLED",
    "CANCELLATION_CODE",
    "DIVERTED",
    "CRS_ELAPSED_TIME",
    "ACTUAL_ELAPSED_TIME",
    "AIR_TIME",
    "DISTANCE",
    "DISTANCE_GROUP",
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY",
]


def normalize_chunk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza estructuralmente un bloque de datos de vuelos.

    Esta función representa la transformación común entre la fuente BTS y la
    capa analítica. Su objetivo es asegurar que todos los periodos históricos
    tengan exactamente la misma estructura y tipos antes de analizarse o
    almacenarse en Parquet.

    Las operaciones realizadas son:

    1. Homogeneizar nombres de columnas.
    2. Convertir ``FL_DATE`` a ``datetime64``.
    3. Derivar ``YEAR``, ``QUARTER``, ``MONTH``, ``DAY_OF_MONTH`` y
       ``DAY_OF_WEEK``.
    4. Convertir variables categóricas a ``string``.
    5. Convertir identificadores a ``Int32``.
    6. Convertir indicadores binarios a ``Int8``.
    7. Mantener horarios HHMM como ``Int16``.
    8. Convertir magnitudes continuas a ``Float32``.
    9. Convertir ``DISTANCE_GROUP`` a ``Int8``.
    10. Aplicar el orden definido en ``FINAL_COLUMN_ORDER``.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame o chunk leído desde un CSV del BTS. Debe contener las
        columnas definidas en ``EXPECTED_RAW_COLUMNS``.

    Returns
    -------
    pandas.DataFrame
        Copia normalizada con 45 columnas: 40 variables originales y
        5 variables temporales derivadas.

    Raises
    ------
    KeyError
        Si alguna columna requerida no está disponible.
    ValueError
        Puede producirse si un valor no puede representarse mediante el tipo
        nullable definido tras la conversión numérica.

    Examples
    --------
    El uso habitual dentro del pipeline es:

    >>> chunk = pd.read_csv("flights.csv", nrows=1000)
    >>> normalized = normalize_chunk(chunk)
    >>> len(normalized.columns)
    45
    >>> "YEAR" in normalized.columns
    True

    Notes
    -----
    ``DAY_OF_WEEK`` utiliza 1 para lunes y 7 para domingo.

    La función NO elimina registros, NO imputa valores faltantes y NO aplica
    transformaciones específicas de Machine Learning.
    """
    df = df.copy()

    # Homogeneizar encabezados evita diferencias por espacios o mayúsculas.
    df.columns = df.columns.str.strip().str.upper()

    # FL_DATE es la fuente temporal única; las demás variables se derivan.
    df["FL_DATE"] = pd.to_datetime(
        df["FL_DATE"],
        format="%m/%d/%Y %I:%M:%S %p",
        errors="coerce",
    )

    # Feature engineering temporal básico necesario para análisis posteriores.
    df["YEAR"] = df["FL_DATE"].dt.year.astype("Int16")
    df["QUARTER"] = df["FL_DATE"].dt.quarter.astype("Int8")
    df["MONTH"] = df["FL_DATE"].dt.month.astype("Int8")
    df["DAY_OF_MONTH"] = df["FL_DATE"].dt.day.astype("Int8")
    df["DAY_OF_WEEK"] = (df["FL_DATE"].dt.dayofweek + 1).astype("Int8")

    # Las categorías se mantienen como texto; su encoding se hará en ML.
    for column in CATEGORICAL_COLUMNS:
        df[column] = df[column].astype("string").str.strip()

    # Son códigos/identificadores, no magnitudes matemáticas.
    for column in IDENTIFIER_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int32")

    # Tipos nullable permiten conservar NA sin convertir toda la columna a float64.
    for column in BINARY_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int8")

    # Se conserva HHMM como entero. La semántica horaria se trabajará después.
    for column in TIME_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int16")

    # Float32 ofrece precisión suficiente para estas magnitudes y reduce memoria.
    for column in CONTINUOUS_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Float32")

    for column in ORDINAL_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int8")

    return df[FINAL_COLUMN_ORDER]


def clean_chunk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica las reglas generales de limpieza validadas para el histórico.

    La función se ejecuta DESPUÉS de :func:`normalize_chunk`. Mantiene
    separadas la normalización estructural y las decisiones de calidad.

    Actualmente invalida valores negativos de ``CRS_ELAPSED_TIME`` porque
    representan una duración programada físicamente no interpretable. El vuelo
    completo se conserva y únicamente se sustituye el valor problemático por
    ``pd.NA``.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame previamente normalizado mediante ``normalize_chunk()``.

    Returns
    -------
    pandas.DataFrame
        Copia limpia con el mismo número de filas que el DataFrame de entrada.

    Raises
    ------
    KeyError
        Si ``CRS_ELAPSED_TIME`` no está presente.

    Examples
    --------
    >>> data = pd.DataFrame({
    ...     "CRS_ELAPSED_TIME": pd.Series([120.0, -74.0, 95.0], dtype="Float32")
    ... })
    >>> result = clean_chunk(data)
    >>> result["CRS_ELAPSED_TIME"].isna().sum()
    1
    >>> len(result)
    3

    Notes
    -----
    No elimina outliers, cancelaciones o desvíos y no imputa nulos
    estructurales. Las transformaciones específicas de cada modelo se
    realizarán en los notebooks correspondientes.
    """
    df = df.copy()

    # La lógica conserva el vuelo y solo invalida la duración imposible.
    invalid_crs_elapsed = df["CRS_ELAPSED_TIME"] < 0
    df.loc[invalid_crs_elapsed, "CRS_ELAPSED_TIME"] = pd.NA

    return df
