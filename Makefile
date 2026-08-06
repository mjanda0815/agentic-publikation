# Makefile — Pandoc/LaTeX-Build-Pipeline für das Whitepaper
# „Agentic Software Development — Enterprise Architecture with AI Agents"
#
# Quelle des Fließtexts sind die Markdown-Kapitel in kapitel/ (00–23).
# kapitel/00-management-summary.md ist das unnummerierte Management Summary
# (wird nach der Pandoc-Konvertierung von \chapter zu \addchap gewandelt,
# siehe Ziel `tex`). Kapitel 01–23 tragen die Original-Kapitelnummerierung.
#
# Kapitel-Überschriften tragen im Markdown die Original-Nummerierung
# (z. B. "# 1 Warum KI-Agenten in der Softwareentwicklung?",
# "## 3.1 Systemkontext ..."). Diese Nummer wird beim Konvertieren per sed
# entfernt, damit LaTeX/KOMA-Script nicht doppelt nummeriert (\chapter,
# \section etc. nummerieren automatisch). Die Markdown-Quelldateien selbst
# bleiben dabei unverändert.
#
# Die sechs Teile (TEIL I–VI) werden NICHT aus den Kapitel-Markdown-Dateien
# erzeugt, sondern als \part{...} direkt in main.tex gesetzt.

PANDOC := pandoc
LATEXMK := latexmk
BUILD := build
KAPITEL := kapitel
CHAPTERS := 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24

STRIP_NUMBERING := sed -E 's/^(\#{1,4}) [0-9]+(\.[0-9]+)* /\1 /'
# Management Summary (00) ist ein unnummertes Kapitel: \chapter -> \addchap
ADDCHAP := sed -E 's/^\\chapter\{/\\addchap{/'
# Pandoc 2.9 wendet --id-prefix nicht auf automatische Überschriften-Anker an
# (nur auf Fußnoten). Gleichlautende Zwischenüberschriften in verschiedenen
# Kapiteln (z. B. "Shared Knowledge Store" in Kap. 8 und Kap. 19) erzeugen
# sonst kollidierende \label/\hypertarget-Ziele. Fix: Anker-IDs je Kapitel
# per sed mit dem Kapitelpräfix versehen (rein technisch, kein Sichttext).

.PHONY: all tex pdf html clean

all: pdf

$(BUILD):
	mkdir -p $(BUILD)

tex: $(BUILD)
	@for n in $(CHAPTERS); do \
		src=$$(ls $(KAPITEL)/$$n-*.md); \
		echo "Pandoc: $$src -> $(BUILD)/$$n.tex"; \
		if [ "$$n" = "00" ]; then \
			$(STRIP_NUMBERING) "$$src" | $(PANDOC) -f markdown -t latex \
				--top-level-division=chapter --biblatex --no-highlight \
				| sed -E "s/\\\\(hypertarget|label)\\{/\\\\\\1{k$$n-/g" \
				| $(ADDCHAP) > $(BUILD)/$$n.tex; \
		else \
			$(STRIP_NUMBERING) "$$src" | $(PANDOC) -f markdown -t latex \
				--top-level-division=chapter --biblatex --no-highlight \
				| sed -E "s/\\\\(hypertarget|label)\\{/\\\\\\1{k$$n-/g" \
				> $(BUILD)/$$n.tex; \
		fi; \
	done

pdf: tex
	$(LATEXMK) -pdf -interaction=nonstopmode -outdir=$(BUILD) main.tex

html: $(BUILD)
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
