# Module : ai_trainer
# Purpose : training pipeline. It reads historical data, calculate what happened after changes, updates ai weights,
#           saves a new version of weights in learning_store.py (enabling rollback)
from collections import defaultdict
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.utils.logger import ai_logger
from app.database import learning_store
# In the future we have to import from learning_store.py and sales_history.py (not existing yet)

# ---------------------------------------------------------
# Base types (placeholders)
# ---------------------------------------------------------
TrainingExample = Dict[str, Any]
Weights = Dict[str, float]
Metrics = Dict[str, Any]
ai_logger = ai_logger

# ---------------------------------------------------------
# 0) Main trainer entry point PIPELINE
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
        "snapshot_id": snapshot_id,
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
            "stock": 10,
            "days_to_expiry": 2,
            "velocity": 1.5,
        },
        {
            "product_id": 2,
            "old_price": 3.0,
            "new_price": 2.5,
            "units_before": 15,
            "units_after": 7,
            "stock": 15,
            "days_to_expiry": 5,
            "velocity": 0.8,
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
    # FEATURE-SPECIFIC VALUES
    # ---------------------------------------

    # Stock
    stock_weighted_st = 0.0
    stock_weight_sum = 0.0

    # MHD
    mhd_weighted_st = 0.0
    mhd_weight_sum = 0.0

    # Velocity
    velocity_weighted_st = 0.0
    velocity_weight_sum = 0.0

    # ---------------------------------------
    # OPERATIONS
    # ---------------------------------------
    for ex in examples:
        units_before = float(ex.get("units_before"))
        units_after = float(ex.get("units_after"))
        product_id = ex.get("product_id")

        if units_before <= 0 or product_id is None:
            continue

        # Feature data for weights
        stock = float(ex.get("stock", units_before))
        days_to_expiry = float(ex.get("days_to_expiry", 0))
        velocity = float(ex.get("velocity", 0.0))

        # ---------------------------------------
        # SELL THROUGH
        # ---------------------------------------

        # Calculate the sell through in percentage
        sell_through = (units_before - units_after) / units_before

        # ---------- GLOBAL st for every example/session
        total_st += sell_through
        global_count += 1

        # ---------- PRODUCT st for every
        per_product_sum[product_id] += sell_through
        per_product_count[product_id] += 1

        # ---------------------------------------
        # EFFECTS
        # ---------------------------------------

        # ---------- STOCK EFFECT
        stock_value = max(stock, 0.0)
        if stock_value > 0.0:
            stock_weighted_st += sell_through * stock_value
            stock_weight_sum += stock_value

        # ---------- MHD EFFECT
        safe_days = max(days_to_expiry, 0)
        mhd_weight = 1.0 / (1.0 + safe_days)
        mhd_weighted_st += sell_through * mhd_weight
        mhd_weight_sum += mhd_weight

        # ---------- VELOCITY EFFECT
        safe_velocity = max(velocity, 0.0)
        vel_weight = 1.0 / (1.0 + safe_velocity)
        velocity_weighted_st += sell_through * vel_weight
        velocity_weight_sum += vel_weight

    # ---------- AVG SELL THROUGH
    # Normal AVG
    avg_sell_through = total_st / global_count if global_count > 0 else 0.0

    # ---------------------------------------
    # OUTPUT PREP
    # ---------------------------------------

    # ---------- DICT FOR PRODUCT
    per_product_metrics: Dict[Any, Dict[str, float]] = {}
    for pid, product_total_st in per_product_sum.items():
        count = per_product_count[pid]
        per_product_metrics[pid] = {
            # Normal AVG
            "avg_sell_through": product_total_st / count if count > 0 else 0.0,
            "num_examples": float(count),
        }

    # ---------- EFFECT FOR FEATURES AND FALLBACK
    stock_effect = (
        stock_weighted_st / stock_weight_sum
        if stock_weight_sum > 0.0 else avg_sell_through
    )
    mhd_effect = (
        mhd_weighted_st / mhd_weight_sum
        if mhd_weight_sum > 0.0 else avg_sell_through
    )
    velocity_effect = (
        velocity_weighted_st / velocity_weight_sum
        if velocity_weight_sum > 0.0 else avg_sell_through
    )

    # ---------- METRICS FOR LOG AND RETURN
    metrics: Metrics = {
        "avg_sell_through": avg_sell_through,
        "num_examples": float(global_count),
        "per_product": per_product_metrics,
        "stock_effect": stock_effect,
        "mhd_effect": mhd_effect,
        "velocity_effect": velocity_effect,
    }

    ai_logger.debug(f"[AI TRAINER] Metrics={metrics}")
    return metrics

# ---------------------------------------------------------
# 3) Loading current weights
# ---------------------------------------------------------
def _load_current_weights() -> Weights:
    # Loading weights from DB
    db_weights = learning_store.load_current_weights()

    if db_weights:
        ai_logger.debug(f"[AI TRAINER] Current weights (from DB): {db_weights}")
        return db_weights

    # Fallback di sicurezza se non ci sono pesi nel DB
    default = {
        "w_stock": 1.0,
        "w_mhd": 1.0,
        "w_velocity": 1.0,
        "w_base": 1.0,
    }
    ai_logger.warning("[AI TRAINER] No weights in DB, using default=%s", default)
    return default
# ---------------------------------------------------------
# 3) Update weights
# ---------------------------------------------------------
def _update_weights(
        current_weights: Weights,
        metrics: Metrics,
        learning_rate: float
) -> Weights:
    # ---------- Global metrics and for features
    avg_sell_through = float(metrics.get("avg_sell_through", 0.0))
    stock_effect = float(metrics.get("stock_effect", avg_sell_through))
    mhd_effect = float(metrics.get("mhd_effect", avg_sell_through))
    velocity_effect = float(metrics.get("velocity_effect", avg_sell_through))

    new_weights = current_weights.copy()

    # We set here an ideal value (0.7 sell through)
    # It is made to measure if th AI has to become more or less aggressive
    target_sell_through = 0.7

    # Map: weight -> metrics  to be used
    feature_effect = {
        "w_stock": stock_effect,
        "w_mhd": mhd_effect,
        "w_velocity": velocity_effect,
    }

    # For cycle writte like this is an elegant form to update more keys. It works well with Dict
    # key: weight's name (w_stock, w_mhd...), effect: associated metric (stock_effect, mhd_effect...)
    for key, effect in (feature_effect.items()):

        # 1) It takes here the actual value of the weight
        old_value = float(new_weights.get(key, 1.0))
        # 2) It calculate the error fot that feature
        error = target_sell_through - effect
        # 3) Update the new value
        # Classic formula for gradient update, used a lot in machine learning
        # Leaning rate defines here how quick AI learns: higher value means bigger changes, bigger wins or bigger mistakes
        new_value = old_value + learning_rate * error
        # 4) Apply security limits
        new_value = max(0.1, min(new_value, 5.0))
        # 5) Save new weight
        new_weights[key] = new_value

    ai_logger.debug(
        "[AI TRAINER] Weights update | old=%s, new=%s,"
        "stock_effect=%.4f, mhd_effect=%.4f, velocity_effect=%.4f",
        current_weights,
        new_weights,
        stock_effect,
        mhd_effect,
        velocity_effect
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
) -> int:
    note = f"AI training on {reference_date.isoformat()}"

    snapshot_id = learning_store.save_new_weights_snapshot(
        new_weights=new_weights,
        note=note,
    )

    if snapshot_id == -1:
        ai_logger.error(
            "[AI TRAINER] Error saving weights snapshot | metrics=%s | old=%s | new=%s",
            metrics,
            old_weights,
            new_weights,
        )
    else:
        ai_logger.info(
            "[AI TRAINER] Snapshot saved | id=%s | metrics=%s | old=%s | new=%s",
            snapshot_id,
            metrics,
            old_weights,
            new_weights,
        )

    return snapshot_id

# ---------------------------------------------------------
# TESTING
# ---------------------------------------------------------
if __name__ == "__main__":
    result = train_once()

    print("\n========== AI TRAINER SUMMARY ==========")
    print(f"Status        : {result.get('status')}")
    print(f"Snapshot ID   : {result.get('snapshot_id') or result.get('snaposhot_id')}")
    print(f"Num examples  : {result.get('num_examples')}")

    print("\n--- Metrics ---")
    metrics = result.get("metrics", {})
    print(f"  Avg sell-through  : {metrics.get('avg_sell_through'):.4f}")
    print(f"  Stock effect      : {metrics.get('stock_effect'):.4f}")
    print(f"  MHD effect        : {metrics.get('mhd_effect'):.4f}")
    print(f"  Velocity effect   : {metrics.get('velocity_effect'):.4f}")
    print(f"  Per-product       : {metrics.get('per_product')}")

    print("\n--- Weights ---")
    print(f"  Old weights : {result.get('old_weights')}")
    print(f"  New weights : {result.get('new_weights')}")

    print("========================================\n")