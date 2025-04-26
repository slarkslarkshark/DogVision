from flask import Flask
from config import Config
from routes.main_routes import main_bp
from routes.metrics_routes import metrics_bp
from routes.camera_controls import camera_bp

app = Flask(__name__)

app.register_blueprint(main_bp)
app.register_blueprint(metrics_bp)
app.register_blueprint(camera_bp, url_prefix="/camera")

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
