# ArduPilot SITL Altitude Control Demo

Docker-based demo that runs ArduCopter SITL and a Python controller using `pymavlink`.

## Requirements

- Linux or WSL2
- Docker with Compose (`docker compose`)

## Run

```bash
cd /mnt/d/Code/gazebo-world
./scripts/run-local.sh
```

When run outside Docker, the script starts Compose. In the container it:

1. Starts ArduCopter SITL.
2. Waits for SITL MAVLink on `tcp:127.0.0.1:5760`.
3. Runs `python3 src/main.py --connect tcp:127.0.0.1:5760 --log-level DEBUG`.

## Build image

```bash
docker compose build aworld
```

Rebuild from scratch (no cache):

```bash
docker compose build --no-cache gazebo_world
```

Build and start:

```bash
docker compose up --build -d gazebo_world
```

## Mission flow

The state machine in `src/main.py` performs:

1. Init telemetry message interval.
2. Arm.
3. Switch to `GUIDED_NOGPS`.
4. Reach 15 m.
5. Hold 15 m for 20 s.
6. Descend to 10 m.
7. Hold 10 m for 20 s.
8. Switch to `LAND`.

## CLI options

`src/main.py` currently supports:

- `--connect` (default: `tcp:127.0.0.1:5760`)
- `--log-level` (`DEBUG|INFO|WARNING|ERROR|CRITICAL`, default: `INFO`)
