# 24 Glossar & Abkürzungsverzeichnis

| Abkürzung / Begriff | Erklärung |
| --- | --- |
| ADR | Architecture Decision Record – Dokumentierte Architekturentscheidung. |
| AOP | Aspect-Oriented Programming – Querschnittsbelange (Logging, Security). |
| AP-1 bis AP-8 | Die acht architektonischen Prinzipien der Control-Plane-Architektur (Kapitel 2). |
| Attestierung | Signierter, verketteter Nachweis einer Entscheidung im Agentensystem (Kap. 19). |
| Blatt-Slice | Modul, das nur konsumiert und von keinem anderen konsumiert wird — Entwurfsmuster zur Zyklenvermeidung (Kap. 19). |
| BPMN | Business Process Model and Notation – Geschäftsprozessmodellierung. |
| Build-Run | Lauf, der ein Backlog-Element umsetzt: Code auf isoliertem Branch, validiert, gemergt oder als Pull Request (Kap. 19). |
| Child Run | Ein regulärer Run, der einem Workflow Task zugeordnet ist (Zielarchitektur, Kap. 19.10). |
| CI/CD | Continuous Integration / Deployment – Automatisierte Pipeline. |
| Claim Verification | Prüfung der Aussagen eines Agenten über seine eigene Arbeit, etwa „alle Tests bestehen“ (in v1.3: Halluzinationserkennung; Kap. 12, 19.5). |
| Contract Version | Versionierter bzw. gehashter gemeinsamer Vertrag, gegen den mehrere Child Runs arbeiten (Zielarchitektur, Kap. 19.10). |
| Control Plane | Steuerschicht, die Agentenläufe orchestriert, begrenzt und protokolliert, ohne selbst Code zu schreiben (Kap. 19). |
| DAG | Directed Acyclic Graph – Gerichteter azyklischer Graph (Task Graph). |
| DDD | Domain-Driven Design – Fachliche Softwaremodellierung. |
| Debt-Ratchet | Eingefrorene, gezählte Architektur-Altschuld; neue Verstöße brechen den Build, behobene verschwinden aus der Baseline (Kap. 19). |
| DTO | Data Transfer Object – Datenobjekt ohne Geschäftslogik. |
| Guardrails-Projektion | Materialisierung der versionierten Verhaltensregeln als AGENTS.md/CLAUDE.md je Lauf in den Workspace (Kap. 19). |
| HPA | Horizontal Pod Autoscaler – Kubernetes-Skalierung. |
| IaC | Infrastructure as Code – Deklarative Infrastruktur. |
| Integration Gate | Quality Gate auf dem zusammengeführten Workflow-Stand (Zielarchitektur, Kap. 19.10). |
| JPA | Jakarta Persistence API – ORM-Standard für Java. |
| JWT | JSON Web Token – Authentifizierungstoken. |
| K8s | Kubernetes – Container-Orchestrierung. |
| LLM | Large Language Model – Großes Sprachmodell (z. B. Claude). |
| Mandant | Isolationseinheit für Projekte, Läufe, Budgets und Policies in einer mehrmandantenfähigen Plattform (Kap. 19). |
| MCP | Model Context Protocol – herstellerneutraler Industriestandard zur Werkzeuganbindung (ursprünglich Anthropic, seit 12/2025 Agentic AI Foundation / Linux Foundation; Kap. 18). |
| Merge Coordinator | Komponente zur kontrollierten Rebase-, Merge-, Konflikt- und Revalidierungssteuerung (Zielarchitektur, Kap. 19.10). |
| OWASP | Open Web Application Security Project – Sicherheitsstandards. |
| Plan-Run | Lauf, der nur analysiert und Arbeitsschritte vorschlägt; darf keinen Code ändern (Kap. 19). |
| Policy-as-Code | Regeln als versioniertes, signiertes Dokument mit genau einer aktiven Version je Mandant (Kap. 19). |
| PSD2 | Payment Services Directive 2 – EU-Zahlungsdiensterichtlinie. |
| Quality Gate | Aggregation der Reviewer-Befunde zu einer Entscheidung (PASS/WARN/FAIL, bei Prüferausfall ERROR — nie ein stiller Pass) (Kap. 12, 19). |
| RBAC | Role-Based Access Control – Rollenbasierte Zugriffskontrolle. |
| Replanner | Komponente, die den Task Graph auf Basis neuer Informationen versioniert anpasst (Zielarchitektur, Kap. 19.10). |
| RFC 9457 (vormals RFC 7807) | Problem Details for HTTP APIs – Strukturierte Fehlerantworten. |
| RTM | Requirements Traceability Matrix – Anforderungsverfolgung. |
| Run | Zustandsbehaftete Ausführungseinheit eines Agentenauftrags mit Phasen, Zuständen und Korrekturschleife (Kap. 19). |
| SBOM | Software Bill of Materials – Software-Komponentenliste. |
| SDLC | Software Development Lifecycle – Entwicklungslebenszyklus. |
| Sealed Interface | Java-Feature zur Einschränkung implementierender Klassen. |
| Single Writer | Prinzip: Innerhalb eines Branch, Worktree oder Workspace arbeitet genau ein Agent schreibend (Kap. 19). |
| Slice | Fachlich geschnittenes Modul (Bounded Context) eines modularen Monolithen (Kap. 19). |
| Testcontainers | Docker-basierte Integrationstests für Java. |
| Warum-Trace | Rekonstruktion je Lauf, welche Policy, welches Modell und welche Freigaben gewirkt haben (Kap. 19). |
| Workflow | Übergeordnete, zustandsbehaftete Ausführungseinheit für ein Feature oder Vorhaben (Zielarchitektur, Kap. 19.10). |
| Workflow Task | Abgegrenzte Arbeitseinheit mit Abhängigkeiten, Capability, Schreibbereichen und optionalem Child Run (Zielarchitektur, Kap. 19.10). |
| Workspace Lease | Zeitlich begrenzte Reservierung von Pfaden, Modulen oder exklusiven Ressourcen (Zielarchitektur, Kap. 19.10). |
