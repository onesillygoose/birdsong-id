# Raspberry Pi Bird Audio Detector

A Raspberry Pi-based environmental audio monitoring system that collects bird vocalizations for machine-learning-based species identification and long-term observation.

## Overview 
This project uses a Raspberry Pi Zero 2 W and an external microphone to continuously monitor local bird activity, record environmental audio, and upload recordings to a web-based processing system.

The Raspberry Pi sends audio recordings to the website through an API, where BirdNET processes the recordings to identify bird species and log detections. These data support long-term observations of bird activity and exploration of its correlations with temperature, time of day, and seasonal changes.

raspberry.py contains the Python code for the Raspberry Pi's audio monitoring, recording, and upload processes. Audio processing, species identification, and detection management are handled separately by the website.

View recorded detections at birdingwith.me/data.



