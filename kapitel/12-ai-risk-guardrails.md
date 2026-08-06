# 12 AI Risk Framework & Guardrails

Beim Einsatz agentischer Entwicklungssysteme besteht eine zentrale Herausforderung darin, sicherzustellen, dass generierter Code nicht nur syntaktisch korrekt ist, sondern auch sicher, architekturkonform und fachlich valide bleibt.

Dazu wird eine mehrstufige Guardrails-Pipeline eingesetzt, die jede durch Agenten erzeugte Codeänderung automatisch validiert.

![Validierungs- und Governance-Pipeline](abbildungen/out/abb12.pdf){width=100%}

Jede durch Agenten erzeugte Änderung durchläuft eine Reihe automatisierter Prüfungen. Dazu gehören statische Codeanalyse, Security-Scans, architektonische Validierung sowie automatisierte Tests.

Erst wenn alle Prüfungen erfolgreich abgeschlossen sind, kann eine Änderung in die Codebasis integriert oder für ein Deployment freigegeben werden.

Die Pipeline ist als Defense-in-Depth-Modell angelegt: Mehrere
unterschiedlich arbeitende Prüfungen reduzieren das Risiko, dass ein
einzelner Fehler unbemerkt bleibt. Die ersten fünf Stufen prüfen überwiegend
deterministische Kriterien; die LLM-basierte letzte Stufe kann zusätzliche
kontextuelle Auffälligkeiten identifizieren, die vom konfigurierten
Regelwerk nicht erfasst werden — sie ist damit selbst nichtdeterministisch.
Der Prüf**prozess** ist reproduzierbar, die Prüf**ergebnisse** sind es auf
dieser Stufe nur eingeschränkt. Eine vollständige Fehlererkennung wird
nicht behauptet.

Guardrails erzwingen definierte technische Mindestkriterien, liefern strukturierte Befunde und reduzieren das Risiko ungeprüfter Änderungen. Sie ersetzen weder fachliche Abnahme noch unabhängige Sicherheitsprüfung oder Produktionsbeobachtung.

![AI-Guardrails-Pipeline zur Validierung agentisch erzeugter Codeänderungen](abbildungen/out/abb13.pdf){width=100%}

| Komponente | Funktion | Umsetzung |
| --- | --- | --- |
| Claim Verification (in v1.3: Halluzinations-Erkennung) | Prüft ob Code auf existierenden Patterns basiert | Grep/AST-Analyse vor Commit |
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
    public Object enforce(ProceedingJoinPoint jp,
            ConfidenceScore cs) throws Throwable {
        if (cs.value() == ConfidenceScore.Level.LOW) {
            log.warn("[CONFIDENCE LOW] {} - {}", jp.getSignature().toShortString(),
                    cs.rationale());
            knowledgeStore.store("findings",
                    "confidence-" + jp.getSignature().hashCode(),
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

> **Praxis-Check SoftwareFabrik (erweitert):** Die Guardrails-Pipeline ist
> als eigener Schichtbegriff umgesetzt: Read-only-Review-Adapter, getrennt
> von den schreibenden Agenten. Sechs Review-Adapter — nicht deckungsgleich
> mit den sechs Pipeline-Stufen oben: zwei LLM-Reviewer, drei statische
> Prüfer, ein werkzeuggestützter Dependency-Scan —, eine konfigurierbare
> Gate-Policy mit drei nicht
> aufweichbaren Sonderregeln und drei Betriebsmodi (off/advisory/blocking);
> das Confidence Scoring ist ohne AOP im Gate-Service gelöst (19.5).
