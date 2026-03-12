import cv2
import time

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def liveness_check():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not accessible")
        return False

    start_time = time.time()

    while True:
        ret, frame = cap.read()

        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        cv2.imshow("Liveness Check", frame)

        # If face detected for 3 seconds → success
        if len(faces) > 0 and time.time() - start_time > 3:
            cap.release()
            cv2.destroyAllWindows()
            return True

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return False