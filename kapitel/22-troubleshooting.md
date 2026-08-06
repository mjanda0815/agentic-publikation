# 22 Troubleshooting & Schnellreferenz

| Problem | Lösung |
| --- | --- |
| Unvollständige Ergebnisse | Prompts aufteilen. max_turns erhöhen. |
| Falsche Dateien geändert | Pfade explizit angeben. isolation="worktree". |
| Kontextverlust | resume mit agent_id nutzen. |
| Parallele Kollisionen | Worktree-Isolation für alle parallelen Agenten. |
| Halluzinierte APIs | Guardrail-Hooks aktivieren. opus für kritische Tasks. |
| Domain-Verstöße | glossary.md aktualisieren. Domain-Hook implementieren. |
| Budget überschritten | Token Budget Tracker einsetzen. Modell-Eskalation prüfen. |
| MCP-Server Fehler | Umgebungsvariablen und Netzwerkzugriff prüfen. |

| Aufgabe | Agent |
| --- | --- |
| Codebasis analysieren | Explore / architecture-agent |
| Implementierungsplan erstellen | planning-agent |
| Anforderungen sammeln | requirements-agent |
| Features implementieren | dev-agent (sonnet) |
| Tests schreiben/ausführen | test-agent |
| Code-Qualität prüfen | review-agent (opus) |
| Deployment | deploy-agent |
| CI/CD Quality Gate | qa-guard |
