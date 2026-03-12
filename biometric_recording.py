import cv2
import time
import threading
import sounddevice as sd
from scipy.io.wavfile import write
from moviepy import VideoFileClip, AudioFileClip

VIDEO_FILE = "recordings/session_video.mp4"
AUDIO_FILE = "recordings/session_audio.wav"
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)

def record_audio(duration=60, fs=44100):
    print("Recording audio...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(AUDIO_FILE, fs, audio)
    print("Audio saved:", AUDIO_FILE)


def record_video_with_liveness():

    cap = cv2.VideoCapture(0)

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(VIDEO_FILE, fourcc, 20.0, (640, 480))

    blink_count = 0
    eyes_detected_prev = True

    start_time = time.time()

    print("Recording started...")

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:

            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]

            eyes = eye_cascade.detectMultiScale(roi_gray)

            if len(eyes) == 0 and eyes_detected_prev:
                blink_count += 1
                print("Blink detected!")

            eyes_detected_prev = len(eyes) > 0

            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

        cv2.putText(frame, f"Blinks: {blink_count}",
                    (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0,255,0),
                    2)

        out.write(frame)

        cv2.imshow("Live Recording", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

        if time.time() - start_time > 60:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("Video saved:", VIDEO_FILE)

def merge_audio_video():

    video_file = "recordings/session_video.mp4"
    audio_file = "recordings/session_audio.wav"
    final_file = "recordings/final_evidence.mp4"

    print("Merging audio and video...")

    video = VideoFileClip(video_file)
    audio = AudioFileClip(audio_file)

    final = video.with_audio(audio)

    final.write_videofile(final_file, codec="libx264", audio_codec="aac")

    print("Final evidence created:", final_file)

    return final_file

def start_biometric_recording():

    audio_thread = threading.Thread(target=record_audio)
    audio_thread.start()

    record_video_with_liveness()

    audio_thread.join()

    final_file = merge_audio_video()

    print("Recording complete.")

    return final_file