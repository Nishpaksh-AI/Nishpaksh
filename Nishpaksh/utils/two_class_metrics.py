# metrics.py

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances


class GroupMetrics:
    """
    Performance metrics based on confusion matrix.
    """

    def __init__(self, y_true, y_pred):
        self.y_true = np.array(y_true)
        self.y_pred = np.array(y_pred)
        self._compute_confusion_metrics()

    def _compute_confusion_metrics(self):
        y_true, y_pred = self.y_true, self.y_pred

        self.TP = np.sum((y_true == 1) & (y_pred == 1))
        self.TN = np.sum((y_true == 0) & (y_pred == 0))
        self.FP = np.sum((y_true == 0) & (y_pred == 1))
        self.FN = np.sum((y_true == 1) & (y_pred == 0))

        self.ACC = (self.TP + self.TN) / len(y_true)
        self.TPR = self.TP / (self.TP + self.FN) if (self.TP + self.FN) > 0 else 0
        self.TNR = self.TN / (self.TN + self.FP) if (self.TN + self.FP) > 0 else 0
        self.FPR = self.FP / (self.FP + self.TN) if (self.FP + self.TN) > 0 else 0
        self.FNR = self.FN / (self.FN + self.TP) if (self.FN + self.TP) > 0 else 0
        self.PPV = self.TP / (self.TP + self.FP) if (self.TP + self.FP) > 0 else 0
        self.NPV = self.TN / (self.TN + self.FN) if (self.TN + self.FN) > 0 else 0
        self.FDR = self.FP / (self.FP + self.TP) if (self.FP + self.TP) > 0 else 0
        self.FOR = self.FN / (self.FN + self.TN) if (self.FN + self.TN) > 0 else 0

    def get_all(self):
        return {
        "TP": int(self.TP),
        "TN": int(self.TN),
        "FP": int(self.FP),
        "FN": int(self.FN),
        "Accuracy": round(self.ACC, 4),
        "TPR (Recall)": round(self.TPR, 4),
        "TNR": round(self.TNR, 4),
        "FPR": round(self.FPR, 4),
        "FNR": round(self.FNR, 4),
        "Precision (PPV)": round(self.PPV, 4),
        "NPV": round(self.NPV, 4),
        "FDR": round(self.FDR, 4),
        "FOR": round(self.FOR, 4)
    }



class FairnessMetrics:
    """
    Fairness metrics based on sensitive attributes.
    Includes group-level disparities and individual-level fairness.
    """

    def __init__(self, y_true, y_pred, sensitive_attr, X=None, model=None, sensitive_attr_indices=None, privileged_value=1):
        self.y_true = np.array(y_true)
        self.y_pred = np.array(y_pred)
        self.sensitive_attr = np.array(sensitive_attr)
        self.X = X
        self.model = model
        self.sensitive_attr_indices = sensitive_attr_indices
        self.privileged_value = privileged_value

    # Group fairness
    def statistical_parity_difference(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        p_priv = np.mean(self.y_pred[priv] == 1)
        p_unpriv = np.mean(self.y_pred[unpriv] == 1)
        return p_unpriv - p_priv

    def disparate_impact(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        p_priv = np.mean(self.y_pred[priv] == 1)
        p_unpriv = np.mean(self.y_pred[unpriv] == 1)
        return p_unpriv / p_priv if p_priv > 0 else 0

    def thiel_index(self):
        df = pd.DataFrame({'pred': self.y_pred, 'group': self.sensitive_attr})
        group_means = df.groupby('group')['pred'].mean()
        overall_mean = df['pred'].mean()
        if overall_mean == 0:
            return 0
        terms = (group_means / overall_mean) * np.log(group_means / overall_mean)
        weights = df['group'].value_counts(normalize=True).sort_index()
        return (terms * weights).sum()

    def cohens_d(self):
        df = pd.DataFrame({'score': self.y_pred, 'group': self.sensitive_attr})
        groups = df['group'].unique()
        if len(groups) != 2:
            raise ValueError("Cohen's d requires exactly two groups")
        s1 = df[df['group'] == groups[0]]['score']
        s2 = df[df['group'] == groups[1]]['score']
        mean_diff = s1.mean() - s2.mean()
        pooled_std = np.sqrt((s1.var() + s2.var()) / 2)
        return mean_diff / pooled_std if pooled_std > 0 else 0

    # Label fairness
    def equal_opportunity_difference(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        tpr_priv = np.mean(self.y_pred[priv & (self.y_true == 1)] == 1)
        tpr_unpriv = np.mean(self.y_pred[unpriv & (self.y_true == 1)] == 1)
        return tpr_unpriv - tpr_priv

    def average_odds_difference(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        tpr_diff = np.mean(self.y_pred[unpriv & (self.y_true == 1)] == 1) - \
                   np.mean(self.y_pred[priv & (self.y_true == 1)] == 1)
        fpr_diff = np.mean(self.y_pred[unpriv & (self.y_true == 0)] == 1) - \
                   np.mean(self.y_pred[priv & (self.y_true == 0)] == 1)
        return 0.5 * (tpr_diff + fpr_diff)

    def error_rate_difference(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        err_priv = np.mean(self.y_pred[priv] != self.y_true[priv])
        err_unpriv = np.mean(self.y_pred[unpriv] != self.y_true[unpriv])
        return err_unpriv - err_priv

    def equalized_odds(self):
        tpr_diff = self.equal_opportunity_difference()
        fpr_diff = np.mean(self.y_pred[(self.sensitive_attr != self.privileged_value) & (self.y_true == 0)] == 1) - \
                   np.mean(self.y_pred[(self.sensitive_attr == self.privileged_value) & (self.y_true == 0)] == 1)
        return 0.5 * (abs(tpr_diff) + abs(fpr_diff))

    def fairness_through_awareness(self):
        if self.X is None:
            raise ValueError("X must be provided for fairness_through_awareness")
        sim_matrix = euclidean_distances(self.X)
        diffs = []
        for i in range(len(self.y_pred)):
            for j in range(i + 1, len(self.y_pred)):
                if sim_matrix[i, j] < 0.1:  # highly similar
                    diffs.append(abs(self.y_pred[i] - self.y_pred[j]))
        return np.mean(diffs) if diffs else 0

    def counterfactual_fairness(self):
        if self.model is None or self.X is None or self.sensitive_attr_indices is None:
            raise ValueError("model, X, and sensitive_attr_indices must be provided for counterfactual_fairness")
        X_flipped = self.X.copy()
        for i in self.sensitive_attr_indices:
            X_flipped[:, i] = 1 - X_flipped[:, i]  # flip binary sensitive features
        preds_orig = self.model.predict(self.X)
        preds_flipped = self.model.predict(X_flipped)
        return np.mean(preds_orig != preds_flipped)
     # ============================

# ============================

    # ----------------------------
    # Selection rate fairness
    # ----------------------------
    def selection_rate_difference(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        sr_priv = np.mean(self.y_pred[priv] == 1)
        sr_unpriv = np.mean(self.y_pred[unpriv] == 1)
        return sr_unpriv - sr_priv

    def selection_rate_ratio(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        sr_priv = np.mean(self.y_pred[priv] == 1)
        sr_unpriv = np.mean(self.y_pred[unpriv] == 1)
        return sr_unpriv / sr_priv if sr_priv > 0 else 0


    # ----------------------------
    # Error-rate parity metrics
    # ----------------------------
    def false_positive_rate_difference(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        fpr_priv = np.mean(self.y_pred[priv & (self.y_true == 0)] == 1)
        fpr_unpriv = np.mean(self.y_pred[unpriv & (self.y_true == 0)] == 1)
        return fpr_unpriv - fpr_priv

    def false_negative_rate_difference(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        fnr_priv = np.mean(self.y_pred[priv & (self.y_true == 1)] == 0)
        fnr_unpriv = np.mean(self.y_pred[unpriv & (self.y_true == 1)] == 0)
        return fnr_unpriv - fnr_priv


    # ----------------------------
    # Accuracy parity
    # ----------------------------
    def accuracy_difference(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        acc_priv = np.mean(self.y_pred[priv] == self.y_true[priv])
        acc_unpriv = np.mean(self.y_pred[unpriv] == self.y_true[unpriv])
        return acc_unpriv - acc_priv

    def accuracy_ratio(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        acc_priv = np.mean(self.y_pred[priv] == self.y_true[priv])
        acc_unpriv = np.mean(self.y_pred[unpriv] == self.y_true[unpriv])
        return acc_unpriv / acc_priv if acc_priv > 0 else 0


    # ----------------------------
    # Predictive value parity
    # ----------------------------
    def precision_difference(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        ppv_priv = np.mean(self.y_true[priv & (self.y_pred == 1)] == 1)
        ppv_unpriv = np.mean(self.y_true[unpriv & (self.y_pred == 1)] == 1)
        return ppv_unpriv - ppv_priv

    def negative_predictive_value_difference(self):
        priv = self.sensitive_attr == self.privileged_value
        unpriv = ~priv
        npv_priv = np.mean(self.y_true[priv & (self.y_pred == 0)] == 0)
        npv_unpriv = np.mean(self.y_true[unpriv & (self.y_pred == 0)] == 0)
        return npv_unpriv - npv_priv


    # ----------------------------
    # Generalized Entropy Index 
    # ----------------------------
    def generalized_entropy_index(self, alpha=2):
        df = pd.DataFrame({'pred': self.y_pred, 'group': self.sensitive_attr})
        group_means = df.groupby('group')['pred'].mean()
        overall_mean = df['pred'].mean()

        if overall_mean == 0:
            return 0

        if alpha == 0:
            terms = -np.log(group_means / overall_mean)
        elif alpha == 1:
            terms = (group_means / overall_mean) * np.log(group_means / overall_mean)
        else:
            terms = ((group_means / overall_mean) ** alpha - 1) / (alpha * (alpha - 1))

        weights = df['group'].value_counts(normalize=True).sort_index()
        return (terms * weights).sum()


    # ----------------------------
    # Consistency (Individual fairness)
    # ----------------------------
    def consistency(self, k=5):
        if self.X is None:
            raise ValueError("X must be provided for consistency")

        from sklearn.neighbors import NearestNeighbors
        nbrs = NearestNeighbors(n_neighbors=k + 1).fit(self.X)
        _, indices = nbrs.kneighbors(self.X)

        diffs = []
        for i in range(len(self.y_pred)):
            neighbors = indices[i][1:]
            diffs.append(np.mean(np.abs(self.y_pred[i] - self.y_pred[neighbors])))
        return 1 - np.mean(diffs)


# ============================
# UPDATE get_all() METHOD
# ============================

    def get_all(self):
        metrics = {
            "Statistical Parity Difference": self.statistical_parity_difference(),
            "Disparate Impact": self.disparate_impact(),
            "Selection Rate Difference": self.selection_rate_difference(),
            "Selection Rate Ratio": self.selection_rate_ratio(),
            "Thiel Index": self.thiel_index(),
            "Generalized Entropy (α=2)": self.generalized_entropy_index(alpha=2),
            "Equal Opportunity Difference": self.equal_opportunity_difference(),
            "Average Odds Difference": self.average_odds_difference(),
            "False Positive Rate Difference": self.false_positive_rate_difference(),
            "False Negative Rate Difference": self.false_negative_rate_difference(),
            "Error Rate Difference": self.error_rate_difference(),
            "Accuracy Difference": self.accuracy_difference(),
            "Accuracy Ratio": self.accuracy_ratio(),
            "Precision Difference": self.precision_difference(),
            "NPV Difference": self.negative_predictive_value_difference(),
            "Equalized Odds": self.equalized_odds(),
        }

        if self.X is not None:
            metrics["Fairness Through Awareness"] = self.fairness_through_awareness()
            metrics["Consistency"] = self.consistency()

        if self.model is not None and self.sensitive_attr_indices is not None:
            metrics["Counterfactual Fairness"] = self.counterfactual_fairness()

        return metrics


