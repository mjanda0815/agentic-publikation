# 12 AI Risk Framework & Guardrails

Beim Einsatz agentischer Entwicklungssysteme besteht eine zentrale Herausforderung darin, sicherzustellen, dass generierter Code nicht nur syntaktisch korrekt ist, sondern auch sicher, architekturkonform und fachlich valide bleibt.

Dazu wird eine mehrstufige Guardrails-Pipeline eingesetzt, die jede durch Agenten erzeugte Codeänderung automatisch validiert.

<!-- TODO(abbildung): Abbildung 12: Validierungs- und Governance-Pipeline -->

Jede durch Agenten erzeugte Änderung durchläuft eine Reihe automatisierter Prüfungen. Dazu gehören statische Codeanalyse, Security-Scans, architektonische Validierung sowie automatisierte Tests.

Erst wenn alle Prüfungen erfolgreich abgeschlossen sind, kann eine Änderung in die Codebasis integriert oder für ein Deployment freigegeben werden.

Diese Guardrails stellen sicher, dass KI-generierter Code denselben Qualitäts- und Sicherheitsanforderungen entspricht wie manuell entwickelte Software.

<!-- TODO(abbildung): Abbildung 13: AI-Guardrails-Pipeline zur Validierung agentisch erzeugter Codeänderungen -->

| Komponente | Funktion | Umsetzung |
| --- | --- | --- |
| Halluzinations-Erkennung | Prüft ob Code auf existierenden Patterns basiert | Grep/AST-Analyse vor Commit |
| Schema-Validierung | Validiert JSON/YAML gegen definierte Schemas | JSON Schema im PostToolUse Hook |
| Security-Scan | Statische Sicherheitsanalyse | SpotBugs, OWASP Dependency Check |
| Domain-Prüfung | Bounded Context Einhaltung | Custom Lint gegen docs/domain/ |
| Confidence Score | Agenten bewerten ihre eigene Sicherheit | Annotation + AOP-Aspekt |
| Rollback | Automatisches Zurücksetzen | Git Worktree + Cleanup |

## Confidence Scoring mit AOP-Eskalation

```java
// === Annotation ===
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.METHOD, ElementType.TYPE})
public @interface ConfidenceScore {
    Level value();
    String rationale() default "";
    enum Level {
        HIGH(90, "Pattern existiert in Codebasis"),
        MEDIUM(65, "Best Practice, kein Vorbild"),
        LOW(30, "Unsicher, Review erforderlich");
        private final int score; private final String desc;
        Level(int s, String d) { this.score = s; this.desc = d; }
    }
}

// === AOP Aspekt ===
@Aspect @Component @Slf4j
public class ConfidenceScoreAspect {
    private final KnowledgeStoreClient knowledgeStore;

    @Around("@annotation(cs) || @within(cs)")
    public Object enforce(ProceedingJoinPoint jp, ConfidenceScore cs) throws Throwable {
        if (cs.value() == ConfidenceScore.Level.LOW) {
            log.warn("[CONFIDENCE LOW] {} - {}", jp.getSignature().toShortString(), cs.rationale());
            knowledgeStore.store("findings", "confidence-" + jp.getSignature().hashCode(),
                    new ReviewFinding(jp.getSignature().toShortString(), cs.value(),
                             cs.rationale(), Instant.now()));
        }
        return jp.proceed();
    }
}
```

| Schritt | Prüfung | Bei Fehler |
| --- | --- | --- |
| 1. Syntax | mvn compile | Agent korrigiert automatisch |
| 2. Style | Checkstyle, Google Java Style Guide | Agent formatiert nach |
| 3. Security | SpotBugs + OWASP | CRITICAL-Findings markiert |
| 4. Domain | Bounded Context, Glossar | Agent gestoppt + informiert |
| 5. Tests | JUnit 5 + Coverage min. 80% | Agent iteriert |
| 6. Confidence | LOW-Stellen gezählt | Weiterleitung an review-agent |
