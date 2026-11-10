# Projektprotokoll

Jede durchgeführte Aufgabe wird hier eingetragen, **auch Probleme und nicht gelöste Herausforderungen
mit Begründung**. Jeder Eintrag nennt, wer ihn durchgeführt hat (Bewertungskriterium *Transparenz*).

## Einträge

| Datum | Wer | Tätigkeit | Ergebnis / Problem |
|---|---|---|---|
| 10.11.2026 | Lucas Frank | Themenwahl: Cybersicherheit, Variante „KI-gestützte Phishing-Erkennung“ statt Honeypot/Täuschung | Begründung: in 5 Tagen reproduzierbar umsetzbar, Praxisbezug zu Security Awareness. *[Ggf. Rückfrage beim Lektor dokumentieren: Das Thema ist keines der drei Beispiele.]* |
| 10.11.2026 | Lucas Frank (mit KI-Unterstützung, siehe `04_KI-Einsatz.md`) | Repository-Struktur, Anforderungsdokument v0.1, Projektplan | Dokumente in `docs/` |
| 10.11.2026 | Lucas Frank (mit KI-Unterstützung) | Datensatzsuche | **Problem:** Hugging Face und Kaggle waren aus der Arbeitsumgebung nicht erreichbar (HTTP 403 am Proxy). **Lösung:** Phishing Pot und Enron-Spam aus GitHub-Repositories, fixiert über Commit-Hashes in `scripts/fetch_data.sh`. |
| 10.11.2026 | Lucas Frank (mit KI-Unterstützung) | Datenaufbereitung `src/prepare_data.py` | 29.409 Mails geladen. Nach dem Entfernen leerer Mails und Duplikate bleiben 22.966 (8.430 Phishing, 14.536 legitim). Viele Phishing-Mails sind Duplikate derselben Kampagne. |
| 10.11.2026 | Lucas Frank (mit KI-Unterstützung) | Baseline TF-IDF + LogReg, erster Lauf | Accuracy 99,4 %. **Auffällig:** Unter den Top-Merkmalen waren „enron“, „vince“ (Enron-Mitarbeiter) und „phishing pot“. |
| 10.11.2026 | Lucas Frank (mit KI-Unterstützung) | Fehleranalyse Datenleck | **Problem 1:** Phishing Pot anonymisiert Empfänger als `phishing@pot`. Der Platzhalter steht in 1.522 Phishing-Mails, und das Modell hat ihn gelernt. **Problem 2:** In Enron sind URLs vortokenisiert (`http : / / www . juno . com`), sodass „http“/„www“ zu Merkmalen für *legitim* wurden. **Lösung:** beide Muster in `normalize()` vereinheitlicht und neu trainiert. |
| 10.11.2026 | Lucas Frank (mit KI-Unterstützung) | Variante B (robust): Enron-Namen und -Kürzel als Stoppwörter, Weiterleitungsköpfe entfernt, nur englische Mails | F1 sinkt leicht von 0,991 auf 0,983. Die Leistung hängt also nur wenig an den offensichtlichen Quellen-Merkmalen. |
| 10.11.2026 | Lucas Frank (mit KI-Unterstützung) | OOD-Test mit 12 selbst geschriebenen, modernen legitimen Mails | **4 von 12 als Phishing erkannt** (Versandbestätigung, Passwort-Reset, Anmeldehinweis, Support-Ticket). Ziel NFR-02 (≤ 10 %) **verfehlt**. Siehe ungelöste Herausforderung H1. |
| 10.11.2026 | Lucas Frank (mit KI-Unterstützung) | LLM-Klassifikator `src/llm_classify.py` | Mit simuliertem API-Client getestet (Ablauf und Cache funktionieren). Ein echter Lauf war nicht möglich, weil kein API-Key verfügbar war (H2). |
| *[Datum]* | *[Name]* | *[Interviews Bedarfsanalyse]* | *[Ergebnisse]* |
| *[Datum]* | *[Name]* | *[LLM-Lauf mit `make llm`]* | *[Metriken aus results/llm_metrics.json]* |
| *[Datum]* | *[Name]* | *[Teammeeting]* | *[Beschlüsse]* |

## Nicht gelöste Herausforderungen

| ID | Herausforderung | Detaillierte Gründe | Mögliche Lösung |
|---|---|---|---|
| H1 | Modell erkennt moderne, legitime Transaktionsmails (Passwort-Reset, Login-Hinweis, Versandinfo) als Phishing | Die legitimen Trainingsdaten (Enron) stammen aus 2000–2005 und enthalten kaum automatisierte Service-Mails. Diese Mails ähneln sprachlich genau den Phishing-Vorlagen („your account“, Link, Handlungsaufforderung). Mit reinem Textinhalt ist die Unterscheidung grundsätzlich schwer, weil der Unterschied oft nur im Absender und im Link-Ziel liegt. | Aktuelle legitime Mails ergänzen (z. B. eigene Newsletter-/Service-Mails, anonymisiert), Header-, SPF/DKIM- und URL-Merkmale einbeziehen (FR-07) |
| H2 | LLM-Vergleich noch nicht ausgeführt | In der Arbeitsumgebung war kein API-Key für die Anthropic-API vorhanden, und über die Kosten muss im Team entschieden werden. | Lauf durch ein Teammitglied mit Key (`make llm`, ca. 212 Anfragen) |
| H3 | Klassen stammen aus unterschiedlichen Quellen | Es gab keinen frei erreichbaren Datensatz, der Phishing und legitime Mails aus derselben Zeit und Umgebung enthält. Der sehr hohe Testwert (F1 ≈ 0,99) ist deshalb wahrscheinlich zu optimistisch. | Ergebnisse vorsichtig interpretieren; OOD-Test als realistischere Messung heranziehen |
| H4 | Legitime Mails nur auf Englisch | Enron enthält keine deutschen Mails, deutsche Phishing-Mails ließen sich daher nicht fair bewerten. | In Variante B nur englische Mails verwenden; deutsche legitime Mails ergänzen |
| H5 | Transformer-Modell (DistilBERT) nicht umgesetzt | Hugging Face war nicht erreichbar, Zeitrahmen 5 Tage | Erweiterung für ESA 2 |

## Beiträge der Gruppenmitglieder

| Mitglied | Rolle | Beiträge (mit Verweis auf Protokolleinträge / Commits) |
|---|---|---|
| Lucas Frank | *[Rolle]* | Themenwahl, Repo-Aufbau, Datenaufbereitung, Baseline, Fehleranalyse, Dokumentation (mit KI-Unterstützung) |
| *[Mitglied 2]* | *[Rolle]* | *[ ]* |
| *[Mitglied 3]* | *[Rolle]* | *[ ]* |
