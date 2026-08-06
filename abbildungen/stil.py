"""Gemeinsamer Stil für alle Abbildungen der Publikation.

Gestaltungsprinzipien (angelehnt an dokumentierte Dataviz-Richtlinien,
angepasst für den wissenschaftlichen Druck):
- eine Serie = ein Farbton, kein Farbzyklus; Farbe validiert für Kontrast auf Weiß
- zurückhaltendes Raster (Haarlinien), nur horizontale Gridlines, keine Box
- Serifenschrift passend zum LaTeX-Fließtext (Latin Modern)
- Beschriftung deutsch, Dezimalkomma, Quelle + Stichtag in der Abbildung
"""

import locale
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Farbrollen (Druck auf weißem Papier)
BLAU = "#256abf"        # Primärserie (Kontrast auf Weiß > 4:1)
BLAU_HELL = "#9ec5f4"   # Rohdaten hinter geglätteter Serie
TINTE = "#0b0b0b"       # Primärtext
TINTE_SEKUNDAER = "#52514e"
GEDECKT = "#898781"     # Achsenbeschriftung, Quellenzeile
RASTER = "#e1e0d9"      # Gridline-Haarlinie
GRUNDLINIE = "#c3c2b7"  # Achsenlinie
EREIGNIS = "#898781"    # vertikale Ereignismarker

BREITE_TEXT = 6.3  # Zoll, entspricht ~16 cm Satzspiegel (A4, 2,5-cm-Ränder)


def aktiviere_stil() -> None:
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Latin Modern Roman", "DejaVu Serif"],
        "font.size": 9.5,
        "axes.titlesize": 10.5,
        "axes.labelsize": 9.5,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.edgecolor": GRUNDLINIE,
        "axes.labelcolor": TINTE_SEKUNDAER,
        "xtick.color": GEDECKT,
        "ytick.color": GEDECKT,
        "text.color": TINTE,
        "axes.grid": True,
        "grid.color": RASTER,
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "figure.dpi": 150,
        "savefig.bbox": "tight",
        "svg.fonttype": "none",
    })


def deutsches_zahlenformat(wert: float, nachkomma: int = 0) -> str:
    """1234.5 -> '1.234,5' (ohne locale-Abhängigkeit)."""
    s = f"{wert:,.{nachkomma}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", ".")


def achsen_aufraeumen(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(GRUNDLINIE)
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)
    ax.margins(x=0.01)


def quellenzeile(fig, text: str) -> None:
    fig.text(0.005, -0.02, text, fontsize=7.5, color=GEDECKT, ha="left", va="top")


def stichtag_text(d: date) -> str:
    return d.strftime("%d.%m.%Y")
