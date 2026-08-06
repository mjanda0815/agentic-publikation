# 6. Adapter- und Modellschicht

## 6.1 Der Port

Die gesamte Vendor-Neutralität hängt an einer Schnittstelle mit fünf Methoden
(`execution/ExecutionAdapter.java`):

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

**Maschinell erzwungen:** Weder `..application..` noch `..web..` darf eine
Klasse referenzieren, die `ExecutionAdapter` implementiert (nur den Port
selbst). Zwei ArchUnit-Tests halten das fest — die Vendor-Neutralität ist
damit keine Absichtserklärung, sondern eine Build-Bedingung.

## 6.2 Die zehn Adapter

| Adapter | Art | Anmerkung |
|---|---|---|
| `mock` | deterministisch | Default; funktioniert ohne API-Key, macht das System ohne Vendor demonstrierbar und testbar |
| `claude` | CLI | Anthropic Claude Code (`claude --print`), Stream-JSON-Parser, Token-Extraktion |
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
| `claude` | `api-key` \| `subscription` | OAuth-Credentials aus `claude /login`, `CLAUDE_CONFIG_DIR` überschreibbar pro Run/Nutzer |
| `codex` | `api-key` \| `subscription` | „Sign in with ChatGPT", `CODEX_HOME` |
| `kimi` | `api-key` \| `subscription` | `kimi login`, `KIMI_CODE_HOME` |

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

## 6.4 Capability-Routing

`execution/routing/` bildet Modelle nicht direkt, sondern über
**Fähigkeitsprofile** ab:

- `RoutingRolle` — wofür wird das Modell gebraucht (Planung vs. Umsetzung),
- `CapabilityTier` / `CapabilityProfile` — welche Fähigkeitsstufe die Rolle
  verlangt,
- `CapabilityProfileRegistry` + `ModelRoutingService` — Auflösung zur
  Laufzeit.

Nutzen: Planung darf ein stärkeres, teureres Modell bekommen als
mechanische Umsetzung, ohne dass irgendwo ein Modellname hart verdrahtet
wird. Eine per Projekt gesetzte **Modell-Policy** wird beim Anlegen eines Runs
erzwungen und attestiert (`RUN_MODELL_AUFGELOEST`) — damit ist im Nachhinein
belegbar, welches Modell wirklich gearbeitet hat.

## 6.5 Sandbox-Modell

`ExecutionSandboxFactory` wählt zwischen zwei Varianten (Setting
`execution.sandbox.variant`):

**`LocalProcessSandbox`** (Default)
- eigener Prozess je Run, Arbeitsverzeichnis = Workspace,
- Umgebungsvariablen sauber pro Prozess gesetzt (kein globales `setenv`),
- `EnvAllowlist` — nur freigegebene Variablen erreichen den Agenten,
- hartes Terminieren bei Abbruch/Timeout (`destroyForcibly()`),
- zeilenweises Mitschreiben von `stdout`/`stderr`.

**`ContainerProcessSandbox`** (ADR-0011, Variante B, seit v0.7.0 *Accepted*)
- ephemerer Docker-/Podman-Container je Agentenlauf,
- `--cpus 2 --memory 4g --pids-limit 512 --read-only`,
- Bindmount ausschließlich auf den Workspace,
- **`--network=none` als Default**,
- fehlt Docker im PATH, fällt die Factory mit Warnung auf lokal zurück.

Die Netzwerksperre als Default ist eine starke Aussage: Ein Coding-Agent
braucht im Normalfall keinen ausgehenden Netzzugriff — Abhängigkeiten kommen
aus dem vorbereiteten Workspace bzw. dem Cache. Wer sie öffnet, tut es
bewusst.

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
- Unbekannte Modelle werden mit 0 € bewertet — bewusst konservativ, statt zu
  raten.
- Token-Erfassung: `ClaudeUsageJsonParser` liest reale Verbrauchswerte;
  `TokenEstimator` (jtokkit) schätzt, wo der Vendor keine Werte liefert.
- Aggregation nach Projekt, Run, Provider, Mandant und **Seat** (auslösender
  Nutzer, abgeleitet aus `run.triggered_by`); CSV-Export je Sicht.
- **Harte Budget-Caps** pro Mandant (`mandant_budget`, V28) sowie Tages-/
  Wochenlimits mit Soft-Schwelle; überschrittene Caps verhindern neue Läufe.
- *Grenze:* Der harte Cap wirkt je Mandant, nicht je Seat — die Seat-Sicht
  wertet aus, sie begrenzt nicht.
