# 10. Betrieb und Deployment

## 10.1 Deployment-Topologie

Die Zielinstallation ist bewusst schlicht: **ein Anwendungscontainer, eine
Datenbank.** Kein Cluster, kein Broker, kein Service-Mesh.

```
Kundenhost
├── softwarefabrik-app      Spring Boot, Port 8080
├── softwarefabrik-postgres PostgreSQL 18, gebunden an 127.0.0.1
├── Workspaces              ein Git-Repository je Projekt
└── (optional) ephemere Agent-Container je Run
```

Optional und getrennt: der Lizenz-Stack (Keycloak + License-Service, eigene
PostgreSQL) als eigener Compose-Stack — er kann außerhalb der
Unternehmensgrenze stehen oder ganz entfallen.

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
| `SOFTWAREFABRIK_LICENSE_V1_*` | Lizenzserver, Issuer, Audience, Public-Key-Quelle |

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

- **Keycloak** als OIDC-Provider (Device-Authorization-Grant für die
  Registrierung).
- **License-Service**: eigener Spring-Boot-Dienst mit eigener Datenbank,
  stellt RS256-signierte **Lease-JWTs** mit sieben Tagen Gültigkeit aus; der
  private Schlüssel ist bind-mount-persistent, damit die `kid` über
  Container-Neustarts stabil bleibt.
- **Client-seitig**: `CredentialStore` (AES-GCM), `LeaseCache`, `LeaseClient`,
  `LeaseValidator` (offline gegen eingebettetes JWKS), `LicenseGate`,
  `LicenseBootstrap`.
- **Stufen**: DEMO (unregistriert, nur `mock`, harte Limits, ohne jeden
  Netzzugriff) → COMMUNITY (nach Registrierung) → FULL.
- **Offline-Verifikation** — kurzzeitige Nichterreichbarkeit des Lizenzservers
  ist unkritisch. Abgelaufenes Lease **und** nicht erreichbarer Server führen
  zu *fail closed*: keine weiteren Läufe.

Für die Publikation relevant, weil es die Air-Gap-Frage beantwortet: Ein
System, das für Verschlusssachen taugen soll, darf keine Online-Aktivierung
als Betriebsvoraussetzung haben. Der Ausweg hier ist ADR-0009
(`refresh-required=false`) — Lizenz ohne Rückkanal.

## 10.6 Air-Gap-Betrieb

Alle Bausteine für den vollständig getrennten Betrieb sind vorhanden:

| Anforderung | Umsetzung |
|---|---|
| Kein Vendor-Cloud-Zugriff | `local-llm`-Adapter (z. B. Ollama) |
| Kein Netz für den Agenten | Container-Sandbox mit `--network=none` |
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
