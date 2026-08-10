# LinkedIn-Post-Entwürfe zu den beiden Karussells (Fassung 3.0, August 2026)

Zwei Beiträge, je einer pro Karussell. Empfehlung: zeitversetzt posten —
zuerst das Whitepaper-Karussell (Prinzipien), einige Tage später das
Fabrik-Karussell (Praxis); der zweite Beitrag funktioniert auch allein,
gewinnt aber als Fortsetzung.

Mechanik: Das Karussell als **Dokument** hochladen (PDF), nicht als Bild —
LinkedIn blättert PDFs seitenweise. Dokumenttitel wird angezeigt,
Vorschlag jeweils unten. Links funktionieren im Beitragstext; wer die
Reichweiten-Folklore ernst nimmt, verschiebt sie in den ersten Kommentar —
beide Varianten sind vorbereitet.

---

## Post 1 — Whitepaper-Karussell (`carousel.pdf`)

**Dokumenttitel:** Agentic Software Development — die Prinzipien in 10 Folien

**Beitragstext:**

Der Engpass beim Einsatz von Coding-Agenten ist nicht das Modell. Es ist die fehlende Prozessschicht.

Coding-Agenten analysieren Repositories, ändern Code, rufen Build- und Testwerkzeuge auf. Das macht sie produktiv — und ihre Ausführung nichtdeterministisch und sicherheitsrelevant. In Enterprise- und regulierten Umgebungen muss Agentenarbeit deshalb spezifiziert, begrenzt, isoliert, geprüft, freigegeben und nachträglich rekonstruierbar sein.

Die 10 Folien fassen zusammen, was das architektonisch bedeutet:

▪ Nicht möglichst viele Agenten — eine Steuerschicht dazwischen.
▪ Single Writer: ein Schreiber je Arbeitskopie, mehrere unabhängige Prüfer.
▪ Wer schreibt, gibt nicht frei — Erzeugung und Freigabe sind technisch getrennt.
▪ Fail Closed: Ein Gate, dessen Ausfall wie Erfolg aussieht, ist schlimmer als kein Gate.
▪ Git trägt die Artefakte, die Datenbank den Prozesszustand.
▪ Für jeden Lauf rekonstruierbar: welche Policy, welches Modell, welche Freigabe.

Neu in der überarbeiteten Fassung 3.0: Ein eigener Teil dokumentiert mit der SoftwareFabrik die Referenzimplementierung dieser Architektur — von kontrollierten Einzel-Runs zu parallelen Agenten-Workflows (umgesetzt bis Release 0.30.0, hinter einem standardmäßig deaktivierten Feature-Flag).

Was das Dokument ausdrücklich nicht behauptet: quantifizierte Produktivitäts- oder ROI-Zahlen. Dafür fehlt eine kontrollierte Vergleichsmessung — die Rechnungen sind als Modellrechnungen gekennzeichnet.

Whitepaper (165 Seiten) und Sonderdruck, CC BY 4.0:
https://www.janda.io/veroeffentlichungen
Quellen, Abbildungsskripte und Build-Pipeline:
https://github.com/mjanda0815/agentic-publikation

Was die Praxis am Konzept korrigiert hat — die Referenzimplementierung hat vier Positionen des Whitepapers verschoben —, folgt in einem eigenen Beitrag.

#AgenticSoftwareDevelopment #CodingAgents #SoftwareArchitecture #EnterpriseArchitecture #Governance #Java #SpringBoot

**Variante „Links im ersten Kommentar":** Die beiden Link-Zeilen am Ende
durch „Whitepaper (165 Seiten, CC BY 4.0) und Quellen: Links im ersten
Kommentar." ersetzen; als ersten Kommentar posten:
„Whitepaper und Sonderdruck: https://www.janda.io/veroeffentlichungen —
Quellen und Build-Pipeline: https://github.com/mjanda0815/agentic-publikation"

---

## Post 2 — Fabrik-Karussell (`carousel-fabrik.pdf`)

**Dokumenttitel:** Die SoftwareFabrik — was die Praxis am Konzept korrigiert hat

**Beitragstext:**

Eine Architektur aufschreiben ist das eine. Sie zu bauen korrigiert sie.

Vor einer Woche habe ich hier die Prinzipien des Whitepapers „Agentic Software Development" gezeigt (Link zum Beitrag im ersten Kommentar). Heute der zweite Teil: was das Bauen daran korrigiert hat.

Aus dem Whitepaper wurde ein laufendes System: 30 fachliche Slices, 38 Releases in vier Monaten, rund 41.700 Zeilen Produktivcode, Testabdeckung als buildbrechendes Gate. Interessanter als die Zahlen sind die vier Stellen, an denen die Praxis das Konzept korrigiert hat:

1️⃣ Perspektivenvielfalt ist beim Prüfen wertvoller als beim Erzeugen. Geplant waren sieben parallele Spezialagenten — gebaut wurde ein schreibender Agent je Lauf, mit mehreren unabhängigen Prüfern danach.

2️⃣ Ein Retry ohne neue Information wiederholt nur den Fehler. Der Agent scheitert seltener am Programmieren als an der Realität des Repositories: veralteter Base-Branch, fremde parallele Änderungen, fremde CI.

3️⃣ Die Nachweisstruktur lässt sich nicht sauber nachrüsten. Acht Datenbankmigrationen in Folge enthielten nichts als Mandanten- und Nachweisstrukturen — und bestimmten rückwirkend, wo im Ablauf überhaupt Ereignisse entstehen müssen.

4️⃣ Kubernetes ist keine Voraussetzung. Souveränität schon: ein Anwendungscontainer, eine Datenbank, lokale Modelle, bis hin zum Air-Gap-Betrieb.

Dazu ein Befund am eigenen System, der hängen bleibt: Ein Gate, das sich selbst überspringt, sieht aus wie ein bestandenes Gate. Der Abhängigkeits-Scan der eigenen CI meldete monatelang Grün — ohne je vollständig gelaufen zu sein. Ein Prüfschritt muss nicht nur existieren; er muss beweisen, dass er gelaufen ist.

Der Sonderdruck (39 Seiten) beschreibt das System vollständig — einschließlich seiner Grenzen, der gezählten Architekturschuld und dessen, was ausdrücklich nicht behauptet wird: Produktivitäts- und ROI-Zahlen ohne kontrollierte Messung.

Sonderdruck und vollständiges Whitepaper (CC BY 4.0):
https://www.janda.io/veroeffentlichungen

#SoftwareFabrik #AgenticSoftwareDevelopment #CodingAgents #ControlPlane #SoftwareArchitecture #Java #SpringBoot

**Erster Kommentar (in jedem Fall posten — der Beitragstext verweist
darauf):**
„Teil 1 mit den Prinzipien des Whitepapers: <URL des ersten Beitrags
nach dem Posten hier eintragen> — Sonderdruck und Whitepaper (CC BY 4.0):
https://www.janda.io/veroeffentlichungen"

**Variante „Links komplett im ersten Kommentar":** Zusätzlich die
Link-Zeile im Beitragstext ersetzen durch „Sonderdruck (39 Seiten) und
Whitepaper: Link im ersten Kommentar."

**Hinweis:** Falls zwischen den Posts mehr oder weniger als eine Woche
liegt, „Vor einer Woche" im Einstieg anpassen (z. B. „Vor ein paar
Tagen", „Letzte Woche").

---

*Beide Texte halten die Projektregeln ein: keine erfundenen Zahlen (alle
Kennzahlen aus Kapitel 19, Erhebungsstand Release 0.30.0, 9. August 2026),
Feature-Flag-Vorbehalt genannt, keine ROI-Behauptungen, keine
Marketing-Superlative.*
