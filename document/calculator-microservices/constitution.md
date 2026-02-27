# Project Constitution — Simple Calculator (Microservices)

**Version**: 1.0.0 | **Ratified**: 2026-02-27 | **Last Amended**: 2026-02-27

This document establishes the core principles and governance rules for the **Simple Calculator** project, implemented as a microservices architecture. All contributors and AI code-generation agents must comply with these principles without exception.

---

## Project Overview

The Simple Calculator exposes arithmetic operations (addition, subtraction, multiplication, division, and optionally modulo/power) as independent, deployable microservices behind a unified API Gateway. Each operation is owned by exactly one service.

### Service Topology

| Service | Responsibility | Default Port |
|---|---|---|
| `api-gateway` | Routes requests, rate limiting, auth | 8000 |
| `addition-service` | Handles `+` operations | 8001 |
| `subtraction-service` | Handles `-` operations | 8002 |
| `multiplication-service` | Handles `*` operations | 8003 |
| `division-service` | Handles `/` operations | 8004 |
| `history-service` | Stores and retrieves past calculations | 8005 |
| `health-service` | Aggregated health checks for all services | 8006 |

---

## Core Principles

### I. Test-First Development (NON-NEGOTIABLE)

All code must follow Test-Driven Development (TDD):
- Write tests **FIRST** before any implementation
- Tests must **FAIL** initially (red phase)
- Implement the minimum code to make tests **PASS** (green phase)
- Refactor while keeping all tests green (refactor phase)
- Minimum **90% code coverage** required per service (calculator logic is deterministic — no excuses)

**Rationale**: Calculator operations are mathematically precise. TDD ensures correctness and prevents silent regressions across service boundaries.

### II. Single Responsibility per Service

Each microservice must:
- Own **exactly one** arithmetic domain (addition, subtraction, etc.)
- Expose **no business logic** belonging to another service
- Never call a sibling operation service directly (communicate only through the API Gateway or an event bus)
- Be independently deployable without requiring other services to restart

**Rationale**: Violating single responsibility couples services and defeats the purpose of the microservices architecture.

### III. API-First Design (CONTRACT BEFORE CODE)

Every service must define its API contract before writing implementation:
- Define OpenAPI 3.x specification (`openapi.yaml`) before coding
- Request schema: `{ "operands": [number, number] }`
- Response schema: `{ "result": number, "operation": string, "timestamp": string }`
- Error schema: `{ "error": string, "code": string, "details": string }`
- All APIs versioned under `/v1/` (e.g., `POST /v1/add`)
- Backward compatibility must be maintained; breaking changes require a new major version

**Rationale**: Contracts allow parallel development across services and prevent integration surprises.

### IV. Input Validation on Every Boundary

Every service must validate inputs defensively:
- Reject non-numeric operands with HTTP 422 and a clear message
- Reject requests with missing or extra fields
- `division-service` must explicitly reject division by zero with HTTP 400 and code `DIVISION_BY_ZERO`
- Validate numeric range to prevent overflow (IEEE 754 limits)
- Never propagate raw exceptions to API consumers

**Rationale**: Calculator services receive untrusted input from the network. Silent errors or unhandled edge cases produce wrong results consumers may trust.

### V. Observability (MANDATORY FROM DAY ONE)

All services must be observable from the first commit:
- **Structured JSON logging** for every request/response (operation, operands, result, duration_ms, service_name, trace_id)
- **Health check endpoint**: `GET /health` returning `{ "status": "ok" | "degraded" | "down" }`
- **Metrics**: request count, error count, and p95 latency exposed via `GET /metrics` (Prometheus format)
- **Distributed tracing**: propagate `X-Trace-Id` header across all service hops
- **Never log raw operands at INFO level** in production (privacy/compliance)

**Rationale**: Microservices fail independently and in non-obvious ways. Observability is how you diagnose cascading failures at 2 AM.

### VI. Resilience and Fault Isolation

Services must be resilient by design:
- `api-gateway` must implement a **circuit breaker** per downstream service
- Downstream service failure must return HTTP 503 with `{ "error": "service_unavailable", "service": "<name>" }`
- All service calls must have a **timeout** (default: 2 seconds)
- Services must implement **graceful shutdown** (drain in-flight requests before stopping)
- `history-service` failure must not break arithmetic operations (non-critical path)

**Rationale**: A failing division service must not take down addition. Fault isolation is the primary value proposition of microservices.

### VII. Security by Default

Security is not optional:
- The `api-gateway` is the **only** service exposed externally; all operation services are internal only
- Inter-service communication must use mTLS or a shared internal secret header (`X-Internal-Token`)
- No secrets, API keys, or credentials in source code — use environment variables or a secrets manager
- Rate limiting enforced at the gateway: 100 req/min per IP by default
- All inputs sanitized before processing (no eval, no dynamic code execution)

**Rationale**: Even a simple calculator can be abused (DoS, data harvesting of calculation history) if not properly secured.

### VIII. Clean Code and Documentation

Code must be:
- Self-documenting with clear, intention-revealing names (`divide_operands()`, not `do_calc()`)
- Fully documented with docstrings (all public functions, classes, and modules)
- Type-hinted throughout (Python: type annotations; TS/JS: TypeScript strict mode)
- Free of dead code, commented-out blocks, and TODO items at merge time
- Each service must have a `README.md` explaining its purpose, API contract, and how to run it locally

**Rationale**: Microservices multiply surface area. Documentation and clarity are critical when different people (or agents) own different services.

---

## Architecture Constraints

### Service Communication

| Rule | Detail |
|---|---|
| Protocol | HTTP/REST (JSON) for synchronous calls |
| Async events | Use an event bus (e.g., Redis Streams or RabbitMQ) for history recording only |
| No direct DB sharing | Each service owns its own data store (if any) |
| Discovery | Services discovered via environment variable (`ADDITION_SERVICE_URL`, etc.) |

### Data Ownership

- `history-service` is the **sole owner** of calculation history data
- Arithmetic services must not persist results themselves
- `api-gateway` must not contain business logic — routing and cross-cutting concerns only

### Deployment

- Each service must have its own `Dockerfile`
- A root-level `docker-compose.yml` must orchestrate all services for local development
- Each service must be independently scalable (stateless arithmetic services, stateful history service)
- Environment-specific configuration via `.env` files (never committed) — `.env.example` committed instead

---

## Additional Constraints

### Error Handling

- Use HTTP status codes correctly: 200 (success), 400 (bad input), 422 (validation), 500 (internal), 503 (downstream unavailable)
- Never return a 200 with an error in the body
- Log errors with: `service_name`, `trace_id`, `error_code`, `message`, stack trace (DEBUG only)
- User-facing errors must be human-readable; never expose internal stack traces

### Testing Strategy

| Test Type | Scope | Minimum Coverage |
|---|---|---|
| Unit tests | Pure business logic (arithmetic functions) | 95% |
| Integration tests | Service HTTP endpoints (test with real HTTP) | 80% |
| Contract tests | API Gateway ↔ operation services | All endpoints |
| End-to-end tests | Full flow through gateway | Happy path + key error paths |

### Code Organization (per service)

```
<service-name>/
├── src/
│   ├── main.py          # Entry point
│   ├── router.py        # Route definitions
│   ├── service.py       # Business logic
│   ├── schema.py        # Request/response models
│   └── validator.py     # Input validation
├── tests/
│   ├── unit/
│   └── integration/
├── openapi.yaml         # API contract (written first)
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Governance

### Constitution Authority

This constitution supersedes all other development practices for the Calculator Microservices project. Any deviation must be:
1. Documented with a clear technical justification
2. Approved by the technical lead before implementation
3. Reviewed in the next retrospective
4. Constitution amended if the deviation becomes a recurring pattern

### Amendment Process

To amend this constitution:
1. Propose the change with rationale (GitHub issue or PR description)
2. Team discussion and majority vote
3. Update the version number (semantic versioning)
4. Update the **Last Amended** date
5. Communicate changes to all contributors and AI agents using this document

### Compliance Checklist

All code reviews must verify the following before merge:

- [ ] API contract (`openapi.yaml`) written/updated before implementation
- [ ] Tests written first and all passing (≥ 90% coverage)
- [ ] Input validation covers all edge cases including division by zero
- [ ] Health check endpoint present and tested
- [ ] Structured logging added for request/response cycle
- [ ] No secrets or credentials in code
- [ ] `README.md` updated with any API or behavior changes
- [ ] Service does not call sibling services directly
- [ ] Error responses follow the defined error schema
- [ ] `Dockerfile` and `docker-compose.yml` updated if new service was added

**Violations**: Code that violates these principles will not be merged. The reviewer is equally responsible for compliance.
