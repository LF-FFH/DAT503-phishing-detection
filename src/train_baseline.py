"""Klassischer ML-Klassifikator: TF-IDF + Logistische Regression.

Zwei Varianten werden trainiert und verglichen:
  A  "naiv"   – Text wie aufbereitet
  B  "robust" – Shortcut-Merkmale entfernt (Enron-Weiterleitungsköpfe, Enron-Namen/Kürzel,
                nur englischsprachige Mails), damit das Modell nicht die Datenquelle statt
                Phishing lernt

Ausgabe in results/: metrics.json, top_features_<variante>.csv, confusion_<variante>.png,
ood_predictions.csv (Plausibilitätstest mit selbst geschriebenen, modernen legitimen Mails),
test_split_ids.csv (für den LLM-Vergleich auf identischen Testdaten).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from prepare_data import normalize

SEED = 42
DATA = Path("data/processed/emails.csv")
OOD = Path("data/ood_legit_emails.csv")
OUT = Path("results")

# Begriffe, die nur in der Enron-Quelle vorkommen (Organisationskürzel, häufige Namen,
# Weiterleitungs-Metadaten). Sie verraten die Quelle, nicht ob eine Mail Phishing ist.
ENRON_TOKENS = {
    "enron", "ect", "hou", "corp", "ees", "ena", "vince", "kaminski", "louise", "kitchen",
    "sally", "beck", "daren", "farmer", "jeff", "dasovich", "forwarded", "cc", "subject",
    "fyi", "re", "fw", "fwd", "pm", "am", "lon", "na", "hpl", "kay", "mann", "steven",
}
FWD_BLOCK_RE = re.compile(r"(?s)-\s*-\s*-.*?subject\s*:")   # "- - - forwarded by ... subject :"
NON_EN_RE = re.compile(r"\b(?:und|nicht|ihr|sie|der|die|das|você|não|para|seu|sua|le|vous|est)\b", re.I)


def make_pipeline(stop_words: set[str] | None = None) -> Pipeline:
    vec = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=3, max_df=0.9,
                          sublinear_tf=True, max_features=50_000,
                          token_pattern=r"(?u)<?\b\w\w+\b>?",
                          stop_words=sorted(stop_words) if stop_words else None)
    clf = LogisticRegression(max_iter=2000, C=4.0, class_weight="balanced", random_state=SEED)
    return Pipeline([("tfidf", vec), ("clf", clf)])


def robust_text(s: pd.Series) -> pd.Series:
    return s.str.lower().str.replace(FWD_BLOCK_RE, " ", regex=True)


def evaluate(name, pipe, X_test, y_test) -> dict:
    proba = pipe.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    m = {
        "variant": name,
        "n_test": int(len(y_test)),
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred),
        "recall": recall_score(y_test, pred),
        "f1": f1_score(y_test, pred),
        "roc_auc": roc_auc_score(y_test, proba),
        "confusion_matrix [[TN, FP], [FN, TP]]": confusion_matrix(y_test, pred).tolist(),
    }
    ConfusionMatrixDisplay(confusion_matrix(y_test, pred),
                           display_labels=["legitim", "Phishing"]).plot(cmap="Blues", colorbar=False)
    plt.title(f"Variante {name}")
    plt.tight_layout()
    plt.savefig(OUT / f"confusion_{name}.png", dpi=150)
    plt.close()
    return m


def top_features(name, pipe, k=25):
    vec, clf = pipe.named_steps["tfidf"], pipe.named_steps["clf"]
    names = np.array(vec.get_feature_names_out())
    coef = clf.coef_[0]
    order = np.argsort(coef)
    rows = [{"richtung": "Phishing", "merkmal": names[i], "gewicht": round(coef[i], 3)}
            for i in order[::-1][:k]]
    rows += [{"richtung": "legitim", "merkmal": names[i], "gewicht": round(coef[i], 3)}
             for i in order[:k]]
    pd.DataFrame(rows).to_csv(OUT / f"top_features_{name}.csv", index=False)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = pd.read_csv(DATA).fillna("")

    # Ein gemeinsamer, stratifizierter Split (80/20) für alle Varianten und das LLM
    train_idx, test_idx = train_test_split(df.index, test_size=0.2, stratify=df["label"],
                                           random_state=SEED)
    df.loc[test_idx, ["id", "label"]].to_csv(OUT / "test_split_ids.csv", index=False)
    print(f"Train: {len(train_idx)}  Test: {len(test_idx)}")

    metrics = []

    # Variante A: naiv
    pipe_a = make_pipeline()
    pipe_a.fit(df.loc[train_idx, "text"], df.loc[train_idx, "label"])
    metrics.append(evaluate("A_naiv", pipe_a, df.loc[test_idx, "text"], df.loc[test_idx, "label"]))
    top_features("A_naiv", pipe_a)

    # Variante B: robust (Shortcuts entfernt, nur englische Mails)
    df["text_b"] = robust_text(df["text"])
    english = ~df["text"].str.contains(NON_EN_RE.pattern, case=False, regex=True)
    tr_b = [i for i in train_idx if english[i]]
    te_b = [i for i in test_idx if english[i]]
    pipe_b = make_pipeline(stop_words=ENRON_TOKENS)
    pipe_b.fit(df.loc[tr_b, "text_b"], df.loc[tr_b, "label"])
    metrics.append(evaluate("B_robust", pipe_b, df.loc[te_b, "text_b"], df.loc[te_b, "label"]))
    top_features("B_robust", pipe_b)

    # Plausibilitätstest außerhalb der Trainingsverteilung (OOD): moderne legitime Mails
    ood = pd.read_csv(OOD)
    ood["text"] = ood["raw"].str.replace(r"^Subject:\s*", "", regex=True).map(normalize)
    ood["p_phishing_A"] = pipe_a.predict_proba(ood["text"])[:, 1].round(3)
    ood["p_phishing_B"] = pipe_b.predict_proba(robust_text(ood["text"]))[:, 1].round(3)
    ood.to_csv(OUT / "ood_predictions.csv", index=False)
    for v in ("A", "B"):
        fp = int((ood[f"p_phishing_{v}"] >= 0.5).sum())
        print(f"OOD Variante {v}: {fp}/{len(ood)} legitime Mails fälschlich als Phishing erkannt")
        metrics.append({"variant": f"{v}_ood_legit", "n_test": len(ood),
                        "false_positive_rate": fp / len(ood)})

    with open(OUT / "metrics.json", "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, ensure_ascii=False, default=float)
    print(json.dumps(metrics, indent=2, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
