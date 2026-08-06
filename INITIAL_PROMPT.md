# Initial-Prompt für die erste Arbeitssession

*(Diesen Text als ersten Prompt in der neuen Claude-Session in diesem
Verzeichnis verwenden — die CLAUDE.md greift dort automatisch.)*

---

Wir modernisieren mein Whitepaper „Agentic Software Development — Enterprise
Architecture with AI Agents" (v1.3, März 2026; liegt als PDF unter
`quellen/`). Das Projekt hat zwei Ziele:

1. **Modernisierung:** Alle schnelllebigen Angaben (Modelle, Tools, Features,
   Preise) auf den aktuellen Stand bringen, mit Stand-Datum und Primärquellen
   gemäß CLAUDE.md; überholte Abschnitte überarbeiten.
2. **Neuer Hauptabschnitt „SoftwareFabrik":** Das Whitepaper war die
   konzeptionelle Basis meiner SoftwareFabrik — die inzwischen real existiert.
   Ein neuer, klar gekennzeichneter Abschnitt soll sie vollständig beschreiben:
   Architektur, Agenten-Orchestrierung, Workflows, Qualitätssicherung,
   Lessons Learned. Quelle der Wahrheit ist das Repo unter
   `/mnt/c/dev/SoftwareFabrik` (lesen und daraus ableiten — nichts erfinden).
   ACHTUNG Public-Ready-Regel: keine Secrets, Tokens, internen Zugangsdaten
   oder Kundendetails in Text oder Repo übernehmen; bei Unsicherheit fragen.

Arbeitsplan für diese Session, in dieser Reihenfolge:

1. **CLAUDE.md-Entwurf mit mir abnehmen** — insbesondere die offenen
   Grundsatzentscheidungen (Lizenz der Neuauflage, Zielumfang, Namen).
2. **Extraktion:** v1.3 nach `kapitel/*.md` (extraktor; falls ich eine .docx
   in `quellen/` gelegt habe, diese statt des PDFs verwenden). `main.tex`
   nach Vorbild des DeFi-Projekts anlegen, `Makefile` auf die neue
   Kapitelstruktur anpassen, Build zum Laufen bringen, danach den
   Push-Trigger im CI-Workflow aktivieren.
3. **Bestandsaufnahme** (zweitgutachter): Was ist seit März 2026 überholt,
   was fehlt? Ergebnis als priorisierte Arbeitsliste in TODO.md.
4. **Gliederungsvorschlag für den SoftwareFabrik-Abschnitt** aus dem Repo
   ableiten und mir zur Abnahme vorlegen — erst nach Abnahme Rohtext.

Arbeitsweise wie in CLAUDE.md: TODO.md als Single Source of Truth pflegen,
kapitelweise arbeiten, Reviews nach jedem inhaltlichen Kapitel, Repo bleibt
durchgehend public-ready (auch die Commit-Messages).
