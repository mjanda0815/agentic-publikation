# 21 Die Vendor-Frage ist eine Konfigurationsfrage

> **Hinweis:** Dieses Kapitel ersetzt den Werkzeugvergleich der v1.3
> („Claude Code vs. andere KI-Entwicklungssysteme“). Die damalige
> Gegenüberstellung — Claude Code als orchestrierte Multi-Agent-Pipeline,
> Devin als autonomer Single-Agent, Cursor/Copilot als IDE-Assistenten — war
> zum Erscheinungszeitpunkt eine brauchbare Landkarte. Sie ist aus zwei
> Gründen nicht mehr die richtige Frage: Der Markt hat sich vervielfacht und
> angeglichen, und die relevanten Fähigkeiten sind zu Standards geworden.

## 21.1 Was sich seit v1.3 verändert hat

**Der Markt ist breit und konvergent geworden.** Stand August 2026 existiert
für jede Kategorie eine Mehrzahl leistungsfähiger Produkte: Terminal-Agenten
(u. a. Claude Code von Anthropic, die Codex-CLI von OpenAI, die Gemini CLI
von Google, dazu Open-Source-Agenten wie Aider oder OpenCode),
IDE-integrierte Assistenten mit Agentenmodus (u. a. Cursor, GitHub Copilot)
und autonome Cloud-Agenten (u. a. Devin, dazu die Cloud-Betriebsformen der
Terminal-Agenten selbst).^[Die Produktzuordnungen lassen sich sämtlich über
die Unterstützerliste des AGENTS.md-Standards nachvollziehen [@agentsmd],
die u. a. OpenAI (Codex), Google (Gemini CLI), Cursor, GitHub Copilot,
Cognition (Devin), Aider und OpenCode führt; Stand August 2026.] Die
Fähigkeitsmerkmale, an denen v1.3 die Systeme unterschied — Subagenten,
deklarative Repo-Konfiguration, Hooks, Werkzeuganbindung,
Hintergrund-Ausführung — finden sich inzwischen in mehreren Produkten. Nach
Beobachtung des Autors wechseln einzelne Spitzenplätze auf Benchmarks im
Monatsrhythmus; eine Vergleichstabelle wäre bei Drucklegung veraltet.

**Die Differenzierungsmerkmale von damals sind Standards geworden.** Die
deklarative Konfiguration im Repository hat mit `AGENTS.md` ein
werkzeugübergreifendes Format (Kapitel 4) [@agentsmd]; die Werkzeuganbindung
hat mit MCP einen herstellerneutralen Industriestandard unter der Linux
Foundation (Kapitel 18) [@mcp]. Wer seine Projektregeln, Skills und
Werkzeugintegrationen gegen diese Standards baut, kann den darunterliegenden
Agenten wechseln, ohne die Investition zu verlieren.

## 21.2 Die Konsequenz für die Architektur

Damit kehrt sich die Fragestellung um. Nicht mehr: *Welches Werkzeug ist das
beste?* Sondern: *Wie baue ich meinen Entwicklungsprozess so, dass die
Werkzeugwahl eine Konfigurationsentscheidung ist?* Drei Regeln folgen daraus:

1. **Kein Vendor im Fachkern.** Kein Bestandteil des eigenen Prozesses —
   Skripte, CI, Governance, Dokumentation — sollte einen konkreten Agenten
   hart voraussetzen. Die Anbindung gehört hinter eine Schnittstelle.
2. **Standards vor Produkt-Features.** Regeln in `AGENTS.md` statt in
   werkzeugspezifischen Dateien pflegen, Integrationen als MCP-Server statt
   als produktspezifische Plugins bauen. Produktspezifische Features (etwa
   Hooks) bewusst als Zusatz behandeln, nicht als Fundament.
3. **Mehrgleisigkeit einpreisen.** Nach Erfahrung des Autors arbeiten Teams bereits
   heute mit mehreren Agenten nebeneinander — je nach Aufgabe, Preismodell
   und Verfügbarkeit. Ein Prozess, der das zulässt, verhandelt bei jedem
   Modellsprung aus einer Position der Stärke.

Dass diese Umkehrung trägt, ist keine Theorie: Kapitel 19 beschreibt ein
System, in dem zehn Agenten-Anbindungen hinter einem einzigen Port stehen
und die Vendor-Neutralität als Build-Bedingung maschinell erzwungen wird.
Die Adapterwahl ist dort buchstäblich ein Konfigurationsfeld je Lauf.

> **Praxis-Check SoftwareFabrik (erweitert):** Der v1.3-Werkzeugvergleich
> ist durch die Implementierung hinfällig geworden — die Fabrik integriert
> zehn Execution-Adapter (ein deterministischer Mock, sechs CLI-Agenten,
> drei Cloud-Gateways) hinter einem Port;
> zwei ArchUnit-Regeln machen es technisch unmöglich, Anwendungs- oder
> Web-Schicht an einen konkreten Vendor zu koppeln (19.2, 19.4).

## 21.3 Was von der v1.3-Einordnung bleibt

Zwei Aussagen des alten Kapitels haben sich als richtig erwiesen und bleiben
gültig: Erstens, dass **Governance das entscheidende
Enterprise-Kriterium** ist — daran hat sich nichts geändert, nur dass
Governance heute weniger vom einzelnen Werkzeug zu erwarten ist als von der
Prozessschicht darüber (Kapitel 12, 14, 19.5–19.6). Zweitens, dass sich
**Autonomiegrade unterscheiden** müssen: gesteuerte Human-in-the-Loop-Arbeit,
beaufsichtigte Hintergrund-Läufe und autonome Agenten sind verschiedene
Betriebsarten mit verschiedenen Risikoprofilen — heute oft innerhalb
desselben Produkts wählbar, was die Betriebsart zur bewussten
Prozessentscheidung macht statt zur Werkzeugeigenschaft.
