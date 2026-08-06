# 4 Konfiguration mit CLAUDE.md

CLAUDE.md ist die zentrale Konfigurationsdatei für das Agenten-Verhalten, Team-Standards und Projektregeln. Sie funktioniert wie eine Kombination aus .editorconfig, ESLint-Konfiguration und Architektur-Dokumentation – nur für KI-Agenten. Die Datei ist Klartext im Markdown-Format und wird von jedem Agenten beim Context Build (Lifecycle-Phase 2) automatisch geladen. CLAUDE.md bzw. AGENTS.md stellt dem Agenten verbindlich formulierte Projektregeln als Kontext bereit — die deklarative Hälfte von AP-5 (Policy as Executable Structure). Technische Erzwingung entsteht erst durch Tool-Beschränkungen, Hooks, Sandbox und nachgelagerte Quality Gates.

> **Aktualisierung (Stand August 2026):** Seit v1.3 hat sich mit `AGENTS.md`
> ein werkzeugübergreifender De-facto-Standard für genau diese Datei
> etabliert — ein offenes Format, das inzwischen von den großen
> Coding-Agenten (u. a. Codex, GitHub Copilot, Cursor, Gemini CLI)
> unterstützt und unter dem Dach der Agentic AI Foundation der Linux
> Foundation gepflegt wird [@agentsmd]. Claude Code liest weiterhin
> CLAUDE.md. Die Empfehlung für vendor-neutrale Projekte lautet daher: die
> Regeln **einmal** in `AGENTS.md` pflegen und werkzeugspezifische Dateien
> wie CLAUDE.md als minimale Verweise darauf anlegen — eine Quelle, mehrere
> Projektionen. Alles, was dieses Kapitel über Aufbau, Vererbung und Wirkung
> der Datei sagt, gilt unabhängig vom Dateinamen.

> **Praxis-Check SoftwareFabrik (erweitert):** Genau dieses Muster ist
> dort implementiert: Die Engineering-Guardrails liegen als eine
> versionierte Quelle vor und werden bei jedem Lauf als `AGENTS.md` plus
> minimaler CLAUDE.md-Verweis ins Repository projiziert; welche Version
> gewirkt hat, wird attestiert (19.6).

## Konfigurationsebenen

CLAUDE.md folgt einem dreistufigen Vererbungsmodell. Höhere Ebenen können durch niedrigere überschrieben werden, ähnlich wie CSS-Spezifizität:

| Geltungsbereich | Ort | Zweck |
| --- | --- | --- |
| Global (Nutzer) | ~/.claude/CLAUDE.md | Persönliche Defaults für alle Projekte: bevorzugter Stil, Standardsprache, globale Regeln |
| Projekt (Team) | ./CLAUDE.md (Repo-Root) | Team-gemeinsame Konfigurationen: Agentendefinitionen, Architekturregeln, DDD-Glossar, CI/CD-Standards |
| Lokal (Entwickler) | ./CLAUDE.local.md | Persönliche Overrides (nicht im Git): IDE-Pfade, lokale DB-URLs, experimentelle Flags |

Die Vererbung funktioniert so: Global definiert Baselines, Projekt überschreibt für das Team, Lokal überschreibt für den einzelnen Entwickler. Konflikte werden nach dem Last-Wins-Prinzip aufgelöst – die spezifischste Konfiguration gewinnt.

## 4.1 Aufbau und Sektionen

Eine vollständige CLAUDE.md besteht aus mehreren klar abgegrenzten Sektionen. Jede Sektion adressiert einen spezifischen Aspekt der Agenten-Steuerung:

| Sektion | Inhalt | Wirkung |
| --- | --- | --- |
| Agentendefinitionen | Welche Custom Agents existieren, mit welchen Tools und Rollen | Steuert die Rollen-/Capability-Zuordnung (vgl. Kap. 2) und das Berechtigungsmodell |
| Projektstandards | Java-Version, Style Guide, Framework-Versionen, Package-Struktur | Agenten generieren Code konform zu diesen Standards |
| DDD-Regeln | Bounded Contexts, Glossar-Pfad, Event-Naming, Context Map | Domain-Hooks prüfen gegen diese Regeln (AP-5) |
| Architekturregeln | Erlaubte Patterns, verbotene Anti-Patterns, Schichtentrennung | Review-Agent nutzt diese als Prüfkatalog |
| Cost Controls | Default-Modell, Budget-Limits, Eskalationsregeln | Steuert Execution Budget (Kap. 7) und Token Budget (Kap. 15) |
| Hooks & MCP | PreToolUse/PostToolUse Hooks, MCP-Server-Referenzen | Automatische Validierung als Teil von AP-5/AP-7 |
| Verbotene Aktionen | Dateien/Pfade die nie geändert werden dürfen, gesperrte Kommandos | Sicherheitsleitplanken über das Tool-Whitelisting hinaus |

## 4.2 Vollständiges Enterprise-Beispiel

Das folgende Beispiel zeigt eine produktionsnahe CLAUDE.md für ein fiktives Behördenprojekt der Exportkontrolle. Jede Sektion ist kommentiert, um die Wirkung auf das Agenten-Verhalten zu erklären:

```markdown
# ============================================================
# Projekt: Behoerdenplattform Exportkontrolle (fiktives Beispiel)
# Team: Backend Engineering, Modernisierungsprogramm
# ============================================================

# --- Agentendefinitionen ---
# Jeder Agent hat: Name, Rolle, erlaubte Tools, Beschränkungen
# Dies setzt die Rollen-/Capability-Zuordnung (vgl. Kap. 2) operativ um.

## Agenten
- architecture-agent: Analysiert Systemdesign, erstellt ADRs.
  Tools: Read, Glob, Grep, LSP, WebFetch
  Modell: opus (für maximale Analysetiefe)
  Einschränkung: Kein Schreibzugriff auf Code

- dev-agent: Implementiert Features nach Projektstandards.
  Tools: Read, Write, Edit, Glob, Grep, Bash, LSP
  Modell: sonnet (Kosten-/Qualitätsbalance)
  Regel: MUSS bestehenden Code lesen BEVOR Änderungen vorgenommen werden

- test-agent: Schreibt und führt Tests aus.
  Tools: Read, Write, Edit, Bash, Glob, Grep
  Regel: Iteriert bis 100% Bestehensrate
  Einschränkung: Darf nur Dateien in src/test/ ändern

- review-agent: Prüft Code auf Qualität und Sicherheit.
  Tools: Read, Glob, Grep, LSP
  Modell: opus (Security-relevante Analyse)
  Einschränkung: Kein Schreibzugriff

- deploy-agent: Erstellt IaC-Artefakte.
  Tools: Read, Write, Edit, Bash
  Einschränkung: Darf nur Dateien in deploy/ und k8s/ ändern

# --- Projektstandards ---
# Agenten generieren Code EXAKT nach diesen Vorgaben.

## Technologie-Stack
- Java 21 LTS, Google Java Style Guide
- Spring Boot 3.4, Maven Multi-Module
- JUnit 5, Testcontainers, WireMock
- Angular 21 (Frontend), NX Monorepo
- Camunda 8 (BPMN Workflow Engine)

## Package-Struktur
- com.company.{bounded-context}.domain             # Entities, Value Objects, Events
- com.company.{bounded-context}.application        # Services, Use Cases
- com.company.{bounded-context}.adapter.in         # REST Controller, GraphQL
- com.company.{bounded-context}.adapter.out        # JPA Repos, Kafka, External APIs
- com.company.{bounded-context}.config             # Spring Configuration

## Code-Konventionen
- Constructor Injection (kein @Autowired auf Feldern)
- @Slf4j für Logging (kein System.out)
- Records für DTOs und Value Objects
- Sealed Interfaces für Strategy Patterns
- @Transactional nur auf Service-Layer

# --- DDD-Regeln ---
# Definiert fachliche Grenzen, die Agenten einhalten MÜSSEN.

## Bounded Contexts
- ausfuhr-context: Ausfuhrgenehmigungen, KN-Codes, TARIC
- pruefung-context: Prüfverfahren, Vier-Augen-Prinzip
- stammdaten-context: Antragsteller, Firmen, Adressen
- dokument-context: Dokumenten-Upload, Signierung

## Ubiquitous Language
- Glossar: docs/domain/glossary.md (MUSS vor jeder Implementierung gelesen werden)
- Context Map: docs/domain/context-map.json
- Events folgen: {Aggregate}{Verb}Event (z.B. AntragEingereichtEvent)

## Verbotene Übergriffe
- ausfuhr-context darf NICHT direkt auf stammdaten-context zugreifen
- Kommunikation zwischen Contexts NUR über Domain Events (Kafka)
- Keine JPA-Beziehungen über Context-Grenzen hinweg

# --- Cost Controls ---
# Verhindert unkontrollierten API-Verbrauch (siehe Kap. 15).

## Budget-Limits
- DEFAULT_MODEL: sonnet
- MAX_TURNS_DEFAULT: 15
- MAX_TURNS_REVIEW: 8
- SPRINT_BUDGET_USD: 200
- FEATURE_BUDGET_USD: 50
- ALERT_THRESHOLD: 0.8

## Modell-Eskalation
- opus NUR für: Architektur-ADRs, Security Reviews, Claim Verification
- haiku NUR für: Code-Formatierung, einfache Umbenennung, Docs ohne Fachlogik

# --- Hooks ---
# Automatische Validierung bei jeder Tool-Nutzung (AP-5/AP-7).

## PreToolUse
- Pfad-Whitelist: Schreibzugriffe nur auf src/, test/, docs/, deploy/
- Gesperrte Pfade: .env, secrets/, credentials.properties, CLAUDE.md
- Gesperrte Kommandos: rm -rf, DROP TABLE, curl (ohne Whitelist)

## PostToolUse
- checkstyle: Google Java Style (nach jedem Write/Edit)
- domain-compliance: Bounded Context Check (nach jedem Write in src/)
- secret-scanner: Credential-Erkennung (nach jedem Write/Edit)

# --- MCP-Server ---
# Externe Tool-Integrationen (Jira, DB, Confluence).

## Verfügbare Server
- jira-server: Sprint-Tickets, User Stories, Akzeptanzkriterien
- postgres-server: Datenbank-Schema-Abfragen (readonly!)
- confluence-server: Architektur-Dokumentation lesen

# --- Verbotene Aktionen ---
# Absolute Grenzen, die KEIN Agent überschreiten darf.

## Niemals
- Produktionsdatenbanken ändern oder löschen
- Credentials oder Secrets in Code oder Logs schreiben
- Dependencies ohne OWASP-Check hinzufügen
- Direkt auf main/master pushen (immer Feature-Branch + PR)
- CLAUDE.md selbst ändern
```

## 4.3 CLAUDE.md im Team-Workflow

CLAUDE.md ist eine Datei im Repository und unterliegt damit denselben Prozessen wie jeder andere Code: Sie wird versioniert, reviewed und über Pull Requests geändert. Das bedeutet, dass Änderungen an Agenten-Konfigurationen denselben Quality Gates unterliegen wie Codeänderungen – ein wichtiger Aspekt für Audit-Compliance.

In der Praxis empfiehlt sich folgendes Vorgehen: Das Team definiert die initiale CLAUDE.md gemeinsam in einem Architecture Workshop. Der Architektur-Agent wird als Erster konfiguriert, da seine Findings die Basis für alle anderen Agenten bilden. Anschließend werden die übrigen Agenten schrittweise hinzugefügt und in einem Pilotfeature getestet. Erkenntnisse aus dem Piloten fließen als Änderungen an CLAUDE.md zurück – der typische Feedback-Loop dauert 2–3 Sprints, bis die Konfiguration stabil ist.

> **Hinweis:** CLAUDE.md ist das mächtigste Steuerungsinstrument im Agentensystem. Eine gut gepflegte Konfiguration macht den Unterschied zwischen einem nützlichen Werkzeug und einer unkontrollierbaren Black Box. Investieren Sie Zeit in die initiale Konfiguration – es zahlt sich in jedem Sprint mehrfach aus.
