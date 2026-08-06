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

1. **Erfassen.** Ein fünfschrittiger Wizard sammelt Projektidee, Zielplattform,
   Backend- und Frontend-Stack; 18 Templates decken Web, Mobile und Desktop ab,
   inklusive Import eines bestehenden Repositories.
2. **Spezifizieren.** Daraus generiert die Plattform versionierte
   Markdown-Artefakte (`PROJECT.md`, `INSTRUCTIONS.md`, `AGENTS.md`,
   `WORKFLOW.md`, `DEFINITION_OF_DONE.md`, `README.md`), die der Mensch vor
   dem Lauf editieren kann. Das ist der Punkt, an dem menschliche Absicht
   maschinenlesbar wird.
3. **Ausführen.** Ein *Run* durchläuft sieben Phasen. Der Coding-Agent läuft in
   einer Sandbox auf einem projektpersistenten Workspace mit eigenem
   Git-Repository, auf einem eigenen Branch.
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
| Produktivklassen (Java) | 362 |
| Produktivcode | ~33.000 Zeilen |
| Testklassen | 257 |
| Fachliche Slices (Module) | 27 |
| Datenbanktabellen | 39 |
| Flyway-Migrationen | 37 (V1–V39, zwei Nummern historisch übersprungen) |
| Execution-Adapter | 10 |
| Review-Adapter | 6 |
| Wizard-Templates | 18 |
| Coverage-Gate | Line ≥ 85 %, Branch ≥ 81 % (JaCoCo, buildbrechend) |
| Releases | 26 (0.1.0 … 0.19.0, seit 2026-04-17) |

*Erhoben auf `main` @ `526d718`, 2026-07-26.*

## 1.4 Technologiestack

| Ebene | Wahl |
|---|---|
| Sprache / Runtime | Java 25 |
| Framework | Spring Boot 4.0.7 (WebMVC, Data JPA, Security, OAuth2-Client, Actuator) |
| UI | Server-Rendered Thymeleaf + HTMX, Server-Sent Events für Live-Logs. Kein SPA. |
| Persistenz | PostgreSQL 18, Flyway-Migrationen, Hibernate mit `ddl-auto=validate` |
| Sicherheit | Spring Security, BCrypt (Cost 12), AES-GCM für Secrets, Ed25519 für Attestierung, RS256-Lease-JWTs für Lizenzen |
| Qualität | JUnit 5, Mockito, AssertJ, ArchUnit 1.4.1, JaCoCo 0.8.15, Playwright (E2E, on demand) |
| Supply Chain | Trivy (Filesystem + Image), OWASP Dependency-Check, gitleaks, CycloneDX-SBOM |
| Betrieb | Docker Compose (App + Postgres), systemd auf der Demo-Instanz |

Die Wahl ist bewusst konservativ: ein Maven-Modul, ein Prozess, eine
Datenbank. Kein Cluster, kein Message-Broker, kein Service-Mesh. Die
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
damit nicht versehentlich pro Token abgerechnet wird.

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
- Die **Container-Sandbox** existiert und ist aktivierbar
  (`execution.sandbox.variant=container`), ist aber nicht der Default; ohne
  Docker im PATH fällt das System auf lokale Prozessisolation zurück.
- Der **Architektur-Ratchet** friert bestehende Modul-Zyklen und 13
  `web → JpaRepository`-Zugriffe als Altschuld ein. Neue Verstöße brechen den
  Build, die bestehenden sind dokumentierte, noch zu tilgende Schuld.
- Eine **Seat-Level-Kostenattribution** (Kosten pro Nutzer statt pro Mandant)
  ist bewusst offen.
- Ein bekannter **Test-Isolationsdefekt** ist offen: ein Integrationstest
  committet unter bestimmten Bedingungen in das reale Repository statt in ein
  temporäres.
