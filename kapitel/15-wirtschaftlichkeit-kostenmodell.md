# 15 Wirtschaftlichkeitshypothese, Kostenmodell und Messplan

> **Hinweis:** Agentensysteme können erhebliche API-Kosten verursachen. Ohne aktives Kostenmanagement skalieren die Ausgaben unkontrolliert. Ein transparentes Kostenmodell ist Voraussetzung für den Enterprise-Einsatz.

## 15.1 Token Budget Management

Preisstand 6. August 2026, API-Listenpreise von Anthropic [@anthropicmodels;
@anthropicpricing] (je 1 Mio. Tokens; Kontextfenster 1 Mio. Tokens, Ausnahme
Haiku 4.5 mit 200.000):

| Modell | Input (pro 1M Tokens) | Output (pro 1M Tokens) | Typischer Einsatz |
| --- | --- | --- | --- |
| Claude Fable 5 | $10.00 | $50.00 | schwierigste Langzeit-Agentenaufgaben |
| Claude Opus 5 | $5.00 | $25.00 | Architektur, Security Review, komplexe agentische Entwicklung |
| Claude Sonnet 5 | $2.00 (Einführungspreis bis 31.08.2026; danach $3.00) | $10.00 (danach $15.00) | Entwicklung, Testing, Planung |
| Claude Haiku 4.5 | $1.00 | $5.00 | Formatierung, einfache Tasks |

Bemerkenswert ist der Vergleich mit der v1.3-Tabelle: Sie nannte für die
Opus-Klasse noch $15/$75 — die Preise der Opus-4/4.1-Generation. Schon
Opus 4.5 (November 2025, also vor Erscheinen der v1.3) lag bei $5/$25; die
Tabelle war bei Drucklegung bereits überholt. Die Bewegung ist dabei nicht
monoton nach unten: Die Haiku-Klasse wurde über zwei
Generationen hinweg viermal teurer je Token — von Haiku 3 ($0.25/$1.25)
über Haiku 3.5 ($0.80/$4) auf Haiku 4.5 ($1/$5) —, und seit der
Opus-4.7-Generation erzeugt ein neuer Tokenizer für denselben Text bis zu
rund 35 % mehr Tokens (inhaltsabhängig; Anthropics Migrationsleitfaden
nennt einen Faktor von 1,0x bis 1,35x, der Modellüberblick „rund 30 %“)
[@anthropicmigration; @anthropicmodels] — Token-Preise sind generationsübergreifend
also nur mit Vorbehalt vergleichbar. Die Lehre: Preistabellen in
Kostenmodellen für agentische Entwicklung brauchen zwingend ein Stand-Datum,
und Wirtschaftlichkeitsrechnungen sind in beide Richtungen schnell veraltet.

Als Modellannahme dieses Kapitels — Erfahrungswerte, nicht systematisch gemessen (vgl. den Messplan in 15.6): Ein typischer Entwicklungs-Agent verbraucht 10.000–100.000 Tokens pro Task. Ein End-to-End-Workflow mit 7 Agenten kann 500.000–2.000.000 Tokens verbrauchen.

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
| maxTurns (in der Subagenten-Definition; v1.3: max_turns als Aufrufparameter) | Maximale API-Roundtrips pro Agent | 10–25 für Entwicklung, 5–10 für Reviews |
| timeout | Maximale Laufzeit in Sekunden | 300s Standard, 600s für komplexe Tasks |
| max_cost_per_task | Kostenobergrenze pro Einzeltask | $2–5 für sonnet, $10–20 für opus |
| max_cost_per_workflow | Kostenobergrenze Gesamtworkflow | $20–50 pro Feature |
| stop_on_error | Abbruch bei Kompilier-/Testfehlern | true für Deployment, false für Entwicklung |

## 15.3 Parallelisierungskosten

*Die Dollarwerte dieser Tabelle sind eine Modellrechnung auf
v1.3-Preisstand (März 2026); vgl. die aktuelle Preistabelle in 15.1.*

| Szenario | Wanduhrzeit | Kosten |
| --- | --- | --- |
| Sequenziell: 7 Agenten | ~45 Minuten | $8–12 |
| Hybrid: 3 seq. + 4 parallel | ~25 Minuten | $8–12 (gleich) |
| Maximal parallel: 7 gleichzeitig | ~10 Minuten | $8–12 (gleich) |
| Parallel mit Retry-Schleifen | ~15 Minuten | $12–20 (höher!) |

In dieser vereinfachten Modellrechnung bleiben die reinen
Ausführungskosten unveränderter Einzeltasks unabhängig von ihrer zeitlichen
Anordnung gleich. **Nicht berücksichtigt sind** zusätzlicher Kontextaufbau
je paralleler Ausführung, Planungs-, Synthese- und Integrationsschritte,
Merge-Konflikte und Revalidierung — die Gesamtkosten eines parallelen
Workflows sind daher nicht notwendigerweise identisch, sondern in der Regel
höher. Besonders teuer wird es bei Merge-Konflikten und Retry-Schleifen. Deshalb ist Worktree-Isolation (AP-2) bei paralleler Ausführung Pflicht.

## 15.4 ROI-Berechnung

> **Hinweis:** Die folgende Gegenüberstellung ist eine Modellrechnung auf
> Basis der genannten Annahmen (Stundensätze, Aufwände, Token-Verbrauch) —
> keine gemessene Betriebsauswertung. Eine kontrollierte Messung liegt auch
> für das in Kapitel 19 beschriebene Realsystem nicht vor (siehe 19.9).

| Kostenfaktor | Manuell (Entwicklerteam) | KI-Agenten + Review |
| --- | --- | --- |
| Entwickleraufwand | 40h Senior Dev × €95/h = €3.800 | 8h Review + Steering = €760 |
| API-Kosten | – | ~2M Tokens ≈ €15–30 |
| Testabdeckung (angenommen) | Oft <60% unter Zeitdruck | >80% durch iteratives Testing |
| Time-to-Feature (angenommen) | 1–2 Wochen | 1–2 Tage |
| Gesamtkosten | €3.800+ | €775–€790 |

Der ROI hängt stark von der Aufgabenkomplexität ab: Bei Standard-CRUD-Features wird der Hebel am größten angenommen (modellhaft 5–10x; nicht gemessen). Bei komplexen Architekturentscheidungen sinkt der Automatisierungsgrad, aber der Analyse-Output (ADRs, Findings) kann die menschliche Entscheidungsfindung beschleunigen (Erfahrungswert, nicht gemessen; vgl. 15.6).

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
- opus NUR für: ADRs, Security Reviews, Claim Verification
- haiku für: Formatierung, Linting, Docs ohne Fachlogik
- sonnet für: alles andere (Default)
```

## 15.5 Abo- statt Token-Abrechnung *(neu in v2.0)*

Das bisherige Kapitel rechnet ausschließlich in Token-Preisen. Die Realität
agentischer Entwicklung hat sich seit v1.3 an einer entscheidenden Stelle
verschoben: Die großen Coding-CLIs lassen sich auf **zwei Wegen**
authentifizieren — per API-Key (Abrechnung je Token, wie oben modelliert)
oder per **Abo-Login** (Flatrate-Konto des Anbieters, etwa die
Claude-Abonnements für Claude Code [@claudecodeauth] oder das ChatGPT-Konto
für die Codex-CLI [@codexcli]; Stand August 2026).

Für das Kostenmodell hat das grundlegende Konsequenzen:

1. **Die Grenzkosten je Lauf sind im Abo-Modus bis zur Limitgrenze
   praktisch null.** Ein reines Token-ROI-Modell (wie in 15.4) bildet die
   Wirtschaftlichkeit dann nicht mehr ab; an die Stelle variabler API-Kosten
   tritt ein fixer Abo-Preis je Entwicklerplatz und Monat, gedeckelt durch
   die Nutzungslimits des jeweiligen Abos.
2. **Die Betriebsform wird zur Kostenentscheidung.** Einzelplatz mit Abo,
   Team-Pool mit API-Keys oder Mischformen unterscheiden sich in
   Planbarkeit (fix vs. variabel), Attribution (je Platz vs. je Verbrauch)
   und Skalierungsverhalten.
3. **Der Abrechnungsweg muss technisch kontrolliert werden.** Eine CLI, die
   sowohl einen Abo-Login als auch einen API-Key in der Umgebung vorfindet,
   wählt unter Umständen stillschweigend den kostenpflichtigen Pfad — bei
   Claude Code etwa hat ein gesetzter `ANTHROPIC_API_KEY` Vorrang vor dem
   Abo-Login [@claudecodeauth] —, ein Fehler, der erst auf der
   Monatsrechnung sichtbar wird. Wer beide Wege betreibt, braucht eine
   Stelle im System, die den jeweils nicht gewollten Weg aktiv unterbindet.

Diese Einordnung ist ein Erfahrungswert aus dem Betrieb der in Kapitel 19
beschriebenen Plattform; die dortige Umsetzung (Abo-Modus je Adapter mit
aktivem Entfernen des API-Keys aus der Prozessumgebung) steht in 19.4.

> **Praxis-Check SoftwareFabrik (erweitert):** Preistabelle je Modell mit
> Input-, Output- und Cached-Input-Preisen, Kostenaggregation nach Projekt,
> Run, Provider, Mandant und Seat, harte Budget-Caps je Mandant — und der
> Abo-Modus als eigener Authentifizierungsweg, der den API-Key aktiv aus der
> Subprozess-Umgebung entfernt (19.4). Die ROI-Modellrechnung aus 15.4
> bleibt dagegen unbelegt: Für das Realsystem existiert keine kontrollierte
> Produktivitätsmessung, und eine Budget-Obergrenze je Nutzer ist offen
> (19.9).

## 15.6 Messplan *(neu in v2.1)*

Die Modellrechnungen dieses Kapitels werden erst durch Messung zu
Ergebnissen. Für die in 19.10 beschriebene Weiterentwicklung ist deshalb
begleitend ein Messprogramm vorgesehen, das drei Vorgehensweisen
vergleicht — manuelle Umsetzung, Einzel-Run und paralleler Workflow — mit
folgenden Messgrößen:

- menschliche aktive Arbeitszeit je Vorhaben
- Time to Accepted Merge
- First-Pass-Gate-Rate (Anteil der Läufe ohne Korrekturschleife)
- Korrekturschleifen und Replans
- Kosten je Child Run, je Workflow und je akzeptierter Änderung
- Merge-Konfliktrate
- entkommene Defekte und Rollbacks
- Reviewzeit und Testabdeckungsänderung

> **Praxis-Check SoftwareFabrik (Stand 0.30.0):** Ein Teil dieses
> Messplans ist seit Release 0.27.0 implementiert (19.10, Stufe 6):
> Time to Accepted Merge, Erstdurchlauf-Quote, Korrekturschleifen,
> Planänderungen, Kosten je Workflow und Child Run, Merge-Konfliktquote
> und Freigabe-Wartezeit werden aus ohnehin entstehenden Daten abgeleitet;
> seit 0.28.0 kommt die Testabdeckungsänderung hinzu (in Prozentpunkten,
> erst ab der zweiten Messung), seit 0.29.0 die Rollback-Quote aus der
> Git-Historie (als Untergrenze ausgewiesen), seit 0.30.0 die Eingriffe
> und die Entscheiderzahl aus der Freigabeentscheidung — dazu ein
> erfragter, freiwilliger Aufwand, der nur zusammen mit seiner
> Abdeckungsquote ausgewiesen und nie mit Gemessenem verrechnet wird.
> Drei Messgrößen weist die
> Plattform bewusst als Lücke aus, statt sie zu
> schätzen: die menschliche aktive Arbeitszeit (Wartezeit ist
> nicht Arbeitszeit; seit 0.30.0 in messbare Eingriffe und erfragten
> Aufwand zerlegt — die Arbeitszeit selbst bleibt Lücke), entkommene
> Defekte (sauber messbar erst über eine
> Ticketsystem-Anbindung, die es nicht gibt; die Rollback-Hälfte dieser
> Lücke ist seit 0.29.0 geschlossen) und der
> Vergleich zur manuellen Umsetzung, dessen
> Referenzgruppe im System nicht existiert. Gemessen wird überwiegend auf
> der Workflow-Ebene, die weiterhin hinter dem standardmäßig deaktivierten
> Feature-Flag steht; allein der Einzel-Run-Teil der Rollback-Erkennung
> und das Aufwandsfeld an der Run-Freigabe wirken auch ohne Flag. Der
> dreiarmige Vergleich dieses Messplans steht damit weiter aus.

Bis diese Messungen vorliegen, sind alle Produktivitäts- und ROI-Aussagen
dieses Kapitels als Hypothesen bzw. Modellrechnungen zu lesen (vgl. 15.4,
19.9).
