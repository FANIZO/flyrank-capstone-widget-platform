CREATE TABLE IF NOT EXISTS owners (
    id SERIAL PRIMARY KEY,
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS widgets (
    id SERIAL PRIMARY KEY,
    public_id VARCHAR(36) NOT NULL UNIQUE,
    owner_id INTEGER NOT NULL REFERENCES owners(id) ON DELETE CASCADE,
    widget_type VARCHAR(30) NOT NULL,
    title VARCHAR(120) NOT NULL,
    description VARCHAR(500),
    button_text VARCHAR(60) NOT NULL,
    field_configuration JSONB NOT NULL,
    display_options JSONB NOT NULL DEFAULT '{}'::jsonb,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    widget_id INTEGER NOT NULL REFERENCES widgets(id) ON DELETE CASCADE,
    owner_id INTEGER NOT NULL REFERENCES owners(id) ON DELETE CASCADE,
    idempotency_key VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(320) NOT NULL,
    message TEXT NOT NULL,
    ip_address VARCHAR(64) NOT NULL,
    country VARCHAR(120),
    city VARCHAR(120),
    geo_provider VARCHAR(40),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_submission_widget_idempotency UNIQUE (widget_id, idempotency_key)
);

CREATE TABLE IF NOT EXISTS background_jobs (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL DEFAULT 'confirmation',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_widgets_owner_created ON widgets(owner_id, created_at);
CREATE INDEX IF NOT EXISTS ix_submissions_owner_created ON submissions(owner_id, created_at);
CREATE INDEX IF NOT EXISTS ix_submissions_widget_created ON submissions(widget_id, created_at);
CREATE INDEX IF NOT EXISTS ix_jobs_status_created ON background_jobs(status, created_at);
