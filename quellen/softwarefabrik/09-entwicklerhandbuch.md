# 9. Entwicklerhandbuch

Praxisteil: Wie man die Fabrik lokal betreibt, erweitert und wie ihre
Qualitätsmechanik funktioniert. Eignet sich als Anhang der Publikation oder
als Grundlage eines „So baut man so etwas selbst"-Kapitels.

## 9.1 Voraussetzungen

| | |
|---|---|
| JDK | 25 |
| Maven | 3.9+ (Wrapper vorhanden) |
| Docker / Podman | für PostgreSQL, optional für die Container-Sandbox |
| Optional | Coding-CLI (`claude`, `codex`, `gemini`, `aider`, `kimi`), `trivy` |

Ohne jede CLI ist das System vollständig lauffähig: Der `mock`-Adapter ist
`alwaysAvailable` und deterministisch.

## 9.2 Lokal starten

```bash
# 1) Konfiguration
cp .env.example .env
#    SOFTWAREFABRIK_DB_PASSWORD          (>= 16 Zeichen)
#    SOFTWAREFABRIK_SECRETS_MASTER_KEY   (>= 32 Zeichen, openssl rand -base64 48)
#    SOFTWAREFABRIK_ADMIN_PASSWORD

# 2) Datenbank
docker compose up -d postgres

# 3a) Anwendung aus der IDE / per Maven
export SOFTWAREFABRIK_ADMIN_PASSWORD='…'
export SOFTWAREFABRIK_EXECUTION_ADAPTER=claude
export SOFTWAREFABRIK_CLAUDECODE_COMMAND="$(which claude)"
export SOFTWAREFABRIK_WORKSPACES_ROOT=/tmp/softwarefabrik-workspaces
mvn -f app/pom.xml spring-boot:run

# 3b) …oder der komplette Stack
docker compose up -d
```

Anwendung danach auf `http://localhost:8080`.

**Härtung, die beim Start greift:** Das `container`-Profil lehnt bekannte
Demo-Werte und zu kurze Master-Keys hart ab (`SecretsEncryptor`), Compose
bricht ohne `.env` ab (`${VAR:?…}`), und Postgres ist auf `127.0.0.1`
gebunden. Ohne gesetztes Admin-Passwort wird kein Admin angelegt.

## 9.3 Bauen und Testen

```bash
mvn -f app/pom.xml verify          # Tests + ArchUnit + JaCoCo-Gate + Trivy
mvn -f app/pom.xml -Pci verify     # wie CI
mvn -f app/pom.xml -Pe2e verify    # Playwright-E2E (on demand)
```

**Coverage-Gate (buildbrechend):** Line ≥ 0,85 · Branch ≥ 0,81 (JaCoCo).

### Testpyramide

| Stufe | Werkzeug | Prinzip |
|---|---|---|
| Unit | JUnit 5, Mockito, AssertJ | je Service, ohne Spring-Kontext |
| Integration | `@WebMvcTest`, `@DataJpaTest` gegen H2 | Slice-Tests |
| Architektur | ArchUnit 1.4.1 | Schichten, Ports, Debt-Ratchet |
| Boot-Smoke | Docker Compose + echtes PostgreSQL | `/actuator/health` = UP |
| E2E | Playwright | on demand, `-Pe2e` |

**Testbarkeitsregel des Projekts:** Kein `JaCoCo`-Exclude für schwer testbare
Stellen, sondern testbare Verdrahtung — Netz-Adapter bekommen eine
injizierbare URL und werden gegen einen lokalen `HttpServer` getestet;
CLI-Adapter bekommen einen injizierbaren `ProcessRunner`. Das ist der Grund,
warum eine 33-kLOC-Codebasis mit sehr viel Prozess- und Netzanbindung
überhaupt 85 % Line-Coverage erreichen kann.

## 9.4 Konventionen

- Konstruktor-Injection; Ausnahme sind die optionalen Setter-Kollaborateure
  des Orchestrators.
- Fachsprache **deutsch** in Domäne und Services (`fuehreAus`,
  `wechsleStatus`, `verifiziereKette`), technische Rahmen englisch. Das ist
  eine bewusste Ubiquitous-Language-Entscheidung, kein Zufall.
- Neue Klassen bevorzugt in **Blatt-Slices** — siehe 9.6.
- Schemaänderungen ausschließlich als **neue** Flyway-Migration. Änderungen an
  bestehenden Migrationen markiert der `architecture-reviewer` als CRITICAL.
- Controller nur in `..web..`; keine Repositories in `..web..`/`..application..`.
- Kein Feld-Zugriff auf fremde Slice-Domänen.

## 9.5 Erweiterungsrezepte

### Neuen Execution-Adapter hinzufügen

1. Klasse in `execution/<vendor>/` anlegen, `ExecutionAdapter` implementieren.
2. `name()` eindeutig wählen; `alwaysAvailable()` nur, wenn kein externes
   Binary nötig ist.
3. Prozessstart über `VendorCliRunner` / `ExecutionSandboxFactory`, nicht
   direkt über `ProcessBuilder` — sonst umgeht der Adapter Sandbox und
   `EnvAllowlist`.
4. Events (Logzeile, Token, Phase) über den `eventHandler` melden, sonst
   bleibt die Live-Ansicht leer.
5. Braucht der Vendor einen Abo-Modus: `…AuthResolver` + `…AuthMode` nach dem
   Muster von `claudecode`/`codex`/`kimi`, inklusive **Strippen** des
   API-Keys im Abo-Modus.
6. Preise in `application.yml` unter `softwarefabrik.models` ergänzen.
7. Test mit injiziertem `ProcessRunner` schreiben.

Der Adapter wird automatisch von `ExecutionAdapterRegistry` eingesammelt — es
gibt keine Registrierungsliste, die man vergessen könnte.

### Neuen Reviewer hinzufügen

1. Klasse in `review/reviewer/`, `ReviewAdapter` implementieren.
2. Befunde als `ReviewFinding` mit Kategorie und Schweregrad liefern.
3. Blockierverhalten kommt aus der `QualityGatePolicy` — nicht im Reviewer
   hart kodieren. Ausnahmen sind die drei systemweiten Sonderregeln
   (SECURITY/HIGH+, ARCHITECTURE/CRITICAL, Reviewer-Absturz).
4. Reviewer bleiben **read-only**. Ein schreibender Reviewer hebt die Trennung
   auf, die das Gate erst begründet.

### Neue Migration

`app/src/main/resources/db/migration/V<n>__<thema>.sql`, aufsteigend,
unveränderlich nach Auslieferung. `ddl-auto=validate` deckt Abweichungen
zwischen Entität und Schema beim Start auf.

## 9.6 Fallstricke aus der Projektpraxis

Diese Punkte sind für ein Praxiskapitel wertvoll, weil sie in keiner
Architekturzeichnung stehen:

1. **ArchUnit-Ratchet und die Zyklen-Kappungsgrenze.** Der Freeze speichert
   nur bis zu 100 elementare Modulzyklen. Bleibt die Gesamtzahl darunter, ist
   die Enumeration deterministisch und CI stimmt mit lokal überein. Sprengt
   eine neue Cross-Slice-Kante die Grenze, wird die Enumeration abgeschnitten
   und reihenfolgeabhängig — der Test wird lokal grün und in CI rot.
   *Regel:* neue Klassen in Blatt-Slices legen; Refreeze nur unterhalb der
   Grenze; nach einem `git merge main` in einen Feature-Branch den Store neu
   einfrieren.
2. **Coverage in CI liegt systematisch unter lokal** (etwa 0,01–0,012 Branch),
   weil Vendor-CLI-Prozesspfade lokal häufiger durchlaufen werden. Lokal also
   mit Reserve zielen, nicht knapp über der Schwelle.
3. **Secret-Scanner und Testfixtures.** `gitleaks` schlägt auf PEM-Label in
   Krypto-Hilfsklassen an — gelöst über eine pfad-gescopte Allowlist mit
   `useDefault=true`, nicht durch Abschalten des Scanners.
4. **Jackson 2 vs. 3.** Spring Boot 4.0.7 stellt Jackson 3 (`tools.jackson`)
   als primären `ObjectMapper` bereit; `com.fasterxml` ist nur transitiv da.
   Für neue Serialisierung entweder den Jackson-3-Bean injizieren oder — wie
   beim Audit-Export — einen eigenen Mapper mit String-only-DTOs verwenden.
5. **Signaturen und Zeitstempel.** Ohne Trunkierung auf Millisekunden ist eine
   Signatur nach dem PostgreSQL-Roundtrip nicht mehr byte-stabil.
6. **Ein CI-Job, der sich ohne Secret selbst überspringt, zeigt ein grünes
   Häkchen ohne echten Scan.** Beim Aufsetzen neuer Repositories prüfen, dass
   die Secrets gesetzt sind.
7. **Offener Defekt:** Ein Integrationstest committet unter bestimmten
   Bedingungen in das reale Repository statt in ein temporäres
   (Test-Isolationsdefekt).

## 9.7 CI-Pipeline

GitHub Actions (`.github/workflows/ci.yml`), sechs Jobs:

| Job | Inhalt |
|---|---|
| **Build & Test** (Matrix je Modul) | `mvn verify` inkl. Tests, ArchUnit und JaCoCo-Gate; Reports als Artefakte |
| **Boot-Smoke** | echtes PostgreSQL, `container`-Profil, wartet auf `/actuator/health` = UP |
| **OWASP Dependency-Check** | mit NVD-Cache; Erstlauf dauert lange, danach gecacht |
| **Secret-Scan** | `gitleaks` über die volle Historie |
| **Docker-Image** | Image bauen, Trivy-Scan, CycloneDX-SBOM extrahieren und hochladen |

Der Arbeitsmodus im Projekt: Feature-Branch → Pull Request → CI als Gate →
Squash-Merge. Nie direkt auf `main`. Die PR-Nummer wird als Buildnummer in der
UI angezeigt — jede laufende Instanz ist damit einer konkreten Änderung
zuordenbar.

## 9.8 Qualitätsmechanik im Überblick

```
Entwickler
   │  Feature-Branch
   ▼
Lokal:  mvn verify   →  Tests · ArchUnit · Ratchet · JaCoCo · Trivy
   │  Push + Pull Request
   ▼
CI:     6 Jobs       →  Build · Smoke · OWASP · gitleaks · Image+SBOM
   │  Squash-Merge
   ▼
Release: Version · CHANGELOG · Tag · GitHub-Release · Deploy
```

Bemerkenswert für die Publikation: Die Fabrik unterwirft sich denselben
Mechanismen, die sie anderen Projekten auferlegt — Quality Gate, SBOM,
Secret-Scan, Architekturregeln, Coverage-Schwelle. Ein Werkzeug für
disziplinierte Entwicklung, das selbst undiszipliniert entwickelt würde, wäre
kein glaubwürdiger Beleg.
