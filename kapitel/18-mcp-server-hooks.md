# 18 MCP-Server & Hooks

Das Model Context Protocol (MCP) war bei Erscheinen der v1.3 ein
Anthropic-Protokoll zur Werkzeuganbindung. Diese Einordnung ist überholt:
MCP — im November 2024 von Anthropic vorgestellt [@mcpintro] — wurde im
Dezember 2025 an die Agentic AI Foundation unter dem Dach der Linux
Foundation übergeben [@mcpaaif] und wird dort herstellerneutral
weiterentwickelt [@mcp]; die Foundation wurde von Anthropic, Block und
OpenAI mitgegründet und wird unter anderem von Google, Microsoft und AWS
getragen (Stand August 2026) [@lfaaif].
Wer heute Werkzeuganbindung für Agenten baut, baut sie gegen einen
Industriestandard, nicht gegen ein Vendor-Protokoll — dieselbe Entwicklung,
die `AGENTS.md` für die deklarative Konfiguration genommen hat (Kapitel 4).

## MCP-Server Konfiguration

Projektweite MCP-Server werden bei Claude Code in einer `.mcp.json` im
Repository-Root konfiguriert (Stand August 2026 [@claudecodedocs]; v1.3
nannte hier noch `.claude/settings.json` — dort liegen heute Hooks und
Berechtigungen). Servernamen und -pakete im Beispiel sind teils fiktiv;
der frühere Referenzserver `@modelcontextprotocol/server-postgres` ist seit Juli 2025 archiviert und ungepflegt (dokumentierte SQL-Injection-Schwachstelle) — für den produktiven Einsatz ist ein gepflegter Server zu wählen; das Beispiel steht hier nur für die Struktur:

```json
// .mcp.json (Repository-Root)
{
    "mcpServers": {
        "postgres-server": {
            "command": "npx", "args": ["-y",
                    "@modelcontextprotocol/server-postgres"],
            "env": { "DATABASE_URL": "${DATABASE_URL}" }
        },
        "jira-server": {
            "command": "npx", "args": ["-y", "firmeninternes-jira-mcp-paket"],
            "env": {
                "JIRA_URL": "https://firma.example",
                "JIRA_TOKEN": "${JIRA_API_TOKEN}"
            }
        }
    }
}
```

| Hook-Event | Auslöser | Anwendungsfall |
| --- | --- | --- |
| PreToolUse | Vor jeder Werkzeugausführung | Zugriffe blockieren, Pfade validieren |
| PostToolUse | Nach Werkzeugabschluss | Linting, Security-Scan, Domain-Compliance |
| Notification | Agent benötigt Aufmerksamkeit | Slack/Teams-Alerts, Eskalation |
| Stop | Hauptagent beendet seine Antwort | Abschlussprüfungen, Weiterarbeit erzwingen |
| SessionEnd | Sitzung endet | Cleanup, Report-Generierung, Metriken |

## Domain-Compliance Hook

```java
// === PostToolUse Hook: Bounded Context Check ===
public class DomainComplianceHook {
    private final Map<String, Set<String>> contextBoundaries;

    public record ComplianceResult(boolean compliant, List<Violation> violations) {
        public record Violation(String sourceCtx, String targetCtx,
                String importLine) {}
    }

    public ComplianceResult check(Path changedFile) {
        List<ComplianceResult.Violation> violations = new ArrayList<>();
        String fileCtx = resolveContext(changedFile);
        Set<String> allowed = contextBoundaries.getOrDefault(fileCtx, Set.of());

        Files.lines(changedFile).filter(l -> l.startsWith("import "))
                .forEach(imp -> {
            String importedCtx = resolveContextFromImport(imp);
            if (importedCtx != null && !importedCtx.equals(fileCtx)
                    && !allowed.contains(importedCtx))
                violations.add(new ComplianceResult.Violation(fileCtx, importedCtx,
                        imp));
        });
        return new ComplianceResult(violations.isEmpty(), violations);
    }
}
```

> **Praxis-Check SoftwareFabrik (bewusst offen):** MCP ist dort nicht
> umgesetzt. Das funktionale Äquivalent ist die versionierte,
> mandantengescopte Skill-/Plugin-Bibliothek plus die Materialisierung von
> Agenten-Definitionen und Skills je Run in den Workspace — mit dem
> Governance-Vorteil, dass nachweisbar bleibt, welche Erweiterung in welcher
> Version im Kontext des Agenten war (19.6).
