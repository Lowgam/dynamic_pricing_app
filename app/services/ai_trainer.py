# Module : ai_trainer
# Purpose : training pipeline. It reads historical data, calculate what happened after changes, updates ai weights,
#           saves a new version of weights in learning_store.py (enabling rollback)
from collections import defaultdict
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.utils.logger import ai_logger
# In the future we have to import from learning_store.py and sales_history.py (not existing yet)

# ---------------------------------------------------------
# Base types (placeholders)
# ---------------------------------------------------------
TrainingExample = Dict[str, Any]
Weights = Dict[str, float]
Metrics = Dict[str, float]
ai_logger = ai_logger

# ---------------------------------------------------------
# Main trainer entry point PIPELINE
# ---------------------------------------------------------
def train_once(
        reference_date: Optional[date] = None,
        lookback_days: int = 14,
        # Learning rate is a value that says how quickly AI is modifying the prices
        # High rate : aggressive ai. We want to set it low, so it doesn't change the prices crazily for a single strange day
        learning_rate: float = 0.1,
) -> Dict[str, Any]:
    # We configure here the function to execute a training session
    if reference_date is None:
        reference_date = date.today()

    ai_logger.info(
        f"[AI TRAINER] Start | ref_date={reference_date}, "
        f"lookback={lookback_days}, lr={learning_rate}"
    )

    # 1) Historical data
    example = _load_training_examples(reference_date, lookback_days)
    if not example:
        ai_logger.warning("[AI TRAINER] No training examples found")
        return {
            "status": "no_data",
            "message": "No training examples found",
            "num_examples": 0,
        }

    # 2) Metrics
    metrics = _compute_metrics(example)

    # 3) Current weights
    current_weights = _load_current_weights()
    if not current_weights:
        current_weights = {
            "w_stock": 1.0,
            "w_mhd": 1.0,
            "w_velocity": 1.0,
            "w_base": 1.0,
        }

    # 4) New weights
    new_weights = _update_weights(current_weights, metrics, learning_rate)

    # 5) Save snapshots
    snapshot_id = _save_weights_snapshot(
        old_weights = current_weights,
        new_weights = new_weights,
        reference_date = reference_date,
        metrics = metrics,
    )

    ai_logger.info(
        f"[AI TRAINER] Completed | snapshot={snapshot_id},"
        f"example={len(example)}, "
    )

    return {
        "status": "success",
        "snaposhot_id": snapshot_id,
        "num_examples": len(example),
        "metrics": metrics,
        "old_weights": current_weights,
        "new_weights": new_weights,
    }

# ---------------------------------------------------------
# 1) Load training data (placeholder)
# ---------------------------------------------------------
def _load_training_examples(reference_date: date, lookback_days: int) -> List[TrainingExample]:
    start = reference_date - timedelta(days=lookback_days)
    ai_logger.debug(
        f"[AI TRAINER] Loading training examples from {reference_date}, ")

    return[
        {
            "product_id": 1,
            "old_price": 5.0,
            "new_price": 4.0,
            "units_before": 10,
            "units_after": 3,
            "days_to_expiry": 2,
        },
        {
            "product_id": 2,
            "old_price": 3.0,
            "new_price": 2.5,
            "units_before": 15,
            "units_after": 7,
            "days_to_expiry": 5,
        }
    ]

# ---------------------------------------------------------
# 2) Aggregated metrics
# ---------------------------------------------------------
def _compute_metrics(examples: List[TrainingExample]) -> Metrics:
    # It calculates here metrics like medium sell-through
    # Sell through indicates how much has been sold after a certain period

    # Protection to avoid later / 0 cases
    if not examples:
        return {}

    # ---------------------------------------
    # GLOBAL VALUES
    # ---------------------------------------

    # Total sell through of all products for a training-session
    total_st = 0.0
    # How many example / events are being analysed
    global_count = 0

    # ---------------------------------------
    # PRODUCT VALUES
    # ---------------------------------------

    # Total sell through for every product analysed in this training-session
    per_product_sum = defaultdict(float)
    # How many examples / events are being analysed for the product
    # It is possible that in 14 days (lookback) we changed many times the price. We might have different price-change-event
    per_product_count = defaultdict(int)

    # ---------------------------------------
    # OPERATIONS
    # ---------------------------------------
    for ex in examples:
        units_before = float(ex.get("units_before"))
        units_after = float(ex.get("units_after"))
        product_id = ex.get("product_id")

        if units_before <= 0 or product_id is None:
            continue

        # Calculate the sell through in percentage
        sell_through = (units_before - units_after) / units_before

        # GLOBAL st for every example/session
        total_st += sell_through
        global_count += 1

        # PRODUCT st for every
        per_product_sum[product_id] += sell_through
        per_product_count[product_id] += 1

    avg_sell_through = total_st / global_count if global_count > 0 else 0.0

    # Dict for product
    per_product_metrics: Dict[Any, Dict[str, float]] = {}
    for pid, product_total_st in per_product_sum.items():
        count = per_product_count[pid]
        per_product_metrics[pid] = {
            "avg_sell_through": product_total_st / count if count > 0 else 0.0,
            "num_examples": float(count),
        }

    metrics: Metrics = {
        "avg_sell_through": avg_sell_through,
        "num_examples": float(global_count),
        "per_product": per_product_metrics,
    }

    ai_logger.debug(f"[AI TRAINER] Metrics={metrics}")
    return metrics

# ---------------------------------------------------------
# 3) Loading current weights (placeholder)
# ---------------------------------------------------------
def _load_current_weights() -> Weights:
    default = {
        "w_stock": 1.0,
        "w_mhd": 1.0,
        "w_velocity": 1.0,
        "w_base": 1.0,
    }
    ai_logger.debug(f"[AI TRAINER] Current weights (default): {default}")
    return default

# ---------------------------------------------------------
# 3) Update weights (placeholder)
# ---------------------------------------------------------
def _update_weights(
        current_weights: Weights,
        metrics: Metrics,
        learning_rate: float
) -> Weights:
    avg_sell_through = metrics.get("avg_sell_through", 0.0)

    new_weights = current_weights.copy()

    # We set here an ideal value (0.7 sell through)
    # It is made to measure if th AI has to become more or less aggressive
    target_sell_through = 0.7
    error = target_sell_through - avg_sell_through

    # For cycle writte like this is an elegant form to update more keys. It works well with Dict
    for key in ("w_stock", "w_mhd", "w_velocity"):
        old_value = new_weights.get(key, 1.0)
        # Classic formula for gradient update, used a lot in machine learning
        # Leaning rate defines here how quick AI learns: higher value means bigger changes, bigger wins or bigger mistakes
        new_value = old_value + learning_rate * error

        new_weights[key] = new_value

    ai_logger.debug(
        "Weights update | old=%s, new=%s, error=%.4f",
        current_weights,
        new_weights,
        error,
    )
    return new_weights

# ---------------------------------------------------------
# 3) Snapshot new weights
# ---------------------------------------------------------
def _save_weights_snapshot(
        old_weights: Weights,
        new_weights: Weights,
        reference_date: date,
        metrics: Metrics,
) -> str:
    # It saves the values in a store. It is useful for rollbacks for AI weights

    # TODO integrate with learning_store.save_new_weights_snapshot(...)
    snapshot_id = f"snapshot-{reference_date.isoformat()}"

    ai_logger.info(
        "Snapshot pesi salvati (FAKE) | id=%s | metrics=%s | old_weights=%s | new_weights=%s",
        snapshot_id,
        metrics,
        old_weights,
        new_weights,
    )

    return snapshot_id

# ---------------------------------------------------------
# Test manuale da terminale
# ---------------------------------------------------------
if __name__ == "__main__":
    result = train_once()
    print(result)