import cv2
import numpy as np
from PIL import Image
import os
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


def speak(text):
    """Use text-to-speech to speak the given text."""
    engine.say(text)
    engine.runAndWait()

# Path to the samples directory
path = 'C:/Users/HITMAN/Jarvis/Samples'

# Create LBPH face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Load the Haar Cascade for face detection
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def Images_And_Labels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        gray_img = Image.open(imagePath).convert('L')
        img_arr = np.array(gray_img, 'uint8')

        try:
            # Extract ID from the image file name
            id = int(os.path.split(imagePath)[-1].split(".")[1])
        except (IndexError, ValueError) as e:
            speak(f"Error processing file {imagePath}: {e}")
            continue
        
        # Detect faces in the image
        faces = detector.detectMultiScale(img_arr)

        for (x, y, w, h) in faces:
            faceSamples.append(img_arr[y:y+h, x:x+w])
            ids.append(id)

    return faceSamples, ids

("Training faces. It will take a few seconds. Wait...")

faces, ids = Images_And_Labels(path)
if len(faces) == 0 or len(ids) == 0:
    speak("No faces or IDs were detected. Please check the images and their formats.")
else:
    recognizer.train(faces, np.array(ids))

    # Create the trainer directory if it doesn't exist
    if not os.path.exists('trainer'):
        os.makedirs('trainer')

    # Save the trained model
    recognizer.write('trainer/trainer.yml')

    speak("Model trained. Now we can recognize your face.")
