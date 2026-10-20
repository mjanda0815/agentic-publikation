# 4. Domänenmodell

## 4.1 Bounded Contexts und Aggregate

Die Fabrik modelliert **den Entwicklungsprozess selbst** als Fachdomäne. Das
ist der entscheidende Unterschied zu einem Werkzeug: Nicht der generierte Code
ist die Domäne, sondern Spezifikation, Lauf, Freigabe, Befund und Nachweis.

| Aggregat | Wurzel | Enthält / referenziert | Bounded Context |
|---|---|---|---|
| Projektspezifikation | `ProjectDefinition` | Vision, Tech-Stack, Vorgaben, Workspace-Pfad, Import-Quelle, Mandant | `projectdefinition` |
| Artefakt | `PromptArtifact` | versionierter Markdown-Inhalt, Art, relativer Pfad | `prompt` |
| Agententeam | `AgentTeam` | geordnete `AgentTeamMember` | `team` |
| Agentendefinition | `AgentDefinition` | Rolle, Mission, bevorzugtes Modell, aktive Skills | `agent` |
| **Lauf** | `Run` | `RunPhase` (Komposition), Logs/Checkpoints/Builds referenziell | `run` |
| Backlog-Element | `PlanItem` | Status, Reihenfolge, Quell-Run, Build-Run, Meilenstein, `dependsOn` | `sdlc` |
| Meilenstein | `ProjectMilestone` | Version, Status, zugeordnete Plan-Items | `sdlc` |
| Routine | `Routine` | Art (PLAN/BUILD), Zeitplan, aktiv/inaktiv | `sdlc` |
| Freigabe | `ApprovalPolicy` / `ApprovalDecision` | Phase, Entscheidung, Akteur | `policy` |
| Policy-Dokument | `PolicyDocument` | Version, kanonischer Inhalt, Ed25519-Signatur, aktiv-Flag | `policy` |
| Audit-Ereignis | `AuditEvent` | `seq`, `prev_hash`, `entry_hash`, `signature`, `key_id` | `audit` |
| Mandant | `Mandant` | Nutzer, Projekte, `MandantBudget` | `mandant` |
| Skill | `SkillCatalogEntry` | `SkillVersion`-Historie, Art, Herkunft | `skills` |
| Lieferkette | `SbomArtifact` | SBOM-Inhalt, Digest, Signatur | `validation` |
| Workflow (seit 0.21.0, Flag aus) | `Workflow` | Tasks mit Abhängigkeiten, Leases, Merge-Queue-Einträge, Planrevisionen | `workflow` |
| Vertrag (seit 0.23.0) | `ContractVersion` | unveränderliche Fassung, Content-Hash, Befunde | `contract` |
| Isolationsnachweis (seit 0.31.0) | `Isolationsnachweis` | Adapter, CLI-Version, Urteil `BESTANDEN`/`NICHT_BESTANDEN`/`UNGUELTIG`, Protokoll, Ed25519-Signatur | `mcp` |
| **Produkt-Spec** (seit 0.35.0, opt-in) | `Spec` | unveränderliche `SpecVersion` (SHA-256, `DRAFT → APPROVED → SUPERSEDED`), `SpecApproval`-Historie, `SpecFrage` | `spec` |

## 4.2 Das Run-Aggregat im Detail

`Run` ist die zentrale Entität und trägt bewusst mehr als reine
Ausführungsdaten — nämlich die Kopplung an Repository-Realität und
Qualitätsergebnis:

```java
UUID id, projectId, teamId;
String title, objective;
String adapterId;              // gewählter Vendor für genau diesen Lauf
RunKind kind;                  // BUILD | PLAN | SPEC (SPEC seit 0.38.0)
String branchName, baseBranch; // Branch-Isolation
String prUrl;                  // Pull Request, falls Remote-Projekt
int correctionAttempts;        // Regelkreis-Zähler, hart begrenzt
String qualityGateDecision;    // PASS | WARN | FAIL | ERROR
RunStatus status;              // 14 Zustände (Stand v0.38.0; neu WAITING_FOR_INPUT)
PhaseName currentPhase;        // 7 Phasen
OffsetDateTime startedAt, finishedAt, createdAt, updatedAt;
String triggeredBy;            // Mensch, Routine oder Folge-Run
UUID workflowId, workflowTaskId; // einmalige Zuordnung zu einer Workflow-Task (V40)
String workspacePath;          // eigener Worktree eines Child Runs (V42)
String mergeCommit, zurueckgenommenDurch; // Rollback-Anker (V53)
List<RunPhase> phases;         // Komposition, mit dem Aggregat erzeugt
```

*Stand v0.38.0* (`run/domain/Run.java`); die drei Feldzeilen vor
`phases` kamen mit 0.21.0–0.29.0 hinzu.

**Invariante:** Statuswechsel geschehen ausschließlich über
`RunOrchestrationService`; die erlaubten Übergänge liegen zentral in
`RunStatusTransitions`. Ein unerlaubter Übergang wirft
`InvalidRunStateTransitionException` statt still zu passieren.

`triggeredBy` ist klein, aber für die Publikation relevant: Es unterscheidet
menschlich ausgelöste, zeitgesteuerte (Routine) und agentisch angestoßene
Folgeläufe — die Grundlage jeder Aussage über Autonomiegrade.

## 4.3 Wissens- und Gedächtnisschicht

Die Fabrik hält drei klar getrennte Gedächtnisformen — nützlich als Kontrast
zum Fünf-Schichten-Memory-Modell aus v1.3 (Kapitel 8):

| Form | Träger | Lebensdauer | Zweck |
|---|---|---|---|
| Spezifikations-Gedächtnis | `PromptArtifact` (versioniert) | dauerhaft, editierbar | Absicht des Menschen, maschinenlesbar |
| Projekt-Gedächtnis | `ProjectMemory` → `MEMORY.md` im Workspace | dauerhaft, kuratiert | Learnings und Entscheidungen über Läufe hinweg |
| Lauf-Gedächtnis | Workspace + Git-Historie | dauerhaft pro Projekt | der reale Code-Stand als Zustand |
| Kontext-Gedächtnis | Kontextfenster des Agenten | ephemer | Arbeitsspeicher eines Laufs |

Bemerkenswert: Es gibt **keinen Vektorspeicher**. Der geteilte Wissensstand
wird über versionierte Dateien im Repository hergestellt, nicht über
Embeddings. Begründung im System: Was der Agent liest, muss ein Mensch
reviewen und ein Auditor zitieren können — eine Ähnlichkeitssuche erfüllt
beides nicht.

## 4.4 Persistenz

- PostgreSQL 18, Schemaverwaltung ausschließlich über Flyway
  (`app/src/main/resources/db/migration/`), `ddl-auto=validate`,
  `open-in-view=false`.
- UUID-Primärschlüssel über einen zentralen `IdGenerator`.
- Migrationen sind nach Auslieferung unveränderlich; die
  `architecture-reviewer`-Prüfung markiert Änderungen an bestehenden
  Migrationen als CRITICAL — ein Agent kann diese Regel also nicht umgehen.

### 4.4.1 Die 63 Tabellen (Stand v0.38.0; bei 0.19.0: 39)

**Spezifikation** `project_definition`, `instruction_set`,
`definition_of_done`, `prompt_artifact`, `artifact`, `project_memory`,
`wizard_draft`, `version_cache`, `agent_definition`, `agent_team`,
`agent_team_member`, `task`

**Ausführung** `run`, `run_phase`, `run_metrics`, `run_template`,
`execution_log`, `execution_step`, `build_result`, `git_checkpoint`,
`git_repository`

**Lebenszyklus** `plan_item`, `plan_item_dependency`, `project_milestone`,
`routine`

**Governance** `approval_policy`, `approval_decision`, `policy_document`,
`audit_event`, `audit_chain_checkpoint`, `mandant`, `mandant_budget`,
`app_user`, `app_setting`, `platform_setting`, `budget_config`

**Lieferkette / Wissen** `sbom_artifact`, `skill_catalog_entry`,
`skill_version`

**Workflow-Ebene (V41–V51)** `workflow`, `workflow_task`,
`workflow_task_dependency`, `workflow_task_artifact`,
`workflow_task_referenz`, `workflow_task_pfad`, `workflow_task_ressource`,
`workspace_lease`, `workspace_lease_pfad`, `workspace_lease_ressource`,
`merge_queue_entry`, `workflow_gate_result`, `workflow_plan_revision`,
`workflow_plan_revision_task`, `workflow_worker`

**Verträge (V46–V47)** `contract_version`, `contract_finding`,
`workflow_task_vertrag`, `workflow_task_vertragsbindung`

**MCP-Governance (V56)** `isolationsnachweis`

**Spec-Driven Development (V61, V65)** `spec`, `spec_version`,
`spec_approval`, `spec_frage`

### 4.4.2 Migrationsverlauf als Entwicklungsgeschichte

Der Verlauf liest sich wie die Reifungskurve des Systems und eignet sich gut
als Beleg dafür, dass Governance nachgezogen werden *musste*:

| Migrationen | Thema | Reifestufe |
|---|---|---|
| V1–V9 | Grundschema, Runs, Logs, Metriken, Budgets, Settings | Werkzeug |
| V12–V18 | Wizard-Zustand, Versions-Cache, Modellwahl, Templates, Repo-Import, Projekt-Memory | Prozess |
| V19–V25 | Plan-/Build-Runs, Branch, Remote+PR, Korrekturversuche, Quality Gate, erlaubte Adapter | Lebenszyklus |
| V26–V28 | Mandant, Nutzer-Mandanten-Bindung, Mandantenbudget | Mehrmandantenfähigkeit |
| V29–V33 | Audit-Hashkette, Policy-as-Code, SBOM, SBOM-Signatur, Ketten-Checkpoint | Nachweisfähigkeit |
| V34–V37 | Auslöser-Herkunft, harte Tenant-Isolation, Meilensteine, Backlog-Abhängigkeiten | Repository-Realität |
| V38–V39 | Skill-Bibliothek, Routinen | Wiederverwendung und Automatisierung |
| V40–V54 | Workflow-Ebene, Leases, Merge Queue, Contract Registry, Planrevisionen, Worker, Abdeckung, Rollback-Anker, Aufwand je Entscheidung (Details `12-kennzahlen-historie.md`) | Parallelisierung und Messung |
| V56 | `isolationsnachweis`: signiertes Laufzeit-Register des Canary-Harness (0.31.0) | MCP-Governance |
| V58 | `run_metrics.kosten_geschaetzt` (nullable): Abo-Kosten als Schätzung gekennzeichnet (0.33.0) | ehrliche Kosten |
| V59 | `workflow.aufwand_minuten`: Aufwandsfeld an der Planfreigabe (0.34.0) | Messung |
| V60 | `run_metrics.total_cache_creation_tokens`, `gemeldete_kosten_usd`: Cache-Schreib-Tokens und CLI-Kostenschätzung (0.34.0) | ehrliche Kosten |
| V61 | `spec`, `spec_version`, `spec_approval`, `project_definition.spec_modus` (0.35.0) | Anforderungsebene |
| V62 | `plan_item.spec_id`, `plan_item.ac_ids`: Backlog-Bezug (0.35.0) | Anforderungsebene |
| V63 | Spec-Bindung an `workflow_task` (Spec, Version, Hash, AC-IDs) (0.36.0) | Traceability |
| V64 | `plan_item.veraltet_grund`: Veraltet-Markierung durch Spec-Drift (0.38.0) | Spec-Drift |
| V65 | `spec_frage`: Rückfragen von Spec-Runs (0.38.0) | Spec-Run |

Stand v0.38.0: 61 Migrationsdateien, letzte V65; die Nummern V10, V11, V55
und V57 sind nicht vergeben.

## 4.5 Modellierungsentscheidungen mit Diskussionswert

1. **Aggregat = JPA-Entität.** Kein separates Persistenzmodell. Erspart
   Mapping-Code, verletzt aber die reine DDD-Lehre. Die Entscheidung ist
   dokumentiert und in den ArchUnit-Regeln bewusst ausgespart, statt sie
   stillschweigend zu brechen.
2. **`RunPhase` als Komposition, alles andere referenziell.** Phasen sind
   ohne Run sinnlos und werden mit ihm erzeugt; Logs, Checkpoints und
   Build-Ergebnisse wachsen unabhängig und sind über IDs verbunden — sonst
   würde jeder Aggregatzugriff Megabyte an Log-Zeilen laden.
3. **Ein Workspace pro Projekt, nicht pro Run.** Runs zweigen als Branch ab.
   Das ist die Voraussetzung dafür, dass ein zweiter Lauf auf dem Ergebnis des
   ersten aufsetzt — also für iterative Entwicklung statt wiederholtem
   Greenfield. Preis: Läufe desselben Projekts sind nicht beliebig parallel.
   (Stand v0.38.0: Seit 0.21.0 vergleicht die Sperre den *effektiven*
   Workspace; Child Runs der Workflow-Ebene laufen in getrennten Worktrees
   parallel, höchstens drei gleichzeitig — hinter dem Feature-Flag
   `softwarefabrik.workflow.enabled`, Default aus. Ein Run in
   `WAITING_FOR_INPUT` belegt keinen Workspace-Slot.)
4. **Genau eine aktive Policy-Version.** Erzwungen über partiellen
   Unique-Index in PostgreSQL plus Service-Logik. Ohne diese Invariante wäre
   die Frage „welche Regel galt zu diesem Zeitpunkt?" nicht beantwortbar.
5. **Zeitstempel auf Millisekunden trunkiert.** Klingt nach Detail, ist aber
   Voraussetzung für byte-stabile Signaturen über den Datenbank-Roundtrip —
   ein typischer, teuer gelernter Fallstrick beim Signieren persistenter
   Daten.
