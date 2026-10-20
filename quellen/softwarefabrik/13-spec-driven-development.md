# 13. Spec-Driven Development

*Stand v0.38.0* — erhoben auf dem Tag `v0.38.0` (= `1fb8aac`, 2026-10-20).
Umgesetzt in den Releases 0.35.0, 0.36.0 und 0.38.0; eine Version 0.37.0 gibt
es nicht, 0.38.0 bündelt die Roadmap-Stufen 0.37 (SPEC-003) und 0.38
(SPEC-004). Grundlagen im Repository: ADR-0027 (Status **Proposed**,
2026-10-19), `docs/roadmap/spec-driven-development.md` (Status *Entwurf*),
`specs/SPEC-001` bis `SPEC-005`, Migrationen V61–V65, `CHANGELOG.md`.

Dieses Kapitel beschreibt, wie die Fabrik eine Lücke schließt, die sie selbst
so benennt: Das Quality Gate prüfte, ob Code **gut** ist, nicht, ob er das
**Richtige** tut (ADR-0027, Kontext). Akzeptanzkriterien existierten nur als
Freitext in der Plan-Direktive und erreichten das Gate nie —
`erzeugeReviewRequest` setzte `ReviewRequest.acceptanceCriteria` fest auf
`null`.

```
Idee → Spec (Freigabe) → Plan/Tasks → Build (parallel) → Quality Gate gegen Spec → Abnahme
```

(Leitbild aus der Roadmap; *Du beschreibst. Die Fabrik baut. Du
genehmigst.*)

## 13.1 Die Produkt-Spec als Artefakt

Eine Produkt-Spec ist **Markdown mit YAML-Frontmatter** (ADR-0027 E1; Vorlage
`specs/_vorlage/spec.md`):

| Element | Inhalt |
|---|---|
| Frontmatter | `id` (`SPEC-<nnn>`), `titel`, `version`, `status`, `owner`, `contracts` (optional: verknüpfte Verträge der Contract Registry), `ersetzt` (optional) |
| Pflichtabschnitte | `## Ziel`, `## Nicht-Ziele`, `## Akzeptanzkriterien` |
| Optional | `## Kontext`, `## Randfälle`, `## Offene Fragen` |
| Ablage im Workspace | `specs/SPEC-<nnn>-<slug>/spec.md` |

**Akzeptanzkriterien tragen Pflicht-IDs** nach dem Schema `AC-<nnn>-<nn>`
(`<nnn>` = Spec-Nummer), eindeutig innerhalb der Spec, stabil über Versionen;
eine entfernte ID wird nicht wiederverwendet (ADR-0027 E4). Formulierung in
**EARS** empfohlen (*Wenn …, dann soll das System …*), Given/When/Then
erlaubt. Der Parser (`spec/domain/SpecParser.java`) prüft
**ID-Schema, Spec-Nummer im Präfix, Eindeutigkeit und Pflichtabschnitte —
nicht die Satzform**. HTML-Kommentare der Vorlage dürfen stehen bleiben.

Begründung im ADR: IDs statt Text machen Traceability prüfbar (Tests, Commits,
Trace) und Drift berechenbar; EARS ohne Zwang vermeidet eine
Formalismus-Hürde.

## 13.2 Datenbank führend, Datei als Projektion

- **Die Datenbank ist führend** (ADR-0027 E1). Jede Fassung ist eine
  unveränderliche `SpecVersion` mit SHA-256 über den Inhalt (`SpecHash`).
  Tabellen `spec` (Kopf je Projekt: Nummer, Slug, Titel, Mandant),
  `spec_version`, `spec_approval` (V61).
- Die Datei im Workspace ist **Projektion** der freigegebenen Fassung; ein
  neuerer Entwurf liegt als `spec.draft.md` daneben (`SpecService`,
  CHANGELOG 0.35.0).
- Änderungen, die ein Agent unter `specs/` vornimmt, werden nach dem Lauf als
  **neue DRAFT-Fassung** übernommen — **nie** als freigegebene.
- **Status** (`SpecStatus`): `DRAFT → APPROVED → SUPERSEDED`; je Spec
  höchstens eine `APPROVED` (im Service erzwungen). `SUPERSEDED` bleibt für
  Trace und Export erhalten.
- UI unter `/projects/{id}/specs` (`web/SpecController`): Liste, Anlegen aus
  der Vorlage, Bearbeiten (= neue Entwurfsfassung), Detail mit Fassungen und
  Freigabe-Historie, AC-Vergleich zweier Fassungen.
- Mandantentrennung: `tenant_id` an der Spec wird vom Projekt geerbt und
  zusätzlich zur Projektgrenze geprüft; fremde Mandanten sehen „nicht
  gefunden" (V61-Kommentar, CHANGELOG 0.35.0).

## 13.3 Freigabe als eigenes, auditiertes Gate

- Freigabe ab Rolle **MAINTAINER** (`requireCanApproveSpec` in
  `security/authz/AuthorizationService`), mit Validierung von
  Pflichtabschnitten, ID-Schema und Eindeutigkeit — ein Verstoß ist ein
  Validierungsfehler (400), kein Serverfehler.
- Die Freigabe löst die zuvor freigegebene Fassung ab, schreibt die Historie
  (wer, wann, welche Fassung, warum) nach `spec_approval` und das Ereignis
  `SPEC_APPROVED` mit `spec;version;hash` in die Audit-Hashkette. Weitere
  Ereignisse: `SPEC_CREATED`, `SPEC_VERSION_CREATED`.
- **Gleichzeitigkeitsschutz (0.36.0, AC-002-10):** Die Freigabe sperrt den
  Spec-Kopf in der Datenbank (`SELECT … FOR UPDATE`, `SpecRepository` mit
  `PESSIMISTIC_WRITE`, H2- und PostgreSQL-tauglich) und prüft die Invariante
  „höchstens eine `APPROVED` je Spec" nach; zwei gleichzeitige Freigaben
  hinterlassen genau eine freigegebene Fassung.

## 13.4 Freischaltung: Feature-Flag, Lizenz-Tier, Spec-Modus

Drei Schalter, alle standardmäßig aus bzw. neutral (ADR-0027 E5, E8):

| Schalter | Wirkung |
|---|---|
| Feature-Flag `softwarefabrik.spec.enabled` (`SOFTWAREFABRIK_SPEC_ENABLED`, Default `false`) | ohne Flag keine Spec-Oberfläche und exakt bisheriges Verhalten |
| `FeatureGate` (Port in `common`, Implementierung `license/LizenzFeatureGate`) | `erlaubt(Feature.SPEC)` = Flag an **und** (Lizenzsystem inaktiv **oder** Tier ≥ `PROFESSIONAL`). Gegated über den Tier, nicht über einen neuen JWT-Claim, damit bestehende Lizenzen gültig bleiben. Ohne aktives Lizenzsystem (`softwarefabrik.license.v1.enabled=false`) ist SDD freigeschaltet, sofern das Flag an ist |
| **Spec-Modus je Projekt** (`SpecModus`, Spalte `project_definition.spec_modus`, V61) | `AUS` (Default, heutiges Verhalten; Specs lassen sich trotzdem anlegen und freigeben) · `LEICHT` (Specs werden projiziert, Agenten-Änderungen als DRAFT übernommen, Conformance beratend) · `STRENG` (zusätzlich ist eine freigegebene Spec Startbedingung; Conformance blockierend) |

Der Spec-Modus ist auf der Spec-Übersicht wählbar und seit 0.36.0 im
Projekt-Assistenten (Schritt 5), wo das FeatureGate SDD freischaltet.

## 13.5 Spec im Backlog und im Gate (0.35.0)

- **Backlog-Bezug (V62):** Im Modus `LEICHT`/`STRENG` verlangt die
  Plan-Direktive je Plan die Zeilen `Spec: SPEC-<nnn>` und
  `AC: AC-<nnn>-<nn>, …` und zählt die verfügbaren Specs mit Freigabestand
  auf; der `PlanService` liest beides beim Indexieren
  (`plan_item.spec_id`, `plan_item.ac_ids`). Das Backlog zeigt Spec-Bezug und
  Hinweise (keine Spec, keine freigegebene Fassung, unbekannte AC-IDs).
- **STRENG-Ablehnung:** Im Modus `STRENG` lehnt die Aktivierung eines
  Plan-Items ohne freigegebene Spec oder mit unbekannten AC-IDs ab (400).
- **`ReviewRequest.acceptanceCriteria`** — vorher fest `null` — erhält
  erstmals die Kriterien (ID + Text) der freigegebenen Fassung zum umgesetzten
  Plan-Item, für **alle** Reviewer. Ohne Flag, Spec-Service oder Spec-Bezug
  bleibt alles wie bisher.

## 13.6 Traceability (0.36.0)

Nur wenn das FeatureGate SDD freischaltet **und** der Spec-Modus nicht `AUS`
ist (sonst exakt bisheriges Verhalten):

| Baustein | Umsetzung |
|---|---|
| Commit-Trailer | `Spec: SPEC-<nnn>` / `Implements: AC-…` am Fabrik-Commit und im PR-Body — auch wenn der Agent selbst keine Trailer gesetzt hat |
| Attestierung | `RUN_SPEC_GEBUNDEN` (`spec=…;version=N;hash=…;ac=…`) hält die zum Run-Start freigegebene Fassung in der Kette fest; ohne freigegebene Fassung (Modus `LEICHT`) startet der Run ohne Bindung, mit Hinweis im Run-Log |
| Warum-Trace | `WarumTrace.SpecBezug` (Spec, gebundene Version, Hash, AC-IDs) aus diesem Ereignis |
| Agentenkontext, vendor-neutral | **Objective-Kopf** mit den gebundenen Kriterien (ID + Text) direkt hinter den Guardrails — nachgewiesen für Claude, Codex und Gemini; Guardrails und ihr Hash bleiben unverändert. **Spec-Index in `AGENTS.md`** (ID, Titel, Status, Pfad) als markierter, idempotenter Zusatzabschnitt |
| Workflow-Task-Bindung (V63) | Ein Task deklariert Spec und AC-IDs; beim Start des Child Runs bindet die Fabrik die freigegebene Fassung (Version, Hash, AC-IDs; `WORKFLOW_TASK_SPEC_GEBUNDEN`). Alle Child Runs eines Workflows arbeiten gegen **dieselbe** Fassung, auch wenn die Spec zwischenzeitlich neu freigegeben wurde (Port `SpecBindungsQuelle` im `run`-Slice). Im Modus `STRENG` lehnt die Planfreigabe ab, wenn ein schreibender Task keinen Bezug auf eine freigegebene Fassung hat |
| Spiegelung als Vertrag | Bei Freigabe wird der AC-Block als Vertrag `SPEC-<nnn>-ac` der Art `ACCEPTANCE_CRITERIA` in der Contract Registry veröffentlicht (Ereignis `SpecFreigegeben`, Listener im `contract`-Slice); ein unveränderter Block erzeugt keine neue Fassung. Die Spec bleibt die einzige Stelle, an der AC bearbeitet werden (ADR-0027 E2) |

Architektur: Der Slice `spec` importiert nur `common` und `audit`
(ADR-0027 E3, am Tag nachgeprüft), damit `run`, `workflow`, `provenance`,
`export` und `kennzahlen` ihn nutzen können, ohne einen neuen Modulzyklus zu
erzeugen. Policy-Felder hält `policy` selbst.

## 13.7 Spec-Conformance-Reviewer (0.38.0, Roadmap-Stufe 0.37)

Reviewer `spec-conformance` (`review/reviewer/SpecConformanceReviewerAdapter`),
Kategorie `REQUIREMENTS`, **regelbasiert ohne Agent-CLI**
(`brauchtIsolationsnachweis=false`), nur für Runs mit Spec-Bezug (FeatureGate
frei **und** Spec-Modus ≠ `AUS`). Drei Prüfungen:

1. **AC-Abdeckung:** Jede gebundene AC-ID muss in mindestens einer
   Testdatei des Repositorys vorkommen (Testname, Dateiname, Annotation
   `@Spec("AC-…")` oder Kommentar). Fehlende Abdeckung wird mit der AC-ID
   gemeldet.
2. **Unbekannte AC-IDs:** Tests, die eine in der gebundenen Fassung nicht
   existierende AC-ID nennen, ergeben einen Hinweis.
3. **Ungedecktes Verhalten:** Geänderte Produktivdateien ohne AC-Zuordnung
   (weder `Implements:`-Trailer der Commits noch Pfad-Hinweis in der Spec)
   ergeben einen Hinweis mit begrenzter Pfadliste und Gesamtzahl.

**Schweregrade:** In `STRENG` ist `spec-conformance` Pflicht-Reviewer,
fehlende Abdeckung ist `CRITICAL`, und das Pipeline-Gate läuft blockierend
(der globale Gate-Modus wird angehoben, Hinweis im Run-Log). In `LEICHT`
sind alle Befunde beratend (fehlende Abdeckung `MEDIUM`, Hinweise
`LOW`/`INFO`).

**Konfigurierbare Muster** (`softwarefabrik.spec.conformance.*`,
`SpecConformanceProperties`) mit Vorgaben für Java, TypeScript/JavaScript und
Python: Testdatei-Globs (z. B. `**/src/test/**`, `**/*.spec.ts`,
`**/test_*.py`), AC-Referenz-Regex `(?i)AC[-_](\d{3})[-_](\d{2})(?!\d)`
(passt auch auf Methodennamen wie `ac_003_02_…`), Ausschlussmuster für
Nicht-Produktivcode (Markdown, `specs/`, `plans/`, `docs/`, Agenten-
Konfiguration). **Scan-Grenzen** wie bei der MCP-Workspace-Prüfung:
höchstens 5.000 Testdateien, Dateien bis 1 MiB, höchstens 20 Pfade im Befund.

Der Spec-Kontext (Spec, Fassung, Modus, gebundene und alle AC-IDs) wandert als
`ReviewRequest.metadata` (`review/domain/SpecKontext`) vom Orchestrator zum
Reviewer; `review` importiert `spec` nicht, der Architektur-Ratchet blieb
unverändert. Eine LLM-Bewertung „erfüllt der Diff AC x?" ist laut ADR-0027 E7
optional über die bestehenden Vendor-Reviewer vorgesehen, die
`acceptanceCriteria` seit 0.35.0 erhalten.

## 13.8 Spec-Drift (0.38.0, Roadmap-Stufe 0.37)

- **`SPEC_DRIFT`:** Die Freigabe einer neuen Fassung vergleicht sie auf
  AC-Ebene mit der vorher freigegebenen (neu / entfernt / geändert, Text je
  AC-ID) und schreibt das Ergebnis in die Kette
  (`spec=…;von=N;nach=M;neu=…;entfernt=…;geaendert=…`). Die erste Freigabe
  erzeugt keinen Vergleich. Ereignis `SpecDrift` nach dem Muster
  `VertragVeroeffentlicht`.
- **Veraltet-Markierung (V64):** Offene Plan-Items (nicht `DONE`/`REJECTED`),
  die an ein entferntes oder geändertes Kriterium gebunden sind — ein Item
  ohne AC-IDs gilt für alle Kriterien der Spec —, bekommen eine Begründung in
  `plan_item.veraltet_grund` (`PLAN_ITEM_VERALTET`) und erscheinen im Backlog
  als `VERALTET`. Die Aktivierung löscht die Markierung, weil der neue
  Build-Run die dann freigegebene Fassung bindet.
- **Workflow:** Gebundene, nicht-terminale Tasks wechseln wie bei einer
  Vertragsänderung nach `WAITING_FOR_REPLAN` (`WORKFLOW_TASK_VERALTET`); die
  Workflow-Ansicht nennt die Spec-Bindung unter „Veraltete Grundlage".
- **Strukturell prüfbare AC-Verträge:** Verträge der Art
  `ACCEPTANCE_CRITERIA` sind jetzt strukturell prüfbar (eigener kleiner
  AC-Block-Leser im `contract`-Slice): entferntes Kriterium = Bruch (`HIGH`),
  geänderter Text = Hinweis (`LOW`), neues Kriterium = `INFO`, Block ohne IDs
  = `MEDIUM`-Hinweis.
- **„Prüfbedürftig":** Nennt eine Spec im Frontmatter unter `contracts:`
  einen Vertrag, dessen aktuelle Fassung einen Bruch trägt, zeigt die
  Spec-Übersicht sie als „prüfbedürftig" mit den Befunden — abgeleitet beim
  Lesen über den Port `VertragsBefundQuelle` (implementiert in `contract`),
  ohne neue Kante `web → contract`.

## 13.9 Spec-Run (0.38.0)

**Run-Typ `SPEC`** (`RunKind.SPEC`), startbar aus der Spec-Oberfläche ab Rolle
DEVELOPER — aus einer Idee in Freitext (legt die Spec aus der Vorlage an) oder
zum Schärfen einer bestehenden Spec. Voraussetzung ist das FeatureGate; der
Spec-Modus darf `AUS` sein, weil ein Spec-Run ein expliziter Nutzerauftrag
ist, kein Nebeneffekt eines Build-Runs.

| Aspekt | Umsetzung |
|---|---|
| Direktive | nur `specs/` schreiben; Ziel, Nicht-Ziele, Akzeptanzkriterien mit IDs nach Vorlage, je Kriterium Negativ- und Grenzfälle, Abschnitt „Offene Fragen". Die Regel „Stelle keine Rückfragen" der `INSTRUCTIONS.md` wird **nur** für Spec-Runs ersetzt (`MarkdownGenerator.fuerSpecRun`) |
| Übernahme | ausschließlich aus `specs/` (`GitService.committeSpecsVerwirfRest`, Gegenstück zur Plan-Übernahme); alles andere wird verworfen und mit Pfadliste im Run-Log genannt. Jede geänderte Spec-Datei wird **immer DRAFT**, auch wenn der Parser sie beanstandet (Befunde an der Fassung und im Log). Kein Build, kein Branch, kein Merge |
| Modellwahl | Routing-Rolle `SPEC` (`RoutingRolle.SPEC`, Setting `run.routing.spec-model`): Override > Team > Rollen-Default (wie PLAN), attestiert als `RUN_MODELL_AUFGELOEST` mit `rolle=SPEC` |
| Vendor-Neutralität | Direktive und Ersatzregel laufen über Objective und `INSTRUCTIONS.md`; nachgewiesen mit Claude- und Codex-Adapter (Stub-Tests). Der Mock-Adapter ergänzt die Spec um einen Beispielabschnitt mit offener Frage, damit der Pfad ohne Vendor-CLI demonstrierbar ist |

**Rückfragen ohne interaktiven Dialog (headless):** Hinterlässt ein Spec-Run
Fragen im Abschnitt `## Offene Fragen` der neuen Fassung (nummeriert oder als
Aufzählung; `keine`/`–` zählen nicht), legt die Fabrik sie einzeln in
**`spec_frage`** ab (V65: Spec, Fassung, Run, Nummer, Frage, Status
`OFFEN`/`BEANTWORTET`/`NICHT_RELEVANT`, Antwort, beantwortet von/am,
Mandant; `SPEC_FRAGEN_ERFASST`) und beendet den Run in
**`WAITING_FOR_INPUT`** (`RUN_WAITING_FOR_INPUT`). Der Zustand ist
nicht-terminal und belegt **keinen** Kapazitäts- und Workspace-Slot
(`RunCapacityGuard.AKTIV`). Ohne Fragen endet der Run regulär `COMPLETED`.

- **Antworten** in der Spec-Oberfläche ab DEVELOPER, mandantengeprüft: je
  Frage beantworten oder „nicht relevant" (`SPEC_FRAGE_BEANTWORTET`,
  `SPEC_FRAGE_NICHT_RELEVANT`); beides ist endgültig.
- **Folge-Run:** Fortsetzen erst, wenn keine Frage mehr offen ist. Umgesetzt
  als **neuer, verknüpfter SPEC-Run** (`RUN_CREATED … vorgaenger=<id>`) mit
  den Antworten als Eingabe; der wartende Run wird `COMPLETED`
  (`RUN_FORTGESETZT`, `folgeRun=<id>`). Der Folge-Durchlauf erzeugt wieder
  eine neue DRAFT-Fassung.
- **Reverse-Spec:** nur für Projekte mit importiertem Repository
  (`importSource`; sonst Ablehnung mit Hinweis). Legt eine Spec
  „Reverse-Spec: <Projekt>" an und startet einen SPEC-Run mit Markerzeile
  `Modus: REVERSE-SPEC`; die Import-Direktive verlangt, aus Code und Tests
  abzuleiten, je AC die Quelle zu nennen, `## Annahmen`, `## Nicht-Ziele` und
  `## Offene Fragen` ausdrücklich zu füllen und nichts zu erfinden
  (`RUN_CREATED … modus=reverse`).

## 13.10 Restrisiken laut ADR-0027

- Die **Abdeckungsheuristik** erzeugt Falsch-Positive → zunächst advisory
  (Modus `LEICHT`), Muster konfigurierbar.
- **Generierte Specs** (Spec-Run, Reverse-Spec) können plausibel und falsch
  sein → nie automatisch freigegeben; die Freigabe bleibt menschlich.

*Einschränkungen (Stand v0.38.0):*

- ADR-0027 steht auf **Proposed**, die Roadmap auf *Entwurf*. Die
  Migrationsnummern der Roadmap weichen vom umgesetzten Stand ab
  (`spec_modus` kam mit V61, nicht V64; `spec_frage` ist V65, nicht V66) —
  maßgeblich sind die Migrationsdateien.
- Die Abdeckungsprüfung belegt, dass eine AC-ID in einer Testdatei
  **vorkommt**, nicht, dass der Test das Kriterium inhaltlich prüft.
- Alles ist opt-in; Projekte im Modus `AUS` und Installationen ohne Flag
  sehen keine Veränderung. Zu Nutzung im Betrieb liegen keine Messdaten vor.
- Die Specs SPEC-001 bis SPEC-005 der Fabrik selbst liegen im Repository mit
  Frontmatter-Status `DRAFT` (Dogfooding-Dateien; der Freigabestand in einer
  Fabrik-Datenbank ist daraus nicht ablesbar).

## 13.11 Geplant: Governance-Stufe 0.39 (SPEC-005, nicht umgesetzt)

`specs/SPEC-005-sdd-governance/spec.md` (Status `DRAFT`) beschreibt, was die
Roadmap-Stufe 0.39.0 bringen soll — **am Tag v0.38.0 nicht umgesetzt**:

- `PolicyInhalt.pflichtSpecFreigabe` und `minAcAbdeckung` (kanonisch nur bei
  Abweichung vom Default, alte Signaturen bleiben gültig); Durchsetzung bei
  Run-Start und Planfreigabe mit `RUN_POLICY_DENIED`; Mindestabdeckung als
  Gate-Blockade.
- Compliance-Profile `EU_AI_ACT` und `BAIT_MARISK_DORA` mit
  `pflichtSpecFreigabe = true`; `BASELINE` und `BSI_VS_NFD` unverändert.
- **Export-Schema 2.1** mit `nachweis.specVersionen` (Inhalt, Hash,
  Signatur, Key-ID, Freigabe); der Verifier prüft Fassungen und gleicht
  `RUN_SPEC_GEBUNDEN` ab; Kompatibilität 2.0 ↔ 2.1 in beide Richtungen.
- SDD-Kennzahlen (AC-Abdeckung, `SPEC_DRIFT`-Ereignisse, Anteil der Starts
  mit freigegebener Spec, Spec-Änderungen je Release) — auch für Einzel-Runs.
- Diese Governance-Funktionen nur für Tier `ENTERPRISE` (bzw. ohne aktives
  Lizenzsystem).

## 13.12 Einordnung für das Whitepaper

- Das Kapitel „Requirements-Agent" aus v1.3 (Kapitel 10) findet hier seine
  Umsetzung — nicht als eigener Agent, sondern als **versioniertes,
  freigegebenes Artefakt** mit IDs, an dem sich Plan, Build, Gate, Commit und
  Trace ausrichten. Der Spec-Run ist der Teil, in dem ein Agent an
  Anforderungen mitarbeitet; die Freigabe bleibt beim Menschen.
- Muster der Fabrik wiederholen sich: DB führend und Datei als Projektion (wie
  Prompt-Artefakte), unveränderliche Fassungen mit Hash (wie Verträge und
  Policies), Freigabe als attestierter Zustand (wie Run-Freigaben), die
  Rückfrage als **Zustand** `WAITING_FOR_INPUT` statt als Dialog, und
  Wiederverwendung statt Parallelwelt (Spiegelung des AC-Blocks in die
  Contract Registry).
- Ehrliche Grenze: Die Conformance-Prüfung ist eine deterministische
  Belegprüfung über IDs, keine semantische Verifikation der Anforderung.
