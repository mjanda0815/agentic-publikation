# TODO — Modernisierung „Agentic Software Development"

Single Source of Truth für offene Aufgaben. Public-ready geführt (siehe
CLAUDE.md, Public-Ready-Regel): keine sensiblen Details in diese Datei.

## A. Projekt-Setup (06.08.2026)

- [x] Projektverzeichnis parallel zu DEFI_Publikation angelegt; Baukasten
      übernommen: `praeambel.tex`, `Makefile` (noch DeFi-Kapitelnummern —
      bei Extraktion anpassen), `abbildungen/stil.py`, `carousel/karussell.sty`,
      Subagents `extraktor`/`zweitgutachter`, Skills `faktencheck`/
      `kapitel-review`, `.claude/settings.json`.
- [x] Original-Whitepaper v1.3 (März 2026, 75 S.) heruntergeladen:
      `quellen/Agentic_Software_Development_v13.pdf`.
- [x] CI-Workflow als Gerüst hinterlegt (nur `workflow_dispatch`, kein
      Push-Trigger — aktivieren, sobald der Build steht).
- [x] Privates GitHub-Repo angelegt und Erst-Commit gepusht.
- [ ] (Martin) CLAUDE.md-Entwurf abnehmen — insb. Quellenregeln, Lizenzfrage,
      Zielumfang, Projektname (siehe CLAUDE.md, „Offene Grundsatzentscheidungen").
- [ ] (Martin) Falls vorhanden: Word-Quelldatei (.docx) der v1.3 nach
      `quellen/` legen — bessere Extraktionsbasis als das PDF.

## B. Sichtung und Umbauplan (06.08.2026)

- [x] Vollständige Sichtung: v1.3-Whitepaper (75 S., 23 Kapitel, 20 Abb.,
      4 ADRs) und SoftwareFabrik-Quellen-Set (13 Dokumente, Stand 0.19.0).
- [x] Umbauplan v1.3 → v2.0 erstellt: `UMBAUPLAN.md` (Ziel-Gliederung mit
      neuem Teil VI „SoftwareFabrik", Praxis-Check-Kästen als roter Faden,
      Modernisierungsliste P1–P3, Abbildungsplan, Version 2.0,
      Entscheidungsvorlage E1–E6).
- [x] **(Martin) UMBAUPLAN.md abgenommen** (06.08.2026): Gliederung wie
      vorgeschlagen (Teil VI + Praxis-Checks), Lizenz CC BY 4.0, Untertitel
      = Plan-Vorschlag, Version 2.0. E5 (Produktnennungs-Grenzen) und E6
      (Repo-Name) mit Plan-Empfehlung übernommen.

## C. Umsetzung (nach Abnahme des Umbauplans)

- [x] Extraktion v1.3 → `kapitel/*.md` (extraktor; aus PDF mit `pdftotext
      -layout`, keine .docx vorhanden), Kapitelstruktur (00 Management
      Summary + 23 Kapitel) und `Makefile`/`main.tex`/`praeambel.tex`
      eingerichtet, `literatur.bib` als leerer Stub angelegt. `make pdf`
      läuft fehlerfrei durch (latexmk-Exitcode 0, 90 Seiten, keine
      LaTeX-Warnungen im finalen Lauf). CI-Push-Trigger in
      `.github/workflows/build.yml` aktiviert (Pfad-Filter auf
      kapitel/abbildungen/*.tex/literatur.bib/Makefile/Workflow-Datei
      selbst) — noch nicht in echtem CI-Lauf verifiziert (lokal getestet
      mit Pandoc 2.9.2.1, CI pinnt 2.19.2).
      - Bekannter Nummerierungsfehler im Original (Kap. 7: „7.3" doppelt)
        korrigiert zu 7.3/7.4/7.5, mit HTML-Kommentar an der Stelle vermerkt
        (`kapitel/07-execution-model.md`).
      - 21 Abbildungs-Platzhalter (`TODO(abbildung)`) und 9
        `TODO(verify)`-Marker über die Kapitel verteilt gesetzt (siehe
        Aufschlüsselung unten) — Abbildungen entstehen gemäß UMBAUPLAN § 4
        neu als Skripte, `TODO(verify)`-Stellen sind bei der inhaltlichen
        Überarbeitung gegen Primärquellen zu prüfen.
      - **(Martin) Inhaltliche Auffälligkeiten aus der Extraktion, zur
        Entscheidung/Prüfung** (nicht selbst korrigiert):
        - `kapitel/02-architektonische-prinzipien.md`: Tabelle „Zuordnung zu
          Architekturkonzepten" (Original S. 10) verweist auf Kapitelnummern,
          die nicht zum Original-Inhaltsverzeichnis passen (z. B.
          „Berechtigungsmodell" als Kap. 12 statt 14, „Guardrails" als
          Kap. 13 statt 12, „Hooks" als Kap. 17 statt 18, ADR-Verweise als
          Kap. 18 statt 19). Wörtlich übernommen.
        - `kapitel/04-konfiguration-claude-md.md`: Tabelle „Aufbau und
          Sektionen" (S. 15) verweist bei „Cost Controls" auf „Kap. 14" für
          das Token Budget Management — das steht tatsächlich in Kap. 15
          (Wirtschaftlichkeit & Kostenmodell), nicht Kap. 14 (Security
          Model). Derselbe Verweis („Kap. 14") taucht auch im
          CLAUDE.md-Beispiel selbst als Kommentar auf.
        - `kapitel/06-agent-lifecycle.md` und `kapitel/07-execution-model.md`:
          Hinweis-Kästen verweisen auf „Kapitel 15" für die
          Multi-Agent-Workflows — im Original-Inhaltsverzeichnis tragen
          diese jedoch Kapitelnummer 16.
        - Abbildungsverzeichnis (Original S. 5) vs. Bildunterschriften im
          Fließtext: Bei Abbildung 2/3 sind Nummer und Reihenfolge
          vertauscht (Verzeichnis führt „2: SDLC-Agenten-Pipeline" / „3:
          Systemkontext", der Fließtext zeigt in dieser Reihenfolge aber
          „Abbildung 2: Systemkontext" vor „Abbildung 3:
          SDLC-Agenten-Pipeline"). Für die Platzhalter wurden die im
          Fließtext direkt an der Abbildungsposition stehenden, vollständigen
          Bildunterschriften übernommen (nicht die Kurzfassungen aus dem
          Verzeichnis), da sie inhaltlich zur Position passen.
        - `kapitel/19-architekturentscheidungen-adrs.md`: Task-Datei-Beispiel
          (ADR-4, Original S. 64) verwendet Zeitstempel
          „2025-03-04T10:00:00Z" — das Whitepaper selbst ist auf Version 1.3,
          März **2026** datiert. Möglicher Zahlen-/Datumsfehler im Original.
        - LaTeX-Feintypografie (nicht Teil der mechanischen Extraktion):
          Unnummerierte Original-Zwischenüberschriften (z. B. „Kernaussagen",
          „Das Orchestrator-Prinzip", ADR-Unterteile „Motivation / Kontext")
          werden von Pandoc/KOMA-Script aktuell automatisch nummeriert
          (z. B. „0.1 Kernaussagen", „1.1 Das Orchestrator-Prinzip") und
          verlassen damit stellenweise die Nummerierung des Originals (das
          diese Überschriften unnummeriert führt). Fachliche Entscheidung für
          die „Feintypografie am Ende in LaTeX" (siehe CLAUDE.md, Abschnitt
          „Format"): entweder unnummeriert lassen (Pandoc-Attribut `{-}`,
          erfordert Fence-bewusste Vorverarbeitung, da einfache sed-Filter
          sonst auch `#`-Kommentare in Codeblöcken träfen) oder so belassen.
      - Aufschlüsselung `TODO(verify)` / `TODO(abbildung)` je Kapitel:
        01: 0/1 · 02: 1/0 · 03: 0/4 · 04: 1/0 · 06: 1/0 · 07: 1/2 · 08: 2/3 ·
        11: 0/1 · 12: 0/2 · 13: 0/1 · 15: 1/0 · 16: 0/1 · 19: 1/4 (davon eine
        Abbildung ohne Nummer im Original-Abbildungsverzeichnis, S. 54) ·
        20: 1/0 · 21: 0/2 (Summe: 9 verify, 21 abbildung).
- [x] Teil VI „SoftwareFabrik" geschrieben: `kapitel/19-softwarefabrik.md`
      (neun Abschnitte, ~18 Druckseiten); bisherige Kapitel 19–23 auf 20–24
      aufgerückt (Kopfzeilen-Nummern angepasst, Querverweise im Bestand noch
      v1.3-nummeriert → wird mit der Modernisierung je Kapitel bereinigt).
      zweitgutachter-Review durchgeführt; alle WICHTIG-Befunde und fast alle
      KLEIN-Befunde eingearbeitet (u. a. Sandbox-Default klargestellt,
      SBOM-Default, Mandanten-Isolations-Einschränkung, Hochrisiko-Hinweis
      EU AI Act, Kennzeichnung der ROI-Modellrechnung in Kap. 00/15.4,
      AGENTS.md-Beleg). Faktenkorrektur aus Code-Verifikation: Run hat
      **13** Zustände, nicht 14 (Quellen-Set an 5 Stellen korrigiert;
      `RunStatus.java` gezählt); Tippfehler „getrunken"→„trunkiert" in
      Quellen-Set und Kapitel behoben.
      - Offen aus dem Review (verschoben): Glossar-Erweiterung um die
        Teil-VI-Begriffe (Run, Plan-Run, Quality Gate, Policy-as-Code,
        Attestierung, Warum-Trace, Mandant, Guardrails-Projektion,
        Debt-Ratchet, Slice/Blatt-Slice, Control Plane) → mit der
        Glossar-Modernisierung (P3); Abbildungen 21–30 → Abbildungsphase.
- [ ] Konzeptkapitel modernisieren in P1→P2→P3-Reihenfolge (UMBAUPLAN § 3);
      schnelllebige Angaben gegen Primärquellen mit Stand-Datum recherchieren;
      je Kapitel zweitgutachter-Review.
- [ ] Abbildungen als Skripte neu erzeugen (UMBAUPLAN § 4): ~16 aus v1.3
      konsolidiert + 10 neue aus den Mermaid-Systemdiagrammen.
- [ ] Später: Veröffentlichung (janda.io), optional public + Release + DOI
      (Zenodo-GitHub-Integration besteht bereits; archiviert nur öffentliche
      Releases).
