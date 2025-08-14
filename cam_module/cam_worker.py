from __future__ import annotations
from multiprocessing import Queue, Value
import loguru
from help_tools.data_containers import FrameData
from .cam_reader import CameraReader
import cv2


class CameraWorker:
    """Class camera worker."""

    def __init__(
        self,
        camera_source: [int, str],
        cam_name: str,
        general_image_queue: Queue,
        control_frames_queue: Queue,
        get_control_frame,
        device: str,
    ) -> None:
        self.project_logger: [loguru.logger, None] = None

        self.general_image_queue: Queue = general_image_queue
        self.control_frames_queue: Queue = control_frames_queue
        self.get_control_frame = get_control_frame
        self.camera_source = camera_source
        self.cam_name = cam_name
        self.device = device

        self.camera_reader: [CameraReader, None] = None

    def get_frame_data(self) -> FrameData:
        frame_data: FrameData = self.camera_reader.get_frame_data

        return frame_data

    @staticmethod
    def preprocess_frame(frame, target_size=640):
        """
        Принимает кадр размером (720, 1280, 3), уменьшает до (360, 640, 3),
        затем добавляет черные полосы сверху и снизу, чтобы получить (640, 640, 3).

        Возвращает:
            padded_frame: кадр для инференса (640, 640, 3)
        """

        resized_frame = cv2.resize(frame, (640, 360))  # (width, height)

        pad_size = (target_size - resized_frame.shape[0]) // 2  # (640 - 360) // 2 = 140
        top_pad = pad_size
        bottom_pad = target_size - resized_frame.shape[0] - top_pad

        padded_frame = cv2.copyMakeBorder(
            resized_frame,
            top=top_pad,
            bottom=bottom_pad,
            left=0,
            right=0,
            borderType=cv2.BORDER_CONSTANT,
            value=(0, 0, 0),
        )

        return padded_frame

    def processing(self, frame_data: FrameData):
        if frame_data:
            if self.get_control_frame.value:
                self.control_frames_queue.put(frame_data, timeout=1)
                self.get_control_frame.value = False
            elif not self.general_image_queue.full():
                frame_data.frame = CameraWorker.preprocess_frame(frame_data.frame)
                self.general_image_queue.put(frame_data)
                # self.project_logger.info(f"Putting frame from {frame_data.cam_name} into main queue.")
            else:
                # self.project_logger.critical("General queue is full.")
                del frame_data

    def start_camera_process(self, logger):
        self.project_logger = logger

        self.camera_reader: CameraReader = CameraReader(
            project_logger=self.project_logger,
            camera_source=self.camera_source,
            cam_name=self.cam_name,
        )

        self.camera_reader.start_capture()

        while not self.camera_reader.stopped:
            try:
                stream_frame_data: FrameData = self.get_frame_data()
                self.processing(stream_frame_data)
            except Exception as e:
                self.camera_reader.stop_capture()
                self.project_logger.exception(e)
