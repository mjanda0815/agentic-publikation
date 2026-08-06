# 12. Kennzahlen, Entwicklungsverlauf, offene Punkte

## 12.1 Kennzahlen

| Kennzahl | Wert | Erhebung |
|---|---|---|
| Produktivklassen | 364 | `find app/src/main/java -name '*.java'` |
| Produktivcode | ~33.182 Zeilen | |
| Testklassen | 259 | |
| Test-zu-Produktiv-Verhältnis | ~0,71 Klassen | |
| Fachliche Slices | 28 (neu: `workflow`) | |
| Datenbanktabellen | 39 | `CREATE TABLE` in Migrationen |
| Flyway-Migrationen | 38 (V1–V40) | |
| HTTP-Routen | 156 in 34 Controllern | Mapping-Annotationen |
| Execution-Adapter | 10 | |
| Review-Adapter | 6 | |
| Wizard-Templates | 18 | |
| Run-Zustände / Phasen | 13 / 7 | |
| Rollen | 5 | |
| Compliance-Profile | 4 | |
| Coverage-Gate | Line ≥ 85 %, Branch ≥ 81 % | JaCoCo, buildbrechend |
| Releases | 27 (0.1.0 – 0.20.0) | 2026-04-17 bis 2026-08-06 |
| CI-Jobs je Push | 6 | |

*Stand: `main` @ `35c1b9e` (zwei Commits nach `v0.20.0`), 2026-08-06.*

## 12.2 Entwicklungsverlauf

Der Verlauf eignet sich als Evidenz dafür, in welcher Reihenfolge ein
agentisches Entwicklungssystem tatsächlich reift — und dass Governance nicht
am Anfang steht, aber früher gebraucht wird, als man plant.

### Phase 1 — Werkzeug (0.1.0 – 0.8.1, April–Mai 2026)

Wizard, Spezifikations-Artefakte, Run mit Phasen, Mock- und
Claude-Code-Adapter, Approval-Policies, Audit-Log, Settings mit
Scope-Hierarchie, Quality-Gate-Grundlagen, Lizenzstack, Container-Sandbox
(ADR-0011), Run-Templates, Conductor (Plugins/Skills/`AGENTS.md`-Sync),
Modell-Routing je Agentenrolle, Kostenschätzung im Wizard, Inline-Diffs vor
Freigabe.

### Phase 2 — Vendor-Neutralität und Betriebsformen (0.9.0 – 0.12.0, Juni 2026)

Abo-Authentifizierung statt API-Key (inkl. aktivem Strippen des Keys),
Windows-nativer Einzelplatzbetrieb, Wizard-Umbau von „ein Template" auf drei
orthogonale Dimensionen (Zielplattform × Backend × Frontends) mit
Kompatibilitätsmatrix, weitere Stacks.

### Phase 3 — Lebenszyklus statt Greenfield (0.13.0 – 0.14.0, Juni 2026)

Projektpersistenter Workspace mit Re-Run, echter Repo-Import, Projekt-Memory,
Plan-/Build-Runs mit Backlog, Branch-Isolation je Build-Run, Push + Pull
Request, automatische Korrektur-Feedback-Schleife, Quality Gate in der
Pipeline mit drei Betriebsmodi, automatische Folgevorschläge.

### Phase 4 — Enterprise-Fähigkeit (0.15.0 – 0.17.2, Juli 2026)

Betriebsmodi (Einzelplatz-Abo vs. Team-API-Pool), OpenAI-kompatibler Adapter
für lokale Modelle, Cloud-Gateways, erzwungene Modell-Policy je Projekt,
Capability-Routing; Mandanten mit harter Isolation, RBAC, SSO-OIDC,
Mandantenbudgets; signierte Audit-Hashkette, Warum-Trace, Policy-as-Code,
Compliance-Profile, Audit-Export; SBOM, signierte Artefakte, Dependency-Scan
als blockierender Reviewer.

Ab 0.16.0 dominieren **Befunde aus adversarialen Multi-Agent-Reviews** die
Changelogs — das System wurde systematisch mit dem Ziel geprüft, seine eigenen
Zusagen zu brechen. Behobene Klassen von Befunden: Pflichtfreigaben, die real
umgangen werden konnten (RS-01); IDOR-Schreiblücken (RS-02); Policy-Shadowing
durch Mandanten-Policies; Cross-Tenant-Flächen ohne Betreiber-Gate.

### Phase 5 — Repository-Realität und Härtung (0.18.0 – 0.19.0, Juli 2026)

Remote-Synchronisation vor dem Lauf, Merge-Konflikt als Korrektureingabe,
PR-/CI-Rückkopplung mit eigenem Run-Zustand, Meilensteine mit Changelog/Tag/
GitHub-Release, Backlog-Abhängigkeiten. Sicherheits-Hotfix 0.18.1 gegen
Token-Exfiltration/SSRF über manipulierte Remote-URLs und RCE über
`git ext::`-Remote-Helper. 0.19.0: versionierte Skill-Bibliothek,
zeitgesteuerte Routinen, Segregation of Duties, vendor-neutrale
Engineering-Guardrails.

### Phase 6 — Konsolidierung und Sicherheitsrunde (0.20.0, August 2026)

Kimi-Adapter (Moonshot AI) mit API-Key- und Abo-Modus, Buildnummer-Anzeige
in der UI, Doku-Sweep. Sicherheitsseitig: zwei CVEs per Patch-Bump innerhalb
der Minor-Linie geschlossen, eine dritte ohne verfügbaren Fix begründet
akzeptiert — als Suppression **mit Ablaufdatum**, danach schlägt der Scan
bewusst wieder fehl; die Suppression-Datei verlangt seither für jeden
Eintrag Begründung und Ablaufdatum. Ursache der bis dahin unbemerkten Lage:
der Abhängigkeits-Scan lief in der CI ohne gültigen Zugang zur
Schwachstellendatenbank (das Geheimnis wurde nur zur Vorprüfung gelesen,
dem Build aber nie als Parameter übergeben) und war zugleich als nicht
blockierend konfiguriert — die Oberfläche meldete Grün, ohne dass je ein
vollständiger Scan stattgefunden hatte.

### Danach (nach 0.20.0 auf `main`)

**Workflow-Ebene, Phase 0** (`35c1b9e`): ADR-0014 (hierarchische
Workflow-Orchestrierung, strikte Richtung `workflow → run`) und ADR-0015
(Single Writer per Workspace), Migration V40 (`run.workflow_id`,
`run.workflow_task_id`, nullable, ohne FK), einmalige Zuordnung eines Runs
zu einer Workflow-Task, neuer Slice `io.softwarefabrik.app.workflow`,
Feature-Flag `softwarefabrik.workflow.enabled` mit Default **aus**.
Bewusst ohne sichtbares Feature. Offen aus Phase 0: Workflow-Ereignisse im
Auditmodell und Workflow-Daten im Warum-Trace.

## 12.3 Beobachtungen zum Verlauf

Drei Muster, die sich für die Publikation verallgemeinern lassen:

1. **Governance kam spät, wurde aber strukturbildend.** Die Migrationen
   V26–V33 sind ausschließlich Mandanten- und Nachweisstrukturen. Rückwirkend
   bestimmten sie, an welchen Stellen im Ablauf überhaupt Ereignisse entstehen
   müssen — Attestierungslücken (Modellauflösung, Gate-Ergebnis) mussten
   nachträglich geschlossen werden, damit der Warum-Trace vollständig ist.
   Wer die Nachweisstruktur früher entwirft, spart diese Nacharbeit.
2. **Die härtesten Befunde lagen an den Übergängen**, nicht in den Funktionen:
   der Branch-Zustand nach einem abgebrochenen Merge, ein vor der
   Policy-Aktivierung angelegter Lauf, eine Mandanten-Policy, die eine
   globale unterlaufen konnte. Automatismen sind einzeln korrekt und im
   Zusammenspiel angreifbar.
3. **Vendor-Neutralität wurde durch einen Test billig.** Solange die
   ArchUnit-Regeln stehen, kostet ein neuer Adapter eine Klasse und einen
   Test. Ohne sie wäre die Kopplung längst durch die Schichten diffundiert.

## 12.4 Offene Punkte (Stand 2026-08-06, nach 0.20.0)

| Punkt | Art |
|---|---|
| Parallele Multi-Branch-Ausführung mehrerer Runs je Projekt | Phase 0 begonnen, Feature-Flag aus |
| Seat-scharfe Budget-Obergrenze (Auswertung je Seat existiert seit v0.17) | offen |
| Cloud-Gateways (Bedrock/Vertex/Azure) nicht end-to-end verifiziert | Verifikationslücke |
| Vollständige Sandbox für Coding-Adapter | offen |
| Test-Isolationsdefekt: Integrationstest committet ins reale Repository | Defekt |
| Architektur-Altschuld: eingefrorene Modulzyklen + 13 `web → JpaRepository` | dokumentierte Schuld |
| Playwright-E2E-Suite als Standard nach jedem Deploy | geplant |
| Workflow-Ereignisse in Audit und Warum-Trace (Rest aus Phase 0) | offen |
| Eine Laufzeit-CVE ohne verfügbaren Fix, akzeptiert mit Ablaufdatum | bewusst akzeptiert |

Diese Liste gehört bewusst in die Publikation. Ein System, das seine offenen
Punkte benennt und seine Architekturschuld *zählt*, ist der glaubwürdigere
Beleg für die These des Whitepapers als eines, das keine hat.

## 12.5 Quellenverweise im Repository

Für Fußnoten mit konkreter Fundstelle:

| Aussage | Fundstelle |
|---|---|
| Orchestrierung, Phasen, Regelkreis | `app/src/main/java/io/softwarefabrik/app/run/application/RunOrchestrationService.java` |
| Zustandsmodell | `run/domain/RunStatus.java`, `RunStatusTransitions.java` |
| Adapter-Port | `execution/ExecutionAdapter.java` |
| Vendor-Neutralität maschinell erzwungen | `src/test/java/.../architecture/HexagonalRulesTest.java` |
| Schichtenregeln | `.../architecture/LayeringRulesTest.java` |
| Architektur-Ratchet | `.../architecture/ArchitectureDebtRatchetTest.java`, `src/test/resources/archunit-store/` |
| Gate-Policy | `qualitygate/domain/QualityGatePolicy.java` |
| Compliance-Profile inkl. Regulatorik-Bezug | `policy/domain/ComplianceProfil.java` |
| Policy-Inhalt (kanonisch, signierbar) | `policy/domain/PolicyInhalt.java` |
| Audit-Hashkette | `audit/AuditService.java`, `audit/AttestierungService.java` |
| Warum-Trace | `provenance/WarumTraceService.java` |
| Audit-Export | `export/AuditExportService.java` |
| Guardrails-Quelle | `guardrails/GuardrailsService.java`, `resources/guardrails/engineering-guardrails.md` |
| Sandbox | `execution/sandbox/` |
| Host-Allowlist gegen SSRF/Token-Exfiltration | `common/RemoteUrlPolicy` |
| Migrationen | `app/src/main/resources/db/migration/` |
| CI | `.github/workflows/ci.yml` |
| ADRs | `docs/adr/` |
| Runbooks | `docs/runbooks/` |
| Versionshistorie | `CHANGELOG.md` |
