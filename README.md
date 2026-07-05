# ArduPilot AltHold Demo

Docker-based demo that runs ArduCopter SITL and a Python thrust controller using `pymavlink`.

## Requirements

- Linux or WSL2
- Docker

## Build image

```bash
docker compose build aworld
```

## Run

```bash
./scripts/run.sh
```

## Mission flow

1. Init telemetry message interval.
2. Arm.
3. Switch to `GUIDED_NOGPS`.
4. Reach 15 m.
5. Hold 15 m for 20 s.
6. Descend to 10 m.
7. Hold 10 m for 20 s.
8. Switch to `LAND`.
