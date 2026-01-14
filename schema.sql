-- =========================================================
-- Canonical Database Schema
-- System: BetaSphere / Core Intelligence Platform
-- Version: v1.0
-- Date: 2026-01-11
-- =========================================================

-- Enable UUID generation (Postgres)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =========================================================
-- 1. systems
-- =========================================================
CREATE TABLE IF NOT EXISTS systems (
    system_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name           TEXT NOT NULL,
    environment    TEXT CHECK (environment IN ('dev', 'staging', 'prod')) NOT NULL,
    status         TEXT CHECK (status IN ('active', 'paused', 'retired')) NOT NULL DEFAULT 'active',
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- 2. modules
-- =========================================================
CREATE TABLE IF NOT EXISTS modules (
    module_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    system_id      UUID NOT NULL REFERENCES systems(system_id) ON DELETE CASCADE,
    name           TEXT NOT NULL,
    version        TEXT,
    role           TEXT CHECK (role IN ('compute', 'sensor', 'control', 'ui', 'storage')),
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- 3. events (IMMUTABLE / APPEND-ONLY)
-- =========================================================
CREATE TABLE IF NOT EXISTS events (
    event_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    system_id      UUID NOT NULL REFERENCES systems(system_id) ON DELETE CASCADE,
    module_id      UUID REFERENCES modules(module_id),
    event_type     TEXT NOT NULL,
    payload        JSONB NOT NULL,
    occurred_at    TIMESTAMPTZ NOT NULL,
    ingested_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_system_time
ON events(system_id, occurred_at);

-- =========================================================
-- 4. state_snapshots
-- =========================================================
CREATE TABLE IF NOT EXISTS state_snapshots (
    snapshot_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    system_id      UUID NOT NULL REFERENCES systems(system_id) ON DELETE CASCADE,
    context        TEXT NOT NULL,
    state_data     JSONB NOT NULL,
    confidence     REAL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- 5. predictions
-- =========================================================
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    system_id       UUID NOT NULL REFERENCES systems(system_id) ON DELETE CASCADE,
    model_name      TEXT NOT NULL,
    horizon_ms      INTEGER NOT NULL CHECK (horizon_ms > 0),
    prediction_data JSONB NOT NULL,
    confidence      REAL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- 6. decisions
-- =========================================================
CREATE TABLE IF NOT EXISTS decisions (
    decision_id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    system_id          UUID NOT NULL REFERENCES systems(system_id) ON DELETE CASCADE,
    trigger_event_id   UUID REFERENCES events(event_id),
    decision_type      TEXT CHECK (decision_type IN ('act', 'suppress', 'escalate')) NOT NULL,
    decision_data      JSONB NOT NULL,
    executed           BOOLEAN DEFAULT FALSE,
    created_at         TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- 7. feedback
-- =========================================================
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id    UUID NOT NULL REFERENCES decisions(decision_id) ON DELETE CASCADE,
    outcome        TEXT CHECK (outcome IN ('success', 'failure', 'unknown')) NOT NULL,
    metrics        JSONB,
    received_at    TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- END OF CANONICAL SCHEMA
-- =========================================================
