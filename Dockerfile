FROM python:3.12

RUN pip install polars numpy scipy scikit-learn mlflow

COPY wine-quality.csv .
COPY train.py .
