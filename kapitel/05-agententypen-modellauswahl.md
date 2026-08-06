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

Die Wahl des richtigen Modells hat erheblichen Einfluss auf Qualität, Geschwindigkeit und Kosten. Als Faustregel gilt: opus für Entscheidungen, bei denen Fehler teuer wären (Architektur, Security), sonnet als Arbeitspferd für den Großteil der Entwicklung, und haiku für schnelle, unkritische Aufgaben.
