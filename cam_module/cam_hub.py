from __future__ import annotations
import multiprocessing as mp
import loguru
from .cam_worker import CameraWorker
from config import CamConfig as cfg


class CamHub:
    def __init__(
        self,
        general_image_queue,
        control_frames_queue,
        get_control_frame,
        project_logger: loguru.Logger,
        device: str,
    ) -> None:

        self.general_image_queue = general_image_queue
        self.control_frames_queue = control_frames_queue
        self.get_control_frame = get_control_frame
        self.project_logger = project_logger
        self.processes: dict[str, mp.Process] = {}
        self.device = device

    def start_camera_processes(self):
        cameras_source: dict = cfg.cam_sources
        for camera_name, camera_id in cameras_source.items():
            stream: CameraWorker = CameraWorker(
                camera_source=camera_id,
                cam_name=camera_name,
                general_image_queue=self.general_image_queue,
                control_frames_queue=self.control_frames_queue,
                get_control_frame=self.get_control_frame,
                device=self.device,
            )

            process = mp.Process(
                target=stream.start_camera_process,
                args=((self.project_logger,)),
                daemon=True,
            )
            self.processes[camera_name] = process
            self.processes[camera_name].start()
