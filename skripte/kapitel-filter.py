#!/usr/bin/env python3
"""Markdown-Präprozessor für die Kapitel (stdin -> stdout).

Zwei Aufgaben, beide zaunbewusst (Codeblöcke bleiben unangetastet):
1. Nummerierte Überschriften ("## 3.1 Titel") verlieren ihre Nummer —
   LaTeX/KOMA-Script nummeriert selbst (ersetzt den früheren sed-Filter).
2. Unnummerierte Zwischenüberschriften der Ebenen 2-4 (z. B. "Kernaussagen",
   "Motivation / Kontext") erhalten das Pandoc-Attribut {-} und werden damit
   wie im Original ohne Nummer gesetzt (aber ins Inhaltsverzeichnis
   aufgenommen).
"""
import re
import sys

NUMMER = re.compile(r"^(#{1,4}) [0-9]+(\.[0-9]+)* ")
UEBERSCHRIFT = re.compile(r"^(#{2,4}) (?![0-9]+(\.[0-9]+)* )(.+?)\s*$")

in_fence = False
for line in sys.stdin:
    stripped = line.rstrip("\n")
    if stripped.startswith("```") or stripped.startswith("~~~"):
        in_fence = not in_fence
        sys.stdout.write(line)
        continue
    if not in_fence:
        m = NUMMER.match(stripped)
        if m:
            sys.stdout.write(NUMMER.sub(r"\1 ", stripped) + "\n")
            continue
        m = UEBERSCHRIFT.match(stripped)
        if m and not stripped.endswith("}"):
            sys.stdout.write(f"{m.group(1)} {m.group(3)} {{-}}\n")
            continue
    sys.stdout.write(line)
