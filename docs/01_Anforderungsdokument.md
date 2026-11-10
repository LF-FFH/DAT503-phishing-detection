# Anforderungsdokument – KI-gestützte Phishing-Erkennung

| | |
|---|---|
| Lehrveranstaltung | DAT503 – AI assisted Engineering (FernFH, ITMA) |
| Einsendeaufgabe | ESA 1, Abgabe 15.11.2026 |
| Version | 0.2 (10.11.2026) |
| Verantwortlich | Requirements Engineering: *[Name eintragen]* |

## 1. Ausgangslage und Problem

Phishing ist einer der häufigsten Einstiegswege für Angriffe auf Organisationen. Klassische
E-Mail-Filter arbeiten mit Signaturen, Reputationslisten (Absender, Domains, URLs) und festen Regeln.
Sie erkennen neue Kampagnen oft erst, wenn diese bereits bekannt und gemeldet sind. Zudem erreichen
täuschend echte Mails (z. B. gefälschte Passwort-Resets, Rechnungen, Paketbenachrichtigungen) weiterhin
die Postfächer, wo die Erkennung beim Menschen liegt.

**Ziel des Projekts:** Untersuchen, wie gut KI-Verfahren Phishing-Mails allein anhand von Betreff und
Text erkennen. Dabei wird ein klassisches ML-Verfahren mit einem Large Language Model (LLM)
verglichen, und zwar reproduzierbar und mit offen dokumentierten Grenzen.

## 2. Stakeholder und Bedarfsanalyse

| Stakeholder | Interesse |
|---|---|
| Mitarbeitende (Empfänger:innen) | weniger Phishing im Postfach, wenige Fehlalarme bei echten Mails |
| IT-Security / SOC | frühe Erkennung neuer Kampagnen, nachvollziehbare Begründung pro Treffer |
| Security-Awareness-Team | Erkenntnisse, welche Merkmale Phishing ausmachen (für Schulungen und Simulationen) |
| Datenschutz / Compliance | keine Weitergabe von Mail-Inhalten an Dritte ohne Rechtsgrundlage |

**Methode:** Kurzinterviews (je ca. 15 Min.) mit 2–3 Personen aus IT-Security bzw. Security Awareness.
Leitfaden:

1. Welche Phishing-Mails kommen aktuell durch die bestehenden Filter?
2. Was kostet ein Fehlalarm (echte Mail landet in Quarantäne) im Vergleich zu einer übersehenen Phishing-Mail?
3. Wie schnell muss eine Entscheidung vorliegen (Zustellung in Echtzeit oder nachgelagerte Analyse)?
4. Welche Begründung braucht ein Analyst, um einem KI-Urteil zu vertrauen?
5. Dürfen Mail-Inhalte an einen Cloud-Dienst (LLM-API) übermittelt werden?

**Ergebnisse:** *[Nach den Interviews eintragen: Datum, Rolle der befragten Person, Kernaussagen.
Keine erfundenen Ergebnisse eintragen. Falls keine Interviews möglich sind, im Protokoll begründen.]*

## 3. Funktionale Anforderungen

| ID | Anforderung | Priorität | Status Prototyp |
|---|---|---|---|
| FR-01 | Das System muss eine E-Mail (Betreff + Text) als *Phishing* oder *legitim* klassifizieren. | Muss | erfüllt |
| FR-02 | Das System muss zu jeder Entscheidung eine Wahrscheinlichkeit bzw. Konfidenz ausgeben. | Muss | erfüllt (Baseline), LLM nur Label |
| FR-03 | Das System muss die Entscheidung erklärbar machen (einflussreiche Merkmale oder Begründung). | Soll | erfüllt (Top-Merkmale, LLM-Begründung) |
| FR-04 | Das System muss HTML-Mails in Klartext umwandeln und URLs, Mail-Adressen und Zahlen vereinheitlichen. | Muss | erfüllt |
| FR-05 | Das System soll deutsch- und englischsprachige Mails verarbeiten. | Soll | teilweise (Ham-Daten nur Englisch) |
| FR-06 | Das System muss ein klassisches ML-Modell und ein LLM auf identischen Testdaten vergleichen. | Muss | Code fertig, LLM-Lauf ausstehend |
| FR-07 | Das System soll Absender-Header, SPF/DKIM und Link-Ziele auswerten. | Kann | nicht umgesetzt (außerhalb Scope) |

## 4. Nicht-funktionale Anforderungen

| ID | Anforderung | Messgröße / Ziel |
|---|---|---|
| NFR-01 Erkennungsleistung | Hohe Erkennungsrate bei wenigen Fehlalarmen | Recall ≥ 0,95 **und** Precision ≥ 0,95 auf dem Testsplit |
| NFR-02 Generalisierung | Moderne legitime Mails dürfen nicht systematisch als Phishing gelten | False-Positive-Rate auf OOD-Testmails ≤ 10 % |
| NFR-03 Antwortzeit | Klassifikation einer Mail | Baseline < 100 ms, LLM < 5 s |
| NFR-04 Reproduzierbarkeit | Gleiche Ergebnisse bei erneutem Lauf | fixierte Datensatz-Commits, Seeds, Paketversionen, `make all` |
| NFR-05 Kosten | Betrieb im Studienkontext | Baseline kostenlos; LLM-Lauf (200 Mails) unter 2 € |
| NFR-06 Datenschutz | Keine echten Mails aus Organisationen der Teammitglieder | nur öffentliche Datensätze |
| NFR-07 Nachvollziehbarkeit | Jede Entscheidung im Projekt dokumentiert | Projektprotokoll, KI-Einsatz-Log |

## 5. Daten

| Quelle | Inhalt | Lizenz | Verwendung |
|---|---|---|---|
| [Phishing Pot](https://github.com/rf-peixoto/phishing_pot) (Commit `78be141`) | 12.864 echte Phishing-Mails (.eml), 2022–2026, mehrsprachig | CC BY-NC 4.0 | Klasse *Phishing* |
| [Enron-Spam](https://github.com/MWiechmann/enron_spam_data) (Commit `e73c300`) | 16.545 legitime Geschäftsmails (Ham), ca. 2000–2005, Englisch | GPL-3.0 (Aufbereitung) | Klasse *legitim* |

Bekannte Schwächen, die das Ergebnis beeinflussen:
- Beide Klassen stammen aus **unterschiedlichen Quellen und Jahrzehnten**. Ein Modell kann deshalb die
  Quelle statt Phishing lernen. Gegenmaßnahmen: Variante B, Merkmalsanalyse, OOD-Test.
- Phishing Pot enthält auch Scam- und Spam-Mails (z. B. Kreditangebote). Das Label „Phishing“ ist also weit gefasst.
- Legitime Mails liegen nur auf Englisch vor.

## 6. Technologische Bewertung

Bewertung 1 (schlecht) bis 5 (sehr gut).

| Option | Erkennungsleistung | Erklärbarkeit | Skalierbarkeit | Benutzerfreundlichkeit | Kosten | Datenschutz | Reproduzierbarkeit | Summe |
|---|---|---|---|---|---|---|---|---|
| **TF-IDF + Logistische Regression** (scikit-learn) | 4 | 5 | 5 | 5 | 5 | 5 | 5 | **34** |
| Naive Bayes (scikit-learn) | 3 | 4 | 5 | 5 | 5 | 5 | 5 | 32 |
| Feinabgestimmtes Transformer-Modell (DistilBERT, Hugging Face) | 5 | 2 | 3 | 3 | 3 | 5 | 4 | 25 |
| **LLM Zero-Shot über API** (Anthropic Claude Haiku) | 4 | 4 | 3 | 5 | 3 | 2 | 3 | **24** |
| Lokales LLM (z. B. über Ollama) | 3 | 4 | 2 | 3 | 4 | 5 | 4 | 25 |
| Kommerzieller Mail-Security-Dienst | 5 | 2 | 5 | 4 | 1 | 2 | 1 | 20 |

**Entscheidung:**
- **Baseline:** TF-IDF + Logistische Regression. Sie ist schnell, kostenlos, vollständig reproduzierbar
  und über die Modellgewichte direkt erklärbar.
- **Vergleich:** LLM Zero-Shot (Claude Haiku). Es braucht kein Training, liefert Begründungen in Textform
  und zeigt, ob ein vortrainiertes Modell besser generalisiert. Ein Nachteil ist der Datenschutz bei
  echten Mails, deshalb werden nur öffentliche Daten verwendet (NFR-06).
- **Verworfen:** DistilBERT. Hugging Face war in der Projektumgebung nicht erreichbar, und die
  verfügbare Zeit reichte nicht (siehe Protokoll). Es bleibt eine Erweiterung.

## 7. Abgrenzung (Out of Scope)

Keine Integration in einen Mailserver, keine Auswertung von Headern, Anhängen oder Link-Zielen,
kein Produktivbetrieb, keine Verarbeitung echter Unternehmensmails.

## 8. Versionshistorie

| Version | Datum | Änderung | Autor:in |
|---|---|---|---|
| 0.1 | 10.11.2026 | Erstfassung: Anforderungen, Technologie-Matrix | Lucas Frank |
| 0.2 | 10.11.2026 | Datenschwächen und Status Prototyp ergänzt | Lucas Frank |
