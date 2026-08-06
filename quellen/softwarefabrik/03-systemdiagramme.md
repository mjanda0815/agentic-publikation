# 3. Systemdiagramme

Neun Diagramme als Mermaid-Quelltext. Die Nummerierung schließt an das
Abbildungsverzeichnis von v1.3 an (dort endet es bei Abbildung 20), damit die
Vorschläge direkt übernommen werden können.

Rendern für LaTeX z. B. mit
`mmdc -i diagramm.mmd -o abbildungen/abb21.pdf -b transparent`.

---

## Abbildung 21 — Systemkontext

*Bildunterschrift:* Systemkontext der Agentic Software Factory: eine Control
Plane zwischen Mensch, Coding-Agenten und Zielrepository.

```mermaid
flowchart TB
    subgraph Menschen
        ARCH["Architekt / Lead Developer<br/>spezifiziert, gibt frei"]
        AUD["Auditor / Compliance<br/>liest Nachweise"]
        ADM["Administrator<br/>Mandanten, Rollen, Policies"]
    end

    FAB["<b>Agentic Software Factory</b><br/>Control Plane<br/>Spring Boot 4 · Java 25"]

    subgraph "Coding-Agenten (Subprozesse)"
        CLI["Vendor-CLIs<br/>Claude Code · Codex · Gemini<br/>Aider · Kimi · lokales LLM"]
        GW["Cloud-Gateways<br/>Bedrock · Vertex AI · Azure OpenAI"]
    end

    subgraph "Externe Systeme"
        GIT["Git-Remote / GitHub<br/>Push · Pull Request · CI-Status"]
        SEC["Scanner<br/>Trivy · OWASP DC"]
        LIC["Lizenz-Stack<br/>Keycloak + License-Service"]
    end

    DB[("PostgreSQL 18<br/>Runs · Artefakte · Audit-Kette")]

    ARCH --> FAB
    ADM --> FAB
    AUD --> FAB
    FAB --> CLI
    FAB --> GW
    FAB <--> GIT
    FAB --> SEC
    FAB <--> LIC
    FAB <--> DB
```

---

## Abbildung 22 — Bausteinsicht (Container/Schichten)

*Bildunterschrift:* Bausteinsicht: modularer Monolith mit Ports-and-Adapters
pro Slice; externe Werkzeuge ausschließlich hinter Ports.

```mermaid
flowchart TB
    B["Browser<br/>Thymeleaf · HTMX · SSE"]

    subgraph APP["Spring-Boot-Prozess"]
        direction TB
        W["<b>web</b><br/>Controller · View-DTOs · SSE-Endpunkte"]
        A["<b>application</b><br/>Use Cases · Transaktionen · Audit"]
        D["<b>domain</b><br/>Aggregate · Invarianten · Repository-Ports"]
        I["<b>infrastructure</b><br/>JPA · Vendor-Adapter · Scheduled Jobs"]
        W --> A --> D
        I -.implementiert.-> D
        A --> I
    end

    DB[("PostgreSQL 18")]
    EXT["Externe Prozesse<br/>Coding-CLI · git · mvn · trivy"]

    B <--> W
    I --> DB
    I --> EXT
```

> Regel im Bild: Pfeile zeigen ausschließlich nach innen bzw. auf Ports.
> Die Rückrichtung (`domain → application/web`) ist per ArchUnit ausgeschlossen.

---

## Abbildung 23 — Slice-Landkarte

*Bildunterschrift:* Fachliche Slices der Fabrik, gruppiert nach Aufgabe.
Blatt-Slices (`provenance`, `export`, `guardrails`) konsumieren nur.

```mermaid
flowchart LR
    subgraph SPEC["Spezifikation"]
        WIZ[wizard]
        PD[projectdefinition]
        PR[prompt]
        AG[agent]
        TE[team]
    end

    subgraph EXEC["Ausführung"]
        RUN[run]
        EX[execution]
        CON[conductor]
        GT[git]
        VAL[validation]
        SK[skills]
        SD[sdlc]
    end

    subgraph QUAL["Bewertung"]
        REV[review]
        QG[qualitygate]
    end

    subgraph GOV["Governance"]
        POL[policy]
        AUD[audit]
        MAN[mandant]
        SECU[security]
        SET[settings]
        SECR[secrets]
        LIC[license]
    end

    subgraph LEAF["Blatt-Slices"]
        PROV[provenance]
        EXP[export]
        GR[guardrails]
        OBS[observability]
    end

    SPEC --> RUN
    RUN --> EX
    RUN --> CON
    RUN --> GT
    RUN --> VAL
    RUN --> QUAL
    GOV --> RUN
    RUN -.Ereignisse.-> AUD
    AUD --> PROV
    AUD --> EXP
```

---

## Abbildung 24 — Laufzeitablauf eines Runs

*Bildunterschrift:* Laufzeitablauf eines Build-Runs von der Anlage bis zum
Merge, inklusive Korrekturschleife und Approval-Punkten.

```mermaid
sequenceDiagram
    autonumber
    actor U as Nutzer
    participant O as RunOrchestrationService
    participant P as PolicyAsCode / Modell-Policy
    participant WS as WorkspaceService + Git
    participant AD as ExecutionAdapter (Sandbox)
    participant QG as QualityGate (Reviewer)
    participant AU as Audit-Hashkette

    U->>O: Run anlegen (Projekt, Team, Ziel, Adapter)
    O->>P: Adapter/Modell gegen aktive Policy prüfen
    P-->>O: erlaubt / RUN_POLICY_DENIED
    O->>AU: RUN_POLICY_ANGEWENDET (Policy-Version)
    O->>WS: Workspace, Artefakte, MEMORY.md, Guardrails schreiben
    WS->>WS: Base mit Remote synchronisieren, Run-Branch abzweigen
    O->>U: Freigabe vor Execution? (falls Policy es verlangt)
    U-->>O: freigegeben
    O->>AD: Prompt ausführen (Stream: Logs, Tokens, Phasen)
    AD-->>O: Diff + Exitcode
    O->>QG: Reviewer parallel auf den Diff
    QG-->>O: PASS / WARN / FAIL + Findings
    alt Gate FAIL oder Build FAIL
        O->>AD: Korrekturlauf mit Feedback (max. 2 Versuche)
    else PASS
        O->>WS: Branch pushen bzw. lokal mergen
        opt PR-Rückkopplung aktiv
            WS-->>O: warten auf grüne CI + Merge
        end
        O->>AU: Run abgeschlossen, Backlog-Item DONE
    end
```

---

## Abbildung 25 — Zustandsautomat des Runs

*Bildunterschrift:* Zustandsmodell eines Runs. Alle Übergänge sind zentral
in `RunStatusTransitions` hinterlegt; unerlaubte Übergänge werfen.

```mermaid
stateDiagram-v2
    [*] --> DRAFT
    DRAFT --> READY
    READY --> PREPARING
    PREPARING --> RUNNING
    RUNNING --> WAITING_FOR_APPROVAL: Freigabe vor Execution
    WAITING_FOR_APPROVAL --> RUNNING: freigegeben
    RUNNING --> PAUSED
    PAUSED --> RUNNING
    RUNNING --> VALIDATING
    VALIDATING --> NEEDS_CORRECTION: Gate/Build FAIL
    NEEDS_CORRECTION --> RUNNING: Korrekturversuch (max. 2)
    VALIDATING --> WAITING_FOR_APPROVAL: Freigabe vor Merge
    VALIDATING --> WAITING_FOR_PR: Push + Pull Request
    WAITING_FOR_PR --> COMPLETED: CI grün + gemerged
    WAITING_FOR_PR --> NEEDS_CORRECTION: CI rot
    VALIDATING --> COMPLETED
    RUNNING --> FAILED
    RUNNING --> TIMEOUT
    RUNNING --> CANCELLED
    COMPLETED --> [*]
    FAILED --> [*]
    TIMEOUT --> [*]
    CANCELLED --> [*]
```

---

## Abbildung 26 — Datenmodell (Ausschnitt)

*Bildunterschrift:* Kernaggregate des Datenmodells. Vollständig: 39 Tabellen,
37 Flyway-Migrationen.

```mermaid
erDiagram
    MANDANT ||--o{ APP_USER : "hat"
    MANDANT ||--o{ PROJECT_DEFINITION : "besitzt"
    MANDANT ||--o| MANDANT_BUDGET : "begrenzt durch"

    PROJECT_DEFINITION ||--o{ PROMPT_ARTIFACT : "spezifiziert durch"
    PROJECT_DEFINITION ||--o| PROJECT_MEMORY : "kuratiert"
    PROJECT_DEFINITION ||--o{ RUN : "führt aus"
    PROJECT_DEFINITION ||--o{ PLAN_ITEM : "Backlog"
    PROJECT_DEFINITION ||--o{ PROJECT_MILESTONE : "Meilensteine"
    PROJECT_DEFINITION ||--o{ ROUTINE : "geplante Läufe"

    PLAN_ITEM ||--o{ PLAN_ITEM_DEPENDENCY : "hängt ab von"

    RUN ||--o{ RUN_PHASE : "besteht aus"
    RUN ||--o{ EXECUTION_LOG : "protokolliert"
    RUN ||--o| RUN_METRICS : "misst"
    RUN ||--o{ GIT_CHECKPOINT : "sichert"
    RUN ||--o{ BUILD_RESULT : "validiert durch"
    RUN ||--o{ APPROVAL_DECISION : "freigegeben durch"
    RUN ||--o| SBOM_ARTIFACT : "belegt durch"

    POLICY_DOCUMENT ||--o{ RUN : "regelt"
    AUDIT_EVENT ||--o| AUDIT_CHAIN_CHECKPOINT : "verankert"
    SKILL_CATALOG_ENTRY ||--o{ SKILL_VERSION : "versioniert"
```

---

## Abbildung 27 — Adapter- und Modellschicht

*Bildunterschrift:* Vendor-Neutralität durch einen Port: Application- und
Web-Schicht kennen ausschließlich `ExecutionAdapter` (ArchUnit-erzwungen).

```mermaid
flowchart TB
    APPL["application / web<br/><i>kennt nur den Port</i>"]
    PORT["<b>ExecutionAdapter</b> (Port)<br/>name() · execute(request, eventHandler)"]
    REG["ExecutionAdapterRegistry<br/>Auflösung: Run &gt; Projekt &gt; User &gt; Global &gt; YAML"]
    ROUT["ModelRoutingService<br/>Capability-Profil je Rolle (PLAN/BUILD)"]
    SB["ExecutionSandboxFactory<br/>lokal | Container (--network=none, read-only)"]

    APPL --> REG --> PORT
    ROUT --> REG
    PORT --> SB

    subgraph CLIA["CLI-Adapter"]
        M[mock]
        C[claude]
        X[codex]
        G[gemini]
        AI[aider]
        K[kimi]
        L[local-llm]
    end
    subgraph GWA["Gateway-Adapter"]
        BR[bedrock]
        VE[vertex]
        AZ[azure-openai]
    end

    SB --> CLIA
    SB --> GWA

    SEC["SecretsResolver<br/>AES-GCM · Abo-Modus strippt API-Key"]
    SEC -.Prozessumgebung.-> SB
```

---

## Abbildung 28 — Governance- und Nachweiskette

*Bildunterschrift:* Von der Policy bis zum Auditbericht: jede Durchsetzung
erzeugt ein signiertes Kettenglied.

```mermaid
flowchart LR
    CP["Compliance-Profil<br/>Baseline · EU AI Act<br/>BAIT/MaRisk/DORA · BSI/VS-NfD"]
    PD["PolicyDocument<br/>versioniert · Ed25519-signiert<br/>genau eine aktive Version"]
    ENF["Enforcement im Orchestrator<br/>Adapter · Modell · Attestierungspflicht<br/>Segregation of Duties"]
    EV["AuditEvent<br/>seq · prev_hash · entry_hash<br/>signature · key_id"]
    VER["Kettenprüfung<br/>HASH_MISMATCH · CHAIN_BREAK<br/>BAD_SIGNATURE"]
    TR["Warum-Trace je Run<br/>Modell · Policy · Freigaben<br/>Gate-Ergebnis · Kosten"]
    EXP["Audit-Export-Bundle<br/>JSON + HTML, inkl. Public Key"]

    CP --> PD --> ENF --> EV --> VER
    EV --> TR --> EXP
    VER --> EXP
    SBOM["SBOM je Build<br/>+ Ed25519-Signatur über den Digest"] --> EXP
```

---

## Abbildung 29 — Deployment

*Bildunterschrift:* Deployment-Sicht: ein Anwendungscontainer, eine Datenbank,
optional getrennter Lizenz-Stack. Air-Gap-fähig.

```mermaid
flowchart TB
    subgraph HOST["Kundenhost (Docker Compose / systemd)"]
        APP["softwarefabrik-app<br/>Spring Boot · Port 8080"]
        PG[("softwarefabrik-postgres<br/>PostgreSQL 18<br/>gebunden an 127.0.0.1")]
        WSV[/"Workspaces<br/>ein Git-Repo je Projekt"/]
        APP --- PG
        APP --- WSV
    end

    subgraph SBX["Ephemere Agent-Sandbox (optional)"]
        CT["Container je Run<br/>--cpus 2 --memory 4g<br/>--pids-limit 512 --read-only<br/>--network=none"]
    end

    subgraph LICS["Lizenz-Stack (optional, extern)"]
        KC["Keycloak<br/>OIDC · Device-Flow"]
        LS["License-Service<br/>eigene PostgreSQL"]
    end

    REM["Git-Remote / GitHub<br/>nur Hosts der Allowlist"]

    APP --> CT
    APP -. "Lease-JWT, 7 Tage,<br/>offline verifiziert" .-> LS
    LS --- KC
    APP --> REM
```

---

## Optional: Abbildung 30 — Korrekturschleife im Detail

*Bildunterschrift:* Die Korrekturschleife als Regelkreis — Befunde werden zu
Eingaben des nächsten Laufs.

```mermaid
flowchart LR
    EX["Execution<br/>Agent erzeugt Diff"] --> BUILD["Build-Gate<br/>mvn verify / npm run build"]
    BUILD --> GATE["Quality Gate<br/>6 Reviewer, parallel"]
    GATE -->|PASS| MERGE["Branch-Abschluss<br/>Merge oder Pull Request"]
    GATE -->|"FAIL / Build rot /<br/>Merge-Konflikt / CI rot"| FB["Feedback-Text<br/>Findings, Konfliktdateien, Logs"]
    FB --> COUNT{"Versuch &lt; 2 ?"}
    COUNT -->|ja| EX
    COUNT -->|nein| FAILED["Run FAILED<br/>Befunde bleiben nachvollziehbar"]
```
