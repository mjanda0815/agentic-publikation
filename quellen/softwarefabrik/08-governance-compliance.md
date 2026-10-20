# 8. Governance, Compliance und Nachweisführung

Dieses Kapitel enthält den Teil, den das Whitepaper v1.3 konzeptionell nur
streift und der in regulierten Umgebungen über Einsatz oder Nicht-Einsatz
entscheidet: **Wie beweist man hinterher, was ein Agent unter welchen Regeln
getan hat?**

## 8.1 Mandantenisolation

- Ein Mandant je Nutzer (`app_user.tenant_id`, V27); `null` bedeutet
  Einzelmandantenbetrieb.
- `TenantContext` trägt den Mandanten durch den Request.
- **Isolation an der Projektgrenze:** Projekte, Runs und alle abgeleiteten
  Aggregate sind mandantengescopt (V35 verschärft das). Ein IDOR-Versuch über
  fremde IDs scheitert; das ist als Test festgeschrieben
  (`MandantIsolationTest`).
- **Bewusste Entscheidung:** `ADMIN` ist *kein* Super-Admin. Auch ein
  Administrator bleibt für **Daten** mandantengescopt; isolationsfrei sind nur
  Kontenverwaltung und Projektzuweisung. Damit kann eine Administrationsrolle
  Betrieb führen, ohne Einblick in fremde Projektinhalte zu haben.
- *Einschränkung:* Die Isolation ist an den interaktiven Pfaden verankert; die
  asynchrone Engine löst den Mandanten über einen eigenen Resolver auf.

## 8.2 Rollenmodell

`Rolle`: `VIEWER < DEVELOPER < MAINTAINER < OWNER < ADMIN`

| Fähigkeit | ab Rolle |
|---|---|
| lesen | VIEWER |
| Runs ausführen | DEVELOPER |
| freigeben | MAINTAINER |
| Integrationen/Secrets verwalten | MAINTAINER |
| Mandanten-Administration | OWNER |

Implementiert als `RoleBasedAuthorizationService` (`@Primary`), mit einer
permissiven Variante für Betriebsarten ohne RBAC. **Segregation of Duties** ist
zuschaltbar: Der Auslöser eines Runs darf ihn nicht selbst freigeben.

Ergänzend: optionales **SSO über OIDC** mit JIT-Provisioning (neue Nutzer
landen als `VIEWER` ohne Mandanten — bewusst restriktiv, damit ein
SSO-Anschluss nie versehentlich Zugriff erweitert).

*Einschränkung, behoben in 0.34.0 (CHANGELOG):* Die Workflow-Ebene
(`/workflows/**`, `/vertraege/**`, hinter Feature-Flag) ließ bis dahin jede
angemeldete Rolle jede Aktion ausführen — auch auf Workflows und Verträgen
fremder Mandanten, die ID genügte. Seither: Lesen für alle Rollen, Ändern/
Starten/Umplanen ab DEVELOPER, Planfreigabe, Integration und
Konfliktentscheidung ab MAINTAINER, fremde Mandanten sehen „nicht gefunden".
Spec-Freigaben verlangen MAINTAINER+ (`requireCanApproveSpec`, seit 0.35.0).

## 8.3 Policy-as-Code

Regeln sind kein Konfigurationszustand, sondern ein **versioniertes,
signiertes Dokument** (`policy_document`, V30).

Der kanonische Inhalt (`PolicyInhalt`) ist bewusst minimal und dadurch
prüfbar:

```java
record PolicyInhalt(
    List<String> erlaubteAdapter,        // Vendor-Beschränkung
    String       gateModus,              // off | advisory | blocking
    List<String> pflichtFreigabePhasen,  // z. B. EXECUTION, VALIDATION
    boolean      pflichtAttestierung,    // Signaturpflicht
    List<String> erlaubtePlugins,        // seit 0.31.0: Plugins standardmäßig gesperrt
    boolean      mcpStandardverbot,      // seit 0.31.0: Isolationsnachweis-Pflicht
    List<McpServerFreigabe> erlaubteMcpServer) // seit 0.34.0: Gateway-Freigaben mit Pins
```

*Stand v0.38.0* (`policy/domain/PolicyInhalt.java`). Die drei neuen Felder
erscheinen in der kanonischen, signierten Form nur, wenn sie vom Default
abweichen — **bestehende Policy-Signaturen bleiben gültig**. Über mehrere
wirksame Policies (global und Mandant) gilt für `erlaubtePlugins` und
`erlaubteMcpServer` die Schnittmenge, für `mcpStandardverbot` das Strengere
(eine Mandanten-Policy kann es ein-, nicht ausschalten). Ein Feld
`pflichtSpecFreigabe` ist für 0.39 geplant (SPEC-005), am Tag v0.38.0 nicht
vorhanden.

Eigenschaften:

- **Genau eine aktive Version** je Mandant — erzwungen über partiellen
  Unique-Index in PostgreSQL plus Service-Logik.
- **Ed25519-signiert**; die Signatur deckt den kanonischen Text.
- **Kanonische Serialisierung** (`kanonisch()` / `parse()`) statt JSON-Dump:
  nur so ist die Signatur über einen Datenbank-Roundtrip stabil.
- **Durchsetzung im Orchestrator** an zwei Zeitpunkten — bei Anlage und
  erneut bei Ausführung (siehe `05-run-pipeline.md`, 5.4).

Verstöße erzeugen `RUN_POLICY_DENIED`, erfolgreiche Anwendungen
`RUN_POLICY_ANGEWENDET` mit der real geltenden Policy-Version.

## 8.4 Compliance-Profile

Vier Profile übersetzen Regulatorik in erzwingbare Policy-Vorlagen. Das ist
der Teil, der sich am unmittelbarsten für die Publikation eignet, weil er die
Brücke von Norm zu Code explizit macht:

| Profil | Gate | Pflichtfreigaben | Attestierung | MCP-Standardverbot (seit 0.31.0) | Regulatorischer Bezug |
|---|---|---|---|---|---|
| **Baseline** | advisory | — | nein | nein | kein reguliertes Umfeld |
| **EU AI Act** | blocking | `EXECUTION` | ja | nein | VO (EU) 2024/1689, Art. 12 (Aufzeichnungspflichten), Art. 14 (menschliche Aufsicht) |
| **BAIT / MaRisk / DORA** | blocking | `EXECUTION`, `VALIDATION` | ja | **ja** | BaFin BAIT/MaRisk; DORA (EU) 2022/2554 — IKT-Risiko, Drittparteienrisiko, Nachweisführung |
| **BSI-Grundschutz / VS-NfD** | blocking | `EXECUTION`, `VALIDATION` | ja | **ja** | BSI IT-Grundschutz; VS-NfD. Zusätzlich: für Verschlusssachen ausschließlich On-Prem-/souveräner Betrieb — die erlaubten Adapter sind projektspezifisch auf lokale Backends zu beschränken |

*Verhaltensänderung seit 0.31.0:* In `BAIT_MARISK_DORA` und `BSI_VS_NFD` ist
nach dem Update zunächst nur der Mock-Adapter nutzbar; Agent-CLI-Adapter und
-Reviewer laufen erst, wenn ein Admin den Canary für die installierte
CLI-Version erfolgreich ausgeführt hat (8.11). Das gilt auch für Bedrock,
Vertex, Azure OpenAI und local-llm, weil sie intern `aider` starten —
gewollt fail-closed. *Einschränkung:* Die Seite „Compliance-Profile" ließ sich wegen eines
Template-Fehlers nicht öffnen; behoben in 0.36.0 (`ComplianceProfilWebTest`;
seit wann der Fehler bestand, nennt der CHANGELOG nicht).

Das Anwenden eines Profils veröffentlicht eine neue signierte Policy-Version
und erzeugt das Ereignis `COMPLIANCE_PROFILE_APPLIED`.

**Ehrliche Einordnung für das Whitepaper:** Die Profile setzen die *technisch
erzwingbaren* Anteile der jeweiligen Regelwerke durch — Aufzeichnung,
menschliche Aufsicht, Nachweisführung, Vendor-Beschränkung. Sie ersetzen keine
Rechtsberatung und decken keine organisatorischen Pflichten ab. Regionale
Datenhaltung wird bewusst nicht hier, sondern in der Gateway-Konfiguration
durchgesetzt.

## 8.5 Signierte Audit-Hashkette

Der Kern der Nachweisfähigkeit (`audit`, V29 + V33):

Jedes `AuditEvent` trägt:

| Feld | Zweck |
|---|---|
| `seq` | lückenlose Sequenz, `UNIQUE` |
| `prev_hash` | Hash des Vorgängers |
| `entry_hash` | Hash über den eigenen Inhalt inkl. `prev_hash` |
| `signature` | Ed25519-Signatur |
| `key_id` | verwendeter Schlüssel |

`AuditService.erfasse` verkettet und signiert unter einem Monitor
(`synchronized`), mit auf Millisekunden trunkiertem Zeitstempel — sonst wäre
die Signatur nach dem Datenbank-Roundtrip nicht byte-stabil.

`AttestierungService.verifiziereKette` unterscheidet drei Fehlerbilder:

- `HASH_MISMATCH` — ein Eintrag wurde nachträglich verändert,
- `CHAIN_BREAK` — ein Eintrag wurde entfernt oder eingefügt,
- `BAD_SIGNATURE` — der Eintrag stammt nicht vom erwarteten Schlüssel.

Altbestand ohne Signatur wird transparent als solcher ausgewiesen, statt die
Prüfung scheitern zu lassen. `audit_chain_checkpoint` (V33) verankert
Kettenzustände periodisch.

**Schlüsselbetrieb, konfigurationsgegatet:** in Entwicklung/Test ephemer; in
Container-/Produktionsprofilen ist „aktiviert ohne Schlüssel" ein
**Startfehler**. Wer ohne Signatur betreiben will, muss das explizit
deklarieren (`enabled=false`) — Sicherheit durch bewusste Entscheidung statt
durch Vergessen.

### Attestierte Ereignistypen (Auswahl)

`RUN_CREATED`, `RUN_READY`, `RUN_STARTED`, `RUN_PAUSED`, `RUN_RESUMED`,
`RUN_CANCELLED`, `RUN_MODELL_AUFGELOEST`, `RUN_POLICY_ANGEWENDET`,
`RUN_POLICY_DENIED`, `RUN_GUARDRAILS_ANGEWENDET`, `QUALITY_GATE_EVALUATED`,
`SBOM_ERZEUGT`, `ARTEFAKT_SIGNIERT`, `POLICY_AS_CODE_PUBLISHED`,
`POLICY_UPDATED`, `COMPLIANCE_PROFILE_APPLIED`, `APPROVAL_*`

Hinzugekommen bis v0.38.0 (Auswahl, Namen im Code nachgeprüft):

- MCP-Governance: `MCP_KONFIG_BASELINE`, `MCP_KONFIG_VORGEFUNDEN`,
  `MCP_KONFIG_AGENT_GESCHRIEBEN`, `AGENT_KONFIG_AUSFUEHRBAR_VORGEFUNDEN`,
  `ISOLATIONSNACHWEIS_ERSTELLT`, `MCP_SERVER_VERMESSEN`,
  `MCP_SERVER_VERBUNDEN`, `MCP_TOOL_AUFRUF`, `MCP_PIN_ABWEICHUNG`,
  `MCP_RUN_BEENDET`
- Spec-Driven Development: `SPEC_CREATED`, `SPEC_VERSION_CREATED`,
  `SPEC_APPROVED`, `SPEC_DRIFT`, `RUN_SPEC_GEBUNDEN`,
  `WORKFLOW_TASK_SPEC_GEBUNDEN`, `PLAN_ITEM_VERALTET`,
  `WORKFLOW_TASK_VERALTET`, `SPEC_FRAGEN_ERFASST`,
  `SPEC_FRAGE_BEANTWORTET`, `SPEC_FRAGE_NICHT_RELEVANT`,
  `RUN_WAITING_FOR_INPUT`, `RUN_FORTGESETZT`

Die Liste selbst ist die Antwort auf die Frage, was in einem agentischen
System nachweispflichtig ist: *nicht* jeder Tastendruck, sondern jede
Entscheidung, die den Handlungsspielraum des Agenten festgelegt hat.

## 8.6 Warum-Trace

`provenance/WarumTraceService` beantwortet für einen einzelnen Run die Frage
„warum ist dieser Code so entstanden?", indem er korreliert:

- Run und Metriken (Modell, Kosten, Dauer),
- Plan-Herkunft (`PlanItem.sourceRunId` → `buildRunId`),
- Freigabeentscheidungen und deren Akteure,
- verwendete Prompts/Artefakte,
- die attestierten Audit-Ereignisse.

Zwei Lücken wurden dafür eigens geschlossen: Modellauflösung und
Gate-Ergebnis waren vorher nicht attestiert und sind es seither
(`RUN_MODELL_AUFGELOEST`, `QUALITY_GATE_EVALUATED`). Der Trace liegt unter
`/runs/{id}/trace` und ist mandantengegated.

Ergänzungen bis v0.38.0: Herkunft der Modellwahl (`quelle=…` in
`RUN_MODELL_AUFGELOEST`, 0.33.0); Abo-Kosten als „Schätzung (API-Tarif),
nicht abgerechnet" (0.33.0); die CLI-eigene Kostenschätzung als Gegenprobe
(0.34.0); der **Spec-Bezug** (`WarumTrace.SpecBezug`: Spec, gebundene
Version, Hash, AC-IDs aus `RUN_SPEC_GEBUNDEN`, 0.36.0).

## 8.7 Audit-Export

`export/AuditExportService` erzeugt ein prüffähiges Bundle je Projekt oder
Run — als JSON und HTML — bestehend aus Warum-Trace, Kettenverifikation,
geltendem Policy-Stand und dem öffentlichen Schlüssel.

Ein technisches Detail mit Praxiswert: Das Bundle enthält ausschließlich
Strings, Primitive und UUIDs (Zeitstempel als ISO-8601-Text). Damit ist die
Serialisierung deterministisch und unabhängig von Jackson-Datumsmodulen — ein
Bundle, das je nach Bibliotheksversion anders aussieht, taugt nicht als
Nachweis.

### 8.7.1 Export-Schema 2.0 und Offline-Verifier (seit 0.32.0, ADR-0023)

Schema 1.0 war für eine **unabhängige** Prüfung nicht ausreichend: nicht
nachrechenbar (je Ereignis nur Kurzhash und das Urteil `intakt` der Fabrik
über sich selbst), nicht vollständigkeitsbeweisend (die Kette ist global,
ein Projekt-Export enthält nur die eigenen Einträge), mit der *aktuell*
aktiven statt der im Run angewandten Policy und mit einem Schlüssel aus
derselben Datei als Vertrauensanker (ADR-0023, Kontext).

**Schema 2.0** ergänzt additiv einen Abschnitt `nachweis`:

- **volle Einträge** im Geltungsbereich (alle Felder der kanonischen Form
  plus `prevHash`, `entryHash`, `signature`, `keyId`),
- **Hash-Stellvertreter ohne Inhalt** (`seq`, Hashes, Signatur, Key-ID) für
  alle anderen Einträge bis zum Ketten-Kopf — so ist lückenlose Verkettung
  beweisbar, ohne fremde Mandanten offenzulegen (rund 250 Byte je fremdem
  Eintrag),
- den **signierten Ketten-Kopf** zum Exportzeitpunkt,
- die **im Run angewandten Policy-Versionen** (per `RUN_POLICY_ANGEWENDET`),
- **signierte Run-Manifeste** (je Run die zugehörigen `seq`),
- den Schlüsselring mit SHA-256-Fingerabdruck je Key-ID.

**Offline-Verifier** (Modul `verifier/`, `softwarefabrik-verifier.jar`):
eigenständig, **nur JDK** (SHA-256, Ed25519 aus `java.security`, eigener
minimaler JSON-Leser, kein Fabrik-Code), rund 1.000 Zeilen — klein genug, um
ihn zu lesen. Aufruf
`java -jar softwarefabrik-verifier.jar export.json --schluessel <fingerabdruck>`.
Vertrauensanker ist der von außen übergebene Fingerabdruck (angezeigt auf
`/attestierung`, vom Betreiber auf einem zweiten Weg zu veröffentlichen).
Prüfschritte: Schlüssel, Einträge (Hash neu berechnen, Signatur), Stellvertreter,
Verkettung, Kopf, Policy, Run-Nachweis (`docs/verifier.md`). Exit-Codes:
**0** alles bewiesen und verankert · **1** Verletzung · **2** keine
Verletzung, aber nicht alles beweisbar (z. B. ohne Anker, unsignierte
Einträge) — ohne Anker nie 0. Optional `--bekannt <seq>:<entryHash>` gegen
das Zurücksetzen des Kopfes. Der Build ist reproduzierbar; die geprüfte
Fabrik-Installation liefert das JAR bewusst **nicht** aus. Kompatibilität
prüft ein App-Test, der das gebaute JAR als eigenen Prozess gegen echte und
gezielt manipulierte Exporte aufruft (eigene CI-Stufe).

*Einschränkung:* Bewiesen wird die Unversehrtheit ab dem ersten exportierten
Eintrag bis zum Kopf zum Exportzeitpunkt. Wer vor dem Export
Datenbankzugriff hat, kann die neuesten Einträge löschen und den Kopf auf
einen älteren gültig signierten Eintrag zurücksetzen — das zeigt nur ein
Abgleich mit bekannten Kettenständen. Export-Schema 2.1 mit
Spec-Versionen ist für 0.39 geplant (SPEC-005), am Tag v0.38.0 nicht
umgesetzt.

## 8.8 Supply-Chain-Nachweis

| Baustein | Umsetzung |
|---|---|
| SBOM je Build | `SbomService` (Trivy Filesystem-Scan), `sbom_artifact` (V31), Ereignis `SBOM_ERZEUGT`; standardmäßig `off`, graceful bei fehlendem Trivy |
| Signierte Artefakte | Ed25519-Signatur über den SBOM-Digest (V32), Ereignis `ARTEFAKT_SIGNIERT` |
| Abhängigkeitsprüfung | `DependencyScanReviewerAdapter` (Trivy vuln + license) als blockierender Reviewer im Quality Gate |
| CI-seitig | OWASP Dependency-Check, Trivy-Image-Scan, gitleaks-Secret-Scan, CycloneDX-SBOM als Artefakt |

*Stand v0.38.0:* Die mit 0.20.0 befristet akzeptierte Laufzeit-CVE entfiel
mit 0.31.0 durch ein Tomcat-Update ersatzlos; OWASP- und Trivy-Scan sind
seither ohne Suppression grün (CHANGELOG 0.31.0). Seit 0.33.0 stehen drei
Go-CVEs im `pebble`-Binary des Temurin-Basis-Images in `.trivyignore`
(laut CHANGELOG nie ausgeführt).

## 8.9 Skill-Bibliothek als Governance-Objekt

Die Skill-/Plugin-Bibliothek (`skills`, V38) ist bewusst kein
Konfigurationsordner:

- Einträge sind **mandantengescopt** und **versioniert**
  (`skill_catalog_entry` + `skill_version`),
- Herkunft ist typisiert: `CATALOG` (kuratiert), `INSTALLED` (übernommen),
  `FORKED` (angepasst),
- Arten: `SKILL` und `PLUGIN`.
- Seit 0.31.0 schaltet der Conductor nur noch Plugins frei, die **jede**
  wirksame Policy in `erlaubtePlugins` freigibt; ohne Policy ist die Liste
  leer (ADR-0017 E3).

Damit ist beantwortbar, welche Erweiterung in welcher Version zum Zeitpunkt
eines Laufs im Kontext des Agenten war — die Frage, an der sonst jede
Reproduzierbarkeitsdiskussion scheitert.

## 8.10 Vendor-neutrale Engineering-Guardrails

Der `guardrails`-Slice hält die Verhaltens-Policy für Agenten als eine
versionierte Classpath-Ressource; die Versions-ID ist ein SHA-256-Kurzhash des
normalisierten Inhalts (`sha256:…`), also deterministisch und ohne Datenbank.

Bei jedem Run wird sie ins Repository projiziert: als `AGENTS.md`
(werkzeugübergreifender De-facto-Standard) mit einer minimalen `CLAUDE.md`,
die darauf verweist. **Eine Quelle, mehrere Projektionen** — statt pro
Werkzeug eine gepflegte Kopie, die auseinanderläuft. Das Ereignis
`RUN_GUARDRAILS_ANGEWENDET` hält fest, welche Guardrails-Version gewirkt hat.

## 8.11 MCP-Governance (Stand v0.38.0; 0.31.0–0.34.0)

Das Whitepaper v1.3 behandelt MCP als Werkzeuganbindung (Kapitel 18). Die
Fabrik hat MCP zuerst als **Angriffsfläche** behandelt und erst danach
geöffnet. Grundlage: ADR-0016 (Ist-Analyse, drei Lecks: Host-`HOME`,
Plugin-Freischaltung, MCP-Konfiguration im Workspace), ADR-0017, ADR-0022,
ADR-0018.

**Phase 1 — MCP-Nullzustand für alle Agentenläufe (0.31.0, ADR-0017).**
Kein Agentenlauf erreicht einen MCP-Server, den die Fabrik nicht ausdrücklich
projiziert hat.

- **Ephemeres HOME je CLI-Aufruf** (`execution/sandbox/AgentHome`; Claude
  Code, Codex, Gemini, Aider, Kimi — Ausführung und Review): nur die
  Auth-Dateien als Kopie und eine neutrale `.gitconfig`; nicht hinein kommen
  `~/.claude.json`, `settings.json`, Hooks, Plugins, `config.toml`,
  `mcp.json`, SSH-, Git- und Cloud-Credentials.
- **Claude Code** zusätzlich mit `--strict-mcp-config`, leerer
  `--mcp-config=<datei>` und `ENABLE_CLAUDEAI_MCP_SERVERS=false`; seit 0.34.0
  außerdem `--setting-sources=user` (keine Projekt-Settings, kein
  `.mcp.json`) und `--settings` mit `{"disableAllHooks":true}` — Anlass: Im
  `--print`-Modus führte Claude Code Hooks, `env`-Block und Helper aus
  `.claude/settings.json` eines importierten Repos ohne Trust-Dialog aus
  (ADR-0017, Nachtrag 2026-10-19). Laut ADR-0017 ist das Defense in Depth,
  kein Isolationsnachweis.
- **Workspace-Prüfung** (`mcp/McpWorkspacePruefung`): Vor der ersten
  Ausführung eines Runs wird der Stand von `.mcp.json`, `.claude/`, `.codex/`,
  `.gemini/`, `.kimi-code/` als `MCP_KONFIG_BASELINE` (Pfad → SHA-256) in die
  Kette geschrieben — außerhalb des Workspace, manipulationssicher, über
  Neustarts und Freigabe-Pausen hinweg. Vorgefundene Server-Definitionen
  ergeben `MCP_KONFIG_VORGEFUNDEN`, jede Abweichung nach einer Ausführung
  `MCP_KONFIG_AGENT_GESCHRIEBEN`, ausführbare Konfiguration im Bestand (Hooks,
  `env`, `apiKeyHelper` u. a., `allowed-tools` in Skill-Frontmatter)
  `AGENT_KONFIG_AUSFUEHRBAR_VORGEFUNDEN` (seit 0.34.0). Unter
  MCP-Standardverbot ist eine vom Agenten geschriebene Konfiguration ein
  blockierendes `SECURITY`-Finding (CRITICAL).
- **Adapter-Gating:** Unter `mcpStandardverbot` wird ein Run mit einem
  Adapter ohne bestandenen Isolationsnachweis für die *installierte*
  CLI-Version abgelehnt (`RUN_POLICY_DENIED` mit Adapter und Version) — bei
  Anlage und unmittelbar vor der Ausführung. Für Reviewer siehe
  `07-review-qualitygate.md`, 7.4.
- Schnitt: Senken-Slice `mcp` (nur `audit`), Port `McpServerPolicy`
  implementiert in `policy` — keine neue Kante in die Zyklen-SCC.

**Canary-Harness (0.31.0, ADR-0022).** Admin-Funktion
`/admin/isolationsnachweise` (Rolle ADMIN), läuft in der Fabrik selbst auf
dem Produktivpfad (Host, echter Adapter-Code, installierte CLI, echter
Login). Je Adapter/Reviewer und CLI-Version zwei Läufe gegen eine
**simulierte** Host-Umgebung mit Marker-Servern (die echte Konfiguration des
Betriebsnutzers bleibt unberührt): ein **Kontroll-Lauf** ohne Nullzustand,
in dem die Marker der erwarteten Quellen erscheinen *müssen*, und ein
**Nullzustand-Lauf** über den echten Adapter-Pfad, der *keinen* Marker
zeigen darf. Urteil `NICHT_BESTANDEN` (Marker im Nullzustand oder
systemweite Server-Konfiguration), `UNGUELTIG` (Kontrolle gescheitert,
erwartete Quelle wirkungslos, CLI-Version gewechselt) oder `BESTANDEN`.
Ergebnis in Tabelle `isolationsnachweis` (V56), Ed25519-signiert mit dem
Attestierungsschlüssel, als `ISOLATIONSNACHWEIS_ERSTELLT` in der Kette; das
Register erkennt nur gültig signierte Einträge an (ohne aktive Signatur
keiner). Ein CLI-Update braucht kein Fabrik-Release, nur einen neuen
Canary-Lauf. Kosten: zwei kurze Modellaufrufe je CLI-Version.
*Einschränkung:* System-/Managed-Ebene und claude.ai-Connectors sind nicht
per Marker nachweisbar; für CLIs ohne MCP-Client (Aider und die darauf
aufsetzenden Gateway-/local-llm-Adapter) genügt ein erfolgreicher
Kontroll-Lauf; Gemini-/Kimi-Formate sind nicht in jeder Version belegt.

**Phase 2 — MCP-Gateway (0.34.0, ADR-0018, opt-in).** Eigener Prozess
(Modul `gateway/`, JDK-HTTP-Server und -Client plus Jackson, kein
Spring-Kontext, **ohne** Signaturschlüssel), Anbindung über Slice
`mcpgateway`. Betriebsarten `aus` (Standard, keine Verhaltensänderung),
`lokal` (von der Fabrik auf `127.0.0.1` gestartet, Verwaltungsgeheimnis per
stdin) und `extern` (eigener Dienst) — `softwarefabrik.mcp-gateway.modus`,
`mcpgateway/McpGatewayEinstellungen`.

- **Nur Claude Code** (Ausführung), weil nur dort der Nullzustand per Canary
  nachgewiesen ist; Reviewer und andere Adapter bleiben im Nullzustand.
- **Nur lesende Tools:** sichtbar und aufrufbar sind ausschließlich Tools mit
  `annotations.readOnlyHint = true` und ohne `destructiveHint = true`.
- **Freigabe über Policy-as-Code** (`erlaubteMcpServer`) mit Pins
  `serverDigest` (SHA-256 über Befehl+Argumente bzw. URL) und `toolsDigest`
  (SHA-256 über das kanonische `tools/list`); Zugangsdaten nur als Verweise
  auf Fabrik-Secrets. Abweichung → Server gesperrt, `MCP_PIN_ABWEICHUNG`,
  Run abgebrochen. Die Digests liefert eine Vermessung auf
  `/admin/mcp-gateway`.
- **Jeder Aufruf in der Kette:** `MCP_TOOL_AUFRUF` mit Server, Tool,
  Protokollversion, Entscheidung, Dauer und **SHA-256 von Argumenten und
  Ergebnis** statt der Inhalte. Zustellung **fail-closed**: Kann der Gateway
  ein Ereignis nicht zustellen, führt er keinen weiteren Aufruf des Runs aus.
  Run-Token und Ereignis-Token je Run, TTL (Standard 4 h).

*Einschränkungen (ADR-0018):* Ohne Agent-Container ist der Gateway der
einzige *MCP*-Weg, nicht der einzige *Netz*weg. `serverDigest` pinnt Befehl
und Argumente, nicht die Binärdatei dahinter. Die Lese-Einstufung beruht auf
den Annotationen des Servers (über `toolsDigest` gepinnt, Ehrlichkeit prüft
der Admin bei der Vermessung). Schreibende Tools mit Freigabe je Aufruf sind
ein eigener, nicht umgesetzter Schritt.
