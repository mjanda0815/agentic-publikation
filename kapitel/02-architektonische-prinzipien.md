# 2 Architektonische Prinzipien

Jedes Enterprise-Architekturdokument basiert auf einem Set formaler Prinzipien, die als Leitplanken für alle Designentscheidungen dienen. Die folgenden acht Prinzipien bilden das Fundament der in diesem Whitepaper beschriebenen Control-Plane-Architektur. Sie sind gegenüber der v1.3 überarbeitet: Die Praxiserfahrung der Referenzimplementierung (Kapitel 19) und die Zielarchitektur der parallelen Agenten-Workflows (19.10) haben die ursprünglichen sechs Prinzipien geschärft und erweitert.

| Prinzip | Kurzformel | Beschreibung |
| --- | --- | --- |
| AP-1: Controlled Non-Determinism | Begrenzen statt vorhersagen | Das LLM-Ergebnis ist nicht deterministisch — kontrollierbar sind Zustände, Übergänge, Budgets, Policies, Schreibrechte, Freigaben, Gate-Regeln und Audit-Ereignisse. Die Architektur macht Agentenarbeit begrenzt und nachvollziehbar, nicht vorhersagbar. |
| AP-2: Single Writer per Workspace | Ein Schreiber je Arbeitskopie | Pro Branch, Worktree oder Workspace schreibt zu einem Zeitpunkt genau ein Agent. Das verhindert Schreibkonkurrenz, unklare Zurechnung und nicht attestierbare Zwischenstände. |
| AP-3: Parallelism by Dependency | Parallel nur, was unabhängig ist | Parallelität wird aus Task-Abhängigkeiten, Schreibbereichen, versionierten Verträgen und Risikopolicies abgeleitet — nicht aus festen Agentenrollen. Voneinander abhängige Komponenten werden erst parallel implementiert, wenn gemeinsame Verträge vorliegen. |
| AP-4: Independent Verification | Wer schreibt, gibt nicht frei | Erzeugung und Freigabe sind technisch getrennt: Read-only-Reviewer und Gates liefern strukturierte Befunde; ein Agent bewertet nie allein die eigene Arbeit. |
| AP-5: Policy as Executable Structure | Regeln als Code | Policies sind versionierter, signierter und attestierter Teil des Ausführungsmodells — keine Prosa-Dokumentation. Deklarative Repo-Konfiguration liefert den Kontext, technische Durchsetzung erfolgt über Tool-Rechte, Hooks und Gates. |
| AP-6: Human Authority | KI assistiert, Mensch entscheidet | Kritische Architektur-, Security-, Policy- und Deployment-Entscheidungen bleiben menschlich freigabepflichtig; die Freigabe ist ein Zustand im Prozess, kein Nebenkanal. |
| AP-7: Fail Closed | Ausfall ist kein Erfolg | Ein ausgefallener Pflicht-Reviewer, eine nicht prüfbare Policy oder eine fehlgeschlagene Attestierung darf niemals als Erfolg gelten. Ein Gate, dessen Ausfall wie Erfolg aussieht, ist schlimmer als kein Gate. |
| AP-8: Sovereign by Default | Läuft auch ohne Cloud | Die Architektur bleibt lokal, on-premises und ohne Cloud-Abhängigkeit betreibbar — bis hin zum Air-Gap-Betrieb. Skalierende Infrastruktur ist Option, nicht Voraussetzung. |

Diese Prinzipien stehen nicht isoliert, sondern bedingen sich gegenseitig: Controlled Non-Determinism (AP-1) ist der Grund, warum es die übrigen sieben braucht. Single Writer (AP-2) macht Zurechnung und Attestierung erst möglich, auf denen Independent Verification (AP-4) und Policy as Executable Structure (AP-5) aufsetzen. Parallelism by Dependency (AP-3) definiert, wann AP-2 mehrfach nebeneinander existieren darf. Human Authority (AP-6) und Fail Closed (AP-7) sind die Sicherheitsnetze für alles, was AP-1 nicht einfangen kann. Und Sovereign by Default (AP-8) stellt sicher, dass das Ganze dort betreibbar bleibt, wo die Anforderungen am strengsten sind.

**Was aus der Agentenspezialisierung wurde:** Die v1.3 führte „Agent Specialization“ als oberstes Prinzip. Die Praxis hat das relativiert: Spezialisierung ist kein Architekturprinzip, sondern eine mögliche Ausführungs- und Routingstrategie — Rollen und Fähigkeitsprofile werden in den Kontext eines Laufs projiziert oder über Capability-Routing auf Modelle abgebildet (Kapitel 5, 19.4), ohne dass daraus mehrere gleichzeitig schreibende Prozesse folgen müssen.

## Zuordnung zu Architekturkonzepten

| Prinzip | Kapitelreferenzen | Durchsetzung |
| --- | --- | --- |
| AP-1: Controlled Non-Determinism | Kap. 6 (Lifecycle), Kap. 7 (Execution Model) | Zustandsautomat, Turn-Limits, Execution Budgets, Timeouts |
| AP-2: Single Writer per Workspace | Kap. 16 (Workflows), Kap. 20 (ADR-2/ADR-5), 19.3/19.10 | Branch-/Worktree-Isolation, Workspace Leases (geplant) |
| AP-3: Parallelism by Dependency | Kap. 16, 19.10 | Task-Graph, Schreibbereiche, versionierte Verträge (geplant) |
| AP-4: Independent Verification | Kap. 12 (Guardrails), 19.5 | Read-only-Reviewer, Quality Gate, Claim Verification |
| AP-5: Policy as Executable Structure | Kap. 4 (Repo-Konfiguration), 19.6 | Signierte Policy-Dokumente, Hooks, Gate-Policies |
| AP-6: Human Authority | Kap. 9 (Failure Handling), 19.3 | Pflichtfreigaben als Prozesszustand, Segregation of Duties |
| AP-7: Fail Closed | Kap. 12, 19.5/19.7 | Reviewer-Ausfall führt zu ERROR, Lizenz fail closed, Attestierung ohne Schlüssel führt zu Startfehler |
| AP-8: Sovereign by Default | Kap. 13 (Deployment), 19.7 | Ein-Prozess-Betrieb, lokale Modelle, netzlose Sandbox, Lizenz ohne Rückkanal |

*Die Prinzipien und Referenzen wurden gegenüber v1.3 überarbeitet; die
damaligen sechs Prinzipien (u. a. „Deterministic Execution“, das die
Ausführung präziser als begrenzt und nachvollziehbar beschreibt) gehen in
den neuen acht auf.*

> **Praxis-Check SoftwareFabrik (erweitert):** Die Prinzipien sind dort
> nicht beschrieben, sondern maschinell erzwungen: ArchUnit-Tests brechen
> den Build bei Schichten- oder Vendor-Kopplungs-Verstößen, und ein
> Debt-Ratchet friert bestehende Altschuld gezählt ein, statt sie wachsen zu
> lassen (19.2). AP-2 und AP-4 gelten bereits im Einzel-Run (ein
> schreibender Agent je Lauf, mehrere unabhängige read-only Reviewer).
> AP-3 ist seit Release 0.23.0 vollständig implementiert (Feature-Flag,
> standardmäßig deaktiviert): Tasks werden aus einem Abhängigkeitsgraphen
> parallelisiert und laufen in getrennten Arbeitsverzeichnissen — seit
> 0.21.0 lesend, seit 0.22.0 auch schreibend, und seit 0.23.0 gebunden an
> versionierte Verträge, deren Änderung betroffene Tasks automatisch auf
> Neuplanung setzt. AP-2 gilt dabei Workflow-weit: Ein Task startet nur,
> wenn seine Schreibbereiche mit keinem aktiven Task kollidieren. Auch AP-6
> ist dort maschinell erzwungen — ein Task wird nur zurückgesetzt, wenn der
> Grund eine neue Eingabe trägt; Umsortieren allein genügt nicht (19.10).
