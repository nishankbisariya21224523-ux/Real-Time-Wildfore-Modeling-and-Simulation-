# Risk Model Evaluation Report: `risk-xgboost-v001`

- **Model Name:** risk-xgboost
- **Algorithm:** XGBoost
- **Created At:** 2026-10-06T09:25:34.820916+00:00
- **Dataset Version:** features
- **Random Seed:** 42

## 1. Dataset & Temporal Split

- **Training Period:** 2026-05-15 to 2026-05-15
- **Validation Period:** 2026-05-15 to 2026-05-15
- **Total Evaluated Samples:** 668
- **Positive Fire Samples:** 1 (0.15%)
- **Negative Non-Fire Samples:** 667
- **Class Imbalance Strategy:** `scale_pos_weight` (scale_pos_weight = 999.0)

## 2. Classification Performance Metrics

| Metric | Value |
|---|---|
| **Accuracy** | 0.9985 |
| **Precision** | 0.0000 |
| **Recall** | 0.0000 |
| **F1-Score** | 0.0000 |
| **ROC-AUC** | 0.8658 |
| **PR-AUC** | 0.0092 |

### Confusion Matrix

| | Predicted Negative (0) | Predicted Positive (1) |
|---|---|---|
| **Actual Negative (0)** | True Negatives: **667** | False Positives: **0** |
| **Actual Positive (1)** | False Negatives: **1** | True Positives: **0** |

## 3. Top Feature Importance (Descriptive)

| Rank | Feature Name | Relative Importance |
|---|---|---|
| 1 | `dist_to_recent_fire_m` | 0.2813 |
| 2 | `slope_deg` | 0.2137 |
| 3 | `wind_speed_ms` | 0.1596 |
| 4 | `elevation_m` | 0.1595 |
| 5 | `fwi` | 0.0759 |
| 6 | `relative_humidity_pct` | 0.0758 |
| 7 | `ndvi` | 0.0208 |
| 8 | `temperature_c` | 0.0133 |
| 9 | `aspect_deg` | 0.0000 |
| 10 | `aspect_sin` | 0.0000 |

> **Note on Feature Importance:** Importance values indicate relative predictive split utility within the trained tree ensemble and do **not** imply direct causality.

## 4. Hyperparameters

```json
{
  "n_estimators": 100,
  "max_depth": 5,
  "learning_rate": 0.05,
  "subsample": 0.8,
  "colsample_bytree": 0.8,
  "reg_alpha": 0.1,
  "reg_lambda": 1.0,
  "random_state": 42,
  "objective": "binary:logistic",
  "eval_metric": "logloss",
  "tree_method": "hist",
  "scale_pos_weight": 999.0
}
```

## 5. Known Scientific & Practical Limitations

1. **Baseline Tabular Model:** Does not model spatio-temporal graph propagation or deep visual raster contexts (deferred to future spatial research).
2. **Threshold Sensitivity:** Probability classifications rely on standard engineering thresholds [0.25, 0.50, 0.75]; operational field thresholds must be calibrated with local forest division SOPs.
3. **Resolution:** Predictions operate at 500m × 500m spatial grid partition. Sub-pixel micro-topographical variations are aggregated.
4. **Sample Data Disclaimer:** If trained on development sample data, metrics demonstrate software correctness and pipeline reproducibility rather than operational field efficacy.
