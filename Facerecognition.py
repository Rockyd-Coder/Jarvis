import cv2
import pyautogui
import pyttsx3
import time
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


def speak(text):
    """Use text-to-speech to speak the given text."""
    engine.say(text)
    engine.runAndWait()


recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')

# Load the face cascade
cascadePath = 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascadePath)

# Define font for displaying text
font = cv2.FONT_HERSHEY_COMPLEX

# Initialize pyttsx3 for text-to-speech
engine = pyttsx3.init()

# Ask for username and password
while True:
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")

    if (username.lower() == 'rajveer') and (password == 'Mygames@20000'):
        print("Login successful!")
        break
    else:
        print("Invalid username or password. Please try again.")

# Initialize and set video capture parameters
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(3, 640)  # Width
cam.set(4, 480)  # Height

# Define minimum window size
minW = int(0.1 * cam.get(3))
minH = int(0.1 * cam.get(4))

# Wait for 10 seconds before starting face recognition
print("Starting face recognition...")
time.sleep(5)

while True:
    ret, img = cam.read()

    if not ret:
        print("Failed to capture image")
        break

    # Convert the captured image to grayscale
    converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = faceCascade.detectMultiScale(
        converted_image,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(minW, minH),
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        predicted_id, accuracy = recognizer.predict(converted_image[y:y + h, x:x + w])

        accuracy_percentage = round(100 - accuracy)

        if accuracy < 100 and accuracy_percentage >= 60:
            id_name = "Rajveer"
            accuracy_text = f" {accuracy_percentage}%"
        else:
            id_name = "unknown"
            accuracy_text = f" {accuracy_percentage}%"

        # Display the name and accuracy on the image
        cv2.putText(img, str(id_name), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
        cv2.putText(img, str(accuracy_text), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

        # If the face matches with accuracy >= 60%, exit after displaying the name
        if accuracy_percentage >= 60:
            print(f"Verification successful: {id_name}")
            speak(f"Verification successful: {id_name}")
            pyautogui.press('esc')
            break

    # Show the image with the detected faces
    cv2.imshow('camera', img)

    k = cv2.waitKey(10) & 0xff
    if k == 27:  # Press 'ESC' to exit
        break

print("Thanks for using this program, have a good day.")
cam.release()
cv2.destroyAllWindows()
