from dataclasses import dataclass, asdict
import numpy as np


@dataclass
class FrameData:
    """Data container for frame information."""

    cam_name: str
    frame_exist: bool
    frame: np.ndarray
    timestamp: str

    def get_data_as_dict(self):
        return asdict(self)


@dataclass
class KeyPointsData:
    """
    Data container for YOLO results.
    
    TODO: points names
    """

    cam_name: str
    keypoints: np.ndarray
    boxes: np.ndarray
    timestamp: str

    def get_data_as_dict(self):
        return asdict(self)
