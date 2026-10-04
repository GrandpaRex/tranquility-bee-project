# 🐝 The Tranquility Bee Project

**An open, local-first platform for intelligent apiary monitoring, environmental observation, and beekeeping research.**

The Tranquility Bee Project combines hive telemetry, environmental sensors,
beekeeper observations, long-range LoRa/Meshtastic communications, local-first
data storage, and eventually machine learning into a modular apiary monitoring
platform.

The project began as infrastructure for Tranquility Bee Farms and is being
developed and validated using real colonies.

> **Collect locally. Analyze locally. Alert immediately. Share intentionally.**

## Project Status

🚧 **Prototype 001 — Active Development**

Prototype 001 is being developed around:

- BroodMinder hive instrumentation
- Meshtastic / US915 LoRa networking
- HiveTracks inspection records
- Environmental monitoring
- MQTT
- PostgreSQL + TimescaleDB
- Grafana
- Ubuntu Server
- Docker Compose

The initial deployment will support two colonies while the architecture is
developed and validated.

## Design Principles

### Local First

Apiary infrastructure should continue collecting and storing data when Internet
connectivity is unavailable.

### Store and Forward

Routine telemetry can synchronize periodically. Time-sensitive alerts receive
priority and can use any available communications path.

### Integration Instead of Replacement

Existing equipment should be reused whenever practical. Tranquility is intended
to integrate systems such as BroodMinder, HiveTracks, Meshtastic, existing
weather stations, cellular connectivity, and Starlink rather than requiring a
completely proprietary ecosystem.

### Data Ownership

Beekeepers own their raw data. Future research participation will be explicit
and opt-in.

### Open Architecture

Sensors, communications, storage, visualization, analytics, and backhaul are
separate layers so individual components can evolve without replacing the
entire system.

## High-Level Architecture

```text
Hive Sensors ─────┐
Weather Station ──┤
Water Monitoring ─┤
Power Monitoring ─┤
                  ▼
             Yard Gateway
                  │
          Meshtastic / LoRa
                  │
                  ▼
              Farm Hub
        MQTT + Local Database
                  │
       ┌──────────┴──────────┐
       │                     │
 Routine Sync          Emergency Alerts
       │                     │
       └──────────┬──────────┘
                  ▼
          Home / Private Cloud
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    Grafana    Analytics     ML
