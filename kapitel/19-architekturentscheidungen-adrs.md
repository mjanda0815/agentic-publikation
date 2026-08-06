# 19 Architekturentscheidungen (ADRs)

Die folgenden Architecture Decision Records dokumentieren die wichtigsten Designentscheidungen des Agentensystems. Jeder ADR folgt dem Lightweight ADR-Format nach Michael Nygard: Kontext, Entscheidung, Konsequenzen.

## ADR-1: Multi-Agent vs. Single-Agent Architektur

### Motivation / Kontext

KI-basierte Entwicklungssysteme lassen sich grundsätzlich in zwei Architekturen implementieren:

Single-Agent (Monolithisch): Ein einzelner LLM-Aufruf mit einem umfangreichen System-Prompt übernimmt alle Aufgaben – von der Anforderungsanalyse über die Implementierung bis zum Deployment. Der gesamte Kontext (Architekturregeln, Code-Konventionen, Domain-Wissen, Tool-Zugriffe) wird in einem einzigen Prompt-Kontext gehalten.

Multi-Agent (Spezialisiert): Mehrere Agenten mit jeweils fokussiertem Auftrag, eigenem System-Prompt, eingeschränkten Tool-Zugriffen und abgegrenztem Kontextfenster arbeiten koordiniert an einer Aufgabe. Ein Orchestrator verteilt Aufgaben und aggregiert Ergebnisse.

Die Entscheidung ist architekturprägend, weil sie beeinflusst: Kontextfenster-Nutzung (und damit Antwortqualität), Token-Kosten, Parallelisierbarkeit, Fehler-Isolation, Modellwahl pro Aufgabe und Erweiterbarkeit um neue Fähigkeiten.

Aus der Praxis mit Claude Code zeigt sich: Ein monolithischer Agent mit >50.000 Token System-Prompt degradiert messbar in der Ausgabequalität, weil das Modell zwischen Architekturregeln, Test-Konventionen, Deployment-Wissen und Domain-Constraints priorisieren muss. Gleichzeitig bleiben einfache Aufgaben (Linting, Formatierung) unnötig teuer, wenn sie mit dem leistungsstärksten Modell (Opus) ausgeführt werden.

### Entscheidung

Wir verwenden eine Multi-Agent-Architektur mit Hub-and-Spoke-Topologie und zentralem Orchestrator.

#### Agenten-Katalog

| Agent | Verantwortung | Modell (Empfehlung) | Tool-Zugriffe | Kontext-Fokus |
| --- | --- | --- | --- | --- |
| Orchestrator | Task-Dekomposition, Agent-Zuweisung, Ergebnis-Aggregation, Conflict Resolution | Opus | Alle Agenten, Shared Knowledge Store, Git | Gesamtarchitektur, Task-Graph, Agent-Status |
| Architecture Agent | ADR-Erstellung, Architektur-Validierung, Bounded-Context-Prüfung | Opus | Dateisystem (read), Shared Knowledge Store | ADRs, Architekturregeln, DDD-Modell |
| Planning Agent | Task-Dekomposition, Abhängigkeitsanalyse, Schätzung | Sonnet | Shared Knowledge Store, Issue Tracker | Anforderungen, Task-Graph, Velocity-Daten |
| Requirements Agent | Anforderungsanalyse, Akzeptanzkriterien, User-Story-Verfeinerung | Sonnet | Shared Knowledge Store, Dokumentation | Fachdomäne, bestehende Requirements |
| Development Agent | Code-Generierung, Refactoring, Implementierung | Sonnet / Opus (je nach Komplexität) | Dateisystem (read/write), Build-Tools, Terminal | Service-Code, Dependencies, API-Contracts |
| Testing Agent | Testgenerierung, Coverage-Analyse, Mutation Testing | Sonnet | Dateisystem, Test-Runner, Coverage-Tools | Test-Code, Fixtures, Coverage-Reports |
| Review Agent | Code-Review, Architektur-Compliance, Security-Check | Opus | Dateisystem (read), Guardrails-Pipeline | Diff, ADRs, Security-Policies, Style-Guides |
| Deployment Agent | CI/CD-Konfiguration, Infrastructure as Code, Rollout-Strategien | Sonnet / Haiku | Dateisystem, Docker, K8s-Config | Deployment-Manifeste, Helm Charts, Pipelines |

#### Hub-and-Spoke-Topologie

<!-- TODO(abbildung): Abbildung 16: Hub and Spoke - Topologie -->

#### Kommunikationsmodell

Agenten kommunizieren ausschließlich über den Orchestrator und den Shared Knowledge Store – keine direkte Agent-zu-Agent-Kommunikation. Das verhindert unkoordinierte Seiteneffekte und stellt sicher, dass der Orchestrator jederzeit den Gesamtzustand kennt.

Ablauf einer typischen Feature-Implementierung:

1. Orchestrator erhält Feature-Request, ruft Requirements Agent auf
2. Requirements Agent schreibt Anforderungsdokument in Shared Knowledge Store
3. Orchestrator ruft Architecture Agent auf → prüft Architektur-Impact, erstellt/aktualisiert ADR
4. Orchestrator ruft Planning Agent auf → dekomponiert in Tasks mit Abhängigkeiten
5. Orchestrator verteilt unabhängige Tasks parallel an Development Agents (je eigener Worktree)
6. Nach Implementierung: Testing Agent generiert und führt Tests aus
7. Review Agent prüft Diff gegen ADRs, Conventions, Security-Policies
8. Bei Bestehen: Deployment Agent erstellt/aktualisiert Deployment-Konfiguration
9. Orchestrator führt Merge durch (nach bestandener Guardrails-Pipeline)

#### Modellwahl-Strategie

| Task-Komplexität | Modell | Beispiele | Token-Kosten (relativ) |
| --- | --- | --- | --- |
| Hoch (Architekturentscheidungen, komplexe Geschäftslogik, Security-Review) | Opus | Architecture Agent, Review Agent, komplexe Dev-Tasks | 1x (Referenz) |
| Mittel (Standard-Implementierung, Testgenerierung, Planung) | Sonnet | Development Agent, Testing Agent, Planning Agent | ~0,2x |
| Niedrig (Formatierung, einfache Konfiguration, Boilerplate) | Haiku | Deployment Agent (simple Configs), Dokumentations-Updates | ~0,04x |

Diese Differenzierung senkt die Token-Kosten um 60–70 % gegenüber einer reinen Opus-Nutzung bei vergleichbarer Ergebnisqualität.

### Begründung

Warum Multi-Agent statt Single-Agent?

Kontextfenster-Effizienz: Ein spezialisierter Agent benötigt nur den für seine Aufgabe relevanten Kontext. Der Architecture Agent braucht keine Test-Fixtures, der Testing Agent keine Deployment-Manifeste. Dadurch bleibt mehr Kontextfenster für die eigentliche Aufgabe – die Antwortqualität steigt messbar.

Modellwahl pro Task: Nicht jede Aufgabe rechtfertigt die Kosten des leistungsstärksten Modells. Formatierung mit Opus ist Verschwendung; eine Architekturentscheidung mit Haiku ist riskant. Multi-Agent ermöglicht die richtige Modellwahl pro Aufgabe.

Parallelisierung: Unabhängige Tasks (z. B. drei Services eines Features) können gleichzeitig von drei Development Agents bearbeitet werden. Ein Single-Agent arbeitet sequenziell.

Fehler-Isolation: Wenn der Testing Agent halluziniert, ist nur die Test-Generierung betroffen – nicht die bereits fertige Implementierung. Beim Single-Agent kann eine Halluzination den gesamten Kontext korrumpieren.

Erweiterbarkeit: Ein neuer Agent (z. B. Documentation Agent, Performance Agent) wird hinzugefügt, ohne bestehende Agenten zu ändern. Beim Single-Agent wächst der System-Prompt mit jeder neuen Fähigkeit.

Warum Hub-and-Spoke statt Mesh?

In einer Mesh-Topologie kommuniziert jeder Agent direkt mit jedem anderen. Bei n Agenten sind das n×(n-1)/2 Kommunikationskanäle. Hub-and-Spoke hat nur n Kanäle (jeder Agent zum Orchestrator). Das reduziert Komplexität, verhindert zirkuläre Abhängigkeiten und gibt dem Orchestrator die vollständige Kontrolle über die Ausführungsreihenfolge.

Warum keine Agent-zu-Agent-Kommunikation?

Direkte Kommunikation zwischen Agenten erzeugt Koordinationsprobleme: Wer hat Vorrang? Was passiert bei widersprüchlichen Anweisungen? Der Shared Knowledge Store als einzige Kommunikationsschicht stellt sicher, dass jeder Agent auf demselben, versionierten Wissensstand arbeitet.

### Konsequenzen

#### Positive Konsequenzen

- Spezialisierung und fokussierte System-Prompts: höhere Antwortqualität pro Agent durch kleineren, relevanten Kontext
- Kostenoptimierung durch Modellwahl pro Task: 60–70 % niedrigere Token-Kosten gegenüber reiner Opus-Nutzung
- Parallelisierung unabhängiger Tasks: Reduktion der Wall-Clock-Time um Faktor 2–4 bei Multi-Service-Features
- Fehler-Isolation: Halluzination eines Agenten beeinträchtigt nicht die Ergebnisse anderer Agenten
- Erweiterbarkeit: Neue Agenten können hinzugefügt werden, ohne bestehende zu ändern (Open/Closed Principle)
- Nachvollziehbarkeit: Jeder Schritt ist einem spezifischen Agenten zuordenbar (Audit-Trail)
- Wiederverwendbarkeit: Agenten können über Projekte hinweg eingesetzt werden (z. B. derselbe Testing Agent für verschiedene Repositories)

#### Negative Konsequenzen

- Höhere Orchestrierungskomplexität: Der Orchestrator muss Task-Dekomposition, Abhängigkeitsanalyse und Conflict Resolution beherrschen
- Token-Overhead: Jeder Agent muss seinen Kontext neu aufbauen (System-Prompt, relevante Knowledge-Store-Einträge) – ca. 10–20 % Overhead gegenüber einem Single-Agent mit persistentem Kontext
- Debugging über Agent-Grenzen hinweg ist schwieriger: Wenn ein Feature nicht funktioniert, muss ermittelt werden, welcher Agent den Fehler verursacht hat
- Latenz: Inter-Agent-Kommunikation über Orchestrator und Shared Knowledge Store addiert Latenz (Sekunden pro Hop)
- Initialer Setup-Aufwand: System-Prompts, Tool-Konfigurationen und Guardrails für sieben Agenten statt für einen

## ADR-2: Workspace Isolation via Git Worktrees

### Motivation / Kontext

Die Multi-Agent-Architektur (ADR-1) ermöglicht die parallele Ausführung mehrerer Agenten – z. B. drei Development Agents, die gleichzeitig drei unabhängige Services eines Features implementieren. Diese Parallelisierung ist einer der Hauptvorteile der Architektur, setzt aber eine strikte Isolation der Arbeitsbereiche voraus.

Ohne Isolation drohen:

Race Conditions: Zwei Agenten ändern dieselbe Datei gleichzeitig → inkonsistenter Zustand, nicht kompilierbarer Code

Halbfertige Artefakte: Agent A sieht den unfertigen Zwischenstand von Agent B → generiert Code gegen instabile Interfaces

Build-Instabilität: Ein Agent startet einen Build, während ein anderer gerade Dateien schreibt → sporadische Build-Fehler

Nicht-reproduzierbare Ergebnisse: Die Reihenfolge, in der Agenten ihre Änderungen schreiben, beeinflusst das Endergebnis

Git bietet mit Worktrees einen Mechanismus, der genau dieses Problem löst: Mehrere parallele Checkouts desselben Repositories, jeder in einem eigenen Verzeichnis mit eigenem Branch, die sich eine gemeinsame .git-Datenbank teilen.

### Entscheidung

Jeder parallellaufende Agent arbeitet in einem eigenen Git Worktree. Änderungen werden erst nach erfolgreicher Validierung (Guardrails-Pipeline) in den Haupt-Branch gemergt.

#### Worktree-Lebenszyklus

<!-- TODO(abbildung): Worktree-Lebenszyklus (Diagramm ohne Nummerierung im Abbildungsverzeichnis des Originals, S. 54) -->

#### Namenskonventionen

| Element | Konvention | Beispiel |
| --- | --- | --- |
| Worktree-Pfad | /tmp/agent-{agent-type}-{task-id} | /tmp/agent-dev-FEAT-42-payment-service |
| Branch-Name | agent/{agent-type}/{task-id} | agent/dev/FEAT-42-payment-service |
| Commit-Message | Conventional Commits + Task-ID | feat(FEAT-42): implement PaymentService with DDD |

#### Merge-Strategie

| Szenario | Strategie |
| --- | --- |
| Unabhängige Dateien (verschiedene Services) | Parallele Merges – keine Konflikte zu erwarten |
| Überlappende Dateien (z. B. shared config, API contracts) | Sequenzieller Merge in Orchestrator-definierter Reihenfolge. Zweiter Agent rebased auf aktualisierten main. |
| Merge-Konflikt | Orchestrator erkennt Konflikt, weist einem Agenten (typischerweise Review Agent) die Konfliktlösung zu. Bei nicht-trivialen Konflikten: Eskalation an menschlichen Entwickler. |

#### Ressourcen-Management

Disk-Budget: Worktrees teilen sich die .git-Datenbank → nur Working Directory wird dupliziert. Bei einem typischen Spring-Boot-Projekt: ~50–200 MB pro Worktree (ohne target/node_modules, die per .gitignore ausgeschlossen sind).

Lebensdauer: Worktrees haben eine maximale TTL (konfigurierbar, Default: 30 Minuten). Nach Ablauf wird der Worktree zwangsweise entfernt und der Task als fehlgeschlagen markiert.

Concurrency-Limit: Maximal n parallele Worktrees pro Repository (konfigurierbar, Default: 5). Verhindert Disk-Exhaustion und zu hohe Build-Last.

### Begründung

Warum Git Worktrees statt Feature-Branches mit separatem Clone?

Ein vollständiger git clone dupliziert die gesamte Git-History und das Working Directory. Ein Worktree teilt sich die .git-Datenbank mit dem Haupt-Checkout – deutlich schneller zu erstellen (Millisekunden statt Sekunden) und speichereffizienter. Die Isolation ist identisch: Jeder Worktree hat sein eigenes Working Directory und seinen eigenen Branch.

Warum nicht Docker-Container pro Agent?

Docker-Container bieten noch stärkere Isolation (eigenes Dateisystem, eigene Prozesse), aber der Overhead ist erheblich: Image-Pull, Container-Start, Volume-Mounts für den Code, Build-Tool-Installation. Worktrees sind leichtgewichtig (kein OS-Level-Overhead) und direkt in die Git-basierte Orchestrierung (ADR-4) integriert. Docker-Container können bei Bedarf zusätzlich eingesetzt werden (z. B. für Build-Isolation), sind aber kein Ersatz für die Workspace-Isolation.

Warum atomare Merges?

Ein Agent committet und merged entweder alles oder nichts. Partial Merges (nur manche Dateien eines Agents) erzeugen inkonsistente Zustände: ein Service ohne seine Tests, ein Interface ohne seine Implementierung. Die Guardrails-Pipeline (ADR-3) validiert den gesamten Branch – wenn sie besteht, ist der Branch als Ganzes mergebar.

### Konsequenzen

#### Positive Konsequenzen

- Vollständige Isolation: Kein Agent sieht halbfertige Änderungen eines anderen Agenten
- Atomare Merges: Die Guardrails-Pipeline validiert den gesamten Branch, nicht einzelne Commits – Alles-oder-Nichts-Semantik
- Einfaches Rollback: Worktree löschen und Branch entfernen = Änderungen vollständig rückgängig, keine Spuren im Haupt-Branch
- Parallelisierung: Mehrere Agenten arbeiten gleichzeitig ohne Koordination auf Dateisystemebene
- Deterministische Builds: Jeder Agent baut gegen einen definierten Stand (den main-Branch zum Zeitpunkt der Worktree-Erstellung)
- Audit-Trail: Jeder Agent-Branch zeigt exakt, was der Agent geändert hat (sauberer Diff gegen main)

#### Negative Konsequenzen

- Disk-Overhead: Jeder Worktree dupliziert das Working Directory (~50–200 MB pro Spring-Boot-Projekt). Mitigation: Concurrency-Limit und TTL.
- Merge-Konflikte bei überlappenden Dateien: Wenn zwei Agenten dieselbe Datei ändern, entsteht ein Konflikt. Mitigation: Intelligentes Task-Routing im Orchestrator (überlappende Tasks sequenziell zuweisen) und automatische Rebase-Strategie.
- Veralteter Basis-Stand: Ein lang laufender Agent arbeitet auf einem zunehmend veralteten main. Mitigation: TTL und periodischer Rebase für langlebige Worktrees.
- Build-Redundanz: Jeder Worktree führt eigene Builds aus. Mitigation: Shared Build-Cache (Maven Local Repository, Gradle Build Cache, NX Cache) über alle Worktrees hinweg.

## ADR-3: Guardrail Pipeline als Pflicht-Gate

### Motivation / Kontext

Large Language Models generieren Code, der syntaktisch korrekt aussieht und funktional plausibel wirkt – aber in Produktionsumgebungen gefährlich sein kann. Die Risiken sind vielfältig:

- Halluzinationen: Das Modell ruft APIs auf, die nicht existieren, oder verwendet Bibliotheksversionen mit inkompatiblen Signaturen
- Security-Lücken: Generierter Code enthält SQL Injection, unsichere Deserialisierung, hardcodierte Credentials oder fehlende Input-Validierung
- Architektur-Verstöße: Ein Agent greift direkt auf die Datenbank eines anderen Bounded Context zu, statt über die definierte Schnittstelle zu kommunizieren
- Style-Inkonsistenz: Generierter Code weicht von den Projekt-Konventionen ab (Naming, Package-Struktur, Logging-Pattern)
- Unzureichende Tests: Agent generiert Implementierung ohne Tests, oder Tests, die trivial sind (keine Assertions, nur Happy Path)
- Confidence-Probleme: Das Modell ist sich unsicher, generiert aber trotzdem Code, anstatt zu eskalieren

Ohne eine automatische, systematische Validierung ist jeder generierte Code ein Risiko. Die Guardrails-Pipeline ist die zentrale Qualitätssicherungsmaßnahme der gesamten Agenten-Architektur. Sie stellt sicher, dass kein Code – unabhängig davon, welcher Agent ihn generiert hat – ohne Validierung in die Codebasis gelangt.

### Entscheidung

Jede Codeänderung eines Agenten durchläuft eine sechsstufige Validierungs-Pipeline. Alle Stufen müssen bestanden werden, bevor ein Merge möglich ist. Bei Fehlschlag erhält der Agent strukturiertes Feedback und kann korrigieren (max. n Retries, danach Eskalation).

#### Pipeline-Stufen

<!-- TODO(abbildung): Abbildung 17: Pipeline Stufen -->

Stufe 1: Syntax-Validierung

| Aspekt | Details |
| --- | --- |
| Prüfung | Kompilierung (Backend: mvn compile, Frontend: ng build), Dependency Resolution |
| Typische Fehler | Nicht-existierende Imports, falsche Methodensignaturen, fehlende Dependencies in pom.xml/package.json |
| Feedback an Agent | Compiler-Fehlermeldungen als strukturierter Text |
| Ausführungszeit | 5–15 Sekunden |

Stufe 2: Style-Validierung

| Aspekt | Details |
| --- | --- |
| Prüfung | Code-Style (Checkstyle, ESLint), Formatierung (Prettier, google-java-format), Naming Conventions |
| Typische Fehler | Falsche Package-Struktur, inkonsistente Naming-Patterns, fehlende Javadoc auf public APIs |
| Feedback an Agent | Regel-ID + betroffene Zeile + erwartetes Pattern |
| Ausführungszeit | 3–8 Sekunden |

Stufe 3: Security-Validierung

| Aspekt | Details |
| --- | --- |
| Prüfung | SAST (SpotBugs + Find-Security-Bugs), Dependency-Vulnerabilities (OWASP Dependency-Check), Custom Rules (Semgrep), Secret Detection (Gitleaks) |
| Typische Fehler | SQL Injection, unsichere Deserialisierung, hardcodierte Credentials, Verwendung vulnerabler Dependencies |
| Feedback an Agent | CWE-ID, Schweregrad, betroffene Codezeile, Remediation-Hinweis |
| Ausführungszeit | 10–20 Sekunden |
| Verhalten bei Findings | Critical/High → Pipeline bricht ab. Medium → Warnung, Agent entscheidet. Low → informativ. |

Stufe 4: Domain-Validierung

| Aspekt | Details |
| --- | --- |
| Prüfung | Bounded-Context-Grenzen (kein direkter DB-Zugriff über Kontextgrenzen), Layer-Abhängigkeiten (Domain darf nicht von Infrastructure abhängen), Naming (Aggregate Roots, Value Objects, Repositories) |
| Tool | ArchUnit mit projektspezifischem Regelset |
| Typische Fehler | Service A importiert Repository von Service B, Domain-Entity hat Spring-Annotation, Controller enthält Business-Logik |
| Feedback an Agent | Verletzte Regel + betroffene Klasse + erlaubte Abhängigkeiten laut ADR |
| Ausführungszeit | 5–10 Sekunden |

Stufe 5: Test-Validierung

| Aspekt | Details |
| --- | --- |
| Prüfung | Alle bestehenden Tests bestehen (Regression), neue Tests für neuen Code vorhanden, Coverage ≥ Schwellwert |
| Tools | JUnit 5 + Vitest (Execution), JaCoCo + Istanbul (Coverage) |
| Schwellwerte | Line Coverage ≥ 80 % (für den geänderten Code, nicht das Gesamtprojekt) |
| Typische Fehler | Agent generiert Code ohne Tests, Tests bestehen, prüfen aber nichts (leere Assertions), bestehende Tests brechen |
| Feedback an Agent | Fehlgeschlagene Tests mit Stack-Trace, Coverage-Delta mit unkovered Lines |
| Ausführungszeit | 10–30 Sekunden (abhängig von Testumfang) |

Stufe 6: Confidence Scoring

| Aspekt | Details |
| --- | --- |
| Prüfung | LLM-basierte Bewertung des gesamten Changesets: Kohärenz (passt der Code zum bestehenden Projekt?), Vollständigkeit (fehlen offensichtliche Teile?), Pattern-Konsistenz (werden etablierte Patterns korrekt angewendet?), Risiko (gibt es subtile Probleme, die die vorherigen Stufen nicht erkennen?) |
| Modell | Sonnet (kosteneffizient für Scoring) oder Opus (für kritische Changesets) |
| Scoring | 0–100 Score, konfigurierbar Threshold (Default: 70) |
| Feedback an Agent | Score + Begründung + spezifische Bedenken |
| Ausführungszeit | 5–15 Sekunden |
| Sonderregel | Score < 50 → automatische Eskalation an menschlichen Reviewer, unabhängig von Retry-Budget |

#### Retry-Mechanismus

| Parameter | Wert | Begründung |
| --- | --- | --- |
| Max Retries | 3 | Erfahrungswert: Nach 3 Versuchen ist ein Feedback-Loop ausgeschöpft. Weitere Versuche verbrennen nur Token. |
| Feedback-Format | Strukturierter JSON mit Stufe, Regel-ID, betroffener Datei/Zeile, Fehlerbeschreibung, Lösungshinweis | Agent kann Feedback direkt als Kontext in den nächsten Versuch einspeisen |
| Eskalation nach Max Retries | Task wird als „blocked" markiert, menschlicher Reviewer wird benachrichtigt | Verhindert Endlosschleifen und unkontrollierten Token-Verbrauch |

### Begründung

Warum sechs Stufen statt einer monolithischen Prüfung?

Stufenweise Validierung ermöglicht Early Exit: Wenn der Code nicht kompiliert (Stufe 1), ist es sinnlos, Security-Scans oder Tests auszuführen. Jede Stufe gibt spezifisches, actionable Feedback – „Zeile 42: SQL Injection (CWE-89)" ist hilfreicher als „Pipeline failed".

Warum Confidence Scoring als letzte Stufe?

Die ersten fünf Stufen prüfen objektive, regelbasierte Kriterien. Stufe 6 fängt die subtilen Probleme ab, die regelbasierte Tools nicht erkennen: Code, der zwar kompiliert und alle Tests besteht, aber konzeptionell falsch ist (z. B. ein Event-Handler, der synchron statt asynchron implementiert ist). Das LLM prüft, ob das Gesamtbild stimmig ist.

Warum kein menschlicher Review als Pflicht?

Die Guardrails-Pipeline ersetzt den menschlichen Review nicht, sondern reduziert seinen Aufwand. In der Praxis werden 70–80 % der Agenten-Ausgaben ohne Korrekturbedarf die Pipeline bestehen. Menschliche Reviewer können sich auf die verbleibenden 20–30 % konzentrieren und auf die Confidence-Score-Begründungen als Entscheidungshilfe zugreifen.

### Konsequenzen

#### Positive Konsequenzen

- Systematische, reproduzierbare Qualitätssicherung für jeden generierten Code-Artefakt – unabhängig davon, welcher Agent oder welches Modell den Code generiert hat
- Früherkennung von LLM-Halluzinationen (nicht-existierende APIs, falsche Signaturen) in Stufe 1 (Syntax), bevor aufwendigere Prüfungen starten
- Compliance-Nachweis für Audit-Anforderungen: Jede Pipeline-Ausführung ist protokolliert und nachvollziehbar
- Strukturiertes Feedback ermöglicht Agenten, gezielt zu korrigieren – kein blindes Raten
- Defense in Depth: Sechs unabhängige Prüfebenen – ein Fehler, der Stufe 3 passiert, wird mit hoher Wahrscheinlichkeit in Stufe 4, 5 oder 6 erkannt
- Confidence Scoring fängt subtile, kontextabhängige Probleme ab, die regelbasierte Tools prinzipiell nicht erkennen können

#### Negative Konsequenzen

- Zusätzliche Laufzeit: 30–90 Sekunden pro Pipeline-Durchlauf (abhängig von Projektgröße und Testumfang). Mitigation: Stufenweises Early Exit und Parallelisierung der Stufen 2–4.
- False Positives (besonders in Stufen 3 und 6) können Agenten-Workflows verlangsamen und Token verschwenden. Mitigation: Regelmäßige Kalibrierung der Regeln und Schwellwerte, Suppress-Mechanismus für bekannte False Positives.
- Initiale Konfiguration der Pipeline erfordert Aufwand: ArchUnit-Regeln für Domain-Validierung, Semgrep-Rules für projektspezifische Security-Patterns, Confidence-Score-Kalibrierung.
- Confidence Scoring (Stufe 6) ist selbst LLM-basiert und damit nicht deterministisch: Derselbe Code kann bei wiederholter Prüfung unterschiedliche Scores erhalten. Mitigation: Score-Schwellwert mit Puffer (70 statt 50).

## ADR-4: Git-basierte Orchestrierung

### Motivation / Kontext

Die Multi-Agent-Architektur (ADR-1) benötigt einen Orchestrierungsmechanismus, der den Workflow steuert: Welcher Agent arbeitet wann an welcher Aufgabe? Wo werden Zwischenergebnisse abgelegt? Wie wird der Fortschritt nachvollziehbar?

Denkbare Orchestrierungsmechanismen:

| Option | Beschreibung | Zusätzliche Infrastruktur |
| --- | --- | --- |
| Message Queue (RabbitMQ, Kafka) | Events zwischen Agenten, async Verarbeitung | Broker-Infrastruktur, Monitoring |
| Workflow-Engine (Temporal, Camunda) | Formale Workflow-Definition, State Management | Engine-Infrastruktur, Deployment |
| Datenbank-basiert | Shared State in DB, Polling-Mechanismus | Datenbank, Schema-Management |
| Git-basiert | Branches = States, Commits = Checkpoints, PRs = Gates, Repository = Knowledge Store | Keine – Git ist bereits vorhanden |

In einem Agenten-System, das Code generiert, ist Git bereits der zentrale Artefakt-Speicher. Jeder Agent liest und schreibt Code im Repository. Der Orchestrierungsmechanismus sollte diesen bestehenden Artefakt-Speicher nutzen, statt einen zweiten, parallelen State-Management-Layer einzuführen.

### Entscheidung

Git dient als primärer Orchestrierungsmechanismus.

Branches repräsentieren Workflow-States, Commits sind Checkpoints, Pull Requests (bzw. Merge Requests) sind Review- und Validation-Gates, und ein dediziertes Verzeichnis im Repository (docs/knowledge/) dient als Shared Knowledge Store.

#### Git als State Machine

<!-- TODO(abbildung): Abbildung 18: Git als State-Machine -->

#### Shared Knowledge Store

Das Verzeichnis docs/knowledge/ im Repository dient als gemeinsamer Wissensspeicher für alle Agenten. Es ist versioniert, durchsuchbar und über Git-History nachvollziehbar.

Verzeichnisstruktur

```
docs/knowledge/
├── architecture/
│   ├── adrs/                                              # Architecture Decision Records
│   │   ├── ADR-001-*.md
│   │   └── ...
│   ├── bounded-contexts.md                                # DDD Bounded Context Map
│   ├── api-contracts/                                     # OpenAPI-Specs, AsyncAPI
│   └── patterns.md                                        # Erlaubte/verbotene Patterns
├── domain/
│   ├── glossary.md                                        # Ubiquitous Language
│   ├── event-catalog.md                                   # Domain Events
│   └── aggregates.md                                      # Aggregate-Beschreibungen
├── conventions/
│   ├── coding-standards.md                                # Code-Konventionen
│   ├── testing-standards.md                               # Test-Konventionen
│   └── commit-conventions.md                              # Commit-Message-Format
├── tasks/
│   ├── active/                                            # Laufende Tasks (JSON)
│   │   ├── FEAT-42-task-1.json
│   │   └── FEAT-42-task-2.json
│   ├── completed/                                         # Abgeschlossene Tasks
│   └── blocked/                                           # Blockierte Tasks
└── memory/
    ├── decisions.md                                       # Entscheidungen im laufenden Feature
    ├── lessons-learned.md                                 # Aus Fehlern gelernt (Retry-Feedback)
    └── context-cache.md                                   # Wiederverwendbarer Kontext
```

Task-Datei-Format

```json
{
    "id": "FEAT-42-task-1",
    "feature": "FEAT-42-payment",
    "title": "Implement PaymentAggregate with DDD",
    "agent": "development",
    "model": "sonnet",
    "status": "in_progress",
    "worktree": "/tmp/agent-dev-FEAT-42-payment-domain",
    "branch": "agent/dev/FEAT-42-payment-domain",
    "dependencies": [],
    "created_at": "2025-03-04T10:00:00Z",
    "started_at": "2025-03-04T10:00:05Z",
    "guardrails_attempts": 0,
    "max_retries": 3,
    "context_files": [
      "docs/knowledge/architecture/adrs/ADR-001-ddd.md",
      "docs/knowledge/domain/aggregates.md",
      "docs/knowledge/conventions/coding-standards.md"
    ]
}
```

<!-- TODO(verify): Die Zeitstempel im Task-Datei-Beispiel (S. 64) lauten "2025-03-04T...", während das Whitepaper selbst auf Version 1.3, März 2026 datiert ist. Möglicher Zahlen-/Datumsfehler im Original – wörtlich übernommen, nicht korrigiert. Siehe TODO.md. -->

Workflow-Events als Git-Operationen

| Workflow-Event | Git-Operation | Nachvollziehbarkeit |
| --- | --- | --- |
| Feature gestartet | git checkout -b feature/{id} | Branch-Erstellung in Git-Log |
| Task an Agent zugewiesen | Task-Datei in docs/knowledge/tasks/active/ committed | Commit-History |
| Agent startet Arbeit | git worktree add + Branch-Erstellung | Worktree + Branch in Git |
| Agent erstellt Checkpoint | git commit im Agent-Branch | Commit mit Message |
| Agent ist fertig | Task-Datei → completed/, PR gegen Feature-Branch | PR-History |
| Guardrails bestanden | Merge des Agent-Branch in Feature-Branch | Merge-Commit |
| Feature abgeschlossen | PR von Feature-Branch gegen main | PR + Review-History |

Vorteile gegenüber externen Orchestrierungstools

| Aspekt | Git-basiert | Externe Tools (Temporal, Kafka, etc.) |
| --- | --- | --- |
| Zusätzliche Infrastruktur | Keine | Broker/Engine muss betrieben werden |
| Nachvollziehbarkeit | Git-History ist der Audit-Trail | Separater Log-/Event-Store nötig |
| CI/CD-Integration | Nativ (PRs triggern Pipelines) | Adapter/Webhooks nötig |
| Persistenz | Git-Repository = persistent by default | State-Store muss gesichert werden |
| Wiederherstellung | git log + git reset = vollständiger Zustand | Tool-spezifische Recovery-Mechanismen |
| Lernkurve | Git kennt jeder Entwickler | Tool-spezifisches Wissen nötig |

### Begründung

Warum Git statt Message Queue?

Message Queues (RabbitMQ, Kafka) sind für lose gekoppelte, asynchrone Systeme mit hohem Durchsatz optimiert. Agenten-Workflows sind aber koordiniert, nicht lose gekoppelt: Der Orchestrator muss wissen, welche Tasks abgeschlossen sind, bevor er die nächsten startet. Git-Branches und PRs bilden diese Abhängigkeiten natürlicher ab als Events in einer Queue.

Warum Git statt Workflow-Engine?

Workflow-Engines (Temporal, Camunda) bieten formale State Machines, Retry-Mechanismen und Monitoring. Der Overhead ist jedoch erheblich: Engine-Deployment, Workflow-Definition, Worker-Registrierung. Für ein Agenten-System mit 5–10 parallelen Agenten und klar definierten Phasen (Plan → Develop → Test → Review → Merge) ist Git ausreichend. Wenn das System auf 50+ Agenten skaliert, sollte diese Entscheidung revisited werden.

Warum der Knowledge Store im Repository und nicht in einer Datenbank?

Der Knowledge Store ist primär Textdokumente: ADRs, API-Specs, Konventionen, Glossare. Diese sind in Markdown/JSON im Repository natürlicher zuhause als in einer Datenbank. Agenten lesen diese Dateien als Teil ihres Kontextfensters – ein File-Read ist einfacher als ein DB-Query. Zudem ist der Knowledge Store damit automatisch versioniert und über PRs reviewbar.

### Konsequenzen

#### Positive Konsequenzen

- Kein zusätzlicher Infrastrukturbedarf: Git-Repository ist bereits vorhanden, kein Broker, keine Engine, keine Datenbank
- Vollständige Nachvollziehbarkeit: Jeder Workflow-Schritt ist ein Git-Commit, jede Entscheidung ein Datei-Eintrag im Knowledge Store – die gesamte Historie ist über git log abrufbar
- Nahtlose CI/CD-Integration: Pull Requests gegen Feature-Branches triggern automatisch die Guardrails-Pipeline – kein zusätzliches Webhook-Setup
- Versionierter Knowledge Store: Architekturentscheidungen, Domain-Wissen und Konventionen sind im selben Repository wie der Code – immer synchron, immer reviewbar
- Entwickler-freundlich: Jeder Entwickler versteht Git-Branches, PRs und Merges – keine Einarbeitung in ein neues Orchestrierungstool
- Offline-fähig: Git funktioniert lokal, kein Netzwerkzugang zu externen Services nötig

#### Negative Konsequenzen

- Git-Operationen können bei großen Repositories (>1 GB, >100.000 Commits) langsam werden. Mitigation: Shallow Clones für Worktrees, regelmäßiges Repository-Housekeeping, Git LFS für große Dateien.
- Shared Knowledge Store ist dateibasiert: Kein Index, keine Query-Language, keine Transaktionen. Mitigation: Klare Verzeichnisstruktur, JSON für maschinenlesbare Daten, Markdown für menschenlesbare Dokumente.
- Skalierungsgrenzen bei >10 parallelen Agenten: Viele gleichzeitige Branches, häufige Merges, potenzielle Git-Lock-Contention. Mitigation: Concurrency-Limit (ADR-2), sequenzielle Merges für überlappende Dateien.
- Task-Status-Management über Dateien in docs/knowledge/tasks/ ist rudimentär: Kein Dashboard, kein Alerting, keine automatische Timeout-Erkennung. Mitigation: Leichtgewichtiges CLI-Tool, das Task-Dateien auswertet und Statusübersichten generiert.
- Keine native Unterstützung für komplexe Workflow-Patterns (Compensating Transactions, Saga Pattern). Für einfache Plan→Develop→Test→Review→Merge-Workflows ausreichend, bei komplexen Orchestrierungen revisit nötig.
