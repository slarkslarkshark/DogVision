from __future__ import annotations
import loguru
import os

from pathlib import Path, PurePath
from config import GeneralConfig as cfg


class LoggerWorker:
    """Class logger worker."""

    def __init__(self) -> None:
        self._abs_path: Path = Path(__file__).parents[1]
        self.log_dir_path: Path = cfg.LOGS_PATH
        self.log_file_name: Path = Path("logs.log")
        self.abs_file_path: Path = Path(
            PurePath(self._abs_path, self.log_dir_path, self.log_file_name)
        )
        os.makedirs(self.abs_file_path.parent, exist_ok=True)
        self.logger: loguru.Logger = self._get_custom_logger()

    def _get_custom_logger(self) -> loguru.Logger:
        loguru.logger.add(
            self.abs_file_path,
            format="| {time:DD-MM-YYYY HH:mm:ss:SSS} | {level} | {message} | {module} |",
            encoding="utf-8",
            level="INFO",
            rotation="00:00",
            retention="1 month",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )
        return loguru.logger
