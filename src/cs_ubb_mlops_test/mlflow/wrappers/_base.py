import functools
from abc import ABCMeta, abstractmethod
from typing import Callable, Any, Optional

from mlflow.client import MlflowClient
from mlflow.models import infer_signature, ModelSignature


class mlflow_decorator(metaclass=ABCMeta):
    def __init__(self, enabled: bool, tracking_uri: str, experiment: Optional[str] = None) -> None:
        self._mlflow = MlflowClient(tracking_uri if enabled else None)
        self._experiment = experiment

    def __ensure_experiment_id(self):
        if not self._experiment:
            return None
        exp = self._mlflow.get_experiment_by_name(self._experiment)
        if exp:
            return exp.experiment_id
        return self._mlflow.create_experiment(self._experiment)

    @abstractmethod
    def _log_model(self, model: Any, sig: ModelSignature) -> None:
        pass

    @property
    @abstractmethod
    def _model_path(self) -> str:
        return ""

    def __call__(self, wrapped: Callable[..., ModelSignature]) -> Callable:
        @functools.wraps(wrapped)
        def wrapper(*args, **kwargs) -> Any:
            run_args = {}
            experiment_id = self.__ensure_experiment_id()
            if experiment_id:
                run_args["experiment_id"] = experiment_id
            run = self._mlflow.create_run(**run_args)
            run_finish_status = "FINISHED"
            try:
                model_params = {
                    f"param_{idx+1}": arg
                    for idx, arg in enumerate(args)
                }
                model_params.update(**kwargs)
                for param_name, param_value in model_params.items():
                    self._mlflow.log_param(run.info.run_id, param_name, param_value)
                result = wrapped(*args, **kwargs)

                if result is None:
                    raise TypeError("model training function returned NoneType")
                if not isinstance(result, tuple):
                    raise TypeError("model training function did not return tuple")
                if len(result) != 3:
                    raise ValueError("expected training to return tuple with 3 values")
                data_in, model_out, model = result

                self._log_model(model, infer_signature(data_in, model_out, model_params))

                return result
            except Exception as exc:
                run_finish_status = "FAILED"
                raise exc
            finally:
                self._mlflow.update_run(run.info.run_id, run_finish_status)

        return wrapper
