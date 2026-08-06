# 5 Eingebaute Agententypen und Modellauswahl

Claude Code bietet vorkonfigurierte Agententypen, die auf die häufigsten SDLC-Aufgaben zugeschnitten sind. Zusätzlich können über CLAUDE.md eigene Agententypen definiert werden.

## Agententypen und ihre SDLC-Phasen

| Agententyp | Zweck | SDLC-Phase |
| --- | --- | --- |
| Bash | Kommandoausführung, Git-Ops, Build-Automatisierung | Build / CI/CD |
| Explore | Codebase-Erkundung, Abhängigkeitsanalyse | Beliebig |
| Plan | Implementierungsstrategie mit Meilensteinen | Architektur |
| general-purpose | Mehrstufige Recherche und Analyse | Beliebig |
| implementation-planner | Erstellt Tracking-Dokumente und Aufgabenlisten | Planung |
| implementation-executor | Hohe Komplexität, mehrstufige Implementierung | Entwicklung |
| test-executor | Tests erstellen, ausführen und iterieren | Testing |
| qa-guard | Pre-Commit-Hooks, automatische Korrekturen | QA |
| doc-researcher | Dokumentation durchsuchen und analysieren | Requirements |
| doc-agent | Dokumentation erstellen und pflegen | Dokumentation |

## Modellauswahl-Strategie

Die Wahl des richtigen Modells hat erheblichen Einfluss auf Qualität,
Geschwindigkeit und Kosten. Die Faustregel aus v1.3 gilt unverändert — nur
die konkreten Modelle dahinter haben gewechselt: Die Klassenbezeichnungen
`opus`, `sonnet` und `haiku` bleiben in Claude Code stabil, während die
dahinterliegenden Modellversionen wechseln (Stand 6. August 2026: Claude
Opus 5, Claude Sonnet 5, Claude Haiku 4.5; darüber Claude Fable 5 als
höchste Leistungsklasse für die schwierigsten Langzeit-Agentenaufgaben)
[@anthropicmodels]. Also: die Opus-Klasse für Entscheidungen, bei denen
Fehler teuer wären (Architektur, Security), die Sonnet-Klasse als
Arbeitspferd für den Großteil der Entwicklung, und die Haiku-Klasse für
schnelle, unkritische Aufgaben.

Die eigentliche Lehre aus der kurzen Halbwertszeit von Modellnamen: Ein
System sollte **Fähigkeitsklassen** konfigurieren, nicht Modellnamen. Wo ein
konkreter Modellname in Konfiguration oder Code steht, ist er in Monaten
veraltet; eine Zuordnung „Rolle → Fähigkeitsstufe → aktuelles Modell" bleibt
stabil.

> **Praxis-Check SoftwareFabrik (erweitert):** Genau diese Abstraktion ist
> dort umgesetzt — Capability-Routing bildet Rollen (Planung vs. Umsetzung)
> auf Fähigkeitsprofile ab, die erst zur Laufzeit auf ein konkretes Modell
> aufgelöst werden; die Auflösung wird je Run attestiert (19.4).
