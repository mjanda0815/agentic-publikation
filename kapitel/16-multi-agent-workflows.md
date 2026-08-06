# 16 Multi-Agent-Workflows

> **Hinweis:** Abgrenzung: Die theoretischen Grundlagen (Lifecycle, Execution Model, Memory) wurden in Teil II beschrieben. Dieses Kapitel zeigt die konkreten Aufruf-Patterns für sequenzielle, parallele und asynchrone Workflows.

<!-- TODO(abbildung): Abbildung 15: Sequenzieller Multi-Agent-Workflow im Software Development Lifecycle -->

## Sequenzieller Workflow

```
// Phase 1: Architekturanalyse (muss zuerst laufen)
result1 = Task(subagent_type="architecture-agent",
    prompt="Analysiere Auth-Architektur, schreibe in Shared Knowledge Store...")
// Phase 2: Planung (hängt von Analyse ab)
result2 = Task(subagent_type="planning-agent",
    prompt="Lies docs/knowledge/auth-analysis.json. Erstelle Plan...")
// Phase 3: Implementierung (folgt dem Plan)
result3 = Task(subagent_type="dev-agent",
    prompt="Lies docs/implementations/auth-tracker.md. Phase 1 umsetzen...")
```

## Paralleler Workflow

```
// Diese drei Agenten laufen PARALLEL:
Task(subagent_type="test-agent", prompt="JUnit 5 Tests...")
Task(subagent_type="doc-agent", prompt="OpenAPI-Dokumentation...")
Task(subagent_type="review-agent", prompt="Security-Review...")
```

## Background & Wiederaufnahme

```
Task(subagent_type="test-agent", prompt="mvn test", run_in_background=True)
// Später fortsetzen:
Task(subagent_type="dev-agent", prompt="Korrigiere Fehler.", resume="agent_abc123")
```
