# 22 End-to-End: Payment Service Implementation

Während die vorherigen Kapitel die Architektur, das Ausführungsmodell und die Governance-Mechanismen eines agentischen Entwicklungssystems beschreiben, zeigt dieses Kapitel den vollständigen Ablauf einer realistischen Feature-Implementierung.

Als Beispiel dient die Entwicklung eines Payment Services für eine E-Commerce-Plattform. Der Service stellt eine REST-API zur Verarbeitung von Zahlungen bereit, publiziert Domain Events über Kafka und wird containerisiert in einer Kubernetes-Umgebung betrieben.

Der Ablauf demonstriert, wie der Orchestrator spezialisierte Agenten entlang des Software Development Lifecycle koordiniert. Beginnend mit der Anforderungsanalyse werden Architekturentscheidungen getroffen, Implementierungsaufgaben geplant, Code generiert, Tests erstellt und schließlich das Deployment vorbereitet.

Dabei wird sichtbar, wie die zuvor eingeführten Konzepte – insbesondere Task Graph, Workspace Isolation, Guardrails Pipeline und Shared Knowledge Store – in einem zusammenhängenden Workflow zusammenspielen.

Das folgende Beispiel zeigt die agentische Orchestrierung eines solchen Entwicklungsauftrags in Form eines vereinfachten Task-Workflows.

## 22.1 Ausgangssituation

In diesem Szenario wird die Implementierung eines Payment Services für eine E-Commerce-Plattform betrachtet. Der Service stellt eine REST-basierte API zur Verarbeitung von Zahlungen bereit, verwaltet Zahlungszustände innerhalb eines Domain-Driven-Design-Modells und publiziert relevante Domain Events über Apache Kafka, um andere Systeme über erfolgreiche oder fehlgeschlagene Transaktionen zu informieren.

Der Service muss dabei mehrere Anforderungen erfüllen. Dazu gehören eine klare Trennung der Domänenschichten gemäß hexagonaler Architektur, die Einhaltung regulatorischer Anforderungen wie PSD2 sowie eine sichere Integration in bestehende Plattformkomponenten. Darüber hinaus muss der Service containerisiert bereitgestellt und in einer Kubernetes-Umgebung betrieben werden können.

Der Entwicklungsauftrag wird nicht manuell umgesetzt, sondern durch ein agentisches Entwicklungssystem orchestriert. Ein zentraler Orchestrator übersetzt das Entwicklungsziel in einen Task Graph, der von spezialisierten Agenten entlang des Software Development Lifecycle abgearbeitet wird. Jeder Agent übernimmt dabei eine klar abgegrenzte Verantwortung, beispielsweise für Anforderungsanalyse, Architekturentscheidungen, Implementierung, Tests oder Deployment.

Während der gesamten Ausführung greifen die Agenten auf einen Shared Knowledge Store zu, in dem Projektdokumentation, Architekturentscheidungen und relevante Kontextinformationen abgelegt sind. Gleichzeitig stellt eine mehrstufige Guardrails-Pipeline sicher, dass generierter Code Qualitäts-, Sicherheits- und Architekturregeln einhält.

Das folgende Beispiel zeigt, wie ein solcher Entwicklungsauftrag durch den Orchestrator in mehrere Phasen zerlegt und durch spezialisierte Agenten umgesetzt wird.

## 22.2 Gesamtworkflow

Der folgende Ablauf zeigt den vollständigen Lebenszyklus einer Feature-Implementierung innerhalb des agentischen Entwicklungssystems. Ein Feature-Request wird vom Orchestrator entgegengenommen und in mehrere Phasen des Software Development Lifecycle zerlegt. Für jede Phase wird ein spezialisierter Agent gestartet, der innerhalb eines isolierten Workspaces arbeitet und auf den gemeinsamen Wissensspeicher zugreifen kann.

Der Workflow beginnt mit der Analyse der Anforderungen und der Ableitung einer geeigneten Architektur. Anschließend erstellt der Planungsagent einen Implementierungsplan, der von mehreren Entwicklungsagenten umgesetzt wird. Nach der Implementierung werden automatisch Tests generiert und ausgeführt, bevor ein Review-Agent die Einhaltung von Architektur- und Sicherheitsregeln prüft.

Abschließend übernimmt ein Deployment-Agent die Erstellung der notwendigen Infrastrukturartefakte und bereitet das Deployment in der Zielumgebung vor.

Die folgende Abbildung zeigt den Gesamtworkflow der agentischen Umsetzung eines Features.

<!-- TODO(abbildung): Abbildung 19: End-to-End Workflow -->

Während das vorherige Diagramm den Ablauf eines Entwicklungsauftrags zeigt, ist für das Verständnis der Architektur auch relevant, welche Systemkomponenten während dieses Prozesses miteinander interagieren.

Der Orchestrator fungiert dabei als zentrale Steuerungseinheit des agentischen Entwicklungssystems. Er übersetzt Entwicklungsziele in einen Task Graph und startet spezialisierte Agenten, die jeweils klar abgegrenzte Aufgaben übernehmen. Diese Agenten arbeiten in isolierten Workspaces und greifen über definierte Tool-Schnittstellen auf Build-Systeme, Testframeworks und Deployment-Werkzeuge zu.

Die folgende Abbildung zeigt, wie die einzelnen Architekturkomponenten während eines End-to-End-Workflows zusammenwirken.

<!-- TODO(abbildung): Abbildung 20: Interaktion der Systemkomponenten -->

## 22.3 Agentischer Workflow

> **Versionshinweis (v2.0):** Die folgenden Aufruf-Skizzen sind Pseudocode
> auf v1.3-Werkzeugstand; das Werkzeug heißt heute `Agent`, und
> `isolation: worktree` wird in der Subagenten-Definition gesetzt
> (vgl. 3.5).

```
// PHASE 1: Requirements & Architektur
Task(subagent_type="requirements-agent",
    prompt="Stories für payment-service aus Jira Sprint 43. RTM erstellen.")
Task(subagent_type="architecture-agent", model="opus",
    prompt="Hexagonale Architektur, DDD, Kafka, PSD2. Output: ADR + Shared Knowledge Store")

// PHASE 2: Planung
Task(subagent_type="planning-agent",
    prompt="Implementierungstracker: Domain -> Application -> Infra -> Test -> Deploy")

// PHASE 3: Implementierung (sequenziell + parallel)
Task(subagent_type="dev-agent", prompt="Domain Layer: Entities, Value Objects, Events.")
Task(subagent_type="dev-agent", prompt="Application: Controllers, Security.", isolation="worktree")
Task(subagent_type="dev-agent", prompt="Infra: Kafka, Outbox.", isolation="worktree")

// PHASE 4: Testing & Review
Task(subagent_type="test-agent", prompt="JUnit 5 + Testcontainers. Min. 80% Coverage.")
Task(subagent_type="review-agent", model="opus", prompt="PSD2, Confidence, Domain-Compliance.")

// PHASE 5: Deployment
Task(subagent_type="deploy-agent", prompt="K8s-Manifeste, HPA, TLS-Ingress.")
Task(subagent_type="qa-guard", prompt="Finale Validierung: 100% Tests, Security.")
```

## 22.4 Artefakte des Workflows

Der agentische Workflow erzeugt nicht nur Quellcode, sondern eine Reihe strukturierter Artefakte, die den gesamten Entwicklungsprozess nachvollziehbar und wiederverwendbar machen. Dazu gehören Anforderungen, Architekturentscheidungen, Implementierungspläne, Quellcode, Tests sowie Deployment-Artefakte.

Im vorliegenden Beispiel entstehen typischerweise folgende Ergebnisse:

- Anforderungsdokumentation und Traceability Matrix für den Payment Service
- Architekturartefakte wie ADRs und Einträge im Shared Knowledge Store
- Implementierter Code für Domain-, Application- und Infrastructure-Layer
- Automatisch erzeugte Unit- und Integrationstests
- Deployment-Artefakte wie Kubernetes-Manifeste, HPA-Konfiguration und TLS-Ingress-Regeln

Diese Artefakte bilden zusammen die technische und fachliche Grundlage für den produktiven Betrieb des Payment Services. Gleichzeitig ermöglichen sie eine vollständige Nachvollziehbarkeit der Entscheidungen und Änderungen entlang des gesamten Entwicklungslebenszyklus.

## 22.5 Guardrails Pipeline

Ein wesentliches Merkmal des End-to-End-Szenarios ist die konsequente Einbettung von Guardrails in jede Phase des Entwicklungsprozesses. Agentisch erzeugte Änderungen werden nicht ungeprüft übernommen, sondern durchlaufen eine mehrstufige Validierungs- und Governance-Pipeline.

Im Payment-Service-Beispiel umfasst diese Pipeline insbesondere:

- Syntax- und Compile-Prüfungen zur Sicherstellung der technischen Korrektheit
- Style- und Konventionsprüfungen gemäß den in CLAUDE.md definierten Projektstandards
- Security-Scans zur Erkennung potenzieller Schwachstellen oder problematischer Abhängigkeiten
- Domain-Prüfungen zur Absicherung von Bounded Contexts, Glossarregeln und DDD-Konventionen
- Automatisierte Tests mit vorgegebenen Mindestanforderungen an die Testabdeckung
- Confidence-Scoring zur Bewertung unsicherer oder potenziell halluzinierter Änderungen

Erst wenn alle Prüfungen erfolgreich bestanden wurden, kann der Workflow in die nächste Phase übergehen. Dadurch wird sichergestellt, dass agentisch erzeugter Code denselben Qualitäts-, Sicherheits- und Architekturmaßstäben genügt wie manuell entwickelte Software.

## 22.6 Deployment Ergebnis

Das End-to-End-Szenario zeigt, dass ein agentisches Entwicklungssystem weit mehr ist als ein Werkzeug zur Codegenerierung. Der Orchestrator koordiniert spezialisierte Agenten entlang des gesamten Software Development Lifecycle und verbindet Anforderungen, Architektur, Implementierung, Tests, Review und Deployment in einem konsistenten Ablauf.

Im Payment-Service-Beispiel wird deutlich, dass insbesondere folgende Vorteile erzielt werden können:

- klare Trennung von Verantwortlichkeiten zwischen spezialisierten Agenten
- reproduzierbare und nachvollziehbare Entwicklungsabläufe
- frühzeitige Validierung von Architektur-, Sicherheits- und Qualitätsanforderungen
- bessere Wiederverwendbarkeit von Wissen durch Shared Knowledge Store und ADRs
- höhere Geschwindigkeit bei gleichzeitig kontrollierter Qualitätssicherung

Damit wird das agentische Entwicklungssystem zu einer belastbaren Architektur für die Umsetzung komplexer Features in Enterprise-Umgebungen. Das Beispiel des Payment Services verdeutlicht, wie die in den vorangegangenen Kapiteln beschriebenen Konzepte in der Praxis zusammenspielen und gemeinsam einen produktionsnahen Entwicklungsprozess ermöglichen.

> **Praxis-Check SoftwareFabrik (bestätigt):** Der hier skizzierte
> End-to-End-Pfad ist dort reproduzierbar produktisiert: Wizard
> (18 Templates inklusive Repo-Import) → versionierte
> Spezifikations-Artefakte → Run → Quality Gate → Merge bzw. Pull Request
> (19.1).
