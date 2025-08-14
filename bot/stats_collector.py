import multiprocessing as mp
import time
import threading


class StatsCollector:
    def __init__(self, project_logger=None):
        self.kp_queue: mp.Queue = None
        self.stats = {"frames": 0, "lying": 0, "standing": 0}
        self.is_running = False
        self.start_time = None
        self.thread = None
        self.project_logger = project_logger

    def set_queue(self, queue: mp.Queue):
        self.kp_queue = queue

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._collect, daemon=True)
        self.thread.start()

    def _collect(self):
        while self.is_running:
            try:
                data = self.kp_queue.get(timeout=0.1)
                self._update(data)
            except:
                continue

    def _update(self, data):
        self.stats["frames"] += 1
        self.stats["lying"] += 1


    def stop_and_get(self) -> str:
        self.is_running = False
        duration = time.time() - self.start_time if self.start_time else 0
        s = self.stats
        text = (
            f"⏱️ Длительность: {duration//60:.0f} мин\n"
            f"📹 Кадров: {s['frames']}\n"
            f"🛌 Лёжа: {s['lying']}\n"
            f"🐾 Стояние: {s['standing']}\n"
        )
        # Сброс
        self.stats = {k: 0 for k in self.stats}
        self.start_time = None
        return text