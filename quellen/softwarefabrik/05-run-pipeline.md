# 5. Das Ausführungsmodell: der Run

Der *Run* ist die Ausführungseinheit der Fabrik — das Gegenstück zum
„Execution Model" aus Kapitel 7 des Whitepapers v1.3, jedoch nicht als
Task-Graph, sondern als **zustandsbehaftete Pipeline mit Regelkreis**.

Zentrale Implementierung: `run/application/RunOrchestrationService`
(~1.550 Zeilen; die einzige Stelle im System, an der Run-Statuswechsel
stattfinden).

## 5.1 Zwei Run-Arten

| Art | Zweck | Ergebnis |
|---|---|---|
| `PLAN` | Analysiert den Ist-Stand und schlägt die nächsten Arbeitsschritte vor | Dateien unter `plans/` werden committet, alles andere verworfen; Vorschläge werden als `plan_item` ins Backlog indexiert |
| `BUILD` | Setzt ein Backlog-Element bzw. ein Ziel tatsächlich um | Code auf einem isolierten Branch, validiert, gemergt oder als Pull Request |

Die Trennung ist bewusst asymmetrisch: Ein Plan-Run darf **keinen Code
ändern** (`committePlansVerwirfRest`) und durchläuft kein Build-Gate. Damit ist
Planung risikofrei automatisierbar — die Grundlage für zeitgesteuerte
Routinen und für Folgevorschläge nach abgeschlossenen Builds.

## 5.2 Die sieben Phasen

| Phase | Inhalt |
|---|---|
| `INTAKE` | Aufnahme des Auftrags, Zuordnung von Projekt, Team, Ziel |
| `PROMPT_ASSEMBLY` | Zusammenbau des Agentenauftrags aus versionierten Artefakten |
| `WORKSPACE_PREPARATION` | Workspace, Git, Artefakte, `MEMORY.md`, Guardrails-Projektion, Remote-Sync, Branch-Abzweig |
| `EXECUTION` | Lauf des Coding-Agenten in der Sandbox, Streaming von Logs/Tokens |
| `VALIDATION` | Build-Gate, Commit auf dem Run-Branch, SBOM, Quality Gate |
| `CORRECTION` | Rückkopplung der Befunde in einen erneuten Agentenlauf |
| `COMPLETION` | Merge bzw. PR-Abschluss, Backlog-Fortschreibung, Folgeereignisse |

Phasen haben eigene Zustände (`PENDING → RUNNING → DONE/FAILED`) und sind Teil
des Run-Aggregats.

## 5.3 Zustandsmodell

14 Zustände: `DRAFT`, `READY`, `PREPARING`, `RUNNING`, `PAUSED`,
`WAITING_FOR_APPROVAL`, `VALIDATING`, `NEEDS_CORRECTION`, `WAITING_FOR_PR`,
`FAILED`, `TIMEOUT`, `COMPLETED`, `CANCELLED`.

Drei davon sind für die Argumentation im Whitepaper besonders aussagekräftig:

- **`WAITING_FOR_APPROVAL`** — der Mensch ist ein Zustand im System, kein
  Nebenprozess.
- **`NEEDS_CORRECTION`** — Fehlschlag ist ein *regulärer* Zustand mit
  definiertem Ausgang, nicht ein Abbruch.
- **`WAITING_FOR_PR`** — die Realität des Zielrepositories (fremde CI, fremde
  Reviewer, fremder Merge-Zeitpunkt) ist im Modell abgebildet, statt am
  Systemrand zu enden.

## 5.4 Ablauf eines Build-Runs

**1 — Anlage.** Vor der Anlage prüft der Orchestrator die Modell-Policy des
Projekts, die aktive Policy-as-Code (Adapter erlaubt?), die
Attestierungspflicht und die Lizenzgrenzen. Abgelehnte Läufe erzeugen ein
attestiertes Ereignis `RUN_POLICY_DENIED` — auch die Ablehnung ist Nachweis.

**2 — Ausführungszeitliche Neuprüfung.** Beim tatsächlichen Start werden
Attestierungspflicht und geltende Policy-Version **erneut** ausgewertet und
gestempelt (`RUN_POLICY_ANGEWENDET`). Grund: Ein vor der Policy-Aktivierung
angelegter Run würde sie sonst umgehen; und Warum-Trace wie Export sollen die
*real durchgesetzte* Version ausweisen, nicht die zum Anlagezeitpunkt gültige.

**3 — Workspace.** Der Workspace ist projektpersistent. Der erste Run
initialisiert Git; Folgeläufe arbeiten auf dem bestehenden Code weiter. Ist
eine Import-Quelle gesetzt und der Workspace leer, wird ein bestehendes
Repository geklont oder kopiert. Anschließend werden geschrieben:

- die versionierten Spezifikations-Artefakte (nicht-destruktiv, nur `.md`),
- `MEMORY.md` aus dem kuratierten Projekt-Gedächtnis,
- die Guardrails-Projektion: `AGENTS.md` als kanonische, cross-tool-lesbare
  Datei plus eine minimale `CLAUDE.md`, die darauf verweist — bewusst *eine*
  Quelle statt Duplikate je Werkzeug.

**4 — Remote-Synchronisation und Branch-Isolation.** Bei Remote-Projekten wird
der Base-Branch **vor** dem Abzweig auf den Remote-Stand vorgespult, damit der
Lauf nicht auf veraltetem Code aufsetzt. Danach zweigt der Run auf
`sdlc/run-<id8>` ab. Plan-Runs bleiben auf dem Base, damit ihre `plans/` im
Backlog sichtbar sind.

**5 — Approval vor Execution.** Verlangt die Policy eine Freigabe, geht der
Run in `WAITING_FOR_APPROVAL` und die Methode kehrt zurück. Fortsetzung
erfolgt über einen eigenen Einstiegspunkt, der wieder auf den Run-Branch
wechselt.

**6 — Execution.** Der Adapter läuft in der Sandbox; `stdout`/`stderr` gehen
zeilenweise in `execution_log` und parallel in den SSE-Stream. Token- und
Kostenzähler laufen live mit.

**7 — Validation.** `mvn verify` bzw. der stackspezifische Build. Die
Agentenarbeit wird auf dem Run-Branch committet — auch bei Misserfolg, damit
sie inspizierbar bleibt. Danach optional SBOM-Erzeugung und -Signatur, dann
das Quality Gate.

**8 — Zweiter Approval-Punkt (vor dem Merge).** Regulierte Profile verlangen
Vier-Augen auch in der Validierung. Ohne Freigabe geht der Run erneut in
`WAITING_FOR_APPROVAL`; die Fortsetzung führt **nicht** erneut aus, sondern
finalisiert nur den bereits validierten Stand. Die Begründung im Code ist
zitierfähig: *ohne diesen zweiten Checkpoint wäre die signierte Zusage
Fassade.*

**9 — Abschluss.** Entweder lokaler Merge in den Base oder Push + Pull
Request. Im PR-Fall wechselt der Run in `WAITING_FOR_PR`; ein Poller
übernimmt. Beim Abschluss wird das zugehörige Backlog-Element auf `DONE`
gesetzt — erst mit dem Merge, nicht mit dem Codeschreiben — und ein
`RunCompletedEvent` publiziert, das einen Folge-Plan-Run auslösen kann.

## 5.5 Der Regelkreis: Korrekturschleife

Vier Ereignisse speisen dieselbe Schleife:

1. Build fehlgeschlagen,
2. Quality Gate blockiert (im Blocking-Modus),
3. **Merge-Konflikt** mit dem Base-Branch,
4. rote CI am Pull Request.

In allen vier Fällen wird ein Feedback-Text erzeugt (Build-Ausgabe, Findings,
Konfliktdateien) und als zusätzlicher Kontext in einen erneuten Agentenlauf
eingespeist — maximal **zwei** Versuche (`MAX_KORREKTUR_VERSUCHE = 2`), danach
bleibt der Run in `NEEDS_CORRECTION`.

Zwei Details lohnen die Erwähnung im Whitepaper:

- **Merge-Konflikte gelten als Arbeitsanweisung, nicht als Systemfehler.** Der
  Konflikt wird dem Agenten mit den betroffenen Dateien und der expliziten
  Aufforderung übergeben, die Konfliktmarker aufzulösen. Repository-Realität
  wird damit Teil der Aufgabe.
- **Der Branch-Wechsel vor der Korrektur ist sicherheitsrelevant.** Nach einem
  abgebrochenen Merge steht der Workspace auf dem Base-Branch. Ohne expliziten
  Rückwechsel würde die Korrektur samt `git add -A` direkt auf `main`
  committen — und damit sowohl die Branch-Isolation als auch die
  Pflichtfreigabe umgehen. Dieser Fall wurde in einem adversarialen
  Sicherheits-Re-Review gefunden und behoben (v0.18.1). Er ist ein sehr
  konkretes Beispiel dafür, dass agentische Systeme an den *Übergängen*
  zwischen Automatismen scheitern, nicht in ihnen.

## 5.6 Approval-Modell

- Freigabepunkte liegen vor `EXECUTION` und vor dem Merge (in `VALIDATION`).
- Eine Approval-Policy kann automatisch fortsetzen — oder eben nicht.
- Freigeben darf ab Rolle `MAINTAINER`.
- **Segregation of Duties** ist konfigurierbar: Wer einen Run ausgelöst hat,
  darf ihn dann nicht selbst freigeben.
- Jede Entscheidung landet als `approval_decision` und als attestiertes
  Audit-Ereignis.

## 5.7 Automatisierung höherer Ordnung

| Mechanismus | Wirkung |
|---|---|
| **Routinen** (`routine`, V39) | Zeitgesteuerte Plan- oder Build-Runs pro Projekt, an-/abschaltbar |
| **Folgevorschläge** | Ein abgeschlossener Build-Run stößt über `RunCompletedEvent` einen Plan-Run an |
| **PR-Feedback-Poller** | Fragt CI-Status und Merge-Zustand ab; standardmäßig **deaktiviert** (`git.pr-feedback.enabled=false`), weil unbeaufsichtigte periodische Remote-Kontakte eine bewusste Betriebsentscheidung sein sollen |
| **Meilenstein-Release** | Bündelt Runs zu einer Version: Changelog, Tag, GitHub-Release |
| **Kapazitätsschutz** | `RunCapacityGuard` begrenzt gleichzeitige Läufe |

Die Kombination ergibt einen geschlossenen Kreis: *planen → bauen → prüfen →
mergen → neu planen* — ohne dass ein Mensch den Anstoß geben muss, aber mit
definierten Stellen, an denen er es tun muss.

## 5.8 Beobachtbarkeit zur Laufzeit

- **Server-Sent Events** für Logs, Phasenwechsel und Token-Zähler; Heartbeat
  alle 20 s, Auto-Reconnect nach 5 s, Replay der letzten 50 Zeilen nach
  Verbindungsabriss, begrenzter Puffer je Sitzung. Polling-Fallback (2 s),
  falls ein Reverse-Proxy SSE blockiert.
- **Prometheus** über `/actuator/prometheus` (nur `ROLE_ADMIN`).
- **MDC-Logging** mit `projectId`, `runId`, `phase`.
- **Analytics-Sicht** mit Kosten je Projekt, Run, Provider und Mandant,
  jeweils als CSV exportierbar.
