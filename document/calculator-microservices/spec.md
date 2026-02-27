# Project Specification: Addition Service

**Project**: Simple Calculator — Addition Microservice  
**Service**: `addition-service`  
**Version**: 1.0.0  
**Author**: Development Team  
**Date**: 2026-02-27  
**Governing Document**: [constitution.md](./constitution.md)

---

## Overview

The **Addition Service** is a standalone Python microservice responsible exclusively for performing addition of two numeric operands. It exposes:

1. A **REST API** (`POST /v1/add`) that accepts two numbers and returns their sum.
2. An **HTML-based Web UI** served at `GET /` that allows a user to enter two numbers in a browser and see the result instantly without any external frontend infrastructure.

The service runs on **port 8001** as defined in the Service Topology of the constitution.

---

## Scope

| In Scope | Out of Scope |
|---|---|
| Addition of two numeric operands | Any other arithmetic operation |
| HTML UI served from the same service | A separate frontend deployment |
| Input validation (numeric, range) | Authentication / authorisation |
| Structured JSON logging | Distributed tracing integration (Phase 1 only) |
| Health check endpoint | Metrics endpoint (Phase 2) |
| Unit + integration tests | End-to-end tests with API Gateway |

---

## User Stories

### Epic 1: Web UI

#### US-1.1: Enter and Add Two Numbers
**As a** calculator user  
**I want to** open a webpage, enter two numbers, and click "Add"  
**So that** I can immediately see the sum without needing developer tools or Postman

**Acceptance Criteria**:
- The page loads at `http://localhost:8001/`
- Two clearly labelled numeric input fields are present: **Operand A** and **Operand B**
- An **"Add"** button submits the inputs
- The result is displayed on the same page below the inputs as: `A + B = <result>`
- Non-numeric input is rejected before submission with an inline validation message
- Empty inputs are rejected before submission with an inline validation message
- The page works without JavaScript frameworks — plain HTML + CSS + minimal vanilla JS only

**Technical Notes**:
- The UI calls `POST /v1/add` via `fetch()` and updates the result area dynamically (no full page reload)
- The HTML file is served by the Python service directly (FastAPI `StaticFiles` or inline `HTMLResponse`)
- All styling is embedded in the HTML file (no external CDN dependencies)

---

#### US-1.2: View Clear Error Feedback
**As a** calculator user  
**I want to** see a clear, human-readable error message if my input is invalid  
**So that** I know exactly what went wrong and can correct it

**Acceptance Criteria**:
- If either field is empty: show `"Please enter a value for Operand A/B"`
- If either field contains non-numeric text: show `"Operand A/B must be a number"`
- If a number exceeds the safe range (> 1e308 or < -1e308): show `"Value is out of the supported numeric range"`
- API errors (HTTP 4xx/5xx) display `"Calculation failed: <server error message>"`
- Errors are shown in a red-highlighted box below the result area
- Errors clear automatically when the user corrects the input and resubmits

**Technical Notes**:
- Client-side validation runs before the API call (fast feedback)
- Server-side validation is also performed independently (defence in depth per constitution §IV)

---

#### US-1.3: View Calculation History on Page
**As a** calculator user  
**I want to** see my last 5 calculations on the same page  
**So that** I can review recent additions without leaving the UI

**Acceptance Criteria**:
- Below the result, a "Recent Calculations" table shows up to 5 past calculations
- Each row shows: `Operand A`, `+`, `Operand B`, `=`, `Result`, `Timestamp`
- History is session-based (in-memory, not persisted to a database in Phase 1)
- History list updates immediately after each successful calculation
- The most recent calculation appears at the top

**Technical Notes**:
- History stored in a Python list in the service's in-memory state (capped at 100 entries)
- Separate endpoint `GET /v1/history` returns the list as JSON; the UI polls it after each calculation
- History is cleared on service restart (persistence is a Phase 2 concern handled by `history-service`)

---

### Epic 2: Addition API

#### US-2.1: Add Two Numbers via API
**As a** developer or API Gateway  
**I want to** call `POST /v1/add` with two numbers  
**So that** I receive the correct sum in a structured JSON response

**Acceptance Criteria**:
- Endpoint: `POST /v1/add`
- Request body (JSON):
  ```json
  {
    "operands": [3.5, 2.5]
  }
  ```
- Success response (HTTP 200):
  ```json
  {
    "result": 6.0,
    "operation": "add",
    "operands": [3.5, 2.5],
    "timestamp": "2026-02-27T10:00:00Z"
  }
  ```
- Supports integers, floats, negative numbers, and zero
- Result precision: Python native `float` addition (IEEE 754 double)
- Response `Content-Type` is always `application/json`

**Technical Notes**:
- Use FastAPI with Pydantic v2 for request validation
- `timestamp` is UTC ISO-8601 format
- Route decorated with `POST`, path `/v1/add`

---

#### US-2.2: Reject Invalid Inputs via API
**As a** developer or API Gateway  
**I want to** receive a structured error response for invalid inputs  
**So that** I can handle errors predictably without parsing HTML error pages

**Acceptance Criteria**:
- Missing `operands` field → HTTP 422, code `MISSING_OPERANDS`
- `operands` array does not have exactly 2 elements → HTTP 422, code `INVALID_OPERAND_COUNT`
- Non-numeric operand (e.g., `"abc"`) → HTTP 422, code `NON_NUMERIC_OPERAND`
- Operand outside IEEE 754 range → HTTP 422, code `OPERAND_OUT_OF_RANGE`
- All error responses follow the schema:
  ```json
  {
    "error": "Human-readable message",
    "code": "ERROR_CODE",
    "details": "Optional technical detail"
  }
  ```
- HTTP 500 for unexpected internal errors (logged server-side, not exposed to caller)

**Technical Notes**:
- Pydantic validators handle type coercion and range checks
- Custom exception handlers added to FastAPI app for uniform error envelope

---

#### US-2.3: Health Check
**As a** DevOps engineer or API Gateway  
**I want to** call `GET /health`  
**So that** I can determine if the addition service is alive and ready

**Acceptance Criteria**:
- Endpoint: `GET /health`
- Success response (HTTP 200):
  ```json
  {
    "status": "ok",
    "service": "addition-service",
    "version": "1.0.0"
  }
  ```
- Response time < 50ms under no load
- Returns HTTP 200 even if history is empty

**Technical Notes**:
- No external dependencies to check in Phase 1 (stateless service)
- Used as Docker `HEALTHCHECK` target

---

## API Contract (OpenAPI Summary)

> Full `openapi.yaml` is written before implementation, per constitution §III.

### `POST /v1/add`

| Property | Value |
|---|---|
| Method | POST |
| Path | `/v1/add` |
| Content-Type | `application/json` |
| Auth | None (internal service in Phase 1) |

**Request Schema**:
```json
{
  "type": "object",
  "required": ["operands"],
  "properties": {
    "operands": {
      "type": "array",
      "items": { "type": "number" },
      "minItems": 2,
      "maxItems": 2
    }
  }
}
```

**Response Schema (200)**:
```json
{
  "type": "object",
  "properties": {
    "result":    { "type": "number" },
    "operation": { "type": "string", "enum": ["add"] },
    "operands":  { "type": "array", "items": { "type": "number" } },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
```

**Error Response Schema (4xx/5xx)**:
```json
{
  "type": "object",
  "properties": {
    "error":   { "type": "string" },
    "code":    { "type": "string" },
    "details": { "type": "string" }
  }
}
```

### `GET /v1/history`

| Property | Value |
|---|---|
| Method | GET |
| Path | `/v1/history` |
| Auth | None |

**Response Schema (200)**:
```json
{
  "type": "object",
  "properties": {
    "history": {
      "type": "array",
      "maxItems": 5,
      "items": {
        "type": "object",
        "properties": {
          "operands":  { "type": "array", "items": { "type": "number" } },
          "result":    { "type": "number" },
          "timestamp": { "type": "string", "format": "date-time" }
        }
      }
    }
  }
}
```

### `GET /health`

**Response Schema (200)**:
```json
{
  "type": "object",
  "properties": {
    "status":  { "type": "string", "enum": ["ok", "degraded", "down"] },
    "service": { "type": "string" },
    "version": { "type": "string" }
  }
}
```

---

## Technical Requirements

### Technology Stack

| Concern | Choice | Rationale |
|---|---|---|
| Language | Python 3.11+ | Constitution mandate |
| Framework | FastAPI 0.110+ | Async support, auto OpenAPI, Pydantic v2 |
| Validation | Pydantic v2 | Type safety, clean error messages |
| Server | Uvicorn | ASGI, production-grade |
| UI delivery | FastAPI `HTMLResponse` | Single-service, no external server needed |
| Testing | pytest + httpx | Async-compatible, FastAPI recommended |
| Linting | ruff + mypy | Fast, type-safe |
| Containerisation | Docker | Constitution mandate |

### Folder Structure (per constitution §Code Organisation)

```
addition-service/
├── src/
│   ├── main.py          # FastAPI app factory, startup/shutdown
│   ├── router.py        # Route definitions (/v1/add, /v1/history, /health)
│   ├── service.py       # add_operands() business logic
│   ├── schema.py        # Pydantic request/response models
│   ├── validator.py     # Range and type validation helpers
│   ├── history.py       # In-memory history store (capped list)
│   └── ui.py            # Serves the HTML UI (HTMLResponse)
├── tests/
│   ├── unit/
│   │   ├── test_service.py    # Pure addition logic tests
│   │   └── test_validator.py  # Input validation tests
│   └── integration/
│       ├── test_add_endpoint.py     # POST /v1/add HTTP tests
│       ├── test_history_endpoint.py # GET /v1/history HTTP tests
│       └── test_health_endpoint.py  # GET /health HTTP tests
├── openapi.yaml         # Written FIRST before any src/ code
├── Dockerfile
├── .env.example
├── requirements.txt
└── README.md
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8001` | Port the service listens on |
| `HOST` | `0.0.0.0` | Bind address |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `MAX_HISTORY` | `100` | Maximum in-memory history entries |
| `SERVICE_VERSION` | `1.0.0` | Version returned in health check |

---

## Testing Requirements

Per constitution §Testing Strategy:

| Test Type | File | What is Tested |
|---|---|---|
| Unit | `test_service.py` | `add_operands(a, b)` with int, float, negative, zero, large values |
| Unit | `test_validator.py` | All invalid input combinations |
| Integration | `test_add_endpoint.py` | Full HTTP request/response cycle for POST /v1/add |
| Integration | `test_history_endpoint.py` | History list grows and caps correctly |
| Integration | `test_health_endpoint.py` | Health returns 200 with correct body |

**Minimum Coverage**: 90% overall; 95% for `service.py` and `validator.py`

### Key Test Cases for `add_operands()`

| Input A | Input B | Expected Result | Notes |
|---|---|---|---|
| `3` | `2` | `5` | Positive integers |
| `3.5` | `2.5` | `6.0` | Floats |
| `-3` | `-2` | `-5` | Negative integers |
| `0` | `0` | `0` | Zero identity |
| `-10` | `10` | `0` | Cancel out |
| `1e308` | `1e308` | `inf` | IEEE overflow — must NOT raise |
| `1e308` | `1` | `1e308` | Near max |

### Key Test Cases for Input Validation

| Input | Expected HTTP | Expected Code |
|---|---|---|
| `{"operands": [1, 2]}` | 200 | — |
| `{}` | 422 | `MISSING_OPERANDS` |
| `{"operands": [1]}` | 422 | `INVALID_OPERAND_COUNT` |
| `{"operands": [1, 2, 3]}` | 422 | `INVALID_OPERAND_COUNT` |
| `{"operands": ["a", 2]}` | 422 | `NON_NUMERIC_OPERAND` |
| `{"operands": [null, 2]}` | 422 | `NON_NUMERIC_OPERAND` |

---

## Non-Functional Requirements

| Requirement | Target |
|---|---|
| Response time (p95) | < 100ms under 100 concurrent requests |
| Startup time | < 3 seconds |
| Memory footprint | < 128MB at idle |
| History cap | 100 entries (in-memory, FIFO eviction) |
| Log format | Structured JSON, UTF-8 |
| Graceful shutdown | Drain in-flight requests within 5 seconds |

---

## Compliance Checklist (Per Constitution)

Before the first PR is opened:

- [ ] `openapi.yaml` written and reviewed
- [ ] All unit tests written and failing (TDD red phase)
- [ ] `service.py` implemented to make unit tests pass
- [ ] Integration tests written and passing
- [ ] Coverage ≥ 90% confirmed via `pytest --cov`
- [ ] Input validation covers all error codes in §US-2.2
- [ ] `GET /health` implemented and tested
- [ ] Structured JSON logging on every `POST /v1/add` request
- [ ] No secrets in source code; `.env.example` committed
- [ ] `Dockerfile` builds successfully
- [ ] `README.md` documents how to run locally and via Docker
- [ ] HTML UI tested in Chrome, Firefox, and Safari

---

## Out of Scope (Future Phases)

| Feature | Phase |
|---|---|
| API Gateway routing | Phase 2 |
| Persistent history via `history-service` | Phase 2 |
| Prometheus `/metrics` endpoint | Phase 2 |
| mTLS inter-service auth | Phase 2 |
| Rate limiting | Phase 2 (gateway level) |
| Support for more than 2 operands | Not planned |

---

## Wireframe Specification

> The actual `wireframe.html` file and all implementation code are created only during the implementation phase. This section specifies what the wireframe and production UI must look like.

### Deliverables

1. **`wireframe.html`** — a single, self-contained HTML file with all styling embedded. No external CDN or assets. Must be openable directly in a browser.
2. **Production UI** served at `GET /` by the Python service — must match the same layout and design tokens.

### Page Structure (Top to Bottom)

```
┌──────────────────────────────────────────────────────┐
│  HEADER BAR (sticky, full width)                     │
│  [+] Addition Service   ● Service: OK    [Port 8001] │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  WIREFRAME ANNOTATION BANNER (dashed border, amber)  │
│  "📐 Wireframe Document — ..."                       │
└──────────────────────────────────────────────────────┘

  [addition-service tag]
  Page Title: "Add Two Numbers"
  Subtitle:   "Enter two numeric values and click Add..."

┌──────────────────────────────────────────────────────┐
│  CARD: Calculator                                    │
│  ┌────────────┐   ┌───┐   ┌────────────┐            │
│  │ Operand A  │   │ + │   │ Operand B  │            │
│  │ [______]  │   │   │   │ [______]  │            │
│  └────────────┘   └───┘   └────────────┘            │
│  [         Add ＋          ]  (full-width button)    │
│  ┌──────────────────────────────────────────────┐   │
│  │ RESULT BOX (shown after success)             │   │
│  │ "Result"  |  expression  |  value (large)    │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │ ERROR BOX (shown on validation/API error)    │   │
│  │ ⚠️ Error title  |  error detail/code         │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  CARD: Recent Calculations                           │
│  Table: Operand A | + | Operand B | = | Result | TS │
│  (5 rows max; "No calculations yet" empty state)     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  CARD: API Reference (2-column grid)                 │
│  [POST /v1/add] [GET /v1/history]                    │
│  [GET /health]  [GET /]                              │
└──────────────────────────────────────────────────────┘
```

### Component Specifications

#### Header Bar

| Property | Value |
|---|---|
| Position | Sticky, top: 0, full viewport width |
| Height | 60px |
| Background | White (`#ffffff`) |
| Border | 1px bottom border, light grey |
| Shadow | Subtle drop shadow |
| Left element | Square icon badge with `+` symbol (brand primary colour), service name and subtitle |
| Centre element | Animated health dot (green pulsing) + "Service: OK" label |
| Right element | Port badge: `Port 8001` (blue-tinted pill shape) |

#### Wireframe Annotation Banner

| Property | Value |
|---|---|
| Background | Amber-yellow tint (`#fffbe6`) |
| Border | 1.5px dashed amber (`#d4a017`) |
| Icon | 📐 |
| Text | Identifies the file as a wireframe spec and names the production URL (`http://localhost:8001`) |
| Visibility | Present only in `wireframe.html`; absent from the production UI |

#### Page Title Area

| Element | Spec |
|---|---|
| Service tag | Small pill badge: `✦ addition-service`, green background |
| H1 title | `"Add Two Numbers"`, 24px, bold |
| Subtitle | `"Enter two numeric values and click Add to calculate their sum."`, muted grey, 14px |

#### Calculator Card

**Operand Inputs** (`Operand A` and `Operand B`):

| Property | Value |
|---|---|
| Input type | `number`, `step="any"` |
| Height | 48px |
| Font | Monospace, 18px, centred text |
| Placeholder | `e.g. 12.5` / `e.g. 7.5` |
| Label | Bold, 13px, above the input |
| Required marker | Red asterisk `*` beside label |
| Focus state | Border turns primary blue, outer glow ring |
| Error state | Border turns red, background `#fff8f8` |
| Inline error text | Red, 11px, appears below the input when validation fails |

**Operator Symbol** (`+` between the two inputs):

| Property | Value |
|---|---|
| Character | `+` |
| Size | 30px, light weight |
| Colour | Muted grey |
| Alignment | Vertically aligned to the bottom of the input fields |
| Responsive | Hidden on mobile (< 600px) |

**Add Button**:

| Property | Value |
|---|---|
| Layout | Full width of the card |
| Height | 52px |
| Background | Primary blue (`#4f75ff`) |
| Hover state | Darker blue (`#3a5ce0`), stronger shadow |
| Active (click) state | Scales to 98% |
| Disabled state | Muted blue (`#b0bfff`), no cursor |
| Loading state | Spinner replaces button label text; button is disabled |
| Label | Icon `＋` + text `"Add"` |

**Result Box** (visible only after a successful response):

| Property | Value |
|---|---|
| Background | Light blue tint (`#eef2ff`) |
| Border | 1.5px solid primary blue |
| Layout | Horizontal flex; left side shows label + expression; right side shows large number |
| Label | `"RESULT"`, uppercase, small, dark blue |
| Expression | `"A + B"` in monospace, grey, 13px |
| Value | Large number, 36px, bold, monospace, primary blue |
| Visibility | Hidden by default; shown after first successful calculation |

**Error Box** (visible only on validation failure or API error):

| Property | Value |
|---|---|
| Background | Light red tint (`#fff0f0`) |
| Border | 1.5px solid red (`#e53e3e`) |
| Icon | `⚠️` |
| Title | Short human-readable error name, 13px, bold, red |
| Detail | Error code or technical detail, 12px, monospace, dark red |
| Visibility | Hidden by default; replaces Result Box on error |
| Auto-clear | Hides again when user corrects input and resubmits |

#### Recent Calculations Card

| Property | Value |
|---|---|
| Title | `"Recent Calculations"`, with right-aligned note `"Last 5 · session only"` |
| Table columns | Operand A (right-aligned, mono) · `+` badge · Operand B (right-aligned, mono) · `=` · Result (right-aligned, bold, primary blue) · Timestamp (small, mono, muted) |
| Row alternation | Odd rows: very light blue tint; Even rows: white |
| Empty state | Single centred row: `"No calculations yet"`, muted grey |
| Row count | Maximum 5 rows displayed; newest at top |
| Operator badge | Small square badge `+`, light blue background |

#### API Reference Card

| Property | Value |
|---|---|
| Layout | 2-column grid (1-column on mobile) |
| Each cell | Dark-bordered block with label + method badge + path + short description |
| Method badge colours | `POST` — amber tint; `GET` — green tint |
| Endpoints listed | `POST /v1/add`, `GET /v1/history`, `GET /health`, `GET /` |

### Design Tokens

All values below must be used consistently across the wireframe and production UI:

| Token | Value | Usage |
|---|---|---|
| `--color-bg` | `#f4f6fb` | Page background |
| `--color-surface` | `#ffffff` | Card background |
| `--color-border` | `#d1d8e8` | Default borders |
| `--color-border-focus` | `#4f75ff` | Focused input border |
| `--color-primary` | `#4f75ff` | Buttons, result value, highlights |
| `--color-primary-dark` | `#3a5ce0` | Button hover |
| `--color-primary-text` | `#ffffff` | Text on primary button |
| `--color-text` | `#1a1f36` | Default body text |
| `--color-text-muted` | `#6b7694` | Labels, hints, timestamps |
| `--color-result-bg` | `#eef2ff` | Result box background |
| `--color-error-bg` | `#fff0f0` | Error box background |
| `--color-error-border` | `#e53e3e` | Error box border |
| `--color-error-text` | `#c53030` | Error text |
| `--radius-md` | `10px` | Input fields, buttons, inner boxes |
| `--radius-lg` | `16px` | Cards |
| `--font-sans` | `'Segoe UI', system-ui, sans-serif` | All body text |
| `--font-mono` | `'Cascadia Code', 'Fira Code', monospace` | Numbers, code, timestamps |

### Interaction & State Flow

```
[Page Load]
  └─► Default state: both inputs empty, result box hidden, error box hidden

[User fills inputs and clicks Add]
  ├─► Client validates inputs:
  │     ├─► Empty field       → Show inline field error, no API call
  │     └─► Non-numeric value → Show inline field error, no API call
  │
  ├─► If valid: disable button, show spinner (loading state)
  │
  ├─► API call: POST /v1/add → { "operands": [a, b] }
  │     ├─► HTTP 200 → hide error box, show result box, update history table
  │     └─► HTTP 4xx/5xx → hide result box, show error box with title + code
  │
  └─► Re-enable button, hide spinner

[User corrects input and resubmits]
  └─► Clear all field errors and error box, repeat validation flow
```

### Responsive Behaviour

| Breakpoint | Layout Change |
|---|---|
| ≥ 600px | Two inputs side-by-side with `+` symbol between them |
| < 600px | Inputs stack vertically; `+` symbol hidden; API grid collapses to 1 column |

### Wireframe File Requirements

The `wireframe.html` file produced during implementation must satisfy:

- [ ] Single self-contained `.html` file — no external CSS, JS, font, or image files
- [ ] All styles embedded in a `<style>` block in `<head>`
- [ ] All interactivity in a `<script>` block at end of `<body>` (vanilla JS, no frameworks)
- [ ] Displays all 4 component sections described above
- [ ] Demonstrates all component states: default, loading button, result box, error box
- [ ] History table shows wireframe example data (hardcoded, not a real API call)
- [ ] "Add" button triggers client-side calculation and updates history (simulated, no server needed)
- [ ] Annotation banner clearly marks the file as a wireframe document
- [ ] File opens correctly in Chrome, Firefox, and Edge without a web server
- [ ] All design tokens from this spec are used as CSS custom properties
