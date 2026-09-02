# AI-Assisted Build Log

This file honestly records how AI assisted the capstone, what was verified manually, what required correction, and what was learned. AI assistance was used, but responsibility for understanding, testing, documenting, and submitting the system remains with the project owner.

## 2026-09-02: capstone selection and requirements analysis

### Task

Review the Embeddable Widget & Lead-Capture Platform brief and determine whether it matched the owner's existing Python backend experience.

### How AI helped

AI reviewed the capstone requirements, separated core requirements from optional stretch goals, identified the required repository files, and converted the brief into implementation stages.

### Human decisions

The owner selected the widget platform capstone and chose the Python/FastAPI lane. The owner agreed to use a separate public repository as required by the brief.

### What was learned

The capstone combines existing skills-FastAPI, PostgreSQL, Docker, authentication, validation, and error handling-with new public-internet concerns such as CORS, rate limiting, widget delivery, fallback chains, and tenant isolation.

## 2026-09-02: initial implementation

### Task

Create a complete minimal core implementation satisfying the capstone's behavioral requirements.

### How AI helped

AI generated an initial repository containing:

- FastAPI and PostgreSQL configuration
- SQLAlchemy models and PostgreSQL migration
- Local JWT owner authentication
- Tenant-isolated widget CRUD
- Public widget configuration and versioned JavaScript delivery
- Public lead submission API
- CORS and preflight support
- Pydantic boundary validation and payload-size protection
- Per-IP/per-widget rate limiting
- Honeypot spam protection
- Deterministic and optional real geo providers
- Idempotency constraint
- Retrying background notification job
- Owner dashboard endpoints
- Second-origin customer test page
- Docker, seeding, documentation, and tests

### Corrections made during review

- Idempotency was enforced with a database uniqueness constraint rather than only an application lookup.
- Background notification failure was bounded to two attempts and stored as a job failure.
- The versioned JavaScript bundle received an immutable one-year cache header.
- Geo-provider mocks were retained for deterministic evaluation, while optional real-provider modes were added.
- Docker defaults were made runnable locally without requiring paid services or cloud credentials.
- Public CORS was configured without credentials because the widget is intended for arbitrary customer sites.

### Human ownership

The owner extracted the project, created the dedicated public repository, reviewed the folder structure, made eight meaningful commits, started Docker, seeded the application, configured the generated public widget ID, and performed the browser demonstration.

## 2026-09-02: Docker networking diagnosis

### Problem

Docker initially failed to bind the capstone API to port `8000` because a previous development container was already using that port.

### How AI helped

AI explained how to identify the container publishing port `8000`, stop only the previous development service, bring down the partially started capstone stack, and restart it cleanly.

### Human verification

The owner freed port `8000`, started the capstone stack successfully, and opened the health and Swagger endpoints.

### What was learned

Only one process or container can bind the same host port at a time. A port-allocation error is a host networking conflict rather than an application-code failure.

## 2026-09-02: authentication and Swagger verification

### Task

Authenticate as the seeded owner and use the bearer token to access protected dashboard routes.

### How AI helped

AI explained that Swagger's authorization box requires only the complete access-token value, without the JSON key, quotation marks, comma, or manually added `Bearer` prefix.

### Security correction

An access token became visible in a troubleshooting screenshot. The screenshot was excluded from submission evidence. Submission screenshots were taken without exposing tokens, passwords, or environment values.

### What was learned

Bearer tokens are credentials. They must not appear in repositories, logs, documentation, or screenshots. Swagger adds the bearer scheme automatically.

## 2026-09-02: second-origin and dashboard proof

### Human verification

The owner confirmed that:

- The widget rendered at `http://localhost:5500`.
- The API ran at `http://localhost:8000`.
- A valid submission displayed `Thank you. Your message was received.`
- The stored lead appeared in `/dashboard/submissions`.
- Dashboard statistics were available.
- The browser console showed no CORS errors.

Evidence was saved as:

```text
evidence/01-widget-success.png
evidence/02-dashboard-submission.png
evidence/03-dashboard-stats.png
evidence/04-tests-passed.png
```

### What was learned

Different ports are different browser origins. Correct preflight and response headers are necessary before a public widget can communicate with an API it does not share an origin with.

## 2026-09-02: acceptance testing

### Command

```powershell
docker compose exec app pytest -q
```

### Actual result

```text
......                                                                   [100%]
6 passed in 4.34s
```

### Behaviors verified

- Authentication and tenant isolation
- Embed snippet and cache headers
- CORS preflight and boundary validation
- Idempotent lead storage and dashboard visibility
- Honeypot filtering and burst rate limiting
- Geo-provider fallback and all-provider degradation
- Side-effect failure with persistent lead storage
- Oversized-payload rejection

### What was learned

Deterministic tests provide stronger evidence than manually claiming that a feature works. Failure behavior must be deliberately forced and checked, not assumed.

## Known limitations accepted for the core

- The rate limiter is in-process and intended for a single local API instance.
- Trusted reverse-proxy IP handling is not configured.
- Geo providers default to deterministic mocks.
- Confirmation is represented by a console side effect instead of real email.
- The widget is a minimal contact form rather than a visual form-building product.
- Production hosting and CDN deployment are outside the required local scope.

These limitations are documented openly rather than hidden. They do not prevent the required core acceptance probes from passing.
