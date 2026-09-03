\# Aplicación de alerta temprana de retrasos de vuelos



Esta carpeta contiene la aplicación Streamlit desarrollada para utilizar el modelo predictivo de retrasos de vuelos del TFM.



La aplicación permite realizar:



1\. Predicciones individuales mediante un formulario.

2\. Predicciones masivas mediante archivos CSV o Parquet.



El sistema devuelve una puntuación de riesgo (`risk\_score`) y una alerta binaria (`alert`). La puntuación de riesgo no debe interpretarse como una probabilidad calibrada de retraso.



\## Requisitos



Para ejecutar la aplicación es necesario disponer de Python y de las siguientes librerías:



```text

streamlit

pandas

numpy

scipy

scikit-learn

joblib

pyarrow

```



Si se utiliza el entorno Conda del proyecto, debe activarse previamente:



```powershell

conda activate tfm-flights-core

```



Si Streamlit no está instalado en el entorno:



```powershell

pip install streamlit

```



\## Estructura requerida



La aplicación recupera automáticamente los artefactos persistidos del modelo. Por este motivo, debe mantenerse la siguiente estructura relativa:



```text

TFM/

├── app/

│   ├── app.py

│   └── README.md

│

└── results/

&#x20;   └── modeling/

&#x20;       ├── final\_categorical\_encoder\_2022\_2025.joblib

&#x20;       ├── final\_numerical\_scaler\_2022\_2025.joblib

&#x20;       ├── final\_logistic\_regression\_2022\_2025.joblib

&#x20;       └── final\_model\_configuration.json

```



Los cuatro archivos de `results/modeling/` son necesarios para ejecutar la inferencia. No es necesario disponer de los datasets históricos ni ejecutar previamente los notebooks del proyecto.



\## Ejecución



Desde la carpeta raíz del proyecto:



```powershell

cd "G:\\My Drive\\MASTER Big Data\\TFM"

```



Activar el entorno:



```powershell

conda activate tfm-flights-core

```



Ejecutar la aplicación:



```powershell

streamlit run app/app.py

```



También puede ejecutarse desde la propia carpeta `app`:



```powershell

cd app

streamlit run app.py

```



Streamlit iniciará un servidor local y mostrará una dirección similar a:



```text

http://localhost:8501

```



La aplicación se utilizará desde el navegador.



\## Predicción individual



La modalidad individual solicita los datos programados de un vuelo:



\- fecha del vuelo;

\- aerolínea comercializadora;

\- aerolínea operadora;

\- aeropuerto de origen;

\- aeropuerto de destino;

\- franja programada de salida;

\- franja programada de llegada;

\- duración programada en minutos;

\- distancia en millas.



`MONTH` y `DAY\_OF\_WEEK` se calculan automáticamente a partir de la fecha.



Al seleccionar `Analizar vuelo`, la aplicación aplica el mismo preprocesamiento y modelo persistidos durante el desarrollo del TFM y devuelve:



\- `risk\_score`: puntuación de riesgo;

\- `alert`: indicador de superación del umbral de decisión.



El umbral definitivo utilizado por el sistema es `0.406588`.



\## Carga masiva



La modalidad de carga masiva admite archivos CSV o Parquet con múltiples vuelos.



La propia aplicación incluye la opción:



```text

Descargar plantilla CSV

```



Se recomienda utilizar esta plantilla para garantizar que los nombres y el formato de las columnas sean compatibles con el sistema.



Una vez procesado el archivo, la aplicación muestra el número de vuelos y alertas generadas y permite descargar un archivo con los resultados.



\## Consideraciones



La aplicación utiliza exclusivamente el modelo definitivo y sus artefactos persistidos. Su ejecución no realiza reentrenamiento, selección de hiperparámetros ni modificación del umbral.



Los resultados deben interpretarse como un sistema de alerta temprana y priorización de riesgo, no como una determinación de que un vuelo vaya necesariamente a experimentar un retraso.

