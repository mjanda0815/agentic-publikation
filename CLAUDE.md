# CLAUDE.md — Whitepaper-Modernisierung „Agentic Software Development"

> **STATUS: ENTWURF zur Abnahme durch Martin.** Struktur und Baukasten sind vom
> DeFi-Publikationsprojekt übernommen; die fachlichen Regeln (insb. Quellen und
> Lizenz) bitte prüfen und freigeben bzw. anpassen.

## Projekt

Modernisierung des Whitepapers „Agentic Software Development — Enterprise
Architecture with AI Agents" (Version 1.3, März 2026; 75 Seiten, Word-Satz) zu
einer aktualisierten, reproduzierbar gebauten Fassung — **erweitert um einen
neuen Hauptabschnitt, der Martins SoftwareFabrik vollständig beschreibt**
(das Whitepaper war ihre konzeptionelle Basis; Quelle der Wahrheit ist das
Repo `/mnt/c/dev/SoftwareFabrik`, daraus ableiten, nichts erfinden; keine
Secrets/Zugangsdaten/Kundendetails übernehmen). Die Original-PDF liegt unter
`quellen/Agentic_Software_Development_v13.pdf`; falls die Word-Quelldatei
(.docx) verfügbar ist, gehört sie ebenfalls nach `quellen/` (bessere
Extraktionsbasis als das PDF). Einstieg für die erste Session:
`INITIAL_PROMPT.md`. Die Arbeitsliste ist `TODO.md` — Single Source of Truth
für offene Aufgaben.

## Arbeitsweise

- Sprache aller Inhalte: **Deutsch** (wie das Original; englische Fachbegriffe
  des Felds bleiben englisch), sachlicher Stil, keine Marketing-Sprache.
- Immer TODO.md pflegen: erledigt `[x]`, neue Erkenntnisse ergänzen, nie löschen.
- Kapitelweise arbeiten (`kapitel/`), nach jedem Kapitel Diff-Zusammenfassung.
- **Public-Ready-Regel (Lektion aus dem DeFi-Projekt):** Das Repo wird von
  Commit 1 an so geführt, dass es jederzeit ohne History-Rewrite öffentlich
  gestellt werden kann. Das heißt: keine personenbezogenen Daten, keine
  Zugangsdaten, keine Bewertungsnoten oder vertraulichen Kundendetails —
  weder in Dateien noch in Commit-Messages. Interne Notizen, die das verletzen
  würden, gehören nicht ins Repo (oder werden publish-tauglich formuliert).

## Harte Regeln (nicht verhandelbar)

1. **Keine erfundenen Fakten oder Zahlen.** Nicht Verifizierbares als
   `TODO(verify): …` markieren statt schätzen.
2. **Schnelllebige Angaben immer mit Stand-Datum:** Modellnamen und -versionen,
   Tool-Features, Preise, Kontextfenster, Benchmarks. Belege aus Primärquellen
   (Hersteller-Dokumentation, Release Notes, Papers, offizielle Ankündigungen);
   Blogaggregatoren und Hörensagen sind kein Beleg.
3. **Code-Beispiele müssen lauffähig sein** (Java/Spring Boot/DDD wie im
   Original) bzw. sind als Pseudocode/Skizze gekennzeichnet; getestete
   Beispiele mit Versionsangaben der verwendeten Abhängigkeiten.
4. **Eigene Erfahrungswerte als solche kennzeichnen** — sie sind zulässig und
   erwünscht (Praxis-Whitepaper), aber klar von belegten Fremdaussagen zu
   trennen.
5. **Keine Fremdabbildungen.** Grafiken werden als Skripte unter `abbildungen/`
   neu erzeugt (Stil: `stil.py`), Daten eingecheckt → reproduzierbar.
6. **Kernaussagen des Originals nicht verfälschen** — es bleibt die
   modernisierte Fassung desselben Whitepapers; Neues (seit v1.3) kommt in
   gekennzeichnete Abschnitte.

## Modell-Politik

- Mechanische Arbeit (Extraktion, Konvertierung, Builds, Tippfehler) →
  Subagent `extraktor`.
- Review nach jedem inhaltlich überarbeiteten Kapitel → Subagent
  `zweitgutachter`.
- Inhaltliche Überarbeitung, Analyse, Neuformulierungen → Hauptsession.

## Format

Workflow wie im DeFi-Projekt: Kapitel als Markdown in `kapitel/`
(01-….md, 02-….md, …), Zitate `[@key]` (BibLaTeX in `literatur.bib`),
Konvertierung per Pandoc ins LaTeX-Projekt (`praeambel.tex` liegt bereit,
`main.tex` entsteht nach der Extraktion), Feintypografie am Ende in LaTeX.
Das kopierte `Makefile` ist noch auf die DeFi-Kapitelnummern eingestellt —
bei der Extraktion anpassen.

## Grundsatzentscheidungen (von Martin entschieden, 06.08.2026)

- **Lizenz der Neuauflage:** CC BY 4.0.
- **Zielumfang:** inhaltliche Erweiterung gemäß abgenommenem `UMBAUPLAN.md`
  (Version 2.0; neuer Teil VI „SoftwareFabrik" + Praxis-Check-Kästen).
- **Titel:** Haupttitel unverändert; Untertitel neu: „Vom Konzept zum System:
  Referenzarchitektur und ihre Realisierung als Agentic Software Factory.
  Praxisbeispiele mit Java, Spring Boot und Domain-Driven Design".
- **Projektname/Repo-Name:** bleibt `AGENTIC_Publikation`.

## Befehle

- Build: `make pdf` (Pandoc → latexmk/biber) → `build/main.pdf`
- Sonderdruck SoftwareFabrik: `make fabrik` → `build/main-fabrik.pdf`
  (eigenständiges PDF aus **derselben** `kapitel/19-softwarefabrik.md`;
  `skripte/sonderdruck-filter.py` kennzeichnet die Verweise auf die übrigen
  Kapitel. Bewusst kein zweiter Text über dasselbe System — zwei Fassungen
  liefen bei jedem Release auseinander.)
- LinkedIn-Karussell: `make karussell` → `carousel/carousel.pdf`
- Abbildungen: `make abbildungen` (Mermaid → `abbildungen/out/`)

## Projektstruktur

```
quellen/        Original-PDF (v1.3), später ggf. .docx, recherchierte Belege
kapitel/        modernisierte Kapitel als Markdown (entsteht mit der Extraktion)
abbildungen/    Skripte + daten/ für eigene Grafiken (stil.py liegt bereit)
carousel/       LinkedIn-Karussell (carousel.tex, folientexte.txt, karussell.sty)
skripte/        Build-Filter (kapitel-filter.py, sonderdruck-filter.py)
main.tex        Whitepaper; main-fabrik.tex: Sonderdruck aus Kapitel 19
literatur.bib   Bibliographie (entsteht mit der Überarbeitung)
TODO.md         Aufgabenliste (Single Source of Truth, public-ready formuliert)
```
