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
- [ ] **(Martin) UMBAUPLAN.md abnehmen** — insb. Entscheidungen E1–E6
      (Lizenz, Untertitel, Gliederungsvariante, Version, Produktnennungs-
      Grenzen, Repo-Name).

## C. Umsetzung (nach Abnahme des Umbauplans)

- [ ] Extraktion v1.3 → `kapitel/*.md` (extraktor; aus .docx falls verfügbar,
      sonst PDF), Kapitelstruktur und `Makefile`/`main.tex` einrichten,
      Build zum Laufen bringen, CI-Push-Trigger aktivieren.
- [ ] Teil VI „SoftwareFabrik" schreiben (Quellen-Set als Basis; Repo
      `/mnt/c/dev/SoftwareFabrik` nur zur Detail-Verifikation; Public-Ready:
      keine Secrets/Kundendetails/Konditionen).
- [ ] Konzeptkapitel modernisieren in P1→P2→P3-Reihenfolge (UMBAUPLAN § 3);
      schnelllebige Angaben gegen Primärquellen mit Stand-Datum recherchieren;
      je Kapitel zweitgutachter-Review.
- [ ] Abbildungen als Skripte neu erzeugen (UMBAUPLAN § 4): ~16 aus v1.3
      konsolidiert + 10 neue aus den Mermaid-Systemdiagrammen.
- [ ] Später: Veröffentlichung (janda.io), optional public + Release + DOI
      (Zenodo-GitHub-Integration besteht bereits; archiviert nur öffentliche
      Releases).
