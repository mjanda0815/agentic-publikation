# 12. Kennzahlen, Entwicklungsverlauf, offene Punkte

## 12.1 Kennzahlen

| Kennzahl | v0.39.0 | v0.38.0 | v0.30.0 | Erhebung |
|---|---|---|---|---|
| Produktivklassen | 502 | 499 | 421 | `git ls-tree -r <tag> app/src/main/java`, `*.java` |
| Produktivcode | ~54.938 Zeilen | ~53.967 Zeilen | ~41.737 Zeilen | Zeilen aller dieser Dateien (`git show <tag>:<datei> \| wc -l`) |
| Testklassen | 360 | 353 | 291 | `app/src/test/java`, `*.java` |
| Test-zu-Produktiv-Verhältnis | ~0,72 Klassen | ~0,71 Klassen | ~0,69 Klassen | |
| Fachliche Slices | 34 | 34 | 30 | Pakete unter `io.softwarefabrik.app` (bisherige Zählweise); neu: `canary`, `mcp`, `mcpgateway`, `spec` |
| Datenbanktabellen | 63 | 63 | 58 | `CREATE TABLE` in Migrationen |
| Flyway-Migrationen | 61 (V1–V65) | 61 (V1–V65) | 52 (V1–V54) | Dateien in `db/migration`; nicht vergeben: V10, V11, V55, V57 |
| HTTP-Routen | 184 in 39 Controllern | 184 in 39 Controllern | 161 in 34 Controllern | Mapping-Annotationen (methodenweise, repo-weit ohne Tests); Controller = Dateien mit Mapping-Annotation |
| Execution-Adapter | 10 | 10 | 10 | `implements ExecutionAdapter` |
| Review-Adapter | 7 | 7 | 6 | neu: `SpecConformanceReviewerAdapter` |
| Wizard-Templates | 18 | 18 | 18 | `TemplateRegistry.builtin()` |
| Run-Zustände / Phasen | 14 / 7 | 14 / 7 | 13 / 7 | neu: `WAITING_FOR_INPUT` |
| Run-Arten | 3 (BUILD, PLAN, SPEC) | 3 | 2 | `RunKind` |
| Workflow-Zustände / Task-Zustände | 11 / 12 | 11 / 12 | 11 / 12 | |
| Rollen | 5 | 5 | 5 | `Rolle` |
| Compliance-Profile | 4 | 4 | 4 | `ComplianceProfil` |
| Coverage-Gate | Line ≥ 85 %, Branch ≥ 81 % | dto. | dto. | JaCoCo, buildbrechend (`app/pom.xml`) |
| Releases | 47 (0.1.0 – 0.39.0) | 46 (0.1.0 – 0.38.0) | 38 (0.1.0 – 0.30.0) | `## [x.y.z]` in `CHANGELOG.md`; 2026-04-17 bis 2026-10-20; eine Version 0.37.0 gibt es nicht |
| CI-Jobs je Push | 7 | 7 | 5 | Jobs in `.github/workflows/ci.yml`; neu `verifier`, `gateway` |
| Eigenständige Module neben `app/` | `license-service/`, `verifier/` (~1.130 Zeilen, Version 1.1.0), `gateway/` (~2.370 Zeilen) | `license-service/`, `verifier/` (~1.010 Zeilen), `gateway/` (~2.370 Zeilen) | `license-service/` | nicht in den Klassen-/Zeilenzahlen enthalten |

*Stand: Tag `v0.39.0` (= `4acd5c1`), 2026-10-20; erhoben auf dem Tag (am
2026-10-20 per `git ls-tree`/`git show v0.39.0:…`/`git grep v0.39.0`),
nicht im Arbeitsverzeichnis. Dasselbe Skript reproduziert die Spalte
v0.38.0 (= `1fb8aac`) exakt. 0.39.0 brachte weder Slice noch Tabelle,
Migration, Route oder Zustand; der Zuwachs (+3 Klassen, ~+970 Zeilen,
+7 Testklassen) liegt in Policy, Audit, Export, Kennzahlen, Orchestrierung
und Workflow (SDD-Governance). Die CI-Jobzahl bleibt 7; der Job `verifier`
baut zusätzlich den alten Verifier aus dem Tag `v0.38.0`. Die
Vergleichsspalte v0.30.0 wurde mit demselben
Verfahren neu erhoben und reproduziert die Werte der Fassung 3.0 exakt —
mit einer Ausnahme: Die Fassung 3.0 nannte 6 CI-Jobs, `ci.yml` am Tag
`v0.30.0` enthält 5.*

## 12.2 Entwicklungsverlauf

Der Verlauf eignet sich als Evidenz dafür, in welcher Reihenfolge ein
agentisches Entwicklungssystem tatsächlich reift — und dass Governance nicht
am Anfang steht, aber früher gebraucht wird, als man plant.

### Phase 1 — Werkzeug (0.1.0 – 0.8.1, April–Mai 2026)

Wizard, Spezifikations-Artefakte, Run mit Phasen, Mock- und
Claude-Code-Adapter, Approval-Policies, Audit-Log, Settings mit
Scope-Hierarchie, Quality-Gate-Grundlagen, Lizenzstack, Container-Sandbox
(ADR-0011), Run-Templates, Conductor (Plugins/Skills/`AGENTS.md`-Sync),
Modell-Routing je Agentenrolle, Kostenschätzung im Wizard, Inline-Diffs vor
Freigabe.

### Phase 2 — Vendor-Neutralität und Betriebsformen (0.9.0 – 0.12.0, Juni 2026)

Abo-Authentifizierung statt API-Key (inkl. aktivem Strippen des Keys),
Windows-nativer Einzelplatzbetrieb, Wizard-Umbau von „ein Template" auf drei
orthogonale Dimensionen (Zielplattform × Backend × Frontends) mit
Kompatibilitätsmatrix, weitere Stacks.

### Phase 3 — Lebenszyklus statt Greenfield (0.13.0 – 0.14.0, Juni 2026)

Projektpersistenter Workspace mit Re-Run, echter Repo-Import, Projekt-Memory,
Plan-/Build-Runs mit Backlog, Branch-Isolation je Build-Run, Push + Pull
Request, automatische Korrektur-Feedback-Schleife, Quality Gate in der
Pipeline mit drei Betriebsmodi, automatische Folgevorschläge.

### Phase 4 — Enterprise-Fähigkeit (0.15.0 – 0.17.2, Juli 2026)

Betriebsmodi (Einzelplatz-Abo vs. Team-API-Pool), OpenAI-kompatibler Adapter
für lokale Modelle, Cloud-Gateways, erzwungene Modell-Policy je Projekt,
Capability-Routing; Mandanten mit harter Isolation, RBAC, SSO-OIDC,
Mandantenbudgets; signierte Audit-Hashkette, Warum-Trace, Policy-as-Code,
Compliance-Profile, Audit-Export; SBOM, signierte Artefakte, Dependency-Scan
als blockierender Reviewer.

Ab 0.16.0 dominieren **Befunde aus adversarialen Multi-Agent-Reviews** die
Changelogs — das System wurde systematisch mit dem Ziel geprüft, seine eigenen
Zusagen zu brechen. Behobene Klassen von Befunden: Pflichtfreigaben, die real
umgangen werden konnten (RS-01); IDOR-Schreiblücken (RS-02); Policy-Shadowing
durch Mandanten-Policies; Cross-Tenant-Flächen ohne Betreiber-Gate.

### Phase 5 — Repository-Realität und Härtung (0.18.0 – 0.19.0, Juli 2026)

Remote-Synchronisation vor dem Lauf, Merge-Konflikt als Korrektureingabe,
PR-/CI-Rückkopplung mit eigenem Run-Zustand, Meilensteine mit Changelog/Tag/
GitHub-Release, Backlog-Abhängigkeiten. Sicherheits-Hotfix 0.18.1 gegen
Token-Exfiltration/SSRF über manipulierte Remote-URLs und RCE über
`git ext::`-Remote-Helper. 0.19.0: versionierte Skill-Bibliothek,
zeitgesteuerte Routinen, Segregation of Duties, vendor-neutrale
Engineering-Guardrails.

### Phase 6 — Konsolidierung und Sicherheitsrunde (0.20.0, August 2026)

Kimi-Adapter (Moonshot AI) mit API-Key- und Abo-Modus, Buildnummer-Anzeige
in der UI, Doku-Sweep. Sicherheitsseitig: zwei CVEs per Patch-Bump innerhalb
der Minor-Linie geschlossen, eine dritte ohne verfügbaren Fix begründet
akzeptiert — als Suppression **mit Ablaufdatum**, danach schlägt der Scan
bewusst wieder fehl; die Suppression-Datei verlangt seither für jeden
Eintrag Begründung und Ablaufdatum. Ursache der bis dahin unbemerkten Lage:
der Abhängigkeits-Scan lief in der CI ohne gültigen Zugang zur
Schwachstellendatenbank (das Geheimnis wurde nur zur Vorprüfung gelesen,
dem Build aber nie als Parameter übergeben) und war zugleich als nicht
blockierend konfiguriert — die Oberfläche meldete Grün, ohne dass je ein
vollständiger Scan stattgefunden hatte.

### Phase 7 — Workflow-Ebene, Roadmap-Stufen 0 und 1 (0.21.0, August 2026)

**Stufe 0:** ADR-0014 (hierarchische Workflow-Orchestrierung, strikte
Richtung `workflow → run`) und ADR-0015 (Single Writer per Workspace),
Migration V40 (`run.workflow_id`, `run.workflow_task_id`), einmalige
Zuordnung eines Runs zu einer Workflow-Task, neuer Slice
`io.softwarefabrik.app.workflow`, Feature-Flag
`softwarefabrik.workflow.enabled` mit Default **aus**. Nachweisanbindung
vollständig: acht `WORKFLOW_*`-Auditereignisse (CREATED, TASK_ADDED,
SYNTHESIS_ADDED, BUDGET_SET, PLAN_SUBMITTED, PLAN_APPROVED, TASK_STARTED,
TASK_FINISHED) und `WorkflowKontext` im Warum-Trace jedes Child Runs.

**Stufe 1:** Workflow-Aggregat (11 Zustände), Workflow Tasks (12 Zustände)
mit Abhängigkeitsgraph, parallele Analyse-Child-Runs in getrennten
Worktrees (Obergrenze 3 gleichzeitig), Synthese-Task, menschliche
Planfreigabe als eigener Zustand, Workflow-Budget mit Prüfung *vor* dem
Start der nächsten Task, UI unter `/workflows`. Migrationen V41–V43.
Ausgeführt werden ausschließlich nicht-schreibende Capabilities
(`istInPhase1Erlaubt()`); die acht schreibenden sind technisch gesperrt.

Der Synthese-Task hängt automatisch an allen Tasks, baut seinen Auftrag aus
deren Ergebnissen und referenziert die eingeflossenen Eingaben — belegt,
nicht behauptet. Sein Auftrag fordert Widersprüche ausdrücklich ein und
verbietet das Glätten.

**Geändert:** Die Sperre gegen gleichzeitige Läufe war projektweit
formuliert, begründete sich aber mit dem geteilten Workspace. Sie vergleicht
jetzt den effektiven Workspace — getrennte Worktrees dürfen parallel laufen,
dasselbe Verzeichnis nicht. Präziser, nicht schwächer.

## 12.3 Beobachtungen zum Verlauf

Drei Muster, die sich für die Publikation verallgemeinern lassen:

1. **Governance kam spät, wurde aber strukturbildend.** Die Migrationen
   V26–V33 sind ausschließlich Mandanten- und Nachweisstrukturen. Rückwirkend
   bestimmten sie, an welchen Stellen im Ablauf überhaupt Ereignisse entstehen
   müssen — Attestierungslücken (Modellauflösung, Gate-Ergebnis) mussten
   nachträglich geschlossen werden, damit der Warum-Trace vollständig ist.
   Wer die Nachweisstruktur früher entwirft, spart diese Nacharbeit.
2. **Die härtesten Befunde lagen an den Übergängen**, nicht in den Funktionen:
   der Branch-Zustand nach einem abgebrochenen Merge, ein vor der
   Policy-Aktivierung angelegter Lauf, eine Mandanten-Policy, die eine
   globale unterlaufen konnte. Automatismen sind einzeln korrekt und im
   Zusammenspiel angreifbar.
3. **Vendor-Neutralität wurde durch einen Test billig.** Solange die
   ArchUnit-Regeln stehen, kostet ein neuer Adapter eine Klasse und einen
   Test. Ohne sie wäre die Kopplung längst durch die Schichten diffundiert.

### Phase 8 — Parallel schreibende Child Runs, Roadmap-Stufe 2 (0.22.0, August 2026)

**2a — Pfad-Besitzmodell und Workspace-Leases** (Migration V44): Ein Task
erklärt `OWNED`, `READ_ONLY` und `PROTECTED`. Überschneidungen mit einem
aktiven Task verhindern den Start; der Vergleich läuft auf Segmentgrenzen
(`src/main` kollidiert nicht mit `src/mainx`). Leases mit Ablauffrist und
Herzschlag — ein abgestürzter Agent legt den Workflow nicht dauerhaft lahm.
Build-Dateien (`pom.xml`, `build.gradle[.kts]`) und das
Migrationsverzeichnis sind immer exklusiv, auch ohne Anmeldung.

**2b — Merge Queue und Integration Gate** (Migration V45): Erfolgreiche
Child-Branches werden sequenziell und in Planreihenfolge in einen
Integrationsbranch geführt, nicht in Fertigstellungsreihenfolge. Das lokale
Gate je Child Run prüft eine Änderung für sich, das Integration Gate den
zusammengeführten Gesamtstand; nur über dessen Urteil erreicht ein Workflow
`COMPLETED`. Merge-Status: `WARTEND`, `LAEUFT`, `GEMERGED`, `KONFLIKT`,
`ABGEBROCHEN`.

Ein Merge-Konflikt hält an, statt zu scheitern: Der Workflow geht nach
`WAITING_FOR_APPROVAL` und zeigt die Konfliktdateien; entschieden wird
zwischen erneutem Versuch (max. zwei) und Verwerfen des Branches. Ein
verworfener Branch macht das Integration Gate `FAILED`. Ein Kaskaden-Abbruch
stoppt alle mittelbar abhängigen Tasks und verwirft offene Merge-Einträge.

### Phase 9 — Vertraege und Planaenderungen, Roadmap-Stufen 3 und 4a (0.23.0/0.24.0)

**Stufe 3** (V46–V48): eigener Blatt-Slice `contract` mit unveraenderlichen
Fassungen, Content-Hash ueber den normalisierten Inhalt (Normalisierung
bewusst minimal), sechs Vertragsarten (OpenAPI, AsyncAPI, JSON-Schema,
Java-Interface, Domain Event, Akzeptanzkriterien). Bindung beim Start des
Child Runs statt bei der Planung; Stale-Erkennung synchron in der
Veroeffentlichungstransaktion; Merge-Blockade vor dem Einreihen und vor dem
Merge.

**Stufe 4a** (V49): `PlanRevision` haelt jede Planaenderung unveraenderlich
fest (Grund, Pflichtbeschreibung, Ausloeser, betroffene Tasks), attestiert
ueber `WORKFLOW_REPLANNED`. Von acht Replanning-Gruenden tragen sechs eine
neue Eingabe; `ZUSCHNITT_GEAENDERT` und `REIHENFOLGE_GEAENDERT` nicht — ein
Task wird nur bei neuer Eingabe zurueckgesetzt (Regelkreis statt blindem
Retry maschinell erzwungen — „Rule Loop" der Fabrik-Roadmap; nicht mit
AP-6 des Whitepapers verwechseln, dort Human Authority).
Aufteilen vererbt Abhaengigkeiten und Capability, aber nicht die
Schreibbereiche; Zusammenfuehren erbt deren Vereinigung; laufende Tasks
lassen sich nicht umschneiden.

**Website:** KI-Chatbot (TrustChat) auf allen 44 Seiten DE+EN, mit
entsprechend ergaenzter Datenschutzerklaerung. Betrifft die Website, nicht
die Plattform.

### Phase 10 — Merge Intelligence und Koordinationsschicht (0.25.0/0.26.0)

**Stufe 4b** (V50): Konfliktklassifikation in sieben Arten
(`MIGRATIONSNUMMER`, `BUILD_KONFIGURATION`, `SPERRDATEI`, `NUR_FORMATIERUNG`,
`VERALTETER_BRANCH`, `INHALTLICHER_WIDERSPRUCH`, `UNBEKANNT`), geprueft von
der teuersten zur harmlosesten Art. Analyse nebenwirkungsfrei ueber
`git merge-tree --write-tree`. Rebase nur, wenn die Einordnung ihn als
aussichtsreich einstuft — bei Migrationsnummer und inhaltlichem Widerspruch
bewusst nicht (waere ein Retry ohne neue Information — Rule-Loop-Prinzip
der Fabrik-Roadmap).
Eskalationsbericht mit vollstaendigem Kontext; die Einordnung wird am
Queue-Eintrag festgehalten, weil der Konflikttext nur im Moment der Analyse
existiert.

**Stufe 5a** (Release 0.26.0, V51): Worker-Registrierung mit Ablaufzeit und
Herzschlag, Anspruch vor Seitenwirkung. Der verteilte Betrieb ueber mehrere
Hosts ist ausdruecklich zurueckgestellt — die Roadmap-Voraussetzung
*gemessener Bedarf* ist nicht erfuellt. Dieselbe Maschinerie schloss aber
auf einem Host drei reale Luecken: Nachfolger starteten nicht automatisch,
nach einem Neustart nahm niemand laufende Arbeit wieder auf, und `CLAIMED`
stand seit Phase 1 im Zustandsmodell, ohne je gesetzt zu werden.
Anspruchsverfall ohne stillen Erfolg: Ein noch nicht gestarteter Task geht
zurueck nach `READY`, ein bereits laufender nach `FAILED` (Workspace in
unbekanntem Zustand; Weg zurueck ueber das Replanning aus 4a). Automatischer
Versand freigewordener Nachfolger hinter eigenem Flag
(`softwarefabrik.workflow.dispatcher.enabled`, Default aus) — automatisches
Starten von Laeufen kostet Tokens.

### Phase 11 — Produktivitaets- und Qualitaetsmessung (0.27.0)

**Stufe 6:** neuer Blatt-Slice `kennzahlen` (`/kennzahlen`), 30. Fachlichkeit,
**ohne eigenes Schema und ohne Migration** — alle Werte werden aus ohnehin
entstehenden Daten abgeleitet (eine mitgefuehrte Kennzahl weicht frueher
oder spaeter von dem ab, was sie beschreiben soll). Messbar: Time to
Accepted Merge, Erstdurchlauf-Quote, Korrekturschleifen, Planaenderungen,
Kosten je Workflow und je Child Run, Merge-Konfliktquote samt Verteilung
nach Konfliktart, Freigabe-Wartezeit. Vier Messgroessen der Roadmap werden
ausdruecklich NICHT gemessen, sondern als `Messluecke` mit Begruendung
ausgewiesen: menschliche aktive Arbeitszeit, Testabdeckungsaenderung,
entkommene Defekte und Rollbacks, Vergleich zur manuellen Umsetzung. Der
Typ `Quote` unterscheidet „ohne Nenner = unbekannt" von 0 % (UI zeigt
einen Strich). Behoben: `KennzahlenController` lag ausserhalb von `..web..`
und brach `LayeringRulesTest` — nicht zu verwechseln mit dem eingefrorenen
Ratchet fuer Altschulden, der gruen war und den Verstoss gar nicht sehen
konnte.

**0.28.0 — Testabdeckungsaenderung nachgereicht** (V52): `AbdeckungsLeser`
liest den ohnehin im Workspace liegenden Abdeckungsbericht nach jedem Build
in drei Formaten (JaCoCo, Cobertura, Istanbul; feste Pruefreihenfolge,
damit die Kennzahl nicht vom Dateisystem abhaengt). Zeilen-/Zweigabdeckung
samt Quelle am `build_result`; Spalten bewusst nullable (kein Bericht heisst
unbekannt, nicht 0 %). Ausweis in Prozentpunkten, erst ab der zweiten
Messung. Bewusst ohne XML-Parser gelesen — agentengenerierter Code ist
nicht vertrauenswuerdig, ein Parser waere eine XXE-Angriffsflaeche im
Eingabepfad. Messluecken damit 4 → 3.

**0.29.0 — Rollback-Erkennung nachgereicht** (V53): `GitService.findeRollbacks`
liest Reverts aus der Git-Historie; `merge_queue_entry` und `run` halten
Merge-Commit und Ruecknahme als Anker. Zwei duenne Anwender
(`RollbackErkennung` fuer den Workflow, `RunRollbackErkennung` fuer den
Einzel-Run beim Basis-Abgleich), weil der `run`-Slice nach ADR-0014 nichts
vom `workflow`-Slice wissen darf — der Einzel-Run ist der Normalfall, dieser
Teil wirkt also auch ohne Workflow-Flag. Gemessen wird der Revert, nicht der
Defekt; die Quote ist als Untergrenze ausgewiesen; nur verankerte
Auslieferungen stehen im Nenner. Attestiert ueber `MERGE_ZURUECKGENOMMEN`
und `RUN_ZURUECKGENOMMEN`. Die Messluecke heisst nur noch „entkommene
Defekte" — die Rollback-Haelfte ist geschlossen, die Defekt-Haelfte braeuchte
eine Ticketsystem-Anbindung, die es nicht gibt.

**0.30.0 — Arbeitszeit-Luecke zerlegt, Schema gegen Mapping geprueft** (V54):
Die Messluecke „menschliche aktive Arbeitszeit" bleibt bestehen, ist aber
zerlegt: *Eingriffe* (wie oft ein Mensch entscheiden musste) und
*Entscheiderzahl* sind messbar, beide aus `ApprovalDecision` abgeleitet
(ausgewiesen in `WorkflowKennzahlen`); dazu ein freiwilliges Aufwandsfeld an
der Freigabe (`approval_decision.aufwand_minuten`, nullable, Check-Constraint
max. 10080 Minuten = eine Woche) — erfragt, nicht gemessen, nie mit
Abgeleitetem verrechnet, immer mit *Aufwandsabdeckung* („45 min aus 3/12")
ausgewiesen. Das Feld steht auch an der Einzel-Run-Freigabe
(`RunController.freigeben`) und wirkt dort ohne Workflow-Flag. Bewusst nicht
gebaut: Interaktions-Telemetrie/Leerlauf-Erkennung. Ausserdem zwei neue
Schema-Tests gegen die zweimal zugeschlagene Fehlerklasse
Migration-vs.-JPA-Mapping (0.23.0: `CHAR(64)`/`varchar(64)`; V53:
`merge_queue_eintrag` statt `merge_queue_entry`): `SchemaMappingTest`
(Namensvergleich ohne Docker) und `SchemaValidierungTest` (Testcontainers,
Flyway + Hibernate `validate`; Ueberspringen ohne Docker wird ausdruecklich
als Nicht-Bestehen gemeldet); beide gegen absichtliche Abweichungen
geprueft. Hintergrund: Die Suite laeuft gegen H2 mit `ddl-auto=create-drop`
und abgeschaltetem Flyway und kann diese Fehlerklasse per Konstruktion nicht
sehen. Website: Foliensatz zum Sonderdruck als Download (DE+EN).

### Phase 12 — Absicherung der Agentenläufe und unabhängiger Nachweis (0.31.0–0.34.0, September/Oktober 2026)

Grundlage: ADR-0016 (MCP-Readiness, Ist-Analyse), ADR-0017 (Nullzustand),
ADR-0022 (Canary-Harness), ADR-0023 (Offline-Verifier), ADR-0018
(MCP-Gateway); Details in `08-governance-compliance.md` (8.7.1, 8.11) und
`06-adapter-und-modellschicht.md`.

**0.31.0** (V56): MCP-Nullzustand für alle Agentenläufe — ephemeres HOME
je CLI-Aufruf mit kopierten Auth-Dateien, Claude Code zusätzlich mit
`--strict-mcp-config`, leerer `--mcp-config` und
`ENABLE_CLAUDEAI_MCP_SERVERS=false` (beobachtet an Claude Code 2.1.283:
`.mcp.json` im Workspace startete im `--print`-Modus ohne Trust-Rückfrage);
Workspace-Prüfung mit `MCP_KONFIG_BASELINE`/`_VORGEFUNDEN`/
`_AGENT_GESCHRIEBEN`; Policy-Felder `mcpStandardverbot` (BAIT/MaRisk/DORA,
BSI/VS-NfD) und `erlaubtePlugins` (Plugins standardmäßig gesperrt);
Canary-Harness mit signiertem Register `isolationsnachweis`. Spring Boot
4.1.1. Die seit 0.20.0 befristet akzeptierte Laufzeit-CVE entfiel durch
ein Tomcat-Update. Bei der Vorbereitung fiel auf, dass die Agent-CLIs nie
im Container liefen (ADR-0017, „Korrektur zu ADR-0016") — die
Container-Sandbox kapselt nur Build und trivy-Scans, und zwar mit Netz.

**0.32.0**: Offline-Verifier (`verifier/`, nur JDK, Exit 0/1/2,
Vertrauensanker Fingerabdruck) und Audit-Export-Schema 2.0
(Hash-Stellvertreter, signierter Ketten-Kopf, signierte Run-Manifeste,
im Run angewandte Policy-Versionen).

**0.33.0/0.33.1** (V58): Prüfung der Claude-Anbindung fand vier Stellen
„Erfolg ohne Beleg" — stiller PASS der LLM-Reviewer bei Fehler-Exit, Gate
auf leerem Diff (`git diff HEAD` statt Branch-Diff), Abbruch ohne
Prozessende (neu: `ProzessRegistry`), Build-Runs ohne Schreibrechte (neu:
`--permission-mode acceptEdits` + `--allowedTools`; Reviews `dontAsk`).
BYOS entfernt, Abo-Modus als persönliche Nutzung; `kosten_geschaetzt`
kennzeichnet Abo-Kosten als Schätzung; Rollen-Defaults der Modellwahl,
`RUN_MODELL_AUFGELOEST` mit `quelle=`. 0.33.1: Patch-Sweep ohne Migration.

**0.34.0** (V59–V60): MCP-Gateway (eigener Prozess, nur lesende Tools,
Pinning, `MCP_TOOL_AUFRUF` je Aufruf, fail-closed Zustellung, Standard
aus); Hooks/Projekt-Settings importierter Repos bei Claude Code
abgeschaltet (`--setting-sources=user`, `disableAllHooks`); Rollen- und
Mandantenprüfung der Workflow-Ebene nachgezogen (fehlte bis dahin);
Claude-Läufe wurden mit 0 € bewertet (Parser las nicht geliefertes Feld)
— behoben, dazu Cache-Schreib-Tokens und CLI-Kostenschätzung; Aufwandsfeld
an der Planfreigabe; Kennzahl „Eingriffe" zählt die Planfreigabe.

### Phase 13 — Spec-Driven Development (0.35.0–0.39.0, Oktober 2026)

Grundlage: ADR-0027 (Status *Proposed*), `docs/roadmap/spec-driven-development.md`,
`specs/SPEC-001…005`; Details in `13-spec-driven-development.md`.

**0.35.0** (V61–V62): Slice `spec`, Produkt-Spec mit AC-IDs, Fassungen
mit SHA-256, Freigabe ab MAINTAINER (`SPEC_APPROVED`), Spec-Modus
AUS/LEICHT/STRENG, Feature-Flag `softwarefabrik.spec.enabled` + FeatureGate
(Professional/Enterprise); Backlog-Bezug; `ReviewRequest.acceptanceCriteria`
erstmals gefüllt (vorher fest `null` — die AC-Prüfung des
Halluzinations-Reviewers lief bis dahin ins Leere).

**0.36.0** (V63): Traceability — Commit-Trailer, `RUN_SPEC_GEBUNDEN`,
Warum-Trace, Objective-Kopf, Spec-Index in `AGENTS.md`, Workflow-Task-
Bindung, Spiegelung des AC-Blocks als Vertrag, Freigabe gegen
Gleichzeitigkeit gesichert.

**0.38.0** (V64–V65; bündelt die Roadmap-Stufen 0.37 und 0.38, keine
Version 0.37.0): Conformance-Reviewer `spec-conformance`, Spec-Drift
(`SPEC_DRIFT`, Veraltet-Markierung), Spec-Run (`RunKind.SPEC`,
`WAITING_FOR_INPUT`, `spec_frage`), Reverse-Spec.

**0.39.0** (keine Migration; SPEC-005, PR #168/#169, Release-PR #170):
SDD-Governance, nur Tier Enterprise (`Feature.SPEC_GOVERNANCE`) —
Policy-Felder `pflichtSpecFreigabe` und `minAcAbdeckung`, Durchsetzung bei
BUILD-Start, Workflow-Planfreigabe und im Quality Gate; Compliance-Profile
EU_AI_ACT und BAIT_MARISK_DORA mit Spec-Pflicht; Audit-Export 2.1 mit
signierten Spec-Fassungen, Offline-Verifier 1.1.0 (kompatibel in beide
Richtungen); SDD-Kennzahlen ohne neue Tabelle. Sicherheitsfix:
`RUN_POLICY_DENIED` bei der Run-Anlage wurde bis 0.38.0 mit der Ablehnung
zurückgerollt und stand nie in der Kette (Ablehnungen während des Laufs
schon); seit 0.39.0 `AuditService.erfasseUnabhaengig`, dazu neu
`WORKFLOW_PLAN_DENIED`. Details
`13-spec-driven-development.md`, 13.11.

## 12.4 Offene Punkte (Stand 2026-10-20, nach 0.39.0)

| Punkt | Art |
|---|---|
| Verteilter Betrieb über mehrere Hosts (Stufe 5b); Stufen 0–4, 6 und die Koordinationsschicht aus 5a sind umgesetzt | bewusst zurückgestellt, Voraussetzung nicht erfüllt |
| Seat-scharfe Budget-Obergrenze (Auswertung je Seat existiert seit v0.17) | offen |
| Cloud-Gateways (Bedrock/Vertex/Azure) nicht end-to-end verifiziert | Verifikationslücke |
| Agent-CLIs laufen als Host-Prozess; Agent-Container (Auth-Projektion, Netz nur zu Modell-APIs) eigenes Arbeitspaket (ADR-0017) | offen |
| MCP-Gateway nur lesend, nur Ausführung mit Claude Code; Canary-Fall „Gateway projiziert" und Hook-Markerquelle (ADR-0018 Schritt 3, ADR-0017 Nachtrag) | Verifikationslücke |
| Preisstatus unbekannter Modelle weiterhin 0 € (`ModelPricingProperties`) | Budgetlücke |
| Legacy-Verifikationsstatus in der Plattform undifferenziert (Verifier unterscheidet für Exporte) | Nachweislücke |
| SBOM ohne Scanner wird übersprungen (`SbomService`, `SKIPPED`) | Fail-Closed-Lücke |
| Architektur-Altschuld: eingefrorene Modulzyklen (Baseline genau 100 Zyklen; wirksame Kappung seit 0.29.0: 400) + 13 `web → JpaRepository` | dokumentierte Schuld |
| SDD-Abdeckungsprüfung (auch `minAcAbdeckung`) ist eine Heuristik über Test-Referenzen; Wirkung von SDD nicht gemessen | Einschränkung |
| Playwright-E2E-Suite als Standard nach jedem Deploy | geplant |

Entfallen gegenüber 0.30.0: die befristet akzeptierte Laufzeit-CVE
(seit 0.31.0 ohne Suppression grün). Entfallen gegenüber 0.38.0:
SDD-Governance (umgesetzt mit 0.39.0) und der Test-Isolationsdefekt — er
war bereits in 0.19.0 behoben (Commit `8dc06d5`, PR #51, Guard in
`MilestoneReleaseService.gibFrei` + Regressionstest; siehe
`01-systemueberblick.md`); die Quelle hatte eine nicht nachgezogene
Arbeitsnotiz übernommen.

Diese Liste gehört bewusst in die Publikation. Ein System, das seine offenen
Punkte benennt und seine Architekturschuld *zählt*, ist der glaubwürdigere
Beleg für die These des Whitepapers als eines, das keine hat.

## 12.5 Quellenverweise im Repository

Für Fußnoten mit konkreter Fundstelle:

| Aussage | Fundstelle |
|---|---|
| Orchestrierung, Phasen, Regelkreis | `app/src/main/java/io/softwarefabrik/app/run/application/RunOrchestrationService.java` |
| Zustandsmodell | `run/domain/RunStatus.java`, `RunStatusTransitions.java` |
| Adapter-Port | `execution/ExecutionAdapter.java` |
| Vendor-Neutralität maschinell erzwungen | `src/test/java/.../architecture/HexagonalRulesTest.java` |
| Schichtenregeln | `.../architecture/LayeringRulesTest.java` |
| Architektur-Ratchet | `.../architecture/ArchitectureDebtRatchetTest.java`, `src/test/resources/archunit-store/` |
| Gate-Policy | `qualitygate/domain/QualityGatePolicy.java` |
| Compliance-Profile inkl. Regulatorik-Bezug | `policy/domain/ComplianceProfil.java` |
| Policy-Inhalt (kanonisch, signierbar) | `policy/domain/PolicyInhalt.java` |
| Audit-Hashkette | `audit/AuditService.java`, `audit/AttestierungService.java` |
| Warum-Trace | `provenance/WarumTraceService.java` |
| Audit-Export | `export/AuditExportService.java` |
| Guardrails-Quelle | `guardrails/GuardrailsService.java`, `resources/guardrails/engineering-guardrails.md` |
| Sandbox | `execution/sandbox/` |
| Host-Allowlist gegen SSRF/Token-Exfiltration | `common/RemoteUrlPolicy` |
| Migrationen | `app/src/main/resources/db/migration/` |
| CI | `.github/workflows/ci.yml` |
| ADRs | `docs/adr/` |
| Runbooks | `docs/runbooks/` |
| Versionshistorie | `CHANGELOG.md` |
| MCP-Nullzustand, Workspace-Prüfung | `execution/sandbox/AgentHome.java`, `mcp/McpWorkspacePruefung.java` |
| Isolationsnachweis (Canary) | `canary/CanaryService.java`, `mcp/IsolationsnachweisRegister.java` (V56) |
| MCP-Gateway | Modul `gateway/`, Slice `mcpgateway/` |
| Offline-Verifier, Export 2.0 | Modul `verifier/`, `export/AuditExportService.java`, `docs/verifier.md` |
| Sandbox-Reichweite | `execution/sandbox/SandboxScopeAdvisory.java`, `docs/security/sandbox.md` |
| Spec-Driven Development | Slice `spec/` (`SpecParser`, `SpecVersion`, `SpecService`), `review/reviewer/SpecConformanceReviewerAdapter.java`, `specs/_vorlage/spec.md`, ADR-0027 |
