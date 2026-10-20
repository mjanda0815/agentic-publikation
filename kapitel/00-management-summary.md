# Management Summary

KI-gestützte Coding-Agenten können Anforderungen analysieren, Code verändern, Tests ausführen und Entwicklungsartefakte erzeugen. Ihr Einsatz in Enterprise- und regulierten Umgebungen erfordert jedoch mehr als ein leistungsfähiges Modell: Agentenarbeit muss spezifiziert, begrenzt, isoliert, geprüft, freigegeben und nachträglich rekonstruiert werden können.

Dieses Whitepaper beschreibt eine implementierte Control-Plane-Architektur für diesen Zweck. Die Referenzimplementierung SoftwareFabrik steuert zustandsbehaftete Agentenläufe, projiziert versionierte Regeln in den Workspace, begrenzt Modelle und Budgets, isoliert Ausführungen, bewertet Änderungen durch unabhängige Reviewer und führt relevante Entscheidungen in einem attestierten Audit- und Warum-Trace zusammen.

Der aktuelle Implementierungsstand verwendet genau einen schreibenden Agenten je Run. Mehrere read-only Reviewer prüfen den entstandenen Diff unabhängig voneinander. Diese Architektur vermeidet unkontrollierte Schreibkonkurrenz und bildet die Basis für den nächsten Entwicklungsschritt.

Die Weiterentwicklung ergänzt eine übergeordnete Workflow-Ebene. Ein Feature wird in einen Task Graph zerlegt; voneinander unabhängige Tasks können als isolierte Child Runs parallel ausgeführt werden. Jeder Child Run besitzt einen eigenen Branch oder Worktree und bleibt dem Single-Writer-Prinzip unterworfen. Ein Merge Coordinator und ein abschließendes Integration Gate führen die Ergebnisse kontrolliert zusammen.

Diese Ebene ist vollständig umgesetzt (seit SoftwareFabrik-Release 0.30.0, August 2026) — hinter einem standardmäßig deaktivierten Feature-Flag (zwei Detailmessungen wirken auch ohne — 19.10). Der Weg dorthin folgte bewusst der Risikoreihenfolge: erst parallele Analyse ohne Schreibrechte, dann Schreibrechte unter einer Besitzregel, dann versionierte Verträge, begründungspflichtiges Umplanen, eine Merge-Diagnose, eine Koordinationsschicht — begleitet von einer Messung, die ausweist, was sie nicht messen kann, statt es zu schätzen. Welches Release welchen Schritt brachte, dokumentiert die Release-Verlaufstabelle in Kapitel 19.10. Der verteilte Betrieb über mehrere Hosts bleibt bewusst zurückgestellt, solange der Bedarf nicht gemessen ist.

Seither (Stand: Release 0.39.0, Oktober 2026) kamen zwei Linien hinzu. Die erste sichert die Agentenläufe gegen nicht freigegebene Werkzeugkonfiguration ab, weist diese Isolation je Werkzeugversion nach und macht den Audit-Export mit einem eigenständigen Prüfwerkzeug ohne Zugriff auf die Plattform verifizierbar. Die zweite ergänzt eine Anforderungsebene (Spec-Driven Development): versionierte, freigegebene Produkt-Specs mit nummerierten Akzeptanzkriterien, gegen die Läufe gebunden, nachverfolgt und im Quality Gate geprüft werden; in regulierten Umgebungen kann eine Policy die Spec-Freigabe zur Startbedingung machen — ebenfalls opt-in hinter einem eigenen Feature-Flag (19.11).

Das Whitepaper unterscheidet konsequent zwischen implementiertem Stand, Zielarchitektur und Roadmap. Quantifizierte Produktivitäts- und ROI-Werte werden als Hypothesen beziehungsweise Modellrechnungen behandelt, solange keine kontrollierte Vergleichsmessung vorliegt.

## Kernaussagen

- **Control Plane statt unkontrollierter Autonomie:** Der entscheidende Schritt ist nicht die maximale Zahl gleichzeitig arbeitender Agenten, sondern eine Steuerschicht, die nichtdeterministische Agentenarbeit begrenzt, isoliert, koordiniert, prüft und nachweisbar macht.
- **Single Writer, Multiple Reviewers:** Innerhalb eines Workspace schreibt genau ein Agent; mehrere unabhängige Reviewer prüfen read-only.
- **Parallelität nach Abhängigkeiten:** Parallelität entsteht zwischen isolierten Tasks und Child Runs — abgeleitet aus Abhängigkeiten, Verträgen und Schreibbereichen, nicht aus festen Agentenrollen.
- **Governance by Design:** Governance ist keine Ergänzung der Agentenarchitektur, sondern ein Teil ihrer Struktur — von der Policy-Prüfung bis zur signierten Audit-Hashkette.
- **Git plus autoritativer Prozesszustand:** Git trägt Artefakte, Branches und Checkpoints; Workflow-, Policy-, Freigabe- und Audit-Zustand liegen autoritativ in der Datenbank.
- **Regelkreis statt blindem Retry:** Wiederholungen sind nur zulässig, wenn neue Informationen eingehen — Build-Ausgaben, Reviewer-Findings, Merge-Konflikte, CI-Ergebnisse.
- **Souveränität vor Infrastrukturkomplexität:** Die Architektur bleibt lokal, on-premises und ohne Cloud-Abhängigkeit betreibbar — bis hin zum Air-Gap-Betrieb.

## Zielgruppe

Dieses Dokument richtet sich an IT-Architekten, technische Projektleiter und Entwicklungsteams, die KI-Agenten systematisch in ihren Software Development Lifecycle integrieren möchten. Alle Beispiele verwenden Java, Spring Boot und bewährte Enterprise-Patterns – die Prinzipien sind jedoch technologieunabhängig übertragbar.
