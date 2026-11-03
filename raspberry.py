import os
import time
import wave
import requests
import pyaudio
from datetime import datetime

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024
RECORD_SECONDS = 15

FOLDER_NAME = "/home/pi/bird_song_project/song_recordings"
URL = "https://birdingwith.me/upload"

os.makedirs(FOLDER_NAME, exist_ok=True)
audio = pyaudio.PyAudio()

def record_audio():
    stream = None
    try:
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=0,
            frames_per_buffer=CHUNK
        )

        print("recording...")
        frames = []

        for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

        print("done recording.")
        return frames
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()

try:
    print("24/7 recording session started:", datetime.now())
    while True:
        try:
            frames = record_audio()
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"recording_{timestamp}.wav"
            file_path = os.path.join(FOLDER_NAME, file_name)

            with wave.open(file_path, "wb") as wave_file:
                wave_file.setnchannels(CHANNELS)
                wave_file.setsampwidth(audio.get_sample_size(FORMAT))
                wave_file.setframerate(RATE)
                wave_file.writeframes(b"".join(frames))

            print(f"saved as: {file_path}")

            try:
                with open(file_path, "rb") as f:
                    response = requests.post(URL, files={"file": f}, timeout=30)

                print("upload status:", response.status_code)

                if response.ok:
                    print("upload successful.")
                    os.remove(file_path)
                    print("local file deleted.")
                else:
                    print("upload failed. keeping local file.")
            except requests.RequestException as e:
                print("upload failed:", e)
                print("keeping local file.")

        except Exception as script_err:
            print("Internal loop error:", script_err)

        time.sleep(5)

except Exception as main_err:
    print("Main session error:", main_err)

finally:
    audio.terminate()
    print("recording session ended:", datetime.now())
