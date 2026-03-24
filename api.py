from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
import os
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime
import threading
import json

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return("Bird Server")

analyzer = Analyzer()

def process_audio(filepath):
    try:
        recording = Recording(
            analyzer,
            filepath,
            lat=32.4,
            lon=-81.8,
            date=datetime.now(),
            min_conf=0.25,
        )
        recording.analyze()
        
        high_conf_results = [d for d in recording.detections if d["confidence"] > 0.8]

        if not high_conf_results:
            print(f"No high-confidence detections in {filepath}")
            return  

        #save high-confidence results
        with open(filepath + ".json", "w") as f:
            json.dump(high_conf_results, f, indent=4)

        print(f"Results saved for {filepath}!")

        # Print detections
        for d in high_conf_results:
            print(f"{d['species']} ({d['confidence']:.2f})")

        print("results saved")    

    except Exception as e:
        print("Error processing audio:", e)



@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return {"status": "error", "message": "No file part"}, 400
    
    file = request.files["file"]

    if file.filename == "":
        return {"status": "error", "message": "No selected file"}, 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    print("Recieved:", file.filename)

    threading.Thread(target=process_audio, args=(filepath,)).start()
    
    return {"status": "ok"}

if __name__ == "__main__":
    app.run()

