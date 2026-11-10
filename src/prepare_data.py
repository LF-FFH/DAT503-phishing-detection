"""Datenaufbereitung: Phishing Pot (Phishing) + Enron-Spam (nur Ham).

Erzeugt data/processed/emails.csv mit den Spalten
    id, source, label (1 = Phishing, 0 = legitim), subject, body, text

Aufruf:
    python src/prepare_data.py --phishing data/raw/phishing_pot --enron data/raw/enron_spam_data
"""
from __future__ import annotations

import argparse
import email
import html
import re
import zipfile
from email import policy
from pathlib import Path

import pandas as pd

URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.I)
# Enron-Texte sind vortokenisiert ("http : / / www . juno . com"), daher eigenes Muster
SPACED_URL_RE = re.compile(r"\b(?:https?\s*:\s*/\s*/|www\s*\.)\s*[\w-]+(?:\s*[./]\s*[\w-]+)*", re.I)
MAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
# Phishing Pot anonymisiert Empfänger als "phishing@pot" (ohne Punkt in der Domain).
# Ohne diese Regel lernt das Modell den Platzhalter statt Phishing-Merkmale (Datenleck).
ANON_RE = re.compile(r"\bphishing\s*@\s*pot\b", re.I)
NUM_RE = re.compile(r"\b\d[\d.,]*\b")
TAG_RE = re.compile(r"(?s)<(script|style)[^>]*>.*?</\1>|<[^>]+>")
WS_RE = re.compile(r"\s+")
# Langer Zeichensalat ohne Leerzeichen (Base64-Reste, Tracking-Strings)
JUNK_RE = re.compile(r"\b\S{40,}\b")

MAX_CHARS = 5000  # Texte kürzen, damit Training und LLM-Kosten überschaubar bleiben


def normalize(text: str) -> str:
    """Gleiche Normalisierung für beide Quellen, um Quellen-Artefakte zu reduzieren."""
    text = html.unescape(TAG_RE.sub(" ", text))
    text = URL_RE.sub(" <URL> ", text)
    text = SPACED_URL_RE.sub(" <URL> ", text)
    text = ANON_RE.sub(" <EMAIL> ", text)
    text = MAIL_RE.sub(" <EMAIL> ", text)
    text = JUNK_RE.sub(" ", text)
    text = NUM_RE.sub(" <NUM> ", text)
    return WS_RE.sub(" ", text).strip()[:MAX_CHARS]


def parse_eml(path: Path) -> tuple[str, str]:
    with path.open("rb") as fh:
        msg = email.message_from_binary_file(fh, policy=policy.default)
    subject = str(msg.get("subject", "") or "")
    body = ""
    try:
        part = msg.get_body(preferencelist=("plain", "html"))
        if part is not None:
            body = part.get_content()
    except Exception:  # defekte Kodierungen kommen in echten Phishing-Mails häufig vor
        body = ""
    return subject, body


def load_phishing(root: Path) -> pd.DataFrame:
    rows = []
    for p in sorted((root / "email").glob("*.eml")):
        subject, body = parse_eml(p)
        rows.append({"id": f"pp_{p.stem}", "source": "phishing_pot", "label": 1,
                     "subject": subject, "body": body})
    return pd.DataFrame(rows)


def load_enron_ham(root: Path) -> pd.DataFrame:
    with zipfile.ZipFile(root / "enron_spam_data.zip") as zf:
        with zf.open("enron_spam_data.csv") as fh:
            df = pd.read_csv(fh)
    df = df[df["Spam/Ham"] == "ham"].fillna("")
    return pd.DataFrame({
        "id": "enron_" + df["Message ID"].astype(str),
        "source": "enron_ham",
        "label": 0,
        "subject": df["Subject"].astype(str),
        "body": df["Message"].astype(str),
    })


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phishing", type=Path, default=Path("data/raw/phishing_pot"))
    ap.add_argument("--enron", type=Path, default=Path("data/raw/enron_spam_data"))
    ap.add_argument("--out", type=Path, default=Path("data/processed/emails.csv"))
    args = ap.parse_args()

    df = pd.concat([load_phishing(args.phishing), load_enron_ham(args.enron)], ignore_index=True)
    df["subject"] = df["subject"].map(normalize)
    df["body"] = df["body"].map(normalize)
    df["text"] = (df["subject"] + " \n " + df["body"]).str.strip()

    n_before = len(df)
    df = df[df["text"].str.len() >= 20]                 # leere/kaputte Mails entfernen
    df = df.drop_duplicates(subset="text")              # Duplikate verfälschen die Evaluation
    print(f"Mails geladen: {n_before}, nach Bereinigung: {len(df)}")
    print(df.groupby("source").size().to_string())

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Gespeichert: {args.out}")


if __name__ == "__main__":
    main()
