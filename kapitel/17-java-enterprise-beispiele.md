# 17 Erweiterte Java Enterprise Praxisbeispiele

## 17.1 Spring Security mit JWT und RBAC

```java
@Configuration @EnableWebSecurity @EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {
    private final JwtAuthFilter jwtAuthFilter;
    private final AuthenticationProvider authProvider;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/auth/**").permitAll()
                .requestMatchers("/actuator/health/**").permitAll()
                .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
                .requestMatchers("/api/v1/payments/**").hasAnyRole("USER", "ADMIN")
                .anyRequest().authenticated())
            .authenticationProvider(authProvider)
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }
}

// === JWT Auth Filter ===
@Component @RequiredArgsConstructor @Slf4j
public class JwtAuthFilter extends OncePerRequestFilter {
    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res,
            FilterChain chain) throws ServletException, IOException {
        String header = req.getHeader("Authorization");
        if (header == null || !header.startsWith("Bearer ")) { chain.doFilter(req, res); return; }
        String jwt = header.substring(7);
        try {
            String username = jwtService.extractUsername(jwt);
            if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                UserDetails user = userDetailsService.loadUserByUsername(username);
                if (jwtService.isTokenValid(jwt, user)) {
                    var auth = new UsernamePasswordAuthenticationToken(user, null,
                            user.getAuthorities());
                    SecurityContextHolder.getContext().setAuthentication(auth);
                }
            }
        } catch (JwtException e) { log.warn("Invalid JWT: {}", e.getMessage()); }
        chain.doFilter(req, res);
    }
}
```

## 17.2 Camunda 8 mit Zeebe

```java
@Component @Slf4j
public class AmountCheckWorker {
    private static final Money THRESHOLD = Money.of(10000, "EUR");

    @ZeebeWorker(type = "payment-amount-check", timeout = 30000, maxJobsActive = 10)
    public void handle(@ZeebeVariable Money amount, @ZeebeVariable String paymentId,
            JobClient client, ActivatedJob job) {
        boolean needsApproval = amount.compareTo(THRESHOLD) > 0;
        client.newCompleteCommand(job.getKey())
                .variables(Map.of("requiresApproval", needsApproval,
                        "checkResult", needsApproval ? "MANUAL_APPROVAL" : "AUTO_APPROVED"))
                .send().join();
    }
}
```
