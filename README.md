# TFM — Flight Delay Analysis

Trabajo Fin de Máster desarrollado en el Máster en Big Data, Data Science e Inteligencia Artificial.

El proyecto aborda el análisis y la predicción temprana de retrasos en vuelos comerciales de Estados Unidos a partir de información histórica del Bureau of Transportation Statistics (BTS).

El objetivo principal es construir y evaluar un sistema de alerta temprana capaz de identificar vuelos con riesgo elevado de retraso utilizando exclusivamente información disponible antes de la operación del vuelo.

El proyecto comprende el ciclo completo de un problema de ciencia de datos: ingesta y preparación de datos, análisis exploratorio, modelado predictivo, evaluación temporal, análisis operativo, visualización, reproducibilidad y despliegue de un prototipo web.

---

## Accesos principales

### ✈️ Aplicación de predicción

[**Abrir sistema de alerta temprana**](https://tfm-uflight-delay-analysis-ucm.streamlit.app)

La aplicación permite realizar predicciones individuales y masivas utilizando el modelo definitivo del TFM.

No requiere instalación para su utilización mediante navegador.

### 📓 Notebooks

El desarrollo analítico y metodológico se encuentra documentado en:

[**Acceder a los notebooks**](notebooks/)

### 📖 Documentación de la aplicación

Las instrucciones de utilización y ejecución local están disponibles en:

[**Documentación de la aplicación**](app/README.md)

---

## Fuente de datos

Los datos proceden del Bureau of Transportation Statistics (BTS) del Departamento de Transporte de Estados Unidos, concretamente del conjunto de datos Marketing Carrier On-Time Performance.

Fuente oficial:

[Bureau of Transportation Statistics — Download On-Time Data](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGK&QO_fu146_anzr=b0-gvzr)

El período utilizado en el proyecto comprende desde enero de 2022 hasta mayo de 2026.

El proceso de ingesta y preparación generó:

- 32,761,129 registros procesados.
- 45 variables en la capa analítica.
- 354 archivos Parquet normalizados.
- 0 errores de ingesta.

Los datos originales y los productos analíticos de gran volumen no se almacenan en GitHub debido a su tamaño. El repositorio contiene el código, la metodología y los componentes necesarios para reproducir el flujo analítico.

---

## Objetivo predictivo

La variable objetivo es:

```text
ARR_DEL15
```

Esta variable identifica si un vuelo llega a su destino con un retraso igual o superior a 15 minutos.

El sistema se plantea como un mecanismo de alerta temprana. Por este motivo, las variables predictivas se restringen a información programada o disponible antes de la operación del vuelo, evitando incorporar información que solo puede conocerse posteriormente.

Las variables utilizadas por el modelo definitivo son:

```text
MONTH
DAY_OF_WEEK
MKT_UNIQUE_CARRIER
OP_UNIQUE_CARRIER
ORIGIN
DEST
DEP_TIME_BLK
ARR_TIME_BLK
CRS_ELAPSED_TIME
DISTANCE
```

---

## Diseño temporal de la evaluación

Debido al carácter temporal del problema, la evaluación se realiza respetando estrictamente el orden cronológico de las observaciones.

La estrategia definitiva es:

```text
2022 ─┐
2023  ├── Desarrollo y entrenamiento
2024 ─┘
          ↓
2025 ───── Validación temporal y selección
          ↓
2022–2025 ─ Entrenamiento del modelo definitivo
          ↓
Ene–May 2026 ─ Test externo
```

Los datos de 2026 permanecen completamente separados durante la selección del modelo, hiperparámetros y umbral de decisión.

Esta estrategia reproduce mejor el escenario real de aplicación: utilizar información histórica para generar predicciones sobre observaciones futuras.

---

## Modelo definitivo

El modelo seleccionado es una regresión logística regularizada.

Configuración principal:

```text
Modelo: Logistic Regression
Penalty: L2
C: 0.1
Solver: saga
Tolerance: 0.01
Class weight: balanced
Max iterations: 500
Random state: 42
```

Después del preprocesamiento, el espacio predictivo contiene:

```text
853 variables transformadas
```

El desbalance de la variable objetivo se aborda mediante:

```text
class_weight="balanced"
```

---

## Umbral de decisión

El sistema no utiliza directamente el umbral convencional de `0.5`.

El umbral definitivo fue seleccionado exclusivamente sobre la validación temporal de 2025:

```text
0.406588
```

El criterio operativo prioriza alcanzar aproximadamente un `recall ≥ 0.80`, dado que el objetivo del sistema es identificar anticipadamente una proporción elevada de los vuelos que posteriormente experimentan retrasos.

La puntuación generada por el modelo se presenta como:

```text
risk_score
```

Debe interpretarse como una puntuación relativa de riesgo y no como una probabilidad calibrada de retraso.

---

## Evaluación externa

La evaluación final se realizó sobre un período completamente posterior al utilizado durante el desarrollo:

```text
Enero–mayo de 2026
```

El test externo contiene:

```text
3,102,447 vuelos
```

Resultados principales:

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.4569 |
| Precision | 0.2527 |
| Recall | 0.7994 |
| F1 | 0.3840 |
| ROC-AUC | 0.6355 |
| Average Precision | 0.3053 |
| Tasa de alerta | 66.98 % |

Matriz de confusión:

| | Predicción negativa | Predicción positiva |
|---|---:|---:|
| Real negativo | 892,540 | 1,553,063 |
| Real positivo | 131,739 | 525,105 |

El sistema identifica aproximadamente el 80 % de los retrasos observados, aunque requiere generar alertas sobre aproximadamente el 67 % de los vuelos.

La elevada proporción de falsas alertas constituye una de las principales limitaciones del modelo y debe considerarse al interpretar su utilidad operativa.

---

## Aplicación web

El modelo definitivo se encuentra integrado en una aplicación desarrollada con Streamlit.

[**✈️ Probar el sistema predictivo**](https://tfm-uflight-delay-analysis-ucm.streamlit.app)

La aplicación proporciona dos modalidades.

### Predicción individual

Permite introducir las características programadas de un vuelo y obtener:

```text
risk_score
alert
```

### Predicción masiva

Permite cargar múltiples observaciones mediante:

```text
CSV
Parquet
```

La aplicación proporciona una plantilla CSV compatible y permite descargar posteriormente los resultados generados.

Los detalles técnicos y las instrucciones para ejecutar la aplicación localmente se encuentran en:

[app/README.md](app/README.md)

---

## Reproducibilidad de la inferencia

La aplicación utiliza directamente los artefactos persistidos del modelo definitivo:

```text
app/artifacts/
├── final_categorical_encoder_2022_2025.joblib
├── final_numerical_scaler_2022_2025.joblib
├── final_logistic_regression_2022_2025.joblib
└── final_model_configuration.json
```

Esto permite ejecutar nuevas inferencias sin:

- volver a entrenar el modelo;
- repetir la selección de hiperparámetros;
- recalcular el umbral;
- disponer de los más de 32 millones de registros históricos.

La reproducibilidad del procedimiento de inferencia fue comprobada utilizando observaciones persistidas del test externo, obteniendo coincidencia del 100 % en las decisiones de alerta.

---

## Visualización y análisis operativo

Los resultados del modelo se analizan desde distintas perspectivas:

- comportamiento global;
- evolución temporal;
- franjas horarias;
- aerolíneas;
- aeropuertos;
- concentración de falsos positivos;
- concentración de falsos negativos;
- intensidad de las alertas.

El proyecto incluye además una capa analítica específicamente preparada para su explotación mediante Power BI.

La capa principal consolidada contiene:

```text
32,761,129 registros
45 variables
```

y se complementa con tablas de referencia, resultados predictivos y agregados analíticos.

---

## Estructura general del proyecto

```text
TFM/
│
├── app/
│   ├── app.py
│   ├── README.md
│   ├── requirements.txt
│   └── artifacts/
│
├── config/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── rejected/
│   └── reference/
│
├── docs/
│
├── notebooks/
│
├── results/
│
├── src/
│
├── environment.yml
├── .gitignore
└── README.md
```

Las carpetas de datos y resultados de gran volumen se mantienen fuera del control de versiones cuando corresponde.

Los artefactos mínimos necesarios para ejecutar la aplicación sí se incluyen en `app/artifacts/`.

---

## Flujo general del proyecto

```text
Datos BTS
    ↓
Ingesta y validación
    ↓
Normalización y almacenamiento Parquet
    ↓
Análisis exploratorio
    ↓
Preparación del dataset de modelado
    ↓
Desarrollo y comparación de modelos
    ↓
Validación temporal 2025
    ↓
Selección del modelo y umbral
    ↓
Entrenamiento definitivo 2022–2025
    ↓
Evaluación externa 2026
    ↓
Análisis operativo
    ↓
Visualización y Power BI
    ↓
Reproducibilidad de inferencia
    ↓
Aplicación Streamlit
```

---

## Entorno de ejecución

El entorno principal del proyecto se gestiona mediante Conda:

```bash
conda env create -f environment.yml
```

Para activarlo:

```bash
conda activate tfm-flights-core
```

La aplicación dispone adicionalmente de sus propias dependencias:

```text
app/requirements.txt
```

que pueden instalarse mediante:

```bash
pip install -r app/requirements.txt
```

Para ejecutar la aplicación localmente:

```bash
streamlit run app/app.py
```

---

## Tecnologías utilizadas

El proyecto utiliza principalmente:

```text
Python
Pandas
NumPy
PyArrow
Scikit-learn
SciPy
Joblib
Matplotlib
Streamlit
Power BI
Git
GitHub
```

El almacenamiento analítico se realiza principalmente mediante formato Parquet para facilitar el procesamiento eficiente de grandes volúmenes de información.

---

## Alcance del sistema

El resultado del proyecto debe interpretarse como un prototipo académico de sistema de alerta temprana.

Una alerta indica que las características programadas del vuelo producen una puntuación superior al umbral establecido por el modelo. No implica que el vuelo vaya necesariamente a experimentar un retraso.

El sistema tampoco constituye actualmente una infraestructura productiva de predicción en tiempo real.

Su finalidad es demostrar de forma reproducible el ciclo completo de construcción, evaluación, interpretación y despliegue de un modelo predictivo aplicado a un problema real de gran volumen de datos.

---

## Estado del proyecto

Las principales etapas analíticas se encuentran completadas:

- ingesta y normalización;
- análisis exploratorio;
- preparación del dataset de modelado;
- modelado predictivo;
- selección temporal;
- evaluación externa;
- análisis operativo;
- preparación para visualización en Power BI;
- reproducibilidad de inferencia;
- aplicación web de predicción;
- despliegue mediante Streamlit Community Cloud.

La aplicación predictiva se encuentra disponible públicamente en:

[**https://tfm-uflight-delay-analysis-ucm.streamlit.app**](https://tfm-uflight-delay-analysis-ucm.streamlit.app)
