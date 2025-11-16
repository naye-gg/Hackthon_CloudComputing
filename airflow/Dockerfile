FROM apache/airflow:2.10.3-python3.11

USER root

# Instalar dependencias del sistema
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  gcc \
  python3-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

# Copiar requirements
COPY requirements-airflow.txt /tmp/requirements.txt

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copiar DAGs
COPY airflow/dags /opt/airflow/dags

# Configuración de Airflow
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags
ENV AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor
