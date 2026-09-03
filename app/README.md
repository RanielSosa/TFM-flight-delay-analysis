# Aplicación de alerta temprana de retrasos de vuelos

Esta carpeta contiene la aplicación web desarrollada para utilizar el modelo predictivo de retrasos de vuelos del TFM.

La aplicación permite realizar:

1. Predicciones individuales mediante un formulario.
2. Predicciones masivas mediante archivos CSV o Parquet.
3. Descarga de los resultados obtenidos.

El sistema devuelve una puntuación de riesgo (`risk_score`) y una alerta binaria (`alert`). La puntuación de riesgo representa el nivel de riesgo estimado por el modelo y no debe interpretarse como una probabilidad calibrada de retraso.

## Aplicación web

La aplicación se encuentra desplegada mediante Streamlit Community Cloud y puede utilizarse directamente desde el navegador:

### [✈️ Abrir sistema de predicción](https://tfm-uflight-delay-analysis-ucm.streamlit.app)

Para utilizar esta modalidad no es necesario instalar Python, descargar el repositorio ni configurar el entorno del proyecto.

## Modos de predicción

### Predicción individual

Permite analizar un único vuelo introduciendo sus características programadas:

- fecha del vuelo;
- aerolínea comercializadora;
- aerolínea operadora;
- aeropuerto de origen;
- aeropuerto de destino;
- franja programada de salida;
- franja programada de llegada;
- duración programada en minutos;
- distancia en millas.

Las variables `MONTH` y `DAY_OF_WEEK` se obtienen automáticamente a partir de la fecha introducida.

La aplicación devuelve:

- `risk_score`: puntuación de riesgo generada por el modelo;
- `alert`: indicador binario que señala si la puntuación supera el umbral de decisión.

El umbral definitivo utilizado por el sistema es `0.406588`.

### Predicción masiva

La modalidad de carga masiva permite procesar múltiples vuelos mediante archivos CSV o Parquet.

La aplicación proporciona una plantilla CSV con la estructura requerida. Una vez procesados los datos, muestra:

- número de vuelos procesados;
- número de alertas generadas;
- tasa de alerta;
- `risk_score` y `alert` para cada vuelo.

Los resultados pueden descargarse posteriormente en formato CSV.

## Ejecución local

La aplicación también puede ejecutarse localmente a partir del repositorio.

### Requisitos

Es necesario disponer de Python y de las dependencias definidas en:

```text
app/requirements.txt
```

Desde la raíz del proyecto pueden instalarse mediante:

```powershell
pip install -r app/requirements.txt
```

Los artefactos necesarios para la inferencia se encuentran incluidos en:

```text
app/artifacts/
```

La estructura de la aplicación es:

```text
app/
├── app.py
├── README.md
├── requirements.txt
└── artifacts/
    ├── final_categorical_encoder_2022_2025.joblib
    ├── final_numerical_scaler_2022_2025.joblib
    ├── final_logistic_regression_2022_2025.joblib
    └── final_model_configuration.json
```

Por tanto, no es necesario disponer de los datasets históricos ni ejecutar nuevamente los notebooks de modelado.

### Iniciar la aplicación

Desde la raíz del repositorio:

```powershell
streamlit run app/app.py
```

Streamlit iniciará un servidor local, normalmente disponible en:

```text
http://localhost:8501
```

## Reproducibilidad

La aplicación utiliza los artefactos persistidos del modelo definitivo:

- codificador de variables categóricas;
- escalador de variables numéricas;
- modelo de regresión logística;
- configuración y umbral de decisión.

La ejecución de la aplicación realiza exclusivamente inferencia. No se produce reentrenamiento, selección de hiperparámetros ni modificación del umbral de decisión.

Esta separación permite reproducir el procedimiento predictivo utilizado en el TFM sin depender del entorno empleado originalmente para entrenar el modelo.

## Consideraciones de uso

El sistema debe interpretarse como una herramienta de alerta temprana y priorización de riesgo.

Una alerta indica que el vuelo supera el umbral de riesgo establecido por el modelo, pero no implica que el retraso vaya a producirse necesariamente.

La aplicación constituye un prototipo académico de despliegue del sistema predictivo y no un sistema de producción en tiempo real.