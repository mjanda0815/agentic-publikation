# 15 Wirtschaftlichkeit & Kostenmodell

> **Hinweis:** Agentensysteme können erhebliche API-Kosten verursachen. Ohne aktives Kostenmanagement skalieren die Ausgaben unkontrolliert. Ein transparentes Kostenmodell ist Voraussetzung für den Enterprise-Einsatz.

## 15.1 Token Budget Management

| Modell | Input (pro 1M Tokens) | Output (pro 1M Tokens) | Typischer Einsatz |
| --- | --- | --- | --- |
| opus | $15.00 | $75.00 | Architektur, Security Review |
| sonnet | $3.00 | $15.00 | Entwicklung, Testing, Planung |
| haiku | $0.25 | $1.25 | Formatierung, einfache Tasks |

<!-- TODO(verify): Preistabelle für opus/sonnet/haiku (S. 43) ist eine schnelllebige Angabe ohne Stand-Datum im Original; bei der inhaltlichen Überarbeitung gegen aktuelle Anthropic-Preisliste mit Stand-Datum prüfen. -->

Ein typischer Entwicklungs-Agent verbraucht 10.000–100.000 Tokens pro Task. Ein End-to-End-Workflow mit 7 Agenten kann 500.000–2.000.000 Tokens verbrauchen.

```java
// === Token Budget Tracker ===
public record TokenBudget(
        String budgetId, String scope,
        BigDecimal maxCostUsd, Map<String, AgentUsage> usageByAgent) {

    public record AgentUsage(String agentType, String model,
            long inputTokens, long outputTokens, BigDecimal costUsd) {}

    public BigDecimal totalCost() {
        return usageByAgent.values().stream()
                .map(AgentUsage::costUsd).reduce(BigDecimal.ZERO, BigDecimal::add);
    }
    public double utilizationPercent() {
        return totalCost().divide(maxCostUsd, 4, RoundingMode.HALF_UP)
                .multiply(BigDecimal.valueOf(100)).doubleValue();
    }
    public boolean isExhausted() { return totalCost().compareTo(maxCostUsd) >= 0; }
    public boolean isWarning() { return utilizationPercent() >= 80.0; }
}
```

## 15.2 Execution Budget & Stop-Conditions

| Parameter | Steuerung | Empfehlung |
| --- | --- | --- |
| max_turns | Maximale API-Roundtrips pro Agent | 10–25 für Entwicklung, 5–10 für Reviews |
| timeout | Maximale Laufzeit in Sekunden | 300s Standard, 600s für komplexe Tasks |
| max_cost_per_task | Kostenobergrenze pro Einzeltask | $2–5 für sonnet, $10–20 für opus |
| max_cost_per_workflow | Kostenobergrenze Gesamtworkflow | $20–50 pro Feature |
| stop_on_error | Abbruch bei Kompilier-/Testfehlern | true für Deployment, false für Entwicklung |

## 15.3 Parallelisierungskosten

| Szenario | Wanduhrzeit | Kosten |
| --- | --- | --- |
| Sequenziell: 7 Agenten | ~45 Minuten | $8–12 |
| Hybrid: 3 seq. + 4 parallel | ~25 Minuten | $8–12 (gleich) |
| Maximal parallel: 7 gleichzeitig | ~10 Minuten | $8–12 (gleich) |
| Parallel mit Retry-Schleifen | ~15 Minuten | $12–20 (höher!) |

Die Token-Kosten bleiben bei Parallelisierung identisch. Teurer wird es erst bei Merge-Konflikten und Retry-Schleifen. Deshalb ist Worktree-Isolation (AP-4) bei paralleler Ausführung Pflicht.

## 15.4 ROI-Berechnung

| Kostenfaktor | Manuell (Entwicklerteam) | KI-Agenten + Review |
| --- | --- | --- |
| Entwickleraufwand | 40h Senior Dev × €95/h = €3.800 | 8h Review + Steering = €760 |
| API-Kosten | – | ~2M Tokens ≈ €14–28 |
| Testabdeckung | Oft <60% unter Zeitdruck | >80% durch iteratives Testing |
| Time-to-Feature | 1–2 Wochen | 1–2 Tage |
| Gesamtkosten | €3.800+ | €790–€850 |

Der ROI hängt stark von der Aufgabenkomplexität ab: Bei Standard-CRUD-Features ist der Hebel am größten (5–10x). Bei komplexen Architekturentscheidungen sinkt der Automatisierungsgrad, aber der Analyse-Output (ADRs, Findings) beschleunigt die menschliche Entscheidungsfindung erheblich.

### Kostenoptimierungs-Strategie

```markdown
# Budget-bewusste CLAUDE.md Konfiguration
## Cost Controls
- DEFAULT_MODEL: sonnet              # Nie opus als Default
- MAX_TURNS_DEFAULT: 15
- SPRINT_BUDGET_USD: 200
- FEATURE_BUDGET_USD: 50
- ALERT_THRESHOLD: 0.8               # Warnung bei 80%

## Modell-Eskalation (nur bei Bedarf)
- opus NUR für: ADRs, Security Reviews, Halluzinations-Prüfung
- haiku für: Formatierung, Linting, Docs ohne Fachlogik
- sonnet für: alles andere (Default)
```
