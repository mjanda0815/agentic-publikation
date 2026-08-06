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
- [x] **P1-Modernisierung** (06.08.2026): Kap. 15.1 Preistabelle aktuell
      (Claude-5-Familie, Stand 06.08.2026, [@anthropicmodels]) + Hinweis auf
      Preisverfall seit v1.3; neues Kap. 15.5 „Abo- statt Token-Abrechnung";
      Kap. 5 Modellauswahl auf Fähigkeitsklassen umgestellt; Kap. 3.5
      Task-Tool-Parameter auf Stand 08/2026; Kap. 8.1 Kontextfenster
      200K→1M korrigiert; Kap. 4 um AGENTS.md-Standard ergänzt; Kap. 18 um
      MCP-als-Industriestandard-Einordnung (Agentic AI Foundation/Linux
      Foundation, Primärquelle [@mcp]); Kap. 21 komplett ersetzt („Die
      Vendor-Frage ist eine Konfigurationsfrage"). Erste Praxis-Check-Kästen
      in Kap. 4, 5, 15, 18, 21. Querverweis-Fehler des Originals in Kap. 4,
      6, 7 korrigiert (Kap.-14/15/16-Verweise). Neue Primärquellen in
      literatur.bib: anthropicmodels, claudecodedocs, mcp.
- [x] **P2/P3-Modernisierung** (06.08.2026): Kap. 16 Aufruf-Patterns auf
      Agent-Tool/SendMessage-Stand 08/2026; Versionshinweise für die
      Java-Beispiele in Kap. 10 und 17 (bewusst auf Java 21/Spring Boot 3.x
      belassen, Verweis auf Boot-4-Fallstricke in Kap. 19); Kap. 13 um
      Einordnung „Kubernetes ist Option, nicht Voraussetzung" ergänzt;
      Praxis-Check-Kästen jetzt flächendeckend (Kap. 1–18, 20 je ADR,
      21–23); Glossar um 13 Teil-VI-Begriffe erweitert (alphabetisch
      einsortiert).
- [x] **Abbildungen** (06.08.2026): 29 Diagramme als Mermaid-Quellen unter
      `abbildungen/*.mmd` (19 aus v1.3 neu gezeichnet inkl.
      Worktree-Lebenszyklus; 10 aus den SoftwareFabrik-Systemdiagrammen
      übernommen), gerendert nach `abbildungen/out/*.pdf` via
      `make abbildungen` (mermaid-cli/npx, Stil in `abbildungen/mermaid.json`).
      Outputs werden mitversioniert (CI braucht kein Node). Die
      v1.3-Abbildungen 19/20 wurden planmäßig mit Kap. 16/20 konsolidiert;
      Bildunterschriften ohne harte Nummern (LaTeX nummeriert automatisch).
      Pandoc-Höhenkappe (`FIG_HEIGHT`) im Makefile gegen überlaufende
      Floats. Hinweis: `abbildungen/stil.py` (matplotlib) bleibt für
      künftige Datendiagramme liegen, wird von den Mermaid-Diagrammen nicht
      genutzt.
- [x] **Feintypografie** (06.08.2026): Unnummerierte Original-
      Zwischenüberschriften werden jetzt korrekt ohne Nummer gesetzt
      (zaunbewusster Präprozessor `skripte/kapitel-filter.py` ersetzt den
      sed-Filter; Pandoc-`{-}`, Überschriften bleiben im Inhaltsverzeichnis);
      Abbildungsverzeichnis via `\listoffigures`; Slice-Landkarte (abb23)
      kompakt neu gelayoutet. Beide letzten `TODO(verify)`-Marker aufgelöst:
      Embedding-Modell `deepset-mxbai-embed-de-large-v1` per Primärquelle
      belegt (Hugging Face, [@mxbaide]); Datumsfehler „2025-03-04" im
      ADR-4-Beispiel des Originals auf 2026 korrigiert.
- [x] **Schlussdurchlauf + v2.1** (06.08.2026): Kapitelübergreifendes
      Schlussgutachten (zweitgutachter auf Fable 5, Urteil: freigabefähig
      nach Punktkorrekturen) und Martins Prüfung (anpassungen/) gesammelt
      umgesetzt — im 2.1-Umfang gemäß der Versionsstrategie in
      anpassungen/whitepaper_anpassungen.md (§23; die 3.0-Gesamtumgliederung
      folgt erst mit implementierter paralleler Analyse und Messdaten):
      Management Summary neu (Control-Plane-These, 7 Kernaussagen),
      Untertitel neu, Version 2.1; Kapitel 19 in Stand (19.1–19.9) und
      Zielbild geteilt, neues 19.10 „Roadmap zum parallelen Workflow" mit
      Zielarchitektur-Diagramm (abb31) und Threats-to-Validity-Block in
      19.9; ADR-Status-Vermerke (v2.1) je ADR; Kap. 15 zu
      „Wirtschaftlichkeitshypothese, Kostenmodell und Messplan" mit neuem
      15.6 Messplan; Formulierungen präzisiert (Guardrails-Zusage, Claim
      Verification, Kontrollprofile, deterministisch→nachvollziehbar);
      Glossar um 10 Zielarchitektur-Begriffe. Alle Gutachten-Befunde
      eingearbeitet (u. a. .mcp.json statt settings.json mit realem
      MCP-Referenzserver, Codex-CLI-Quelle korrigiert, Glossar-MCP-Eintrag,
      ROI-Arithmetik, v1.3-Preisstand-Kennzeichnungen, 18
      Anführungszeichen-Fixes, BAFA-Beispiel anonymisiert, RFC 9457,
      @JobWorker-Hinweis). Tokenizer-Attribution (Opus 4.7) war korrekt —
      durch Anthropic-Modellübersicht gedeckt, keine Änderung.
      Abbildungen: Farbschema umgesetzt (schwarze Rahmen, blaue Pfeile,
      semantische Pastelltöne; Sequenz-Schriftgrößen erhöht), alle 30
      Diagramme neu gerendert.
- [x] **Autorenreview v2.1 eingearbeitet** (06.08.2026): Kap. 1 neu (Start
      bei Coding-Agenten und Prozessschicht statt Claude Code als
      Fundament), Kap. 2 auf acht neue Prinzipien umgestellt (AP-1
      Controlled Non-Determinism … AP-8 Sovereign by Default; alle
      AP-Verweise dokumentweit umgezogen), Kap. 3 Hub-and-Spoke als
      logische Rollenstruktur eingeordnet; ADR-Status-Blöcke (ADR-1
      Superseded, ADR-2/4 Amended) plus neue ADRs 5–8; Kap. 22 zweigeteilt
      (implementierter Single-Run-Prozess / geplanter paralleler Workflow);
      ROI-, Prozent- und Faktorangaben als Annahmen gekennzeichnet;
      Parallelisierungskosten-Aussage richtiggestellt; 0-€-Bewertung,
      Audit-Altbestand und SBOM-Skip als offene Punkte im Sinne von AP-7
      benannt; alle Codezeilen > 92 Zeichen manuell umgebrochen; Tippfehler
      und Anführungszeichen bereinigt; Abbildungen 13/17/22/27/31
      vergrößert bzw. neu gelayoutet.
- [x] **Zweiter Autorenreview eingearbeitet** (06.08.2026, vor
      Veröffentlichung): Kap. 22.2 neu gefasst (keine Sieben-Agenten-
      Erzählung mehr, sondern Phasen + Gegenüberstellung Teil A/B);
      ADR-Status auf Entscheidungs- vs. Implementierungsstatus getrennt
      (ADR-5–8 jetzt *Accepted* / *Planned* statt *Proposed*), historische
      Wirkannahmen der ADRs 1–4 im Statuskasten als ungemessen
      gekennzeichnet; versteckte Abhängigkeit im geplanten Payment-Workflow
      aufgelöst (Contract Tasks 1a extern / 1b intern, Task 3 hängt an 1a+1b
      statt an Task 2), Parallelitätsgewinn als angestrebtes Ergebnis mit
      Verweis auf den Messplan formuliert; absolute Aussagen in Kap. 12 und
      ADR-3 abgeschwächt (Defense in Depth ohne Vollständigkeitsanspruch,
      Prüfprozess reproduzierbar vs. Prüfergebnisse nichtdeterministisch);
      drei Produktlücken (Preisstatus, Legacy-Auditdaten, SBOM-Scanner) in
      die Tabelle 19.9 aufgenommen; AP-Hinweis in Kap. 2 präzisiert;
      Textfehler bereinigt (Anführungszeichen, Claim Verification,
      maxTurns- und Capability-Zeilen in Kap. 23).
      Layout: Praxis-Check-Kästen brechen nicht mehr über Seitengrenzen
      (`needspace`), Float-Parameter halten Abbildungen beim Bezugstext,
      Agenten-Katalog in zwei lesbare Tabellen geteilt, Zustandsautomat ins
      Hochformat, alle Codezeilen auf die reale Satzbreite (84 Zeichen)
      umgebrochen — keine Umbruchmarker mehr im Dokument.
- [ ] (Martin) Finale Durchsicht der v2.1; danach „Entwurf"-Vermerk von der
      Titelseite nehmen und Veröffentlichungsschritte (janda.io, optional
      Repo public + Release + Zenodo-DOI).
- [ ] Optional für v3.0 (laut anpassungen/whitepaper_anpassungen.md §23):
      neue Gesamtgliederung in fünf Teile, Workflow-Fallstudie mit erster
      implementierter paralleler Analyse, Messdaten aus dem Messplan (15.6),
      Evidenzpaket.
- [ ] Später: Veröffentlichung (janda.io), optional public + Release + DOI
      (Zenodo-GitHub-Integration besteht bereits; archiviert nur öffentliche
      Releases).
