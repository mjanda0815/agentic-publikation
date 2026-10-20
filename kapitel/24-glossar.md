# 24 Glossar & Abkürzungsverzeichnis

| Abkürzung / Begriff | Erklärung |
| --- | --- |
| ADR | Architecture Decision Record – Dokumentierte Architekturentscheidung. |
| Akzeptanzkriterium (AC-ID) | Prüfbare Anforderung einer Produkt-Spec mit stabiler ID nach dem Schema `AC-<nnn>-<nn>`; Grundlage von Traceability und Conformance-Prüfung (seit 0.35.0, opt-in; Kap. 19.11). |
| AOP | Aspect-Oriented Programming – Querschnittsbelange (Logging, Security). |
| AP-1 bis AP-8 | Die acht architektonischen Prinzipien der Control-Plane-Architektur (Kapitel 2). |
| Attestierung | Signierter, verketteter Nachweis einer Entscheidung im Agentensystem (Kap. 19). |
| Blatt-Slice | Modul, das nur konsumiert und von keinem anderen konsumiert wird — Entwurfsmuster zur Zyklenvermeidung (Kap. 19). |
| BPMN | Business Process Model and Notation – Geschäftsprozessmodellierung. |
| Build-Run | Lauf, der ein Backlog-Element umsetzt: Code auf isoliertem Branch, validiert, gemergt oder als Pull Request (Kap. 19). |
| Canary-Harness | Nachweisverfahren der SoftwareFabrik, das je Adapter und installierter CLI-Version prüft, dass der MCP-Nullzustand wirkt (seit 0.31.0; Kap. 19.4). |
| Child Run | Ein regulärer Run, der einem Workflow Task zugeordnet ist (seit 0.21.0 für nicht-schreibende, seit 0.22.0 auch für schreibende Tasks implementiert, Feature-Flag — Kap. 19.10). |
| CI/CD | Continuous Integration / Deployment – Automatisierte Pipeline. |
| Claim Verification | Prüfung der Aussagen eines Agenten über seine eigene Arbeit, etwa „alle Tests bestehen“ (in v1.3: Halluzinationserkennung; Kap. 12, 19.5). |
| Contract Version | Versionierter bzw. gehashter gemeinsamer Vertrag, gegen den mehrere Child Runs arbeiten (seit 0.23.0 implementiert, Feature-Flag; Kap. 19.10). |
| Control Plane | Steuerschicht, die Agentenläufe orchestriert, begrenzt und protokolliert, ohne selbst Code zu schreiben (Kap. 19). |
| DAG | Directed Acyclic Graph – Gerichteter azyklischer Graph (Task Graph). |
| DDD | Domain-Driven Design – Fachliche Softwaremodellierung. |
| Debt-Ratchet | Eingefrorene, gezählte Architektur-Altschuld; neue Verstöße brechen den Build, behobene verschwinden aus der Baseline (Kap. 19). |
| DTO | Data Transfer Object – Datenobjekt ohne Geschäftslogik. |
| EARS | Easy Approach to Requirements Syntax – fünf Satzschablonen für natürlichsprachliche Anforderungen (allgemein, ereignis-, zustandsgesteuert, unerwünschtes Verhalten, optionale Funktion) (Kap. 19.11). |
| Guardrails-Projektion | Materialisierung der versionierten Verhaltensregeln als AGENTS.md/CLAUDE.md je Lauf in den Workspace (Kap. 19). |
| HPA | Horizontal Pod Autoscaler – Kubernetes-Skalierung. |
| IaC | Infrastructure as Code – Deklarative Infrastruktur. |
| Integration Gate | Quality Gate auf dem zusammengeführten Workflow-Stand (seit 0.22.0 implementiert, Feature-Flag; Kap. 19.10). |
| JPA | Jakarta Persistence API – ORM-Standard für Java. |
| JWT | JSON Web Token – Authentifizierungstoken. |
| K8s | Kubernetes – Container-Orchestrierung. |
| LLM | Large Language Model – Großes Sprachmodell (z. B. Claude). |
| Mandant | Isolationseinheit für Projekte, Läufe, Budgets und Policies in einer mehrmandantenfähigen Plattform (Kap. 19). |
| MCP | Model Context Protocol – herstellerneutraler Industriestandard zur Werkzeuganbindung (ursprünglich Anthropic, seit 12/2025 Agentic AI Foundation / Linux Foundation; Kap. 18). |
| MCP-Nullzustand | Betriebszustand, in dem ein Agentenlauf keinen Werkzeugserver erreicht, den die Plattform nicht ausdrücklich bereitstellt (SoftwareFabrik seit 0.31.0; Kap. 19.4). |
| Merge Coordinator | Komponente zur kontrollierten Rebase-, Merge-, Konflikt- und Revalidierungssteuerung (seit 0.22.0 implementiert, Feature-Flag; Kap. 19.10). |
| Offline-Verifier | Eigenständiges Prüfprogramm, das einen Audit-Export ohne Zugriff auf die Plattform nachrechnet (SoftwareFabrik seit 0.32.0; Kap. 19.6). |
| OWASP | Open Worldwide Application Security Project (bis 2023: Open Web Application Security Project) – Sicherheitsstandards. |
| Owned Paths | Die Pfade, die ein Workflow Task exklusiv beschreiben darf — technische Grundlage des Single-Writer-Prinzips (Kap. 22.4, 19.10). |
| Plan-Run | Lauf, der nur analysiert und Arbeitsschritte vorschlägt; darf keinen Code ändern (Kap. 19). |
| Policy-as-Code | Regeln als versioniertes, signiertes Dokument mit genau einer aktiven Version je Mandant (Kap. 19). |
| Produkt-Spec | Versionierte, freigabepflichtige Anforderungsbeschreibung mit Ziel, Nicht-Zielen und Akzeptanzkriterien; einzige Quelle für Anforderungen beim Spec-Driven Development (seit 0.35.0, opt-in; Kap. 19.11). |
| PSD2 | Payment Services Directive 2 – EU-Zahlungsdiensterichtlinie. |
| Quality Gate | Aggregation der Reviewer-Befunde zu einer Entscheidung (PASS/WARN/FAIL, bei Prüferausfall ERROR — nie ein stiller Pass) (Kap. 12, 19). |
| RBAC | Role-Based Access Control – Rollenbasierte Zugriffskontrolle. |
| Replanner | Komponente, die den Task Graph auf Basis neuer Informationen versioniert anpasst (seit 0.24.0 implementiert, Feature-Flag; Kap. 19.10). |
| Reverse-Spec | Spec-Run, der für ein importiertes Repository einen Spec-Entwurf aus Code und Tests ableitet; nie automatisch freigegeben (seit 0.38.0; Kap. 19.11). |
| RFC 9457 (vormals RFC 7807) | Problem Details for HTTP APIs – Strukturierte Fehlerantworten. |
| RTM | Requirements Traceability Matrix – Anforderungsverfolgung. |
| Run | Zustandsbehaftete Ausführungseinheit eines Agentenauftrags mit Phasen, Zuständen und Korrekturschleife (Kap. 19). |
| SBOM | Software Bill of Materials – Software-Komponentenliste. |
| SDLC | Software Development Lifecycle – Entwicklungslebenszyklus. |
| Sealed Interface | Java-Feature zur Einschränkung implementierender Klassen. |
| Single Writer | Prinzip: Innerhalb eines Branch, Worktree oder Workspace arbeitet genau ein Agent schreibend (Kap. 19). |
| Slice | Fachlich geschnittenes Modul (Bounded Context) eines modularen Monolithen (Kap. 19). |
| Spec-Drift | Abweichung zwischen einer neu freigegebenen Spec-Fassung und der darauf gebundenen Planung; markiert betroffene Arbeit als veraltet (seit 0.38.0; Kap. 19.11). |
| Spec-Driven Development (SDD) | Vorgehen, bei dem versionierte, freigegebene Produkt-Specs die Anforderungen tragen, gegen die Läufe gebunden und geprüft werden (SoftwareFabrik seit 0.35.0, opt-in; Kap. 19.11). |
| Spec-Modus | Projekteinstellung AUS/LEICHT/STRENG, die festlegt, wie verbindlich Specs für Backlog, Planfreigabe und Quality Gate sind (Kap. 19.11). |
| Spec-Run | Lauf, der ausschließlich Specs unter `specs/` erarbeitet oder schärft und offene Fragen als Wartezustand ausweist (seit 0.38.0; Kap. 19.11). |
| Testcontainers | Docker-basierte Integrationstests für Java. |
| Warum-Trace | Rekonstruktion je Lauf, welche Policy, welches Modell und welche Freigaben gewirkt haben (Kap. 19). |
| Workflow | Übergeordnete, zustandsbehaftete Ausführungseinheit für ein Feature oder Vorhaben (seit 0.21.0 implementiert, Feature-Flag; Kap. 19.10). |
| Workflow Task | Abgegrenzte Arbeitseinheit mit Abhängigkeiten, Capability, Schreibbereichen und optionalem Child Run (seit 0.21.0 implementiert, die Schreibbereiche seit 0.22.0; Feature-Flag — Kap. 19.10). |
| Workspace Lease | Zeitlich begrenzte Reservierung von Pfaden, Modulen oder exklusiven Ressourcen (seit 0.22.0 implementiert, Feature-Flag; Kap. 19.10). |
