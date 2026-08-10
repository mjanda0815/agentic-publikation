# 9 Failure Handling & Resilience

> **Hinweis:** In Enterprise-Umgebungen ist nicht die Frage ob, sondern wann ein Agent scheitert. Ein robustes Failure-Handling-Modell ist der Unterschied zwischen einem Prototyp und einem produktionsreifen System.

Das Failure-Handling-Modell definiert fünf Eskalationsstufen, die je nach Schwere und Art des Fehlers greifen. Das Modell folgt dem Prinzip „automatisiere was möglich, eskaliere was nötig“:

| # | Strategie | Beschreibung | Anwendungsfall |
| --- | --- | --- | --- |
| 1 | Retry | Automatische Wiederholung mit gleicher oder angepasster Konfiguration. Exponential Backoff für transiente Fehler. | Kompilierungsfehler, API-Timeouts, flaky Tests |
| 2 | Rollback | Automatisches Zurücksetzen auf den letzten konsistenten Zustand über Git Worktree Reset. | Fehlgeschlagene Refactorings, kaputte Abhängigkeiten |
| 3 | Escalation | Weiterleitung an einen spezialisierten Agent (z. B. review-agent mit opus für Claim Verification). | LOW Confidence Score, wiederkehrende Fehler |
| 4 | Human Intervention | Eskalation an einen menschlichen Entwickler mit vollständigem Kontext (Findings, Logs, Diff). | Security CRITICAL, Domain-Verletzungen, Budget-Erschöpfung |
| 5 | Compensation | Gegenläufige Aktion zur Wiederherstellung eines konsistenten Gesamtzustands bei verteilten Workflows. | Wenn parallele Worktrees inkonsistent werden |

## Java-Beispiel: Failure Handler mit Eskalationslogik

```java
// === Failure Handler ===
@Component @Slf4j
public class AgentFailureHandler {

    private final KnowledgeStoreClient knowledgeStore;

    public sealed interface FailureAction {
        record Retry(int attempt, int maxAttempts,
                Duration delay) implements FailureAction {}
        record Rollback(String worktreeId,
                String commitRef) implements FailureAction {}
        record Escalate(String targetAgent, String model,
                String context) implements FailureAction {}
        record HumanIntervention(String summary, List<String> findings,
                                  String diffRef) implements FailureAction {}
        record Compensate(List<String> compensationTasks)
                implements FailureAction {}
    }

    public FailureAction determineAction(AgentFailure failure) {
        return switch (failure.severity()) {
            case TRANSIENT -> {
                if (failure.retryCount() < 3)
                    yield new FailureAction.Retry(failure.retryCount() + 1, 3,
                            Duration.ofSeconds((long) Math.pow(2,
                                    failure.retryCount())));
                yield new FailureAction.Escalate("review-agent", "opus",
                        "Transient failure after 3 retries: " + failure.message());
            }
            case RECOVERABLE -> {
                if (failure.type() == FailureType.COMPILATION_ERROR
                        && failure.retryCount() < 3)
                    yield new FailureAction.Retry(failure.retryCount() + 1, 3,
                            Duration.ofSeconds(1));
                yield new FailureAction.Rollback(failure.worktreeId(),
                        failure.lastGoodCommit());
            }
            case CRITICAL -> new FailureAction.HumanIntervention(
                    failure.message(), failure.findings(), failure.diffRef());
            case FATAL -> {
                log.error("[FATAL] Agent {} failed irrecoverably: {}",
                        failure.agentId(),
                        failure.message());
                yield new FailureAction.Compensate(
                        List.of("revert-worktree:" + failure.worktreeId(),
                                "notify-team:" + failure.agentId(),
                                "update-findings:" + failure.taskId()));
            }
        };
    }

    public record AgentFailure(
            String agentId, String taskId, String worktreeId,
            String lastGoodCommit, String message, String diffRef,
            FailureType type, FailureSeverity severity,
            int retryCount, List<String> findings
    ) {}

    public enum FailureType { COMPILATION_ERROR, TEST_FAILURE, SECURITY_FINDING,
            DOMAIN_VIOLATION, HALLUCINATION, TIMEOUT, UNKNOWN }
    public enum FailureSeverity { TRANSIENT, RECOVERABLE, CRITICAL, FATAL }
}
```

> **Praxis-Check SoftwareFabrik (erweitert):** Fehlschlag ist dort ein
> regulärer Zustand mit definiertem Ausgang (Korrekturschleife,
> Terminalzustände). Zentrale Regel über das Konzept hinaus: Der Ausfall
> eines Prüfmechanismus darf nie wie Erfolg aussehen — ein abgestürzter
> Reviewer führt zu `ERROR`, die Lizenzprüfung ist *fail closed* (19.5,
> 19.7).
