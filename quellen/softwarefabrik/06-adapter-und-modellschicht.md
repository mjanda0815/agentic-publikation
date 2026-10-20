# 6. Adapter- und Modellschicht

## 6.1 Der Port

Die gesamte Vendor-Neutralität hängt an einer Schnittstelle mit (bei 0.19.0)
fünf Methoden (`execution/ExecutionAdapter.java`):

```java
public interface ExecutionAdapter {
    String name();
    default String displayName()   { return name(); }
    default String description()   { return ""; }
    default boolean alwaysAvailable() { return false; }

    ExecutionResult execute(ExecutionRequest request,
                            Consumer<ExecutionEvent> eventHandler);

    record ExecutionResult(boolean success, int exitCode,
                           String summary, boolean timedOut) { … }
}
```

Drei Entwurfsentscheidungen stecken darin:

1. **Streaming statt Rückgabewert.** Der `Consumer<ExecutionEvent>` liefert
   Logzeilen, Token-Verbrauch und Phasensignale *während* des Laufs. Ohne das
   wäre Live-Beobachtbarkeit unmöglich und ein Abbruch bliebe folgenlos.
2. **`alwaysAvailable()`** trennt Adapter, die ohne externes Werkzeug
   funktionieren (`mock`), von solchen, deren CLI fehlen kann. Fehlt das
   Binary, verschwindet der Adapter geordnet aus der UI-Auswahl, statt zur
   Laufzeit zu scheitern.
3. **Timeout ist ein eigener Ergebniszustand**, nicht ein Sonderfall von
   Fehler. Bei nichtdeterministischen Agenten ist „hat zu lange gebraucht" ein
   fachlich anderes Ereignis als „ist gescheitert".

*Stand v0.38.0:* Der Vertrag trägt zusätzliche Default-Methoden für die
MCP-Governance (ADR-0017 E5, ADR-0022): `brauchtIsolationsnachweis()`
(`true` für jeden Adapter, der eine Agent-CLI startet), `cliVersion()`,
`cliBefehl()`, `anmeldedaten()` (Projektionen ins ephemere HOME),
`unterstuetztMcpGateway()`, `fuerCanary(…)` und `kontrollAufruf(…)`.
Abstrakt bleibt nur `execute`.

**Maschinell erzwungen:** Weder `..application..` noch `..web..` darf eine
Klasse referenzieren, die `ExecutionAdapter` implementiert (nur den Port
selbst). Zwei ArchUnit-Tests halten das fest — die Vendor-Neutralität ist
damit keine Absichtserklärung, sondern eine Build-Bedingung.

## 6.2 Die zehn Adapter

| Adapter | Art | Anmerkung |
|---|---|---|
| `mock` | deterministisch | Default; funktioniert ohne API-Key, macht das System ohne Vendor demonstrierbar und testbar |
| `claude` | CLI | Anthropic Claude Code (`claude --print --output-format json`), Token-Extraktion aus dem Endergebnis (`ClaudeUsageJsonParser`); der frühere, nie verdrahtete `ClaudeStreamJsonParser` wurde in 0.34.0 entfernt |
| `codex` | CLI | OpenAI Codex CLI |
| `gemini` | CLI | Google Gemini CLI |
| `aider` | CLI | Aider mit freier Modellwahl |
| `kimi` | CLI | Moonshot AI Kimi; Besonderheit siehe 6.3 |
| `local-llm` | CLI | Lokales Modell (z. B. via Ollama) — der Air-Gap-Pfad |
| `bedrock` | Gateway | AWS Bedrock |
| `vertex` | Gateway | Google Vertex AI |
| `azure-openai` | Gateway | Azure OpenAI |

> *Einschränkung:* Die drei Gateway-Adapter sind konfigurierbar und
> degradieren sauber, wurden aber nicht end-to-end gegen echte
> Cloud-Credentials verifiziert. Für das Whitepaper sollte das als
> „vorbereitet" statt „erprobt" bezeichnet werden.

### Auflösungsreihenfolge

```
Run-Override  >  Projekt-Default  >  User-Setting  >  Globales Setting  >  YAML
```

Dieselbe Hierarchie (`PROJECT > USER > GLOBAL > YAML`) implementiert
`SettingService` für alle Laufzeiteinstellungen. Zusätzlich kann ein Projekt
die erlaubten Adapter explizit einschränken (`project_allowed_adapters`,
V25) — und Policy-as-Code kann diese Wahl mandantenweit übersteuern.

## 6.3 Abo-Modus statt Token-Abrechnung

Ein in der Literatur selten behandelter, praktisch aber sehr relevanter Punkt:
Coding-CLIs lassen sich meist auf zwei Wegen authentifizieren — per API-Key
(Abrechnung je Token) oder per Abo-Login (Flatrate). Die Fabrik unterstützt
beides explizit:

| Adapter | `auth-mode` | Abo-Mechanik |
|---|---|---|
| `claude` | `api-key` \| `subscription` | OAuth-Credentials aus `claude /login`; Kopie von `.claude/.credentials.json` ins ephemere HOME |
| `codex` | `api-key` \| `subscription` | „Sign in with ChatGPT"; Kopie von `.codex/auth.json` |
| `kimi` | `api-key` \| `subscription` | `kimi login`; Kopie von `.kimi-code/credentials/` ohne `credentials/mcp/` |

*Stand v0.38.0:* Seit 0.31.0 (ADR-0017 E1) werden `CLAUDE_CONFIG_DIR`,
`CODEX_HOME` und `KIMI_CODE_HOME` nicht mehr an die CLIs durchgereicht; die
Config-Verzeichnisse dienen nur noch als Quelle der Auth-Dateien, die als
**Kopie** ins ephemere HOME je CLI-Aufruf projiziert und nach dem Lauf per
Compare-and-Swap zurückgeschrieben werden (rotierende Refresh-Tokens). Der
frühere Pro-Run-/Pro-Nutzer-Override der `CLAUDE_CONFIG_DIR` ist mit 0.33.0
entfernt (BYOS gestrichen, siehe unten).

**Der kritische Teil ist das Strippen.** Im Abo-Modus wird der jeweilige
API-Key (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, das
`KIMI_MODEL_*`-Override-Trio) **aktiv aus der Subprozess-Umgebung entfernt**.
Sonst würde die CLI stillschweigend den kostenpflichtigen Pfad wählen — ein
Fehler, der erst auf der Rechnung sichtbar wird. Umgekehrt injiziert der
Kimi-Adapter im API-Key-Modus das Trio, weil die Kimi-CLI Keys nur aus ihrer
`config.toml` bzw. diesen Variablen liest.

Konsequenz für das Kostenkapitel: Die Preistabelle der Fabrik führt für
Abo-Modelle bewusst 0,00 € je Million Token (`k3`, `kimi-for-coding`), weil
dort keine Token-Kosten entstehen. Ein reines Token-Kostenmodell würde die
Wirtschaftlichkeit agentischer Entwicklung heute systematisch falsch abbilden.

**Abo-Modus als persönliche Nutzung (Stand v0.38.0, CHANGELOG 0.33.0).**
Der Betriebsmodus `EINZELPLATZ_ABO` ist als Nutzung durch den Abo-Inhaber auf
seinem eigenen Rechner beschrieben; `TEAM_API_POOL` sperrt den Abo-Login und
erzwingt den API-Key-Modus (prüft aber nicht, ob ein Key vorhanden ist; er muss
in der Umgebung des App-Prozesses stehen). „Bring Your Own Subscription"
(mehrere Nutzer mit eigenem Claude-Abo auf einem Server) wurde entfernt, weil
der Anbieter Drittanwendungen das Sammeln, Speichern oder Vermitteln von
Claude.ai-Zugangsdaten untersagt. Für Claude-Abo-Läufe stempelt der Adapter
den Auth-Modus; die Kosten werden weiterhin zum API-Tarif berechnet, aber als
„Schätzung (API-Tarif), nicht abgerechnet" gekennzeichnet
(`run_metrics.kosten_geschaetzt`, V58; `null` = unbekannt/Altbestand). Sie
zählen bewusst weiter gegen Budget und Hard-Cap, weil sie die erzeugte Last
abbilden.

## 6.4 Capability-Routing

`execution/routing/` bildet Modelle nicht direkt, sondern über
**Fähigkeitsprofile** ab:

- `RoutingRolle` — wofür wird das Modell gebraucht: `PLAN`, `BUILD` und seit
  0.38.0 `SPEC` (Setting `run.routing.spec-model`),
- `CapabilityTier` / `CapabilityProfile` — welche Fähigkeitsstufe die Rolle
  verlangt,
- `CapabilityProfileRegistry` + `ModelRoutingService` — Auflösung zur
  Laufzeit.

Nutzen: Planung darf ein stärkeres, teureres Modell bekommen als
mechanische Umsetzung, ohne dass irgendwo ein Modellname hart verdrahtet
wird. Eine per Projekt gesetzte **Modell-Policy** wird beim Anlegen eines Runs
erzwungen und attestiert (`RUN_MODELL_AUFGELOEST`) — damit ist im Nachhinein
belegbar, welches Modell wirklich gearbeitet hat.

*Stand v0.38.0 (CHANGELOG 0.33.0):* Liefern weder Routing-Override noch
Team-Präferenz ein Modell, greift für den Adapter `claude` ein
**Rollen-Default** aus dem `ModelCatalog`; andere Adapter bleiben beim
Adapter-Default, weil sie `--model` an fremde CLIs durchreichen.
`RUN_MODELL_AUFGELOEST` nennt seither die Herkunft
(`quelle=override|team|rollen-default|adapter-default`). Konkrete
Modell-IDs der Rollen-Defaults sind schnelllebig und hier bewusst nicht
genannt (Stand-Datum im `application.yml`-Kommentar).

## 6.5 Sandbox-Modell

> **Korrektur (Stand v0.38.0; ADR-0017 „Korrektur zu ADR-0016",
> `execution/sandbox/SandboxScopeAdvisory.java`, `docs/security/sandbox.md`).**
> Die Coding-Adapter (Claude Code, Codex, Gemini, Aider, Kimi, die drei
> Gateways, local-llm) laufen in **keiner** Variante im Container, sondern
> immer als Host-Prozess: `VendorCliRunner`, `ClaudeCodeExecutionAdapter` und
> `ReviewProcessRunner` starten die CLIs per `ProcessBuilder` auf dem Host.
> Seit 0.31.0 jeweils mit **ephemerem HOME je CLI-Aufruf** (`AgentHome`; nur
> die Auth-Dateien des Adapters als Kopie und eine neutrale `.gitconfig`),
> **Env-Allowlist** und **MCP-Nullzustand**. Die unten beschriebene
> Container-Variante kapselt nur Build/Tests (`mvn verify`) sowie trivy
> (SBOM-Erzeugung, Dependency-Scan) des generierten Projekts. Agent-CLIs im
> Container sind ein eigenes, offenes Arbeitspaket (eigener ADR angekündigt).
> Das ephemere HOME schützt vor *Konfiguration*, nicht vor gezieltem Lesen
> über absolute Pfade; Netzzugriff hat der Agentenprozess wie der Host.
> Der Boot-Hinweis sagt das seit 0.33.0 in beiden Varianten.

`ExecutionSandboxFactory` wählt für die Build- und Scan-Schritte zwischen
zwei Varianten (Setting `execution.sandbox.variant`):

**`LocalProcessSandbox`** (Default)
- eigener Prozess je Run, Arbeitsverzeichnis = Workspace,
- Umgebungsvariablen sauber pro Prozess gesetzt (kein globales `setenv`),
- `EnvAllowlist` — nur freigegebene Variablen erreichen den Agenten,
- hartes Terminieren bei Abbruch/Timeout (`destroyForcibly()`),
- zeilenweises Mitschreiben von `stdout`/`stderr`.

**`ContainerProcessSandbox`** (ADR-0011, Variante B, seit v0.7.0 *Accepted*)
- ephemerer Docker-/Podman-Container (`docker run --rm`) je Aufruf,
- `--cpus 2 --memory 4g --pids-limit 512 --read-only`, `--tmpfs /tmp`,
- Bindmount ausschließlich auf den Workspace,
- `--network=none` als Default der Vorlage
  (`softwarefabrik.execution.sandbox.network-none=true`),
- fehlt Docker im PATH, fällt die Factory mit Warnung auf lokal zurück.

*Einschränkung:* Die tatsächlich gekapselten Pfade (`mvn verify` über
`BuildService`, `trivy fs` über `SbomService`, `DependencyScanReviewerAdapter`)
erreichen die Sandbox über den Port `common.SandboxLauncher` und bekommen
laut `docs/security/sandbox.md` **Netzwerk erlaubt** (Maven-Dependency-
Download, trivy-Schwachstellendatenbank); read-only Root-FS, Limits und der
Workspace als einziger beschreibbarer Mount bleiben. Die frühere Aussage
„Coding-Agent ohne Netz per Default" ist damit nicht gedeckt.

## 6.6 Secrets

- Vendor-Keys werden **AES-GCM-verschlüsselt** persistiert; der Master-Key
  kommt aus der Umgebung (`SOFTWAREFABRIK_SECRETS_MASTER_KEY`).
- Sechs Provider-Validatoren (Anthropic, OpenAI, Gemini, Kimi, GitHub, NVD)
  prüfen Keys auf Gültigkeit, bevor ein Lauf daran scheitert.
- Ein `SecretsBootCheck` und ein `SecretsHealthIndicator` machen fehlende oder
  unbrauchbare Schlüssel beim Start und im Health-Endpoint sichtbar.
- Der Audit-Log besitzt einen Secret-Filter, damit Schlüsselmaterial nicht
  über Protokolle abfließt.
- **Host-Allowlist für Remotes** (`common/RemoteUrlPolicy`,
  `git.allowed-hosts`, Default `github.com`): Nur für erlaubte Hosts wird der
  GitHub-Token verwendet und eine API-Anfrage ausgeführt. Ohne diese Grenze
  könnte eine manipulierte Remote-URL den fabrikweiten Token exfiltrieren
  (SSRF) — ein Befund aus dem adversarialen Re-Review von v0.18. Zusätzlich
  wird `GIT_ALLOW_PROTOCOL` gesetzt, um `git-ext::`-Protokoll-Angriffe (RCE)
  auszuschließen.

## 6.7 Kostenmodell

- Preistabelle je Modell in `application.yml`: Input, Output und *Cached
  Input* getrennt, jeweils EUR je 1 Mio. Token.
- Unbekannte Modelle werden mit 0 € bewertet (`ModelPricingProperties`,
  am Tag v0.38.0 unverändert) — bewusst konservativ, statt zu raten.
  *Einschränkung:* Genau das hat einen realen Fehler verdeckt: Bis 0.34.0
  wurden Claude-Läufe mit 0 € bewertet, weil der Parser ein Feld `model` las,
  das die CLI im Ergebnis nicht liefert. Seit 0.34.0 wertet er `modelUsage`
  aus (Tokens aller Modelle inkl. Subagenten, Preis des teuersten Modells
  für alle Tokens — bekannte Grenze).
- Token-Erfassung: `ClaudeUsageJsonParser` liest reale Verbrauchswerte;
  `TokenEstimator` (jtokkit) schätzt, wo der Vendor keine Werte liefert.
  Seit 0.34.0 (V60) zusätzlich **Cache-Schreib-Tokens**
  (`total_cache_creation_tokens`, bewertet mit 1,25 × Input-Preis) und die
  **Kostenschätzung der CLI** (`gemeldete_kosten_usd`) als Gegenprobe im
  Warum-Trace — beides keine Abrechnung.
- Abo-Läufe: Kennzeichnung als Schätzung über `kosten_geschaetzt` (V58,
  siehe 6.3), auch in den CSV-Exporten (`Davon-Schaetzung-Abo-EUR`).
- Aggregation nach Projekt, Run, Provider, Mandant und **Seat** (auslösender
  Nutzer, abgeleitet aus `run.triggered_by`); CSV-Export je Sicht.
- **Harte Budget-Caps** pro Mandant (`mandant_budget`, V28) sowie Tages-/
  Wochenlimits mit Soft-Schwelle; überschrittene Caps verhindern neue Läufe.
- *Grenze:* Der harte Cap wirkt je Mandant, nicht je Seat — die Seat-Sicht
  wertet aus, sie begrenzt nicht.
