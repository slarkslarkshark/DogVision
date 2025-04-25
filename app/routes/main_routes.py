from flask import Blueprint, render_template, Response
from utils.video_processing import generate_frames
from config import Config

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(Config.RTSP_URL),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
