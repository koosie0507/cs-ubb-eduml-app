import argparse
import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

import mlflow
import mlflow.sklearn


MLFLOW_TRACKING_URI=os.getenv("MLFLOW_TRACKING_URI", "http://host.docker.internal:8080")


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


warnings.filterwarnings("ignore")
np.random.seed(40)

parser = argparse.ArgumentParser()
parser.add_argument("--alpha")
parser.add_argument("--l1-ratio")
args = parser.parse_args()
alpha = float(args.alpha)
l1_ratio = float(args.l1_ratio)

print("parsed args alpha", alpha, "and l1 ratio", l1_ratio)

root_dir = Path(__file__).parent.parent.parent
data_dir = root_dir / "data"
dataset_path = data_dir / "wine-quality.csv"
wine_quality_df = pd.read_csv(dataset_path)

# Split the data into training and test sets. (0.75, 0.25) split.
train, test = train_test_split(wine_quality_df)

# The predicted column is "quality" which is a scalar from [3, 9]
train_x = train.drop(["quality"], axis=1)
test_x = test.drop(["quality"], axis=1)
train_y = train[["quality"]]
test_y = test[["quality"]]

print("split train/test data")

print("MLFlow tracking URI=", MLFLOW_TRACKING_URI)
mlflow.set_tracking_uri(uri=MLFLOW_TRACKING_URI)
print("start training")
with mlflow.start_run(run_name="cs_ubb_mlops_test"):
    lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
    lr.fit(train_x, train_y)

    predicted_qualities = lr.predict(test_x)

    (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

    print(f"Elasticnet model (alpha={alpha:f}, l1_ratio={l1_ratio:f}):")
    print(f"  RMSE: {rmse}")
    print(f"  MAE: {mae}")
    print(f"  R2: {r2}")

    mlflow.log_param("alpha", alpha)
    mlflow.log_param("l1_ratio", l1_ratio)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    mlflow.log_metric("mae", mae)

    mlflow.sklearn.log_model(lr, "model")