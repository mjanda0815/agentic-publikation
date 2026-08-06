# Roadmap – Weiterentwicklung der SoftwareFabrik zum parallelen Agentenmodell

**Status:** Entwurf  
**Ausgangspunkt:** SoftwareFabrik 0.19.0 / Whitepaper Version 2.0  
**Zielbild:** Auditierbare Agentic Software Factory mit parallelen, isolierten Agentenläufen, zentraler Orchestrierung und unabhängigen Quality Gates

## 1. Ziel

Die SoftwareFabrik wird von einer Control Plane für einzelne Agentenläufe zu einer Workflow-Plattform für mehrere koordinierte Agentenläufe weiterentwickelt.

Der bestehende Run bleibt die atomare Ausführungseinheit. Neu entsteht darüber eine Workflow-Ebene:

1. Ein **Workflow** bildet ein Feature oder Vorhaben ab.
2. Ein Workflow enthält mehrere **Workflow Tasks** mit Abhängigkeiten.
3. Jeder schreibende Task wird durch einen eigenen **Child Run** ausgeführt.
4. Jeder Child Run besitzt einen isolierten Branch oder Worktree.
5. Read-only Reviewer prüfen Child Runs parallel.
6. Ein Merge Coordinator führt erfolgreiche Ergebnisse kontrolliert zusammen.
7. Ein abschließendes Integration Gate validiert den Gesamtstand.

Leitregel:

> Parallelität findet zwischen isolierten Tasks und Runs statt. Innerhalb eines Workspace existiert genau ein schreibender Agent.

## 2. Architekturprinzipien

### AP-1: Single Writer per Workspace

Pro Branch, Worktree oder Arbeitskopie schreibt zu einem Zeitpunkt genau ein Agent.

### AP-2: Parallelism by Dependency

Parallelität wird aus Task-Abhängigkeiten, Schreibbereichen, Verträgen und Risikopolicies abgeleitet – nicht aus festen Agentenrollen.

### AP-3: Contracts before Parallel Implementation

Voneinander abhängige Komponenten dürfen erst parallel implementiert werden, wenn gemeinsame Verträge versioniert vorliegen, etwa OpenAPI, AsyncAPI, Java-Interfaces, Domain Events, DTO-Schemas oder Akzeptanzkriterien.

### AP-4: Independent Verification

Schreibende Agenten geben ihre Änderungen nicht selbst frei. Reviewer arbeiten read-only und liefern strukturierte Befunde.

### AP-5: Git plus Authoritative Process State

Git bleibt Artefakt-, Branch-, Commit- und Checkpoint-System. Workflow-, Policy-, Freigabe- und Audit-Zustand liegen autoritativ in der Datenbank.

### AP-6: Rule Loop instead of Blind Retry

Eine Wiederholung ist nur zulässig, wenn neue Informationen eingehen, zum Beispiel Compiler-Ausgaben, Reviewer-Findings, Merge-Konflikte, CI-Ergebnisse oder geänderte Verträge.

### AP-7: Fail Closed

Ein ausgefallener Pflicht-Reviewer, eine nicht prüfbare Policy oder eine fehlgeschlagene Attestierung darf niemals als Erfolg gelten.

## 3. Zielarchitektur

```text
Feature / Change Request
        |
        v
Workflow Planner
        |
        v
Task Graph / DAG
        |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
   Child Run A         Child Run B         Child Run C
   Branch A            Branch B            Branch C
   Single Writer       Single Writer       Single Writer
        |                   |                   |
        v                   v                   v
   Local Reviewers     Local Reviewers     Local Reviewers
        |                   |                   |
        +-------------------+-------------------+
                            |
                            v
                    Merge Coordinator
                            |
                            v
                  Workflow Integration Branch
                            |
                            v
                  Integration Quality Gate
                            |
                            v
                    Approval / PR / Merge
```

## 4. Neue fachliche Bausteine

### 4.1 Workflow

Ein Workflow ist die übergeordnete Ausführungseinheit für ein Feature oder Vorhaben.

```java
public enum WorkflowStatus {
    DRAFT,
    PLANNING,
    WAITING_FOR_PLAN_APPROVAL,
    READY,
    RUNNING,
    INTEGRATING,
    VALIDATING,
    WAITING_FOR_APPROVAL,
    COMPLETED,
    FAILED,
    CANCELLED
}
```

Kernattribute:

- Workflow-ID
- Mandant und Projekt
- Zielbeschreibung
- Planversion
- Integrationsbranch
- Budget und Policy-Version
- Status und Freigaben
- Audit-Referenzen

### 4.2 Workflow Task

```java
public enum WorkflowTaskStatus {
    BLOCKED,
    READY,
    CLAIMED,
    RUNNING,
    REVIEWING,
    PASSED,
    FAILED,
    WAITING_FOR_REPLAN,
    MERGING,
    MERGED,
    SUPERSEDED,
    CANCELLED
}
```

Kernattribute:

- Task-ID und Workflow-ID
- Ziel und Capability
- Abhängigkeiten
- erwartete Artefakte
- Owned Paths
- Read-only Paths
- Protected Paths
- Vertragsversionen
- Child-Run-ID
- Branch-/Worktree-Referenz
- lokales Gate-Ergebnis
- Merge-Status

### 4.3 Task Dependency

Abhängigkeitstypen:

- `FINISH_TO_START`
- `CONTRACT_REQUIRED`
- `ARTIFACT_REQUIRED`
- `APPROVAL_REQUIRED`
- `EXCLUSIVE_RESOURCE_REQUIRED`

### 4.4 Workspace Lease

```java
public record WorkspaceLease(
    UUID workflowId,
    UUID taskId,
    Set<String> ownedPaths,
    Set<String> ownedModules,
    Set<String> exclusiveResources,
    Instant expiresAt
) {}
```

Typische exklusive Ressourcen:

- `pom.xml`
- zentrale Build-Konfiguration
- Datenbankmigrationen
- gemeinsame API-Spezifikationen
- globale Security-Konfiguration
- Deployment-Basisdateien

### 4.5 Contract Version

Gemeinsame Verträge erhalten eine unveränderliche Version oder einen Content-Hash. Jeder Child Run attestiert, gegen welche Version er gearbeitet hat. Eine Vertragsänderung setzt betroffene Tasks auf `STALE` oder `WAITING_FOR_REPLAN`.

### 4.6 Merge Coordinator

Verantwortlichkeiten:

- Merge-Reihenfolge
- Rebase auf aktuellen Integrationsstand
- Konflikterkennung
- Vertragskompatibilitätsprüfung
- Revalidierung nach Merge
- automatische Korrekturschleife
- Eskalation an Mensch oder Replanner

### 4.7 Workflow Integration Gate

Prüfungen:

- Gesamtbuild
- Regression und Integrationstests
- End-to-End-Tests
- ArchUnit über den integrierten Stand
- API- und Event-Kompatibilität
- Migrationskonsistenz
- Dependency- und Lizenzprüfung
- Gesamt-SBOM
- Claim Verification
- LLM-basierter Integrationsreview
- Policy- und Freigabekonsistenz

## 5. Capability-Modell

Die Plattform erzwingt keine festen sieben Agentenrollen. Tasks werden nach Fähigkeiten klassifiziert.

### Schreibende Capabilities

- `DOMAIN_IMPLEMENTATION`
- `APPLICATION_IMPLEMENTATION`
- `API_IMPLEMENTATION`
- `PERSISTENCE_IMPLEMENTATION`
- `FRONTEND_IMPLEMENTATION`
- `TEST_IMPLEMENTATION`
- `INFRASTRUCTURE_IMPLEMENTATION`
- `DOCUMENTATION_IMPLEMENTATION`

### Analysierende Capabilities

- `REQUIREMENTS_ANALYSIS`
- `ARCHITECTURE_ANALYSIS`
- `SECURITY_ANALYSIS`
- `DEPENDENCY_ANALYSIS`
- `TEST_PLANNING`
- `MIGRATION_PLANNING`

### Prüfende Capabilities

- `CODE_REVIEW`
- `ARCHITECTURE_REVIEW`
- `SECURITY_REVIEW`
- `TEST_QUALITY_REVIEW`
- `CLAIM_VERIFICATION`
- `DEPENDENCY_REVIEW`
- `LICENSE_REVIEW`
- `INTEGRATION_REVIEW`

Die konkrete Modell- und Adapterwahl erfolgt über Capability-Routing.

## 6. Roadmap

### Phase 0 – Architektur- und Datenmodellvorbereitung

**Ziel:** Bestehende Run-Architektur für Parent-Child-Beziehungen vorbereiten.

Umfang:

- ADR für hierarchische Workflow-Orchestrierung
- ADR für Single Writer per Workspace
- Parent-Child-Referenz zwischen Workflow und Run
- Workflow-Ereignisse im Auditmodell
- Workflow-Daten im Warum-Trace
- Migrationskonzept für bestehende Runs
- Feature Flag für Workflow-Funktionen

Akzeptanzkriterien:

- Bestehende Einzel-Runs funktionieren unverändert.
- Ein Run kann optional einem Workflow Task zugeordnet werden.
- Audit- und Provenance-Daten bleiben vollständig.

### Phase 1 – Parallele Read-only-Analyse

**Vorgeschlagene Version:** 0.20.x  
**Risiko:** niedrig

Umfang:

- Workflow-Aggregat
- Workflow Tasks ohne Schreibrechte
- einfacher DAG
- parallele Analyse-Runs
- Synthese-Task
- menschliche Planfreigabe
- Workflow-Budget und Workflow-Audit

Pilot-Agenten:

- Requirements Analysis
- Architecture Analysis
- Security Analysis
- Test Planning

Akzeptanzkriterien:

- Mindestens drei Analyse-Runs laufen parallel.
- Widersprüche werden explizit ausgewiesen.
- Der Synthese-Schritt referenziert alle Eingangsergebnisse.
- Kein Analyse-Agent besitzt Schreibrechte auf Produktivcode.

### Phase 2 – Parallele Child Runs für unabhängige Module

**Vorgeschlagene Version:** 0.21.x  
**Risiko:** mittel

Umfang:

- Child Runs
- Branch oder Worktree je Task
- Workspace Leases
- Owned-/Read-only-/Protected-Path-Modell
- Exklusiv-Locks
- maximal drei parallele Child Runs pro Workflow
- Workflow-Integrationsbranch
- einfache Merge Queue
- lokales Gate je Child Run
- Integration Gate
- Kaskaden-Cancellation

Geeignete erste Parallelisierung:

- Backend und Frontend
- Produktivcode und Dokumentation
- zwei unabhängige Bounded Contexts
- Anwendungscode und Deployment-Artefakte

Akzeptanzkriterien:

- Drei unabhängige Tasks können parallel ausgeführt werden.
- Überschneidende Schreibbereiche werden vor Ausführung blockiert.
- Ein erfolgreicher Workflow wird nur nach Integration Gate abgeschlossen.

### Phase 3 – Vertragsbasierte Parallelisierung

**Vorgeschlagene Version:** 0.22.x  
**Risiko:** mittel bis hoch

Umfang:

- Contract Registry
- Content-Hash je Vertrag
- Vertragsabhängigkeiten im DAG
- automatische Stale-Erkennung
- Replanning bei Vertragsänderung
- Consumer-/Provider-Vertragstests
- OpenAPI-/AsyncAPI-Validierung

Akzeptanzkriterien:

- Jeder Child Run weist die verwendete Vertragsversion nach.
- Veraltete Tasks können nicht ungeprüft gemergt werden.
- Vertragsbrüche erzeugen strukturierte Findings.

### Phase 4 – Dynamisches Replanning und Merge Intelligence

**Vorgeschlagene Version:** 0.23.x  
**Risiko:** hoch

Umfang:

- Replanner-Service
- Task-Aufteilung und -Zusammenführung
- Invalidierung nach Vertrags- oder Architekturänderung
- automatische Änderung der Ausführungsreihenfolge
- Konfliktklassifikation
- Rebase- und Revalidation-Pipeline
- Human Escalation mit vollständigem Kontext

Akzeptanzkriterien:

- Kein automatischer Wiederholungsversuch ohne neue Eingabe.
- Jede Planänderung ist versioniert und attestiert.
- Der Warum-Trace zeigt Planversionen und Replanning-Gründe.

### Phase 5 – Distributed Worker Pool

**Vorgeschlagene Version:** 0.24.x oder später  
**Voraussetzung:** messbarer Bedarf

Umfang:

- persistente Task Queue
- Worker Leasing und Heartbeats
- Dead-Worker-Erkennung
- idempotente Task-Übernahme
- horizontale Skalierung
- Kubernetes optional
- Single-Host- und Air-Gap-Betrieb bleiben erhalten

Akzeptanzkriterien:

- Ein Workflow kann Child Runs auf mehreren Workern ausführen.
- Worker-Ausfall führt nicht zu stillem Erfolg.
- Ein Task wird höchstens einmal aktiv geschrieben.

### Phase 6 – Produktivitäts- und Qualitätsmessung

Begleitend ab 0.20.x.

Messgrößen:

- menschliche aktive Arbeitszeit
- Time to Accepted Merge
- First-Pass-Gate-Rate
- Korrekturschleifen und Replans
- Kosten je Child Run und Workflow
- Merge-Konfliktrate
- entkommene Defekte und Rollbacks
- Reviewzeit
- Testabdeckungsänderung

Verglichen werden:

- manuelle Umsetzung
- Single-Run-SoftwareFabrik
- paralleler Workflow

## 7. Datenmodellvorschlag

Neue Tabellen beziehungsweise Aggregate:

- `workflow`
- `workflow_plan`
- `workflow_task`
- `workflow_task_dependency`
- `workflow_task_artifact`
- `workflow_contract`
- `workflow_contract_version`
- `workspace_lease`
- `exclusive_resource_lock`
- `merge_queue_entry`
- `integration_result`
- `workflow_gate_result`
- `workflow_approval`
- `workflow_metric`

Bestehende Run-Daten werden ergänzt um:

- `workflow_task_id`
- `parent_workflow_id`
- `plan_version`
- `contract_version_set`
- `workspace_lease_id`

## 8. Sicherheitsanforderungen

Pflicht:

- Single Writer technisch erzwingen
- Prozess- oder Containerisolation je Child Run
- getrennte Credentials je Task
- Environment-Allowlist
- standardmäßig kein Netzwerkzugriff
- Host-Allowlist für Git-Remotes
- keine schreibenden Reviewer
- kein Erfolg bei Reviewer-Ausfall
- Mandantenisolation
- Audit aller Lock-, Merge-, Policy- und Replanning-Ereignisse
- sichere Bereinigung abgelaufener Workspaces

Neue Tests:

- parallele Schreibversuche auf gesperrte Pfade
- Lease-Ablauf während eines Runs
- Worker-Absturz mit aktivem Lease
- veraltete Vertragsversion
- Reviewer-Ausfall
- Merge-Queue-Race
- Cross-Tenant-Zugriff auf Workflow und Child Run

## 9. Betriebsmodi

### Local / Single Host

- ein Anwendungsprozess
- eine Datenbank
- Child Runs als lokale Prozesse oder Container
- begrenzte Parallelität
- Air-Gap-fähig

### Enterprise Single Host

- mehrere parallele Container
- Ressourcenlimits
- lokaler Artefaktcache
- strikte Policies und Attestierung

### Distributed

- mehrere Worker
- persistente Queue
- verteilte Leases
- optionale Kubernetes-Ausführung
- zentrale Control Plane

## 10. Pilotfeature

**Vorschlag:** Kundenverwaltung

1. Vertrag und Domänenmodell
2. REST API
3. Persistence Adapter
4. Test Suite
5. Dokumentation

Nach Abschluss des Vertrags- und Domain-Tasks können die übrigen Tasks teilweise parallel laufen.

## 11. Definition of Done für das Parallel Workflow MVP

Das MVP gilt als erreicht, wenn:

- ein Parent Workflow mindestens drei Child Runs steuert,
- ein DAG Abhängigkeiten erzwingt,
- Child Runs in getrennten Branches oder Worktrees arbeiten,
- Workspace Leases konkurrierende Schreibzugriffe verhindern,
- jeder Child Run ein lokales Gate durchläuft,
- ein Integrationsbranch verwendet wird,
- ein abschließendes Gesamtgate existiert,
- Merge-Konflikte als strukturierte Eingabe zurückgeführt werden,
- Workflow und Child Runs vollständig im Warum-Trace erscheinen,
- mindestens ein echter End-to-End-Pilot reproduzierbar erfolgreich durchlaufen wurde.

## 12. Nicht-Ziele der ersten Ausbaustufen

- freie Agent-zu-Agent-Chats
- unbegrenzte Parallelität
- automatische Architekturentscheidungen ohne Freigabe
- autonomes Produktionsdeployment
- Kubernetes als Pflicht
- Multi-Repository-Transaktionen
- vollständig selbstheilende Workflows
- empirisch unbelegte Produktivitätsversprechen

## 13. Hauptrisiken

### Integrationskosten übersteigen Parallelitätsgewinn

Gegenmaßnahmen: klare Task-Grenzen, Verträge vorab, Merge Queue, Konfliktmetriken.

### Veraltete Task-Grundlage

Gegenmaßnahmen: Vertrags- und Basis-Hashes, Stale-Erkennung, Rebase vor Gate und Merge.

### Unklare Verantwortlichkeit

Gegenmaßnahmen: ein Child Run je Task, eindeutige Artefakt- und Branch-Zuordnung, vollständiger Warum-Trace.

### Lock- und Lease-Probleme

Gegenmaßnahmen: TTL, Heartbeats, Recovery-Zustände und fail closed bei unklarem Besitz.

### Zu hohe Control-Plane-Komplexität

Gegenmaßnahmen: schrittweiser Ausbau, Feature Flags, bestehende Einzel-Runs erhalten und keine verteilte Infrastruktur ohne gemessenen Bedarf.

## 14. Nächste Entwicklungsiteration

Die nächste Iteration sollte nur Phase 0 und Phase 1 umfassen:

1. Workflow-Aggregat
2. Workflow Task
3. Parent-Child-Beziehung zu Run
4. einfacher DAG
5. parallele read-only Analyse
6. Synthese-Task
7. Workflow-Audit
8. Workflow-Why-Trace
9. menschliche Planfreigabe
10. End-to-End-Test mit vier Analyse-Agenten
