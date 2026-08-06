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
    boolean      pflichtAttestierung)    // Signaturpflicht
```

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

| Profil | Gate | Pflichtfreigaben | Attestierung | Regulatorischer Bezug |
|---|---|---|---|---|
| **Baseline** | advisory | — | nein | kein reguliertes Umfeld |
| **EU AI Act** | blocking | `EXECUTION` | ja | VO (EU) 2024/1689, Art. 12 (Aufzeichnungspflichten), Art. 14 (menschliche Aufsicht) |
| **BAIT / MaRisk / DORA** | blocking | `EXECUTION`, `VALIDATION` | ja | BaFin BAIT/MaRisk; DORA (EU) 2022/2554 — IKT-Risiko, Drittparteienrisiko, Nachweisführung |
| **BSI-Grundschutz / VS-NfD** | blocking | `EXECUTION`, `VALIDATION` | ja | BSI IT-Grundschutz; VS-NfD. Zusätzlich: für Verschlusssachen ausschließlich On-Prem-/souveräner Betrieb — die erlaubten Adapter sind projektspezifisch auf lokale Backends zu beschränken |

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
(`synchronized`), mit auf Millisekunden getrunkenem Zeitstempel — sonst wäre
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

## 8.7 Audit-Export

`export/AuditExportService` erzeugt ein prüffähiges Bundle je Projekt oder
Run — als JSON und HTML — bestehend aus Warum-Trace, Kettenverifikation,
geltendem Policy-Stand und dem öffentlichen Schlüssel.

Ein technisches Detail mit Praxiswert: Das Bundle enthält ausschließlich
Strings, Primitive und UUIDs (Zeitstempel als ISO-8601-Text). Damit ist die
Serialisierung deterministisch und unabhängig von Jackson-Datumsmodulen — ein
Bundle, das je nach Bibliotheksversion anders aussieht, taugt nicht als
Nachweis.

## 8.8 Supply-Chain-Nachweis

| Baustein | Umsetzung |
|---|---|
| SBOM je Build | `SbomService` (Trivy Filesystem-Scan), `sbom_artifact` (V31), Ereignis `SBOM_ERZEUGT`; standardmäßig `off`, graceful bei fehlendem Trivy |
| Signierte Artefakte | Ed25519-Signatur über den SBOM-Digest (V32), Ereignis `ARTEFAKT_SIGNIERT` |
| Abhängigkeitsprüfung | `DependencyScanReviewerAdapter` (Trivy vuln + license) als blockierender Reviewer im Quality Gate |
| CI-seitig | OWASP Dependency-Check, Trivy-Image-Scan, gitleaks-Secret-Scan, CycloneDX-SBOM als Artefakt |

## 8.9 Skill-Bibliothek als Governance-Objekt

Die Skill-/Plugin-Bibliothek (`skills`, V38) ist bewusst kein
Konfigurationsordner:

- Einträge sind **mandantengescopt** und **versioniert**
  (`skill_catalog_entry` + `skill_version`),
- Herkunft ist typisiert: `CATALOG` (kuratiert), `INSTALLED` (übernommen),
  `FORKED` (angepasst),
- Arten: `SKILL` und `PLUGIN`.

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
