CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Physical apiary locations
CREATE TABLE apiaries (
    id              BIGSERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Physical hive equipment
CREATE TABLE hives (
    id              BIGSERIAL PRIMARY KEY,
    apiary_id       BIGINT NOT NULL REFERENCES apiaries(id),
    name            TEXT NOT NULL,
    hive_type       TEXT,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Biological colony occupying a hive
CREATE TABLE colonies (
    id              BIGSERIAL PRIMARY KEY,
    hive_id         BIGINT REFERENCES hives(id),
    name            TEXT,
    queen_year      INTEGER,
    queen_source    TEXT,
    installed_at    DATE,
    ended_at        DATE,
    notes           TEXT
);

-- Sensors, gateways and other field devices
CREATE TABLE devices (
    id              BIGSERIAL PRIMARY KEY,
    device_uid      TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    device_type     TEXT NOT NULL,
    manufacturer    TEXT,
    model           TEXT,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Allows devices to move between hives over time
CREATE TABLE device_assignments (
    id              BIGSERIAL PRIMARY KEY,
    device_id       BIGINT NOT NULL REFERENCES devices(id),
    hive_id         BIGINT REFERENCES hives(id),
    apiary_id       BIGINT REFERENCES apiaries(id),
    assigned_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    removed_at      TIMESTAMPTZ
);

-- Time-series sensor measurements
CREATE TABLE measurements (
    time            TIMESTAMPTZ NOT NULL,
    device_id       BIGINT NOT NULL REFERENCES devices(id),
    metric          TEXT NOT NULL,
    value           DOUBLE PRECISION NOT NULL,
    unit            TEXT,
    quality         SMALLINT,
    metadata        JSONB
);

SELECT create_hypertable(
    'measurements',
    by_range('time'),
    if_not_exists => TRUE
);

CREATE INDEX measurements_device_metric_time_idx
    ON measurements (device_id, metric, time DESC);
