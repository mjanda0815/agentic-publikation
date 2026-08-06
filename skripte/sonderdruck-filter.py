#!/usr/bin/env python3
"""Bereitet kapitel/19-softwarefabrik.md fuer den eigenstaendigen Sonderdruck auf.

Das Kapitel ist Teil des Whitepapers und verweist rund dreissig Mal auf dessen
uebrige Kapitel. In einem Auszug zeigten diese Verweise ins Leere. Der Filter
schreibt sie deshalb auf die Quelle um:

    "Kapitel 12"  ->  "Kapitel 12 des Whitepapers"
    "Kap. 15"     ->  "Kapitel 15 des Whitepapers"

Nicht umgeschrieben werden:
  * Bereichsangaben wie "Kapitel 1-18" (Halbgeviertstrich) - dort macht der
    Satz die Zugehoerigkeit ohnehin explizit,
  * Verweise auf Abschnitte des Kapitels selbst (19.1, 19.10, ...),
  * ADR-Verweise - die Einordnung uebernimmt das Vorwort des Sonderdrucks,
    weil eine Umschreibung mitten im Satz ("Und ADR-4 gilt ...") den Text
    unlesbar machen wuerde.

Der Filter veraendert die Markdown-Quelle nicht; er schreibt nach stdout.
Aufruf: python3 skripte/sonderdruck-filter.py kapitel/19-softwarefabrik.md
"""

import re
import sys

# Erfasst auch Aufzaehlungen ("Kapitel 1, 3, 10"), damit der Zusatz ans Ende
# der Aufzaehlung wandert und nicht hinter die erste Zahl. Bereichsangaben mit
# Halbgeviertstrich ("Kapitel 1–18", "Kapitel 12–14") bleiben unberuehrt: dort
# steht die Zugehoerigkeit bereits im Satz.
KAPITEL = re.compile(
    r"\bKap(?:itel|\.) (\d{1,2}(?:\s*(?:,|und|sowie)\s*\d{1,2})*)(?![\d–—-])"
)


def umschreiben(text: str) -> str:
    def ersetze(m: re.Match) -> str:
        nummern = m.group(1)
        if nummern == "19":                      # das Kapitel selbst
            return m.group(0)
        return f"Kapitel {nummern} des Whitepapers"

    return KAPITEL.sub(ersetze, text)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        quelle = f.read()

    # Codebloecke und Inline-Code bleiben unberuehrt: dort stehen Dateipfade
    # und Klassennamen, keine Querverweise.
    teile = re.split(r"(```.*?```|`[^`\n]+`)", quelle, flags=re.DOTALL)
    for i in range(0, len(teile), 2):            # nur die Nicht-Code-Teile
        teile[i] = umschreiben(teile[i])

    sys.stdout.write("".join(teile))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
