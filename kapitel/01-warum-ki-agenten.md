# 1 Warum KI-Agenten in der Softwareentwicklung?

Die Softwareentwicklung steht vor einem fundamentalen Paradigmenwechsel. Während bisherige Automatisierungsansätze – von CI/CD-Pipelines über Code-Generatoren bis hin zu IDE-Plugins – stets auf klar definierte, deterministisch ablaufende Aufgaben beschränkt waren, eröffnen KI-gestützte Agenten eine völlig neue Dimension: sie können kontextabhängig entscheiden, iterativ arbeiten und komplexe Aufgabenketten selbstständig orchestrieren.

Claude Code, Anthropics agentisches CLI-Tool, geht über die reine Code-Generierung weit hinaus. Es ermöglicht ein vollständiges Multi-Agent-System, bei dem spezialisierte Subagenten autonom und koordiniert arbeiten – vergleichbar mit einem erfahrenen Entwicklungsteam, bei dem jedes Mitglied seine Expertise einbringt. Die Agenten lesen bestehenden Code, analysieren Architekturen, schreiben Tests, führen Sicherheitsreviews durch und deployen Anwendungen – alles innerhalb eines kohärenten Workflows.

Dieses Dokument beschreibt im Detail, wie Enterprise-Teams Claude Code Agenten in ihren Software Development Lifecycle (SDLC) integrieren können. Der besondere Fokus liegt auf drei Kernaspekten: Erstens einem geteilten Wissensstand zwischen Agenten, damit Erkenntnisse aus der Architekturanalyse nahtlos in die Implementierung einfließen. Zweitens einer fachlichen Modellierung nach DDD-Prinzipien, die sicherstellt, dass der generierte Code nicht nur technisch korrekt, sondern auch fachlich präzise ist. Drittens einem robusten AI Risk Framework mit Guardrails, das Halluzinationen erkennt und verhindert, bevor fehlerhafter Code in die Codebasis gelangt.

## Das Orchestrator-Prinzip

Das Herzstück der Claude-Code-Agentenarchitektur ist das Orchestrator-Prinzip. Die Claude-Code-Hauptsitzung fungiert als zentrale Steuerungsinstanz – vergleichbar mit einem Technical Lead, der Aufgaben verteilt, Fortschritte überwacht und Ergebnisse zusammenführt.

Über das Task-Tool werden spezialisierte Subagenten gestartet, wobei jeder Agent sein eigenes Kontextfenster besitzt. Dies ist ein entscheidender architektureller Vorteil: Jeder Subagent arbeitet in einem isolierten Kontext, was Interferenzen zwischen parallelen Aufgaben verhindert. Gleichzeitig können Agenten über den Shared Knowledge Store Informationen austauschen, ohne ihre Isolation zu durchbrechen.

<!-- TODO(abbildung): Abbildung 1: Hub-and-Spoke Multi-Agent-Architektur mit zentralem Orchestrator -->

### Kernprinzipien des Orchestrator-Modells

| Prinzip | Beschreibung |
| --- | --- |
| Separation of Concerns | Jeder Agent hat eine klar definierte Rolle und einen begrenzten Werkzeugzugriff. |
| Parallele Ausführung | Unabhängige Agenten laufen gleichzeitig. Testing, Dokumentation und Review können parallel stattfinden. |
| Autonome Operation | Subagenten arbeiten eigenständig innerhalb ihres definierten Rahmens. |
| Ergebnis-Aggregation | Der Orchestrator sammelt und synthetisiert die Outputs aller Subagenten. |
| Konfigurierbarkeit | Benutzerdefinierte Agenten und Regeln werden über CLAUDE.md deklarativ konfiguriert. |
| Wiederaufnahme | Agenten können über ihre Agent-ID fortgesetzt werden. |
| Shared State | Ein gemeinsamer Wissensstand über den Shared Knowledge Store ermöglicht Zusammenarbeit. |
| Guardrails | Ein AI Risk Framework mit Halluzinationserkennung sichert die Codequalität. |

> **Praxis-Check SoftwareFabrik (bestätigt):** Das Orchestrator-Prinzip
> trägt: In der Implementierung ist ein einziger Dienst die einzige Stelle,
> an der Run-Statuswechsel stattfinden — und damit zugleich die Stelle, an
> der Governance überhaupt ansetzen kann (19.3).
