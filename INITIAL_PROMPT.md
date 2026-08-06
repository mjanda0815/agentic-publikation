# Initial-Prompt für die erste Arbeitssession

*(Diesen Text als ersten Prompt in der neuen Claude-Session in diesem
Verzeichnis verwenden — die CLAUDE.md greift dort automatisch.)*

---

Wir bauen aus meinem Whitepaper „Agentic Software Development — Enterprise
Architecture with AI Agents" (v1.3, März 2026) eine neue Version. Kern des
Vorhabens: Das Whitepaper war die konzeptionelle Basis meiner SoftwareFabrik —
die inzwischen real existiert. Beides soll jetzt **verheiratet** werden:
das bestehende Whitepaper, modernisiert, plus eine vollständige Beschreibung
der SoftwareFabrik als integraler Bestandteil der neuen Version.

**Quellenlage:**

- `quellen/Agentic_Software_Development_v13.pdf` — das Original (75 Seiten,
  deutsch, Word-Satz; falls ich eine .docx dazulege, ist die die bessere
  Extraktionsbasis).
- `quellen/softwarefabrik/` — von mir bereitgestellt: kompletter Satz an
  Architektur- und Systemdokumentation der SoftwareFabrik (00-INDEX,
  Systemüberblick, Architektur, Systemdiagramme, Domänenmodell). Das ist die
  inhaltliche Grundlage für den SoftwareFabrik-Teil.
- Ergänzend, nur zur Verifikation von Detailfragen: das Repo
  `/mnt/c/dev/SoftwareFabrik`. ACHTUNG Public-Ready-Regel (CLAUDE.md):
  keine Secrets, Tokens, internen Zugangsdaten oder Kundendetails in Text
  oder Repo übernehmen; im Zweifel fragen.

**Arbeitsauftrag — bitte in genau dieser Reihenfolge:**

1. **Sichtung (noch nichts umbauen):** Lies das v1.3-Whitepaper (Struktur,
   Kapitelinhalte, Kernaussagen) und die komplette Dokumentation unter
   `quellen/softwarefabrik/`. Verschaffe dir ein Bild: Was behauptet das
   Whitepaper konzeptionell, was hat die SoftwareFabrik davon realisiert,
   wo weicht die Realität ab, was ist seit März 2026 fachlich überholt
   (Modelle, Tools, Preise, Features)?
2. **Umbauplan zur Abnahme:** Entwirf auf dieser Basis einen konkreten Plan
   für die neue Version und lege ihn mir vor, BEVOR Text entsteht. Der Plan
   soll enthalten: (a) Ziel-Gliederung der neuen Version — welche
   v1.3-Kapitel bleiben/werden modernisiert/entfallen, wo und wie der
   SoftwareFabrik-Teil integriert wird (eigener Hauptteil vs. Verzahnung mit
   den Konzeptkapiteln — begründete Empfehlung); (b) Abgleich Konzept ↔
   Realisierung als roter Faden (das ist der publizistische Reiz: „so war es
   gedacht, so wurde es gebaut, das haben wir gelernt"); (c) Liste der
   Modernisierungspunkte mit Priorität; (d) welche Abbildungen neu als
   Skripte entstehen (aus den Systemdiagrammen); (e) Versionsnummer und
   Umfangsschätzung. Dazu die offenen Grundsatzentscheidungen aus CLAUDE.md
   (Lizenz, Titel/Untertitel der neuen Version) als Entscheidungsvorlage.
3. **Nach meiner Abnahme des Plans:** Extraktion v1.3 → `kapitel/*.md`
   (extraktor), `main.tex`/`Makefile` einrichten, Build zum Laufen bringen,
   CI-Push-Trigger aktivieren — dann kapitelweise Umbau gemäß Plan, mit
   zweitgutachter-Review nach jedem inhaltlichen Kapitel.

Arbeitsweise wie in CLAUDE.md: TODO.md als Single Source of Truth pflegen,
kapitelweise arbeiten, Repo durchgehend public-ready (auch Commit-Messages).
