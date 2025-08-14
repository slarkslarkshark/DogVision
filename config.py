import os
from ast import literal_eval
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class GeneralConfig:
    """Class for read config file."""
    LOGS_PATH: Path = Path("logs/")
    TIMEZONE: str = "Asia/Novosibirsk"
    TG_BOT_TOKEN: str = os.getenv("TG_BOT_TOKEN")
    TG_USER_LIST: list = literal_eval(os.getenv("TG_USER_LIST"))


class CamConfig:
    cam_sources = {
        "camera_ip_1": "rtsp://192.168.1.104/live/ch00_0",
    }
    FPS = 1


class NNConfig:
    model_path = "./models/yolo11n-pose_harry.pt"
    box_conf = 0.5
