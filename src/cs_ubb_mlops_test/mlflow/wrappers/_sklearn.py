from typing import Any

import mlflow.sklearn
from mlflow.models import ModelSignature

from cs_ubb_mlops_test.mlflow.wrappers._base import mlflow_decorator


class sklearn_model(mlflow_decorator):
    def __new__(cls, *args, **kwargs):
        cls.__HAS_SKLEARN = True
        try:
            import mlflow.sklearn
        except ImportError:
            cls.__HAS_SKLEARN = False
        return super().__new__(cls)

    def _log_model(self, model: Any, sig: ModelSignature) -> None:
        if not self.__HAS_SKLEARN:
            return
        extra_args = {}
        if self._experiment is not None:
            extra_args["registered_model_name"] = f"{self._experiment}-{self._model_path}"
        mlflow.sklearn.log_model(model, self._model_path, **extra_args)

    @property
    def _model_path(self) -> str:
        return "sklearn"
