# 22 End-to-End: Payment Service Implementation

Während die vorherigen Kapitel die Architektur, das Ausführungsmodell und die Governance-Mechanismen eines agentischen Entwicklungssystems beschreiben, zeigt dieses Kapitel den vollständigen Ablauf einer realistischen Feature-Implementierung.

Als Beispiel dient die Entwicklung eines Payment Services für eine E-Commerce-Plattform. Der Service stellt eine REST-API zur Verarbeitung von Zahlungen bereit, publiziert Domain Events über Kafka und wird containerisiert in einer Kubernetes-Umgebung betrieben.

Der Ablauf demonstriert, wie der Orchestrator spezialisierte Agenten entlang des Software Development Lifecycle koordiniert. Beginnend mit der Anforderungsanalyse werden Architekturentscheidungen getroffen, Implementierungsaufgaben geplant, Code generiert, Tests erstellt und schließlich das Deployment vorbereitet.

Dabei wird sichtbar, wie die zuvor eingeführten Konzepte – insbesondere Task Graph, Workspace Isolation, Guardrails Pipeline und Shared Knowledge Store – in einem zusammenhängenden Workflow zusammenspielen.

> **Aufbau dieses Kapitels (v2.1):** Abschnitt 22.3 zeigt den Ablauf so,
> wie er heute in der Referenzimplementierung stattfindet — ein
> **Single-Run-Prozess** mit einem schreibenden Agenten und parallelen
> Reviewern (Teil A, implementiert). Abschnitt 22.4 zeigt denselben Auftrag
> als **parallelen Workflow** der Zielarchitektur (Teil B, geplant). Die
> ursprüngliche v1.3-Skizze mit sieben gleichzeitig arbeitenden
> Lebenszyklus-Agenten ist damit durch zwei präzise Varianten ersetzt: die,
> die läuft, und die, die geplant ist.

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

*(Die Workflow-Abbildungen der v1.3 an dieser Stelle — „End-to-End Workflow“ und „Interaktion der Systemkomponenten“ — sind in v2.0 mit den inhaltsgleichen Darstellungen in Kapitel 16 und Kapitel 20 konsolidiert.)*

Während das vorherige Diagramm den Ablauf eines Entwicklungsauftrags zeigt, ist für das Verständnis der Architektur auch relevant, welche Systemkomponenten während dieses Prozesses miteinander interagieren.

Der Orchestrator fungiert dabei als zentrale Steuerungseinheit des agentischen Entwicklungssystems. Er übersetzt Entwicklungsziele in einen Task Graph und startet spezialisierte Agenten, die jeweils klar abgegrenzte Aufgaben übernehmen. Diese Agenten arbeiten in isolierten Workspaces und greifen über definierte Tool-Schnittstellen auf Build-Systeme, Testframeworks und Deployment-Werkzeuge zu.

Die folgende Abbildung zeigt, wie die einzelnen Architekturkomponenten während eines End-to-End-Workflows zusammenwirken.

## 22.3 Teil A — der implementierte Single-Run-Prozess

> **Status: implementiert** (Referenzimplementierung, Stand 0.19.0; vgl.
> Kapitel 19.1–19.3).

So läuft der Auftrag heute. Ein Lauf, ein schreibender Agent, mehrere
unabhängige Prüfer:

1. **Spezifizieren.** Aus dem Wizard entstehen versionierte
   Markdown-Artefakte (Projektbeschreibung, Instruktionen, Guardrails,
   Definition of Done). Der Mensch editiert sie, bevor der Lauf startet —
   hier wird Absicht maschinenlesbar.
2. **Anlegen und prüfen.** Der Orchestrator prüft Modell-Policy, erlaubte
   Adapter, Attestierungspflicht und Budgetgrenzen; die geltende
   Policy-Version wird attestiert. Verlangt sie eine Freigabe vor der
   Ausführung, geht der Lauf in `WAITING_FOR_APPROVAL`.
3. **Workspace vorbereiten.** Der projektpersistente Workspace wird auf den
   Remote-Stand vorgespult, die Spezifikations-Artefakte, das
   Projektgedächtnis und die Guardrails-Projektion (`AGENTS.md` plus
   minimale `CLAUDE.md`) werden geschrieben, dann zweigt der Lauf auf einen
   eigenen Branch ab (`sdlc/run-<id>`).
4. **Ausführen.** Genau **ein** Agentenprozess läuft in der Sandbox auf dem
   Workspace — Domain, Application und Infrastruktur des Payment Service
   entstehen nacheinander im selben Lauf. Logs, Token- und Kostenzähler
   laufen live mit.
5. **Validieren.** Build-Gate (`mvn verify`), Commit auf dem Run-Branch —
   auch bei Misserfolg, damit die Arbeit inspizierbar bleibt —, optional
   SBOM, dann das Quality Gate: sechs Read-only-Reviewer parallel auf dem
   Diff (LLM-Review, Security, Architektur, Claim Verification,
   Dependency-Scan), aggregiert zu PASS/WARN/FAIL bzw. ERROR.
6. **Korrigieren.** Bei Build-Fehler, blockierendem Gate, Merge-Konflikt
   oder roter CI wird der Befund als Feedback-Text in einen erneuten
   Agentenlauf eingespeist — maximal zwei Versuche, danach bleibt der Lauf
   in `NEEDS_CORRECTION`.
7. **Übergeben.** Lokaler Merge oder Push mit Pull Request; im PR-Fall
   wartet der Lauf auf grüne CI und Merge. Erst dann gilt das
   Backlog-Element als erledigt.
8. **Belegen.** Jeder Schritt liegt als signiertes Glied der Audit-Kette
   vor; der Warum-Trace beantwortet für diesen Payment Service, welche
   Policy galt, welches Modell gearbeitet hat und wer freigegeben hat.

Die Parallelität liegt hier ausschließlich in Schritt 5 — bei der
Bewertung, nicht bei der Erzeugung (AP-2, AP-4).

## 22.4 Teil B — derselbe Auftrag als paralleler Workflow

> **Status: geplant** (Zielarchitektur; vgl. 19.10 und ADR-5 bis ADR-7).
> Die folgende Skizze ist Pseudocode und beschreibt kein heute verfügbares
> Verhalten.

Der Payment Service besteht aus Teilen, die sich sauber schneiden lassen —
genau der Fall, für den die Workflow-Ebene gedacht ist:

```text
Parent Workflow: "Payment Service"
   │
   ├─ Task 1  Contract Task (blockierend)
   │          OpenAPI-Spezifikation + Domain Events + DTO-Schemas
   │          → Contract Version v1 (Content-Hash), attestiert
   │
   ├─ Task 2  Domain-Implementierung      (unabhängig von Task 3, 4)
   │          Owned Paths: domain/**      Child Run A, Branch A
   │
   ├─ Task 3  API-/Application-Schicht    (unabhängig von Task 2, 4)
   │          Owned Paths: adapter/in/**  Child Run B, Branch B
   │
   ├─ Task 4  Infrastruktur (Kafka/Outbox) (unabhängig von Task 2, 3)
   │          Owned Paths: adapter/out/** Child Run C, Branch C
   │          Exklusiv-Lock: db/migration/**
   │
   ├─ Task 5  Tests (abhängig von 2–4)
   │
   └─ Task 6  Deployment-Artefakte (abhängig von 5)
```

Der Ablauf: Der Contract Task läuft zuerst und allein — ohne versionierte
Verträge keine parallele Implementierung (AP-3). Danach starten die Tasks 2
bis 4 als **Child Runs** mit je eigenem Branch und je genau einem
schreibenden Agenten (AP-2); ihre Schreibbereiche überschneiden sich nicht,
und die Datenbankmigrationen sind über ein Exklusiv-Lock serialisiert. Jeder
Child Run durchläuft sein **lokales Task-Gate**. Der **Merge Coordinator**
führt die erfolgreichen Ergebnisse in definierter Reihenfolge auf den
Integrationsbranch, rebased auf den jeweils aktuellen Stand und
klassifiziert Konflikte; ein Vertragsbruch oder ein veralteter Basisstand
setzt den betroffenen Task auf Neuplanung statt auf blindes Retry (AP-1,
19.10). Das **Integration Gate** prüft den zusammengeführten Stand als
Ganzes — Gesamtbuild, Regression, End-to-End, API- und
Event-Kompatibilität, Migrationskonsistenz, Gesamt-SBOM. Erst danach folgen
Freigabe und Pull Request.

Der Gewinn ist Wanduhrzeit bei unveränderter Zurechenbarkeit: Jede Änderung
bleibt einem Child Run zugeordnet, jeder Schritt bleibt attestiert, und der
Warum-Trace umfasst zusätzlich Planversion, Vertragsversionen und
Merge-Entscheidungen. Der Preis sind Integrationskosten — und die Tatsache,
dass sich Parallelität nur lohnt, wenn die Dekomposition trägt (19.10,
Risiken).

## 22.5 Artefakte des Workflows

Der agentische Workflow erzeugt nicht nur Quellcode, sondern eine Reihe strukturierter Artefakte, die den gesamten Entwicklungsprozess nachvollziehbar und wiederverwendbar machen. Dazu gehören Anforderungen, Architekturentscheidungen, Implementierungspläne, Quellcode, Tests sowie Deployment-Artefakte.

Im vorliegenden Beispiel entstehen typischerweise folgende Ergebnisse:

- Anforderungsdokumentation und Traceability Matrix für den Payment Service
- Architekturartefakte wie ADRs und Einträge im Shared Knowledge Store
- Implementierter Code für Domain-, Application- und Infrastructure-Layer
- Automatisch erzeugte Unit- und Integrationstests
- Deployment-Artefakte wie Kubernetes-Manifeste, HPA-Konfiguration und TLS-Ingress-Regeln

Diese Artefakte bilden zusammen die technische und fachliche Grundlage für den produktiven Betrieb des Payment Services. Gleichzeitig ermöglichen sie eine vollständige Nachvollziehbarkeit der Entscheidungen und Änderungen entlang des gesamten Entwicklungslebenszyklus.

## 22.6 Guardrails Pipeline

Ein wesentliches Merkmal des End-to-End-Szenarios ist die konsequente Einbettung von Guardrails in jede Phase des Entwicklungsprozesses. Agentisch erzeugte Änderungen werden nicht ungeprüft übernommen, sondern durchlaufen eine mehrstufige Validierungs- und Governance-Pipeline.

Im Payment-Service-Beispiel umfasst diese Pipeline insbesondere:

- Syntax- und Compile-Prüfungen zur Sicherstellung der technischen Korrektheit
- Style- und Konventionsprüfungen gemäß den in CLAUDE.md definierten Projektstandards
- Security-Scans zur Erkennung potenzieller Schwachstellen oder problematischer Abhängigkeiten
- Domain-Prüfungen zur Absicherung von Bounded Contexts, Glossarregeln und DDD-Konventionen
- Automatisierte Tests mit vorgegebenen Mindestanforderungen an die Testabdeckung
- Confidence-Scoring zur Bewertung unsicherer oder potenziell halluzinierter Änderungen

Erst wenn alle Prüfungen erfolgreich bestanden wurden, kann der Workflow in die nächste Phase übergehen. Dadurch werden für agentisch erzeugten Code definierte Mindestmaßstäbe an Qualität, Sicherheit und Architektur erzwungen — als Risikoreduktion, nicht als Garantie.

## 22.7 Deployment Ergebnis

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
