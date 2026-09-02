# Capstone Evidence

This document maps every core requirement and acceptance probe to real automated or manual evidence. Tokens, passwords, visitor IPs, and private information are excluded.

## Environment verification

The application was built and run using Docker Compose. The FastAPI service ran at `http://localhost:8000`, and the customer demonstration page ran from the separate origin `http://localhost:5500`.

The following command was run on 2026-09-02:

```powershell
docker compose exec app pytest -q
```

Actual output:

```text
......                                                                   [100%]
6 passed in 4.34s
```

## Demonstration screenshots

### Embedded widget and successful submission

The widget rendered on the second-origin customer page. A valid form submission displayed: `Thank you. Your message was received.`

![Successful embedded widget submission](evidence/01-widget-success.png)

### Submission visible through the owner dashboard

The stored lead appeared in the authenticated `/dashboard/submissions` response.

![Lead visible in dashboard](evidence/02-dashboard-submission.png)

### Dashboard analytics

The authenticated `/dashboard/stats` endpoint reported owner-scoped submission statistics.

![Dashboard statistics](evidence/03-dashboard-stats.png)

### Automated acceptance tests

![Six acceptance tests passed](evidence/04-tests-passed.png)

## Requirement-by-requirement evidence

| Requirement | Proof | Result |
|---|---|---|
| Authenticated widget CRUD | `tests/test_auth_widgets.py::test_authentication_and_tenant_isolation` | Authenticated owner operations succeeded |
| Requests without valid authentication rejected | JWT dependency exercised by protected routes | Protected operations require bearer authentication |
| Tenant isolation | `test_authentication_and_tenant_isolation` | Tenant B received `404` for Tenant A's widget |
| Embed snippet generated | `test_snippet_and_cache_headers` | Snippet contained the correct public widget ID |
| Public cached configuration | `test_snippet_and_cache_headers` | Config returned `Cache-Control: public, max-age=60` |
| Versioned widget bundle | `test_snippet_and_cache_headers` | `widget.v1.js` returned an immutable one-year cache header |
| Widget renders on another origin | Manual browser test and screenshot 01 | Widget rendered successfully at port `5500` |
| Correct CORS and preflight | `test_cors_validation_idempotency_and_dashboard` | Preflight returned `200` and wildcard public CORS header |
| Boundary validation | Same test | Malformed email returned clean `422` JSON |
| Oversized payload rejection | `test_oversized_payload_returns_413` | Oversized request returned JSON `413`, never `500` |
| Valid submission storage | Dashboard test and screenshot 02 | Lead stored and visible to its owner |
| Correct widget and tenant linkage | Dashboard test | Submission count appeared only in the authenticated owner's dashboard |
| Rate limiting | `test_honeypot_and_rate_limit` | Burst returned `429`; health endpoint continued returning `200` |
| Honeypot spam control | Same test | Filled honeypot was accepted silently but no lead row was stored |
| Provider A to B fallback | `test_geo_fallback_and_safe_side_effect_failure` | A failed; B enriched the submission |
| Both geo providers unavailable | Same test | Submission succeeded with no geo data |
| Safe failing side effect | Same test | Submission stayed stored; job failed only after two bounded attempts |
| Idempotency | `test_cors_validation_idempotency_and_dashboard` | Repeated key returned `already_processed`; only one row existed |
| Background job | `test_geo_fallback_and_safe_side_effect_failure` | Notification executed off the response path with retries and failure status |
| Dashboard leads and analytics | Dashboard test plus screenshots 02-03 | Owner saw stored lead and matching total |
| Persistence and indexes | `migrations/001_initial.sql` | PostgreSQL tables, foreign keys, uniqueness, and tenant/query indexes defined |
| Secrets kept out of Git | `.gitignore` and `.env.example` | Runtime `.env` is ignored; only placeholders are documented |
| Layered architecture | `app/routers`, `app/services`, models and schemas | HTTP, business services, validation, and persistence are separated |

## Acceptance probes

### Probe 1: valid second-origin submission

- Customer site origin: `http://localhost:5500`
- API origin: `http://localhost:8000`
- Widget rendered successfully.
- Browser displayed the successful receipt message.
- Lead appeared in `/dashboard/submissions`.
- Browser console contained no CORS errors.

Evidence: screenshots 01 and 02, plus `test_cors_validation_idempotency_and_dashboard`.

### Probe 2: malformed and oversized payloads

- Invalid email produced `422` JSON.
- Declared body above the configured 8 KiB limit produced `413` JSON.
- Neither condition produced a server error.

Evidence: `test_cors_validation_idempotency_and_dashboard` and `test_oversized_payload_returns_413`.

### Probe 3: burst submissions

Five submissions within the configured window succeeded. The next request returned `429`, while `/health` continued returning `200`.

Evidence: `test_honeypot_and_rate_limit`.

### Probe 4: geolocation fallback

The deterministic test disabled provider A and confirmed provider B enrichment. It then disabled both providers and confirmed that the submission remained stored with null geo fields.

Evidence: `test_geo_fallback_and_safe_side_effect_failure`.

### Probe 5: notification failure

The test forced the confirmation side effect to throw. The primary submission still returned success and remained in the database. The job retried twice and recorded final failure.

Evidence: `test_geo_fallback_and_safe_side_effect_failure`.

### Probe 6: honeypot spam

A submission with a filled `company_website` honeypot received a non-revealing accepted response, while the database submission count remained zero.

Evidence: `test_honeypot_and_rate_limit`.

## Git history evidence

```text
266d614 Stage 7: configure seeded widget demo
2535cd6 Stage 6: add deterministic acceptance tests
15a1d42 Stage 5: add dashboard and second-origin demo
9277764 Stage 4: add resilient lead submission pipeline
ff515c5 Stage 3: add widget management and delivery
4286406 Stage 2: add owner authentication
03c90c0 Stage 1: add database schema and application foundation
988b937 Stage 0: initialize capstone design and documentation
```

## Final verification

- [x] Dedicated public repository created
- [x] Eight meaningful stage commits present
- [x] Docker application starts
- [x] Seed command creates demonstration data
- [x] Widget renders from a separate origin
- [x] Cross-origin submission succeeds
- [x] Stored lead appears in owner dashboard
- [x] Browser console is free from CORS errors
- [x] All six deterministic tests pass
- [x] Required submission documents are present
- [x] Evidence screenshots use the documented filenames
