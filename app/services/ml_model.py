# Module : ml_model.py
# Purpose : Future "real ML" model (DISABLED for now)
#
# IMPORTANT:
# - This file is intentionally NOT used by the current pricing flow.
# - We keep it here to show the future evolution when we will have enough real data.
# - Current production logic = pricing_engine (rules) + ai_engine (weights/tilt).
#
# When data becomes sufficient:
# - we can train a model using CLOSED change_price_events (with real outcomes)
# - then swap ai_engine to call this model's predict_coefficient()

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

# sklearn is installed per roadmap, but this module stays unused until enabled.
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# Feature order for ML input (keep stable!)
FEATURE_COLUMNS = [
    "stock",
    "days_to_expire",
    "sales_velocity",
    "old_price",
    "new_price",
    "window_days",
]


@dataclass
class MLConfig:
    enabled: bool = False  # <-- MUST remain False until we have enough data
    min_samples_to_train: int = 200  # safety threshold (adjust later)
    alpha: float = 1.0  # Ridge regularization strength


class PriceMLModel:
    """
    A simple regression model that predicts a "price adjustment coefficient".
    - target y is intended to be a coefficient (e.g. 0.9..1.1) that modulates engined_price
    - model: Ridge regression (stable, interpretable-ish, works with small-ish data when regularized)
    """

    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()
        self._model: Optional[Pipeline] = None
        self._trained_samples: int = 0

    @property
    def is_enabled(self) -> bool:
        return bool(self.config.enabled)

    @property
    def trained_samples(self) -> int:
        return self._trained_samples

    def build_pipeline(self) -> Pipeline:
        return Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("regressor", Ridge(alpha=self.config.alpha)),
            ]
        )

    def _features_to_vector(self, features: Dict) -> np.ndarray:
        """
        Convert a feature dict to a numeric vector in FEATURE_COLUMNS order.
        Missing values default to 0.
        """
        row = []
        for k in FEATURE_COLUMNS:
            v = features.get(k, 0)
            if v is None:
                v = 0
            row.append(float(v))
        return np.array(row, dtype=float)

    def prepare_training_data(self, examples: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert DB training examples into X,y.
        Expected example keys (suggested):
          stock, days_to_expire, sales_velocity, old_price, new_price, window_days, target_coeff
        """
        X = []
        y = []

        for ex in examples:
            if ex.get("target_coeff") is None:
                continue

            vec = self._features_to_vector(ex)
            X.append(vec)
            y.append(float(ex["target_coeff"]))

        if not X:
            return np.zeros((0, len(FEATURE_COLUMNS))), np.zeros((0,))

        return np.vstack(X), np.array(y, dtype=float)

    def train(self, examples: List[Dict]) -> Dict:
        """
        Train the model if enabled and enough data exists.
        Returns a small report dict for logging/diagnostics.
        """
        if not self.is_enabled:
            return {"trained": False, "reason": "ML disabled by config"}

        X, y = self.prepare_training_data(examples)

        if len(y) < self.config.min_samples_to_train:
            return {
                "trained": False,
                "reason": f"not enough samples ({len(y)}/{self.config.min_samples_to_train})",
            }

        self._model = self.build_pipeline()
        self._model.fit(X, y)
        self._trained_samples = int(len(y))

        return {"trained": True, "samples": self._trained_samples}

    def predict_coefficient(self, features: Dict) -> Dict:
        """
        Predict a coefficient based on features.
        Safe fallback if not enabled/trained.
        """
        if not self.is_enabled:
            return {"coefficient": 1.0, "reason": "ML disabled"}

        if self._model is None:
            return {"coefficient": 1.0, "reason": "ML not trained"}

        x = self._features_to_vector(features).reshape(1, -1)
        pred = float(self._model.predict(x)[0])

        # Safety clamp
        pred = max(0.8, min(1.2, pred))

        return {"coefficient": round(pred, 3), "reason": "ML prediction (ridge regression)"}
