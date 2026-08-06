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

## 4.2 Das Run-Aggregat im Detail

`Run` ist die zentrale Entität und trägt bewusst mehr als reine
Ausführungsdaten — nämlich die Kopplung an Repository-Realität und
Qualitätsergebnis:

```java
UUID id, projectId, teamId;
String title, objective;
String adapterId;              // gewählter Vendor für genau diesen Lauf
RunKind kind;                  // BUILD | PLAN
String branchName, baseBranch; // Branch-Isolation
String prUrl;                  // Pull Request, falls Remote-Projekt
int correctionAttempts;        // Regelkreis-Zähler, hart begrenzt
String qualityGateDecision;    // PASS | WARN | FAIL | ERROR
RunStatus status;              // 14 Zustände
PhaseName currentPhase;        // 7 Phasen
OffsetDateTime startedAt, finishedAt, createdAt, updatedAt;
String triggeredBy;            // Mensch, Routine oder Folge-Run
List<RunPhase> phases;         // Komposition, mit dem Aggregat erzeugt
```

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

### 4.4.1 Die 39 Tabellen

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
4. **Genau eine aktive Policy-Version.** Erzwungen über partiellen
   Unique-Index in PostgreSQL plus Service-Logik. Ohne diese Invariante wäre
   die Frage „welche Regel galt zu diesem Zeitpunkt?" nicht beantwortbar.
5. **Zeitstempel auf Millisekunden getrunken.** Klingt nach Detail, ist aber
   Voraussetzung für byte-stabile Signaturen über den Datenbank-Roundtrip —
   ein typischer, teuer gelernter Fallstrick beim Signieren persistenter
   Daten.
