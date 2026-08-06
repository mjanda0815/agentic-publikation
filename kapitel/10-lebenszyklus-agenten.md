# 10 Die sieben Lebenszyklus-Agenten

Für jede Phase des Software Development Lifecycle steht ein spezialisierter Agent bereit. Im Folgenden werden alle sieben Agenten mit ihren Agenten-Aufrufen und Java-Enterprise-Codebeispielen vorgestellt.

> **Versionshinweis (v2.0):** Die Java-Codebeispiele dieses Teils stammen
> aus v1.3 und sind gegen Java 21 LTS und Spring Boot 3.x formuliert; sie
> wurden für v2.0 bewusst nicht auf neuere Versionen gehoben und nicht
> erneut dagegen getestet. Für den Sprung auf Spring Boot 4 (GA seit
> November 2025) siehe die dokumentierten Fallstricke des Realsystems in
> Kapitel 19 — das dort beschriebene System läuft auf Java 25 und Spring
> Boot 4.0 (u. a. Wechsel auf Jackson 3 als primären Serialisierer).
> Aufruf-Skizzen (`Task(...)`) sind Pseudocode auf v1.3-Werkzeugstand; das
> Werkzeug heißt heute `Agent` (vgl. 3.5).

## 10.1 Architektur-Agent

Der Architektur-Agent analysiert die bestehende Systemarchitektur, bewertet Design-Patterns, identifiziert Anti-Patterns und erstellt ADRs. Er hat ausschließlich lesenden Zugriff auf die Codebasis (AP-2, AP-4).

```
Task(subagent_type="architecture-agent", model="opus",
    description="Spring Boot Architektur analysieren",
    prompt=""Analysiere die Spring Boot Microservice-Architektur:
    - Controller -> Service -> Repository Trennung
    - Spring Security FilterChain-Konfiguration
    - JPA Entity-Beziehungen und Fetch-Strategien
    - Exception Handling (@ControllerAdvice)
    - Anti-Patterns: N+1 Queries, Zirkuläre Beans
    Output: Architektur-Diagramm + Findings als ADR"")
```

### Erzeugter Code: Schichtentrennung

```java
// === Controller Layer (REST API) ===
@RestController @RequestMapping("/api/v1/payments")
@RequiredArgsConstructor @Validated
public class PaymentController {
    private final PaymentService paymentService;

    @PostMapping @ResponseStatus(HttpStatus.CREATED)
    public ResponseEntity<PaymentResponse> initiatePayment(
            @Valid @RequestBody PaymentRequest request) {
        PaymentResponse response = paymentService.initiatePayment(request);
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}").buildAndExpand(response.paymentId()).toUri();
        return ResponseEntity.created(location).body(response);
    }
}

// === Service Layer ===
@Service @RequiredArgsConstructor @Slf4j
public class PaymentService {
    private final PaymentRepository paymentRepository;
    private final PaymentValidator paymentValidator;
    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public PaymentResponse initiatePayment(PaymentRequest request) {
        paymentValidator.validate(request);
        Payment payment = Payment.create(request.amount(), request.currency(),
                request.recipientIban());
        Payment saved = paymentRepository.save(payment);
        eventPublisher.publishEvent(new PaymentInitiatedEvent(saved.getId(),
                saved.getAmount()));
        return PaymentResponse.from(saved);
    }
}

// === Repository Layer ===
@Repository
public interface PaymentRepository extends JpaRepository<Payment, UUID> {
    @Query("SELECT p FROM Payment p JOIN FETCH p.auditEntries WHERE p.id = :id")
    Optional<Payment> findByIdWithAudit(@Param("id") UUID id);
}
```

### Globales Exception Handling (RFC 9457, vormals RFC 7807)

```java
@RestControllerAdvice @Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(PaymentNotFoundException.class)
    public ProblemDetail handleNotFound(PaymentNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND,
                ex.getMessage());
        problem.setTitle("Zahlung nicht gefunden");
        problem.setType(URI.create("https://api.company.com/errors/not-found"));
        problem.setProperty("paymentId", ex.getPaymentId());
        return problem;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST,
                "Validierungsfehler");
        Map<String, String> errors = ex.getBindingResult().getFieldErrors().stream()
                .collect(Collectors.toMap(FieldError::getField,
                        fe -> fe.getDefaultMessage() != null
                                ? fe.getDefaultMessage() : "ungültig",
                        (a,b)->a));
        problem.setProperty("fieldErrors", errors);
        return problem;
    }
}
```

## 10.2 Planungs-Agent

Der Planungs-Agent erstellt detaillierte Implementierungspläne mit Meilensteinen, Abhängigkeiten und Zeitschätzungen. Er erzeugt typisierte Datenstrukturen für programmatische Fortschrittsverfolgung:

```
Task(subagent_type="planning-agent", description="JWT-Auth planen",
    prompt=""Erstelle Implementierungsplan für JWT-Authentication:
    - Token-Generierung/-Validierung mit JJWT, Refresh Token Rotation
    - RBAC, PostgreSQL User/Role-Tabellen, Spring Security Integration
    Output: docs/implementations/jwt-auth-tracker.md"")
```

```java
// === Implementierungs-Tracker ===
public record ImplementationPlan(
        String featureId, String title, List<Phase> phases, Instant createdAt) {

    public record Phase(int order, String name, Duration estimatedEffort,
                        Set<String> dependencies, List<Task> tasks, PhaseStatus status) {
        public boolean isBlocked() {
            return !dependencies.isEmpty() && status == PhaseStatus.PENDING;
        }
    }
    public record Task(String id, String description, String targetFile,
                       TaskPriority priority, TaskStatus status) {}
    public enum PhaseStatus { PENDING, IN_PROGRESS, COMPLETED, BLOCKED }
    public enum TaskStatus { TODO, IN_PROGRESS, DONE, FAILED }
    public enum TaskPriority { CRITICAL, HIGH, MEDIUM, LOW }

    public double completionPercentage() {
        long total = phases.stream().flatMap(ph -> ph.tasks().stream()).count();
        long done = phases.stream().flatMap(ph -> ph.tasks().stream())
                .filter(t -> t.status() == TaskStatus.DONE).count();
        return total == 0 ? 0 : (double) done / total * 100;
    }
}
```

## 10.3 Requirements-Agent

Der Requirements-Agent erstellt eine Requirements Traceability Matrix (RTM), die jede Anforderung mit Code, Tests und Akzeptanzkriterien verknüpft:

```java
// === Requirements Traceability Matrix ===
public record TraceabilityMatrix(String sprintId, List<TracedRequirement> requirements) {
    public record TracedRequirement(
            String jiraKey, String title, RequirementStatus status,
            List<AcceptanceCriterion> criteria, List<CodeReference> implementations,
            List<CodeReference> tests, Set<String> gaps) {
        public boolean isFullyTraced() {
            return gaps.isEmpty() && !implementations.isEmpty() && !tests.isEmpty();
        }
    }
    public record AcceptanceCriterion(String id, String description, boolean isCovered) {}
    public record CodeReference(String filePath, String className, int lineNumber) {}

    public List<TracedRequirement> untracedRequirements() {
        return requirements.stream().filter(r -> !r.isFullyTraced()).toList();
    }
}
```

## 10.4 Entwicklungs-Agent

Der Entwicklungs-Agent implementiert Features nach den in CLAUDE.md definierten Standards. Das folgende Beispiel zeigt das Strategy Pattern für einen Notification-Service:

```java
// === Strategy Interface (Sealed) ===
public sealed interface NotificationChannel
        permits EmailChannel, SmsChannel, PushChannel {
    CompletableFuture<NotificationResult> send(NotificationRequest request);
    NotificationType getType();
    boolean supports(NotificationRequest request);
}

// === E-Mail Channel ===
@Component @Slf4j
public final class EmailChannel implements NotificationChannel {
    private final JavaMailSender mailSender;
    private final TemplateEngine templateEngine;

    @Override @Async("notificationExecutor")
    @Retryable(retryFor = MailSendException.class, maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2.0))
    public CompletableFuture<NotificationResult> send(NotificationRequest request) {
        log.info("Sending email to {}", request.recipient());
        MimeMessage msg = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(msg, true);
        helper.setTo(request.recipient());
        helper.setSubject(request.subject());
        helper.setText(renderTemplate(request), true);
        mailSender.send(msg);
        return CompletableFuture.completedFuture(
                NotificationResult.success(getType(), request.id()));
    }
    // ...
}

// === Notification Service (Orchestrator) ===
@Service @Slf4j
public class NotificationService {
    private final List<NotificationChannel> channels;
    private final NotificationHistoryRepository historyRepo;

    @Transactional
    public List<NotificationResult> sendNotification(NotificationRequest request) {
        List<NotificationChannel> applicable = channels.stream()
                .filter(ch -> ch.supports(request)).toList();
        if (applicable.isEmpty())
            throw new NoSuitableChannelException("Kein passender Kanal");
        List<CompletableFuture<NotificationResult>> futures =
                applicable.stream().map(ch -> ch.send(request)).toList();
        List<NotificationResult> results = futures.stream()
                .map(CompletableFuture::join).toList();
        results.forEach(r -> historyRepo.save(NotificationHistory.from(request, r)));
        return results;
    }
}
```

## 10.5 Testing-Agent

Der Testing-Agent nutzt JUnit 5, Testcontainers und WireMock für iterative Testsuiten:

```java
// === Unit Test mit Mockito ===
@ExtendWith(MockitoExtension.class)
class NotificationServiceTest {
    @Mock private NotificationHistoryRepository historyRepo;
    @Mock private EmailChannel emailChannel;
    @InjectMocks private NotificationService service;

    @Test @DisplayName("Wählt korrekte Kanäle basierend auf Request")
    void shouldSelectCorrectChannels() {
        var request = new NotificationRequest(null, "test@example.com", "User",
                "Betreff", "Inhalt", Set.of(NotificationType.EMAIL), Map.of());
        when(emailChannel.supports(request)).thenReturn(true);
        when(emailChannel.send(request)).thenReturn(CompletableFuture.completedFuture(
                NotificationResult.success(NotificationType.EMAIL, request.id())));
        var results = service.sendNotification(request);
        assertThat(results).hasSize(1);
        assertThat(results.get(0).isSuccess()).isTrue();
    }
}

// === Integrationstest mit Testcontainers ===
@SpringBootTest @Testcontainers @ActiveProfiles("test")
class NotificationIntegrationTest {
    @Container static PostgreSQLContainer<?> postgres =
            new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void configure(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url", postgres::getJdbcUrl);
        r.add("spring.datasource.username", postgres::getUsername);
        r.add("spring.datasource.password", postgres::getPassword);
    }
}
```

## 10.6 Review-Agent

```
Task(subagent_type="review-agent", model="opus",
    prompt=""Review des Notification-Service:
    1. Thread-Safety in Singleton-Beans
    2. Resource Leaks, JPA N+1 Queries
    3. Security: Input Validation, SQL Injection
    4. Java 21: Records, Sealed Interfaces
    Output: [CRITICAL/WARNING/INFO] Datei:Zeile - Beschreibung"")
```

## 10.7 Deployment-Agent

```yaml
# Kubernetes Deployment
apiVersion: apps/v1
kind: Deployment
metadata: { name: notification-service }
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: notification-service
        image: registry.company.com/notification-service:1.0.0
        resources:
          requests: { memory: "512Mi", cpu: "500m" }
          limits: { memory: "1Gi", cpu: "1000m" }
        readinessProbe:
          httpGet: { path: /actuator/health/readiness, port: 8080 }
        livenessProbe:
          httpGet: { path: /actuator/health/liveness, port: 8080 }
```

> **Praxis-Check SoftwareFabrik (abweichend):** Die sieben Rollen existieren
> dort teils als Agentenrollen im Kontext (Definitionen, Teams), teils als
> Systemfunktionen: Planung = Plan-Run, Review = Read-only-Reviewer-Schicht,
> Testing/Deployment = Build-Gate und Meilenstein-Release. Die Parallelität
> wurde von der Erzeugung auf die Bewertung verschoben — ein Agent je Lauf,
> mehrere Prüfer (19.3, 19.5, 19.8).
