# AI-Assisted Build Log

## 2026-09-02 - Initial complete implementation

### Task

Design and implement the core Embeddable Widget & Lead-Capture capstone in Python.

### How AI helped

AI translated the capstone contract into a repository structure, proposed the schema and endpoint boundaries, generated an initial FastAPI implementation, added Docker configuration, wrote the browser widget, and drafted deterministic acceptance tests and documentation.

### What required human ownership

The project owner must run every command, inspect every test result, replace development secrets, create the public GitHub repository, capture manual browser evidence, and be able to explain the code. Configuration for a real deployment, production proxy IP handling, distributed rate limiting, and real email delivery remain deliberate limitations.

### Corrections made during review

- Added a database uniqueness constraint instead of trusting an application-only idempotency check.
- Stored background-job failure state and bounded retries.
- Added immutable cache headers to the versioned script.
- Made geo fallbacks deterministic for tests while retaining optional real-provider modes.
- Made Docker runnable without requiring a secret file for local evaluation.

### What was learned

Public browser input requires separate validation, abuse, resilience, and caching boundaries. A secondary operation must be committed after the primary data path and observed independently when it fails.

Add a new dated entry whenever AI materially changes the project. Record wrong suggestions and your correction honestly.
