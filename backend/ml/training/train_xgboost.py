# Train XGBoost + Evaluate Metrics

# * Train XGBoost (primary model)
# * Use time-based split
# * Compute Accuracy, Precision, Recall, F1
# * Save model + features + metadata

import json
import joblib
import pandas as pd
from datetime import datetime

from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from ml.data.build_training_dataset import build_training_dataset


def train_xgboost(csv_path: str, window_size: int = 7):
    """
    Train XGBoost model on fraud detection task.
    
    Args:
        csv_path: Path to transactions CSV
        window_size: Number of previous transactions to use in each window (default: 7)
    """
    # ---------------- Load training data ----------------
    df = build_training_dataset(csv_path, window_size=window_size)

    # Sort by time (CRITICAL)
    df = df.sort_values("window_end").reset_index(drop=True)

    # Separate features and label
    feature_cols = [
        c for c in df.columns
        if c not in ["user_id", "window_start", "window_end", "label"]
    ]

    X = df[feature_cols]
    y = df["label"]

    # ---------------- Time-based split ----------------
    split_idx = int(len(df) * 0.7)

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # ---------------- Handle class imbalance ----------------
    pos = y_train.sum()
    neg = len(y_train) - pos
    scale_pos_weight = neg / pos if pos > 0 else 1.0

    # ---------------- Train XGBoost ----------------
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        base_score = y_train.mean(),  # 🔑 FIX
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42
    )

    model.fit(X_train, y_train)

    # ---------------- Evaluate ----------------
    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
    }

    print("Evaluation Metrics:")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    # ---------------- Save model & metadata ----------------
    model_dir = "ml/models/xgboost"
    import os
    os.makedirs(model_dir, exist_ok=True)

    joblib.dump(model, f"{model_dir}/model.pkl")

    with open(f"{model_dir}/feature_list.json", "w") as f:
        json.dump(feature_cols, f, indent=2)

    metadata = {
        "model": "XGBoost",
        "window_type": "N-transaction",
        "window_size": window_size,
        "train_date": datetime.utcnow().isoformat(),
        "metrics": metrics
    }

    with open(f"{model_dir}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return metrics