# 11 Domain-Driven Design Integration

> **Hinweis:** Ohne fachliches Domänenmodell generieren Agenten technisch korrekten, aber fachlich fragwürdigen Code. DDD-Integration ist für Enterprise-Projekte unerlässlich.

![Hexagonale Architektur mit DDD und Agenten-Zuordnung](abbildungen/out/abb11.pdf){width=100%}

| DDD-Konzept | Agenten-Integration | Beispiel |
| --- | --- | --- |
| Bounded Context | Agenten respektieren strikt die Context-Grenzen | payment-context/, user-context/ |
| Ubiquitous Language | Glossar in docs/domain/glossary.md | Zahlungsauslösung statt triggerPayment |
| Aggregates | Dev-Agent erstellt Invarianten und Consistency Rules | OrderAggregate mit OrderLines |
| Domain Events | Kafka-Producer/Consumer für Event-Driven Architecture | PaymentInitiatedEvent |
| Context Map | Architecture-Agent pflegt die Beziehungskarte | docs/domain/context-map.json |

## Java-Beispiel: DDD-Aggregate mit Java 21

```java
// === Value Object als Record ===
public record Money(@Positive BigDecimal amount, @NotNull Currency currency)
        implements Comparable<Money> {
    public Money { amount = amount.setScale(2, RoundingMode.HALF_UP); }
    public static Money of(double amount, String code) {
        return new Money(BigDecimal.valueOf(amount), Currency.getInstance(code));
    }
    public Money add(Money other) { requireSameCurrency(other);
        return new Money(amount.add(other.amount), currency); }
    private void requireSameCurrency(Money o) {
        if (!currency.equals(o.currency)) throw new CurrencyMismatchException(currency, o.currency);
    }
}

// === Aggregate Root ===
@Entity @Table(name = "orders")
public class Order extends AbstractAggregateRoot<Order> {
    @EmbeddedId private OrderId id;
    @Embedded private Money totalAmount;
    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "order_id")
    private List<OrderLine> lines = new ArrayList<>();
    @Enumerated(EnumType.STRING) private OrderStatus status;

    public static Order create(OrderId id) {
        Order order = new Order();
        order.id = id; order.status = OrderStatus.DRAFT;
        order.totalAmount = Money.of(0, "EUR");
        order.registerEvent(new OrderCreatedEvent(id, Instant.now()));
        return order;
    }
    public void confirm() {
        if (lines.isEmpty()) throw new EmptyOrderException(id);
        if (status != OrderStatus.DRAFT) throw new InvalidOrderTransitionException(id, status);
        status = OrderStatus.CONFIRMED;
        registerEvent(new OrderConfirmedEvent(id, totalAmount, Instant.now()));
    }
}

// === Domain Events (Sealed Interface) ===
public sealed interface OrderEvent {
    OrderId orderId(); Instant occurredAt();
    record OrderCreatedEvent(OrderId orderId, Instant occurredAt) implements OrderEvent {}
    record OrderConfirmedEvent(OrderId orderId, Money total, Instant occurredAt) implements OrderEvent {}
}
```

## Kafka Outbox Pattern

```java
@Component @Slf4j
public class OutboxEventPublisher {
    private final OutboxRepository outboxRepo;
    private final KafkaTemplate<String, String> kafka;
    private final ObjectMapper mapper;

    @TransactionalEventListener(phase = BEFORE_COMMIT)
    public void handleDomainEvent(OrderEvent event) {
        outboxRepo.save(new OutboxEntry(UUID.randomUUID(),
                event.getClass().getSimpleName(), event.orderId().value().toString(),
                mapper.writeValueAsString(event), Instant.now(), OutboxStatus.PENDING));
    }

    @Scheduled(fixedDelay = 1000) @Transactional
    public void publishPendingEvents() {
        outboxRepo.findByStatusOrderByCreatedAtAsc(OutboxStatus.PENDING).forEach(entry -> {
            try { kafka.send("order-events", entry.getAggregateId(), entry.getPayload())
                    .get(5, TimeUnit.SECONDS);
                entry.markAsPublished();
            } catch (Exception e) { entry.markAsFailed(e.getMessage()); }
        });
    }
}
```

> **Praxis-Check SoftwareFabrik (abweichend):** Die Fabrik wendet DDD auf
> sich selbst an — modelliert wird der Entwicklungsprozess als Domäne
> (27 Bounded Contexts: Run, Backlog, Freigabe, Policy, Nachweis). Bewusste
> Pragmatik gegen die reine Lehre: Aggregat und JPA-Entität sind dieselbe
> Klasse; statt Kafka genügen interne Events im Einzelprozess-Deployment
> (19.1, 19.2).
