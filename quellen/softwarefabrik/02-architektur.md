# 2. Architektur

## 2.1 Leitprinzipien

1. **Modularer Monolith.** Ein Maven-Modul, ein Deployment-Artefakt, sauber
   geschnittene Pakete pro Bounded Context. Die Modulgrenze ist eine
   Paketgrenze, keine Netzwerkgrenze — und wird trotzdem maschinell erzwungen.
2. **Ports and Adapters pro Modul.** Jedes Modul trägt seine eigenen Schichten
   (`domain`, `application`, `web`, teils `infrastructure`). Externe Systeme
   (Coding-CLIs, Git, Maven, Trivy, GitHub-API) sitzen ausschließlich hinter
   Ports.
3. **Der Fachkern kennt keinen Vendor.** Weder die Use-Case- noch die
   Web-Schicht darf eine konkrete Adapter-Implementierung referenzieren. Das
   ist die technische Grundlage der Vendor-Neutralität und per ArchUnit-Test
   festgenagelt.
4. **Server-Rendered UI.** Thymeleaf + HTMX + SSE statt SPA. Begründung: Der
   Wert des Systems liegt in Prozessführung und Nachvollziehbarkeit; eine
   eigene Frontend-Toolchain hätte Komplexität ohne fachlichen Gewinn
   hinzugefügt.
5. **Konstruktor-Injection durchgängig**, keine Field-Injection. Ausnahme:
   optionale Querschnitts-Kollaborateure des Orchestrators werden per
   `@Autowired(required = false)`-Setter injiziert, damit ein Feature ohne den
   jeweiligen Slice lauffähig bleibt (siehe 2.5).
6. **Schulden werden gemessen, nicht verschwiegen.** Was heute nicht sauber
   ist, wird eingefroren und darf nicht wachsen (Abschnitt 2.6).

## 2.2 Schichtenmodell

```
io.softwarefabrik.app.<slice>.domain          Fachkern: Entitäten, Value Objects,
                                              Repository-Interfaces, Invarianten
io.softwarefabrik.app.<slice>.application     Use Cases, Transaktionsgrenzen,
                                              Audit, Orchestrierung
io.softwarefabrik.app.<slice>.web             Spring-MVC-Controller, View-DTOs,
                                              SSE-Endpunkte
io.softwarefabrik.app.<slice>.infrastructure  JPA-Implementierungen, externe
                                              Adapter, Scheduled Jobs
```

**Abhängigkeitsregeln**

| Von → Nach | erlaubt |
|---|---|
| `domain` → `application` | nein |
| `domain` → `web` | nein |
| `domain` → `execution`-Infrastruktur | nein |
| `application` → `web` | nein |
| `application`/`web` → konkreter Execution-Adapter | nein (nur der Port) |
| `web` → `JpaRepository` | nein (Ratchet: 13 Altfälle eingefroren) |

**Bewusste Pragmatik.** Domänenaggregat und JPA-Entität sind in V1 dieselbe
Klasse. Eine strikte „Domain kennt kein Framework"-Regel wäre daher
falsch-rot; sie ist deshalb *nicht* implementiert, und diese Entscheidung ist
im Code dokumentiert (`docs/architecture-conventions.md`,
`HexagonalRulesTest`-Javadoc). Für das Whitepaper ist das ein
diskussionswürdiger Punkt: DDD-Reinheit vs. Time-to-Value in einem System,
dessen eigentliche Komplexität woanders liegt.

## 2.3 Die 27 Slices

| Slice | Klassen | Aufgabe |
|---|---:|---|
| `run` | 44 | Run-Aggregat, Orchestrierung, Metriken, Analytics, Budgets, Meilenstein-Release, PR-Poller, Routine-Scheduler |
| `execution` | 42 | Port `ExecutionAdapter`, 10 Adapter, Sandbox-Modell, Capability-Routing, Modell-Katalog |
| `wizard` | 31 | Projekt-Assistent, 18 Templates, Toggles, Versions-Cache, Kostenschätzung |
| `license` | 24 | Lease-JWT-Client, Tier-Gate, Credential-Store |
| `security` | 20 | Spring Security, Rollenmodell, Autorisierung, SSO-OIDC, Nutzerverwaltung |
| `secrets` | 19 | AES-GCM-verschlüsselte Vendor-Keys, 6 Provider-Validatoren |
| `review` | 19 | Read-only-Reviewer (Port + 6 Implementierungen) |
| `web` | 17 | Querschnitt: Layout, Dashboard, Markdown-Rendering, Fehlerseiten |
| `policy` | 17 | Approval-Policies, Policy-as-Code, Compliance-Profile, Enforcement |
| `common` | 15 | IDs, Slugger, Clock, `RemoteUrlPolicy` (Host-Allowlist) |
| `sdlc` | 12 | Backlog (`plan_item` + Abhängigkeiten), Meilensteine, Routinen |
| `audit` | 12 | Append-only Audit-Log, Ed25519-Hashkette, Attestierung |
| `projectdefinition` | 10 | Projektspezifikation, Projekt-Memory, Import-Quelle |
| `settings` | 9 | Laufzeit-Settings mit Scope-Hierarchie |
| `qualitygate` | 9 | Aggregation der Reviewer-Befunde zum Verdict |
| `skills` | 8 | Versionierte, mandantengescopte Skill-/Plugin-Bibliothek |
| `git` | 8 | Git-Adapter: Branch, Diff, Checkpoint, Remote-Sync, PR |
| `validation` | 7 | Build-Gate (Maven/npm), SBOM-Erzeugung, Artefaktsignatur |
| `prompt` | 7 | Erzeugung und Versionierung der Markdown-Artefakte |
| `mandant` | 7 | Mandant, Budget, `TenantContext` |
| `team` | 6 | Geordnete Agententeams |
| `agent` | 6 | Agentenrollen, bevorzugtes Modell |
| `conductor` | 4 | Workspace-Vorbereitung: `.claude/`-Settings, Agent-Definitionen, Skills-Sync |
| `provenance` | 3 | Warum-Trace (Blatt-Slice, rein konsumierend) |
| `export` | 3 | Audit-Export-Bundle (Blatt-Slice) |
| `guardrails` | 1 | Vendor-neutrale Engineering-Guardrails als versionierte Ressource |
| `observability` | 1 | Prometheus-Registry, `/actuator/prometheus` |

**Lesart für das Whitepaper:** Die Größenverteilung ist selbst eine Aussage.
`run` und `execution` machen zusammen ein Viertel der Codebasis aus — die
Steuerung des nichtdeterministischen Teils ist der eigentliche Aufwand, nicht
die Fachlichkeit drumherum. Die Governance-Slices (`policy`, `audit`,
`mandant`, `provenance`, `export`, `skills`) sind dagegen klein: Governance
kostet vor allem *Entwurfsdisziplin*, nicht Code.

## 2.4 Slice-Topologie: Blatt-Slices als Zyklenvermeidung

Ein wiederkehrendes Entwurfsmuster, das sich für die Publikation lohnt:

Neue Querschnittsfähigkeiten werden konsequent als **Blatt-Slice** angelegt —
ein Paket, das nur konsumiert und von niemandem konsumiert wird. `provenance`
(Warum-Trace) korreliert Run-, Metrik-, Plan-, Freigabe- und Audit-Daten, ohne
dass irgendein anderer Slice davon abhängt. `export` aggregiert dasselbe zum
Bundle. `guardrails` liefert Text und Versions-Hash, kennt aber nichts.

Der Effekt ist strukturell: Eine Fähigkeit, die naturgemäß *überall*
hinschaut, würde als zentraler Service sofort Modulzyklen erzeugen. Als
Blatt-Slice erzeugt sie keinen einzigen. Dieselbe Regel wurde beim
Attestierungs-Anker angewandt (Sink-Kante in `audit` statt Rückkante aus
`audit` heraus).

## 2.5 Optionale Kollaborateure des Orchestrators

`RunOrchestrationService` ist die einzige Stelle mit Run-Statuswechseln und
damit der natürliche Anknüpfungspunkt für Querschnitts-Features. Damit die
Pflichtabhängigkeiten nicht explodieren, werden diese Kollaborateure als
optionale Setter injiziert:

`MemoryService`, `PlanService`, `MandantKostenService`, `PolicyAsCodeService`,
`PolicyEnforcementService`, `SecretsResolver`, `PullRequestClient`,
`QualityGateService`, `SettingService`, `GuardrailsService`, `SbomService`,
`ModelRoutingService`, `ApplicationEventPublisher`.

Jeder ist einzeln abschaltbar; fehlt er, läuft der Run ohne dieses Feature
weiter statt zu scheitern. Das ist zugleich der Mechanismus, mit dem
Governance-Funktionen konfigurativ zu- und abgeschaltet werden — relevant für
Kunden, die nur einen Teil der Compliance-Kette brauchen.

## 2.6 Maschinelle Architektur-Durchsetzung

Drei ArchUnit-Testklassen, alle Teil des normalen Builds:

**`LayeringRulesTest`** — fünf harte Regeln:
- `domain` hängt nicht von `web` ab
- `domain` hängt nicht von der Execution-Infrastruktur ab (sonst wären
  Fachregeln ohne CLI-Mock nicht testbar)
- `application` hängt nicht von `web` ab
- `@Controller`/`@RestController` ausschließlich in `..web..`
- kein `JpaRepository` in `..web..` oder `..application..`

**`HexagonalRulesTest`** — drei harte Regeln:
- `domain` hängt nicht von `application` ab (Onion-Kern)
- `application` kennt keine konkrete `ExecutionAdapter`-Implementierung
- `web` kennt keine konkrete `ExecutionAdapter`-Implementierung

Die letzten beiden sind der Kern der Vendor-Neutralität: Es ist technisch
unmöglich, versehentlich einen Service an Claude, Codex oder Gemini zu koppeln
— der Build bricht.

**`ArchitectureDebtRatchetTest`** — der interessanteste Teil: zwei Regeln, die
heute *nicht* eingehalten werden (Modulzyklen; `web → JpaRepository`), werden
mit ArchUnits `FreezingArchRule` als versionierte Baseline eingefroren
(`src/test/resources/archunit-store/`). Wirkung:

- ein **neuer** Zyklus oder Direktzugriff bricht den Build,
- ein **behobener** Verstoß verschwindet automatisch aus der Baseline,
- die Schuld ist gezählt und sichtbar statt implizit.

### Der Ratchet-Fallstrick (bemerkenswert für die Publikation)

Der Freeze speichert eine *Teilmenge* der elementaren Modulzyklen
(Kappungsgrenze `cycles.maxNumberOfCyclesToDetect`, Default 100). Solange die
tatsächliche Zyklenzahl unter der Grenze liegt, ist die Enumeration
vollständig und deterministisch — lokaler und CI-Lauf stimmen überein.
Überschreitet eine neue Cross-Slice-Kante die Grenze, wird die Enumeration
abgeschnitten und *reihenfolgeabhängig*: Der Test wird lokal grün und in CI rot,
ohne dass sich der Code inhaltlich unterscheidet.

Das ist ein reales, nicht offensichtliches Betriebsrisiko automatisierter
Architekturmetriken und ein guter Beleg für die These, dass Guardrails selbst
gewartet werden müssen. Die daraus abgeleitete Arbeitsregel im Projekt lautet:
Neue Klassen bevorzugt in Blatt-Slices legen; ein Refreeze nur, wenn die
Gesamtzyklenzahl unter der Kappungsgrenze bleibt.

## 2.7 Architekturentscheidungen (ADRs im Repo)

| ADR | Entscheidung |
|---|---|
| 0001 | Spring Boot + Thymeleaf statt SPA |
| 0002 | PostgreSQL + Flyway, keine automatische Schema-Generierung |
| 0003 | Claude-Code-Adapter (später zum generischen `ExecutionAdapter`-Vertrag verallgemeinert) |
| 0004 | Lizenzierung über Keycloak + Lease-JWT |
| 0005 | Ed25519 als einheitliches Lizenz-/Signaturformat |
| 0006 | Dual-Location-Persistenz der Credentials |
| 0007 | Feature-Flags im JWT-Payload |
| 0008 | Lizenzserver-URL im JWT |
| 0009 | Air-Gap über `refresh-required=false` |
| 0010 | Java 25 + Spring Boot 4 |
| 0011 | Agent-Sandbox (Variante B: ephemere Container, seit v0.7.0 *Accepted*) |
| 0013 | Konzeptübernahme aus claudecode4j |

Die ADRs von v1.3 des Whitepapers (Multi-Agent vs. Single-Agent,
Workspace-Isolation via Git-Worktrees, Guardrail-Pipeline als Pflicht-Gate,
Git-basierte Orchestrierung) finden sich hier teils wieder, teils bewusst
anders entschieden — der Abgleich steht in `11-mapping-whitepaper-v13.md`.
