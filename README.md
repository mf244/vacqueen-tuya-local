# VacQueen Tuya (Local)

A fully local Home Assistant integration for VacQueen / Tuya-based multi-bowl pet feeders.

## Why this exists
This feeder exposes **push-only DPS** that are not available via polling.
This integration uses a **threaded tinytuya receive loop** to capture real feed
and bowl events reliably.
