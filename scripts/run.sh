#!/usr/bin/env bash
set -euo pipefail

if [ -f /.dockerenv ] || [ "${IN_DOCKER:-}" = "1" ]; then
  cat > /tmp/sitl.parm <<'EOF'
GUID_OPTIONS 8
SIM_GPS_DISABLE 1
EOF

  cd /opt/ardupilot
  SITL_RITW_TERMINAL="screen -D -m" python3 Tools/autotest/sim_vehicle.py \
    -v ArduCopter \
    --model quad \
    --add-param-file=/tmp/sitl.parm \
    --no-mavproxy \
    --no-rebuild \
    --out=udp:127.0.0.1:14550 \
    >/tmp/sitl.log 2>&1 &
  sitl_pid=$!

  cleanup() {
    kill "${sitl_pid}" >/dev/null 2>&1 || true
  }
  trap cleanup EXIT

  # Wait until SITL opens SERIAL0 TCP port before controller connects.
  for _ in $(seq 1 60); do
    if python3 -c 'import socket; s=socket.socket(); s.settimeout(0.2); s.connect(("127.0.0.1", 5760)); s.close()' >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done

  cd /workspace
  python3 src/main.py --connect tcp:127.0.0.1:5760 --log-level INFO "$@"
else
  docker compose up
fi