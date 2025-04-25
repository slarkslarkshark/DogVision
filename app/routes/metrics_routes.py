from flask import Blueprint, jsonify
from utils.video_processing import get_fps

metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/metrics')
def metrics():
    return jsonify({"fps": get_fps()})
