from flask import Blueprint, jsonify, request
from config import Config
from .onvif import ONVIF

camera_bp = Blueprint("camera", __name__)

onvif = ONVIF(
    host=Config.CAMERA_IP,
    port=Config.ONVIF_PORT,
    user=Config.CAMERA_USER,
    passwd=Config.CAMERA_PASSWORD,
).activate()


@camera_bp.route("/control", methods=["POST"])
def control_camera():
    data = request.json
    direction = data.get("direction")
    if direction == "up":
        move_camera(pan=0, tilt=0.5)
    elif direction == "down":
        move_camera(pan=0.0, tilt=-0.5)
    elif direction == "left":
        move_camera(pan=-0.5, tilt=0.0)
    elif direction == "right":
        move_camera(pan=0.5, tilt=0.0)

    return (
        jsonify({"status": "success", "message": f"Control applied for {direction}"}),
        200,
    )


def move_camera(pan, tilt):
    """
    Перемещает камеру в заданном направлении.
    :param pan: Горизонтальное перемещение (-1.0 до 1.0)
    :param tilt: Вертикальное перемещение (-1.0 до 1.0)
    """
    request = onvif.ptz.create_type("ContinuousMove")
    request.ProfileToken = onvif.profile_token
    request.Velocity = {"PanTilt": {"x": pan, "y": tilt}}
    onvif.ptz.ContinuousMove(request)
