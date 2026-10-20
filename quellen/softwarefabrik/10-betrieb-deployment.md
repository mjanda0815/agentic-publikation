# 10. Betrieb und Deployment

## 10.1 Deployment-Topologie

Die Zielinstallation ist bewusst schlicht: **ein Anwendungscontainer, eine
Datenbank.** Kein Cluster, kein Broker, kein Service-Mesh.

```
Kundenhost
├── softwarefabrik-app      Spring Boot, Port 8080
├── softwarefabrik-postgres PostgreSQL 18, gebunden an 127.0.0.1
├── Workspaces              ein Git-Repository je Projekt
├── Coding-Agenten          Host-Prozesse der App (ephemeres HOME je CLI-Aufruf)
├── (optional) ephemere Build-/Scan-Container (mvn verify, trivy)
└── (optional) MCP-Gateway  eigener Prozess, 127.0.0.1 (seit 0.34.0)
```

*Korrektur (Stand v0.38.0, ADR-0017):* Die frühere Angabe „ephemere
Agent-Container je Run" traf nicht zu — die Container-Variante kapselt nur
Build/Tests und trivy des generierten Projekts; die Coding-Agenten laufen in
jeder Variante als Host-Prozess.

Optional und getrennt: der Lizenz-Stack (License-Service, eigene PostgreSQL;
`license-infra/docker-compose.yml`) als eigener Compose-Stack — er kann
außerhalb der Unternehmensgrenze stehen oder ganz entfallen. Ebenfalls
optional: der MCP-Gateway als externer Dienst (Betriebsart `extern`) statt
als von der Fabrik gestarteter Prozess.

## 10.2 Profile

| Profil | Zweck |
|---|---|
| *(default)* | lokale Entwicklung |
| `local` | lokale Entwicklung mit abweichenden Pfaden |
| `container` | Betrieb in Docker; härtet Secrets- und Schlüsselprüfungen |
| `demo` | öffentliche Demo: Demo-Banner, täglicher Reset |
| `ci` | Maven-Profil für die CI-Pipeline |
| `e2e` | Maven-Profil für Playwright-Tests on demand |

## 10.3 Konfiguration

Alles läuft über Umgebungsvariablen mit sicheren Defaults. Die wichtigsten:

| Variable | Bedeutung |
|---|---|
| `SOFTWAREFABRIK_DB_*` | Datenbankname, Nutzer, Passwort (≥ 16 Zeichen), Port |
| `SOFTWAREFABRIK_SECRETS_MASTER_KEY` | AES-GCM-Masterkey (≥ 32 Zeichen); im `container`-Profil Pflicht |
| `SOFTWAREFABRIK_ADMIN_USER` / `_PASSWORD` | Bootstrap-Admin; ohne Passwort wird kein Admin angelegt |
| `SOFTWAREFABRIK_WORKSPACES_ROOT` | Wurzel der Projekt-Workspaces |
| `SOFTWAREFABRIK_EXECUTION_ADAPTER` | Standard-Adapter (Default `mock`) |
| `SOFTWAREFABRIK_<VENDOR>_COMMAND` / `_TIMEOUT` / `_AUTH_MODE` | je CLI-Adapter |
| `SOFTWAREFABRIK_GIT_ALLOWED_HOSTS` | Host-Allowlist für Remotes (Default `github.com`) |
| `SOFTWAREFABRIK_GIT_PR_FEEDBACK_ENABLED` | PR/CI-Poller (Default **false**) |
| `SOFTWAREFABRIK_ATTESTATION_SIGNING_*` | Signatur an/aus, Key-ID, Schlüsselpfad, Keyring |
| `SOFTWAREFABRIK_LICENSE_V1_*` | Lizenzsystem an/aus (`…_ENABLED`, Default **false**), Lizenzserver, Public-Key-Quelle |
| `SOFTWAREFABRIK_WORKFLOW_ENABLED` | Workflow-Ebene (Default **false**) |
| `SOFTWAREFABRIK_SPEC_ENABLED` | Spec-Driven Development (Default **false**; seit 0.35.0) |
| `softwarefabrik.mcp-gateway.modus` (Property) | MCP-Gateway `aus` (Default) / `lokal` / `extern`; dazu `jar`, `url`, `ttl-sekunden`, `tls-extern` (seit 0.34.0) |
| `softwarefabrik.execution.sandbox.variant` (Property/Setting) | `local` (Default) / `container` — gilt für Build/Tests und trivy, nicht für die Agenten |

**Startzeit-Härtung** (bewusst *fail fast*):

- Compose bricht ohne `.env` ab (`${VAR:?…}`) — kein versehentlicher Start mit
  Standardpasswörtern.
- `SecretsEncryptor` lehnt bekannte Demo-Werte und zu kurze Master-Keys im
  `container`-Profil hart ab.
- Attestierung „aktiviert ohne Schlüssel" ist im Container-/Prod-Profil ein
  Startfehler; wer ohne Signatur betreiben will, setzt `enabled=false`
  explizit.
- PostgreSQL ist auf `127.0.0.1` gemappt; die App verbindet über das
  Compose-Netzwerk.

## 10.4 Beobachtbarkeit im Betrieb

- `/actuator/health` (inkl. Secrets-Health-Indicator), `/actuator/info` mit
  Version und Buildnummer.
- `/actuator/prometheus`, nur für `ROLE_ADMIN`.
- Logback mit MDC (`projectId`, `runId`, `phase`).
- Live-Ansicht je Run über SSE mit Heartbeat, Reconnect und Replay.

## 10.5 Lizenz- und Identitätsschicht

> *Korrektur (Stand v0.38.0):* Der hier früher beschriebene Stack (Keycloak
> als OIDC-Provider, RS256-Lease-JWTs, Stufen DEMO/COMMUNITY/FULL,
> Client-Klassen `CredentialStore`/`LeaseCache`/`LeaseValidator`/
> `LicenseGate`) ist im Code nicht mehr vorhanden; er wurde mit 0.4.0
> entfernt (Commit „alt-stack (keycloak + rs256) entfernt, v1 einziger
> lizenzstack"; ADR-0005 löst ADR-0004 ab).

- **Format:** JSON Web Signature mit **Ed25519** (`EdDSA`, RFC 8037) als
  einheitliches Lizenzformat (ADR-0005); der Public Key wird mit dem Client
  ausgeliefert, Verifikation offline (`license/v1/Ed25519JwsVerifier`,
  `LicenseVerifier`).
- **License-Service**: eigener Spring-Boot-Dienst mit eigener PostgreSQL
  (`license-infra/docker-compose.yml`).
- **Client-seitig** (`license/v1/`): `LicenseManager`, `LicenseStore`,
  `LeaseClient`, `LicenseStartupRefresh` (best-effort-Refresh bei jedem
  Start, seit 0.10.0), `RunLimiter`; Lease-Zustände `CONNECTED`, `GRACE`,
  `EMERGENCY_GRACE`, `EXPIRED` (`LeaseState`).
- **Tiers** (`license/v1/V1Tier`): `COMMUNITY`, `PROFESSIONAL`,
  `ENTERPRISE`. Seit 0.35.0 wertet ein zentrales `FeatureGate` (Port in
  `common`, Implementierung `license/LizenzFeatureGate`) Flag und Tier aus;
  Spec-Driven Development verlangt Professional oder höher.
- **Standardmäßig aus** (`softwarefabrik.license.v1.enabled=false`); ohne
  aktives Lizenzsystem entscheidet allein das jeweilige Feature-Flag.
- **Offline-Verifikation** — kurzzeitige Nichterreichbarkeit des
  Lizenzservers ist unkritisch (Grace-Fenster). Bei abgelaufener Lizenz
  werden Runs gesperrt, nicht die gesamte App (CHANGELOG 0.10.0).
  TODO(verify): genaue Lease-Laufzeiten je Tier und Grace-Dauer stehen in
  der Lizenz-Konfiguration (`leaseConfig`), nicht im App-Code; hier nicht
  erhoben.

Für die Publikation relevant, weil es die Air-Gap-Frage beantwortet: Ein
System, das für Verschlusssachen taugen soll, darf keine Online-Aktivierung
als Betriebsvoraussetzung haben. Der Ausweg hier ist ADR-0009
(`refresh-required=false`) — Lizenz ohne Rückkanal.

## 10.6 Air-Gap-Betrieb

Alle Bausteine für den vollständig getrennten Betrieb sind vorhanden:

| Anforderung | Umsetzung |
|---|---|
| Kein Vendor-Cloud-Zugriff | `local-llm`-Adapter (z. B. Ollama) |
| Kein Netz für den Agenten | *Nicht durch die Fabrik erzwungen (Stand v0.38.0):* Die Agenten laufen als Host-Prozess mit dem Netz des Hosts; die Container-Sandbox kapselt nur Build/Scans (und erlaubt dort Netz für Dependency-/DB-Download). Netztrennung ist Sache des Hosts/der Umgebung; Agent-Container sind ein offenes Arbeitspaket |
| Kein MCP-Zugriff ohne Freigabe | MCP-Nullzustand für alle Agentenläufe; Gateway standardmäßig `aus` |
| Prüfung durch Dritte ohne Systemzugang | Offline-Verifier (nur JDK) für den Audit-Export, Schema 2.0 |
| Keine Lizenz-Rückfrage | ADR-0009, `refresh-required=false` |
| Keine Remote-Kopplung | PR-Feedback-Poller standardmäßig aus; Host-Allowlist |
| Auslieferung | Runbook `docs/runbooks/airgap-auslieferung.md` |

## 10.7 Öffentliche Demo-Instanz

Unter `demo.softwarefabrik.io` läuft eine dauerhaft verfügbare Instanz im
`demo`-Profil (Demo-Banner, täglicher Datenreset). Sie dient als Beleg, dass
das System nicht nur baubar, sondern betreibbar ist — Deployment als
JAR-Tausch unter systemd, Runbook `docs/runbooks/deploy-demo.md`.

Eine Betriebserfahrung, die in ein Praxiskapitel gehört: Ein Ausfall der
Demo-Instanz ging nicht auf die Anwendung zurück, sondern auf ein
Reset-Skript mit `set -e`, das bei vollem Dateisystem abbrach, **bevor** es
die Anwendung wieder startete. Behoben durch einen `EXIT`-Trap, der die
Anwendung in jedem Fall startet, plus Logrotation. Die Lehre ist
verallgemeinerbar: Automatisierung, die bei Fehlern *abbricht statt
aufzuräumen*, verwandelt kleine Störungen in Ausfälle — dieselbe Logik wie
beim „Reviewer-Absturz darf kein stiller Pass sein".

## 10.8 Backup und Wiederanlauf

- Zu sichern sind zwei Dinge: die PostgreSQL-Datenbank und das
  Workspace-Verzeichnis (letzteres enthält die Git-Repositories der Projekte).
- Verfahren in `docs/backup-restore.md`.
- Die Audit-Hashkette ist nach einem Restore verifizierbar — ein
  unvollständiges oder manipuliertes Backup fällt bei der Kettenprüfung auf
  (`CHAIN_BREAK`). Das ist ein angenehmer Nebeneffekt: Die Nachweisstruktur
  ist zugleich eine Integritätsprüfung der Sicherung.
