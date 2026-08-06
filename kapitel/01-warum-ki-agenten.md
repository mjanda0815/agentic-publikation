# 1 Warum Coding-Agenten eine Prozessschicht brauchen

Coding-Agenten können bestehende Repositories analysieren, Änderungen vornehmen, Build- und Testwerkzeuge aufrufen und Ergebnisse iterativ korrigieren. Ihre Fähigkeit zur selbstständigen Werkzeugnutzung unterscheidet sie von klassischen Codegeneratoren, macht ihre Ausführung aber zugleich nichtdeterministisch und sicherheitsrelevant. Für den Enterprise-Einsatz genügt daher nicht die Auswahl eines leistungsfähigen Modells. Erforderlich ist eine Prozess- und Governance-Schicht, die Agentenarbeit spezifiziert, begrenzt, isoliert, prüft und nachweisbar macht.

Diese Schicht ist der Gegenstand dieses Whitepapers. Es beschreibt eine Control-Plane-Architektur für agentische Softwareentwicklung — vendor-neutral: Der konkrete Coding-Agent (etwa Claude Code, die Codex-CLI oder die Gemini CLI; Stand August 2026, vgl. Kapitel 21) ist darin eine austauschbare Ausführungskomponente hinter einer Schnittstelle, nicht das Fundament der Architektur. Wo dieses Dokument Werkzeugdetails zeigt, dient Claude Code als durchgängiges Beispiel; die Prinzipien gelten werkzeugübergreifend.

Der Fokus liegt auf drei Kernaspekten: Erstens einem geteilten, versionierten Wissensstand, damit Erkenntnisse aus der Analyse nachvollziehbar in die Implementierung einfließen. Zweitens einer fachlichen Modellierung nach DDD-Prinzipien, die den erzeugten Code an fachliche Grenzen bindet. Drittens einer unabhängigen Prüfschicht mit Gates, die strukturierte Befunde liefert — einschließlich der Prüfung der Behauptungen eines Agenten über seine eigene Arbeit (Claim Verification) —, bevor Änderungen in die Codebasis gelangen.

## Das Orchestrator-Prinzip

Das Herzstück der Architektur ist das Orchestrator-Prinzip: Eine zentrale Steuerungsinstanz — vergleichbar mit einem Technical Lead — verteilt Aufgaben, überwacht Fortschritte, besitzt den Prozesszustand und führt Ergebnisse zusammen. In Claude Code übernimmt diese Rolle beispielsweise die Hauptsitzung, die spezialisierte Subagenten mit jeweils eigenem Kontextfenster startet; in der in Kapitel 19 beschriebenen Referenzimplementierung ist es ein Orchestrierungsdienst, der als einzige Stelle Statusübergänge ausführt — und damit zugleich die Stelle, an der Governance überhaupt ansetzen kann (19.3, 19.8).

Die Kontextisolation der Agenten ist dabei ein echter Vorteil — sie verhindert Interferenzen zwischen Aufgaben —, aber sie ist keine Workspace- oder Sicherheitsisolation: Wer schreiben darf, wo geschrieben wird und was als geprüft gilt, muss die Prozessschicht regeln (Kapitel 2, 12, 14). Agenten tauschen Informationen über einen geteilten, versionierten Wissensstand aus, ohne ihre Kontextisolation zu durchbrechen.

![Hub-and-Spoke-Multi-Agent-Architektur mit zentralem Orchestrator](abbildungen/out/abb01.pdf){width=100%}

### Kernprinzipien des Orchestrator-Modells

| Prinzip | Beschreibung |
| --- | --- |
| Separation of Concerns | Jeder Agent hat eine klar definierte Rolle und einen begrenzten Werkzeugzugriff. |
| Kontrollierte Parallelität | Unabhängige Aufgaben können gleichzeitig laufen — sofern Abhängigkeiten und Schreibbereiche es erlauben (Kapitel 2). |
| Autonome Operation | Agenten arbeiten eigenständig innerhalb ihres definierten Rahmens. |
| Ergebnis-Aggregation | Der Orchestrator sammelt und synthetisiert die Ergebnisse. |
| Konfigurierbarkeit | Regeln und Agentendefinitionen liegen deklarativ und versioniert im Repository (AGENTS.md/CLAUDE.md, Kapitel 4). |
| Wiederaufnahme | Läufe sind zustandsbehaftet und können fortgesetzt werden. |
| Shared State | Ein gemeinsamer, versionierter Wissensstand ermöglicht Zusammenarbeit. |
| Unabhängige Prüfung | Read-only-Reviewer und Gates liefern strukturierte Befunde — einschließlich Claim Verification — und geben Änderungen frei oder blockieren sie. |
