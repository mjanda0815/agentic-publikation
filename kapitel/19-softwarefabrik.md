# 19 Die SoftwareFabrik — von der Referenzarchitektur zum System

> **Hinweis:** Die Kapitel 1–18 beschreiben die Referenzarchitektur, wie sie
> in Version 1.3 dieses Whitepapers (März 2026) entworfen wurde. Dieses
> Kapitel beschreibt, was daraus wurde: die *Agentic Software Factory*
> (Produktname: SoftwareFabrik), ein vom Autor gebautes und betriebenes
> System, das die Referenzarchitektur produktisiert. Es ist ein
> Erfahrungsbericht aus erster Hand — alle Angaben sind aus dem Quellcode
> des Systems erhoben (Stand: Version 0.19.0, Juli 2026), nicht aus
> Projektdokumentation oder Erinnerung. Wo eine Aussage im Code verankert
> ist, nennt eine Fußnote die konkrete Klasse.

## 19.1 Von der Referenzarchitektur zur Implementierung

Die SoftwareFabrik ist eine **Control Plane für agentische
Softwareentwicklung**. Sie schreibt keinen Code selbst und hostet kein
Sprachmodell. Sie steuert, begrenzt, protokolliert und bewertet die Arbeit
externer Coding-Agenten — und macht deren Ergebnis prüfbar.

Der Unterschied zur direkten CLI-Nutzung eines Coding-Agenten ist genau der
Unterschied zwischen *ein Entwickler mit einem mächtigen Werkzeug* und *ein
Entwicklungsprozess*: Spezifikation, Freigabe, Isolation, Review,
Nachvollziehbarkeit, Budget, Mandantentrennung. In einem Satz: Die
SoftwareFabrik ist die produktisierte Umsetzung der in diesem Whitepaper
beschriebenen Referenzarchitektur — vendor-neutral statt an ein einzelnes
Werkzeug gebunden, und um die Governance-Schicht erweitert, die ein
reguliertes Umfeld tatsächlich verlangt.

### Der Kernablauf

Ein Vorhaben durchläuft die Fabrik in sechs Schritten:

1. **Erfassen.** Ein sechsschrittiger Wizard sammelt Projektidee,
   Zielplattform, Backend- und Frontend-Stack; 18 Templates decken Web,
   Mobile und Desktop ab, inklusive Import eines bestehenden Repositories.
2. **Spezifizieren.** Daraus generiert die Plattform versionierte
   Markdown-Artefakte (`PROJECT.md`, `INSTRUCTIONS.md`, `AGENTS.md`,
   `WORKFLOW.md`, `DEFINITION_OF_DONE.md`, `README.md`), die der Mensch vor
   dem Lauf editieren kann. Das ist der Punkt, an dem menschliche Absicht
   maschinenlesbar wird.
3. **Ausführen.** Ein *Run* durchläuft sieben Phasen. Der Coding-Agent läuft
   in einer Sandbox auf einem projektpersistenten Workspace mit eigenem
   Git-Repository, auf einem eigenen Branch.
4. **Prüfen.** Read-only-Review-Adapter analysieren den Diff; ein Quality
   Gate aggregiert die Befunde zu PASS/WARN/FAIL. Bei Fehlschlag speist die
   Plattform das Feedback zurück in den Agenten — bis zu zwei automatische
   Korrekturversuche.
5. **Übergeben.** Erfolgreiche Runs werden lokal gemergt oder als Pull
   Request gepusht; bei aktivierter PR-Rückkopplung wartet der Run auf grüne
   CI und den Merge.
6. **Belegen.** Jeder relevante Schritt landet in einer signierten,
   append-only Audit-Hashkette; ein Warum-Trace rekonstruiert für jeden Run,
   *welche* Policy, *welches* Modell und *welche* Freigabe gewirkt haben.

### Kennzahlen der Codebasis

| Kennzahl | Wert |
|---|---|
| Produktivklassen (Java) | 362 |
| Produktivcode | ~33.000 Zeilen |
| Testklassen | 257 |
| Fachliche Slices (Module) | 27 |
| Datenbanktabellen | 39 |
| Flyway-Migrationen | 37 |
| Execution-Adapter | 10 |
| Review-Adapter | 6 |
| Wizard-Templates | 18 |
| Coverage-Gate | Line ≥ 85 %, Branch ≥ 81 % (JaCoCo, buildbrechend) |
| Releases | 26 (0.1.0 bis 0.19.0, April–Juli 2026) |

Der Technologiestack ist bewusst konservativ: Java 25, Spring Boot 4,
server-gerendertes UI (Thymeleaf + HTMX, Server-Sent Events für Live-Logs,
kein SPA), PostgreSQL 18 mit Flyway, Docker Compose. Ein Maven-Modul, ein
Prozess, eine Datenbank — kein Cluster, kein Message-Broker, kein
Service-Mesh. Die Komplexität des Systems liegt in der *Steuerung von
Nichtdeterminismus*, nicht in der Infrastruktur, und genau dort soll sie
auch bleiben.

### Bewusste Nicht-Ziele

Für die Einordnung ist die Abgrenzung so wichtig wie der Funktionsumfang:

- **Kein eigenes Modell-Hosting.** Die Fabrik ist Steuerschicht, kein
  Inferenz-Stack. Lokale Modelle werden über eine CLI (z. B. Ollama)
  angebunden.
- **Keine Web-IDE.** Entwickelt wird weiter in IntelliJ oder VS Code; die
  Fabrik besitzt den Prozess, nicht den Editor.
- **Kein Consumer-SaaS.** Zielbild ist die Installation im Unternehmen —
  bis hin zum Air-Gap-Betrieb.
- **Kein Real-Time-Co-Editing**, kein eigener Build-Server, kein
  Kubernetes-Zwang.

## 19.2 Systemkontext und Bausteinsicht

<!-- TODO(abbildung): Abbildung 21: Systemkontext der Agentic Software Factory: eine Control Plane zwischen Mensch, Coding-Agenten und Zielrepository. -->

Der Systemkontext unterscheidet drei menschliche Rollen — Architekt/Lead
Developer (spezifiziert, gibt frei), Auditor/Compliance (liest Nachweise)
und Administrator (Mandanten, Rollen, Policies) — und drei Klassen externer
Systeme: die Coding-Agenten als Subprozesse (Vendor-CLIs und
Cloud-Gateways), das Zielrepository mit seiner CI, und die Scanner- und
Lizenzinfrastruktur. Gegenüber dem Systemkontext aus Kapitel 3 fällt auf:
Auditor und Administrator sind eigenständige Akteure geworden. Das ist kein
Zufall, sondern die Konsequenz aus dem Governance-Anspruch — wer Nachweise
verlangt, braucht eine Rolle, die sie liest.

<!-- TODO(abbildung): Abbildung 22: Bausteinsicht: modularer Monolith mit Ports-and-Adapters pro Slice; externe Werkzeuge ausschließlich hinter Ports. -->

### Modularer Monolith mit erzwungenen Grenzen

Die Fabrik ist ein **modularer Monolith**: ein Maven-Modul, ein
Deployment-Artefakt, 27 sauber geschnittene Pakete (*Slices*) pro Bounded
Context. Jeder Slice trägt seine eigenen Schichten (`domain`,
`application`, `web`, teils `infrastructure`); externe Systeme —
Coding-CLIs, Git, Maven, Scanner, GitHub-API — sitzen ausschließlich hinter
Ports.

<!-- TODO(abbildung): Abbildung 23: Fachliche Slices der Fabrik, gruppiert nach Aufgabe. Blatt-Slices (provenance, export, guardrails) konsumieren nur. -->

Die Größenverteilung der Slices ist selbst eine Aussage: `run` und
`execution` machen zusammen ein Viertel der Codebasis aus — die Steuerung
des nichtdeterministischen Teils ist der eigentliche Aufwand, nicht die
Fachlichkeit drumherum. Die Governance-Slices (`policy`, `audit`,
`mandant`, `provenance`, `export`, `skills`) sind dagegen klein:
Governance kostet vor allem *Entwurfsdisziplin*, nicht Code.

Der entscheidende Unterschied zum Konzeptteil dieses Whitepapers: Die
Architekturregeln sind nicht beschrieben, sondern **maschinell erzwungen**.
Drei ArchUnit-Testklassen laufen in jedem Build:^[`LayeringRulesTest`,
`HexagonalRulesTest`, `ArchitectureDebtRatchetTest` im Testbaum des
Systems.]

- **Schichtenregeln:** `domain` hängt weder von `web` noch von der
  Execution-Infrastruktur ab; `application` nicht von `web`; Controller nur
  in `..web..`; kein `JpaRepository` in `..web..` oder `..application..`.
- **Hexagonale Regeln:** `domain` kennt `application` nicht; weder
  `application` noch `web` kennt eine konkrete
  `ExecutionAdapter`-Implementierung. Die letzten beiden Regeln sind der
  Kern der Vendor-Neutralität: Es ist technisch unmöglich, versehentlich
  einen Service an einen konkreten Vendor zu koppeln — der Build bricht.
- **Debt-Ratchet:** Zwei Regeln, die heute *nicht* eingehalten werden
  (Modulzyklen; 13 direkte `web → JpaRepository`-Zugriffe), werden mit
  ArchUnits `FreezingArchRule` als versionierte Baseline eingefroren. Ein
  *neuer* Verstoß bricht den Build; ein *behobener* verschwindet automatisch
  aus der Baseline. Die Schuld ist gezählt und sichtbar statt implizit.

Der Ratchet hat einen lehrreichen Fallstrick: Der Freeze speichert nur eine
begrenzte Zahl elementarer Modulzyklen (Kappungsgrenze, Standard 100).
Solange die tatsächliche Zyklenzahl darunter liegt, ist die Enumeration
vollständig und deterministisch. Überschreitet eine neue Cross-Slice-Kante
die Grenze, wird die Enumeration abgeschnitten und *reihenfolgeabhängig* —
der Test wird lokal grün und in der CI rot, ohne dass sich der Code
inhaltlich unterscheidet. Das ist ein reales Betriebsrisiko automatisierter
Architekturmetriken und ein Beleg für eine These, die sich durch dieses
Kapitel zieht: **Guardrails müssen selbst gewartet werden.**

Ein wiederkehrendes Entwurfsmuster verdient Erwähnung, weil es aus dem
Ratchet folgt: Neue Querschnittsfähigkeiten werden konsequent als
**Blatt-Slice** angelegt — ein Paket, das nur konsumiert und von niemandem
konsumiert wird. Der Warum-Trace (`provenance`) korreliert Run-, Metrik-,
Plan-, Freigabe- und Audit-Daten, ohne dass irgendein anderer Slice davon
abhängt; der Audit-Export (`export`) aggregiert dasselbe zum Bundle. Eine
Fähigkeit, die naturgemäß überall hinschaut, würde als zentraler Service
sofort Modulzyklen erzeugen — als Blatt-Slice erzeugt sie keinen einzigen.

### Das Domänenmodell: der Entwicklungsprozess als Fachdomäne

Die Fabrik modelliert **den Entwicklungsprozess selbst** als Domäne. Nicht
der generierte Code ist das Fachobjekt, sondern Spezifikation
(`ProjectDefinition`, `PromptArtifact`), Lauf (`Run` mit `RunPhase`),
Backlog (`PlanItem` mit Abhängigkeiten), Freigabe (`ApprovalDecision`),
Regelwerk (`PolicyDocument`) und Nachweis (`AuditEvent`). Das ist die
konsequente Anwendung von Kapitel 11 auf das Agentensystem selbst — mit
einer bewussten Pragmatik: Domänenaggregat und JPA-Entität sind dieselbe
Klasse. Kein separates Persistenzmodell, kein Mapping-Code; die Entscheidung
ist im Code dokumentiert und in den ArchUnit-Regeln bewusst ausgespart,
statt sie stillschweigend zu brechen. Für die reine DDD-Lehre ist das ein
Verstoß; für ein System, dessen Komplexität woanders liegt, ist es
Time-to-Value.

<!-- TODO(abbildung): Abbildung 26: Kernaggregate des Datenmodells. Vollständig: 39 Tabellen, 37 Flyway-Migrationen. -->

Der Migrationsverlauf liest sich als Reifungskurve des Systems: V1–V9
Grundschema (Werkzeug), V12–V18 Wizard und Projektgedächtnis (Prozess),
V19–V25 Plan-/Build-Runs, Branches, Quality Gate (Lebenszyklus), V26–V33
ausschließlich Mandanten- und Nachweisstrukturen (Mehrmandantenfähigkeit
und Nachweisfähigkeit), V34–V39 Repository-Realität, Skills, Routinen. Auf
diese Kurve kommt Abschnitt 19.8 zurück.

## 19.3 Das Ausführungsmodell: der Run

Der *Run* ist die Ausführungseinheit der Fabrik — das Gegenstück zum
Execution Model aus Kapitel 7, jedoch nicht als Task-Graph, sondern als
**zustandsbehaftete Pipeline mit Regelkreis**. Die gesamte Orchestrierung
hat genau eine Stelle, an der Run-Statuswechsel stattfinden; die erlaubten
Übergänge liegen zentral, unerlaubte Übergänge werfen eine Ausnahme statt
still zu passieren.^[`RunOrchestrationService` (~1.550 Zeilen),
`RunStatusTransitions`; unerlaubte Übergänge werfen
`InvalidRunStateTransitionException`.]

### Zwei Run-Arten, sieben Phasen, 14 Zustände

Es gibt zwei Run-Arten: Ein **Plan-Run** analysiert den Ist-Stand und
schlägt die nächsten Arbeitsschritte vor; nur Dateien unter `plans/` werden
committet, alles andere wird verworfen, und die Vorschläge landen als
Backlog-Elemente (`plan_item`, mit Abhängigkeiten) in der Datenbank. Ein
**Build-Run** setzt ein Backlog-Element tatsächlich um: Code auf einem
isolierten Branch, validiert, gemergt oder als Pull Request übergeben. Die
Asymmetrie ist Absicht — ein Plan-Run darf keinen Code ändern und
durchläuft kein Build-Gate. Damit ist Planung risikofrei automatisierbar,
die Grundlage für zeitgesteuerte Routinen und automatische Folgevorschläge.

Jeder Run durchläuft sieben Phasen (Intake, Prompt-Assembly,
Workspace-Preparation, Execution, Validation, Correction, Completion) und
bewegt sich durch 14 Zustände. Drei davon tragen die Argumentation dieses
Whitepapers weiter:

- **`WAITING_FOR_APPROVAL`** — der Mensch ist ein *Zustand im System*, kein
  Nebenprozess. Human-in-the-Loop (Prinzip AP-6) ist damit nicht Appell,
  sondern Zustandsmaschine.
- **`NEEDS_CORRECTION`** — Fehlschlag ist ein regulärer Zustand mit
  definiertem Ausgang, nicht ein Abbruch.
- **`WAITING_FOR_PR`** — die Realität des Zielrepositories (fremde CI,
  fremde Reviewer, fremder Merge-Zeitpunkt) ist im Modell abgebildet, statt
  am Systemrand zu enden.

<!-- TODO(abbildung): Abbildung 24: Laufzeitablauf eines Build-Runs von der Anlage bis zum Merge, inklusive Korrekturschleife und Approval-Punkten. -->

<!-- TODO(abbildung): Abbildung 25: Zustandsmodell eines Runs. Alle Übergänge sind zentral hinterlegt; unerlaubte Übergänge werfen. -->

### Ablauf eines Build-Runs

Vier Stationen des Ablaufs sind konzeptionell bemerkenswert:

**Policy-Prüfung zweimal.** Vor der Anlage prüft der Orchestrator
Modell-Policy, aktive Policy-as-Code (ist der Adapter erlaubt?),
Attestierungspflicht und Lizenzgrenzen — abgelehnte Läufe erzeugen ein
attestiertes Ereignis `RUN_POLICY_DENIED`, auch die Ablehnung ist Nachweis.
Beim tatsächlichen Start werden Attestierungspflicht und geltende
Policy-Version *erneut* ausgewertet und gestempelt. Der Grund: Ein vor der
Policy-Aktivierung angelegter Run würde sie sonst umgehen — und Warum-Trace
wie Audit-Export sollen die real durchgesetzte Version ausweisen, nicht die
zum Anlagezeitpunkt gültige.

**Projektpersistenter Workspace, Branch-Isolation.** Der Workspace gehört
dem Projekt, nicht dem Run; der erste Lauf initialisiert Git, Folgeläufe
arbeiten auf dem bestehenden Code weiter. Bei Remote-Projekten wird der
Base-Branch *vor* dem Abzweig auf den Remote-Stand vorgespult, damit der
Lauf nicht auf veraltetem Code aufsetzt; dann zweigt der Run auf einen
eigenen Branch (`sdlc/run-<id>`) ab. In den Workspace werden die
versionierten Spezifikations-Artefakte, das kuratierte Projektgedächtnis
(`MEMORY.md`) und die Guardrails-Projektion geschrieben (dazu 19.6).

**Zwei Approval-Punkte.** Verlangt die Policy eine Freigabe, stoppt der Run
vor der Execution — und regulierte Profile verlangen ein zweites
Vier-Augen-Gate vor dem Merge. Die Fortsetzung nach der zweiten Freigabe
führt *nicht* erneut aus, sondern finalisiert nur den bereits validierten
Stand; sonst wäre die signierte Zusage Fassade.

**Abschluss an der Repository-Realität.** Entweder lokaler Merge oder Push
mit Pull Request; im PR-Fall wartet der Run auf grüne CI und den Merge. Das
zugehörige Backlog-Element wird erst mit dem Merge auf `DONE` gesetzt —
nicht mit dem Codeschreiben. Ein abgeschlossener Build-Run kann über ein
Ereignis einen Folge-Plan-Run anstoßen; zusammen mit zeitgesteuerten
Routinen entsteht der geschlossene Kreis *planen → bauen → prüfen → mergen
→ neu planen*, mit definierten Stellen, an denen ein Mensch eingreifen muss.

### Der Regelkreis: Korrekturschleife statt Retry

Kapitel 7 beschreibt eine Retry-Strategie. Die Praxis hat daraus einen
**Regelkreis** gemacht: Vier Ereignisse speisen dieselbe Schleife — Build
fehlgeschlagen, Quality Gate blockiert, **Merge-Konflikt** mit dem
Base-Branch, rote CI am Pull Request. In allen vier Fällen wird ein
Feedback-Text erzeugt (Build-Ausgabe, Findings, Konfliktdateien) und als
zusätzlicher Kontext in einen erneuten Agentenlauf eingespeist — maximal
zwei Versuche, danach bleibt der Run in `NEEDS_CORRECTION` und die Befunde
bleiben nachvollziehbar.

<!-- TODO(abbildung): Abbildung 30: Die Korrekturschleife als Regelkreis — Befunde werden zu Eingaben des nächsten Laufs. -->

Zwei Details aus dem Betrieb:

- **Merge-Konflikte gelten als Arbeitsanweisung, nicht als Systemfehler.**
  Der Konflikt wird dem Agenten mit den betroffenen Dateien und der
  expliziten Aufforderung übergeben, die Konfliktmarker aufzulösen.
  Repository-Realität wird damit Teil der Aufgabe.
- **Der Branch-Wechsel vor der Korrektur ist sicherheitsrelevant.** Nach
  einem abgebrochenen Merge steht der Workspace auf dem Base-Branch. Ohne
  expliziten Rückwechsel würde die Korrektur samt `git add -A` direkt auf
  `main` committen — und damit sowohl die Branch-Isolation als auch die
  Pflichtfreigabe umgehen. Dieser Fall wurde in einem adversarialen
  Sicherheits-Re-Review gefunden und behoben. Er illustriert eine
  Kernerfahrung: Agentische Systeme scheitern an den *Übergängen* zwischen
  Automatismen, nicht in ihnen.

## 19.4 Vendor-Neutralität als Architektureigenschaft

Kapitel 20 der Vorversion verglich Werkzeuge. Die Fabrik hat die Frage
architektonisch aufgelöst: Die gesamte Vendor-Neutralität hängt an einer
Schnittstelle,^[`ExecutionAdapter` im `execution`-Slice.] hinter der zehn
Adapter stehen — ein deterministischer `mock`-Adapter (Default; macht das
System ohne Vendor demonstrierbar und testbar), sechs CLI-Adapter (Claude
Code, Codex, Gemini, Aider, Kimi, lokales LLM z. B. via Ollama) und drei
Cloud-Gateways (AWS Bedrock, Google Vertex AI, Azure OpenAI). Die
Adapterwahl ist eine Konfigurationsfrage je Run, aufgelöst über eine
Hierarchie (Run-Override > Projekt-Default > User-Setting > globales
Setting > Konfigurationsdatei); ein Projekt kann die erlaubten Adapter
einschränken, und Policy-as-Code kann diese Wahl mandantenweit übersteuern.

<!-- TODO(abbildung): Abbildung 27: Vendor-Neutralität durch einen Port: Application- und Web-Schicht kennen ausschließlich den ExecutionAdapter (ArchUnit-erzwungen). -->

Drei Entwurfsentscheidungen im Port selbst:

1. **Streaming statt Rückgabewert.** Ein Event-Consumer liefert Logzeilen,
   Token-Verbrauch und Phasensignale *während* des Laufs — ohne das wäre
   Live-Beobachtbarkeit unmöglich und ein Abbruch bliebe folgenlos.
2. **Verfügbarkeit ist Teil des Vertrags.** Adapter, deren CLI fehlt,
   verschwinden geordnet aus der Auswahl, statt zur Laufzeit zu scheitern.
3. **Timeout ist ein eigener Ergebniszustand**, nicht ein Sonderfall von
   Fehler. Bei nichtdeterministischen Agenten ist „hat zu lange gebraucht"
   fachlich etwas anderes als „ist gescheitert".

*Einschränkung:* Die drei Cloud-Gateway-Adapter sind konfigurierbar und
degradieren sauber, wurden aber nicht end-to-end gegen echte
Cloud-Credentials verifiziert — sie sind als „vorbereitet", nicht als
„erprobt" zu bezeichnen.

### Abo-Modus statt Token-Abrechnung

Ein in der Literatur selten behandelter, praktisch sehr relevanter Punkt:
Coding-CLIs lassen sich meist auf zwei Wegen authentifizieren — per API-Key
(Abrechnung je Token) oder per Abo-Login (Flatrate). Die Fabrik unterstützt
für Claude Code, Codex und Kimi beides explizit. Der kritische Teil ist das
**aktive Entfernen des API-Keys aus der Subprozess-Umgebung im Abo-Modus**:
Sonst würde die CLI stillschweigend den kostenpflichtigen Pfad wählen — ein
Fehler, der erst auf der Rechnung sichtbar wird. Die Konsequenz für das
Kostenmodell aus Kapitel 15 ist grundsätzlich: Bei Flatrate-Abos entstehen
keine Token-Kosten je Lauf; ein reines Token-ROI-Modell bildet die
Wirtschaftlichkeit agentischer Entwicklung nicht mehr vollständig ab.

### Capability-Routing statt Modellnamen

Die Modellwahl-Strategie aus Kapitel 5 ist umgesetzt — aber über
**Fähigkeitsprofile** statt hart verdrahteter Modellnamen: Eine
Routing-Rolle (Planung vs. Umsetzung) verlangt eine Fähigkeitsstufe, die
zur Laufzeit auf ein konkretes Modell aufgelöst wird. Planung darf ein
stärkeres, teureres Modell bekommen als mechanische Umsetzung, ohne dass
irgendwo ein Modellname im Code steht — wichtig in einem Markt, in dem
Modellnamen eine Halbwertszeit von Monaten haben. Eine je Projekt gesetzte
Modell-Policy wird beim Anlegen eines Runs erzwungen und attestiert; im
Nachhinein ist belegbar, welches Modell wirklich gearbeitet hat.

### Sandbox

Eine Factory wählt zwischen zwei Sandbox-Varianten: ein eigener Prozess je
Run mit sauber gesetzter Umgebung und einer Allowlist der Variablen, die
den Agenten überhaupt erreichen — oder ein ephemerer Container je
Agentenlauf mit CPU-, Speicher- und Prozesslimits, read-only-Dateisystem,
Bindmount ausschließlich auf den Workspace und **`--network=none` als
Default**. Die Netzwerksperre als Voreinstellung ist eine starke Aussage:
Ein Coding-Agent braucht im Normalfall keinen ausgehenden Netzzugriff —
Abhängigkeiten kommen aus dem vorbereiteten Workspace beziehungsweise dem
Cache. Wer das Netz öffnet, tut es bewusst.

Zur Absicherung der Außenkontakte gehört eine **Host-Allowlist für
Git-Remotes**:^[`RemoteUrlPolicy` im `common`-Slice.] Nur für erlaubte
Hosts wird der Plattform-Token verwendet und eine API-Anfrage ausgeführt.
Ohne diese Grenze könnte eine manipulierte Remote-URL den fabrikweiten
Token exfiltrieren; zusätzlich wird das `git ext::`-Protokoll unterbunden,
das Kommandoausführung über Remote-Helper erlauben würde. Beide Befunde
stammen aus einem adversarialen Re-Review — Kapitel 14 hatte die
Bedrohungsklassen richtig benannt, die konkreten Angriffsflächen zeigten
sich erst im gebauten System.

## 19.5 Guardrails in der Praxis

Die Guardrails-Pipeline aus Kapitel 12 und ADR-3 ist umgesetzt — mit einer
architektonischen Präzisierung, die sich als tragend erwiesen hat: Es gibt
einen **zweiten Schichtbegriff**. Coding-Agenten *schreiben* Code;
Review-Adapter sind *read-only* und dürfen ihn nicht verändern. Ein System,
in dem dieselbe Instanz erzeugt und freigibt, hat kein Gate, sondern eine
Selbsteinschätzung.

Sechs Review-Adapter laufen parallel auf dem Diff: zwei LLM-Reviewer
(Diff-Review durch Claude Code bzw. Aider im Read-only-Modus), drei
statische Prüfer (Security-Muster wie API-Key-Präfixe, Path-Traversal,
SQL-Konkatenation; Architektur-Verstöße inklusive Änderungen an
bestehenden Datenbankmigrationen; Halluzinationsindikatoren) und ein
werkzeuggestützter Dependency-Scan (CVEs und Lizenzverstöße, blockierend).
Die Mischung ist Absicht: LLM-Reviewer finden Kontextfehler, die keine
Regel beschreibt; statische Reviewer finden deterministisch, kostenlos und
auditierbar genau das, was ein nichtdeterministisches Modell nicht
zuverlässig findet. Ein Gate, das nur aus LLM-Urteilen besteht, wäre selbst
nichtdeterministisch.

Der **Halluzinations-Reviewer** verdient besondere Erwähnung: Er prüft
nicht den Code, sondern die *Behauptungen über den Code* — „alle Tests
laufen durch" bei unverändertem Testverzeichnis, unberührte
Akzeptanzkriterien, Importe nicht existierender Klassen. Das ist die
direkte Umsetzung der Halluzinationserkennung aus Kapitel 12, verschoben
vom Code auf die Selbstauskunft des Agenten — dort sitzt der klassische
Selbstbetrug agentischer Systeme.

### Die Gate-Policy

Das Quality Gate aggregiert die Befunde über eine konfigurierbare
Policy^[`QualityGatePolicy` im `qualitygate`-Slice; vorkonfiguriert als
`strict()` und `lenient()`.] mit acht Stellschrauben (Blockierverhalten je
Schweregrad, Confidence-Schwelle, Pflichtkategorien, Pflicht-Reviewer).
Drei Sonderregeln kann **keine** Policy aufweichen:

- Security-Befunde der Stufen HIGH und CRITICAL blockieren immer.
- Architektur-Befunde der Stufe CRITICAL blockieren immer.
- Ein abgestürzter Reviewer wird zu `ERROR` materialisiert und führt zur
  Gesamtentscheidung `ERROR` — niemals zu einem stillen Pass.

Der letzte Punkt ist der wichtigste Satz dieses Abschnitts: **Ein Gate,
dessen Ausfall wie Erfolg aussieht, ist schlimmer als kein Gate**, weil es
Vertrauen erzeugt, das es nicht deckt. Dieselbe Logik findet sich an drei
weiteren Stellen des Systems (Lizenzprüfung *fail closed*, Attestierung
ohne Schlüssel ist ein Startfehler, ein CI-Job ohne Secret gilt als nicht
bestanden).

Das Confidence Scoring aus Kapitel 12 ist umgesetzt — allerdings ohne den
dort skizzierten AOP-Aspekt: Die Vertrauenswerte der Reviewer werden im
Gate-Service zu einem Gesamtwert verrechnet und gegen die Schwelle der
Policy geprüft. Ein Aspekt hätte die Nachvollziehbarkeit verschlechtert,
ohne funktionalen Gewinn.

### Drei Betriebsmodi

Das Gate läuft in einem von drei Modi, mandantenweit steuerbar: `off`,
`advisory` (Befunde werden erhoben und angezeigt, blockieren aber nicht),
`blocking` (ein FAIL startet die Korrekturschleife). ADR-3 forderte das
Gate als Pflicht; die Praxis hat den `advisory`-Modus ergänzt, denn der
Einführungspfad in Organisationen ist: erst messen, dann durchsetzen. **Ein
Gate, das am ersten Tag blockiert, wird am zweiten Tag abgeschaltet.**
Regulierte Compliance-Profile erzwingen `blocking` (19.6).

Im Blocking-Modus ist ein Gate-FAIL funktional gleichwertig mit einem
fehlgeschlagenen Build: Beides erzeugt Feedback für den nächsten
Agentenlauf. Das Gate ist damit kein Endpunkt, sondern ein **Regler** im
Regelkreis aus 19.3. Die Gate-Entscheidung wird am Run persistiert und geht
in Warum-Trace und Audit-Export ein — für jeden gelieferten Stand ist
nachweisbar, welches Urteil ihn passieren ließ.

## 19.6 Governance und Nachweisführung

Dieser Abschnitt beschreibt den Teil, den die Vorversion konzeptionell nur
streifte und der in regulierten Umgebungen über Einsatz oder Nicht-Einsatz
entscheidet: **Wie beweist man hinterher, was ein Agent unter welchen
Regeln getan hat?**

<!-- TODO(abbildung): Abbildung 28: Von der Policy bis zum Auditbericht: jede Durchsetzung erzeugt ein signiertes Kettenglied. -->

### Mandanten und Rollen

Projekte, Runs und alle abgeleiteten Aggregate sind mandantengescopt;
Zugriffsversuche über fremde IDs scheitern, und diese Eigenschaft ist als
Test festgeschrieben. Bemerkenswert ist eine Entscheidung gegen die
Konvention: `ADMIN` ist *kein* Super-Admin. Auch ein Administrator bleibt
für Daten mandantengescopt; isolationsfrei sind nur Kontenverwaltung und
Projektzuweisung. Eine Administrationsrolle kann Betrieb führen, ohne
Einblick in fremde Projektinhalte zu haben.

Das fünfstufige Rollenmodell (Viewer < Developer < Maintainer < Owner <
Admin) entspricht dem Least-Privilege-Modell aus Kapitel 14; freigeben darf
ab Maintainer. **Segregation of Duties** ist zuschaltbar: Wer einen Run
ausgelöst hat, darf ihn nicht selbst freigeben. Optionales SSO über OIDC
provisioniert neue Nutzer bewusst restriktiv als Viewer ohne Mandanten —
ein SSO-Anschluss darf Zugriff nie versehentlich erweitern.

### Policy-as-Code

Regeln sind kein Konfigurationszustand, sondern ein **versioniertes,
signiertes Dokument**. Der kanonische Inhalt ist bewusst minimal und
dadurch prüfbar: erlaubte Adapter, Gate-Modus, Pflicht-Freigabephasen,
Attestierungspflicht.^[`PolicyInhalt` mit kanonischer Serialisierung
(`kanonisch()`/`parse()`); Ed25519-Signatur über den kanonischen Text.]
Je Mandant existiert **genau eine aktive Version** — erzwungen über einen
partiellen Unique-Index in der Datenbank plus Service-Logik. Ohne diese
Invariante wäre die Frage „welche Regel galt zu diesem Zeitpunkt?" nicht
beantwortbar. Durchgesetzt wird im Orchestrator, an den zwei in 19.3
beschriebenen Zeitpunkten.

### Compliance-Profile

Vier Profile übersetzen Regulatorik in erzwingbare Policy-Vorlagen — die
Brücke von der Norm zum Code:

| Profil | Gate | Pflichtfreigaben | Attestierung | Regulatorischer Bezug |
|---|---|---|---|---|
| Baseline | advisory | — | nein | kein reguliertes Umfeld |
| EU AI Act | blocking | Execution | ja | VO (EU) 2024/1689, u. a. Art. 12 (Aufzeichnungspflichten), Art. 14 (menschliche Aufsicht) [@euaiact2024] |
| BAIT / MaRisk / DORA | blocking | Execution, Validation | ja | BaFin-Anforderungen an die IT; DORA (EU) 2022/2554 — IKT-Risiko, Nachweisführung [@dora2022] |
| BSI-Grundschutz / VS-NfD | blocking | Execution, Validation | ja | BSI IT-Grundschutz; für Verschlusssachen zusätzlich ausschließlich lokale Backends |

Das Anwenden eines Profils veröffentlicht eine neue signierte
Policy-Version und erzeugt ein attestiertes Ereignis. **Ehrliche
Einordnung:** Die Profile setzen die *technisch erzwingbaren* Anteile der
jeweiligen Regelwerke durch — Aufzeichnung, menschliche Aufsicht,
Nachweisführung, Vendor-Beschränkung. Sie ersetzen keine Rechtsberatung
und decken keine organisatorischen Pflichten ab.

### Die signierte Audit-Hashkette

Der Kern der Nachweisfähigkeit: Jedes Audit-Ereignis trägt eine lückenlose
Sequenznummer, den Hash des Vorgängers, den Hash über den eigenen Inhalt,
eine Ed25519-Signatur und die Schlüssel-ID.^[`AuditService.erfasse`
verkettet und signiert unter einem Monitor;
`AttestierungService.verifiziereKette` prüft.] Die Kettenprüfung
unterscheidet drei Fehlerbilder — ein Eintrag wurde nachträglich verändert
(`HASH_MISMATCH`), entfernt oder eingefügt (`CHAIN_BREAK`), oder stammt
nicht vom erwarteten Schlüssel (`BAD_SIGNATURE`). Altbestand ohne Signatur
wird transparent ausgewiesen, statt die Prüfung scheitern zu lassen.

Attestiert wird nicht jeder Tastendruck, sondern **jede Entscheidung, die
den Handlungsspielraum des Agenten festgelegt hat**: Run-Lebenszyklus,
Modellauflösung, angewendete und verweigerte Policies, angewendete
Guardrails-Version, Gate-Ergebnis, Freigaben, erzeugte und signierte
Artefakte. Diese Liste ist die praktische Antwort auf die Frage, was in
einem agentischen System nachweispflichtig ist.

Zwei Implementierungsdetails mit Verallgemeinerungswert: Zeitstempel werden
auf Millisekunden getrunkt, weil die Signatur sonst nach dem
Datenbank-Roundtrip nicht byte-stabil wäre — ein typischer, teuer gelernter
Fallstrick beim Signieren persistenter Daten. Und der Schlüsselbetrieb ist
konfigurationsgegatet: In Produktionsprofilen ist „Attestierung aktiviert,
aber kein Schlüssel vorhanden" ein *Startfehler*; wer ohne Signatur
betreiben will, muss das explizit deklarieren. Sicherheit durch bewusste
Entscheidung statt durch Vergessen.

### Warum-Trace und Audit-Export

Für jeden einzelnen Run beantwortet ein **Warum-Trace** die Frage „warum
ist dieser Code so entstanden?", indem er Run und Metriken (Modell, Kosten,
Dauer), Plan-Herkunft, Freigabeentscheidungen samt Akteuren, verwendete
Artefakte und die attestierten Ereignisse korreliert.^[`WarumTraceService`
(`provenance`-Slice, Blatt-Slice).] Zwei Attestierungslücken
(Modellauflösung, Gate-Ergebnis) wurden eigens dafür geschlossen — der
Trace erzwang rückwirkend, dass diese Ereignisse überhaupt entstehen.

Ein **Audit-Export** bündelt je Projekt oder Run ein prüffähiges Paket aus
Warum-Trace, Kettenverifikation, geltendem Policy-Stand und dem
öffentlichen Schlüssel — als JSON und HTML. Ein Detail mit Praxiswert: Das
Bundle enthält ausschließlich Strings, Primitive und UUIDs (Zeitstempel als
ISO-8601-Text). Die Serialisierung ist damit deterministisch und unabhängig
von Bibliotheksversionen — ein Nachweis, der je nach Jackson-Version anders
aussieht, taugt nicht als Nachweis.

### Lieferkette und Wissensbestand

Der Supply-Chain-Nachweis aus Kapitel 14 ist durchgezogen: SBOM je Build
mit Ed25519-Signatur über den Digest, Dependency- und Lizenz-Scan als
blockierender Reviewer im Gate, dazu CI-seitig Abhängigkeits-, Image- und
Secret-Scans. Auch der Wissensbestand ist Governance-Objekt: Skills und
Plugins liegen in einer mandantengescopten, **versionierten Bibliothek**
mit typisierter Herkunft (kuratiert, übernommen, angepasst). Damit ist
beantwortbar, welche Erweiterung in welcher Version zum Zeitpunkt eines
Laufs im Kontext des Agenten war — die Frage, an der sonst jede
Reproduzierbarkeitsdiskussion scheitert.

Die Verhaltensregeln für Agenten (`guardrails`-Slice) sind eine
versionierte Ressource, deren Versions-ID ein Hash des normalisierten
Inhalts ist. Bei jedem Run wird sie ins Repository projiziert: als
`AGENTS.md` — dem werkzeugübergreifenden De-facto-Standard — plus eine
minimale `CLAUDE.md`, die darauf verweist. **Eine Quelle, mehrere
Projektionen** statt einer gepflegten Kopie je Werkzeug; welche
Guardrails-Version gewirkt hat, wird attestiert.

### Gedächtnis ohne Vektorspeicher

Das Fünf-Schichten-Memory-Modell aus Kapitel 8 hat sich in der Praxis auf
vier klar getrennte Gedächtnisformen reduziert: die versionierten
Spezifikations-Artefakte (Absicht des Menschen, maschinenlesbar), das
kuratierte Projektgedächtnis (`MEMORY.md`, Learnings über Läufe hinweg),
der reale Code-Stand samt Git-Historie als Zustand, und das ephemere
Kontextfenster des Agenten. Es gibt **keinen Vektorspeicher** — bewusst.
Die Begründung ist eine Governance-Begründung: Was der Agent liest, muss
ein Mensch reviewen und ein Auditor zitieren können; eine
Ähnlichkeitssuche erfüllt beides nicht.

## 19.7 Betrieb und Souveränität

Kapitel 13 zeichnete eine Kubernetes-Deployment-Architektur. Die reale
Zielgruppe — Behörden, Finanzdienstleister, Mittelstand — fragt zuerst
etwas anderes: *Läuft es bei uns, ohne Cloud, ohne Rückkanal?* Die Antwort
der Fabrik ist bewusst schlicht: **ein Anwendungscontainer, eine
Datenbank**, dazu die Projekt-Workspaces auf dem Dateisystem und optional
ephemere Agent-Container je Run. Der Lizenz-Stack (OIDC-Provider plus
Lizenzdienst) ist getrennt und optional; er kann außerhalb der
Unternehmensgrenze stehen oder ganz entfallen.

<!-- TODO(abbildung): Abbildung 29: Deployment-Sicht: ein Anwendungscontainer, eine Datenbank, optional getrennter Lizenz-Stack. Air-Gap-fähig. -->

Die Startzeit-Härtung folgt durchgehend dem Prinzip *fail fast*: Der
Compose-Stack bricht ohne Konfigurationsdatei ab statt mit
Standardpasswörtern zu starten; das Container-Profil lehnt bekannte
Demo-Werte und zu kurze Master-Keys hart ab; ohne gesetztes Admin-Passwort
wird kein Admin angelegt; die Datenbank ist an die lokale
Loopback-Adresse gebunden.

**Lizenz ohne Rückkanal.** Die Lizenzschicht stellt signierte Lease-Token
mit sieben Tagen Gültigkeit aus, die offline verifiziert werden.
Kurzzeitige Nichterreichbarkeit des Lizenzservers ist unkritisch;
abgelaufenes Lease *und* nicht erreichbarer Server führen zu *fail closed*.
Für die Air-Gap-Frage ist das die entscheidende Eigenschaft: Ein System,
das für Verschlusssachen taugen soll, darf keine Online-Aktivierung als
Betriebsvoraussetzung haben.

Damit sind alle Bausteine für den vollständig getrennten Betrieb vorhanden:
lokales Modell als Adapter, netzlose Agent-Sandbox, Lizenz ohne Rückkanal,
PR-Poller standardmäßig deaktiviert (unbeaufsichtigte periodische
Remote-Kontakte sind eine bewusste Betriebsentscheidung), Host-Allowlist
für Remotes.

Dass das System nicht nur baubar, sondern betreibbar ist, belegt eine
dauerhaft laufende öffentliche Demo-Instanz (Demo-Profil mit täglichem
Datenreset). Eine Betriebserfahrung daraus gehört hierher, weil sie die
Logik aus 19.5 spiegelt: Ein Ausfall der Instanz ging nicht auf die
Anwendung zurück, sondern auf ein Reset-Skript, das bei vollem Dateisystem
abbrach, *bevor* es die Anwendung wieder startete. Automatisierung, die bei
Fehlern abbricht statt aufzuräumen, verwandelt kleine Störungen in
Ausfälle — dieselbe Klasse Fehler wie ein Reviewer-Absturz, der wie ein
Pass aussieht.

Erwähnenswert ist schließlich, dass die Fabrik sich selbst denselben
Mechanismen unterwirft, die sie anderen Projekten auferlegt: buildbrechende
Architektur-Tests und Coverage-Schwellen, Secret-Scan, SBOM,
Dependency-Scan, CI als Gate vor jedem Merge. Ein Werkzeug für
disziplinierte Entwicklung, das selbst undiszipliniert entwickelt würde,
wäre kein glaubwürdiger Beleg.

## 19.8 Was die Praxis am Konzept korrigiert hat

Der Abgleich zwischen Konzept (v1.3) und Implementierung ergibt über die 23
Kapitel hinweg überwiegend Bestätigung, an vielen Stellen Erweiterung — und
vier bewusste **Positionsverschiebungen**, die aus dem Bau eines realen
Systems folgen. Sie sind der eigentliche inhaltliche Gewinn dieses
Kapitels.

### (1) Ein Agent je Lauf, mehrere Prüfer — statt Hub-and-Spoke-Multi-Agent

Das Konzept (Kapitel 1, 3, 10, ADR-1) setzt auf sieben parallele
Spezialagenten unter einem Orchestrator. Die Implementierung startet
**einen** Agentenprozess je Run und erreicht Spezialisierung anders: über
Rollen- und Teamdefinitionen im Kontext, über getrennte Plan- und
Build-Runs — und vor allem über **mehrere unabhängige Prüfer** nach der
Ausführung.

Die Begründung: Der Nutzen mehrerer Agenten liegt in
*Perspektivenvielfalt*, und die ist beim Prüfen wertvoller als beim
Erzeugen. Mehrere gleichzeitig schreibende Agenten auf einem Repository
erzeugen Konfliktkosten, Zurechnungsprobleme („wer hat das geschrieben?")
und einen nicht attestierbaren Zustand. Die Fabrik verschiebt die
Parallelität deshalb von der Erzeugung auf die Bewertung. Aus demselben
Grund wurde die Workspace-Isolation über Git-Worktrees (ADR-2) zur
**Branch-Isolation auf einem projektpersistenten Workspace**: Iteration
über Läufe hinweg schlägt parallele Isolation. Der Preis ist benannt —
Läufe desselben Projekts sind nicht beliebig parallel; die parallele
Multi-Branch-Ausführung ist bewusst zurückgestellt.

### (2) Regelkreis statt Retry — Repository-Realität als Eingabe

Das Konzept beschreibt eine Retry-Strategie (Kapitel 7.5, 9). Die
Implementierung zeigt: **Ein Retry ohne neue Information wiederholt nur den
Fehler.** Wertvoll wird die Wiederholung erst, wenn die Ursache zur Eingabe
wird — Build-Ausgabe, Reviewer-Findings, Merge-Konfliktdateien, roter
CI-Status. Besonders die letzten beiden sind die eigentliche Erkenntnis:
Der Agent scheitert in der Praxis seltener am Programmieren als an der
*Realität des Repositories* — veralteter Base-Branch, fremde parallele
Änderungen, fremde CI. Ein agentisches System, das diese Realität nicht als
Aufgabe modelliert, endet dort, wo die interessante Arbeit anfängt.

### (3) Governance ist keine Ergänzung, sondern Struktur

Im Konzept steht Compliance neben der Architektur (Kapitel 12–14). In der
Implementierung ist sie in die Architektur eingewachsen: Policy-Prüfung
zweimal (Anlage *und* Ausführung); Freigabe als Zustand des Laufs, nicht
als Nebenprozess; jede Durchsetzung als signiertes Kettenglied; genau eine
aktive Policy-Version.

Die Reifungskurve lässt sich am Migrationsverlauf ablesen: Die Migrationen
V26–V33 sind ausschließlich Mandanten- und Nachweisstrukturen — und sie
bestimmten *rückwirkend*, an welchen Stellen im Ablauf überhaupt Ereignisse
entstehen müssen. Attestierungslücken mussten nachträglich geschlossen
werden, damit der Warum-Trace vollständig ist. Das ist ein belastbares
Argument gegen die verbreitete Reihenfolge „erst Funktion, dann
Compliance": **Die Nachweisstruktur lässt sich nicht sauber nachrüsten** —
wer sie früher entwirft, spart die Nacharbeit.

### (4) Kubernetes ist keine Voraussetzung — Souveränität schon

Das Konzept zeichnet eine Kubernetes-Deployment-Architektur (Kapitel 13).
Die reale Zielgruppe fragt zuerst nach Betreibbarkeit im eigenen Haus:
on-prem, notfalls air-gapped, ohne Online-Aktivierung. Die Antwort der
Fabrik — ein Prozess, eine Datenbank, optionaler Lizenz-Stack, lokales
Modell, netzlose Sandbox — verschiebt die Komplexität dorthin, wo sie
hingehört: in die Steuerung des Nichtdeterminismus, nicht in die
Betriebsinfrastruktur.

Daneben bestätigt die Implementierung zentrale Thesen des Konzepts
ausdrücklich: Das Orchestrator-Prinzip trägt (eine Instanz, die Zustand
besitzt und Übergänge kontrolliert, ist der Unterschied zwischen Werkzeug
und Prozess — und die einzige Stelle, an der Governance ansetzen kann);
Guardrails brauchen einen eigenen Schichtbegriff; Halluzinationserkennung
braucht einen eigenen Prüfer; deklarative Konfiguration im Repository
funktioniert — nur eben werkzeugneutral; ein geteilter Wissensstand ist
notwendig und mit versionierten Dateien herstellbar. Und ADR-4 (Git als
Orchestrierungsmechanismus) gilt mit einer Präzisierung: Git ist
Zustandsträger — Branch, Commit, Checkpoint, Merge, PR —, aber nicht die
alleinige Wahrheit. Der autoritative Zustand liegt in der Datenbank, weil
ein Auditor Fragen stellt, die `git log` nicht beantwortet: welche Policy,
welches Modell, wessen Freigabe.

## 19.9 Grenzen und offene Punkte

Ein System, das seine offenen Punkte benennt und seine Architekturschuld
zählt, ist der glaubwürdigere Beleg für die Thesen dieses Whitepapers als
eines, das angeblich keine hat. Stand 0.19.0 (August 2026):

| Punkt | Art |
|---|---|
| Parallele Multi-Branch-Ausführung mehrerer Runs je Projekt | bewusst zurückgestellt |
| Seat-scharfe Budget-Obergrenze (Kostenauswertung je auslösendem Nutzer existiert; der harte Cap wirkt je Mandant) | offen |
| Cloud-Gateways (Bedrock/Vertex/Azure) nicht end-to-end gegen echte Credentials verifiziert | Verifikationslücke |
| Container-Sandbox existiert, ist aber nicht der Default; ohne Container-Runtime Rückfall auf Prozessisolation | Einschränkung |
| Test-Isolationsdefekt: ein Integrationstest committet unter bestimmten Bedingungen in das reale Repository | Defekt |
| Architektur-Altschuld: eingefrorene Modulzyklen und 13 direkte Repository-Zugriffe der Web-Schicht | dokumentierte, gezählte Schuld |

Dazu drei Beobachtungen aus dem Entwicklungsverlauf (26 Releases in rund
drei Monaten), die sich verallgemeinern lassen:

1. **Governance kam spät, wurde aber strukturbildend** — siehe 19.8 (3).
2. **Die härtesten Befunde lagen an den Übergängen**, nicht in den
   Funktionen: der Branch-Zustand nach einem abgebrochenen Merge, ein vor
   der Policy-Aktivierung angelegter Lauf, eine Mandanten-Policy, die eine
   globale unterlaufen konnte. Ab Version 0.16 dominieren Befunde aus
   adversarialen Multi-Agent-Reviews die Changelogs — das System wurde
   systematisch mit dem Ziel geprüft, seine eigenen Zusagen zu brechen.
   Automatismen sind einzeln korrekt und im Zusammenspiel angreifbar.
3. **Vendor-Neutralität wurde durch einen Test billig.** Solange die
   ArchUnit-Regeln stehen, kostet ein neuer Adapter eine Klasse und einen
   Test. Ohne sie wäre die Kopplung längst durch die Schichten diffundiert.

Ausdrücklich **nicht** behauptet werden quantifizierte Produktivitäts- oder
ROI-Zahlen aus dem Betrieb der Fabrik selbst — dafür existiert keine
kontrollierte Messung. Die Modellrechnungen aus Kapitel 15 bleiben
Modellrechnungen; was dieses Kapitel belegt, ist etwas anderes: dass die
Referenzarchitektur als lauffähiges, betreibbares, nachweisfähiges System
existiert.
