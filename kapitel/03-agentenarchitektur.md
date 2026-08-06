# 3 Die Agentenarchitektur im Überblick

## 3.1 Systemkontext des agentischen Entwicklungssystems

Bevor die interne Architektur des agentischen Entwicklungssystems betrachtet wird, ist es hilfreich, den Systemkontext zu verstehen.

Das agentische Entwicklungssystem ist nicht isoliert, sondern integriert sich in die bestehende Enterprise-Toolchain.

Typische Integrationspunkte sind:

- Versionsverwaltung (Git)
- CI/CD-Pipelines
- Knowledge Stores und Dokumentation
- Container-Runtime und Deploymentplattformen

Der Orchestrator bildet dabei die zentrale Steuerungseinheit, während spezialisierte Agenten Entwicklungsaufgaben automatisiert ausführen.

<!-- TODO(abbildung): Abbildung 2: Systemkontext -->

## 3.2 Referenzarchitektur des Agentensystems

Die Architektur folgt einem erweiterten Hub-and-Spoke-Modell. Im Zentrum steht der Orchestrator, der Arbeit an spezialisierte Subagenten verteilt, deren Ergebnisse koordiniert und einen gemeinsamen Wissensstand (Shared Knowledge Store) verwaltet. Dieses Modell bietet entscheidende Vorteile gegenüber einem monolithischen Agenten: Spezialisierung führt zu höherer Qualität, Parallelisierung beschleunigt den Gesamtprozess, und Isolation verhindert, dass ein fehlerhafter Agent die gesamte Pipeline beeinträchtigt.

<!-- TODO(abbildung): Abbildung 3: SDLC-Agenten-Pipeline – von der Anforderungsanalyse bis zum Deployment -->

## 3.3 Agentenübersicht

<!-- TODO(abbildung): Abbildung 4: Referenzarchitektur eines agentischen Entwicklungssystems im Enterprise-Kontext -->

Der Agent Layer besteht aus spezialisierten Rollen (Architektur, Planung, Requirements, Entwicklung, Testing, Review, Deployment), die jeweils klar begrenzte Verantwortlichkeiten besitzen.

Der Orchestrator übersetzt Ziele in einen Task-Graph, steuert Zustandsübergänge, Budgets und Stop-Conditions und sorgt für deterministische Abläufe.

Der Tool & Workspace Layer kapselt alle mutierenden Aktionen über Tool-Adapter und isolierte Workspaces, um unkontrollierte Seiteneffekte zu verhindern.

Der Governance Core (Execution Contracts, Risk Scoring, Policies, Approvals, Ledger/Audit) stellt sicher, dass Änderungen nur innerhalb definierter Regeln stattfinden.

Delivery & Runtime umfasst PR/Merge, Signierung/SBOM, CI/CD-Gates, Kubernetes Admission Policies sowie Observability.

## 3.4 Runtime-Architektur

<!-- TODO(abbildung): Abbildung 5: Runtime-Architektur eines agentischen Entwicklungssystems -->

Die Runtime-Architektur beschreibt den Ablauf eines Entwicklungsauftrags während der tatsächlichen Ausführung. Ein Entwicklungsziel wird zunächst vom Orchestrator entgegengenommen, der Zustände verwaltet, Budgets kontrolliert und Stop-Conditions definiert. Ein Planner-Agent zerlegt dieses Ziel anschließend in konkrete Aufgaben und delegiert sie an spezialisierte Agenten im Agent Pool.

| Agent | Rolle | Werkzeugzugriff |
| --- | --- | --- |
| Orchestrator | Verteilt Aufgaben, koordiniert Phasen, verwaltet Shared State | Alle Tools inkl. Task |
| Architektur-Agent | Analysiert Systemdesign, erstellt ADRs, bewertet Patterns | Read, Glob, Grep, LSP |
| Planungs-Agent | Erstellt detaillierte Implementierungspläne mit Meilensteinen | Read, Glob, Grep, Write |
| Requirements-Agent | Sammelt, validiert und trackt Anforderungen | Read, Glob, Grep, WebFetch |
| Entwicklungs-Agent | Implementiert Features nach Projektstandards und DDD | Read, Write, Edit, Bash, LSP |
| Testing-Agent | Erstellt und führt Unit-, Integrations- und E2E-Tests aus | Read, Write, Edit, Bash, Glob |
| Review-Agent | Prüft Code auf Qualität, Sicherheit und Domain-Compliance | Read, Glob, Grep, LSP |
| Deployment-Agent | Verwaltet IaC, führt Deployments mit K8s und Terraform aus | Read, Write, Edit, Bash |

## 3.5 Task-Tool Parameter

| Parameter | Pflicht | Typ | Beschreibung |
| --- | --- | --- | --- |
| subagent_type | Ja | string | Welcher Agententyp gestartet wird (z. B. "dev-agent") |
| prompt | Ja | string | Detaillierte Aufgabenanweisungen mit Kontext und Erwartungen |
| description | Ja | string | Kurze 3–5 Wort Zusammenfassung für das Logging |
| model | Nein | enum | sonnet (Standard), opus für komplexe Aufgaben, haiku für schnelle Tasks |
| max_turns | Nein | integer | Maximale API-Roundtrips bevor der Agent automatisch stoppt |
| run_in_background | Nein | boolean | Asynchrone Ausführung – gibt sofort die Agent-ID zurück |
| isolation | Nein | enum | "worktree" für isolierte Git-Worktree-Kopie des Repositories |
| resume | Nein | string | Agent-ID zum Fortsetzen einer unterbrochenen Sitzung |
