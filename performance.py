import gc
import time


class PerformanceTracker:
    def __init__(self, log_interval: float = 5.0):
        now = time.monotonic()
        self.log_interval = log_interval
        self.frame_count = 0
        self.start_time = now
        self.next_log_time = now
        self.update_time_total = 0.0
        self.render_time_total = 0.0
        self.memory_delta_total = 0
        self.memory_allocated_total = 0
        self.memory_delta_peak = 0
        self.last_memory_delta = 0
        self._memory_before = 0
        self._update_started_at = 0.0
        self._render_started_at = 0.0

    def start_frame(self) -> None:
        self._memory_before = gc.mem_alloc()

    def start_update_time(self) -> None:
        self._update_started_at = time.monotonic()

    def add_update_time(self) -> None:
        self.update_time_total += time.monotonic() - self._update_started_at

    def start_render_time(self) -> None:
        self._render_started_at = time.monotonic()

    def add_render_time(self) -> None:
        self.render_time_total += time.monotonic() - self._render_started_at

    def complete_frame(self, current_time: float) -> None:
        memory_after = gc.mem_alloc()
        available_memory = gc.mem_free()

        memory_delta = memory_after - self._memory_before
        self.memory_delta_total += memory_delta
        if memory_delta > 0:
            self.memory_allocated_total += memory_delta
        if memory_delta > self.memory_delta_peak:
            self.memory_delta_peak = memory_delta
        self.last_memory_delta = memory_delta

        self.frame_count += 1
        if current_time > self.next_log_time:
            fps = self.frame_count / (current_time - self.start_time)
            print(
                f"__FPS: {fps:.2f}, Update Time: {self.update_time_total / self.frame_count:.4f}s, Render Time: {self.render_time_total / self.frame_count:.4f}s, "
                f"Mem Delta Avg: {self.memory_delta_total / self.frame_count:.2f}B, Mem Alloc Avg: {self.memory_allocated_total / self.frame_count:.2f}B, "
                f"Mem Delta Last: {self.last_memory_delta}B, Mem Delta Peak: {self.memory_delta_peak}B, "
                f"Mem Used: {memory_after}B, Mem Free: {available_memory}B"
            )
            self.next_log_time = current_time + self.log_interval
