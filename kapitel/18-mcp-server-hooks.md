# 18 MCP-Server & Hooks

## MCP-Server Konfiguration

```json
// .claude/settings.json
{
    "mcpServers": {
        "jira-server": {
            "command": "npx", "args": ["-y", "@anthropic/mcp-jira"],
            "env": { "JIRA_URL": "https://firma.atlassian.net", "JIRA_TOKEN": "${JIRA_API_TOKEN}" }
        },
        "postgres-server": {
            "command": "npx", "args": ["-y", "@anthropic/mcp-postgres"],
            "env": { "DATABASE_URL": "${DATABASE_URL}" }
        }
    }
}
```

| Hook-Event | Auslöser | Anwendungsfall |
| --- | --- | --- |
| PreToolUse | Vor jeder Werkzeugausführung | Zugriffe blockieren, Pfade validieren |
| PostToolUse | Nach Werkzeugabschluss | Linting, Security-Scan, Domain-Compliance |
| Notification | Agent benötigt Aufmerksamkeit | Slack/Teams-Alerts, Eskalation |
| Stop | Sitzung endet | Cleanup, Report-Generierung, Metriken |

## Domain-Compliance Hook

```java
// === PostToolUse Hook: Bounded Context Check ===
public class DomainComplianceHook {
    private final Map<String, Set<String>> contextBoundaries;

    public record ComplianceResult(boolean compliant, List<Violation> violations) {
        public record Violation(String sourceCtx, String targetCtx, String importLine) {}
    }

    public ComplianceResult check(Path changedFile) {
        List<ComplianceResult.Violation> violations = new ArrayList<>();
        String fileCtx = resolveContext(changedFile);
        Set<String> allowed = contextBoundaries.getOrDefault(fileCtx, Set.of());

        Files.lines(changedFile).filter(l -> l.startsWith("import ")).forEach(imp -> {
            String importedCtx = resolveContextFromImport(imp);
            if (importedCtx != null && !importedCtx.equals(fileCtx) && !allowed.contains(importedCtx))
                violations.add(new ComplianceResult.Violation(fileCtx, importedCtx, imp));
        });
        return new ComplianceResult(violations.isEmpty(), violations);
    }
}
```
