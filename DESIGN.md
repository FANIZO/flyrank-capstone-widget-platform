# Capstone Design

## Problem

Small website owners need a reusable contact widget that can be installed with one script tag while keeping captured leads isolated, validated, protected from abuse, enriched, and visible to the correct owner.

## Actors and request paths

1. An authenticated owner manages widgets and views dashboard data.
2. A customer website loads the public versioned script and short-lived widget configuration.
3. A public visitor submits untrusted form data across origins.

## Data model

- `owners`: authenticated tenants.
- `widgets`: owner-scoped configuration and public identifier.
- `submissions`: leads linked to both widget and owner, with an idempotency constraint.
- `background_jobs`: retryable notification work and failure state.

Every private query includes `owner_id`. Public routes resolve only an active widget through its non-sequential `public_id`.

## Layered architecture

```text
HTTP routers -> validation/auth dependencies -> business services -> SQLAlchemy models -> PostgreSQL
```

Rate limiting, geo fallback, and notification jobs are isolated services rather than route-specific implementations.

## Public submission sequence

```text
CORS/preflight -> body limit -> Pydantic validation -> widget lookup
-> rate limit -> idempotency lookup -> honeypot -> geo fallback
-> transaction stores submission + job -> response -> background retry
```

## Security decisions

- Passwords use Argon2 through `pwdlib`.
- Owner tokens are short-lived signed JWTs.
- Widget ownership is enforced in database queries.
- Public payload size and field lengths are bounded.
- Rate limits are keyed by IP and widget.
- A honeypot silently accepts but does not store spam.
- Secrets are environment variables and are never logged.

## Caching

- `/assets/widget.v1.js`: one-year immutable cache; filename changes on release.
- Public widget config: 60-second cache so owner changes become visible quickly.

## Failure boundaries

Provider A failure falls back to provider B. Both failing yields a submission without geo data. Notification failure happens after storage, retries twice, records failure, and does not change submission success.

## Explicit non-goal

The core does not provide production hosting, a real CDN, visual form building, CAPTCHA, or real email delivery. The customer site is intentionally a second local origin.
