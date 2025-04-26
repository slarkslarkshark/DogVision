class Config:
    CAMERA_IP = "192.168.1.102"
    ONVIF_PORT = "8899"
    RTSP_PORT = "554"
    CAMERA_USER = "admin"
    CAMERA_PASSWORD = ""
    RTSP_URL = f"rtsp://{CAMERA_IP}:{RTSP_PORT}/live/ch00_1"
    HOST = None  # '0.0.0.0'
    PORT = None  # 5000
    DEBUG = False
