# KI-gestützte Phishing-Erkennung

**DAT503 – AI assisted Engineering · FernFH ITMA · ESA 1 (Abgabe 15.11.2026)**
Anwendungsbereich: Cybersicherheit

Das Projekt untersucht, wie gut KI-Verfahren Phishing-Mails allein am Text erkennen. Es vergleicht
ein klassisches ML-Modell (TF-IDF + Logistische Regression) mit einem LLM (Zero-Shot) auf öffentlichen,
versionierten Datensätzen. Schwerpunkt sind **nachvollziehbare und reproduzierbare Ergebnisse**.

## Ergebnisse auf einen Blick

| | F1 (Testsplit) | Fehlalarme bei modernen legitimen Mails |
|---|---|---|
| Baseline A (naiv) | 0,991 | 4 von 12 |
| Baseline B (Quellen-Merkmale entfernt) | 0,983 | 4 von 12 |
| LLM (Claude Haiku) | *ausstehend* | *ausstehend* |

Die hohen Testwerte sind wegen der Datenlage zu optimistisch, siehe [Ergebnisse](docs/05_Ergebnisse.md).

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [01 Anforderungsdokument](docs/01_Anforderungsdokument.md) | Bedarfsanalyse, funktionale und nicht-funktionale Anforderungen, Technologie-Matrix |
| [02 Projektplan](docs/02_Projektplan.md) | Meilensteine, Gantt, Rollen, Kommunikation, Risiken |
| [03 Projektprotokoll](docs/03_Projektprotokoll.md) | alle Tätigkeiten, ungelöste Herausforderungen mit Gründen, Beiträge |
| [04 KI-Einsatz](docs/04_KI-Einsatz.md) | Offenlegung der KI-Unterstützung |
| [05 Ergebnisse](docs/05_Ergebnisse.md) | Metriken, Merkmalsanalyse, OOD-Test, Interpretation |

## Reproduzieren

Voraussetzungen: Python 3.11+, git, ca. 3 GB freier Speicher.

```bash
python3 -m venv .venv && source .venv/bin/activate
make setup      # Pakete in fixierten Versionen
make all        # Daten laden (fixe Commits) -> aufbereiten -> Baseline trainieren (ca. 2 Min.)

# optional: LLM-Vergleich (ca. 212 API-Anfragen)
export ANTHROPIC_API_KEY=...
make llm
```

Fixiert sind: Datensatz-Commits (`scripts/fetch_data.sh`), Paketversionen (`requirements.txt`),
Zufalls-Seed 42, Train/Test-Split (`results/test_split_ids.csv`), LLM-Prompt (`prompts/`) und
`temperature=0`. Die LLM-Antworten werden in `results/llm_raw.jsonl` gespeichert.

## Struktur

```
├── data/ood_legit_emails.csv     12 synthetische moderne legitime Mails (Realitätscheck)
├── docs/                         Anforderungen, Plan, Protokoll, KI-Einsatz, Ergebnisse
├── prompts/                      versionierter LLM-Prompt
├── results/                      Metriken, Konfusionsmatrizen, Top-Merkmale
├── scripts/fetch_data.sh         Download der Datensätze in fixer Version
└── src/
    ├── prepare_data.py           .eml/CSV parsen, HTML entfernen, normalisieren, deduplizieren
    ├── train_baseline.py         TF-IDF + LogReg, Varianten A/B, OOD-Test
    └── llm_classify.py           Zero-Shot-LLM auf identischem Testsplit
```

## Daten und Lizenzen

- [Phishing Pot](https://github.com/rf-peixoto/phishing_pot) – echte Phishing-Mails, CC BY-NC 4.0
- [Enron-Spam (Aufbereitung M. Wiechmann)](https://github.com/MWiechmann/enron_spam_data) – nur Ham, GPL-3.0;
  Original: Metsis, Androutsopoulos & Paliouras (2006)

Die Rohdaten sind nicht im Repo enthalten und werden per Skript geladen. Die Nutzung erfolgt nur zu
Studienzwecken (nicht kommerziell).
