FROM apache/airflow:2.9.1

USER root

RUN apt-get update && apt-get install -y redis-tools

USER airflow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY includes /opt/airflow/includes

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/opt/airflow/includes

# You can add any additional setup or customization here if needed
