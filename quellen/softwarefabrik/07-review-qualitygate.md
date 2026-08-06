# 7. Review-Schicht und Quality Gate

Dies ist die Umsetzung dessen, was das Whitepaper v1.3 als „Guardrails
Pipeline" beschreibt (Kapitel 12, ADR-3) — mit einer wesentlichen
architektonischen Präzisierung.

## 7.1 Die Kernidee: ein zweiter Schichtbegriff

```
ExecutionAdapter (schreibt)  ──►  Diff
                                    │
                                    ▼
                         ReviewAdapter (read-only) × N
                                    │
                                    ▼
                         QualityGate (Aggregation)
                                    │
                                    ▼
                        PASSED · WARNING · FAILED · ERROR
```

Coding-Agenten **schreiben** Code; Review-Adapter **prüfen** ihn und dürfen
ihn nicht verändern. Diese Trennung ist der eigentliche Gehalt der
Guardrail-Idee: Ein System, in dem dieselbe Instanz erzeugt und freigibt, hat
kein Gate, sondern eine Selbsteinschätzung.

## 7.2 Die sechs Review-Adapter

| Adapter | Art | Prüft |
|---|---|---|
| `claude-review` | LLM (read-only-Prompt) | Diff-Review durch Claude Code im `--print`-Modus |
| `aider-review` | LLM (read-only-Prompt) | Diff-Review durch Aider |
| `security` | statisch | API-Keys, Path-Traversal, SQL-Konkatenation, `Runtime.exec`, Passwort-Logging; CRITICAL bei Vendor-Key-Präfixen (`AKIA`, `AIza`, `sk-proj`, `sk-ant`) |
| `architecture-reviewer` | statisch | Web/Repository ohne Service, JPA-Importe in der Domänenschicht, **Änderungen an bestehenden Flyway-Migrationen (CRITICAL)** |
| `hallucination-review` | statisch | TODO/FIXME-Marker, „tests pass"-Behauptungen ohne Teständerung, unberührte Akzeptanzkriterien, Importe nicht existierender Klassen |
| `dependency-scan` | Werkzeug (Trivy) | CVEs und Lizenzverstöße in Abhängigkeiten; CVE-Befunde der Kategorie SECURITY blockieren |

Die Mischung ist Absicht: **LLM-Reviewer** finden Kontextfehler, die keine
Regel beschreibt; **statische Reviewer** finden genau das, was ein
nichtdeterministisches Modell nicht zuverlässig findet — und tun es
deterministisch, kostenlos und auditierbar. Ein Gate, das nur aus LLM-Urteilen
besteht, wäre selbst nichtdeterministisch.

Der `hallucination-review` verdient im Whitepaper besondere Erwähnung: Er
prüft nicht den Code, sondern die **Behauptungen über den Code**. „Alle Tests
laufen durch" bei unverändertem Testverzeichnis ist der klassische
Selbstbetrug agentischer Systeme.

## 7.3 Befundmodell

**Kategorien** (`ReviewCategory`): `ARCHITECTURE`, `SECURITY`, `TESTING`,
`CLEAN_CODE`, `MAINTAINABILITY`, `HALLUCINATION`, `DOCUMENTATION`,
`REQUIREMENTS`, `TOOLING`

**Schweregrade** (`ReviewSeverity`): `INFO`, `LOW`, `MEDIUM`, `HIGH`,
`CRITICAL`

**Gate-Entscheidungen** (`QualityGateDecision`): `PASSED`, `WARNING`,
`FAILED`, `SKIPPED`, `ERROR`

## 7.4 Die Gate-Policy

`QualityGatePolicy` ist ein Record mit acht Stellschrauben:

```java
boolean failOnCritical, failOnHigh, failOnMedium;
boolean allowWarnings;
double  minimumConfidenceScore;   // Wertebereich [0.0, 1.0], validiert
boolean strictConfidence;
Set<ReviewCategory> requiredCategories;
List<String>        requiredAdapters;
```

Zwei vorkonfigurierte Ausprägungen:

| | `strict()` | `lenient()` |
|---|---|---|
| blockt CRITICAL | ja | ja |
| blockt HIGH | ja | nein |
| blockt MEDIUM | nein | nein |
| Confidence-Schwelle | 0,70 | 0,00 |
| Pflichtkategorien | SECURITY, ARCHITECTURE | keine |

**Sonderregeln, die keine Policy aufweichen kann:**

- SECURITY/HIGH und SECURITY/CRITICAL blocken **immer**.
- ARCHITECTURE/CRITICAL blockt **immer**.
- Ein abgestürzter Reviewer wird zu `ReviewStatus.ERROR` materialisiert und
  führt zur Gesamtentscheidung `ERROR` — **niemals zu einem stillen Pass**.

Der letzte Punkt ist der wichtigste Satz des ganzen Kapitels: Ein Gate, dessen
Ausfall wie Erfolg aussieht, ist schlimmer als kein Gate, weil es Vertrauen
erzeugt, das es nicht deckt. Dieselbe Logik findet sich an drei weiteren
Stellen des Systems wieder (Lizenz *fail closed*, Attestierung ohne Schlüssel
wirft, CI-Job ohne Secret gilt als nicht bestanden).

## 7.5 Confidence Scoring

`ConfidenceScoreAggregator` verrechnet die Vertrauenswerte der einzelnen
Reviewer zu einem Gesamtwert, der gegen `minimumConfidenceScore` geprüft wird.
Das adressiert die Eigenart von LLM-Reviewern, plausibel klingende, aber
unsichere Befunde zu produzieren: Ein Befund mit niedriger Confidence darf
warnen, aber nicht blockieren — solange die Policy nicht `strictConfidence`
verlangt.

## 7.6 Betriebsmodi des Gates

Das Gate läuft in einem von drei Modi (mandantenweit über Settings bzw.
Policy-as-Code steuerbar):

| Modus | Wirkung |
|---|---|
| `off` | Reviewer laufen nicht |
| `advisory` | Befunde werden erhoben und angezeigt, blockieren aber nicht |
| `blocking` | Ein FAIL erzeugt Feedback und startet die Korrekturschleife |

Der Einführungspfad in Organisationen ist damit vorgezeichnet: erst messen,
dann durchsetzen. Ein Gate, das am ersten Tag blockiert, wird am zweiten Tag
abgeschaltet.

## 7.7 Verknüpfung mit dem Run

Im Blocking-Modus ist ein FAIL des Gates funktional gleichwertig mit einem
fehlgeschlagenen Build: Beides erzeugt einen Feedback-Text, der als
zusätzlicher Kontext in den nächsten Agentenlauf fließt (max. zwei Versuche).
Das Gate ist damit kein Endpunkt, sondern ein **Regler** — es erzeugt die
Eingabe für den nächsten Durchlauf.

Die Gate-Entscheidung wird am Run persistiert (`run.quality_gate_decision`,
V24) und geht in Warum-Trace und Audit-Export ein. Damit ist für jeden
gelieferten Stand nachweisbar, welches Urteil ihn passieren ließ.
