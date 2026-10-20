# 11. Abgleich: Whitepaper v1.3 ↔ Implementierung

Kapitel-für-Kapitel-Abgleich zwischen dem Konzeptpapier
„Agentic Software Development – Enterprise Architecture with AI Agents"
(v1.3, März 2026) und der real gebauten SoftwareFabrik (erhoben an 0.19.0,
Juli 2026; nachgezogen auf den Tag v0.38.0, Oktober 2026 — geänderte Zeilen
tragen „Stand v0.38.0").

**Legende**
· ✅ **bestätigt** — Konzept umgesetzt, funktioniert wie beschrieben
· ➕ **erweitert** — Umsetzung geht über das Konzept hinaus
· ⚠️ **abweichend** — bewusst anders gelöst, mit Begründung
· ○ **offen** — im Konzept vorgesehen, nicht (so) umgesetzt

---

## 11.1 Die Mapping-Tabelle

| v1.3 Kapitel | Konzept | Umsetzung in der Fabrik | |
|---|---|---|---|
| **1** Warum KI-Agenten / Orchestrator-Prinzip | Zentrale Steuerinstanz verteilt Aufgaben, überwacht, führt zusammen | `RunOrchestrationService` — einzige Stelle für Statuswechsel, ~2.610 Zeilen (Stand v0.38.0; bei 0.19.0 ~1.550); Übergänge zentral in `RunStatusTransitions` | ✅ |
| **2** Architektonische Prinzipien | Separation of Concerns, klare Rollen, Konfigurierbarkeit | Modularer Monolith, 34 Slices (Stand v0.38.0, inkl. `common`/`web`), Ports-and-Adapters, **maschinell per ArchUnit erzwungen** statt nur beschrieben | ➕ |
| **3.1** Systemkontext | Agentensystem zwischen Entwickler, Repository, CI | Abbildung 21 (`03-systemdiagramme.md`); zusätzlich Auditor und Administrator als eigene Akteure | ➕ |
| **3.2** Referenzarchitektur | Orchestrator + Agent Layer + Guardrails + Knowledge Store | Vollständig vorhanden; Guardrails als eigener Slice mit versioniertem Hash | ✅ |
| **3.3–3.4** Agentenübersicht / Runtime | Spezialisierte Agenten mit eigenem Kontextfenster | `AgentDefinition` (Rolle, Mission, bevorzugtes Modell, aktive Skills), `AgentTeam` als geordnete Aufstellung; Materialisierung als `.claude/agents/<rolle>.md` | ✅ |
| **3.5** Task-Tool-Parameter | Subagenten-Start über das Task-Tool | ⚠️ Bewusst **nicht** übernommen: die Fabrik startet keine Subagenten, sondern **einen** Agentenprozess je Run (Stand v0.38.0: Host-Prozess mit ephemerem HOME, nicht im Container). Begründung siehe 11.3 | ⚠️ |
| **4** Konfiguration mit `CLAUDE.md` | Deklarative Regeln je Repository | ➕ **Vendor-neutral gelöst:** kanonisch ist `AGENTS.md`; `CLAUDE.md` ist nur noch ein minimaler Verweis. Eine Quelle, mehrere Projektionen — kein Duplikat je Werkzeug | ➕ |
| **5** Agententypen und Modellauswahl | Modellwahl je Agententyp/Phase | `execution/routing/`: Fähigkeitsprofile statt Modellnamen (`RoutingRolle` PLAN/BUILD, seit 0.38.0 auch SPEC; `CapabilityTier`); zusätzlich erzwungene **Modell-Policy je Projekt** mit Attestierung `RUN_MODELL_AUFGELOEST`, seit 0.33.0 mit Herkunft (`quelle=override\|team\|rollen-default\|adapter-default`) | ➕ |
| **6** Agent Lifecycle | Lebenszyklus eines Agenten | Als **Run**-Lebenszyklus modelliert: 7 Phasen, 14 Zustände (Stand v0.38.0; neu `WAITING_FOR_INPUT` für Rückfragen von Spec-Runs, nicht-terminal, ohne Kapazitäts-/Workspace-Slot), drei Run-Arten BUILD/PLAN/SPEC, persistiert, wiederaufnehmbar, pausierbar, abbrechbar (Abbruch beendet seit 0.33.0 auch den Prozess samt Nachkommen) | ➕ |
| **7.1** Task Graph | Aufgaben als Graph | ⚠️ Lineare Phasen-Pipeline statt Graph — plus **Backlog mit Abhängigkeiten** (`plan_item_dependency`, V37) als der eigentliche Graph auf Vorhabensebene. Siehe 11.3 | ⚠️ |
| **7.2** Runtime Execution Flow | Ablauf eines Auftrags | Abbildung 24; deckungsgleich, ergänzt um Remote-Sync und Branch-Abzweig | ✅ |
| **7.3** State Machine & Stop-Conditions | Zustandsautomat mit Abbruchbedingungen | `RunStatus` + `RunStatusTransitions`; unerlaubte Übergänge werfen. Stop-Bedingungen: Timeout als eigener Endzustand, Abbruch mit `destroyForcibly()` (seit 0.33.0 über `ProzessRegistry` inkl. Nachkommen), Korrekturlimit, Kapazitätsschutz | ✅ |
| **7.3** Execution Budget | Aufwandsgrenzen je Lauf | Timeouts je Adapter, Token-Budgets täglich/wöchentlich mit Soft-Schwelle, **harte Mandanten-Caps** (V28), Kapazitätsgrenze für parallele Läufe | ➕ |
| **7.4** Retry-Strategie | Wiederholung bei Fehlschlag | ➕ Kein blindes Retry, sondern **Regelkreis**: Fehlerursache (Build-Ausgabe, Findings, Konfliktdateien, CI-Status) wird als Kontext in den nächsten Lauf eingespeist, max. 2 Versuche. Ein Retry ohne neue Information wiederholt nur den Fehler | ➕ |
| **8.1** Short-Term Context | Kontextfenster je Agent | Vorhanden (Prozesskontext je Run) | ✅ |
| **8.2** Shared Knowledge Store | Geteilter Wissensstand | `ProjectMemory` → `MEMORY.md` im Workspace, nach dem Lauf zurück in die DB ingestiert; plus versionierte Spezifikations-Artefakte; plus Git-Historie | ✅ |
| **8.3** Vector Memory (optional) | Embedding-basierter Speicher | ○ Bewusst **nicht** umgesetzt. Begründung: Was der Agent liest, muss reviewbar und zitierbar sein; eine Ähnlichkeitssuche erfüllt beides nicht | ○ |
| **9** Failure Handling & Resilience | Eskalationslogik | Korrekturschleife, Terminalzustände, Reviewer-Absturz ⇒ `ERROR` statt stillem Pass, Lizenz *fail closed*, graceful Degradation fehlender CLIs | ➕ |
| **10** Die sieben Lebenszyklus-Agenten | Architektur, Planung, Requirements, Entwicklung, Testing, Review, Deployment | Teils als **Agentenrollen** (`AgentDefinition`/`AgentTeam`), teils als **Systemfunktionen**: Planung = Plan-Run, Review = Review-Adapter-Schicht, Testing/Deployment = Build-Gate und Meilenstein-Release. Requirements seit 0.35.0 (opt-in) als **Produkt-Spec** mit Freigabe und AC-IDs plus Spec-Run (0.38.0) — `13-spec-driven-development.md`. Siehe 11.3 | ⚠️ |
| **11** DDD-Integration | Agenten als Bounded-Context-Teilnehmer | Die Fabrik modelliert **den Entwicklungsprozess** als Domäne (34 Pakete am Tag v0.38.0, inkl. `common`/`web`). Aggregat = JPA-Entität (bewusste Pragmatik, dokumentiert) | ⚠️ |
| **11** Kafka Outbox Pattern | Event-Zustellung | ○ Kein Broker. Interne Spring-Events (`RunCompletedEvent`) genügen dem Einzelprozess-Deployment | ○ |
| **12** AI Risk Framework & Guardrails | Sechsstufige Pflicht-Pipeline: Syntax, Style, Security, Domain-Compliance, Tests, Confidence Scoring | ✅➕ Read-only-**ReviewAdapter**-Schicht mit 7 Reviewern (Stand v0.38.0; neu `spec-conformance`) + `QualityGatePolicy` (8 Stellschrauben, `strict`/`lenient`) + `ConfidenceScoreAggregator` + drei nicht abschaltbare Sonderregeln + drei Betriebsmodi (`off`/`advisory`/`blocking`). 0.33.0 behob vier Stellen „Erfolg ohne Beleg" (u. a. stiller PASS der LLM-Reviewer, Gate auf leerem Diff) | ➕ |
| **12** Confidence Scoring mit AOP | Aspektorientierte Eskalation | ⚠️ Ohne AOP gelöst — Aggregation im Gate-Service. Ein Aspekt hätte die Nachvollziehbarkeit verschlechtert, ohne funktionalen Gewinn | ⚠️ |
| **13** Deployment-Architektur | Kubernetes-basiert | ⚠️ **Ein Prozess, eine Datenbank, Docker Compose.** Kubernetes ist möglich, aber nicht Voraussetzung — Zielkunden installieren on-prem, teils air-gapped. Siehe 11.3 | ⚠️ |
| **14** Security Model / Least Privilege | Berechtigungsmodell, Secret-Scanner-Hook | ➕ Fünfstufiges RBAC, Mandantenisolation an der Projektgrenze (IDOR-Test), Segregation of Duties, AES-GCM-Secrets, `EnvAllowlist`, ephemeres HOME je Agent-CLI-Aufruf und MCP-Nullzustand (seit 0.31.0), Host-Allowlist gegen Token-Exfiltration, `security-reviewer` + `gitleaks` in CI. *Korrektur (Stand v0.38.0, ADR-0017):* Die Container-Sandbox kapselt nur Build/Tests und trivy, nicht die Coding-Agenten; diese laufen als Host-Prozess mit Netz des Hosts | ➕ |
| **15** Wirtschaftlichkeit & Kostenmodell | Token-Budget, ROI | ➕ Preistabelle je Modell (Input/Output/**Cached**), Kostenaggregation nach Projekt/Run/Provider/Mandant/Seat mit CSV-Export, harte Caps je Mandant. **Wesentliche Ergänzung: Abo-Modus** — bei Flatrate-Abos sind Token-Kosten null, ein reines Token-ROI-Modell bildet die Realität nicht mehr ab. *Stand v0.38.0:* Abo-Modus als persönliche Nutzung (BYOS entfernt, 0.33.0); Abo-Kosten als „Schätzung (API-Tarif), nicht abgerechnet" gekennzeichnet, zählen aber gegen Budgets (V58); Claude-Läufe wurden bis 0.34.0 mit 0 € bewertet (Parser-Fehler, behoben) | ➕ |
| **16** Multi-Agent-Workflows | Sequenziell, parallel, Wiederaufnahme | Sequenziell und wiederaufnehmbar ✅. *Stand v0.38.0:* Seit 0.21.0/0.22.0 parallele Child Runs in getrennten Worktrees (max. 3), Pfad-Besitz/Leases, Merge Queue und Integration Gate — hinter dem Feature-Flag `softwarefabrik.workflow.enabled` (Default aus); verteilter Betrieb über mehrere Hosts zurückgestellt (`12-kennzahlen-historie.md`) | ⚠️ |
| **17** Java-Enterprise-Praxisbeispiele | Spring Security JWT + RBAC, Camunda | ✅ Spring Security + RBAC real umgesetzt; Ed25519-Signaturen in Lizenz- (JWS, ADR-0005) und Attestierungsschicht (der RS256-Lizenzstack wurde mit 0.4.0 entfernt). Kein Camunda — die Workflow-Engine ist das Run-Aggregat selbst | ⚠️ |
| **18** MCP-Server & Hooks | Werkzeuganbindung über MCP | ➕⚠️ *Stand v0.38.0 (0.31.0–0.34.0; ADR-0016/0017/0018/0022):* MCP zuerst als **Angriffsfläche** behandelt: **MCP-Nullzustand** für alle Agentenläufe (ephemeres HOME, Claude `--strict-mcp-config` + leere `--mcp-config`, seit 0.34.0 `--setting-sources=user` und `disableAllHooks` gegen Hooks importierter Repos), Workspace-Prüfung mit Audit-Ereignissen, Plugins standardmäßig gesperrt (`erlaubtePlugins`), **Canary-Harness** mit signierten Isolationsnachweisen je CLI-Version als Voraussetzung in den Profilen mit `mcpStandardverbot`. Danach gezielt geöffnet: **MCP-Gateway** als eigener Prozess (opt-in), nur lesende Tools, nur Claude-Code-Ausführung, Pinning `serverDigest`/`toolsDigest` per Policy-as-Code (`erlaubteMcpServer`), jeder Aufruf signiert als `MCP_TOOL_AUFRUF` mit Hashes statt Inhalten, fail-closed. Abweichend vom Konzept: Hooks werden in Agentenläufen abgeschaltet statt genutzt; schreibende Tools und andere CLIs noch nicht angebunden. Daneben bleibt die Skill-/Plugin-Bibliothek (V38) mit `ConductorWorkspaceWriter` | ➕ |
| **19 / ADR-1** Multi- vs. Single-Agent | Multi-Agent | ⚠️ Ein Agentenprozess je Run, Spezialisierung über Rollen/Team-Definition und über die **Review-Schicht** (mehrere unabhängige Prüfer) | ⚠️ |
| **19 / ADR-2** Workspace-Isolation via Git-Worktrees | Worktrees je Agent | ⚠️ **Branch-Isolation** (`sdlc/run-<id8>`) auf einem projektpersistenten Workspace statt Worktrees. Grund: Iteration über Läufe hinweg schlägt parallele Isolation. *Stand v0.38.0:* Child Runs der Workflow-Ebene (Flag aus) nutzen getrennte Worktrees; Prozess-Isolation über ephemeres HOME und Env-Allowlist, Container nur für Build/Scans | ⚠️ |
| **19 / ADR-3** Guardrail-Pipeline als Pflicht-Gate | Pflicht | ✅➕ Umgesetzt und um den Betriebsmodus `advisory` ergänzt — sonst wird das Gate am zweiten Tag abgeschaltet. Regulierte Compliance-Profile erzwingen `blocking` | ➕ |
| **19 / ADR-4** Git-basierte Orchestrierung | Git als State Machine | ✅➕ Git ist Zustandsträger (Branch, Commit, Checkpoint, Merge, PR), **aber nicht die alleinige Wahrheit**: der autoritative Zustand liegt in der Datenbank, weil ein Auditor Fragen stellt, die `git log` nicht beantwortet (welche Policy, welches Modell, wessen Freigabe) | ➕ |
| **20** Vergleich Claude Code vs. andere | Werkzeugvergleich | ➕ Hinfällig geworden — die Fabrik integriert **10 Adapter** hinter einem Port; die Vendor-Frage ist eine Konfigurationsfrage, keine Architekturfrage |➕|
| **21** End-to-End: Payment Service | Durchgängiges Beispiel | ✅ Reproduzierbar über den Wizard: 18 Templates (Web/Mobile/Desktop, Backend + Frontend, Repo-Import) → Artefakte → Run → Gate → PR |✅|
| **22** Troubleshooting | Schnellreferenz | ➕ `docs/runbooks/` (Demo-Deploy, Air-Gap-Auslieferung, E2E-Smoke, manueller Frontend-Test) plus die Praxis-Fallstricke aus `09-entwicklerhandbuch.md`, §9.6 |➕|
| **23** Glossar | Begriffe | Zu ergänzen um: Run, Plan-Run, Quality Gate, Policy-as-Code, Attestierung, Warum-Trace, Mandant, Guardrails-Projektion, Debt-Ratchet; seit v0.38.0 zusätzlich Spec-Run, Produkt-Spec, AC-ID, Spec-Drift, MCP-Nullzustand, Isolationsnachweis, Offline-Verifier |➕|

---

## 11.2 Was die Implementierung **bestätigt**

1. **Das Orchestrator-Prinzip trägt.** Eine einzige Instanz, die Zustand
   besitzt und Übergänge kontrolliert, ist der Unterschied zwischen einem
   Werkzeug und einem Prozess. Es ist auch die einzige Stelle, an der
   Governance überhaupt ansetzen kann.
2. **Guardrails müssen ein eigener Schichtbegriff sein.** Die Trennung
   „schreibende Adapter / read-only Reviewer" hat sich als tragfähig erwiesen
   — sie ist der Grund, warum das Gate nicht zur Selbsteinschätzung verkommt.
3. **Halluzinationserkennung braucht einen eigenen Prüfer.** Der
   `hallucination-review` prüft die *Behauptungen über den Code*, nicht den
   Code. „Alle Tests laufen durch" bei unverändertem Testverzeichnis ist der
   klassische Fall.
4. **Deklarative Konfiguration im Repository funktioniert.** Nur eben
   werkzeugneutral (`AGENTS.md`) statt vendorspezifisch.
5. **Ein geteilter Wissensstand ist notwendig** — und er lässt sich mit
   versionierten Dateien herstellen, ohne Vektorspeicher.

## 11.3 Was die Implementierung **korrigiert** — die vier Kernpunkte

Diese vier Punkte sind der eigentliche inhaltliche Gewinn des neuen Kapitels.
Sie sind keine Detailkorrekturen, sondern Positionsverschiebungen, die aus dem
Bau eines realen Systems folgen.

### (1) Ein Agent je Lauf, mehrere Prüfer — statt Hub-and-Spoke-Multi-Agent

Das Konzept setzt auf sieben parallele Spezialagenten unter einem
Orchestrator. Die Implementierung startet **einen** Agentenprozess je Run und
erreicht Spezialisierung anders: über Rollen- und Teamdefinitionen im Kontext,
über getrennte Plan- und Build-Runs, und vor allem über **mehrere unabhängige
Prüfer** nach der Ausführung.

Begründung: Der Nutzen mehrerer Agenten liegt in *Perspektivenvielfalt*, und
die ist beim Prüfen wertvoller als beim Erzeugen. Mehrere gleichzeitig
schreibende Agenten auf einem Repository erzeugen dagegen Konfliktkosten,
Zurechnungsprobleme („wer hat das geschrieben?") und einen nicht
attestierbaren Zustand. Die Fabrik verschiebt die Parallelität deshalb von der
Erzeugung auf die Bewertung.

### (2) Regelkreis statt Retry — Repository-Realität als Eingabe

Das Konzept beschreibt eine Retry-Strategie. Die Implementierung zeigt: Ein
Retry ohne neue Information wiederholt den Fehler. Wertvoll wird die
Wiederholung erst, wenn die **Ursache** zur Eingabe wird — Build-Ausgabe,
Reviewer-Findings, **Merge-Konfliktdateien**, roter CI-Status.

Besonders die letzten beiden sind die eigentliche Erkenntnis: Der Agent
scheitert in der Praxis seltener am Programmieren als an der *Realität des
Repositories* — veralteter Base-Branch, fremde parallele Änderungen, fremde
CI. Ein agentisches System, das diese Realität nicht als Aufgabe modelliert,
endet dort, wo die interessante Arbeit anfängt.

### (3) Governance ist keine Ergänzung, sondern Struktur

Im Konzept steht Compliance neben der Architektur. In der Implementierung ist
sie in die Architektur eingewachsen: Policy-Prüfung **zweimal** (Anlage *und*
Ausführung, weil sonst ein früh angelegter Lauf die spätere Policy umgeht);
Freigabe als **Zustand** des Laufs, nicht als Nebenprozess; jede Durchsetzung
als signiertes Kettenglied; genau eine aktive Policy-Version, damit „welche
Regel galt damals?" beantwortbar bleibt.

Die Reifungskurve lässt sich am Migrationsverlauf ablesen (V26–V33 sind
ausschließlich Mandanten- und Nachweisstrukturen). Das ist ein belastbares
Argument gegen die verbreitete Reihenfolge „erst Funktion, dann Compliance":
Die Nachweisstruktur bestimmt rückwirkend, wo Ereignisse überhaupt entstehen
müssen — sie lässt sich nicht sauber nachrüsten.

### (4) Kubernetes ist keine Voraussetzung — Souveränität schon

Das Konzept zeichnet eine Kubernetes-Deployment-Architektur. Die reale
Zielgruppe (Behörden, Finanzdienstleister, Mittelstand) fragt zuerst nach
etwas anderem: Läuft es bei uns, ohne Cloud, ohne Rückkanal? Die Antwort der
Fabrik ist ein Prozess, eine Datenbank, optionaler Lizenz-Stack, lokales
Modell, Lizenz ohne Online-Aktivierung, Offline-Verifier für Prüfer ohne
Systemzugang. (*Korrektur, Stand v0.38.0:* Eine „netzlose Agent-Sandbox"
erzwingt die Fabrik nicht — die Agenten laufen als Host-Prozess; Netztrennung
liegt beim Host, Agent-Container sind offen.)

Die Komplexität wandert damit dorthin, wo sie hingehört: in die Steuerung des
Nichtdeterminismus, nicht in die Betriebsinfrastruktur.

## 11.4 Vorschlag für die Struktur des neuen Kapitels

Ein Abschnitt von ~20–30 Seiten, der die Referenzarchitektur belegt:

1. **Von der Referenzarchitektur zur Implementierung** — Anspruch, Zeitraum,
   Kennzahlen (`01`)
2. **Systemkontext und Bausteinsicht** — Abbildungen 21–23 (`03`, `02`)
3. **Das Ausführungsmodell** — Phasen, Zustände, Regelkreis; Abbildungen 24,
   25, 30 (`05`)
4. **Vendor-Neutralität als Architektureigenschaft** — Port, 10 Adapter,
   ArchUnit-Beweis, Abo-Modus; Abbildung 27 (`06`)
5. **Guardrails in der Praxis** — Review-Schicht, Gate-Policy, drei
   Betriebsmodi (`07`); seit v0.38.0 auch Prüfung gegen die Produkt-Spec
   (`13`)
6. **Governance und Nachweisführung** — Mandanten, Policy-as-Code,
   Compliance-Profile, Hashkette, Warum-Trace, Offline-Verifier,
   MCP-Governance; Abbildung 28 (`08`)
7. **Betrieb und Souveränität** — Deployment, Air-Gap, Lizenz; Abbildung 29
   (`10`)
8. **Was die Praxis am Konzept korrigiert hat** — die vier Punkte aus 11.3
9. **Grenzen und offene Punkte** — ehrliche Bilanz (`01`, §1.7; `12`)

## 11.5 Belegbare Kernaussagen für das Management Summary

Formulierungen, die durch das Quellen-Set gedeckt sind:

- „Die Referenzarchitektur wurde als lauffähiges System implementiert:
  ~54.000 Zeilen Produktivcode (`app/`), 46 Releases von April bis Oktober
  2026, dauerhaft betriebene Demo-Instanz." (Stand v0.38.0; bei 0.19.0:
  ~33.000 Zeilen, 26 Releases in knapp drei Monaten.)
- „Vendor-Neutralität ist keine Absichtserklärung, sondern eine
  Build-Bedingung: Zwei ArchUnit-Regeln verhindern, dass Anwendungs- oder
  Web-Schicht eine konkrete Vendor-Implementierung referenzieren."
- „Vier Compliance-Profile übersetzen EU AI Act, BAIT/MaRisk/DORA und
  BSI-Grundschutz/VS-NfD in erzwingbare, signierte Policies."
- „Jede Entscheidung, die den Handlungsspielraum des Agenten festlegt, ist ein
  signiertes Glied einer Hashkette — Manipulation, Löschung und
  Schlüsselwechsel sind als getrennte Fehlerbilder erkennbar."
- „Der Nachweis ist so gebaut, dass sein Ausfall nicht wie Erfolg aussieht:
  ein abgestürzter Prüfer führt zu `ERROR`, nie zu `PASS`." (Ehrlich
  ergänzt: Bis 0.33.0 gab es genau solche Stellen — u. a. einen stillen PASS
  der LLM-Reviewer —, die eine gezielte Prüfung fand und die behoben sind.)
- „Ein Audit-Export lässt sich ohne Zugang zur Fabrik prüfen — mit einem
  Werkzeug, das nur das JDK braucht und ohne extern übergebenen
  Schlüssel-Fingerabdruck nie ‚bewiesen' meldet." (Stand v0.38.0, ADR-0023)

**Nicht belegbar** (nicht behaupten): quantifizierte Produktivitäts- oder
ROI-Aussagen aus dem Betrieb der Fabrik selbst — dafür existiert keine
kontrollierte Messung. Die Zahlen aus dem v1.3-Management-Summary (70–80 %
Aufwandsreduktion, 15–30 € je Feature) sind Modellrechnungen und sollten als
solche gekennzeichnet bleiben.
