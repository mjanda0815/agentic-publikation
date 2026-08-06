# 13 Deployment Architektur

Während die vorherigen Kapitel die logische Architektur und das Ausführungsmodell des agentischen Entwicklungssystems beschreiben, stellt sich in der Praxis die Frage, wie ein solches System in einer Enterprise-Umgebung betrieben werden kann.

Agentische Entwicklungssysteme bestehen typischerweise aus einer zentralen Orchestrierungskomponente sowie einem Pool spezialisierter Agenten, die containerisiert betrieben und dynamisch skaliert werden können.

<!-- TODO(abbildung): Abbildung 14: Deployment-Architektur eines agentischen Entwicklungssystems -->

Die Abbildung zeigt eine mögliche Infrastruktur für den Betrieb eines agentischen Entwicklungssystems in einer Enterprise-Umgebung.

Im Zentrum steht der Agent-Orchestrator, der Entwicklungsaufträge entgegennimmt und an einen Pool spezialisierter Agenten delegiert. Diese Agenten werden typischerweise containerisiert betrieben und können innerhalb einer Kubernetes-Umgebung dynamisch skaliert werden.

Die Agenten interagieren mit einem Git-Repository, um bestehende Codebasen zu analysieren und Änderungen vorzunehmen. Generierte Artefakte werden anschließend über eine CI/CD-Pipeline gebaut, getestet und validiert. Parallel greifen die Agenten auf einen Shared Knowledge Store zu, der Architekturentscheidungen, Anforderungen und weitere Kontextinformationen enthält.

Diese Infrastruktur ermöglicht eine reproduzierbare, skalierbare und kontrollierte Ausführung agentischer Entwicklungsprozesse, während bestehende Entwicklungswerkzeuge und Governance-Mechanismen weiterhin genutzt werden können.

In größeren Organisationen wird der Agent-Worker-Pool häufig über Queue- oder Workflow-Systeme gesteuert, um Priorisierung, Parallelisierung und Ressourcenmanagement zu ermöglichen.

## Einordnung *(neu in v2.0)*

Die hier gezeichnete Kubernetes-Architektur ist als **Option** zu lesen,
nicht als Voraussetzung. Die Praxis hat gezeigt: Reale Zielgruppen im
regulierten Umfeld — Behörden, Finanzdienstleister, Mittelstand — stellen
vor der Skalierungsfrage eine andere: *Läuft es bei uns, on-premises, ohne
Cloud-Abhängigkeit, notfalls ohne Rückkanal?* Ein agentisches
Entwicklungssystem kann als einzelner Prozess mit einer Datenbank betrieben
werden; die eigentliche Komplexität liegt in der Steuerung des
Nichtdeterminismus, nicht in der Betriebsinfrastruktur. Kubernetes bleibt
der richtige Weg, wo elastische Skalierung vieler paralleler Agenten
gebraucht wird — es ist aber nicht die Eintrittskarte.

> **Praxis-Check SoftwareFabrik (abweichend):** Ein Anwendungscontainer,
> eine Datenbank, Docker Compose; ephemere Agent-Container optional.
> Air-Gap-fähig bis hin zur Lizenz ohne Online-Aktivierung — Souveränität
> war das Entscheidungskriterium, nicht Skalierung (19.7).
