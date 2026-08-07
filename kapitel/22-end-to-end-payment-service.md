# 22 End-to-End: Payment Service Implementation

Während die vorherigen Kapitel die Architektur, das Ausführungsmodell und die Governance-Mechanismen eines agentischen Entwicklungssystems beschreiben, zeigt dieses Kapitel den vollständigen Ablauf einer realistischen Feature-Implementierung.

Als Beispiel dient die Entwicklung eines Payment Services für eine E-Commerce-Plattform. Der Service stellt eine REST-API zur Verarbeitung von Zahlungen bereit, publiziert Domain Events über Kafka und wird containerisiert in einer Kubernetes-Umgebung betrieben.

Der Ablauf demonstriert, wie der Orchestrator die Phasen des Software Development Lifecycle koordiniert. Beginnend mit der Anforderungsanalyse werden Architekturentscheidungen getroffen, Implementierungsaufgaben geplant, Code generiert, Tests erstellt und schließlich das Deployment vorbereitet.

Dabei wird sichtbar, wie die zuvor eingeführten Konzepte – insbesondere Task Graph, Workspace Isolation, Guardrails Pipeline und Shared Knowledge Store – in einem zusammenhängenden Workflow zusammenspielen.

> **Aufbau dieses Kapitels (v2.2):** Abschnitt 22.3 zeigt den Ablauf so,
> wie er heute in der Referenzimplementierung stattfindet — ein
> **Single-Run-Prozess** mit einem schreibenden Agenten und parallelen
> Reviewern (Teil A, implementiert). Abschnitt 22.4 zeigt denselben Auftrag
> als **parallelen Workflow** der Zielarchitektur (Teil B, geplant). Die
> ursprüngliche v1.3-Skizze mit sieben gleichzeitig arbeitenden
> Lebenszyklus-Agenten ist damit durch zwei präzise Varianten ersetzt: die,
> die als Einzel-Run läuft, und die, die als paralleler Workflow läuft.

## 22.1 Ausgangssituation

In diesem Szenario wird die Implementierung eines Payment Services für eine E-Commerce-Plattform betrachtet. Der Service stellt eine REST-basierte API zur Verarbeitung von Zahlungen bereit, verwaltet Zahlungszustände innerhalb eines Domain-Driven-Design-Modells und publiziert relevante Domain Events über Apache Kafka, um andere Systeme über erfolgreiche oder fehlgeschlagene Transaktionen zu informieren.

Der Service muss dabei mehrere Anforderungen erfüllen. Dazu gehören eine klare Trennung der Domänenschichten gemäß hexagonaler Architektur, die Einhaltung regulatorischer Anforderungen wie PSD2 sowie eine sichere Integration in bestehende Plattformkomponenten. Darüber hinaus muss der Service containerisiert bereitgestellt und in einer Kubernetes-Umgebung betrieben werden können.

Der Entwicklungsauftrag wird durch eine zentrale Control Plane orchestriert. Der Orchestrator strukturiert das Vorhaben in Spezifikation, Planung, Umsetzung, Validierung, Integration und Übergabe. Ob diese Phasen durch einen einzelnen zustandsbehafteten Run oder durch mehrere koordinierte Child Runs ausgeführt werden, hängt vom Architekturstand und von den Abhängigkeiten des Vorhabens ab.

Während der gesamten Ausführung greift die Ausführung auf einen Shared Knowledge Store zu, in dem Projektdokumentation, Architekturentscheidungen und relevante Kontextinformationen abgelegt sind. Gleichzeitig stellt eine mehrstufige Guardrails-Pipeline sicher, dass generierter Code Qualitäts-, Sicherheits- und Architekturregeln einhält.

## 22.2 Gesamtworkflow

Der Gesamtworkflow lässt sich in Spezifikation, Planung, Umsetzung,
Validierung, Integration und Übergabe gliedern. Wie diese Phasen technisch
ausgeführt werden, hängt vom Architekturstand ab: Die aktuelle
Referenzimplementierung verarbeitet den Auftrag als **einen**
zustandsbehafteten Run mit einem schreibenden Agenten und mehreren
unabhängigen Reviewern. Die Zielarchitektur zerlegt denselben Auftrag in
einen Parent Workflow mit mehreren isolierten Child Runs. Die folgenden
beiden Abschnitte stellen beide Varianten gegenüber.

*(Die beiden Workflow-Abbildungen der v1.3 an dieser Stelle — „End-to-End
Workflow“ und „Interaktion der Systemkomponenten“ — sind in v2.0 mit den
inhaltsgleichen Darstellungen in Kapitel 16 und Kapitel 20 konsolidiert.)*

## 22.3 Teil A — der implementierte Single-Run-Prozess

> **Status: implementiert** (Referenzimplementierung, Stand 0.22.0; vgl.
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
   Diff (zwei LLM-Reviews, Security, Architektur, Claim Verification,
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

> **Status: überwiegend implementiert** (vgl. 19.10 und ADR-5 bis ADR-7).
> Die Workflow-Ebene mit Task-Graph, parallelen Child Runs in getrennten
> Worktrees, Planfreigabe, Synthese, Pfad-Besitzmodell, Merge Queue und
> Integration Gate existiert seit Release 0.22.0 — hinter einem
> standardmäßig deaktivierten Feature-Flag. Über den heutigen Stand hinaus
> greift die Skizze bei den **Contract Versions mit Content-Hash** und der
> **Konfliktklassifikation** vor; das sind die Roadmap-Stufen 3 und 4. Die
> Skizze ist insgesamt Pseudocode: Sie zeigt die Struktur, nicht die
> Aufrufsyntax des Systems.

Der Payment Service besteht aus Teilen, die sich sauber schneiden lassen —
genau der Fall, für den die Workflow-Ebene gedacht ist:

```text
Parent Workflow: "Payment Service"
   │
   ├─ Task 1a  Externe Verträge (blockierend)
   │           OpenAPI-Spezifikation · Domain Events · DTO-Schemas
   │
   ├─ Task 1b  Interne Verträge (blockierend)
   │           Use-Case-Ports · Domain-IDs · gemeinsame Value-Object-
   │           Schnittstellen, als eigenes Contract-Modul
   │           → beide als Contract Version v1 (Content-Hash), attestiert
   │
   ├─ Task 2   Domain-Implementierung        abhängig von 1b
   │           Owned Paths: domain/**        Child Run A, Branch A
   │
   ├─ Task 3   API-/Application-Schicht      abhängig von 1a + 1b,
   │           Owned Paths: adapter/in/**,   nicht von der fertigen
   │                        application/**
   │                                         Implementierung aus Task 2
   │                                         Child Run B, Branch B
   │
   ├─ Task 4   Infrastruktur (Kafka/Outbox)  abhängig von 1a + 1b
   │           Owned Paths: adapter/out/**   (Domain Events aus 1a)
   │                                         Child Run C, Branch C
   │           Exklusiv-Lock: db/migration/**
   │
   ├─ Task 5   Tests                         abhängig von 2–4
   │
   └─ Task 6   Deployment-Artefakte          abhängig von 5
```

Der Ablauf: Die beiden Contract Tasks laufen zuerst und allein — ohne
versionierte Verträge keine parallele Implementierung (AP-3). Die Trennung
in **externe** und **interne** Verträge ist dabei entscheidend und in der
v1.3-Fassung dieses Beispiels noch untergegangen: Eine OpenAPI-Datei und
DTO-Schemas allein genügen nicht, damit die Application-Schicht ohne die
fertige Domänenimplementierung übersetzt. Erst wenn auch die internen
Verträge — Use-Case-Ports, Domain-IDs, gemeinsame Value-Object-
Schnittstellen — als eigenes, stabiles Contract-Modul versioniert
vorliegen, sind Task 2 und Task 3 wirklich unabhängig. Danach starten die
Tasks 2 bis 4 als **Child Runs** mit je eigenem Branch und je genau einem
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

Das angestrebte Ergebnis ist eine kürzere Wanduhrzeit bei unveränderter
Zurechenbarkeit: Jede Änderung bleibt einem Child Run zugeordnet, jeder
Schritt bleibt attestiert, und der Warum-Trace umfasst zusätzlich
Planversion, Vertragsversionen und Merge-Entscheidungen. Ob der
Parallelitätsgewinn die zusätzlichen Integrationskosten übersteigt, muss der
Messplan zeigen (15.6) — Parallelität lohnt sich nur, wenn die Dekomposition
trägt (19.10, Risiken).

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
- Style- und Konventionsprüfungen gemäß den in AGENTS.md beziehungsweise CLAUDE.md definierten Projektstandards
- Security-Scans zur Erkennung potenzieller Schwachstellen oder problematischer Abhängigkeiten
- Domain-Prüfungen zur Absicherung von Bounded Contexts, Glossarregeln und DDD-Konventionen
- Automatisierte Tests mit vorgegebenen Mindestanforderungen an die Testabdeckung
- Confidence-Scoring zur Bewertung unsicherer oder potenziell halluzinierter Änderungen

Wie die Pipeline auf Befunde reagiert, hängt vom Betriebsmodus des Gates ab. Im Blocking-Modus beziehungsweise unter einem strikten Kontrollprofil kann der Workflow erst fortgesetzt werden, wenn alle vorgeschriebenen Prüfungen bestanden wurden. Im Advisory-Modus werden die Befunde protokolliert und angezeigt, ohne den Übergang automatisch zu blockieren; im Modus `off` findet keine Prüfung statt (19.5). Nur der Blocking-Modus erzwingt für agentisch erzeugten Code definierte Mindestmaßstäbe an Qualität, Sicherheit und Architektur — und auch dann als Risikoreduktion, nicht als Garantie.

## 22.7 Deployment-Ergebnis

Das End-to-End-Szenario zeigt, wie Spezifikation, Agentenausführung, unabhängige Prüfung, Governance und Übergabe in einem konsistenten Prozess verbunden werden können. Ein agentisches Entwicklungssystem ist damit mehr als ein Werkzeug zur Codegenerierung: Es ist die Prozessschicht, die diese Schritte zusammenhält.

Im Payment-Service-Beispiel wird deutlich, dass insbesondere folgende Vorteile erzielt werden können:

- klare Trennung zwischen erzeugender und prüfender Verantwortung
- nachvollziehbare Entwicklungsabläufe mit reproduzierbarem Prüfprozess
- frühzeitige Validierung von Architektur-, Sicherheits- und Qualitätsanforderungen
- bessere Wiederverwendbarkeit von Wissen durch Shared Knowledge Store und ADRs
- potenziell kürzere Durchlaufzeit bei kontrollierter Qualitätssicherung; der tatsächliche Vorteil gegenüber einem Einzel-Run ist Gegenstand des Messplans (15.6)

Damit wird das agentische Entwicklungssystem zu einer belastbaren Architektur für die Umsetzung komplexer Features in Enterprise-Umgebungen. Das Beispiel des Payment Services verdeutlicht, wie die in den vorangegangenen Kapiteln beschriebenen Konzepte in der Praxis zusammenspielen und gemeinsam einen produktionsnahen Entwicklungsprozess ermöglichen.

> **Praxis-Check SoftwareFabrik (bestätigt):** Der hier skizzierte
> End-to-End-Pfad ist dort reproduzierbar produktisiert: Wizard
> (18 Templates inklusive Repo-Import) → versionierte
> Spezifikations-Artefakte → Run → Quality Gate → Merge bzw. Pull Request
> (19.1).
