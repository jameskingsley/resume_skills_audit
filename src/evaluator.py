import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score

def precision_at_k(df, col, k=3):
    top = df.sort_values(col, ascending=False).groupby("candidate_id").head(k)
    return float(top.groupby("candidate_id").shortlisted.mean().mean())

def evaluate_model(model, X_test, y_test, test_df):
    preds = model.predict_proba(X_test)[:, 1]
    test_eval = test_df.copy()
    test_eval["ml_score"] = preds
    test_eval["keyword_overlap"] += np.random.default_rng(0).random(len(test_eval)) * 1e-3

    metrics = {
        "roc_auc_ml": float(roc_auc_score(y_test, preds)),
        "roc_auc_keyword": float(roc_auc_score(test_eval.shortlisted, test_eval.keyword_overlap)),
        "precision_at_3_ml": precision_at_k(test_eval, "ml_score", 3),
        "precision_at_3_keyword": precision_at_k(test_eval, "keyword_overlap", 3),
    }
    return metrics