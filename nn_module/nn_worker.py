from multiprocessing import Queue
from help_tools.data_containers import FrameData, KeyPointsData
from queue import Empty
import loguru
from help_tools.logger_worker import LoggerWorker
from ultralytics import YOLO
from config import NNConfig as cfg
from numpy import float16


class NNWorker:
    def __init__(
        self,
        general_image_queue: [Queue, None],
        kp_queue: [Queue, None],
        device: str,
        model=None,
    ):
        self.general_image_queue = general_image_queue
        self.kp_queue = kp_queue

        self.device = device

        self.project_logger: [loguru.logger, None] = None
        self.model = model

    def __prepare_results(self, results, timestamp, cam_name):
        prepared_results = None
        if results:
            res = results[0]
            if res.boxes:
                conf = res.boxes.conf.cpu().numpy()[0]
                if res.keypoints is not None and conf > cfg.box_conf:
                    keypoints = res.keypoints.data.cpu().numpy()[0].astype(float16)
                    boxes = res.boxes.data.cpu().numpy()[0].astype(float16)
                    prepared_results = KeyPointsData(
                        cam_name=cam_name,
                        keypoints=keypoints,
                        boxes=boxes,
                        timestamp=timestamp,
                    )
        return prepared_results

    def predict(self, frame):
        results = self.model.predict(frame.frame, verbose=False)
        results = self.__prepare_results(results, frame.timestamp, frame.cam_name)
        return results

    def processing(self):
        frame: FrameData = self.general_image_queue.get(timeout=0.1)
        keypoints = self.predict(frame)
        self.kp_queue.put(keypoints)
        # self.project_logger.info("""Putting keypoints on the queue.""")

    def start(self):
        self.project_logger = LoggerWorker().logger

        if self.model is None:
            self.model = YOLO(cfg.model_path)

        self.project_logger.info("YOLO-pose model is on.")
        while True:
            try:
                self.processing()
            except Empty:
                pass
