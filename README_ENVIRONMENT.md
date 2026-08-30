# Entorno reproducible --- TFM Flight Delay Analysis

## 1. Objetivo

Este documento describe el procedimiento recomendado para crear,
activar, validar y mantener el entorno de ejecución del proyecto **TFM
Flight Delay Analysis**.

El entorno utilizado por el proyecto se denomina:

`tfm-flights-core`

El objetivo es garantizar que la ingesta, preparación, análisis
exploratorio y modelado predictivo puedan reproducirse utilizando una
configuración de Python y librerías controlada.

> **Principio de reproducibilidad:** durante la fase experimental no se
> deben actualizar librerías de forma indiscriminada. Las versiones que
> produzcan los resultados definitivos del TFM deben quedar registradas
> y congeladas en `environment.yml`.

------------------------------------------------------------------------

## 2. Requisitos previos

Se recomienda utilizar **Anaconda** o **Miniconda** para gestionar el
entorno.

Antes de comenzar, comprobar que Conda está disponible:

``` powershell
conda --version
```

También puede comprobarse la instalación de Python:

``` powershell
python --version
```

------------------------------------------------------------------------

## 3. Ubicación recomendada de los archivos

En la raíz del proyecto se recomienda mantener:

``` text
TFM/
├── environment.yml
├── README_ENVIRONMENT.md
├── data/
├── notebooks/
├── results/
└── src/
```

`environment.yml` constituye la definición reproducible del entorno.
Este README documenta cómo utilizarla.

------------------------------------------------------------------------

## 4. Creación del entorno desde `environment.yml`

Situarse en la raíz del proyecto:

``` powershell
cd "G:\My Drive\MASTER Big Data\TFM"
```

Crear el entorno:

``` powershell
conda env create -f environment.yml
```

Activarlo:

``` powershell
conda activate tfm-flights-core
```

La creación desde el archivo YAML es preferible a instalar manualmente
cada dependencia, porque permite reconstruir una configuración coherente
en otro equipo.

------------------------------------------------------------------------

## 5. Activación de un entorno ya existente

Si el entorno ya fue creado:

``` powershell
conda activate tfm-flights-core
```

Comprobar qué intérprete de Python está activo:

``` powershell
where python
```

En Windows debería aparecer una ruta asociada al entorno, por ejemplo:

``` text
...\anaconda3\envs\tfm-flights-core\python.exe
```

------------------------------------------------------------------------

## 6. Librerías principales utilizadas por el proyecto

El proyecto depende, como mínimo, de los siguientes componentes:

  Componente     Uso principal
  -------------- ----------------------------------------------
  Python         Lenguaje de ejecución
  NumPy          Operaciones numéricas
  pandas         Manipulación de datos
  SciPy          Matrices dispersas y operaciones científicas
  scikit-learn   Preprocesamiento, modelos y métricas
  PyArrow        Lectura y escritura de Parquet
  joblib         Persistencia y utilidades de scikit-learn
  tqdm           Barras de progreso
  Jupyter        Ejecución de notebooks
  Matplotlib     Visualización
  ipykernel      Kernel de Jupyter asociado al entorno

Las versiones exactas no deben suponerse a partir de este documento:
deben obtenerse del entorno que produzca los experimentos definitivos y
quedar registradas en `environment.yml`.

------------------------------------------------------------------------

## 7. Registro de las versiones realmente instaladas

Con el entorno activo:

``` powershell
conda activate tfm-flights-core
```

Registrar la versión de Python:

``` powershell
python --version
```

Consultar las versiones principales:

``` powershell
python -c "import sys, numpy, pandas, scipy, sklearn, pyarrow, joblib, tqdm; print('Python:', sys.version); print('NumPy:', numpy.__version__); print('pandas:', pandas.__version__); print('SciPy:', scipy.__version__); print('scikit-learn:', sklearn.__version__); print('PyArrow:', pyarrow.__version__); print('joblib:', joblib.__version__); print('tqdm:', tqdm.__version__)"
```

También puede obtenerse el inventario completo:

``` powershell
conda list
```

Este paso debe realizarse antes de cerrar la versión definitiva del TFM
para documentar exactamente el software utilizado.

------------------------------------------------------------------------

## 8. Exportación reproducible del entorno

### Exportación completa

Para conservar una copia exacta del entorno instalado:

``` powershell
conda env export --name tfm-flights-core > environment-full.yml
```

Esta exportación puede contener dependencias específicas del sistema
operativo y del equipo.

### Exportación portable recomendada

Para generar una definición más portable basada en las dependencias
solicitadas explícitamente:

``` powershell
conda env export --name tfm-flights-core --from-history > environment.yml
```

Después de generarla debe revisarse que incluya las dependencias
necesarias para ejecutar los notebooks.

Para máxima reproducibilidad académica conviene conservar tanto una
definición mantenible (`environment.yml`) como una captura exacta del
entorno utilizado para los experimentos finales
(`environment-full.yml`).

------------------------------------------------------------------------

## 9. Registro del kernel de Jupyter

Con el entorno activo:

``` powershell
conda activate tfm-flights-core
```

Instalar o actualizar el kernel:

``` powershell
python -m ipykernel install --user --name tfm-flights-core --display-name "Python (tfm-flights-core)"
```

En Jupyter debe seleccionarse:

``` text
Python (tfm-flights-core)
```

Esto evita ejecutar accidentalmente los notebooks con el entorno `base`
u otro intérprete.

------------------------------------------------------------------------

## 10. Validación rápida del entorno

Después de crear o restaurar el entorno:

``` powershell
python -c "import numpy, pandas, scipy, sklearn, pyarrow, joblib, tqdm; print('Environment OK')"
```

Si aparece:

``` text
Environment OK
```

las dependencias principales pueden importarse correctamente.

También debe comprobarse el kernel desde un notebook:

``` python
import sys
print(sys.executable)
```

La ruta debe apuntar a `tfm-flights-core`.

------------------------------------------------------------------------

## 11. Actualización del entorno

Durante el desarrollo experimental no se recomienda ejecutar
actualizaciones globales como:

``` powershell
conda update --all
```

sin una necesidad técnica concreta.

Una actualización puede modificar el comportamiento de algoritmos,
parámetros, serialización o dependencias y dificultar la reproducción de
resultados obtenidos anteriormente.

Si una librería debe actualizarse por una razón justificada, el
procedimiento recomendado es:

1.  Registrar el estado actual del entorno.
2.  Actualizar únicamente la dependencia necesaria.
3.  Ejecutar las validaciones relevantes del proyecto.
4.  Confirmar que los experimentos siguen siendo reproducibles.
5.  Actualizar `environment.yml` y la documentación.

------------------------------------------------------------------------

## 12. Reconstrucción completa en otro equipo

El procedimiento esperado es:

``` powershell
git clone <URL_DEL_REPOSITORIO>
cd TFM-flight-delay-analysis
conda env create -f environment.yml
conda activate tfm-flights-core
python -m ipykernel install --user --name tfm-flights-core --display-name "Python (tfm-flights-core)"
jupyter notebook
```

Los datasets masivos no tienen por qué formar parte del repositorio Git.
Deben recuperarse o ubicarse siguiendo la estructura de datos definida
por el proyecto.

------------------------------------------------------------------------

## 13. Comprobación antes de los experimentos definitivos

Antes de ejecutar los modelos que se utilizarán en los resultados
finales del TFM debe verificarse:

``` powershell
conda activate tfm-flights-core
python --version
conda list
```

Además, desde el notebook:

``` python
import sys
import numpy as np
import pandas as pd
import scipy
import sklearn
import pyarrow
import joblib
import tqdm

environment_versions = {
    "python": sys.version.split()[0],
    "numpy": np.__version__,
    "pandas": pd.__version__,
    "scipy": scipy.__version__,
    "scikit-learn": sklearn.__version__,
    "pyarrow": pyarrow.__version__,
    "joblib": joblib.__version__,
    "tqdm": tqdm.__version__,
}

environment_versions
```

Esta comprobación proporciona evidencia directa del entorno utilizado
durante la ejecución.

------------------------------------------------------------------------

## 14. Criterio metodológico

La reproducibilidad computacional forma parte de la metodología del TFM.
Por ello, la configuración utilizada para generar los resultados finales
debe permanecer estable y documentada.

El flujo recomendado es:

``` text
environment.yml
        ↓
creación de tfm-flights-core
        ↓
validación de Python y dependencias
        ↓
ejecución de notebooks
        ↓
registro de versiones finales
        ↓
environment-full.yml
```

De esta forma se distingue entre la configuración necesaria para
reconstruir el proyecto y la captura exacta del software con el que se
obtuvieron los resultados experimentales.

------------------------------------------------------------------------

## 15. Estado pendiente

Antes de considerar cerrada esta documentación deben incorporarse las
**versiones exactas actualmente instaladas** en `tfm-flights-core`.

No deben inventarse ni sustituirse por las versiones más recientes
disponibles. Deben extraerse directamente del entorno que está
ejecutando el TFM y contrastarse con el `environment.yml` existente.
