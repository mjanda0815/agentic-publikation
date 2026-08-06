# 8 Memory Architecture

![Wissens- und Speicherarchitektur eines Multi-Agent-Entwicklungssystems](abbildungen/out/abb08.pdf){width=100%}

Agentische Entwicklungssysteme benötigen eine gemeinsame Wissensbasis, damit spezialisierte Agenten Informationen austauschen können, ohne ihre Kontextisolation aufzugeben.

Der Shared Knowledge Store fungiert als zentrale Wissensquelle für Architekturentscheidungen, Anforderungen, Implementierungspläne und weitere Artefakte. Agenten lesen daraus Kontextinformationen und schreiben ihre Ergebnisse zurück, sodass nachfolgende Agenten darauf aufbauen können.

Ergänzend kann eine Vektor-basierte Memory-Komponente eingesetzt werden, um semantische Suche und kontextuelle Retrieval-Mechanismen zu ermöglichen. Dadurch können Agenten relevante Dokumente, Architekturentscheidungen oder Codefragmente auf Basis semantischer Ähnlichkeit finden und in ihre Entscheidungsprozesse einbeziehen.

> **Hinweis:** Ohne geteilten Zustand läuft die Kommunikation nur über den Orchestrator. Das ist sauber, aber begrenzt. Die Memory Architecture löst dieses Problem mit einem mehrschichtigen Modell.

Die Memory Architecture des Agentensystems definiert, wie Wissen gespeichert, geteilt und über den Lebenszyklus eines Workflows hinweg erhalten bleibt. Das Modell unterscheidet fünf Speicherschichten mit unterschiedlicher Lebensdauer, Sichtbarkeit und Zugriffsgeschwindigkeit:

![Memory Architecture — Fünf-Schichten-Modell von ephemer bis persistent](abbildungen/out/abb09.pdf){width=85%}

| Schicht | Lebensdauer | Sichtbarkeit | Implementierung |
| --- | --- | --- | --- |
| Short-Term Context | Ein Turn | Nur der aktuelle Agent | LLM Context Window (modellabhängig 200K–1M Tokens, Stand 08/2026) |
| Session Memory | Ein Task | Agent während gesamter Sitzung | In-Memory HashMap per Agent-ID |
| Shared Knowledge Store | Workflow / Sprint | Alle Agenten des Workflows | JSON in docs/knowledge/ (dateisystembasiert) |
| Vector Memory | Projektlaufzeit | Alle Agenten | Embeddings in Vector-DB (optional, z. B. Weaviate) |
| Decision Log | Permanent | Team + Audit | Append-only Markdown in docs/decisions/ |

## 8.1 Short-Term Context & Session Memory

Der Short-Term Context ist das LLM Context Window — bei den aktuellen
Claude-Modellen 1 Mio. Tokens, bei Haiku 4.5 200.000 Tokens (Stand
6. August 2026 [@anthropicmodels]; v1.3 nannte hier noch 200K als Maximum —
die Verfünffachung der Tokenzahl binnen weniger Monate (gemessen an der
Textmenge wegen des neuen Tokenizers knapp das Vierfache) ist selbst ein
Argument dafür, Kontextgrößen nie fest in Architekturentscheidungen
einzubauen). Alles, was
der Agent in einem Turn "sieht", existiert nur hier. Session Memory
erweitert dies über mehrere Turns innerhalb eines Tasks: Der Agent kann sich
an seine eigenen früheren Tool-Aufrufe und deren Ergebnisse erinnern, aber
nicht an Informationen anderer Agenten.

## 8.2 Shared Knowledge Store

Der Shared Knowledge Store ist die zentrale Wissensbasis für die agentenübergreifende Zusammenarbeit. Er besteht aus fünf Komponenten:

![Shared Knowledge Store — zentrale Wissensbasis für Agenten](abbildungen/out/abb10.pdf){width=100%}

| Komponente | Beschreibung | Zugriffsmuster |
| --- | --- | --- |
| Knowledge Graph | Entitäten und Beziehungen im Code | Write: architecture-agent \| Read: alle |
| Context Cache | Kurzfristiger Sitzungs-Kontext | Write/Read: aktiver Agent |
| Decision Log | Architekturentscheidungen (ADRs) | Write: architecture-agent \| Read: alle \| Append-only |
| Dependency Map | Service-Abhängigkeiten | Write: architecture-agent \| Read: dev-agent, deploy-agent |
| Findings Store | Review- und Test-Findings | Write: review-agent, test-agent \| Read: dev-agent, orchestrator |

### Java-Beispiel: Shared Knowledge Store Client

```java
// === Shared Knowledge Store Client ===
@Component @Slf4j
public class KnowledgeStoreClient {

    private final ObjectMapper objectMapper;
    private final Path knowledgeBase;

    public KnowledgeStoreClient(
            @Value("${knowledge.base-path:docs/knowledge}") String basePath) {
        this.objectMapper = new ObjectMapper().registerModule(new JavaTimeModule());
        this.knowledgeBase = Path.of(basePath);
    }

    public <T> void store(String domain, String key, T value) {
        try {
            Path filePath = knowledgeBase.resolve(domain).resolve(key + ".json");
            Files.createDirectories(filePath.getParent());
            KnowledgeEntry<T> entry = new KnowledgeEntry<>(
                    key, value, Instant.now(), Thread.currentThread().getName());
            objectMapper.writerWithDefaultPrettyPrinter()
                    .writeValue(filePath.toFile(), entry);
            log.info("Knowledge stored: {}/{}", domain, key);
        } catch (IOException e) {
            throw new KnowledgeStoreException("Failed to store: " + domain + "/" + key, e);
        }
    }

    public <T> Optional<KnowledgeEntry<T>> retrieve(
            String domain, String key, Class<T> type) {
        Path filePath = knowledgeBase.resolve(domain).resolve(key + ".json");
        if (!Files.exists(filePath)) return Optional.empty();
        try {
            JavaType entryType = objectMapper.getTypeFactory()
                    .constructParametricType(KnowledgeEntry.class, type);
            return Optional.of(objectMapper.readValue(filePath.toFile(), entryType));
        } catch (IOException e) {
            log.warn("Failed to read: {}/{}", domain, key, e);
            return Optional.empty();
        }
    }

    public record KnowledgeEntry<T>(String key, T value, Instant storedAt, String storedBy) {}
}
```

## 8.3 Vector Memory (optional)

Für große Codebasen mit Millionen Zeilen Code ist ein dateibasierter Shared Knowledge Store zu langsam für semantische Suchen. Vector Memory ergänzt den Store um eine Embedding-basierte Suche, die ähnliche Code-Patterns, ähnliche Architekturentscheidungen oder relevante Findings finden kann, ohne den exakten Schlüssel zu kennen.

Die Implementierung nutzt eine lokale Vector-Datenbank (z. B. Weaviate, ChromaDB) mit einem deutschen Embedding-Modell (z. B. `deepset-mxbai-embed-de-large-v1`, ein offenes deutsch-englisches Modell von deepset und Mixedbread [@mxbaide]). Dies ist insbesondere für Behörden-Projekte relevant, bei denen Cloud-basierte Embedding-Services aus Datenschutzgründen nicht in Frage kommen.


> **Praxis-Check SoftwareFabrik (abweichend):** Der geteilte Wissensstand
> ist umgesetzt — als versionierte Dateien im Repository plus kuratiertes
> Projektgedächtnis. Auf den optionalen Vektorspeicher wurde bewusst
> verzichtet: Was der Agent liest, muss ein Mensch reviewen und ein Auditor
> zitieren können (19.6).
