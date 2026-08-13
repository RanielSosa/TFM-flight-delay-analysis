# TFM — Flight Delay Analysis

Proyecto desarrollado como Trabajo Fin de Máster dentro del Máster en Big Data y Ciencia de Datos.

El objetivo del proyecto es analizar el comportamiento histórico de los vuelos comerciales en Estados Unidos, estudiar los factores asociados a retrasos y cancelaciones, y desarrollar modelos explicativos y predictivos a partir de datos públicos del Bureau of Transportation Statistics (BTS).

## Fuente de datos

Los datos utilizados proceden del Bureau of Transportation Statistics (BTS), concretamente del conjunto de datos de puntualidad de vuelos.

La capa original de datos se mantiene sin modificaciones dentro de:

```text
data/raw/
```

Por razones de tamaño y reproducibilidad, los archivos de datos no se almacenan en GitHub.

## Estructura del proyecto

```text
TFM/
├── config/
│   └── paths.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── rejected/
│   └── inference/
│
├── docs/
│
├── models/
│
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_pca.ipynb
│   ├── 05_regression.ipynb
│   ├── 06_random_forest.ipynb
│   ├── 07_time_series.ipynb
│   ├── 08_rnn.ipynb
│   └── 09_model_comparison.ipynb
│
├── src/
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── ingestion.py
│   └── setup_project.py
│
├── environment.yml
├── .gitignore
└── README.md
```

## Entorno de ejecución

El proyecto utiliza un entorno Conda definido en:

```text
environment.yml
```

Para crear el entorno:

```bash
conda env create -f environment.yml
```

Para activarlo:

```bash
conda activate tfm-flights-core
```

## Pipeline de ingesta

El notebook:

```text
notebooks/01_data_ingestion.ipynb
```

implementa el proceso de preparación de los datos históricos.

El flujo general es:

```text
CSV BTS
   ↓
Validación de estructura
   ↓
Normalización
   ↓
Análisis de calidad
   ↓
Limpieza
   ↓
Parquet
   ↓
Capa procesada
```

La lógica reutilizable se encuentra separada del notebook:

```text
src/preprocessing.py
src/ingestion.py
```

Esto permite mantener una única implementación de las reglas de transformación.

## Ingesta incremental

El proyecto incluye un mecanismo de actualización incremental.

Antes de procesar nuevos archivos, el pipeline consulta:

```text
ingestion_manifest.csv
```

y compara los archivos disponibles mediante hash SHA-256.

Solo los archivos que todavía no han sido procesados continúan hacia las etapas de validación, normalización, limpieza y almacenamiento.

Esto evita reprocesar innecesariamente todo el histórico.

## Capa procesada

Los datos procesados se almacenan en formato Parquet dentro de:

```text
data/processed/flights/
```

La información está particionada por año y mes para facilitar el acceso temporal y reducir el volumen de lectura durante los análisis posteriores.

## Notebooks del proyecto

La organización analítica prevista es:

```text
01_data_ingestion.ipynb
02_eda.ipynb
03_feature_engineering.ipynb
04_pca.ipynb
05_regression.ipynb
06_random_forest.ipynb
07_time_series.ipynb
08_rnn.ipynb
09_model_comparison.ipynb
```

Cada notebook tiene una responsabilidad específica y se encuentra alineado con la estructura del TFM.

## Reproducibilidad

La reproducibilidad del proyecto se apoya en:

* `environment.yml` para fijar las dependencias.
* Git y GitHub para el control de versiones.
* `src/` para mantener funciones reutilizables.
* `config/paths.py` para centralizar las rutas.
* Parquet como formato de almacenamiento analítico.
* `ingestion_manifest.csv` para controlar la ingesta incremental.

## Estado del proyecto

Actualmente se encuentra completada la fase de ingesta, normalización y preparación inicial de los datos.

La siguiente etapa corresponde al Análisis Exploratorio de Datos (EDA).
