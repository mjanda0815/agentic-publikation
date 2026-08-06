# 2 Architektonische Prinzipien

Jedes Enterprise-Architekturdokument basiert auf einem Set formaler Prinzipien, die als Leitplanken für alle Designentscheidungen dienen. Die folgenden sechs Prinzipien bilden das Fundament des Claude Code Agentensystems und werden in den nachfolgenden Kapiteln durchgehend referenziert.

| Prinzip | Kurzformel | Beschreibung |
| --- | --- | --- |
| AP-1: Agent Specialization | Ein Agent, eine Rolle | Jeder Agent hat genau eine klar definierte Verantwortlichkeit. Kein Agent vereint Entwicklung und Review. Spezialisierung führt zu höherer Qualität und ermöglicht gezielte Modellauswahl (opus für Architektur, haiku für Formatierung). |
| AP-2: Deterministic Execution | Reproduzierbar und nachvollziehbar | Trotz nicht-deterministischer LLM-Outputs sorgen Task-Graphen, Stop-Conditions und Execution Budgets für vorhersagbare Gesamtabläufe. Jeder Lauf ist über Audit-Logs vollständig nachvollziehbar. |
| AP-3: Governance by Design | Compliance eingebaut, nicht nachgerüstet | Sicherheit, Domain-Compliance und Qualitätssicherung sind keine optionalen Add-ons, sondern integraler Bestandteil jeder Pipeline-Stufe – durchgesetzt durch Hooks und Guardrails. |
| AP-4: Isolation by Workspace | Kein Agent verändert unkontrolliert | Jeder Agent arbeitet in einem isolierten Workspace (Git Worktree). Änderungen werden erst nach erfolgreicher Validierung in den Haupt-Branch überführt. Parallele Agenten können sich nicht gegenseitig beeinflussen. |
| AP-5: Policy-Driven Development | Regeln statt Hoffnung | Projektstandards, DDD-Regeln, Coding Conventions und Architekturvorgaben werden deklarativ in CLAUDE.md definiert – nicht als Prosa-Dokumentation, sondern als maschinenlesbare Policies. |
| AP-6: Human-in-the-Loop | KI assistiert, Mensch entscheidet | Kritische Entscheidungen (Architektur-ADRs, Security-Findings, Deployment-Freigaben) erfordern immer menschliche Bestätigung. KI-Agenten sind Werkzeuge, keine autonomen Entscheider. |

Diese Prinzipien stehen nicht isoliert, sondern bedingen sich gegenseitig: Agent Specialization (AP-1) ermöglicht erst Isolation by Workspace (AP-4), weil spezialisierte Agenten klare Workspace-Grenzen haben. Governance by Design (AP-3) setzt Policy-Driven Development (AP-5) voraus, weil Hooks nur durchsetzen können, was als Policy definiert ist. Und Human-in-the-Loop (AP-6) ist das Sicherheitsnetz für alle Fälle, in denen Deterministic Execution (AP-2) an seine Grenzen stößt.

## Zuordnung zu Architekturkonzepten

| Prinzip | Kapitelreferenzen | Durchsetzung |
| --- | --- | --- |
| AP-1: Agent Specialization | Kap. 5 (Agententypen), Kap. 12 (Berechtigungsmodell) | CLAUDE.md Agentendefinitionen + Tool-Restriktionen |
| AP-2: Deterministic Execution | Kap. 7 (Execution Model), Kap. 18 (ADR-4) | Task-Graph, max_turns, Execution Budgets |
| AP-3: Governance by Design | Kap. 13 (Guardrails), Kap. 17 (Hooks) | PreToolUse/PostToolUse Hooks, Validierungs-Pipeline |
| AP-4: Isolation by Workspace | Kap. 15 (Workflows), Kap. 18 (ADR-2) | Git Worktrees, isolation="worktree" Parameter |
| AP-5: Policy-Driven Development | Kap. 4 (CLAUDE.md), Kap. 12 (DDD) | CLAUDE.md als Single Source of Truth |
| AP-6: Human-in-the-Loop | Kap. 9 (Failure Handling), Kap. 14 (Security) | Confidence Score Eskalation, Review Gates |

<!-- TODO(verify): Die Kapitelreferenzen in dieser Tabelle (z. B. "Kap. 12 (Berechtigungsmodell)", "Kap. 13 (Guardrails)", "Kap. 17 (Hooks)", "Kap. 18 (ADR-2/ADR-4)") stimmen im Original (S. 10) nicht mit der tatsächlichen Kapitelnummerierung des Inhaltsverzeichnisses überein (Berechtigungsmodell steht in Kap. 14 Security Model, Guardrails/AI Risk Framework in Kap. 12, Hooks in Kap. 18 MCP-Server & Hooks, ADR-2/ADR-4 in Kap. 19). Wörtlich aus dem Original übernommen, nicht korrigiert – siehe TODO.md. -->
