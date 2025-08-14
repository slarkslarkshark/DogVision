from __future__ import annotations
from datetime import datetime
from queue import Queue, Empty
from threading import Thread
from typing import NoReturn
import os
import time

import cv2
import loguru

from help_tools.data_containers import FrameData


class CameraReader:
    """Class for take frames from camera."""

    _reconnection_attempts = 40

    def __init__(
        self,
        camera_source: [int, str],
        cam_name: str = "local",
        project_logger=None,
    ) -> None:
        self.project_logger: [loguru.Logger, None] = project_logger
        self.camera_source: [int, str] = camera_source
        self.cam_name: str = cam_name

        self.capture: [cv2.VideoCapture, None] = None
        self.frame_data_queue: Queue = Queue(maxsize=3) # only 3 frames per cam

        self.stopped = False
        self.reconnection = False

    def start_capture(self) -> None:
        self.capture: cv2.VideoCapture = cv2.VideoCapture(self.camera_source)

        if self.capture.isOpened():

            start_thread = Thread(target=self._capture_frames, daemon=True)
            start_thread.start()
        else:
            self.project_logger.info(
                f"Can't connect to camera {self.cam_name} "
                f"With source {self.camera_source}."
            )
            raise ValueError("Can't start frame capture.")

        self.project_logger.info(
            f"Connected to camera {self.cam_name} " f"With source {self.camera_source}."
        )

    def stop_capture(self) -> bool:
        self.stopped = True
        time.sleep(0.00005)

        return self.stopped

    @property
    def get_frame_data(self) -> FrameData:
        """Return FrameData object with info of frame."""
        try:
            return self.frame_data_queue.get(timeout=1)
        except Empty:
            pass

    def _capture_frames(self) -> NoReturn:
        while True:
            try:
                if self.stopped:
                    self.capture.release()
                    break
                if not self.reconnection:
                    captured, frame = self.capture.read()
                    if captured and frame is not None:
                        frame_data = FrameData(
                            cam_name=self.cam_name,
                            frame_exist=captured,
                            frame=frame,
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                        )
                        if not self.frame_data_queue.full():
                            self.frame_data_queue.put(frame_data, block=False)
                    else:
                        self._reconnect()
                else:
                    self._reconnect()

            except (cv2.error, Exception) as error:
                self.project_logger.error(error)
                self.project_logger.exception(error)
                self.project_logger.critical(f"{self.cam_name} exception")

    def _reconnect(self) -> bool:
        self.capture.release()

        reconnect_counter = 1

        while reconnect_counter < self._reconnection_attempts:

            self.project_logger.info(
                f"Reconnect to {self.cam_name} try: {reconnect_counter}"
            )
            time.sleep(0.5)

            if isinstance(self.camera_source, int):

                time.sleep(0.5)
                usb_ports = [
                    port[-1]
                    for port in os.listdir(os.path.join("/dev"))
                    if port.startswith("video") and port[-1].isdigit()
                ]

                for port in usb_ports:

                    self.capture = cv2.VideoCapture(int(port))
                    status = self.capture.isOpened()

                    if status:

                        self.captured, self.frame = self.capture.read()

                        self.project_logger.info(
                            f"Successful reconnect to {self.cam_name}."
                        )
                        return True

                reconnect_counter += 1

            if isinstance(self.camera_source, str):
                time.sleep(0.5)
                try:

                    self.capture = cv2.VideoCapture(self.camera_source, cv2.CAP_FFMPEG)
                    status = self.capture.isOpened()
                    captured, frame = self.capture.read()
                    if status and captured and frame is not None:
                        self.captured, self.frame = self.capture.read()

                        self.project_logger.info(
                            f"Successful reconnect to {self.cam_name}."
                        )
                        return True

                    reconnect_counter += 1

                except (AssertionError, ValueError):
                    self.capture.release()
                    reconnect_counter += 1
                    continue

        self.project_logger.info(f"Max try reconnect to {self.cam_name}.")
        if reconnect_counter > self._reconnection_attempts:
            os._exit(0)
        return False