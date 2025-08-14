import multiprocessing as mp
from typing import Optional
from cam_module.cam_hub import CamHub
from help_tools.logger_worker import LoggerWorker
from nn_module.nn_hub import NNHub
import time


class ProcessManager:
    def __init__(self):
        self.project_logger = LoggerWorker().logger
        self.manager = mp.Manager()
        self.cam_hub: Optional[mp.Process] = None
        self.nn_hub: Optional[mp.Process] = None
        self.is_running = False
        self.general_image_queue = self.manager.Queue(maxsize=10)
        self.kp_queue = self.manager.Queue(maxsize=10)
        self.get_control_frame = self.manager.Value("b", False)
        self.control_frames_queue = self.manager.Queue(maxsize=10)

        self.device = "cpu"
        self.project_logger.info(f"""System works with {self.device}!""")

    def start_tracking(self):
        if self.is_running:
            return False

        self.cam_hub = CamHub(
            general_image_queue=self.general_image_queue,
            control_frames_queue=self.control_frames_queue,
            get_control_frame=self.get_control_frame,
            project_logger=self.project_logger,
            device=self.device,
        )
        self.nn_hub = NNHub(
            general_image_queue=self.general_image_queue,
            kp_queue=self.kp_queue,
            project_logger=self.project_logger,
            device=self.device,
        )

        self.nn_hub.start_nn_processes()
        time.sleep(2)
        self.cam_hub.start_camera_processes()

        self.is_running = True
        return True

    def stop_tracking(self):
        if not self.is_running:
            self.project_logger.warning("Tracking is not running.")
            return False

        try:
            self.project_logger.info("🛑 Stopping tracking...")

            # Остановка камер
            for name, proc in self.cam_hub.processes.items():
                if proc.is_alive():
                    self.project_logger.info(f"Terminating camera process: {name}")
                    proc.terminate()
                    proc.join(timeout=5)
                    if proc.is_alive():
                        proc.kill()
                        proc.join()

            # Остановка нейросетей
            for name, proc in self.nn_hub.processes.items():
                if proc.is_alive():
                    self.project_logger.info(f"Terminating NN process: {name}")
                    proc.terminate()
                    proc.join(timeout=5)
                    if proc.is_alive():
                        proc.kill()
                        proc.join()

            self.is_running = False
            self.project_logger.info("🛑 Tracking stopped.")
            return True

        except Exception as e:
            self.project_logger.error(f"Error during stop_tracking: {e}")
            return False
