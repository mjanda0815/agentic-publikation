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

## B. Nächste Arbeitsschritte (nach CLAUDE.md-Abnahme)

- [ ] Extraktion v1.3 → `kapitel/*.md` (extraktor; aus .docx falls verfügbar,
      sonst PDF), Kapitelstruktur und `Makefile`/`main.tex` einrichten.
- [ ] Bestandsaufnahme-Review des Ist-Stands (zweitgutachter): Was ist seit
      März 2026 überholt (Modelle, Tools, Preise, Features), was fehlt?
      → daraus die Arbeitsliste für die Modernisierung ableiten.
- [ ] Abbildungen des Originals sichten: welche werden als eigene Skripte
      neu erzeugt (harte Regel 5)?
- [ ] **SoftwareFabrik mit v1.3 verheiraten:** Grundlage ist die von Martin
      bereitgestellte Doku unter `quellen/softwarefabrik/` (INDEX,
      Systemüberblick, Architektur, Systemdiagramme, Domänenmodell); das Repo
      `/mnt/c/dev/SoftwareFabrik` nur zur Detail-Verifikation. Ablauf laut
      INITIAL_PROMPT.md: erst komplette Sichtung, dann Umbauplan (Ziel-
      Gliederung, Konzept↔Realisierung als roter Faden, Modernisierungsliste,
      Abbildungsplan, Version) zur Abnahme — erst danach Extraktion und Umbau.
      Public-Ready beachten: keine Secrets/Kundendetails.
- [ ] Später: Veröffentlichung (janda.io), optional public + Release + DOI
      (Zenodo-GitHub-Integration besteht bereits; archiviert nur öffentliche
      Releases).
