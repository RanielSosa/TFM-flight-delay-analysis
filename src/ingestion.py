"""
Utilidades reutilizables para la ingesta incremental del dataset de vuelos.

El módulo contiene la lógica que permite descubrir fuentes, identificar su
contenido mediante SHA-256, mantener un manifest histórico y detectar qué
archivos necesitan procesarse.

La finalidad es evitar reprocesar millones de registros cuando BTS publica
nuevos periodos.
"""

from __future__ import annotations

from pathlib import Path
import hashlib

import pandas as pd


MANIFEST_COLUMNS = [
    "source_file",
    "source_folder",
    "relative_path",
    "file_size_bytes",
    "sha256",
    "rows",
    "min_date",
    "max_date",
    "processed_at",
    "status",
]


def calculate_sha256(
    file_path: str | Path,
    block_size: int = 1024 * 1024,
) -> str:
    """
    Calcula el hash SHA-256 de un archivo sin cargarlo completo en memoria.

    El hash funciona como una huella del contenido. Se utiliza en el manifest
    para reconocer archivos previamente procesados aunque el nombre cambie.

    Parameters
    ----------
    file_path : str or pathlib.Path
        Ruta del archivo cuyo contenido se desea identificar.
    block_size : int, default=1048576
        Tamaño de lectura en bytes. El valor por defecto equivale a 1 MB.

    Returns
    -------
    str
        Cadena hexadecimal SHA-256 de 64 caracteres.

    Raises
    ------
    FileNotFoundError
        Si la ruta no existe.
    IsADirectoryError
        Si la ruta apunta a un directorio.

    Examples
    --------
    >>> digest = calculate_sha256("data/raw/Flights/example.csv")
    >>> isinstance(digest, str)
    True
    >>> len(digest)
    64

    Notes
    -----
    Dos archivos con contenido idéntico producirán el mismo hash.
    """
    file_path = Path(file_path)
    sha256 = hashlib.sha256()

    # Lectura por bloques: importante porque los CSV pueden ser muy grandes.
    with file_path.open("rb") as file:
        while True:
            block = file.read(block_size)
            if not block:
                break
            sha256.update(block)

    return sha256.hexdigest()


def load_ingestion_manifest(
    manifest_path: str | Path,
) -> pd.DataFrame:
    """
    Carga el manifest de ingesta o devuelve una estructura vacía.

    El manifest es el catálogo de archivos que ya forman parte de la capa
    procesada. Consultarlo antes del procesamiento evita duplicaciones.

    Parameters
    ----------
    manifest_path : str or pathlib.Path
        Ruta esperada de ``ingestion_manifest.csv``.

    Returns
    -------
    pandas.DataFrame
        Manifest existente o DataFrame vacío con ``MANIFEST_COLUMNS``.

    Examples
    --------
    >>> manifest = load_ingestion_manifest(
    ...     "data/processed/flights/ingestion_manifest.csv"
    ... )
    >>> isinstance(manifest, pd.DataFrame)
    True

    Notes
    -----
    La función solo lee; no crea físicamente el CSV cuando este no existe.
    """
    manifest_path = Path(manifest_path)

    if manifest_path.exists():
        return pd.read_csv(manifest_path)

    return pd.DataFrame(columns=MANIFEST_COLUMNS)


def discover_csv_files(
    flights_dir: str | Path,
) -> list[Path]:
    """
    Descubre recursivamente todos los CSV disponibles en la capa raw.

    Parameters
    ----------
    flights_dir : str or pathlib.Path
        Directorio raíz donde se almacenan las descargas de vuelos.

    Returns
    -------
    list[pathlib.Path]
        Rutas ordenadas de todos los archivos ``.csv`` encontrados.

    Raises
    ------
    FileNotFoundError
        Si el directorio indicado no existe.

    Examples
    --------
    >>> files = discover_csv_files("data/raw/Flights")
    >>> isinstance(files, list)
    True

    Notes
    -----
    Se usa búsqueda recursiva porque cada descarga BTS puede estar dentro de
    su propio subdirectorio.
    """
    flights_dir = Path(flights_dir)

    if not flights_dir.exists():
        raise FileNotFoundError(
            f"No existe el directorio de vuelos: {flights_dir}"
        )

    return sorted(flights_dir.rglob("*.csv"))


def detect_new_files(
    csv_files: list[Path],
    ingestion_manifest: pd.DataFrame,
) -> tuple[list[dict], list[Path]]:
    """
    Separa archivos nuevos de archivos ya procesados.

    Para cada fuente disponible calcula su hash SHA-256 y lo compara con los
    hashes registrados con estado ``PROCESSED`` en el manifest.

    Parameters
    ----------
    csv_files : list[pathlib.Path]
        Archivos actualmente presentes en la capa raw.
    ingestion_manifest : pandas.DataFrame
        Historial de fuentes procesadas.

    Returns
    -------
    new_files : list[dict]
        Archivos pendientes. Cada elemento contiene ``path`` y ``sha256``.
    already_processed_files : list[pathlib.Path]
        Archivos cuyo contenido ya está registrado como procesado.

    Examples
    --------
    >>> new_files, processed = detect_new_files(files, manifest)
    >>> isinstance(new_files, list)
    True
    >>> isinstance(processed, list)
    True

    Notes
    -----
    Esta función es el filtro inicial del pipeline productivo: las fases
    costosas de validación, normalización y escritura solo se ejecutan para
    ``new_files``.
    """
    if ingestion_manifest.empty:
        processed_hashes = set()
    else:
        processed_hashes = set(
            ingestion_manifest.loc[
                ingestion_manifest["status"] == "PROCESSED",
                "sha256",
            ].dropna()
        )

    new_files = []
    already_processed_files = []

    for csv_file in csv_files:
        file_hash = calculate_sha256(csv_file)

        if file_hash in processed_hashes:
            already_processed_files.append(csv_file)
        else:
            new_files.append({"path": csv_file, "sha256": file_hash})

    return new_files, already_processed_files
