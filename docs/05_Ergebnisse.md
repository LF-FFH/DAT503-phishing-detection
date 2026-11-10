# Ergebnisse und Interpretation

Stand: 10.11.2026. Alle Zahlen stammen aus `results/metrics.json` und lassen sich mit `make all` reproduzieren.

## 1. Datensatz

| | Anzahl |
|---|---|
| geladen | 29.409 (12.864 Phishing, 16.545 legitim) |
| nach Bereinigung (leer < 20 Zeichen, Duplikate) | **22.966** (8.430 Phishing, 14.536 legitim) |
| Training / Test (stratifiziert 80/20, Seed 42) | 18.372 / 4.594 |

## 2. Baseline: TF-IDF + Logistische Regression

| Variante | Testmenge | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|---|
| A naiv | 4.594 | 0,993 | 0,991 | 0,991 | 0,991 | 0,9996 |
| B robust (ohne Enron-Merkmale, nur Englisch) | 3.930 | 0,991 | 0,984 | 0,983 | 0,983 | 0,9992 |

Konfusionsmatrizen: `results/confusion_A_naiv.png`, `results/confusion_B_robust.png`

- A: 15 Fehlalarme, 16 übersehene Phishing-Mails
- B: 17 Fehlalarme, 18 übersehene Phishing-Mails

NFR-01 (Precision und Recall ≥ 0,95) ist auf dem Testsplit **erfüllt**.

## 3. Was hat das Modell gelernt?

Top-Merkmale aus `results/top_features_*.csv`:

| | Richtung Phishing | Richtung legitim |
|---|---|---|
| A naiv | `<email>`, your, unsubscribe, account, wallet, claim, details, payment, „your account“ | **enron**, **vince**, **louise**, thanks, attached, gas |
| B robust | `<email>`, your, unsubscribe, account, claim, wallet, details, `<url>`, payment | thanks, attached, gas, energy, **houston** |

- Variante A nutzt Namen von Enron-Mitarbeitenden. Das sind reine Quellen-Merkmale (Shortcut Learning).
- In B sind sie entfernt. Trotzdem bleiben Branchenbegriffe von Enron („gas“, „energy“, „houston“). Ganz
  ohne Quellen-Effekt lässt sich der Datensatz also nicht verwenden.
- Plausible Phishing-Merkmale: persönliche Anrede mit Mail-Adresse (`<email>`), „your account“,
  Krypto-Begriffe (wallet, claim) und Zahlungsaufforderungen.
- Vor der Korrektur des Datenlecks war „phishing pot“ (der Anonymisierungs-Platzhalter des Datensatzes)
  ein Top-Merkmal. Details stehen im Protokoll.

## 4. Realitätscheck: moderne legitime Mails (OOD-Test)

12 synthetische, aber typische legitime Mails von heute (`data/ood_legit_emails.csv`):

| Mail | p(Phishing) A | p(Phishing) B | Urteil |
|---|---|---|---|
| Team-Meeting | 0,04 | 0,03 | ✅ |
| **Versandbestätigung Shop** | 0,72 | 0,77 | ❌ Fehlalarm |
| **Angeforderter Passwort-Reset** | 0,87 | 0,87 | ❌ Fehlalarm |
| Rechnung Lieferant | 0,18 | 0,21 | ✅ |
| IT-Wartungsankündigung | 0,19 | 0,18 | ✅ |
| Kollegenanfrage | 0,09 | 0,08 | ✅ |
| Newsletter Uni | 0,22 | 0,19 | ✅ |
| Kalendereinladung | 0,26 | 0,22 | ✅ |
| **Hinweis auf neue Anmeldung** | 0,99 | 0,99 | ❌ Fehlalarm |
| HR-Erinnerung | 0,35 | 0,32 | ✅ |
| **Support-Ticket** | 0,52 | 0,50 | ❌ Fehlalarm (knapp) |
| Konferenzanmeldung | 0,13 | 0,13 | ✅ |

**False-Positive-Rate: 4/12 = 33 %.** NFR-02 (≤ 10 %) ist **nicht erfüllt**.

## 5. Interpretation

1. **Die hohen Testwerte überschätzen die echte Leistung.** Training und Test stammen aus denselben zwei
   Quellen. Das Modell trennt deshalb auch „Enron 2001“ von „Phishing 2025“. Der OOD-Test zeigt die
   Grenze: Gerade die Mails, die Angreifer am häufigsten nachahmen (Passwort-Reset, Login-Warnung,
   Paketinfo), werden falsch eingestuft.
2. **Text allein reicht für diese Fälle nicht.** Ein echter und ein gefälschter Passwort-Reset können
   wortgleich sein. Unterscheiden lassen sie sich über Absender-Domain, SPF/DKIM und Link-Ziel. Diese
   Merkmale fehlen im Prototyp bewusst (Scope, FR-07).
3. **Merkmalsanalyse ist Pflicht.** Ohne Blick auf die Gewichte wäre das Datenleck (`phishing@pot`)
   unbemerkt geblieben. Die Accuracy hätte trotzdem 99 % gezeigt.

## 6. LLM-Vergleich

*Ausstehend (siehe Protokoll H2).* Nach `make llm` hier eintragen:

| Modell | Stichprobe | Accuracy | Precision | Recall | F1 | OOD-FPR |
|---|---|---|---|---|---|---|
| TF-IDF + LogReg (A) | 4.594 | 0,993 | 0,991 | 0,991 | 0,991 | 33 % |
| *[claude-haiku-5-5]* | *[200]* | *[ ]* | *[ ]* | *[ ]* | *[ ]* | *[ ]* |

Hypothese: Das LLM ist auf dem Testsplit etwas schwächer, weil es die Datensatz-Eigenheiten nicht lernt.
Auf den OOD-Mails sollte es aber deutlich weniger Fehlalarme erzeugen.

## 7. Erweiterungen

- aktuelle legitime Mails ergänzen (gleiche Zeit, gleiche Sprache)
- Header-, Authentifizierungs- und URL-Merkmale (Domain-Alter, Lookalike-Domains)
- Transformer-Modell (DistilBERT) feinabstimmen
- Kombination: schnelle Baseline filtert vor, das LLM begründet unsichere Fälle (0,3 < p < 0,7)
