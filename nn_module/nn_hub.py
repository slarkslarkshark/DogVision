from nn_module.nn_worker import NNWorker
import multiprocessing as mp
from loguru import logger


class NNHub:
    def __init__(
        self,
        general_image_queue: mp.Queue,
        kp_queue: mp.Queue,
        project_logger: logger,
        device: str,
    ):
        self.general_image_queue = general_image_queue
        self.kp_queue = kp_queue
        self.project_logger = project_logger
        self.device = device

        self.model: [NNWorker, None] = None
        self.processes = dict()


    def start_nn_processes(self):
        self.model = NNWorker(
            general_image_queue=self.general_image_queue,
            kp_queue=self.kp_queue,
            device=self.device,
        )
        process = mp.Process(
            target=self.model.start,
            args=((self.project_logger,)),
            daemon=True,
        )
        self.processes["dog_yolo_pose"] = process
        self.processes["dog_yolo_pose"].start()