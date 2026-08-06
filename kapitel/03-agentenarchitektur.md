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

![Systemkontext des agentischen Entwicklungssystems](abbildungen/out/abb02.pdf){width=100%}

## 3.2 Referenzarchitektur des Agentensystems

Die Architektur folgt einem erweiterten Hub-and-Spoke-Modell: Im Zentrum
steht der Orchestrator, der Arbeit an spezialisierte Rollen verteilt, deren
Ergebnisse koordiniert und einen gemeinsamen Wissensstand (Shared Knowledge
Store) verwaltet. Wichtig ist die Einordnung: Hub-and-Spoke ist eine
**logische Rollen- und Kommunikationsstruktur** — ob Rollen als separate
Agentenprozesse materialisiert werden, ist eine
Implementierungsentscheidung. Die Fallstudie in Kapitel 19 zeigt beide
Seiten: Kontextisolation verhindert Interferenzen, aber Parallelität
erzeugt Konfliktkosten, wenn Schreibbereiche nicht abgegrenzt sind, und
Spezialisierung ist nicht automatisch ein Qualitätsgewinn. Die aktuelle
Referenzimplementierung verwendet deshalb einen schreibenden Agenten je
Run und mehrere unabhängige Reviewer. Die Workflow-Ebene führt parallele
Child Runs ein — seit Release 0.21.0 für nicht-schreibende Analyse, und
schreibend erst bei abgegrenzten Schreibbereichen und erfüllten
Abhängigkeiten (AP-2/AP-3, Kapitel 19.10).

![SDLC-Agenten-Pipeline — von der Anforderungsanalyse bis zum Deployment](abbildungen/out/abb03.pdf){width=100%}

## 3.3 Agentenübersicht

![Referenzarchitektur eines agentischen Entwicklungssystems im Enterprise-Kontext](abbildungen/out/abb04.pdf){width=95%}

Der Agent Layer besteht aus spezialisierten Rollen (Architektur, Planung, Requirements, Entwicklung, Testing, Review, Deployment), die jeweils klar begrenzte Verantwortlichkeiten besitzen.

Der Orchestrator übersetzt Ziele in einen Task-Graph, steuert Zustandsübergänge, Budgets und Stop-Conditions und sorgt für begrenzte, nachvollziehbare Abläufe.

Der Tool & Workspace Layer kapselt alle mutierenden Aktionen über Tool-Adapter und isolierte Workspaces, um unkontrollierte Seiteneffekte zu verhindern.

Der Governance Core (Execution Contracts, Risk Scoring, Policies, Approvals, Ledger/Audit) erzwingt die definierten Regeln für Änderungen, soweit sie technisch prüfbar sind; die verbleibenden Risiken behandelt Kapitel 12.

Delivery & Runtime umfasst PR/Merge, Signierung/SBOM, CI/CD-Gates, Kubernetes Admission Policies sowie Observability.

## 3.4 Runtime-Architektur

![Runtime-Architektur eines agentischen Entwicklungssystems](abbildungen/out/abb05.pdf){width=100%}

Die Runtime-Architektur beschreibt den Ablauf eines Entwicklungsauftrags während der tatsächlichen Ausführung. Ein Entwicklungsziel wird zunächst vom Orchestrator entgegengenommen, der Zustände verwaltet, Budgets kontrolliert und Stop-Conditions definiert. Ein Planner-Agent zerlegt dieses Ziel anschließend in konkrete Aufgaben und delegiert sie an spezialisierte Agenten im Agent Pool.

| Agent | Rolle | Werkzeugzugriff |
| --- | --- | --- |
| Orchestrator | Verteilt Aufgaben, koordiniert Phasen, verwaltet Shared State | Alle Tools inkl. Agent (Subagenten-Start) |
| Architektur-Agent | Analysiert Systemdesign, erstellt ADRs, bewertet Patterns | Read, Glob, Grep, LSP |
| Planungs-Agent | Erstellt detaillierte Implementierungspläne mit Meilensteinen | Read, Glob, Grep, Write |
| Requirements-Agent | Sammelt, validiert und trackt Anforderungen | Read, Glob, Grep, WebFetch |
| Entwicklungs-Agent | Implementiert Features nach Projektstandards und DDD | Read, Write, Edit, Bash, LSP |
| Testing-Agent | Erstellt und führt Unit-, Integrations- und E2E-Tests aus | Read, Write, Edit, Bash, Glob |
| Review-Agent | Prüft Code auf Qualität, Sicherheit und Domain-Compliance | Read, Glob, Grep, LSP |
| Deployment-Agent | Verwaltet IaC, führt Deployments mit K8s und Terraform aus | Read, Write, Edit, Bash |

Mehrere schreibende Rollen bedeuten dabei nicht gleichzeitiges Schreiben: Wie die Rollen auf tatsächliche Läufe abgebildet werden, regeln AP-2 und AP-3 (vgl. 3.2 und Kapitel 2).

## 3.5 Parameter des Agent-Tools (in v1.3: „Task-Tool“)

Das Werkzeug, mit dem der Orchestrator Subagenten startet, heißt in Claude
Code inzwischen `Agent` (v1.3 dokumentierte es als „Task“). Die folgende
Tabelle ist auf den Stand von August 2026 aktualisiert [@claudecodedocs];
die Parameterliste ist schnelllebig und bei Umsetzung gegen die aktuelle
Werkzeug-Dokumentation zu prüfen:

| Parameter | Pflicht | Typ | Beschreibung |
| --- | --- | --- | --- |
| subagent_type | Ja | string | Welcher Agententyp gestartet wird (z. B. "code-reviewer"); eigene Typen werden als Markdown-Dateien mit Frontmatter unter `.claude/agents/` definiert |
| prompt | Ja | string | Detaillierte Aufgabenanweisungen mit Kontext und Erwartungen |
| description | Ja | string | Kurze Zusammenfassung der Aufgabe (laut Tool-Schema, für Anzeige und Logging) |
| model | Nein | enum | Modellklasse für diesen Agenten (sonnet, opus, haiku, …); ohne Angabe erbt der Agent das Modell der Hauptsitzung |
| run_in_background | Nein | boolean | Subagenten laufen inzwischen standardmäßig im Hintergrund; `false` erzwingt synchrone Ausführung |

Die Worktree-Isolation (`isolation: worktree` — eine isolierte
Git-Worktree-Kopie des Repositories je Agent) wird heute in der
Subagenten-Definition gesetzt, nicht je Aufruf.

Gegenüber v1.3 bemerkenswert: Das damals als Aufrufparameter dokumentierte
`max_turns` ist kein Parameter des Agent-Tools mehr — die Turn-Obergrenze
wird heute als `maxTurns` in der Subagenten-Definition (Frontmatter)
gesetzt. Und die Fortsetzung eines Agenten läuft nicht mehr über einen
`resume`-Parameter, sondern über eine Nachrichtenschnittstelle an den —
auch bereits beendeten — Agenten. Auch das illustriert eine Kernaussage
dieses Whitepapers:
Werkzeugdetails haben eine Halbwertszeit von Monaten — Architekturprinzipien
(ein Orchestrator, spezialisierte Subagenten mit eigenem Kontextfenster,
Isolation) bleiben.

> **Praxis-Check SoftwareFabrik (abweichend):** Die Fabrik nutzt dieses
> Werkzeugmuster bewusst nicht: Sie startet keine Subagenten, sondern genau
> einen Agentenprozess je Lauf in einer Sandbox. Spezialisierung entsteht
> über Rollen- und Teamdefinitionen im Kontext und über mehrere unabhängige
> Prüfer nach der Ausführung (19.3, 19.8).
