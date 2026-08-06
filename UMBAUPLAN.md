# Umbauplan: „Agentic Software Development" v1.3 → v2.0

**Status: ENTWURF zur Abnahme durch Martin.** Grundlage: vollständige Sichtung
des v1.3-Whitepapers (75 S., 23 Kapitel, 20 Abbildungen, 4 ADRs) und des
SoftwareFabrik-Quellen-Sets (`quellen/softwarefabrik/`, 13 Dokumente,
Faktenstand 0.19.0 @ `526d718`). Erst nach Abnahme beginnt die Textarbeit.

---

## 0. Befund der Sichtung (Kurzfassung)

**Was das Whitepaper behauptet:** Eine Hub-and-Spoke-Multi-Agent-Architektur
(7 SDLC-Agenten unter einem Orchestrator), Git-Worktree-Isolation, sechsstufige
Guardrails-Pipeline als Pflicht-Gate, Git-basierte Orchestrierung, Fünf-
Schichten-Memory, CLAUDE.md als Policy-Instrument — durchgehend am Beispiel
Claude Code, mit Java/Spring-Boot/DDD-Codebeispielen.

**Was die SoftwareFabrik davon realisiert hat:** Orchestrator-Prinzip,
Guardrails als eigene Schicht, deklarative Repo-Konfiguration, geteilter
Wissensstand, Zustandsautomat mit Stop-Conditions — alles bestätigt, vieles
erweitert (maschinelle Architektur-Durchsetzung, Governance/Nachweisführung,
Abo-Kostenmodell). Vier bewusste Positionsverschiebungen (Quelle: `11-mapping`,
§11.3): (1) ein Agent je Lauf + mehrere Prüfer statt paralleler Multi-Agent-
Erzeugung, (2) Regelkreis statt Retry, (3) Governance als Struktur statt
Ergänzung, (4) Souveränität statt Kubernetes.

**Was seit März 2026 fachlich überholt ist:** Modellnamen und Preise
(opus/sonnet/haiku, $15/$3/$0.25), 200K-Kontextfenster-Angabe, Task-Tool-
Parameterliste, CLAUDE.md-only-Konfiguration (heute: `AGENTS.md` als
werkzeugübergreifender De-facto-Standard), Kapitel 20 (Werkzeugvergleich
Claude Code vs. Devin/Cursor), reines Token-ROI-Modell (Abo-Modus fehlt).
Alle Punkte werden in der Umsetzung gegen Primärquellen mit Stand-Datum
recherchiert (harte Regel 2) — die Liste hier ist der Sichtungsbefund, noch
keine Recherche.

---

## 1. (a) Ziel-Gliederung der v2.0

### Empfehlung: eigener Hauptteil + leichte Verzahnung

**Der SoftwareFabrik-Teil wird ein eigener Hauptteil (neuer Teil VI), kein
verteiltes Einweben.** Begründung:

1. Harte Regel 6: Die Konzeptkapitel bleiben als modernisierte Fassung
   erkennbar; ein Einweben würde jedes Kapitel umschreiben und die
   Kernaussagen verwässern.
2. Der publizistische Reiz ist der Abgleich „so gedacht → so gebaut → das
   gelernt". Der trägt nur, wenn das Konzept vorher geschlossen dasteht.
3. Die Verzahnung passiert trotzdem — aber leichtgewichtig: Jedes
   Konzeptkapitel mit Praxisbezug erhält am Ende einen kurzen, einheitlich
   gestalteten Kasten **„Praxis-Check SoftwareFabrik"** (3–8 Zeilen:
   bestätigt/erweitert/abweichend/offen + Verweis auf den Abschnitt in
   Teil VI). Das ist der rote Faden, ohne Duplikation.

### Kapitelplan (v1.3 → v2.0)

| v1.3 | Behandlung in v2.0 |
|---|---|
| Management Summary | **Modernisieren + erweitern:** Kernaussage „Referenzarchitektur wurde als System gebaut" ergänzen (belegbare Aussagen aus `11-mapping` §11.5); 70–80-%-/€15–30-Zahlen explizit als Modellrechnung kennzeichnen; Abo-Modus-Realität ergänzen |
| 1 Warum KI-Agenten / Orchestrator | Bleibt, moderat modernisieren (Stand der Agentic-Tools 08/2026) + Praxis-Check |
| 2 Architektonische Prinzipien (AP-1…6) | Bleibt; Praxis-Check (u. a. AP-4: Branch- statt Worktree-Isolation in der Praxis) |
| 3 Agentenarchitektur | Bleibt; 3.5 Task-Tool-Parameter aktualisieren (Stand 08/2026) |
| 4 Konfiguration mit CLAUDE.md | **Umbauen:** vendor-neutral als „Deklarative Agenten-Konfiguration im Repository" — `AGENTS.md` als De-facto-Standard, CLAUDE.md als Projektion; Beispiel bleibt |
| 5 Agententypen & Modellauswahl | **Stark modernisieren:** aktuelle Modellfamilien mit Stand-Datum; Capability-Profile statt harter Modellnamen (Vorgriff auf Teil VI) |
| 6 Agent Lifecycle | Bleibt, leicht modernisieren + Praxis-Check (Run-Lebenszyklus) |
| 7 Execution Model | Bleibt + Praxis-Check (Pipeline statt Task-Graph; Backlog als eigentlicher Graph; Regelkreis statt Retry) |
| 8 Memory Architecture | Bleibt + Praxis-Check (vier Gedächtnisformen ohne Vektorspeicher; Begründung Reviewbarkeit/Zitierbarkeit) |
| 9 Failure Handling | Bleibt + Praxis-Check (Reviewer-Absturz ⇒ ERROR, fail closed) |
| 10 Die sieben Lebenszyklus-Agenten | Bleibt (Code prüfen/aktualisieren) + Praxis-Check (Rollen vs. Systemfunktionen) |
| 11 DDD-Integration | Bleibt + Praxis-Check (Entwicklungsprozess als Domäne; Aggregat = JPA-Entität als bewusste Pragmatik; kein Kafka) |
| 12 AI Risk Framework & Guardrails | Bleibt + Praxis-Check (Read-only-Reviewer-Schicht, drei Betriebsmodi, Sonderregeln, ohne AOP) |
| 13 Deployment | Bleibt als Konzeptkapitel, relativieren + Praxis-Check (K8s ist Option, nicht Voraussetzung) |
| 14 Security Model | Bleibt + Praxis-Check (SSRF/Host-Allowlist, EnvAllowlist, `--network=none`) |
| 15 Wirtschaftlichkeit & Kostenmodell | **Stark modernisieren:** aktuelle Preise mit Stand-Datum; **Abo- vs. Token-Abrechnung als eigener Abschnitt** (Kernkorrektur); ROI-Rechnung als Modellrechnung kennzeichnen |
| 16 Multi-Agent-Workflows | Bleibt, Aufruf-Patterns aktualisieren + Praxis-Check |
| 17 Java-Enterprise-Beispiele | Bleibt, Versionen aktualisieren (Spring Boot 4 ist Realität der Fabrik) |
| 18 MCP-Server & Hooks | **Modernisieren:** MCP ist seit 2026 Industriestandard, nicht mehr Anthropic-spezifisch; + Praxis-Check (Skill-Bibliothek als governtes Äquivalent) |
| 19 ADRs 1–4 | Bleiben wörtlich als Konzept-ADRs; je ADR ein Praxis-Check-Kasten (die spannendste Stelle des Abgleichs: alle vier wurden teils anders entschieden) |
| 20 Vergleich Claude Code vs. andere | **Ersetzen** durch „Die Vendor-Frage ist eine Konfigurationsfrage": kurzer aktueller Marktüberblick (Stand 08/2026) + Überleitung auf den Adapter-Ansatz |
| 21 End-to-End Payment Service | Bleibt; Schluss verweist auf den realen End-to-End-Pfad der Fabrik (Wizard → Run → Gate → PR) |
| 22 Troubleshooting | Bleibt, aktualisieren; um Praxis-Fallstricke aus `09-entwicklerhandbuch` §9.6 ergänzen |
| 23 Glossar | Erweitern (Run, Plan-Run, Quality Gate, Policy-as-Code, Attestierung, Warum-Trace, Mandant, Debt-Ratchet, …) |

### Neuer Teil VI: „Die SoftwareFabrik — von der Referenzarchitektur zum System"

Eingeschoben **vor** den ADRs/Referenzteil (neue Teile: I–V Konzept wie
bisher, VI SoftwareFabrik, VII Architekturentscheidungen & Referenz).
Neun Abschnitte (~25–30 Seiten), Struktur aus `11-mapping` §11.4:

1. Von der Referenzarchitektur zur Implementierung (Anspruch, Zeitraum, Kennzahlen)
2. Systemkontext und Bausteinsicht (Abb. 21–23)
3. Das Ausführungsmodell: der Run (Phasen, Zustände, Regelkreis; Abb. 24, 25, 30)
4. Vendor-Neutralität als Architektureigenschaft (Port, 10 Adapter, ArchUnit-Beweis, Abo-Modus; Abb. 27)
5. Guardrails in der Praxis (Review-Schicht, Gate-Policy, Betriebsmodi)
6. Governance und Nachweisführung (Mandanten, Policy-as-Code, Compliance-Profile, Hashkette, Warum-Trace; Abb. 28)
7. Betrieb und Souveränität (Deployment, Air-Gap, Lizenz; Abb. 29)
8. Was die Praxis am Konzept korrigiert hat (die vier Kernpunkte)
9. Grenzen und offene Punkte (ehrliche Bilanz inkl. §1.7/`12-kennzahlen` §12.4)

**Public-Ready-Leitplanke für Teil VI:** Kennzahlen, Architektur,
Mechanismen ja; keine Secrets, keine Kundendetails, keine Preis-/
Lizenzkonditionen des Produkts. Fundstellen-Fußnoten nennen Klassen-/
Dateinamen (wie im Quellen-Set), keine Repo-URLs, solange das
SoftwareFabrik-Repo privat ist.

## 2. (b) Konzept ↔ Realisierung als roter Faden

Drei Mechanismen, konsistent durchgehalten:

1. **Praxis-Check-Kästen** in den Konzeptkapiteln (s. o.), mit den vier
   Statuszeichen aus dem Mapping (bestätigt / erweitert / abweichend / offen).
2. **Teil VI, Abschnitt 8** bündelt die vier Positionsverschiebungen als
   eigenständige Erkenntnis-Sektion („Was der Bau eines realen Systems am
   Konzept korrigiert").
3. **Management Summary** erhält die Klammer: „v1.3 beschrieb die
   Referenzarchitektur; v2.0 belegt sie an einem gebauten System und
   dokumentiert, wo die Praxis das Konzept korrigiert hat."

## 3. (c) Modernisierungspunkte mit Priorität

**P1 — sachlich falsch/irreführend ohne Update (muss):**

1. Modellnamen, Preise, Kontextfenster (Kap. 5, 15, 8.1) → aktuelle Werte mit
   Stand-Datum aus Primärquellen; Preistabellen datieren.
2. Kostenmodell: Abo- vs. Token-Abrechnung (Kap. 15) — ein reines Token-ROI-
   Modell bildet die Realität 2026 nicht mehr ab (Beleg: Fabrik-Abo-Modus).
3. CLAUDE.md → `AGENTS.md`-Standard (Kap. 4, 18) — „eine Quelle, mehrere
   Projektionen".
4. Kap. 20 (Werkzeugvergleich) ersetzen — veraltet und durch den
   Adapter-Ansatz konzeptionell überholt.
5. ROI-/Aufwandszahlen (Summary, Kap. 15) als Modellrechnung kennzeichnen
   (harte Regel 1; `11-mapping` §11.5 „Nicht belegbar").

**P2 — veraltet, aber nicht falsch (soll):**

6. Task-Tool-Parameter und Agententypen (Kap. 3.5, 5) auf Stand 08/2026.
7. MCP-Kapitel: MCP als Industriestandard einordnen; Hooks-Stand prüfen.
8. Multi-Agent-Aufruf-Patterns (Kap. 16) gegen aktuelle Claude-Code-Fassung.
9. Java-/Spring-Boot-Versionsstände in Codebeispielen (Kap. 10, 17, 21)
   prüfen; wo sinnvoll auf die real erprobten Versionen der Fabrik heben
   (Java 25, Spring Boot 4) — Beispiele müssen lauffähig bleiben (harte
   Regel 3).
10. Kap. 13 Deployment um die On-Prem-/Souveränitätsperspektive relativieren.

**P3 — Kosmetik/Vollständigkeit (kann):**

11. Glossar-Erweiterung, Troubleshooting-Ergänzung, Abbildungsverzeichnis.
12. Redundanz Abb. 19/20 zu Abb. 15/16 auflösen (Konsolidierung).

## 4. (d) Abbildungsplan

Harte Regel 5: alle Grafiken werden als eingecheckte Skripte reproduzierbar
neu erzeugt (`abbildungen/`, Stil `stil.py`; Mermaid-Quellen → einheitliches
Rendering, Details in der Umsetzungsphase).

- **Aus v1.3 neu zu zeichnen (konsolidiert ~16 statt 20):** Abb. 1–18 nach
  Bedarf der modernisierten Kapitel; Abb. 19/20 werden mit 15/16
  zusammengelegt. Titelgrafik entfällt bzw. wird neu gestaltet.
- **Neu für Teil VI (aus `03-systemdiagramme.md`, Mermaid-Quellen liegen
  vor):** Abb. 21 Systemkontext, 22 Bausteinsicht, 23 Slice-Landkarte,
  24 Run-Sequenz, 25 Zustandsautomat, 26 ER-Ausschnitt, 27 Adapter-/
  Modellschicht, 28 Governance-Kette, 29 Deployment, 30 Korrekturschleife.
- Nummerierung schließt an v1.3 an (21 ff.), wie im Quellen-Set vorbereitet.

## 5. (e) Version und Umfang

- **Versionsnummer: 2.0** (nicht 1.4): neuer Hauptteil, korrigierte
  Kernaussagen (Kostenmodell, Multi-Agent-These relativiert), ersetztes
  Kapitel 20 — das ist eine inhaltliche Weiterentwicklung, keine Pflege.
- **Umfangsschätzung:** ~100–110 Seiten (75 Bestand − ~5 Konsolidierung
  + 25–30 Teil VI + Praxis-Checks/Modernisierung).
- **Arbeitsreihenfolge nach Abnahme** (wie INITIAL_PROMPT Schritt 3):
  Extraktion v1.3 → `kapitel/*.md` (extraktor) → `main.tex`/`Makefile`/Build
  → CI-Push-Trigger → Teil VI schreiben (Quellen-Set als Basis) →
  Konzeptkapitel modernisieren in P1→P2→P3-Reihenfolge, je Kapitel
  zweitgutachter-Review → Abbildungen → Feintypografie.

---

## 6. Entscheidungsvorlage (Martin)

| # | Frage | Empfehlung |
|---|---|---|
| E1 | **Lizenz der v2.0** | CC BY 4.0 — konsistent mit den DeFi-Papieren, Voraussetzung für sauberes Zenodo-DOI; Original war „Alle Rechte vorbehalten", Rechteinhaber ist Martin selbst, Umstellung also möglich |
| E2 | **Titel/Untertitel** | Haupttitel behalten („Agentic Software Development — Enterprise Architecture with AI Agents"); Untertitel neu, Vorschlag: „Vom Konzept zum System: Referenzarchitektur und ihre Realisierung als Agentic Software Factory. Praxisbeispiele mit Java, Spring Boot und Domain-Driven Design" |
| E3 | **Gliederungsvariante** | Eigener Teil VI + Praxis-Check-Kästen (dieser Plan); Alternative wäre volles Einweben — nicht empfohlen (s. § 1) |
| E4 | **Versionsnummer** | 2.0 |
| E5 | **Nennung „SoftwareFabrik"/Produktname** | Produktname + Kennzahlen ja (öffentliche Demo existiert), keine Preis-/Lizenzkonditionen; bitte bestätigen |
| E6 | **Repo-/Projektname** | `AGENTIC_Publikation` beibehalten, sofern nicht anders gewünscht |
