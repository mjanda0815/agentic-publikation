# 7 Execution Model

> **Hinweis:** Abgrenzung: Kapitel 6 (Lifecycle) beschreibt die Phasen eines einzelnen Agenten. Dieses Kapitel beschreibt, wie der Orchestrator mehrere Agenten als Workflow plant, steuert und terminiert. Kapitel 16 (Workflows) zeigt die konkreten Aufruf-Patterns.


Das Execution Model beschreibt, wie der Orchestrator Aufgaben plant, verteilt, überwacht und terminiert. Es ist das operative Herzstück des Agentensystems und setzt die architektonischen Prinzipien AP-1 (Controlled Non-Determinism) und AP-5 (Policy as Executable Structure) in die Praxis um.

![Execution Pipeline — vom Entwicklungsziel über den Task-Graph bis zum Pull Request](abbildungen/out/abb06.pdf){width=100%}

## 7.1 Task Graph

Jeder Workflow wird intern als gerichteter azyklischer Graph (DAG) repräsentiert. Knoten sind Tasks, Kanten sind Abhängigkeiten. Der Orchestrator traversiert den Graphen und startet Tasks, sobald alle Vorgänger abgeschlossen sind:

```java
// === Task Graph Modell ===
public record TaskGraph(
        String workflowId,
        Map<String, TaskNode> nodes,
        Map<String, Set<String>> edges        // taskId -> dependsOn
) {
    public record TaskNode(
            String taskId,
            String agentType,
            String model,
            String prompt,
            TaskStatus status,
            @Nullable String resultRef
    ) {}

    public enum TaskStatus { PENDING, READY, RUNNING, COMPLETED, FAILED, SKIPPED }

    // Nächste ausführbare Tasks (alle Abhängigkeiten erfüllt)
    public List<TaskNode> readyTasks() {
        return nodes.values().stream()
                .filter(n -> n.status() == TaskStatus.PENDING)
                .filter(n -> {
                    Set<String> deps = edges.getOrDefault(n.taskId(), Set.of());
                    return deps.stream().allMatch(depId ->
                             nodes.get(depId).status() == TaskStatus.COMPLETED);
                }).toList();
    }

    public boolean isTerminal() {
        return nodes.values().stream().allMatch(n ->
                n.status() == TaskStatus.COMPLETED
                || n.status() == TaskStatus.FAILED
                || n.status() == TaskStatus.SKIPPED);
    }
}
```

## 7.2 Runtime Execution Flow

Nachdem der Task Graph erzeugt wurde, stellt sich die Frage, wie ein konkreter Entwicklungsauftrag während der Laufzeit durch das Agentensystem verarbeitet wird.

![Laufzeitablauf eines Entwicklungsauftrags](abbildungen/out/abb07.pdf){width=100%}

Die Abbildung zeigt den typischen Ablauf eines Entwicklungsauftrags innerhalb eines agentischen Entwicklungssystems.

Ein Entwicklungsziel wird zunächst vom Orchestrator entgegengenommen, der als zentrale Steuerungseinheit fungiert. Der Orchestrator erzeugt einen Task Graph, der die notwendigen Arbeitsschritte und deren Abhängigkeiten beschreibt.

Anschließend delegiert der Orchestrator Teilaufgaben an spezialisierte Agenten. Requirements-, Architektur- und Planungsagenten analysieren zunächst Anforderungen und Systemkontext. Darauf aufbauend implementiert der Development-Agent die erforderlichen Änderungen im Code.

Die erzeugten Artefakte werden anschließend durch Testing- und Review-Agenten validiert. Diese prüfen Funktionalität, Codequalität und Sicherheitsanforderungen. Erst nach erfolgreicher Validierung wird ein Pull Request erzeugt oder ein Deployment vorbereitet.

Dieser Ablauf ermöglicht eine klare Trennung der Verantwortlichkeiten zwischen den Agenten und erlaubt sowohl sequenzielle als auch parallele Ausführung einzelner Schritte — parallel jedoch nur für read-only-Schritte oder bei getrennten Workspaces mit abgegrenzten Schreibbereichen (AP-2/AP-3, Kapitel 2).

## 7.3 State Machine & Stop-Conditions

Der Orchestrator implementiert eine State Machine, die den Workflow-Zustand verwaltet. Zustandswechsel werden durch Agenten-Ergebnisse, Budgetgrenzen oder externe Signale ausgelöst. Stop-Conditions definieren, wann ein Workflow vorzeitig beendet wird:

| Stop-Condition | Auslöser | Verhalten |
| --- | --- | --- |
| Budget exhausted | Token- oder Kosten-Budget überschritten | Alle laufenden Agenten beenden, Ergebnisse sichern |
| Critical failure | Agent meldet CRITICAL Finding | Workflow stoppen, Human-in-the-Loop eskalieren |
| Max retries exceeded | Agent scheitert N-mal am gleichen Task | Task als FAILED markieren, Workflow fortsetzen |
| Timeout | Wanduhrzeit überschritten | Laufende Agenten terminieren, Teilresultate sichern |
| External signal | Menschliche Intervention / CI-Abbruch | Graceful Shutdown aller Agenten |
| Quality gate failed | Code Coverage < Schwellenwert | Zurück zur Testing-Phase, Retry-Counter erhöhen |

<!-- Extraktion: Nummerierung korrigiert, Original hatte 7.3 doppelt -->

## 7.4 Execution Budget

Das Execution Budget ist ein zweilagiges Sicherheitsnetz: Es begrenzt sowohl einzelne Tasks (Turn-Limit (maxTurns), timeout) als auch den Gesamtworkflow (max_cost, max_duration). Budgets werden pro Sprint, Feature oder Team definiert:

```java
// === Execution Budget ===
public record ExecutionBudget(
        int maxTurnsPerTask,
        Duration maxDurationPerTask,
        BigDecimal maxCostPerTask,
        BigDecimal maxCostPerWorkflow,
        int maxRetriesPerTask,
        int maxParallelAgents
) {
    public static ExecutionBudget standard() {
        return new ExecutionBudget(15, Duration.ofMinutes(5),
                new BigDecimal("5.00"), new BigDecimal("50.00"), 3, 4);
    }

    public static ExecutionBudget conservative() {
        return new ExecutionBudget(10, Duration.ofMinutes(3),
                new BigDecimal("2.00"), new BigDecimal("20.00"), 2, 2);
    }

    public static ExecutionBudget aggressive() {
        // maxParallelAgents gilt nur fuer read-only-Schritte oder Agenten in
        // getrennten Workspaces — ein Schreiber je Arbeitskopie (AP-2).
        return new ExecutionBudget(25, Duration.ofMinutes(10),
                new BigDecimal("10.00"), new BigDecimal("100.00"), 5, 7);
    }
}
```

## 7.5 Retry-Strategie

Nicht jeder Fehlschlag erfordert menschliche Intervention. Die Retry-Strategie definiert, welche Fehler automatisch wiederholt werden, mit welcher Eskalation und bis zu welchem Limit:

| Fehlerart | Retry? | Strategie | Eskalation |
| --- | --- | --- | --- |
| Kompilierungsfehler | Ja (max 3x) | Agent korrigiert selbst | Nach 3x: Review-Agent |
| Test-Failure | Ja (max 5x) | Iterative Korrektur | Nach 5x: Human-in-the-Loop |
| Security Finding (CRITICAL) | Nein | Sofortige Eskalation | Human-in-the-Loop + Audit |
| Domain-Verletzung | Ja (max 2x) | Glossar neu laden | Nach 2x: Architecture-Agent |
| API/Tool Timeout | Ja (exponential) | 1s, 2s, 4s Backoff | Nach 3x: Task als FAILED |
| Halluzinierte API | Nein | Sofortige Korrektur | Review-Agent mit opus |

> **Praxis-Check SoftwareFabrik (abweichend, erweitert):** Statt eines
> Task-Graphen je Auftrag eine lineare Phasen-Pipeline je Lauf — der
> eigentliche Graph liegt eine Ebene höher im Backlog mit Abhängigkeiten.
> Und aus der Retry-Strategie wurde ein Regelkreis: Build-Ausgabe,
> Reviewer-Findings, Merge-Konfliktdateien und CI-Status werden zur Eingabe
> des nächsten Laufs — ein Retry ohne neue Information wiederholt nur den
> Fehler (19.3, 19.8).
