# Management Summary

KI-gestützte Coding-Agenten können Anforderungen analysieren, Code verändern, Tests ausführen und Entwicklungsartefakte erzeugen. Ihr Einsatz in Enterprise- und regulierten Umgebungen erfordert jedoch mehr als ein leistungsfähiges Modell: Agentenarbeit muss spezifiziert, begrenzt, isoliert, geprüft, freigegeben und nachträglich rekonstruiert werden können.

Dieses Whitepaper beschreibt eine implementierte Control-Plane-Architektur für diesen Zweck. Die Referenzimplementierung SoftwareFabrik steuert zustandsbehaftete Agentenläufe, projiziert versionierte Regeln in den Workspace, begrenzt Modelle und Budgets, isoliert Ausführungen, bewertet Änderungen durch unabhängige Reviewer und führt relevante Entscheidungen in einem attestierten Audit- und Warum-Trace zusammen.

Der aktuelle Implementierungsstand verwendet genau einen schreibenden Agenten je Run. Mehrere read-only Reviewer prüfen den entstandenen Diff parallel. Diese Architektur vermeidet unkontrollierte Schreibkonkurrenz und bildet die Basis für den nächsten Entwicklungsschritt.

Die Weiterentwicklung ergänzt eine übergeordnete Workflow-Ebene. Ein Feature wird in einen Task Graph zerlegt; voneinander unabhängige Tasks können als isolierte Child Runs parallel ausgeführt werden. Jeder Child Run besitzt einen eigenen Branch oder Worktree und bleibt dem Single-Writer-Prinzip unterworfen. Ein Merge Coordinator und ein abschließendes Integration Gate führen die Ergebnisse kontrolliert zusammen.

Diese Ebene ist mit Release 0.30.0 vollständig umgesetzt — hinter einem standardmäßig deaktivierten Feature-Flag; nur der Einzel-Run-Teil der Rollback-Erkennung und das Aufwandsfeld an der Run-Freigabe wirken unabhängig davon. Der Weg dorthin führte bewusst über die risikoärmste Stufe: 0.21.0 ließ mehrere Agenten parallel analysieren, ohne dass einer schreiben durfte; 0.22.0 fügte die Schreibrechte hinzu, band sie aber an eine Besitzregel — wessen Schreibbereiche sich mit einem aktiven Task überschneiden, startet nicht; 0.23.0 gab den gemeinsamen Verträgen eine versionierte, gehashte Fassung, gegen die gearbeitet wird; 0.24.0 machte jede Planänderung begründungspflichtig und attestierbar; 0.25.0 verwandelte den Sammelbegriff Merge-Konflikt in eine Diagnose mit Handlungsempfehlung; 0.26.0 ergänzte eine Koordinationsschicht, in der ein Worker einen Task beansprucht, bevor Seitenwirkungen entstehen; 0.27.0 baute die Produktivitäts- und Qualitätsmessung ein — die ausweist, was sie nicht messen kann, statt es zu schätzen; 0.28.0 und 0.29.0 verengten diese Lücken, indem sie Testabdeckungsänderung und Rollbacks messbar machten — die Rollback-Quote ausdrücklich als Untergrenze; 0.30.0 zerlegte die Arbeitszeit-Lücke, statt sie zu schließen: Messbar ist seither, wie oft ein Mensch entscheiden musste; der Aufwand wird erfragt statt gemessen und nur mit ausgewiesener Abdeckung summiert. Der verteilte Betrieb über mehrere Hosts bleibt bewusst zurückgestellt, solange der Bedarf nicht gemessen ist.

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
