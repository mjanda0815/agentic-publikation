# 1. Systemüberblick: Die Agentic Software Factory

## 1.1 Was das System ist

Die *Agentic Software Factory* (Produktname: SoftwareFabrik) ist eine
**Control Plane für agentische Softwareentwicklung**. Sie schreibt keinen Code
selbst und hostet kein Sprachmodell. Sie steuert, begrenzt, protokolliert und
bewertet die Arbeit externer Coding-Agenten — und macht deren Ergebnis
prüfbar.

Der Unterschied zur direkten CLI-Nutzung eines Coding-Agenten ist genau der
Unterschied zwischen *ein Entwickler mit einem mächtigen Werkzeug* und *ein
Entwicklungsprozess*: Spezifikation, Freigabe, Isolation, Review,
Nachvollziehbarkeit, Budget, Mandantentrennung.

> **Positionierung in einem Satz:**
> Die SoftwareFabrik ist die produktisierte Umsetzung der im Whitepaper v1.3
> beschriebenen Referenzarchitektur — vendor-neutral statt Claude-Code-
> spezifisch, und um die Governance-Schicht erweitert, die reguliertes Umfeld
> tatsächlich verlangt.

## 1.2 Der Kernablauf

```
Projektidee  →  Wizard  →  Spezifikations-Artefakte  →  Run  →  Review/Gate  →  Branch/PR  →  Merge
                              (Markdown, editierbar)     ↑          |
                                                         └──────────┘
                                                     Korrekturschleife (max. 2)
```

1. **Erfassen.** Ein sechsschrittiger Wizard sammelt Projektidee, Zielplattform,
   Backend- und Frontend-Stack; 18 Templates decken Web, Mobile und Desktop ab,
   inklusive Import eines bestehenden Repositories.
2. **Spezifizieren.** Daraus generiert die Plattform versionierte
   Markdown-Artefakte (`PROJECT.md`, `INSTRUCTIONS.md`, `AGENTS.md`,
   `WORKFLOW.md`, `DEFINITION_OF_DONE.md`, `README.md`), die der Mensch vor
   dem Lauf editieren kann. Das ist der Punkt, an dem menschliche Absicht
   maschinenlesbar wird. Seit 0.35.0 kommt optional (Feature-Flag, Spec-Modus
   je Projekt) eine freigegebene **Produkt-Spec** mit Akzeptanzkriterien und
   IDs hinzu (`13-spec-driven-development.md`).
3. **Ausführen.** Ein *Run* durchläuft sieben Phasen. Der Coding-Agent läuft
   als Host-Prozess mit ephemerem HOME, Env-Allowlist und MCP-Nullzustand
   (Stand v0.38.0, ADR-0017) auf einem projektpersistenten Workspace mit
   eigenem Git-Repository, auf einem eigenen Branch.
4. **Prüfen.** Read-only-Review-Adapter analysieren den Diff; ein Quality Gate
   aggregiert die Befunde zu PASS/WARN/FAIL. Bei Fehlschlag speist die
   Plattform das Feedback zurück in den Agenten — bis zu zwei automatische
   Korrekturversuche.
5. **Übergeben.** Erfolgreiche Runs werden lokal gemergt oder als Pull Request
   gepusht; bei aktivierter PR-Rückkopplung wartet der Run auf grüne CI und
   Merge.
6. **Belegen.** Jeder relevante Schritt landet in einer signierten,
   append-only Audit-Hashkette; ein Warum-Trace rekonstruiert für jeden Run,
   *welche* Policy, *welches* Modell und *welche* Freigabe gewirkt haben.

## 1.3 Kennzahlen der Codebasis

| Kennzahl | Wert |
|---|---|
| Produktivklassen (Java, `app/`) | 499 |
| Produktivcode (`app/`) | ~54.000 Zeilen (53.967) |
| Testklassen (`app/`) | 353 |
| Slices (Pakete unter `io.softwarefabrik.app`, inkl. `common` und `web`) | 34 |
| Datenbanktabellen | 63 |
| Flyway-Migrationen | 61 (V1–V65; V10, V11, V55, V57 nicht vergeben) |
| Execution-Adapter | 10 |
| Review-Adapter | 7 |
| Wizard-Templates | 18 |
| Coverage-Gate | Line ≥ 85 %, Branch ≥ 81 % (JaCoCo, buildbrechend) |
| Releases | 46 (0.1.0 … 0.38.0, 2026-04-17 bis 2026-10-20; eine Version 0.37.0 gibt es nicht) |

*Stand v0.38.0: erhoben auf dem Tag `v0.38.0` (= `1fb8aac`), 2026-10-20;
Klassen-/Zeilenzahlen per `git ls-tree -r v0.38.0`, `*.java`. Frühere
Erhebung: `main` @ `526d718` (0.19.0), 2026-07-26.*

## 1.4 Technologiestack

| Ebene | Wahl |
|---|---|
| Sprache / Runtime | Java 25 |
| Framework | Spring Boot 4.1.1 seit 0.31.0, vorher 4.0.x (WebMVC, Data JPA, Security, OAuth2-Client, Actuator) |
| UI | Server-Rendered Thymeleaf + HTMX, Server-Sent Events für Live-Logs. Kein SPA. |
| Persistenz | PostgreSQL 18 (Image 18.6), Flyway 13.10.3 (seit 0.33.0; mit Boot 4.1.1 zunächst 12.4), Hibernate mit `ddl-auto=validate` |
| JSON | Jackson 3 (`tools.jackson`) als Boot-Standard; Jackson 2 seit 0.31.0 **explizite** Abhängigkeit (kam vorher nur transitiv über Flyway 11) |
| Sicherheit | Spring Security, BCrypt (Cost 12), AES-GCM für Secrets, Ed25519 für Attestierung und Lizenzen (Ed25519-JWS, ADR-0005; der frühere Keycloak/RS256-Lizenzstack wurde mit 0.4.0 entfernt) |
| Qualität | JUnit Jupiter 6 (Boot-BOM), Mockito, AssertJ, ArchUnit 1.5.1, JaCoCo 0.8.15, Playwright 1.63.0 (E2E, on demand) |
| Supply Chain | Trivy (Filesystem + Image), OWASP Dependency-Check, gitleaks, CycloneDX-SBOM |
| Betrieb | Docker Compose (App + Postgres), systemd auf der Demo-Instanz; optional MCP-Gateway als eigener Prozess (seit 0.34.0, Default aus) |
| Weitere Module | `license-service/` (Lizenzdienst), `verifier/` (Offline-Verifier, nur JDK, ADR-0023, seit 0.32.0), `gateway/` (MCP-Gateway, JDK-HTTP + Jackson, ADR-0018, seit 0.34.0) — je eigenes Maven-Modul neben `app/`, ohne Abhängigkeit auf den Fabrik-Code |

Die Wahl ist bewusst konservativ: ein Anwendungsmodul (`app/`), ein Prozess,
eine Datenbank. Der Offline-Verifier ist bewusst ein getrenntes Werkzeug für
Dritte; der MCP-Gateway läuft nur, wenn er eingeschaltet ist. Kein Cluster, kein Message-Broker, kein Service-Mesh. Die
Komplexität des Systems liegt in der *Steuerung von Nichtdeterminismus*,
nicht in der Infrastruktur — und genau dort soll sie auch bleiben.

## 1.5 Was das System kann (Stand 0.19.0)

**Vendor-Neutralität.** Zehn Execution-Adapter hinter einem Port: `mock`,
`claude`, `codex`, `gemini`, `aider`, `kimi`, `local-llm` sowie drei
Cloud-Gateways (AWS Bedrock, Google Vertex AI, Azure OpenAI). Adapterwahl pro
Run; Application- und Web-Schicht kennen ausschließlich den Port — maschinell
per ArchUnit erzwungen.

**Abo- statt Token-Abrechnung.** Für Claude Code, Codex und Kimi existiert
neben dem API-Key-Modus ein Abo-Modus (OAuth-Credentials der CLI). Im
Abo-Modus wird der jeweilige API-Key aktiv aus der Prozessumgebung entfernt,
damit nicht versehentlich pro Token abgerechnet wird. *Stand v0.38.0:* Der
Abo-Modus ist seit 0.33.0 als **persönliche Nutzung** durch den Abo-Inhaber
gerahmt (Betriebsmodus `EINZELPLATZ_ABO`); mehrere Nutzer mit eigenem Abo auf
einem Server (BYOS) wurden entfernt, Team-Betrieb läuft über `TEAM_API_POOL`
mit API-Key. Abo-Kosten erscheinen als „Schätzung (API-Tarif), nicht
abgerechnet" (`run_metrics.kosten_geschaetzt`, V58).

**Iterativer Lebenszyklus, nicht nur Greenfield.** Projekte haben einen
persistenten Workspace mit Git-Historie. Plan-Runs erzeugen ein Backlog
(`plan_item`, mit Abhängigkeiten), Build-Runs arbeiten es ab; Meilensteine
bündeln Runs zu Versionen mit Changelog, Tag und GitHub-Release. Bestehende
Repositories lassen sich importieren.

**Governance als Systemeigenschaft.** Mandantenisolation an der
Projektgrenze, fünfstufiges Rollenmodell, signierte Policy-Dokumente als Code,
vier Compliance-Profile (Baseline, EU AI Act, BaFin-Trias BAIT/MaRisk/DORA,
BSI-Grundschutz/VS-NfD), signierte Audit-Hashkette, Segregation of Duties,
Kostenattribution und harte Budget-Caps pro Mandant.

**Supply-Chain-Nachweis.** SBOM pro Build, Ed25519-Signatur über den
SBOM-Digest, Dependency- und Lizenz-Scan als blockierender Reviewer.

### Ergänzungen seit 0.19.0 (Stand v0.38.0)

**Workflow-Ebene (0.21.0–0.30.0).** Hierarchische Workflows mit parallelen
Child Runs in getrennten Worktrees, Merge Queue, Contract Registry,
Replanning und Kennzahlen — hinter dem Feature-Flag
`softwarefabrik.workflow.enabled` (Default aus). Details in
`12-kennzahlen-historie.md`.

**MCP-Governance (0.31.0–0.34.0).** MCP-Nullzustand für alle Agentenläufe
(ephemeres HOME je CLI-Aufruf, Claude Code mit `--strict-mcp-config`, leerer
`--mcp-config`, seit 0.34.0 zusätzlich `--setting-sources=user` und
`disableAllHooks`), Workspace-Prüfung mit Audit-Ereignissen,
Canary-Harness für signierte Isolationsnachweise je CLI-Version,
optionaler MCP-Gateway nur für lesende Tools mit Pinning und
signiertem Protokoll jedes Aufrufs (`08-governance-compliance.md`, 8.11).

**Unabhängige Prüfbarkeit (0.32.0).** Audit-Export Schema 2.0 und ein
eigenständiger Offline-Verifier (nur JDK), der einen Export ohne Zugriff auf
die Fabrik prüft (`08-governance-compliance.md`, 8.7).

**Spec-Driven Development (0.35.0–0.38.0, opt-in).** Versionierte,
freigegebene Produkt-Specs mit Akzeptanzkriterien-IDs, Traceability bis zum
Commit, Conformance-Reviewer, Spec-Drift und Spec-Runs
(`13-spec-driven-development.md`; ADR-0027 Status *Proposed*).

## 1.6 Bewusste Nicht-Ziele

Für die Publikation ist die Abgrenzung so wichtig wie der Funktionsumfang:

- **Kein eigenes Modell-Hosting.** Die Fabrik ist Steuerschicht, kein
  Inferenz-Stack. Lokale Modelle werden über eine CLI (z. B. Ollama) angebunden.
- **Keine Web-IDE.** Entwickelt wird weiter in IntelliJ/VS Code; die Fabrik
  besitzt den Prozess, nicht den Editor.
- **Kein Consumer-SaaS.** Zielbild ist die Installation im Unternehmen —
  bis hin zum Air-Gap-Betrieb.
- **Kein Real-Time-Co-Editing**, kein eigener Build-Server, kein
  Kubernetes-Zwang.

## 1.7 Einschränkungen (transparent)

Diese Punkte gehören in ein seriöses Kapitel, weil sie die Belastbarkeit der
Aussagen begrenzen:

- Die drei **Cloud-Gateway-Adapter** (Bedrock, Vertex, Azure OpenAI) sind
  konfigurierbar und degradieren sauber, wurden aber **nicht** end-to-end
  gegen echte Cloud-Credentials verifiziert.
- **Sandbox-Reichweite (Korrektur, Stand v0.38.0; ADR-0017 „Korrektur zu
  ADR-0016", `execution/sandbox/SandboxScopeAdvisory.java`):** Die
  Coding-Adapter (Claude Code, Codex, Gemini, Aider, Kimi, Gateways,
  local-llm) laufen in **keiner** Variante im Container, sondern immer als
  Host-Prozess — seit 0.31.0 mit ephemerem HOME je CLI-Aufruf,
  Env-Allowlist und MCP-Nullzustand. Die aktivierbare Container-Variante
  (`execution.sandbox.variant=container`, nicht Default) kapselt nur
  Build/Tests (`mvn verify`) und trivy (SBOM, Dependency-Scan) des
  generierten Projekts; ohne Docker im PATH fällt sie auf lokale Prozesse
  zurück. Agent-CLIs im Container sind ein eigenes, offenes Arbeitspaket.
  Das ephemere HOME schützt vor *Konfiguration*, nicht vor gezieltem Lesen
  über absolute Pfade.
- Der **Architektur-Ratchet** friert bestehende Modul-Zyklen und 13
  `web → JpaRepository`-Zugriffe als Altschuld ein. Neue Verstöße brechen den
  Build, die bestehenden sind dokumentierte, noch zu tilgende Schuld. Am Tag
  v0.38.0 enthält die Baseline genau 100 Zyklen-Einträge; der Cap steht seit
  0.29.0 auf 400 (siehe `02-architektur.md`, 2.6).
- **Budget-Caps** wirken je Mandant. Eine Kostenauswertung je Seat (auslösender
  Nutzer) existiert seit v0.17 (`/mandanten/seat-kosten`), eine seat-scharfe
  Obergrenze gibt es nicht.
- Ein bekannter **Test-Isolationsdefekt** ist offen: ein Integrationstest
  committet unter bestimmten Bedingungen in das reale Repository statt in ein
  temporäres. TODO(verify): Status am Tag v0.38.0 nicht im Code/CHANGELOG
  belegt.
- Der **MCP-Gateway** ist der einzige *MCP*-Weg, nicht der einzige *Netz*weg:
  Ohne Agent-Container kann ein Agentenprozess weiterhin direkt ins Netz
  (ADR-0018, Konsequenzen). Er bedient zunächst nur die Ausführung mit Claude
  Code und nur lesende Tools.
- **Spec-Driven Development** ist opt-in (Flag + Spec-Modus), ADR-0027 steht
  auf *Proposed*; die Governance-Stufe (SPEC-005, Roadmap 0.39) ist nicht
  umgesetzt.
