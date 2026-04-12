import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import urllib.request
import os

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

def download_model():
    model_path = "face_landmarker.task"
    if not os.path.exists(model_path):
        print("Downloading face model...")
        url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
        urllib.request.urlretrieve(url, model_path)
        print("Done!")
    return model_path

def get_eye_ratio(landmarks, eye_points, w, h):
    coords = []
    for p in eye_points:
        x = int(landmarks[p].x * w)
        y = int(landmarks[p].y * h)
        coords.append((x, y))
    v1 = abs(coords[1][1] - coords[5][1])
    v2 = abs(coords[2][1] - coords[4][1])
    hz = abs(coords[0][0] - coords[3][0])
    if hz == 0:
        return 0
    return (v1 + v2) / (2.0 * hz)

def check_liveness(blink_count_needed=2, time_limit=10):
    model_path = download_model()
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    detector = vision.FaceLandmarker.create_from_options(options)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    blink_count = 0
    eye_closed = False
    start_time = time.time()
    result = False
    print("Camera opening... minimize this window!")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera error!")
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        output = detector.detect(mp_image)
        time_left = int(time_limit - (time.time() - start_time))

        if output.face_landmarks:
            landmarks = output.face_landmarks[0]
            lr = get_eye_ratio(landmarks, LEFT_EYE, w, h)
            rr = get_eye_ratio(landmarks, RIGHT_EYE, w, h)
            avg = (lr + rr) / 2
            if avg < 0.2:
                if not eye_closed:
                    eye_closed = True
            else:
                if eye_closed:
                    blink_count += 1
                    eye_closed = False
                    print(f"Blink! Total: {blink_count}")
            cv2.putText(frame, f"Blinks: {blink_count}/{blink_count_needed}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Time: {time_left}s", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.putText(frame, "Blink naturally!", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "No face - move closer!", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        if blink_count >= blink_count_needed:
            cv2.putText(frame, "LIVENESS CONFIRMED!", (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            cv2.imshow("Liveness Check", frame)
            cv2.waitKey(1500)
            result = True
            break

        if time_left <= 0:
            cv2.putText(frame, "FAKE DETECTED!", (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            cv2.imshow("Liveness Check", frame)
            cv2.waitKey(1500)
            result = False
            break

        cv2.imshow("Liveness Check", frame)
        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    return result

if __name__ == "__main__":
    is_live = check_liveness(blink_count_needed=2, time_limit=10)
    if is_live:
        print("REAL PERSON CONFIRMED!")
    else:
        print("FAKE DETECTED!")