from datetime import datetime, date


class StateManager:
    def __init__(self, project_logger=None):
        self.is_tracking = False
        self.tracking_start_time = None
        self.tracking_disabled_today = False
        self.last_reset_date = date.today()
        self.project_logger = project_logger

    def _ensure_daily_reset(self):
        """Сброс флага 'без отслеживания' в начале нового дня"""
        today = date.today()
        if today > self.last_reset_date:
            self.tracking_disabled_today = False
            self.last_reset_date = today

    def start_tracking(self):
        self._ensure_daily_reset()
        self.is_tracking = True
        self.tracking_start_time = datetime.now()

    def stop_tracking(self):
        self.is_tracking = False
        self.tracking_start_time = None

    def disable_tracking_today(self):
        self._ensure_daily_reset()
        self.tracking_disabled_today = True
