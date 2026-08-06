# 14 Security Model

> **Hinweis:** Guardrails schützen vor fehlerhaftem Output. Das Security Model schützt das Agentensystem selbst – vor Prompt Injection, Tool Escalation, Secret Leakage und Supply-Chain-Angriffen.

Ein KI-Agentensystem mit Schreibzugriff auf die Codebasis, Bash-Zugriff und Netzwerkverbindungen ist eine erhebliche Angriffsfläche. Das Security Model adressiert fünf zentrale Bedrohungsvektoren:

| Bedrohung | Risiko | Gegenmaßnahme |
| --- | --- | --- |
| Prompt Injection | Manipulation des Agentenverhaltens durch eingeschleuste Anweisungen in Code-Kommentaren, Dateien oder API-Responses | Input Sanitization, System-Prompt Hardening, Ergebnis-Validierung durch separaten Review-Agent (AP-1) |
| Tool Escalation | Agent versucht, nicht autorisierte Tools zu nutzen oder Berechtigungsgrenzen zu überschreiten | Striktes Tool-Whitelisting per Agent in CLAUDE.md, PreToolUse-Hook blockiert nicht autorisierte Aufrufe (AP-5) |
| Secret Leakage | Credentials, API-Keys oder sensible Daten werden in generiertem Code, Logs oder Shared Knowledge Store geschrieben | Secret-Scanner im PostToolUse-Hook (Regex + Entropy-Analyse), env-basiertes Secret Management, Audit-Trail |
| Supply Chain | Agent fügt kompromittierte Dependencies hinzu oder nutzt ungeprüfte Libraries | OWASP Dependency Check im Guardrail, Lockfile-Validierung, Allowlist für Dependencies in CLAUDE.md |
| Sandboxing | Unkontrollierter Systemzugriff durch Bash-Tool oder Datei-Operationen | Worktree-Isolation (AP-4), readonly Mounts, Netzwerk-Restriktionen, chroot für Bash-Ausführung |

## Berechtigungsmodell (Least Privilege)

| Agent | Lesen | Schreiben | Ausführen |
| --- | --- | --- | --- |
| architecture-agent | Gesamte Codebasis | Keine | Nur-Lese Bash |
| planning-agent | Gesamte Codebasis | Nur Docs | Keine |
| dev-agent | Gesamte Codebasis | Voll | Build/Lint |
| test-agent | Gesamte Codebasis | Nur Tests | Test-Kommandos |
| review-agent | Gesamte Codebasis | Keine | Nur-Lese Bash |
| deploy-agent | Gesamte Codebasis | Nur IaC | Terraform/K8s |

## Java-Beispiel: Secret-Scanner Hook

```java
// === Secret Scanner (PostToolUse Hook) ===
public class SecretScannerHook {
    private static final List<Pattern> SECRET_PATTERNS = List.of(
        Pattern.compile("(?i)(password|secret|api[_-]?key|token)\\s*[=:]\\s*['\"][^\"]{8,}"),
        Pattern.compile("AKIA[0-9A-Z]{16}"),                  // AWS Access Key
        Pattern.compile("ghp_[0-9a-zA-Z]{36}"),               // GitHub Token
        Pattern.compile("-----BEGIN (RSA |EC )?PRIVATE KEY"), // Private Keys
        Pattern.compile("[0-9a-f]{40}")                        // High-entropy hex (SHA1-like)
    );

    public record ScanResult(boolean clean, List<Finding> findings) {
        public record Finding(String file, int line, String patternName, String masked) {}
    }

    public ScanResult scan(Path changedFile) {
        List<ScanResult.Finding> findings = new ArrayList<>();
        try {
            List<String> lines = Files.readAllLines(changedFile);
            for (int i = 0; i < lines.size(); i++) {
                for (Pattern pat : SECRET_PATTERNS) {
                    if (pat.matcher(lines.get(i)).find()) {
                        findings.add(new ScanResult.Finding(
                                changedFile.toString(), i + 1,
                                pat.pattern().substring(0, 20) + "...",
                                lines.get(i).substring(0, Math.min(40, lines.get(i).length())) + "..."));
                    }
                }
            }
        } catch (IOException e) { throw new HookException("Scan failed", e); }
        return new ScanResult(findings.isEmpty(), findings);
    }
}
```
