import logging
import time

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

logger = logging.getLogger(__name__)


class LiveAltitudePlot:
    def __init__(self) -> None:
        self.started_at = time.monotonic()
        self.last_draw_at = 0.0
        self.time_s: list[float] = []
        self.current_alt_m: list[float] = []
        self.setpoint_alt_m: list[float] = []
        self.draw_interval_s = 0.2
        self.interpolation_step_s = 0.1

        plt.ion()
        self.fig, self.ax = plt.subplots()
        if self.fig.canvas.manager is not None:
            self.fig.canvas.manager.set_window_title("SITL Altitude Plot")
        self.current_line, = self.ax.plot([], [], label="current_alt_m")
        self.setpoint_line, = self.ax.plot([], [], label="setpoint_alt_m")
        self.ax.set_title("Altitude")
        self.ax.set_xlabel("time_s")
        self.ax.set_ylabel("altitude_m")
        self.ax.legend(loc="upper left")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(left=0.0)
        self.ax.set_ylim(bottom=0.0)
        self.fig.tight_layout()
        plt.show(block=False)

    def update(self, current_alt_m: float, setpoint_alt_m: float | None, altitude_changed: bool) -> None:
        now_s = time.monotonic() - self.started_at
        if altitude_changed:
            self.time_s.append(now_s)
            self.current_alt_m.append(current_alt_m)
            self.setpoint_alt_m.append(setpoint_alt_m if setpoint_alt_m is not None else float("nan"))

        if now_s - self.last_draw_at < self.draw_interval_s:
            return

        if not self.time_s:
            self.last_draw_at = now_s
            return

        interp_time_s, interp_current_alt_m = self.interpolate_curve(
            self.time_s,
            self.current_alt_m,
            self.interpolation_step_s,
        )
        self.current_line.set_data(interp_time_s, interp_current_alt_m)
        self.setpoint_line.set_data(self.time_s, self.setpoint_alt_m)
        setpoint_values = [v for v in self.setpoint_alt_m if v == v]
        ymax = max(self.current_alt_m + setpoint_values + [1.0])
        self.ax.set_xlim(0.0, max(now_s, 1.0))
        self.ax.set_ylim(0.0, ymax * 1.1)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        self.last_draw_at = now_s

    @staticmethod
    def interpolate_curve(time_s: list[float], values: list[float], step_s: float) -> tuple[list[float], list[float]]:
        if len(time_s) < 2:
            return time_s, values

        point_count = len(time_s)
        slopes: list[float] = [0.0] * point_count
        for idx in range(point_count):
            if idx == 0:
                dt = time_s[1] - time_s[0]
                slopes[idx] = (values[1] - values[0]) / dt if dt > 0.0 else 0.0
            elif idx == point_count - 1:
                dt = time_s[idx] - time_s[idx - 1]
                slopes[idx] = (values[idx] - values[idx - 1]) / dt if dt > 0.0 else 0.0
            else:
                dt = time_s[idx + 1] - time_s[idx - 1]
                slopes[idx] = (values[idx + 1] - values[idx - 1]) / dt if dt > 0.0 else 0.0

        interp_time_s: list[float] = []
        interp_values: list[float] = []
        for idx in range(point_count - 1):
            t0 = time_s[idx]
            t1 = time_s[idx + 1]
            v0 = values[idx]
            v1 = values[idx + 1]
            m0 = slopes[idx]
            m1 = slopes[idx + 1]
            dt = t1 - t0
            if dt <= 0.0:
                continue

            steps = max(1, int(dt / step_s))
            start_step = 0 if idx == 0 else 1
            for step in range(start_step, steps + 1):
                u = step / steps
                u2 = u * u
                u3 = u2 * u
                h00 = 2.0 * u3 - 3.0 * u2 + 1.0
                h10 = u3 - 2.0 * u2 + u
                h01 = -2.0 * u3 + 3.0 * u2
                h11 = u3 - u2
                interp_time_s.append(t0 + dt * u)
                interp_values.append(h00 * v0 + h10 * dt * m0 + h01 * v1 + h11 * dt * m1)

        return interp_time_s, interp_values

    def close(self) -> None:
        if plt is None:
            return
        plt.close(self.fig)