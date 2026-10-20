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

## 7.2 Die sieben Review-Adapter (Stand v0.38.0)

Namen wie von `name()` geliefert (am Tag v0.38.0 nachgeprüft;
Implementierungen in `review/vendor/` und `review/reviewer/`).

| Adapter | Art | Prüft |
|---|---|---|
| `claude-review` | LLM, seit 0.33.0 technisch read-only (`--permission-mode dontAsk`, `--disallowedTools=Edit,Write,MultiEdit,NotebookEdit,Bash`) | Diff-Review durch Claude Code im `--print`-Modus |
| `aider-review` | LLM (read-only-Prompt) | Diff-Review durch Aider |
| `security-reviewer` | statisch | API-Keys, Path-Traversal, SQL-Konkatenation, `Runtime.exec`, Passwort-Logging; CRITICAL bei Vendor-Key-Präfixen (`AKIA`, `AIza`, `sk-proj`, `sk-ant`) |
| `architecture-reviewer` | statisch | Web/Repository ohne Service, JPA-Importe in der Domänenschicht, **Änderungen an bestehenden Flyway-Migrationen (CRITICAL)** |
| `hallucination-reviewer` | statisch | TODO/FIXME-Marker, „tests pass"-Behauptungen ohne Teständerung, unberührte Akzeptanzkriterien, Importe nicht existierender Klassen |
| `dependency-scan` | Werkzeug (Trivy) | CVEs und Lizenzverstöße in Abhängigkeiten; CVE-Befunde der Kategorie SECURITY blockieren |
| `spec-conformance` (seit 0.38.0) | statisch, regelbasiert ohne Agent-CLI (`brauchtIsolationsnachweis=false`), Kategorie `REQUIREMENTS` | Abdeckung gebundener Akzeptanzkriterien durch Tests, Tests mit unbekannten AC-IDs, geänderte Produktivdateien ohne AC-Zuordnung — nur für Runs mit Spec-Bezug (Details `13-spec-driven-development.md`, 13.7) |

Zusätzlich zu den sieben Adaptern läuft seit 0.31.0 der Prüfschritt
`mcp-nullzustand` im Gate (im Orchestrator, kein `ReviewAdapter`): In
Profilen mit MCP-Standardverbot ist eine vom Agenten geschriebene
Agenten-/MCP-Konfiguration ein blockierendes `SECURITY`-Finding (CRITICAL),
das durch die normale Korrekturschleife läuft (ADR-0017 E4).

Die Mischung ist Absicht: **LLM-Reviewer** finden Kontextfehler, die keine
Regel beschreibt; **statische Reviewer** finden genau das, was ein
nichtdeterministisches Modell nicht zuverlässig findet — und tun es
deterministisch, kostenlos und auditierbar. Ein Gate, das nur aus LLM-Urteilen
besteht, wäre selbst nichtdeterministisch.

Der `hallucination-reviewer` verdient im Whitepaper besondere Erwähnung: Er
prüft nicht den Code, sondern die **Behauptungen über den Code**. „Alle Tests
laufen durch" bei unverändertem Testverzeichnis ist der klassische
Selbstbetrug agentischer Systeme. Der `spec-conformance`-Reviewer setzt das
fort: Er prüft nicht, ob Code *gut* ist, sondern ob die vereinbarten
Akzeptanzkriterien belegt sind — „ob er das Richtige tut" (ADR-0027).

## 7.3 Befundmodell

**Kategorien** (`ReviewCategory`, Stand v0.38.0): `ARCHITECTURE`,
`SECURITY`, `TESTING`, `CLEAN_CODE`, `MAINTAINABILITY`, `HALLUCINATION`,
`DOCUMENTATION`, `REQUIREMENTS`, `TOOLING`, `OTHER`

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

**Ein gesperrter Reviewer ist `SKIPPED`, nicht `ERROR` (seit 0.31.0).** In
Profilen mit MCP-Standardverbot laufen `claude-review` und `aider-review` nur
mit bestandenem Isolationsnachweis; die Sperre sitzt zentral im
`QualityGateService`. Ein gesperrter Reviewer liefert `SKIPPED` mit Sperrgrund
(sonst blockierte jedes Gate im regulierten Profil auch Mock-Runs); ist er per
Gate-Policy Pflicht, scheitert das Gate trotzdem. Im Run wird die Sperre als
`RUN_POLICY_DENIED` (`zeitpunkt=quality-gate`) attestiert (ADR-0017 E5).

## 7.4a Vier Stellen „Erfolg ohne Beleg" (behoben in 0.33.0)

Eine Prüfung der Claude-Code-Anbindung fand vier Stellen, an denen die Fabrik
Erfolg meldete, ohne ihn belegt zu haben (CHANGELOG 0.33.0). Sie sind die
Praxisprobe auf den Satz oben:

| Befund | Wirkung vorher | Behebung |
|---|---|---|
| **Stiller Review-PASS der LLM-Reviewer** | Claude- und Aider-Review werteten Exit ≠ 0 ohne Startfehler (Auth-Fehler, Rate-Limit, Refusal) oder Freitext ohne Finding-/`summary:`-Zeile als „Review ohne Findings" = PASSED | PASSED nur bei Exit 0 **und** nachweisbarem Ergebnis (mindestens eine `[SEV/CAT]`-Zeile oder die nun verpflichtende `summary:`-Zeile), sonst `ERROR` → Gate-`ERROR` (advisory: nur protokolliert) |
| **Gate prüfte einen leeren Diff** | Build-Runs committen vor dem Gate auf den Run-Branch; das Gate las `git diff HEAD` (Working-Tree) und sah nichts | Pipeline- und manuelles Gate prüfen den Branch-Diff `<base>...<run-branch>` ab merge-base, kumulativ über Korrekturschleifen, mit Dateiliste; Architektur-Präferenzen und Definition of Done gehen in den Review-Request |
| **Abbruch beendete den Prozess nicht** | „Run abbrechen" setzte nur den Status; CLI und Kindprozesse liefen weiter | Port `ProzessRegistry` (Implementierung in `execution`); Abbruch und Timeouts (auch der Review-CLIs) beenden den Prozess samt Nachkommen; der Fehler-Exit überschreibt `CANCELLED` nicht mehr und startet keine Korrekturschleife |
| **Build-Runs ohne Schreibrechte** | Claude Code lief headless ohne Permission-Modus und bat im Text um Erlaubnis | Build/Plan mit `--permission-mode acceptEdits` plus `--allowedTools` (Default: Lese-/Such-Tools, Build-/Test-Werkzeuge, lesendes git — kein commit/push, kein curl/wget/rm); `bypassPermissions` wird beim Start abgelehnt; Reviews mit `dontAsk` + `--disallowedTools` |

Gemeinsames Muster: Jeder dieser Fehler sah von außen wie ein erfolgreicher
Lauf aus — ein leeres Review, ein grünes Gate, ein abgebrochener Run. Keiner
wäre durch einen Test aufgefallen, der nur den Erfolgsfall prüft.

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

**Spec-Modus `STRENG` (seit 0.38.0):** `spec-conformance` ist dann
Pflicht-Reviewer, fehlende AC-Abdeckung ist `CRITICAL`, und das
Pipeline-Gate läuft blockierend — der globale Gate-Modus wird dafür
angehoben, mit Hinweis im Run-Log. In `LEICHT` sind alle
Conformance-Befunde beratend (`MEDIUM`/`LOW`).

Die Gate-Entscheidung wird am Run persistiert (`run.quality_gate_decision`,
V24) und geht in Warum-Trace und Audit-Export ein. Damit ist für jeden
gelieferten Stand nachweisbar, welches Urteil ihn passieren ließ.
