from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from scipy.sparse import csr_matrix, hstack


# ---------------------------------------------------------
# 1. Configuración general
# ---------------------------------------------------------

st.set_page_config(
    page_title="Alerta de retrasos",
    page_icon="✈️",
    layout="centered",
)

app_path = Path(__file__).resolve().parent
project_root = app_path.parent
modeling_path = project_root / "results" / "modeling"

encoder_path = modeling_path / "final_categorical_encoder_2022_2025.joblib"
scaler_path = modeling_path / "final_numerical_scaler_2022_2025.joblib"
model_path = modeling_path / "final_logistic_regression_2022_2025.joblib"
configuration_path = modeling_path / "final_model_configuration.json"


# ---------------------------------------------------------
# 2. Recuperación de artefactos
# ---------------------------------------------------------

@st.cache_resource
def load_artifacts():
    # Recuperar los componentes definitivos del sistema
    encoder = joblib.load(encoder_path)
    scaler = joblib.load(scaler_path)
    model = joblib.load(model_path)

    with open(configuration_path, "r", encoding="utf-8") as file:
        configuration = json.load(file)

    return encoder, scaler, model, configuration


try:
    categorical_encoder, numerical_scaler, final_model, configuration = (
        load_artifacts()
    )
except Exception as error:
    st.error(
        f"No fue posible cargar el sistema predictivo: {error}"
    )
    st.stop()


categorical_features = configuration["categorical_features"]
numerical_features = configuration["numerical_features"]

input_features = (
    categorical_features
    + numerical_features
)

decision_threshold = float(
    configuration["decision_threshold"]
)


# ---------------------------------------------------------
# 3. Preparación de nuevas observaciones
# ---------------------------------------------------------

def prepare_input(data):
    # Crear una copia para no modificar los datos originales
    prepared_data = data.copy()

    # Derivar las variables temporales desde FL_DATE
    if "FL_DATE" in prepared_data.columns:

        prepared_data["FL_DATE"] = pd.to_datetime(
            prepared_data["FL_DATE"],
            errors="raise",
        )

        prepared_data["MONTH"] = (
            prepared_data["FL_DATE"]
            .dt.month
            .astype("int8")
        )

        prepared_data["DAY_OF_WEEK"] = (
            prepared_data["FL_DATE"]
            .dt.dayofweek
            .add(1)
            .astype("int8")
        )

    # Comprobar que estén presentes las variables necesarias
    missing_features = [
        feature
        for feature in input_features
        if feature not in prepared_data.columns
    ]

    if missing_features:
        raise ValueError(
            "Faltan variables requeridas para la predicción: "
            f"{missing_features}"
        )

    return prepared_data


# ---------------------------------------------------------
# 4. Procedimiento de inferencia
# ---------------------------------------------------------

def predict_alerts(data):
    # Preparar los datos de entrada
    prepared_data = prepare_input(data)

    # Transformar las variables categóricas
    categorical_data = categorical_encoder.transform(
        prepared_data[categorical_features]
    )

    # Transformar las variables numéricas
    numerical_data = numerical_scaler.transform(
        prepared_data[numerical_features]
    )

    # Combinar ambas transformaciones
    transformed_data = hstack(
        [
            categorical_data,
            csr_matrix(numerical_data),
        ],
        format="csr",
    )

    # Localizar la clase positiva
    positive_class_index = int(
        np.where(
            final_model.classes_ == 1
        )[0][0]
    )

    # Obtener la puntuación de riesgo
    risk_score = final_model.predict_proba(
        transformed_data
    )[:, positive_class_index]

    # Aplicar el umbral definitivo
    alert = (
        risk_score >= decision_threshold
    ).astype("int8")

    # Construir el resultado
    result = data.copy()

    result["risk_score"] = risk_score
    result["alert"] = alert

    return result


# ---------------------------------------------------------
# 5. Cabecera de la aplicación
# ---------------------------------------------------------

st.title(
    "✈️ Sistema de alerta temprana de retrasos"
)

st.write(
    "El sistema analiza las características programadas de "
    "un vuelo y determina si presenta un nivel elevado de "
    "riesgo de retraso."
)

st.caption(
    "La puntuación generada es un indicador de riesgo y no "
    "una probabilidad calibrada de retraso."
)


# ---------------------------------------------------------
# 6. Guía de los datos
# ---------------------------------------------------------

with st.expander(
    "ℹ️ Guía de los datos requeridos"
):

    st.markdown(
        """
        - **Fecha del vuelo:** fecha programada del vuelo.
          Se utiliza para obtener automáticamente el mes y
          el día de la semana.

        - **Aerolínea comercializadora:** código de la
          aerolínea que comercializa el vuelo.
          Ejemplo: `AA`.

        - **Aerolínea operadora:** código de la aerolínea
          que opera efectivamente el vuelo.
          Ejemplo: `AA`.

        - **Aeropuerto de origen:** código IATA de tres
          letras del aeropuerto de salida.
          Ejemplo: `JFK`.

        - **Aeropuerto de destino:** código IATA de tres
          letras del aeropuerto de llegada.
          Ejemplo: `LAX`.

        - **Franja programada de salida:** bloque horario
          previsto para la salida.
          Ejemplo: `0900-0959`.

        - **Franja programada de llegada:** bloque horario
          previsto para la llegada.
          Ejemplo: `1300-1359`.

        - **Duración programada:** duración prevista del
          vuelo expresada en minutos.

        - **Distancia:** distancia del trayecto expresada
          en millas.

        `MONTH` y `DAY_OF_WEEK` se calculan automáticamente
        a partir de la fecha del vuelo.
        """
    )


# ---------------------------------------------------------
# 7. Selección del tipo de predicción
# ---------------------------------------------------------

prediction_mode = st.radio(
    "¿Cómo desea realizar la predicción?",
    [
        "Predicción individual",
        "Carga masiva",
    ],
)


# ---------------------------------------------------------
# 8. Predicción individual
# ---------------------------------------------------------

if prediction_mode == "Predicción individual":

    st.subheader(
        "Datos del vuelo"
    )

    flight_date = st.date_input(
        "Fecha del vuelo",
        help=(
            "Seleccione la fecha programada del vuelo."
        ),
    )

    mkt_carrier = st.text_input(
        "Aerolínea comercializadora",
        placeholder="Ej. AA",
        help=(
            "Código de la aerolínea que comercializa "
            "el vuelo."
        ),
    )

    op_carrier = st.text_input(
        "Aerolínea operadora",
        placeholder="Ej. AA",
        help=(
            "Código de la aerolínea que opera "
            "efectivamente el vuelo."
        ),
    )

    origin = st.text_input(
        "Aeropuerto de origen",
        placeholder="Ej. JFK",
        help=(
            "Código IATA de tres letras del aeropuerto "
            "de salida."
        ),
    )

    dest = st.text_input(
        "Aeropuerto de destino",
        placeholder="Ej. LAX",
        help=(
            "Código IATA de tres letras del aeropuerto "
            "de llegada."
        ),
    )

    dep_time_blk = st.selectbox(
        "Franja programada de salida",
        categorical_encoder.categories_[
            categorical_features.index(
                "DEP_TIME_BLK"
            )
        ].tolist(),
        help=(
            "Bloque horario programado de salida."
        ),
    )

    arr_time_blk = st.selectbox(
        "Franja programada de llegada",
        categorical_encoder.categories_[
            categorical_features.index(
                "ARR_TIME_BLK"
            )
        ].tolist(),
        help=(
            "Bloque horario programado de llegada."
        ),
    )

    crs_elapsed_time = st.number_input(
        "Duración programada (minutos)",
        min_value=1.0,
        step=1.0,
        help=(
            "Duración prevista del vuelo expresada "
            "en minutos."
        ),
    )

    distance = st.number_input(
        "Distancia (millas)",
        min_value=1.0,
        step=1.0,
        help=(
            "Distancia del trayecto expresada en millas."
        ),
    )

    if st.button(
        "Analizar vuelo",
        type="primary",
        use_container_width=True,
    ):

        required_text_fields = [
            mkt_carrier.strip(),
            op_carrier.strip(),
            origin.strip(),
            dest.strip(),
        ]

        if not all(required_text_fields):

            st.warning(
                "Complete todos los datos del vuelo."
            )

        else:

            new_flight = pd.DataFrame(
                {
                    "FL_DATE": [
                        flight_date
                    ],
                    "MKT_UNIQUE_CARRIER": [
                        mkt_carrier
                        .strip()
                        .upper()
                    ],
                    "OP_UNIQUE_CARRIER": [
                        op_carrier
                        .strip()
                        .upper()
                    ],
                    "ORIGIN": [
                        origin
                        .strip()
                        .upper()
                    ],
                    "DEST": [
                        dest
                        .strip()
                        .upper()
                    ],
                    "DEP_TIME_BLK": [
                        dep_time_blk
                    ],
                    "ARR_TIME_BLK": [
                        arr_time_blk
                    ],
                    "CRS_ELAPSED_TIME": [
                        crs_elapsed_time
                    ],
                    "DISTANCE": [
                        distance
                    ],
                }
            )

            try:

                prediction = predict_alerts(
                    new_flight
                )

                risk_score = float(
                    prediction[
                        "risk_score"
                    ].iloc[0]
                )

                alert = int(
                    prediction[
                        "alert"
                    ].iloc[0]
                )

                st.divider()

                st.subheader(
                    "Resultado"
                )

                col_1, col_2 = st.columns(2)

                col_1.metric(
                    "Puntuación de riesgo",
                    f"{risk_score:.4f}",
                )

                col_2.metric(
                    "Umbral de alerta",
                    f"{decision_threshold:.4f}",
                )

                if alert == 1:

                    st.warning(
                        "⚠️ Alerta de riesgo de retraso: "
                        "el vuelo supera el umbral "
                        "establecido por el sistema."
                    )

                else:

                    st.success(
                        "✓ Sin alerta de riesgo de retraso: "
                        "el vuelo no supera el umbral "
                        "establecido por el sistema."
                    )

            except Exception as error:

                st.error(
                    "No fue posible realizar la predicción. "
                    f"Detalle: {error}"
                )


# ---------------------------------------------------------
# 9. Carga masiva
# ---------------------------------------------------------

else:

    st.subheader(
        "Carga masiva"
    )

    st.write(
        "Esta modalidad permite analizar múltiples vuelos "
        "mediante un archivo CSV o Parquet."
    )

    with st.expander(
        "ℹ️ Formato requerido del archivo"
    ):

        st.markdown(
            """
            El archivo debe contener una fila por vuelo y
            las siguientes columnas:

            - `FL_DATE`
            - `MKT_UNIQUE_CARRIER`
            - `OP_UNIQUE_CARRIER`
            - `ORIGIN`
            - `DEST`
            - `DEP_TIME_BLK`
            - `ARR_TIME_BLK`
            - `CRS_ELAPSED_TIME`
            - `DISTANCE`

            No es necesario incluir `MONTH` ni
            `DAY_OF_WEEK`, ya que se calculan
            automáticamente a partir de `FL_DATE`.
            """
        )

    # ---------------------------------------------------------
    # 9.1 Plantilla de ejemplo
    # ---------------------------------------------------------

    template = pd.DataFrame(
        {
            "FL_DATE": [
                "2026-07-15"
            ],
            "MKT_UNIQUE_CARRIER": [
                "AA"
            ],
            "OP_UNIQUE_CARRIER": [
                "AA"
            ],
            "ORIGIN": [
                "JFK"
            ],
            "DEST": [
                "LAX"
            ],
            "DEP_TIME_BLK": [
                "0900-0959"
            ],
            "ARR_TIME_BLK": [
                "1300-1359"
            ],
            "CRS_ELAPSED_TIME": [
                370
            ],
            "DISTANCE": [
                2475
            ],
        }
    )

    template_csv = template.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📄 Descargar plantilla CSV",
        data=template_csv,
        file_name="flight_prediction_template.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.caption(
        "La plantilla incluye un registro de ejemplo que "
        "puede sustituirse o ampliarse con nuevos vuelos."
    )


    # ---------------------------------------------------------
    # 9.2 Carga del archivo
    # ---------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Seleccione el archivo con los vuelos",
        type=[
            "csv",
            "parquet",
        ],
    )

    if uploaded_file is not None:

        try:

            if uploaded_file.name.lower().endswith(
                ".csv"
            ):

                new_flights = pd.read_csv(
                    uploaded_file
                )

            else:

                new_flights = pd.read_parquet(
                    uploaded_file
                )


            # -------------------------------------------------
            # 9.3 Ejecución de las predicciones
            # -------------------------------------------------

            predictions = predict_alerts(
                new_flights
            )

            total_flights = len(
                predictions
            )

            total_alerts = int(
                predictions[
                    "alert"
                ].sum()
            )

            alert_rate = (
                total_alerts
                / total_flights
                if total_flights > 0
                else 0
            )

            st.divider()

            st.subheader(
                "Resultado de la carga"
            )

            col_1, col_2, col_3 = st.columns(3)

            col_1.metric(
                "Vuelos procesados",
                f"{total_flights:,}",
            )

            col_2.metric(
                "Alertas generadas",
                f"{total_alerts:,}",
            )

            col_3.metric(
                "Tasa de alerta",
                f"{alert_rate:.2%}",
            )

            st.dataframe(
                predictions.head(20),
                use_container_width=True,
            )


            # -------------------------------------------------
            # 9.4 Descarga de resultados
            # -------------------------------------------------

            output_csv = predictions.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Descargar resultados",
                data=output_csv,
                file_name="flight_predictions.csv",
                mime="text/csv",
                use_container_width=True,
            )

        except Exception as error:

            st.error(
                "No fue posible procesar el archivo. "
                f"Detalle: {error}"
            )