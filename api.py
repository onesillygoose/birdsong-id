from flask import Flask, request
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime
import threading
import json
import os
from flask_sqlalchemy import SQLAlchemy #remeber to add these to the requirements too
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
db = SQLAlchemy(app)
api = Api(app)

class BirdModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    species = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    # timestamp = i will do this later ig
    recording_session = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Bird(species = {self.species}, confidence = {self.confidence})"
        
with app.app_context():
    db.create_all()    

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
            date=datetime.now(), #yeah i will have to work on time again
            min_conf=0.25,
        )
        recording.analyze()
        
        high_conf_results = [d for d in recording.detections if d["confidence"] > 0.1]

        if high_conf_results:
            with app.app_context():
                for result in high_conf_results:
                    new_detection = BirdModel(
                        species=result["species"],
                        confidence=result["confidence"],
                        recording_session=os.path.basename(filepath)
                    )
                    db.session.add(new_detection)
                db.session.commit()

        print(f"Results saved for {filepath}!")

        for d in high_conf_results:
            print(f"{d['species']} ({d['confidence']:.2f})")

        print("results saved")    

    except Exception as e:
        print(f"Error: {e}")



@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("file")

    if not files or files[0].filename == "":
        return {"status": "error", "message": "No file part"}, 400
    if "file" not in request.files:
        return {"status": "error", "message": "No file part"}, 400
    
    saved_files = []

    for file in files:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        saved_files.append(filepath)
        print("Received:", file.filename)   
        #threading.Thread(target=process_audio, args=(filepath,)).start()
        process_audio(filepath)
    return {"status": "ok", "files_received": len(saved_files)}
    
@app.route("/results")
def results():
    try:
        all_birds = BirdModel.query.all()
        return [
            {
                "species": b.species,
                "confidence": b.confidence,
                "recording_session": b.recording_session
            } 
            for b in all_birds
        ]   
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



