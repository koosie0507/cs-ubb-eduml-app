import functools
from typing import Callable, Any, Optional

import mlflow.sklearn
from mlflow.models import infer_signature, ModelSignature


class sklearn_model:
    __MODEL_PATH = "sklearn-model"

    def __init__(self, enabled: bool, tracking_uri: str, experiment: Optional[str] = None) -> None:
        if enabled:
            mlflow.set_tracking_uri(tracking_uri)
        self._experiment = experiment

    def __ensure_experiment_id(self):
        if not self._experiment:
            return None
        exp = mlflow.get_experiment_by_name(self._experiment)
        if exp:
            return exp.experiment_id
        return mlflow.create_experiment(self._experiment)

    def __call__(self, wrapped: Callable[..., ModelSignature]) -> Callable:
        @functools.wraps(wrapped)
        def wrapper(*args, **kwargs) -> Any:
            status = "FINISHED"
            try:
                run_args = {}
                experiment_id = self.__ensure_experiment_id()
                if experiment_id:
                    run_args["experiment_id"] = experiment_id

                run = mlflow.start_run(**run_args)
                model_params = {
                    f"param_{idx+1}": arg
                    for idx, arg in enumerate(args)
                }
                model_params.update(**kwargs)
                mlflow.log_params(model_params)
                data_in, model_out, model = wrapped(*args, **kwargs)
                sig = infer_signature(data_in, model_out, model_params)
                mlflow.sklearn.log_model(model, artifact_path=self.__MODEL_PATH, signature=sig)
                model_uri = f"runs:/{run.info.run_id}/{self.__MODEL_PATH}"
                mlflow.register_model(model_uri, f"{self._experiment}-sklearn-model")
                return model
            except Exception as exc:
                status = "FAILED"
                raise exc
            finally:
                mlflow.end_run(status)

        return wrapper
