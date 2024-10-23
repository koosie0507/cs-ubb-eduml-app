import argparse
import io
import os
import warnings
from pathlib import Path

import dotenv
import numpy as np
import pandas as pd
from minio import Minio
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

import mlflow.sklearn

dotenv.load_dotenv()

MLFLOW_TRACKING_ENABLED = os.getenv("MLFLOW_TRACKING_ENABLED", "") in {
    "t", "true", "1", "yes", "y"
}
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
MINIO_ENABLED = os.getenv("MINIO_ENABLED", False)
ROOT_DIR = Path(__file__).parent.parent.parent
TRAINING_DATA_PATH = (
    os.getenv("MINIO_OBJECT_PATH", "cs-ubb-mlops-test-1/wine-quality.csv")
    if MINIO_ENABLED
    else ROOT_DIR / "data" / "wine-quality.csv"
)

MINIO_URI = os.getenv("MINIO_URI", "https://minio.minio.svc.cluster.local:9000")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "test-bucket")
MINIO_USERNAME = os.getenv("MINIO_USERNAME")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")


def load_data() -> pd.DataFrame:
    if MINIO_ENABLED:
        minio = Minio(MINIO_URI, access_key=MINIO_USERNAME, secret_key=MINIO_PASSWORD, secure=False)
        response = minio.get_object(MINIO_BUCKET, TRAINING_DATA_PATH)
        try:
            return pd.read_csv(io.StringIO(response.data.decode()))
        finally:
            response.close()
            response.release_conn()
    else:
        local_path = ROOT_DIR / TRAINING_DATA_PATH
        with open(local_path, "r"):
            return pd.read_csv(local_path)


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

wine_quality_df = load_data()

# Split the data into training and test sets. (0.75, 0.25) split.
train, test = train_test_split(wine_quality_df)

# The predicted column is "quality" which is a scalar from [3, 9]
train_x = train.drop(["quality"], axis=1)
test_x = test.drop(["quality"], axis=1)
train_y = train[["quality"]]
test_y = test[["quality"]]

if MLFLOW_TRACKING_ENABLED:
    mlflow.set_tracking_uri(uri=MLFLOW_TRACKING_URI)

for idx, alpha_counter in enumerate(range(2, int(alpha*10))):
    ialpha = alpha_counter / 10
    logfile_name = f"train-log-{idx+1}.log"
    with mlflow.start_run(run_name=f"cs_ubb_mlops_test-{idx+1}") as run:
        mlflow.log_text("start training", logfile_name, run.info.run_id)
        lr = ElasticNet(alpha=ialpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)
        mlflow.log_text("done training", logfile_name, run.info.run_id)

        predicted_qualities = lr.predict(test_x)

        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        mlflow.log_param("alpha", ialpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)
        mlflow.log_text("done eval", logfile_name, run.info.run_id)
        mlflow.sklearn.log_model(lr, "model")