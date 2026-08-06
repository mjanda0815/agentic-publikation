# Agentic Software Development — Enterprise Architecture with AI Agents

Von kontrollierten Einzel-Runs zur parallelen Agentic Software Factory.
Praxisbeispiele mit Java, Spring Boot und Domain-Driven Design.

**Martin Janda** · Version 2.2 (August 2026) · Lizenz: [CC BY 4.0](LICENSE)

<!-- DOI-BADGE -->

Ein Whitepaper über den kontrollierten Einsatz von Coding-Agenten in
Enterprise- und regulierten Umgebungen — und über das System, das aus seiner
Referenzarchitektur entstanden ist.

## Worum es geht

Coding-Agenten können Repositories analysieren, Code verändern, Build- und
Testwerkzeuge aufrufen und Ergebnisse iterativ korrigieren. Für den
Enterprise-Einsatz genügt dafür kein leistungsfähiges Modell: Agentenarbeit
muss spezifiziert, begrenzt, isoliert, geprüft, freigegeben und nachträglich
rekonstruiert werden können.

Das Whitepaper beschreibt eine **Control-Plane-Architektur** für diesen Zweck
und dokumentiert mit der *SoftwareFabrik* eine Referenzimplementierung, die
sie produktisiert. Es unterscheidet dabei konsequent zwischen implementiertem
Stand, Zielarchitektur und Roadmap — und benennt in einem eigenen Abschnitt
die offenen Punkte und die Grenzen der Aussagekraft.

Tragende Prinzipien: **Single Writer per Workspace** (pro Arbeitskopie
schreibt genau ein Agent), **unabhängige Prüfung** (wer schreibt, gibt nicht
frei), **Fail Closed** (ein Gate, dessen Ausfall wie Erfolg aussieht, ist
schlimmer als kein Gate) und **Souveränität** (betreibbar bis zum Air-Gap).

Quantifizierte Produktivitäts- oder ROI-Werte werden ausdrücklich **nicht**
behauptet — dafür fehlt eine kontrollierte Vergleichsmessung. Die
Wirtschaftlichkeitsrechnungen sind als Modellrechnungen gekennzeichnet, der
Messplan steht in Abschnitt 15.6.

## Die Dokumente

| Dokument | Umfang | Inhalt |
|---|---|---|
| **Whitepaper** (`main.tex`) | 157 Seiten | Vollständige Fassung, Teile I–VI |
| **Sonderdruck „Die SoftwareFabrik"** (`main-fabrik.tex`) | 33 Seiten | Kapitel 19 als eigenständiges PDF — dieselbe Quelle, eigene Titelei |
| **Karussell zum Whitepaper** (`carousel/carousel.tex`) | 10 Folien | Prinzipiengetriebener Kurzeinstieg |
| **Karussell zum Sonderdruck** (`carousel/carousel-fabrik.tex`) | 10 Folien | Praxisgetrieben: was die Praxis am Konzept korrigiert hat |

## Bauen

Voraussetzungen: TeX Live (mit `latexmk`, `biber`), Pandoc, Python 3.
Für die Abbildungen zusätzlich Node.js (mermaid-cli via `npx`) — die
gerenderten PDFs sind allerdings eingecheckt, sodass der Dokumentbau ohne
Node auskommt.

```bash
make pdf         # Whitepaper       -> build/main.pdf
make fabrik      # Sonderdruck      -> build/main-fabrik.pdf
make karussell   # beide Karussells -> carousel/*.pdf
make abbildungen # Mermaid-Quellen  -> abbildungen/out/*.pdf (braucht Node)
```

Prüfen, dass alles aus einem frischen Checkout baut:

```bash
git clone --depth 1 <repo-url> /tmp/klontest
make -C /tmp/klontest pdf fabrik karussell
```

## Aufbau des Repositories

```
kapitel/        Fließtext als Markdown (00–24) — alleinige Quelle
main.tex        Whitepaper; main-fabrik.tex: Sonderdruck aus Kapitel 19
abbildungen/    Mermaid-Quellen (*.mmd) + gerenderte PDFs in out/
carousel/       Beide Karussells, gemeinsamer Stil in karussell.sty
skripte/        Build-Filter (Nummernstrippung, Sonderdruck-Verweise)
literatur.bib   Bibliographie (BibLaTeX)
quellen/        Originalfassung v1.3 und die Erhebungsgrundlagen zu Kapitel 19
TODO.md         Arbeitsstand und Entscheidungshistorie
```

Alle Abbildungen sind Eigenanfertigungen und liegen als Skript vor — es sind
keine Fremdgrafiken übernommen. Der Fließtext liegt ausschließlich in
`kapitel/`; die `.tex`-Dateien setzen ihn nur.

## Zitieren

Siehe [`CITATION.cff`](CITATION.cff). Nach der ersten Archivierung auf Zenodo
gilt zusätzlich die dort vergebene DOI.

## Lizenz

[Creative Commons Attribution 4.0 International](LICENSE) (CC BY 4.0) —
Weiterverwendung und Bearbeitung sind erlaubt, solange die Urheberschaft
genannt wird.
