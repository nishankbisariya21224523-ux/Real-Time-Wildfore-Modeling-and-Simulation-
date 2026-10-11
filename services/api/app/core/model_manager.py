"""Model Manager for managing, caching, and serving active risk prediction models."""

import logging
from typing import Any, Dict, Optional

from services.risk_engine.inference.loader import ModelLoader
from services.risk_engine.models.base import BaseRiskModel
from services.risk_engine.models.registry import ModelRegistry
from services.risk_engine.common.exceptions import ModelNotFoundError, ModelCorruptError

from .config import settings
from .exceptions import ModelUnavailableException, ValidationException

logger = logging.getLogger("RiskModelManager")


class RiskModelManager:
    """
    Manages in-memory lifecycle, validation, and retrieval of active risk models.
    Ensures model artifacts are loaded once and reused across API requests.
    """

    _instance: Optional["RiskModelManager"] = None

    def __init__(self):
        self._registry = ModelRegistry()
        self._active_model: Optional[BaseRiskModel] = None
        self._active_version: Optional[str] = None
        self._is_available: bool = False
        self._error_reason: Optional[str] = None

    @classmethod
    def get_instance(cls) -> "RiskModelManager":
        if cls._instance is None:
            cls._instance = RiskModelManager()
        return cls._instance

    @property
    def is_available(self) -> bool:
        return self._is_available

    @property
    def active_version(self) -> Optional[str]:
        return self._active_version

    def load_active_model(self, version: Optional[str] = None) -> bool:
        """
        Loads the specified (or default configured) model version into memory.
        Returns True if successful, False if model could not be loaded.
        """
        target_version = version or getattr(settings, "DEFAULT_RISK_MODEL_VERSION", "risk-xgboost-v001")
        try:
            logger.info(f"Loading risk model version '{target_version}' from registry...")
            model = ModelLoader.load_model(target_version)
            self._active_model = model
            self._active_version = target_version
            self._is_available = True
            self._error_reason = None
            logger.info(
                f"Successfully loaded risk model '{target_version}' "
                f"(algorithm: {model.metadata.algorithm}, features: {len(model.metadata.feature_names)})"
            )
            return True
        except (ModelNotFoundError, FileNotFoundError) as e:
            self._is_available = False
            self._error_reason = f"Model version '{target_version}' not found: {e}"
            logger.warning(self._error_reason)
            return False
        except (ModelCorruptError, Exception) as e:
            self._is_available = False
            self._error_reason = f"Failed to load model '{target_version}': {e}"
            logger.error(self._error_reason)
            return False

    def get_model(self, version: Optional[str] = None) -> BaseRiskModel:
        """
        Retrieves the requested or active model for inference.
        Raises ModelUnavailableException if the model cannot be provided.
        """
        target_version = version or self._active_version or getattr(settings, "DEFAULT_RISK_MODEL_VERSION", "risk-xgboost-v001")

        # If already loaded and matches requested version
        if self._is_available and self._active_model is not None and (version is None or version == self._active_version):
            return self._active_model

        # Attempt on-demand load if a specific version was requested
        try:
            return ModelLoader.load_model(target_version)
        except (ModelNotFoundError, FileNotFoundError) as e:
            raise ModelUnavailableException(
                f"Risk model '{target_version}' is not available in registry: {e}",
                details={"requested_version": target_version, "available_versions": self._registry.list_models()},
            )
        except Exception as e:
            raise ModelUnavailableException(
                f"Failed to load risk model '{target_version}': {e}",
                details={"requested_version": target_version, "error": str(e)},
            )

    def get_status(self) -> Dict[str, Any]:
        """Returns structured status of the risk model subsystem."""
        return {
            "status": "AVAILABLE" if self._is_available else "UNAVAILABLE",
            "active_version": self._active_version,
            "algorithm": self._active_model.metadata.algorithm if self._active_model else None,
            "available_versions": self._registry.list_models(),
            "error": self._error_reason,
        }


# Global singleton instance
risk_model_manager = RiskModelManager.get_instance()
