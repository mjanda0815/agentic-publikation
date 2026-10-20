# 16 Multi-Agent-Workflows

> **Hinweis:** Abgrenzung: Die theoretischen Grundlagen (Lifecycle, Execution Model, Memory) wurden in Teil II beschrieben. Dieses Kapitel zeigt die konkreten Aufruf-Patterns für sequenzielle, parallele und asynchrone Workflows.

> **Einordnung (v2.1):** Dieses Kapitel beschreibt ein Werkzeugmuster —
> die Subagenten-Aufrufe eines Coding-Agenten —, nicht den heutigen Ablauf
> der Referenzimplementierung. Die dort gezeigte Parallelität betrifft
> Analyse und Review, also lesende Arbeit; gleichzeitig **schreibende**
> Agenten setzen die Workspace-Isolation und Koordination der
> Zielarchitektur voraus (19.10, 22.4). Der Praxis-Check am Kapitelende
> ordnet das im Detail ein.

![Sequenzieller Multi-Agent-Workflow im Software Development Lifecycle](abbildungen/out/abb15.pdf){width=100%}

Die Aufruf-Skizzen sind auf den Werkzeugstand von August 2026 aktualisiert
(Agent-Tool statt „Task“, vgl. 3.5) und als Pseudocode zu lesen
[@claudecodedocs]:

## Sequenzieller Workflow

```
// Phase 1: Architekturanalyse (muss zuerst laufen)
result1 = Agent(subagent_type="architecture-agent",
    prompt="Analysiere Auth-Architektur, schreibe in Shared Knowledge Store...")
// Phase 2: Planung (hängt von Analyse ab)
result2 = Agent(subagent_type="planning-agent",
    prompt="Lies docs/knowledge/auth-analysis.json. Erstelle Plan...")
// Phase 3: Implementierung (folgt dem Plan)
result3 = Agent(subagent_type="dev-agent",
    prompt="Lies docs/implementations/auth-tracker.md. Phase 1 umsetzen...")
```

## Paralleler Workflow

```
// Diese drei Agenten laufen PARALLEL (heute der Standardfall:
// Subagenten starten im Hintergrund). Alle drei sind LESEND — parallel
// schreibende Agenten brauchen getrennte Workspaces (AP-2, vgl. 3.5:
// isolation: worktree):
Agent(subagent_type="test-gap-agent",   prompt="Analysiere Testlücken...")
Agent(subagent_type="arch-agent",       prompt="Architektur-Review...")
Agent(subagent_type="review-agent",     prompt="Security-Review...")
```

## Background & Wiederaufnahme

```
Agent(subagent_type="test-agent", prompt="mvn test")   // läuft im Hintergrund
// Später fortsetzen: Nachricht an den (auch bereits beendeten) Agenten
// (v1.3: eigener resume-Parameter; heute Nachrichtenschnittstelle)
SendMessage(to="agent_abc123", message="Korrigiere die Fehler.")
```

> **Praxis-Check SoftwareFabrik (abweichend):** Sequenzielle,
> wiederaufnehmbare Abläufe sind der Normalfall — ein Workspace je
> Projekt, damit Folgeläufe auf dem Ergebnis der vorherigen aufbauen. Im
> Einzel-Run liegt die Mehrstimmigkeit in der Bewertung: mehrere
> unabhängige Reviewer auf demselben Diff, technisch nacheinander (19.3,
> 19.5). Parallele Läufe je Projekt gibt es seit 0.21.0 (lesend) und
> 0.22.0 (schreibend) auf der Workflow-Ebene, in getrennten Worktrees und
> hinter einem standardmäßig deaktivierten Feature-Flag (19.10).
