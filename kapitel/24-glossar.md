# 24 Glossar & Abkürzungsverzeichnis

| Abkürzung / Begriff | Erklärung |
| --- | --- |
| ADR | Architecture Decision Record – Dokumentierte Architekturentscheidung. |
| AOP | Aspect-Oriented Programming – Querschnittsbelange (Logging, Security). |
| AP-1 bis AP-6 | Die sechs architektonischen Prinzipien des Agentensystems (Kapitel 2). |
| Attestierung | Signierter, verketteter Nachweis einer Entscheidung im Agentensystem (Kap. 19). |
| Blatt-Slice | Modul, das nur konsumiert und von keinem anderen konsumiert wird — Entwurfsmuster zur Zyklenvermeidung (Kap. 19). |
| BPMN | Business Process Model and Notation – Geschäftsprozessmodellierung. |
| Build-Run | Lauf, der ein Backlog-Element umsetzt: Code auf isoliertem Branch, validiert, gemergt oder als Pull Request (Kap. 19). |
| CI/CD | Continuous Integration / Deployment – Automatisierte Pipeline. |
| Control Plane | Steuerschicht, die Agentenläufe orchestriert, begrenzt und protokolliert, ohne selbst Code zu schreiben (Kap. 19). |
| DAG | Directed Acyclic Graph – Gerichteter azyklischer Graph (Task Graph). |
| DDD | Domain-Driven Design – Fachliche Softwaremodellierung. |
| Debt-Ratchet | Eingefrorene, gezählte Architektur-Altschuld; neue Verstöße brechen den Build, behobene verschwinden aus der Baseline (Kap. 19). |
| DTO | Data Transfer Object – Datenobjekt ohne Geschäftslogik. |
| Guardrails-Projektion | Materialisierung der versionierten Verhaltensregeln als AGENTS.md/CLAUDE.md je Lauf in den Workspace (Kap. 19). |
| HPA | Horizontal Pod Autoscaler – Kubernetes-Skalierung. |
| IaC | Infrastructure as Code – Deklarative Infrastruktur. |
| JPA | Jakarta Persistence API – ORM-Standard für Java. |
| JWT | JSON Web Token – Authentifizierungstoken. |
| K8s | Kubernetes – Container-Orchestrierung. |
| LLM | Large Language Model – Großes Sprachmodell (z. B. Claude). |
| Mandant | Isolationseinheit für Projekte, Läufe, Budgets und Policies in einer mehrmandantenfähigen Plattform (Kap. 19). |
| MCP | Model Context Protocol – Anthropics Tool-Erweiterungsprotokoll. |
| OWASP | Open Web Application Security Project – Sicherheitsstandards. |
| Plan-Run | Lauf, der nur analysiert und Arbeitsschritte vorschlägt; darf keinen Code ändern (Kap. 19). |
| Policy-as-Code | Regeln als versioniertes, signiertes Dokument mit genau einer aktiven Version je Mandant (Kap. 19). |
| PSD2 | Payment Services Directive 2 – EU-Zahlungsdiensterichtlinie. |
| Quality Gate | Aggregation der Reviewer-Befunde zu einer Entscheidung (PASS/WARN/FAIL); Ausfall eines Prüfers ist nie ein stiller Pass (Kap. 12, 19). |
| RBAC | Role-Based Access Control – Rollenbasierte Zugriffskontrolle. |
| RFC 7807 | Problem Details for HTTP APIs – Strukturierte Fehlerantworten. |
| RTM | Requirements Traceability Matrix – Anforderungsverfolgung. |
| Run | Zustandsbehaftete Ausführungseinheit eines Agentenauftrags mit Phasen, Zuständen und Korrekturschleife (Kap. 19). |
| SBOM | Software Bill of Materials – Software-Komponentenliste. |
| SDLC | Software Development Lifecycle – Entwicklungslebenszyklus. |
| Sealed Interface | Java-Feature zur Einschränkung implementierender Klassen. |
| Slice | Fachlich geschnittenes Modul (Bounded Context) eines modularen Monolithen (Kap. 19). |
| Testcontainers | Docker-basierte Integrationstests für Java. |
| Warum-Trace | Rekonstruktion je Lauf, welche Policy, welches Modell und welche Freigaben gewirkt haben (Kap. 19). |
