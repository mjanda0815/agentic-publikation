# 6 Agent Lifecycle

> **Hinweis:** Abgrenzung: Dieses Kapitel beschreibt den Lebenszyklus eines einzelnen Agenten. Das Execution Model (Kap. 7) beschreibt die Orchestrierung mehrerer Agenten. Die Workflow-Patterns (Kap. 16) zeigen die konkreten Aufruf-Beispiele.


Jeder Claude Code Agent durchläuft einen definierten Lebenszyklus von der Erstellung bis zur Terminierung. Das Verständnis dieses Lifecycles ist entscheidend für die Konfiguration von Timeouts, Budget-Limits und Retry-Strategien. Der Lifecycle besteht aus acht klar abgegrenzten Phasen:

| # | Phase | Beschreibung |
| --- | --- | --- |
| 1 | Spawn | Der Orchestrator erzeugt den Subagenten über das Agent-Tool (in v1.3: „Task“, vgl. 3.5) mit Typ, Prompt, Modell und optionalen Parametern (`run_in_background`); die Turn-Obergrenze `maxTurns` und die Worktree-Isolation stehen in der Subagenten-Definition. Der Agent erhält eine eindeutige Agent-ID. |
| 2 | Context Build | Der Agent lädt seinen Arbeitskontext: CLAUDE.md-Konfiguration, relevante Dateien aus dem Repository, Einträge aus dem Shared Knowledge Store und den Prompt des Orchestrators. Diese Phase bestimmt maßgeblich den Token-Verbrauch. |
| 3 | Planning | Der Agent analysiert die Aufgabe und erstellt einen internen Ausführungsplan. Bei komplexen Tasks wird dieser Plan explizit als Implementierungs-Tracker persistiert. Der Planungsschritt ist bei implementation-planner Agenten die Hauptausgabe. |
| 4 | Execution | Die Kernarbeit: Der Agent führt die geplanten Schritte aus, ruft Tools auf und generiert Artefakte. Jeder API-Roundtrip zählt als ein "Turn" gegen das maxTurns-Limit. Die Execution-Phase kann mehrere Tool-Aufrufe pro Turn umfassen. |
| 5 | Tool Interaction | Innerhalb der Execution-Phase interagiert der Agent mit seinem definierten Werkzeugset. Jede Tool-Nutzung wird durch PreToolUse- und PostToolUse-Hooks validiert. Werkzeugzugriffe außerhalb der Konfiguration werden blockiert. |
| 6 | Validation | Nach Abschluss der Execution durchläuft der Output die Guardrails-Pipeline: Syntax, Style, Security, Domain-Compliance, Tests und Confidence Scoring. Bei Fehlern wird der Agent in die Execution-Phase zurückgesetzt (Retry-Loop). |
| 7 | Memory Update | Erkenntnisse, Findings und Entscheidungen werden in den Shared Knowledge Store geschrieben. Dieser Schritt ist essentiell für die Wissensübergabe an nachfolgende Agenten im Workflow. Er läuft vor dem endgültigen Übergang nach `TERMINATED` — der Endzustand erlaubt keine Übergänge mehr. |
| 8 | Termination | Der Agent beendet sich durch: (a) erfolgreichen Abschluss, (b) Erreichen von maxTurns, (c) Budget-Erschöpfung, (d) explizite Stop-Condition, oder (e) Fehler-Eskalation. Das Ergebnis wird an den Orchestrator zurückgegeben. |

> **Praxis-Check SoftwareFabrik (erweitert):** Der Lebenszyklus ist dort als
> *Run* modelliert: sieben Phasen, 13 Zustände, persistiert, pausier- und
> wiederaufnehmbar. Der Mensch ist als Zustand (`WAITING_FOR_APPROVAL`) Teil
> des Automaten, nicht Nebenprozess (19.3).

> **Versionshinweis (v2.2, gilt für Teil II):** Die Java-Beispiele der
> Kapitel 6 bis 9 sind Modell-Skizzen zur Illustration des jeweiligen
> Konzepts, formuliert gegen Java 21 LTS und Spring Boot 3.x. Sie sind
> gekürzt (Imports, Konstruktoren, Exception-Handling teilweise
> weggelassen) und nicht als lauffähige Bibliothek getestet. Der
> Produktivstand des in Kapitel 19 beschriebenen Systems ist Java 25 und
> Spring Boot 4.0.

## Java-Beispiel: Agent Lifecycle Manager

```java
// === Agent Lifecycle State Machine ===
public class AgentLifecycle {

    public enum Phase {
        SPAWNED, CONTEXT_BUILDING, PLANNING, EXECUTING,
        TOOL_INTERACTION, VALIDATING, TERMINATED, MEMORY_UPDATING;

        public Set<Phase> allowedTransitions() {
            return switch (this) {
                case SPAWNED -> Set.of(CONTEXT_BUILDING);
                case CONTEXT_BUILDING -> Set.of(PLANNING);
                case PLANNING -> Set.of(EXECUTING, TERMINATED);
                case EXECUTING -> Set.of(TOOL_INTERACTION, VALIDATING, TERMINATED);
                case TOOL_INTERACTION -> Set.of(EXECUTING);
                case VALIDATING -> Set.of(EXECUTING, MEMORY_UPDATING, TERMINATED);
                case MEMORY_UPDATING -> Set.of(TERMINATED);
                case TERMINATED -> Set.of();
            };
        }
    }

    public record AgentState(
            String agentId,
            String agentType,
            Phase currentPhase,
            int turnsUsed,
            int maxTurns,
            Instant spawnedAt,
            @Nullable Instant terminatedAt,
            TerminationReason terminationReason,
            List<PhaseTransition> transitionLog
    ) {
        public boolean canTransitionTo(Phase target) {
            return currentPhase.allowedTransitions().contains(target);
        }

        public Duration elapsed() {
            Instant end = terminatedAt != null ? terminatedAt : Instant.now();
            return Duration.between(spawnedAt, end);
        }
    }

    public record PhaseTransition(
            Phase from, Phase to, Instant timestamp, String reason
    ) {}

    public enum TerminationReason {
        SUCCESS, MAX_TURNS_REACHED, BUDGET_EXHAUSTED,
        STOP_CONDITION, ERROR_ESCALATION, TIMEOUT
    }
}
```

> **Hinweis:** Der Agent Lifecycle ist das Fundament für das Execution Budget (Kapitel 7): Jede Phase verbraucht Tokens und Zeit. Context Build und Planning verbrauchen nach eigener Betriebserfahrung (SoftwareFabrik, Stand August 2026) rund 20–30 % des Token-Budgets, bevor die eigentliche Execution beginnt.
