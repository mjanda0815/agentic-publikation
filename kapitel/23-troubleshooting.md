# 23 Troubleshooting & Schnellreferenz

> **Versionshinweis (v2.0):** Die Schnellreferenz nennt v1.3-Werkzeugbegriffe.
> Heute gilt: `maxTurns` in der Subagenten-Definition statt `max_turns` im
> Aufruf, Fortsetzung über `SendMessage` statt `resume`, Agent-Tool statt
> Task-Tool (vgl. 3.5).

| Problem | Lösung |
| --- | --- |
| Unvollständige Ergebnisse | Prompts aufteilen. `maxTurns` in der Subagenten-Definition erhöhen. |
| Falsche Dateien geändert | Pfade explizit angeben. `isolation="worktree"`. |
| Kontextverlust | Nachricht per SendMessage an die Agent-ID senden. |
| Parallele Kollisionen | Worktree-Isolation für alle parallelen Agenten. |
| Halluzinierte APIs | Guardrail-Hooks aktivieren. Für kritische Tasks eine stärkere Modellklasse bzw. höhere Fähigkeitsstufe wählen (vgl. Kap. 5). |
| Domain-Verstöße | glossary.md aktualisieren. Domain-Hook implementieren. |
| Budget überschritten | Token Budget Tracker einsetzen. Modell-Eskalation prüfen. |
| MCP-Server Fehler | Umgebungsvariablen und Netzwerkzugriff prüfen. |

| Aufgabe | Agent |
| --- | --- |
| Codebasis analysieren | Explore / architecture-agent |
| Implementierungsplan erstellen | planning-agent |
| Anforderungen sammeln | requirements-agent |
| Features implementieren | Development Capability (Modellwahl über Capability-Routing) |
| Tests schreiben/ausführen | test-agent |
| Code-Qualität prüfen | Review Capability (Modellwahl über Capability-Routing) |
| Deployment | deploy-agent |
| CI/CD Quality Gate | qa-guard |

> **Praxis-Check SoftwareFabrik (erweitert):** Aus der Schnellreferenz
> wurden betriebliche Abläufe (Demo-Betrieb, Air-Gap-Auslieferung) und
> dokumentierte Praxis-Fallstricke — etwa der Architektur-Ratchet mit
> Zyklen-Kappungsgrenze oder CI-Jobs, die sich ohne Secret still
> überspringen und grün wirken (19.2, 19.5, 19.7).
