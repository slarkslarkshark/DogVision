import cv2
import time

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

def get_fps():
    global fps_value
    return round(fps_value, 2)
