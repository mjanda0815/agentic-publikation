# 4 Konfiguration mit CLAUDE.md

CLAUDE.md ist die zentrale Konfigurationsdatei für das Agenten-Verhalten, Team-Standards und Projektregeln. Sie funktioniert wie eine Kombination aus .editorconfig, ESLint-Konfiguration und Architektur-Dokumentation – nur für KI-Agenten. Die Datei ist Klartext im Markdown-Format und wird von jedem Agenten beim Context Build (Lifecycle-Phase 2) automatisch geladen. Damit ist CLAUDE.md die operative Umsetzung des Prinzips AP-5 (Policy-Driven Development): Was hier steht, wird durchgesetzt.

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
| Agentendefinitionen | Welche Custom Agents existieren, mit welchen Tools und Rollen | Steuert AP-1 (Agent Specialization) und das Berechtigungsmodell |
| Projektstandards | Java-Version, Style Guide, Framework-Versionen, Package-Struktur | Agenten generieren Code konform zu diesen Standards |
| DDD-Regeln | Bounded Contexts, Glossar-Pfad, Event-Naming, Context Map | Domain-Hooks prüfen gegen diese Regeln (AP-3) |
| Architekturregeln | Erlaubte Patterns, verbotene Anti-Patterns, Schichtentrennung | Review-Agent nutzt diese als Prüfkatalog |
| Cost Controls | Default-Modell, max_turns, Budget-Limits, Eskalationsregeln | Steuert Execution Budget (Kap. 7) und Token Budget (Kap. 14) |
| Hooks & MCP | PreToolUse/PostToolUse Hooks, MCP-Server-Referenzen | Governance by Design (AP-3) durch automatische Validierung |
| Verbotene Aktionen | Dateien/Pfade die nie geändert werden dürfen, gesperrte Kommandos | Sicherheitsleitplanken über das Tool-Whitelisting hinaus |

<!-- TODO(verify): Die Verweise "Kap. 7" (Execution Budget) und "Kap. 14" (Token Budget) in der Tabellenzeile "Cost Controls" stimmen im Original (S. 15) nicht mit der tatsächlichen Kapitelnummerierung überein (Execution Budget steht in Kap. 7 – das passt –, Token Budget Management steht jedoch in Kap. 15 "Wirtschaftlichkeit & Kostenmodell", nicht Kap. 14 "Security Model"). Wörtlich aus dem Original übernommen, nicht korrigiert – siehe TODO.md. -->

## 4.2 Vollständiges Enterprise-Beispiel

Das folgende Beispiel zeigt eine produktionsreife CLAUDE.md für ein Banking-Projekt. Jede Sektion ist kommentiert, um die Wirkung auf das Agenten-Verhalten zu erklären:

```markdown
# ============================================================
# Projekt: Banking-Plattform (Export Manager)
# Team: Backend Engineering, BAFA Modernisierung
# ============================================================

# --- Agentendefinitionen ---
# Jeder Agent hat: Name, Rolle, erlaubte Tools, Beschränkungen
# Dies setzt AP-1 (Agent Specialization) operativ um.

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
# Verhindert unkontrollierten API-Verbrauch (siehe Kap. 14).

## Budget-Limits
- DEFAULT_MODEL: sonnet
- MAX_TURNS_DEFAULT: 15
- MAX_TURNS_REVIEW: 8
- SPRINT_BUDGET_USD: 200
- FEATURE_BUDGET_USD: 50
- ALERT_THRESHOLD: 0.8

## Modell-Eskalation
- opus NUR für: Architektur-ADRs, Security Reviews, Halluzinationsprüfung
- haiku NUR für: Code-Formatierung, einfache Umbenennung, Docs ohne Fachlogik

# --- Hooks ---
# Automatische Validierung bei jeder Tool-Nutzung (AP-3).

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
