from flask import Blueprint, jsonify, request
from onvif import ONVIFCamera
import time

camera_bp = Blueprint('camera', __name__)

# Настройки камеры
CAMERA_IP = "192.168.1.102"
CAMERA_PORT = 8899
CAMERA_USER = "admin"
CAMERA_PASSWORD = ""

# Подключение к камере
camera = ONVIFCamera(CAMERA_IP, CAMERA_PORT, CAMERA_USER, CAMERA_PASSWORD)
# Инициализация сервиса PTZ
ptz_service = camera.create_ptz_service()
media_service = camera.create_media_service()

# Получаем профиль камеры (необходим для PTZ-команд)
profiles = media_service.GetProfiles()
profile_token = profiles[0].token

@camera_bp.route('/control', methods=['POST'])
def control_camera():
    data = request.json
    direction = data.get('direction')

    if direction == 'up':
        move_camera(pan=0.2, tilt=1)
    elif direction == 'down':
        move_camera(pan=0.0, tilt=-0.5)
    elif direction == 'left':
        move_camera(pan=-0.5, tilt=0.0)
    elif direction == 'right':
        move_camera(pan=0.5, tilt=0.0)

    return jsonify({"status": "success", "message": f"Control applied for {direction}"}), 200

@camera_bp.route('/reset', methods=['POST'])
def reset_camera():
    stop_camera()
    return jsonify({"status": "success", "message": "Controls reset"}), 200

# Функция для перемещения камеры
def move_camera(pan, tilt):
    """
    Перемещает камеру в заданном направлении.
    :param pan: Горизонтальное перемещение (-1.0 до 1.0)
    :param tilt: Вертикальное перемещение (-1.0 до 1.0)
    :param zoom: Масштабирование (0.0 до 1.0)
    """
    request = ptz_service.create_type('ContinuousMove')
    request.ProfileToken = profile_token
    request.Velocity = {
        'PanTilt': {'x': pan, 'y': tilt}
    }
    ptz_service.ContinuousMove(request)


def stop_camera():
    request = ptz_service.create_type("Stop")
    request.ProfileToken = profile_token
    request.PanTilt = True
    request.Zoom = False
    ptz_service.Stop(request)