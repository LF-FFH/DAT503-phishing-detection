# Dokumentation des KI-Einsatzes

Die Lehrveranstaltung behandelt KI-unterstütztes Engineering. Deshalb wird hier offengelegt, wofür im
Projekt ein KI-Assistent eingesetzt wurde und wie die Ergebnisse geprüft wurden.

| Datum | Werkzeug | Aufgabe | Menschliche Prüfung / Entscheidung |
|---|---|---|---|
| 10.11.2026 | Claude (Anthropic), Agent-Modus | Aufgabenstellung gelesen, Themenvarianten vorgeschlagen | Variante „Phishing-Erkennung“ von Lucas Frank gewählt |
| 10.11.2026 | Claude | Datensatzsuche, Download-Skript mit fixierten Commits | Datensatzwahl und Lizenzen geprüft |
| 10.11.2026 | Claude | Code für Datenaufbereitung, Baseline und LLM-Skript geschrieben und ausgeführt | Code-Review und eigener Lauf mit `make all`: *[nach Prüfung abhaken]* |
| 10.11.2026 | Claude | Datenleck (`phishing@pot`) und vortokenisierte Enron-URLs anhand der Top-Merkmale gefunden und behoben | Analyse nachvollzogen: *[ ]* |
| 10.11.2026 | Claude | Entwürfe für Anforderungsdokument, Projektplan, Protokoll und Ergebnisbericht | Inhalte überarbeitet, Platzhalter ergänzt: *[ ]* |

**Erkenntnis zum KI-Einsatz:** Der Assistent hat den Code schnell und lauffähig geliefert. Das Datenleck
fiel aber erst auf, als die Top-Merkmale des Modells gezielt geprüft wurden. Eine hohe Accuracy allein war
kein Qualitätsnachweis. Die menschliche Kontrolle der Zwischenergebnisse bleibt notwendig.

Die 12 OOD-Testmails in `data/ood_legit_emails.csv` sind **synthetisch** (vom KI-Assistenten nach
Vorgabe formuliert). Sie stellen typische moderne legitime Mails dar und sind keine echten Mails.
