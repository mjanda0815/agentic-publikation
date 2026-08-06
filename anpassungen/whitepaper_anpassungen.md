# Anpassungsplan für das Whitepaper „Agentic Software Development“

**Zielversion:** Version 2.1 oder 3.0  
**Basis:** Version 2.0 vom 6. August 2026  
**Zweck:** Das Whitepaper soll den aktuellen Stand der SoftwareFabrik korrekt beschreiben und zugleich die geplante Weiterentwicklung zum parallelen Agentenmodell konsistent einordnen.

## 1. Grundentscheidung

Das Whitepaper unterscheidet künftig ausdrücklich drei Ebenen:

### Aktueller Implementierungsstand

Die SoftwareFabrik 0.19.0 ist eine Control Plane mit:

- einem schreibenden Agentenprozess je Run,
- persistiertem Run-Zustand,
- sieben Phasen und 13 Zuständen,
- mehreren parallelen read-only Review-Adaptern,
- Quality Gate,
- Policies und Freigaben,
- Audit-Hashkette,
- Warum-Trace,
- Git-, CI- und Sandbox-Integration,
- zehn Execution-Adaptern und sechs Review-Adaptern.

### Zielarchitektur

Die künftige SoftwareFabrik ergänzt oberhalb des bestehenden Runs eine Workflow-Ebene:

- Parent Workflow
- Task Graph
- mehrere parallele Child Runs
- genau ein schreibender Agent je Workspace
- Branch oder Worktree je Child Run
- Workspace Leases
- versionierte Verträge
- Merge Coordinator
- lokales Gate je Task
- Integration Gate für den Gesamtstand

### Roadmap

1. parallele read-only Analyse,
2. parallele Child Runs für unabhängige Module,
3. vertragsbasierte Parallelisierung,
4. dynamisches Replanning,
5. optional verteilter Worker Pool.

Diese Trennung verhindert, dass geplante Funktionen als bereits implementiert erscheinen.

## 2. Neue zentrale These

Die bisherige Leitthese „Multi-Agent statt Monolith“ wird ersetzt.

> Der entscheidende Schritt ist nicht die maximale Zahl gleichzeitig arbeitender Agenten, sondern eine Control Plane, die nichtdeterministische Agentenarbeit begrenzt, isoliert, koordiniert, prüft und nachweisbar macht.

Ergänzend für die Zielarchitektur:

> Parallelität entsteht zwischen isolierten Tasks und Child Runs. Innerhalb eines Workspace gilt das Single-Writer-Prinzip; unabhängige Reviewer prüfen die Ergebnisse read-only.

Weiterhin gültig:

> Governance ist keine Ergänzung der Agentenarchitektur, sondern ein Teil ihrer Struktur.

## 3. Titel und Untertitel

Der Haupttitel kann bleiben:

# Agentic Software Development

Empfohlener Untertitel:

> Enterprise Architecture with AI Agents – von kontrollierten Einzel-Runs zur parallelen Agentic Software Factory

Alternative:

> Referenzarchitektur, implementierte Control Plane und Roadmap für parallele Agenten-Workflows

## 4. Management Summary neu schreiben

### Empfohlene Fassung

KI-gestützte Coding-Agenten können Anforderungen analysieren, Code verändern, Tests ausführen und Entwicklungsartefakte erzeugen. Ihr Einsatz in Enterprise- und regulierten Umgebungen erfordert jedoch mehr als ein leistungsfähiges Modell: Agentenarbeit muss spezifiziert, begrenzt, isoliert, geprüft, freigegeben und nachträglich rekonstruiert werden können.

Dieses Whitepaper beschreibt eine implementierte Control-Plane-Architektur für diesen Zweck. Die Referenzimplementierung SoftwareFabrik steuert zustandsbehaftete Agentenläufe, projiziert versionierte Regeln in den Workspace, begrenzt Modelle und Budgets, isoliert Ausführungen, bewertet Änderungen durch unabhängige Reviewer und führt relevante Entscheidungen in einem attestierten Audit- und Warum-Trace zusammen.

Der aktuelle Implementierungsstand verwendet genau einen schreibenden Agenten je Run. Mehrere read-only Reviewer prüfen den entstandenen Diff parallel. Diese Architektur vermeidet unkontrollierte Schreibkonkurrenz und bildet die Basis für den nächsten Entwicklungsschritt.

Die geplante Weiterentwicklung ergänzt eine übergeordnete Workflow-Ebene. Ein Feature wird in einen Task Graph zerlegt; voneinander unabhängige Tasks können als isolierte Child Runs parallel ausgeführt werden. Jeder Child Run besitzt einen eigenen Branch oder Worktree und bleibt dem Single-Writer-Prinzip unterworfen. Ein Merge Coordinator und ein abschließendes Integration Gate führen die Ergebnisse kontrolliert zusammen.

Das Whitepaper unterscheidet konsequent zwischen implementiertem Stand, Zielarchitektur und Roadmap. Quantifizierte Produktivitäts- und ROI-Werte werden als Hypothesen beziehungsweise Modellrechnungen behandelt, solange keine kontrollierte Vergleichsmessung vorliegt.

### Neue Kernaussagen

- **Control Plane statt unkontrollierter Autonomie**
- **Single Writer, Multiple Reviewers**
- **Parallelität nach Abhängigkeiten**
- **Governance by Design**
- **Git plus autoritativer Prozesszustand**
- **Regelkreis statt blindem Retry**
- **Souveränität vor Infrastrukturkomplexität**

## 5. Neue Begriffe für das Glossar

### Workflow

Übergeordnete, zustandsbehaftete Ausführungseinheit für ein Feature oder Vorhaben.

### Workflow Task

Abgegrenzte Arbeitseinheit mit Abhängigkeiten, Capability, Schreibbereichen, erwarteten Artefakten und optionalem Child Run.

### Child Run

Ein normaler SoftwareFabrik-Run, der einem Workflow Task zugeordnet ist.

### Single Writer

Innerhalb eines Branches, Worktrees oder Workspace arbeitet genau ein Agent schreibend.

### Workspace Lease

Zeitlich begrenzte Reservierung von Pfaden, Modulen oder exklusiven Ressourcen.

### Contract Version

Versionierter oder gehashter gemeinsamer Vertrag, gegen den mehrere Child Runs arbeiten.

### Merge Coordinator

Komponente zur kontrollierten Rebase-, Merge-, Konflikt- und Revalidierungssteuerung.

### Integration Gate

Quality Gate auf dem zusammengeführten Workflowstand.

### Replanner

Komponente, die den Task Graph auf Basis neuer Informationen versioniert anpasst.

### Claim Verification

Prüfung von Aussagen eines Agenten über seine eigene Arbeit, etwa „alle Tests bestehen“.

## 6. Empfohlene neue Gliederung

## Teil I – Problem, Begriffe und Methodik

1. Warum Coding-Agenten eine Prozessschicht benötigen  
2. Begriffe und Systemgrenzen  
3. Evidenzklassen und Methodik  
4. Architekturprinzipien  

## Teil II – Implementierte Referenzarchitektur

5. Systemkontext der Control Plane  
6. Run Lifecycle und Zustandsmodell  
7. Execution Adapter und Capability Routing  
8. Workspace-, Prozess- und Containerisolation  
9. Knowledge, Artefakte und Kontext  
10. Quality Gates und unabhängige Reviewer  
11. Policies, Freigaben und Human-in-the-Loop  
12. Audit, Attestierung und Warum-Trace  
13. Betrieb, Air Gap und Souveränität  

## Teil III – SoftwareFabrik als Fallstudie

14. Von der Referenzarchitektur zum implementierten System  
15. Bausteinsicht und Domänenmodell  
16. Ausführungsmodell der aktuellen Version  
17. Guardrails und Governance in der Praxis  
18. Betriebserfahrungen, Defekte und Architekturschuld  
19. Grenzen des aktuellen Stands  

## Teil IV – Zielarchitektur für parallele Agenten-Workflows

20. Warum Parallelität auf Workflow-Ebene entsteht  
21. Parent Workflow und Task Graph  
22. Child Runs und Single-Writer-Isolation  
23. Workspace Leases und exklusive Ressourcen  
24. Versionierte Verträge  
25. Merge Coordinator und Integration Gate  
26. Replanning statt Retry  
27. Distributed Worker Pool als optionale Ausbaustufe  

## Teil V – Roadmap und Evaluation

28. Entwicklungsroadmap  
29. Pilotierung  
30. Qualitäts- und Produktivitätsmessung  
31. Threats to Validity  
32. End-to-End-Fallstudie  

## Anhang

- Werkzeugkonfigurationen
- versionsabhängige Tool-Parameter
- Codebeispiele
- vollständige ADRs
- Troubleshooting
- Glossar

## 7. Architekturprinzipien überarbeiten

### AP-1: Controlled Non-Determinism

Nicht das LLM-Ergebnis ist deterministisch. Kontrollierbar sind Zustände, Übergänge, Budgets, Policies, Schreibrechte, Freigaben, Gate-Regeln und Audit-Ereignisse.

### AP-2: Single Writer per Workspace

Ein Workspace besitzt genau einen schreibenden Agenten.

### AP-3: Parallelism by Dependency

Tasks laufen nur parallel, wenn Abhängigkeiten, Verträge und Schreibbereiche dies erlauben.

### AP-4: Independent Verification

Erzeugung und Freigabe werden technisch getrennt.

### AP-5: Policy as Executable Structure

Policies sind versionierter, attestierter Teil des Ausführungsmodells.

### AP-6: Human Authority

Kritische Architektur-, Security-, Policy- und Deploymententscheidungen bleiben menschlich freigabepflichtig.

### AP-7: Fail Closed

Pflichtkontrollen dürfen bei Ausfall keinen Erfolg liefern.

### AP-8: Sovereign by Default

Die Architektur muss lokal und ohne Cloud-Abhängigkeit betreibbar bleiben.

## 8. Kapitel zur Agentenarchitektur ändern

Die Hub-and-Spoke-Topologie wird als logische Rollenverteilung eingeordnet, nicht als bereits realisierte Architektur mit sieben gleichzeitig schreibenden Agenten.

Aktueller Stand:

- ein Agentenprozess je Run,
- Rolle und Capability werden in den Kontext projiziert,
- Plan- und Build-Runs sind getrennt,
- mehrere Reviewer arbeiten parallel,
- der Orchestrator kontrolliert Zustand und Übergänge.

Zielbild:

- Workflow-Orchestrator als Hub,
- Child Runs als ausführende Spokes,
- Kommunikation über versionierte Artefakte und Zustände,
- keine nicht persistierte Agent-zu-Agent-Kommunikation als autoritativer Prozessbestandteil.

## 9. Agent Lifecycle und Execution Model anpassen

Der Run bleibt atomare Ausführungseinheit. Darüber entsteht ein Workflow Lifecycle.

### Workflow-Zustände

- DRAFT
- PLANNING
- WAITING_FOR_PLAN_APPROVAL
- READY
- RUNNING
- INTEGRATING
- VALIDATING
- WAITING_FOR_APPROVAL
- COMPLETED
- FAILED
- CANCELLED

### Task-Zustände

- BLOCKED
- READY
- CLAIMED
- RUNNING
- REVIEWING
- PASSED
- FAILED
- WAITING_FOR_REPLAN
- MERGING
- MERGED
- SUPERSEDED
- CANCELLED

Leitsatz:

> Der Run steuert eine Agentenausführung. Der Workflow steuert mehrere Runs und deren Abhängigkeiten.

## 10. Memory-Kapitel neu fokussieren

Beibehalten:

- ephemeres Kontextfenster
- Run-Kontext
- versionierte Spezifikationsartefakte
- kuratiertes Projektgedächtnis
- Repositoryzustand
- Audit- und Warum-Trace

Ergänzen:

- Workflow Plan
- Contract Registry
- Task-Ergebnisse
- Merge-Findings
- Planversionen
- Replanning-Gründe

Abgrenzung:

> Ein Vektorspeicher ist eine optionale Retrieval-Technik, aber kein autoritativer Nachweis- oder Prozesszustand.

## 11. Guardrails-Kapitel ändern

### Präzisere Aussage

Statt:

> Guardrails stellen sicher, dass KI-generierter Code denselben Qualitäts- und Sicherheitsanforderungen wie manuell entwickelter Code entspricht.

Neu:

> Guardrails erzwingen definierte technische Mindestkriterien, liefern strukturierte Befunde und reduzieren das Risiko ungeprüfter Änderungen. Sie ersetzen weder fachliche Abnahme noch unabhängige Sicherheitsprüfung oder Produktionsbeobachtung.

### Halluzinationserkennung umbenennen

> Claim Verification und Konsistenzprüfung

### Zwei Gate-Ebenen

#### Local Task Gate

- Syntax
- Style
- Security
- Domain
- Tests
- Claim Verification
- lokaler LLM-Review

#### Workflow Integration Gate

- Gesamtbuild
- Regression
- Integration und E2E
- Verträge
- Migrationen
- Gesamtarchitektur
- Gesamt-SBOM
- Merge- und Konfliktprüfung
- Workflow-Policy
- abschließender Integrationsreview

## 12. Security-Kapitel ändern

Klare Trennung:

- **Workspace-Isolation:** schützt vor konkurrierenden Änderungen.
- **Prozessisolation:** begrenzt Umgebung, Prozesse und lokale Ressourcen.
- **Containerisolation:** begrenzt Dateisystem, Netzwerk, CPU, Speicher und Prozesse.
- **Mandantenisolation:** begrenzt Datenzugriffe zwischen Kunden und Projekten.

Neue Bedrohungen:

- doppelte Lease-Vergabe
- veraltete Vertragsgrundlage
- Cross-Task-Write
- Merge-Queue-Races
- Worker-Ausfall mit aktivem Lock
- Cross-Tenant-Zugriff auf Child Runs
- Policy-Bypass zwischen Workflow- und Run-Ebene
- Reviewer-Ausfall im Integration Gate

## 13. Wirtschaftlichkeitskapitel ändern

Neue Überschrift:

> Wirtschaftlichkeitshypothese, Kostenmodell und Messplan

Änderungen:

- keine 70–80-Prozent-Aussage als zentrales Ergebnis,
- Sensitivitätsanalyse statt Einzelwert,
- API-, Abo- und lokale Modellkosten,
- Kosten der Control Plane,
- Replanning- und Integrationskosten,
- klare Trennung zwischen Modellannahme und Messwert.

Messgrößen:

- menschliche aktive Arbeitszeit
- Time to Accepted Merge
- First-Pass-Gate-Rate
- Kosten je akzeptierter Änderung
- Korrekturschleifen
- Merge-Konfliktrate
- Rollbacks
- entkommene Defekte
- Reviewzeit

## 14. Kapitel über die SoftwareFabrik zweiteilen

# Teil A – Implementierter Stand

## 19.1 Systemstatus

> Die folgenden Abschnitte beschreiben den implementierten Stand der SoftwareFabrik 0.19.0. Roadmap-Funktionen werden separat ausgewiesen.

## 19.2 Aktueller Kernablauf

Beibehalten:

1. Erfassen
2. Spezifizieren
3. Ausführen
4. Prüfen
5. Übergeben
6. Belegen

## 19.3 Aktuelles Ausführungsmodell

> Die SoftwareFabrik startet derzeit genau einen schreibenden Agentenprozess je Run. Parallelität findet vor allem in der Bewertung durch mehrere read-only Reviewer statt.

## 19.4 Gründe gegen unkontrollierte parallele Schreiber

- Konfliktkosten
- schwierige Zurechnung
- schwer attestierbare Zwischenzustände
- veraltete Basisstände
- Merge- und CI-Realität

## 19.5 Implementierte Governance

- Policy-Prüfung
- Gate-Modi
- Pflichtregeln
- Audit-Kette
- Warum-Trace
- Segregation of Duties
- fail closed

## 19.6 Aktuelle Grenzen

- keine parallelen Multi-Branch-Runs je Projekt,
- kein dynamischer Workflow-DAG,
- kein Merge Coordinator,
- keine Contract Registry,
- keine kontrollierte Produktivitätsmessung,
- Container-Sandbox nicht zwingend Default,
- bekannte Architekturschuld.

# Teil B – Geplante Weiterentwicklung

## 19.7 Vom Run zum Workflow

> Der bestehende Run wird nicht ersetzt. Er wird zum Child Run eines übergeordneten Workflows.

## 19.8 Zielarchitektur

- Parent Workflow
- Task Graph
- Child Runs
- Single Writer
- Workspace Leases
- Contract Versions
- Integration Branch
- Merge Coordinator
- Integration Gate

## 19.9 Entwicklungsstufen

1. parallele read-only Analyse,
2. parallele Child Runs für unabhängige Module,
3. vertragsbasierte Parallelisierung,
4. dynamisches Replanning,
5. optional verteilter Worker Pool.

## 19.10 Neue Position

> Die Implementierung der Version 0.19.0 hat die ursprüngliche Vorstellung mehrerer gleichzeitig schreibender Rollenagenten zunächst korrigiert. Die nächste Ausbaustufe verwirft diese Praxiserkenntnis nicht, sondern generalisiert sie: Mehrere Agenten dürfen parallel arbeiten, sofern Schreibbereiche, Verträge und Zustände isoliert und durch einen übergeordneten Workflow kontrolliert werden.

## 15. ADRs neu ordnen

### ADR-1 – Superseded

Alt: Multi-Agent Hub-and-Spoke mit sieben spezialisierten Agenten.

### Neuer ADR-1

Hierarchische Orchestrierung mit Parent Workflow und Child Runs.

### Neuer ADR-2

Single Writer per Workspace.

### Neuer ADR-3

Workspace Leases und exklusive Ressourcen.

### Neuer ADR-4

Git als Artefaktzustand, Datenbank als autoritativer Prozesszustand.

### Neuer ADR-5

Unabhängige Reviewer und zweistufiges Quality Gate.

### Neuer ADR-6

Versionierte Verträge vor paralleler Implementierung.

### Neuer ADR-7

Regelkreis und Replanning statt blindem Retry.

### Neuer ADR-8

Single Host als Basis, Distributed Worker Pool als Option.

## 16. Vendor-Neutralität erweitern

Vendor-Neutralität gilt auf drei Ebenen:

1. Execution Adapter hinter Ports.
2. Capability Routing statt harter Modellnamen.
3. Workflow Tasks referenzieren Capabilities, keine Vendoren.

## 17. End-to-End-Kapitel ersetzen

Das neue Beispiel enthält zwei Stufen.

### Stufe A – aktueller Single-Run-Prozess

- Spezifikation
- Run
- Diff
- Reviewer-Findings
- Gate
- Korrekturschleife
- Merge
- Warum-Trace

### Stufe B – geplanter Parallel Workflow

- Plan und Task Graph
- Contract Task
- mehrere Child Runs
- Workspace Leases
- lokale Gates
- Integration Branch
- Merge Coordinator
- Integration Gate
- Workflow-Why-Trace

Roadmap-Teile werden sichtbar als Zielbild oder Prototyp gekennzeichnet.

## 18. Threats to Validity ergänzen

### Interne Validität

- System und Whitepaper stammen vom selben Autor.
- Architekturentscheidungen wurden nicht unabhängig evaluiert.
- Produktivitätsdaten sind nicht kontrolliert gemessen.
- Das Repository ist nicht öffentlich.

### Externe Validität

- bisher eine Referenzimplementierung,
- begrenzte Zahl realer Projekte,
- unklare Übertragbarkeit auf große Monorepos und verteilte Teams.

### Konstruktvalidität

- Lines of Code sind kein Qualitätsmaß,
- Coverage ist kein vollständiger Testwirksamkeitsnachweis,
- Confidence Scores sind keine Wahrscheinlichkeiten,
- bestandene Gates beweisen keine Fehlerfreiheit.

### Zeitliche Validität

- Modelle, Preise und Tool-Parameter ändern sich schnell.
- versionsabhängige Details gehören in einen aktualisierbaren Anhang.

## 19. Formulierungen ersetzen

- **produktionsreife Architektur** → implementierte, produktionsnahe Referenzarchitektur
- **stellt sicher** → erzwingt definierte Mindestkontrollen / reduziert das Risiko
- **Multi-Agent statt Monolith** → kontrollierte Agenten-Workflows statt unkontrollierter Agentennutzung
- **deterministische Ausführung** → begrenzte und nachvollziehbare Ausführung
- **Halluzinationserkennung** → Claim Verification und Konsistenzprüfung
- **Compliance-Profil** → technisches Kontrollprofil mit Bezug zu ausgewählten Anforderungen
- **höhere Qualität** → angestrebte oder in der Fallstudie beobachtete Qualitätsverbesserung

## 20. Diagramme anpassen

### Aktueller Stand

```text
User / Lead
    |
    v
SoftwareFabrik Control Plane
    |
    v
Single Agent Run
    |
    v
Parallel Read-only Reviewers
    |
    v
Quality Gate
    |
    v
Merge / PR / Audit
```

### Zielarchitektur

```text
Parent Workflow
    |
    v
Task Graph
    |
    +----------+----------+
    |          |          |
 Child A    Child B    Child C
    |          |          |
 Local Gate Local Gate Local Gate
    +----------+----------+
               |
         Merge Coordinator
               |
        Integration Gate
               |
           Approval
```

### Zustandsverantwortung

```text
Git:
- Branches
- Commits
- Diffs
- Checkpoints
- Pull Requests

Database:
- Workflow Status
- Task Status
- Policy Version
- Model Resolution
- Approvals
- Gate Results
- Audit Chain
```

Jedes Diagramm erhält eine sichtbare Kennzeichnung:

- **Implemented**
- **In development**
- **Target architecture**
- **Optional**

## 21. Nachweistypen

Für Aussagen zur SoftwareFabrik werden vier Status verwendet:

- `IMPLEMENTED`
- `TESTED`
- `OPERATED`
- `PLANNED`

Beispiele:

> Workspace Leases – PLANNED für Phase 2.

> Mehrere read-only Review-Adapter – IMPLEMENTED und TESTED.

## 22. Reproduzierbares Evidenzpaket

Mögliche öffentliche Artefakte:

- anonymisierter Workflow-Export
- Beispiel eines Child-Run-Auditpfads
- Policy-Dokument
- Gate-Ergebnis
- Warum-Trace
- ArchUnit-Report
- JaCoCo-Zusammenfassung
- SBOM-Auszug
- anonymisierte Merge-Findings
- Skript zur Erhebung der Codekennzahlen
- Roadmap mit Versions- und Statusangaben

## 23. Versionsstrategie

### Whitepaper 2.1

- Management Summary korrigieren
- aktueller Stand versus Zielbild trennen
- Roadmap ergänzen
- Kapitel 19 zweiteilen
- Formulierungen präzisieren
- ADR-Status ergänzen
- noch keine vollständige Umstrukturierung

### Whitepaper 3.0

- neue Gesamtgliederung
- echte Workflow-Fallstudie
- erste implementierte parallele Analyse
- aktualisierte ADRs
- Messkonzept und erste Messdaten
- Evidenzpaket
- Zielarchitektur als teilweise implementierter Stand

## 24. Empfohlene neue Einleitung für das SoftwareFabrik-Kapitel

> Dieses Kapitel unterscheidet zwischen dem implementierten Stand der SoftwareFabrik und ihrer geplanten Weiterentwicklung. Der aktuelle Stand verwendet genau einen schreibenden Agenten je Run und mehrere unabhängige read-only Reviewer. Diese Entscheidung entstand aus der praktischen Erfahrung, dass mehrere gleichzeitig schreibende Agenten Konfliktkosten, unklare Zurechnung und schwer attestierbare Zwischenzustände erzeugen.
>
> Die nächste Ausbaustufe verwirft das parallele Agentenmodell nicht, sondern ordnet es neu: Parallelität wird auf eine übergeordnete Workflow-Ebene verlagert. Ein Workflow zerlegt ein Vorhaben in Tasks; voneinander unabhängige Tasks können als isolierte Child Runs parallel ausgeführt werden. Innerhalb jedes Workspace bleibt das Single-Writer-Prinzip bestehen. Workspace Leases, versionierte Verträge, ein Merge Coordinator und ein abschließendes Integration Gate sichern die Zusammenführung.
>
> Alle folgenden Funktionen werden als implementiert, in Entwicklung oder geplant gekennzeichnet. Die Beschreibung des Zielbilds ist damit keine Behauptung über den aktuellen Produktstand, sondern eine nachvollziehbare Roadmap aus der bestehenden Architektur heraus.

## 25. Schlussformel

> Von einem kontrollierten Agentenlauf zu parallelen Agenten-Workflows – ohne das Single-Writer-, Governance- und Nachweisprinzip aufzugeben.
