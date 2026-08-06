# Quellen-Set: Die SoftwareFabrik als Referenzimplementierung

**Zweck.** Dieses Verzeichnis liefert die Faktenbasis, um das Whitepaper
„Agentic Software Development – Enterprise Architecture with AI Agents"
(v1.3, März 2026) um ein Kapitel zu erweitern, das die konzeptionelle
Referenzarchitektur an einem **real gebauten, laufenden System** belegt:
der *Agentic Software Factory* (SoftwareFabrik).

**Faktenstand.** Alle Angaben sind aus dem Quellcode erhoben, nicht aus
älterer Projektdokumentation (die im Repo teils auf v0.9.1 stehengeblieben
ist). Erhebungsbasis:

| | |
|---|---|
| Repository | `/mnt/c/dev/SoftwareFabrik`, Branch `main` |
| Commit | `526d718` (2026-07-26) |
| Produktversion | 0.19.0 (`app/pom.xml`), Buildnummer-Anzeige „Build #63" |
| Erhebungsdatum | 2026-08-06 |

---

## Die Dokumente

| Datei | Inhalt | Nutzbar für |
|---|---|---|
| `01-systemueberblick.md` | Was das System ist, Zahlen, Fähigkeiten, bewusste Nicht-Ziele | Kapiteleinstieg, Management-Summary-Ergänzung |
| `02-architektur.md` | Leitprinzipien, modularer Monolith, 27 Slices, Schichtenmodell, maschinelle Architektur-Durchsetzung (ArchUnit + Debt-Ratchet) | Architekturkapitel |
| `03-systemdiagramme.md` | 9 Diagramme als Mermaid-Quelle (Kontext, Container, Komponenten, Run-Sequenz, Zustandsautomat, ER, Deployment, Governance, Adapter) | Abbildungen |
| `04-domaenenmodell.md` | Aggregate, 39 Tabellen, 37 Flyway-Migrationen, Aggregatgrenzen | DDD-Kapitel |
| `05-run-pipeline.md` | Der Run als Ausführungsmodell: 7 Phasen, 14 Zustände, Korrekturschleife, Branch/PR-Kopplung, Approval-Punkte | Execution-Model-Kapitel |
| `06-adapter-und-modellschicht.md` | Port `ExecutionAdapter`, 10 Adapter, Abo-vs-API-Key-Auth, Capability-Routing, Sandbox-Modell, Secrets, Kostenmodell | Vendor-Neutralität, Kostenkapitel |
| `07-review-qualitygate.md` | Read-only-Review-Schicht, 6 Reviewer, Gate-Policies, Halluzinationserkennung | Guardrails-Kapitel |
| `08-governance-compliance.md` | Mandantenisolation, RBAC, Policy-as-Code, Compliance-Profile, signierte Audit-Hashkette, Warum-Trace, Audit-Export, SBOM | Regulatorik-Kapitel |
| `09-entwicklerhandbuch.md` | Setup, Build, Test, Coverage-Gate, Konventionen, Erweiterungsrezepte, Fallstricke, CI-Pipeline | Anhang / Praxisteil |
| `10-betrieb-deployment.md` | Profile, Compose-Stack, Env-Variablen, Demo-Betrieb, Lizenzstack | Deployment-Kapitel |
| `11-mapping-whitepaper-v13.md` | Kapitel-für-Kapitel-Abgleich v1.3 ↔ Implementierung, inkl. der Stellen, wo die Praxis vom Konzept abweicht | **Zentrales Dokument für die Kapitelplanung** |
| `12-kennzahlen-historie.md` | Versionshistorie 0.1.0–0.19.0, Metriken, Migrationsverlauf, offene Punkte | Evidenzteil, Anhang |

---

## Empfohlene Lesereihenfolge für die Kapitelarbeit

1. `11-mapping-whitepaper-v13.md` — zeigt, welche v1.3-Kapitel durch die
   Implementierung belegt, ergänzt oder korrigiert werden.
2. `01-systemueberblick.md` — der Rahmen.
3. `03-systemdiagramme.md` — die Abbildungen früh festlegen; alles Weitere
   hängt sich daran auf.
4. Die Fachkapitel nach Bedarf.

## Hinweise zur Weiterverwendung

- **Diagramme.** Alle Diagramme liegen als Mermaid-Quelltext vor, mit
  vorgeschlagener Bildunterschrift und Anschluss an die Abbildungsnummerierung
  von v1.3 (dort endet sie bei Abbildung 20). Für LaTeX lassen sie sich per
  `mmdc` nach PDF/SVG rendern oder als Vorlage für TikZ nutzen.
- **Belegbarkeit.** Wo eine Aussage im Code verankert ist, steht die Klasse
  bzw. Datei dabei — das erlaubt Fußnoten mit konkreten Fundstellen statt
  pauschaler Behauptungen.
- **Ehrlichkeit als Argument.** Das Quellen-Set weist offene Schulden,
  bewusste Nicht-Ziele und nicht end-to-end verifizierte Teile explizit aus
  (jeweils als *Einschränkung* markiert). Für ein Enterprise-Publikum ist das
  glaubwürdiger als eine lückenlose Erfolgsgeschichte — und es ist genau die
  Haltung, die das System selbst mit dem Architektur-Ratchet einnimmt.
