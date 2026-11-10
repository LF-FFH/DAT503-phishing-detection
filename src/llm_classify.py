"""LLM-Klassifikator (Zero-Shot) über die Anthropic-API – Vergleich zur Baseline.

Klassifiziert eine stratifizierte Stichprobe aus DEMSELBEN Testsplit wie die Baseline
(results/test_split_ids.csv) sowie die OOD-Mails (data/ood_legit_emails.csv).

Voraussetzung:  export ANTHROPIC_API_KEY=...
Aufruf:         python src/llm_classify.py --n 200 --model claude-haiku-5-5

Reproduzierbarkeit:
- feste Stichprobe (Seed 42), temperature=0, Prompt versioniert in prompts/
- jede Antwort wird in results/llm_raw.jsonl gespeichert; erneute Läufe verwenden den
  Cache und rufen die API nur für fehlende Mails auf
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

from prepare_data import normalize

SEED = 42
PROMPT = Path("prompts/llm_classifier_prompt.md")
CACHE = Path("results/llm_raw.jsonl")
OUT = Path("results")


def load_cache() -> dict:
    if not CACHE.exists():
        return {}
    with CACHE.open(encoding="utf-8") as fh:
        return {r["id"]: r for r in map(json.loads, fh)}


def classify(client, model: str, system: str, text: str) -> dict:
    resp = client.messages.create(
        model=model, max_tokens=200, temperature=0, system=system,
        messages=[{"role": "user", "content": f"<email>\n{text[:4000]}\n</email>"}],
    )
    raw = resp.content[0].text.strip()
    try:
        parsed = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
        label = 1 if str(parsed.get("label", "")).lower() == "phishing" else 0
    except ValueError:
        parsed, label = {}, None          # nicht parsebare Antwort -> im Protokoll auswerten
    return {"raw": raw, "label_pred": label, "reason": parsed.get("reason", "")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200, help="Stichprobengröße aus dem Testsplit")
    ap.add_argument("--model", default="claude-haiku-5-5")
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY ist nicht gesetzt.")
    import anthropic
    client = anthropic.Anthropic()
    system = PROMPT.read_text(encoding="utf-8")

    df = pd.read_csv("data/processed/emails.csv").fillna("")
    test_ids = pd.read_csv(OUT / "test_split_ids.csv")
    test = df[df["id"].isin(test_ids["id"])]
    sample = pd.concat([test[test["label"] == lab].sample(
        n=min(int((test["label"] == lab).sum()), args.n // 2), random_state=SEED) for lab in (0, 1)])

    ood = pd.read_csv("data/ood_legit_emails.csv")
    ood = pd.DataFrame({"id": ood["id"], "label": 0,
                        "text": ood["raw"].str.replace(r"^Subject:\s*", "", regex=True).map(normalize)})
    items = pd.concat([sample[["id", "label", "text"]], ood], ignore_index=True)

    cache = load_cache()
    with CACHE.open("a", encoding="utf-8") as fh:
        for i, row in enumerate(items.itertuples(), 1):
            if row.id in cache:
                continue
            res = classify(client, args.model, system, row.text)
            rec = {"id": row.id, "label_true": int(row.label), "model": args.model, **res}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            cache[row.id] = rec
            print(f"[{i}/{len(items)}] {row.id}: {res['label_pred']}")

    res = pd.DataFrame([cache[i] for i in items["id"]])
    res.to_csv(OUT / "llm_predictions.csv", index=False)

    test_res = res[~res["id"].str.startswith("ood")]
    ok = test_res.dropna(subset=["label_pred"])
    y, p = ok["label_true"].astype(int), ok["label_pred"].astype(int)
    ood_res = res[res["id"].str.startswith("ood")]
    metrics = {
        "model": args.model,
        "n_sample": int(len(test_res)),
        "n_unparseable": int(test_res["label_pred"].isna().sum()),
        "accuracy": accuracy_score(y, p), "precision": precision_score(y, p),
        "recall": recall_score(y, p), "f1": f1_score(y, p),
        "confusion_matrix [[TN, FP], [FN, TP]]": confusion_matrix(y, p).tolist(),
        "ood_false_positive_rate": float((ood_res["label_pred"] == 1).mean()),
    }
    (OUT / "llm_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
