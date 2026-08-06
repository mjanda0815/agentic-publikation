# 15 Wirtschaftlichkeit & Kostenmodell

> **Hinweis:** Agentensysteme können erhebliche API-Kosten verursachen. Ohne aktives Kostenmanagement skalieren die Ausgaben unkontrolliert. Ein transparentes Kostenmodell ist Voraussetzung für den Enterprise-Einsatz.

## 15.1 Token Budget Management

Preisstand 6. August 2026, API-Listenpreise von Anthropic [@anthropicmodels]
(je 1 Mio. Tokens; alle Modelle mit 1 Mio. Tokens Kontextfenster, Haiku 4.5
mit 200.000):

| Modell | Input (pro 1M Tokens) | Output (pro 1M Tokens) | Typischer Einsatz |
| --- | --- | --- | --- |
| Claude Fable 5 | $10.00 | $50.00 | schwierigste Langzeit-Agentenaufgaben |
| Claude Opus 5 | $5.00 | $25.00 | Architektur, Security Review, komplexe agentische Entwicklung |
| Claude Sonnet 5 | $3.00 (Einführungspreis $2.00 bis 31.08.2026) | $15.00 ($10.00) | Entwicklung, Testing, Planung |
| Claude Haiku 4.5 | $1.00 | $5.00 | Formatierung, einfache Tasks |

Bemerkenswert ist die Preisentwicklung seit v1.3 dieses Whitepapers
(März 2026): Das damalige Spitzenmodell der Opus-Klasse lag bei $15/$75 —
das heutige liegt bei $5/$25, bei gleichzeitig deutlich größerem
Kontextfenster. Preistabellen in Kostenmodellen für agentische Entwicklung
brauchen deshalb zwingend ein Stand-Datum, und Wirtschaftlichkeitsrechnungen
altern schnell in Richtung *zu konservativ*.

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

> **Hinweis:** Die folgende Gegenüberstellung ist eine Modellrechnung auf
> Basis der genannten Annahmen (Stundensätze, Aufwände, Token-Verbrauch) —
> keine gemessene Betriebsauswertung. Eine kontrollierte Messung liegt auch
> für das in Kapitel 19 beschriebene Realsystem nicht vor (siehe 19.9).

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

## 15.5 Abo- statt Token-Abrechnung *(neu in v2.0)*

Das bisherige Kapitel rechnet ausschließlich in Token-Preisen. Die Realität
agentischer Entwicklung hat sich seit v1.3 an einer entscheidenden Stelle
verschoben: Die großen Coding-CLIs lassen sich auf **zwei Wegen**
authentifizieren — per API-Key (Abrechnung je Token, wie oben modelliert)
oder per **Abo-Login** (Flatrate-Konto des Anbieters, etwa die
Claude-Abonnements für Claude Code oder das ChatGPT-Konto für die Codex-CLI;
Stand August 2026).

Für das Kostenmodell hat das grundlegende Konsequenzen:

1. **Die Grenzkosten je Lauf sind im Abo-Modus null.** Ein reines
   Token-ROI-Modell (wie in 15.4) bildet die Wirtschaftlichkeit dann nicht
   mehr ab; an die Stelle variabler API-Kosten tritt ein fixer
   Abo-Preis je Entwicklerplatz und Monat, gedeckelt durch die
   Nutzungslimits des jeweiligen Abos.
2. **Die Betriebsform wird zur Kostenentscheidung.** Einzelplatz mit Abo,
   Team-Pool mit API-Keys oder Mischformen unterscheiden sich in
   Planbarkeit (fix vs. variabel), Attribution (je Platz vs. je Verbrauch)
   und Skalierungsverhalten.
3. **Der Abrechnungsweg muss technisch kontrolliert werden.** Eine CLI, die
   sowohl einen Abo-Login als auch einen API-Key in der Umgebung vorfindet,
   wählt unter Umständen stillschweigend den kostenpflichtigen Pfad — ein
   Fehler, der erst auf der Monatsrechnung sichtbar wird. Wer beide Wege
   betreibt, braucht eine Stelle im System, die den jeweils nicht gewollten
   Weg aktiv unterbindet.

Diese Einordnung ist ein Erfahrungswert aus dem Betrieb der in Kapitel 19
beschriebenen Plattform; die dortige Umsetzung (Abo-Modus je Adapter mit
aktivem Entfernen des API-Keys aus der Prozessumgebung) steht in 19.4.

> **Praxis-Check SoftwareFabrik (erweitert):** Preistabelle je Modell mit
> Input-, Output- und Cached-Input-Preisen, Kostenaggregation nach Projekt,
> Run, Provider, Mandant und Seat, harte Budget-Caps je Mandant — und der
> Abo-Modus als eigener Authentifizierungsweg, der den API-Key aktiv aus der
> Subprozess-Umgebung entfernt (19.4, 19.6). Die ROI-Modellrechnung aus 15.4
> bleibt dagegen unbelegt: Für das Realsystem existiert keine kontrollierte
> Produktivitätsmessung (19.9).
