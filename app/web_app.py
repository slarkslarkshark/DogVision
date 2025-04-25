from flask import Flask, Response, render_template
import cv2
import time

app = Flask(__name__)

fps_value = 0

def generate_frames(rtsp_url):
    global fps_value

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("Ошибка: Не удалось открыть видеопоток.")
        return

    frame_counter = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_counter += 1
        elapsed_time = time.time() - start_time
        if elapsed_time >= 1.0:
            fps_value = frame_counter / elapsed_time
            frame_counter = 0
            start_time = time.time()

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    rtsp_url = "rtsp://192.168.1.102:554/live/ch00_1"
    return Response(generate_frames(rtsp_url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/metrics')
def metrics():
    global fps_value
    return {
        "fps": round(fps_value, 2)
    }

if __name__ == '__main__':\
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)