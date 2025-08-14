class Config:
    CAMERA_IP = "192.168.1.104"
    ONVIF_PORT = "8899"
    RTSP_PORT = "554"
    CAMERA_USER = "admin"
    CAMERA_PASSWORD = ""
    RTSP_URL = f"rtsp://{CAMERA_IP}:{RTSP_PORT}/live/ch00_1"
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False
