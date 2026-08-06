# Makefile — Pandoc/LaTeX-Build-Pipeline für die Diplomarbeit
#
# Quelle des Fließtexts sind die Markdown-Kapitel in kapitel/ (01–06).
# Die Datei kapitel/00-titel-verzeichnisse.md wird NICHT konvertiert —
# ihr Inhalt (Titelblatt, Verzeichnisse) wird durch main.tex/praeambel.tex
# als LaTeX-Verzeichnisse (\tableofcontents, \listoffigures, ...) ersetzt.
#
# Kapitel-Überschriften tragen im Markdown die Original-Nummerierung
# (z. B. "# 2 Blockchain Grundlagen", "## 2.1 Theoretische Grundlagen").
# Diese Nummer wird beim Konvertieren per sed entfernt, damit LaTeX/KOMA-Script
# nicht doppelt nummeriert (\chapter, \section etc. nummerieren automatisch).
# Die Markdown-Quelldateien selbst bleiben dabei unverändert.

PANDOC := pandoc
LATEXMK := latexmk
BUILD := build
KAPITEL := kapitel
CHAPTERS := 01 02 03 04 05 06 90

STRIP_NUMBERING := sed -E 's/^(\#{1,4}) [0-9]+(\.[0-9]+)* /\1 /'

.PHONY: all tex pdf html clean

all: pdf

$(BUILD):
	mkdir -p $(BUILD)

tex: $(BUILD)
	@for n in $(CHAPTERS); do \
		src=$$(ls $(KAPITEL)/$$n-*.md); \
		echo "Pandoc: $$src -> $(BUILD)/$$n.tex"; \
		$(STRIP_NUMBERING) "$$src" | $(PANDOC) -f markdown -t latex \
			--top-level-division=chapter --biblatex \
			-o $(BUILD)/$$n.tex; \
	done

pdf: tex
	$(LATEXMK) -pdf -interaction=nonstopmode -outdir=$(BUILD) main.tex

html: $(BUILD)
	@for n in $(CHAPTERS); do \
		src=$$(ls $(KAPITEL)/$$n-*.md); \
		echo "Vorschau einlesen: $$src"; \
	done
	@files=""; \
	for n in $(CHAPTERS); do \
		src=$$(ls $(KAPITEL)/$$n-*.md); \
		files="$$files $$src"; \
	done; \
	$(PANDOC) -f markdown -t html5 -s --top-level-division=chapter \
		-o $(BUILD)/vorschau.html $$files

pdfa: pdf
	gs -dPDFA=2 -dBATCH -dNOPAUSE -dPDFACompatibilityPolicy=1 \
		-sColorConversionStrategy=UseDeviceIndependentColor \
		-sDEVICE=pdfwrite -o $(BUILD)/main_pdfa.pdf $(BUILD)/main.pdf

clean:
	rm -rf $(BUILD)
