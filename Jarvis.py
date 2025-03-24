import os
import subprocess
import pyttsx3
import speech_recognition as sr
import psutil
import time
import pyautogui
import pyjokes
import requests
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import random
import string
import pywhatkit as kit
import qrcode
import credentials as Credentials
import speedtest
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pygame import mixer
from bs4 import BeautifulSoup
import wikipedia
import webbrowser
import six
import nltk
from nltk.tokenize import word_tokenize
import pandas

wake_phrases = ["jarvis", "wake up", "hello jarvis"]
sleep_phrases = ["goodbye", "go to sleep", "sleep mode", "see you later", "shutdown jarvis", "bye", "rest now"]

# Mailtrap settings (Replace with your Mailtrap credentials)
MAILTRAP_SMTP_SERVER = 'smtp.mailtrap.io'
MAILTRAP_SMTP_PORT = 587
MAILTRAP_USERNAME = 'rocky'  # Replace with your Mailtrap username
MAILTRAP_PASSWORD = 'mygames@20000'  # Replace with your Mailtrap password
FROM_EMAIL = 'jarvis@mailtrap.io'  # Mailtrap's dummy email

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Global variables for Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'path/to/service.json'  # Update this with your service account file

def speak(text):
    """Use text-to-speech to speak the given text."""
    engine.say(text)
    engine.runAndWait()

def take_command():
    """Listen to user command and recognize speech."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in').lower()
        print(f"User said: {query}")
        return query
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Please repeat.")
        return None
    except sr.RequestError:
        speak("Sorry, I'm having trouble with the service.")
        return None

def perform_task(command):
    # 30 different question starters for Wikipedia search
    question_starters = ["who is", "what is", "where is", "when is", "why", "how to", "what if", "what are", "define", 
                         "tell me about", "explain", "give me information on", "list", "describe", "history of", 
                         "biography of", "who invented", "what does", "what happened", "who created", "who discovered",
                         "when was", "where can I find", "what's the", "how did", "how much", "how many", "who wrote", 
                         "who directed", "who starred in"]
    
    # Wikipedia search for specific question starters
    if any(starter in command.lower() for starter in question_starters):
        query = command.lower().strip()
        try:
            print(f"Searching Wikipedia for: {query}")
            result = wikipedia.summary(query, sentences=3)
            print(f"Result from Wikipedia: {result}")
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"Multiple results found for {query}. Options: {e.options}")
        except Exception as e:
            print(f"Error fetching Wikipedia result: {e}")
    
    # YouTube video search
    elif 'play video on youtube' in command.lower():
        video_name = command.lower().replace('play video on youtube', '').strip()
        if video_name:
            print(f"Playing {video_name} on YouTube...")
            kit.playonyt(video_name)
        else:
            print("Please specify the video name to search on YouTube.")
    
    # Google search
    elif 'search on google' in command.lower():
        search_query = command.lower().replace('search on google', '').strip()
        if search_query:
            print(f"Searching Google for: {search_query}")
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
        else:
            print("Please specify the search query.")

    # Play random music from a directory
    elif 'play music' in command.lower():
        music_dir = "path_to_your_music_directory"  # Replace with your music folder path
        songs = os.listdir(music_dir)
        random_song = random.choice(songs)
        print(f"Playing random song: {random_song}")
        mixer.init()
        mixer.music.load(os.path.join(music_dir, random_song))
        mixer.music.play()

    # Play music on Spotify
    elif 'play song on spotify' in command.lower():
        song_name = command.lower().replace('play song on spotify', '').strip()
        if song_name:
            print(f"Playing {song_name} on Spotify...")
            # Spotify API credentials (Make sure to set up Spotify Developer credentials)
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="your_client_id",
                                                           client_secret="your_client_secret",
                                                           redirect_uri="your_redirect_uri",
                                                           scope="user-read-playback-state,user-modify-playback-state"))
            results = sp.search(q=song_name, limit=1)
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                sp.start_playback(uris=[track_uri])
                print(f"Playing {song_name} on Spotify.")
            else:
                print(f"Song '{song_name}' not found on Spotify.")
    
    # Open application
    elif 'open' in command.lower():
        app_name = command.lower().replace('open', '').strip()
        open_application(app_name)

# Function to open an application using the system command
def open_application(app_name):
    """Open an application using the system command."""
    try:
        os.system(f"start {app_name}")
        print(f"Opening {app_name}")
    except Exception as e:
        print(f"Error opening {app_name}: {e}")
        

def close_application(app_name):
    """Close an application if it's running."""
    for proc in psutil.process_iter(['pid', 'name']):
        if app_name.lower() in proc.info['name'].lower():
            os.kill(proc.info['pid'], 9)
            print(f"Closing {app_name}")
            speak(f"Closing {app_name}")
            return
    speak(f"{app_name} is not running.")

def create_and_save_file(app_name):
    """Create and save a file for the specified application type."""
    file_extensions = {
        'word': '.docx',
        'excel': '.xlsx',
        'powerpoint': '.pptx'
    }
    
    extension = file_extensions.get(app_name.lower(), '')
    default_location = os.path.join(os.path.expanduser("~"), "Desktop")

    try:
        import win32com.client as win32
        if app_name.lower() == 'word':
            app = win32.gencache.EnsureDispatch('Word.Application')
            doc = app.Documents.Add()
        elif app_name.lower() == 'excel':
            app = win32.gencache.EnsureDispatch('Excel.Application')
            doc = app.Workbooks.Add()
        elif app_name.lower() == 'powerpoint':
            app = win32.gencache.EnsureDispatch('PowerPoint.Application')
            doc = app.Presentations.Add()
        else:
            print(f"Unsupported application: {app_name}")
            speak(f"Unsupported application: {app_name}")
            return
        
        speak(f"Please tell me the name for the new {app_name} file.")
        file_name = take_command()
        
        if file_name:
            full_path = os.path.join(default_location, f"{file_name}{extension}")
            
            if app_name.lower() == 'word':
                doc.SaveAs(full_path)
                doc.Close()
            elif app_name.lower() == 'excel':
                doc.SaveAs(full_path)
                doc.Close()
            elif app_name.lower() == 'powerpoint':
                doc.SaveAs(full_path)
                doc.Close()
            
            app.Quit()
            print(f"File has been saved as {full_path}")
            speak(f"Your {app_name} file has been saved as {file_name}.")
        else:
            speak("No name provided. File creation canceled.")
    except Exception as e:
        speak(f"An error occurred: {e}")

def handle_notepad():
    """Open Notepad and write text as per user's command."""
    open_application('notepad')
    speak("Please tell me what to write.")
    text = take_command()
    if text:
        pyautogui.typewrite(text)
        speak("Text has been written.")

def draw_in_paint(shape, color):
    """Draw the specified shape and color in Paint."""
    pyautogui.click(100, 100)  # Click to make sure Paint is active
    time.sleep(1)

    color_picker = {'red': (150, 300), 'blue': (200, 300), 'green': (250, 300), 'yellow': (300, 300), 'black': (350, 300)}
    if color in color_picker:
        pyautogui.click(*color_picker[color])
    
    shape_tool = {'line': (100, 400), 'rectangle': (150, 400), 'ellipse': (200, 400), 'triangle': (250, 400)}
    if shape in shape_tool:
        pyautogui.click(*shape_tool[shape])
        pyautogui.moveTo(400, 400)  # Move to draw the shape
        pyautogui.mouseDown()
        pyautogui.moveTo(500, 500)  # Draw the shape
        pyautogui.mouseUp()
    
def open_paint_and_draw():
    """Open Paint and perform drawing based on user's command."""
    open_application('paint')
    speak("Please tell me what you want to draw and color.")
    command = take_command()

    if command:
        parts = command.split()
        shape = None
        color = None
        
        if 'rectangle' in parts:
            shape = 'rectangle'
        elif 'circle' in parts or 'ellipse' in parts:
            shape = 'ellipse'
        elif 'line' in parts:
            shape = 'line'
        elif 'triangle' in parts:
            shape = 'triangle'
        elif 'square' in parts:
            shape = 'square'
            
        if 'red' in parts:
            color = 'red'
        elif 'blue' in parts:
            color = 'blue'
        elif 'green' in parts:
            color = 'green'
        elif 'yellow' in parts:
            color = 'yellow'
        elif 'black' in parts:
            color = 'black'

        if shape and color:
            draw_in_paint(shape, color)
            speak(f"Drew a {shape} in {color}.")
        else:
            speak("I didn't understand what to draw or color.")

def weather_update(location):
    """Provide weather update for the given location."""
    API_KEY = '69bf0a590576448ed0bfd804ac2b2694'
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    url = base_url + "q=" + location + "&appid=" + API_KEY
    response = requests.get(url)
    data = response.json()
    if data["cod"] != "404":
        main = data["main"]
        weather = data["weather"][0]
        temperature = round(main["temp"] - 273.15, 2)
        description = weather["description"]
        speak(f"The temperature in {location} is {temperature}°C with {description}.")
    else:
        speak("Location not found.")

def manage_calendar(query):
    """Manage Google Calendar based on user query."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(SERVICE_ACCOUNT_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    
    if 'create' in query:
        speak("What event should I create?")
        event_summary = take_command()
        if event_summary:
            event = {
                'summary': event_summary,
                'start': {
                    'dateTime': '2024-09-14T09:00:00-07:00',
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': '2024-09-14T17:00:00-07:00',
                    'timeZone': 'America/Los_Angeles',
                },
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            speak(f"Event created: {event.get('htmlLink')}")
        else:
            speak("Event details not provided.")
    elif 'list' in query:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            speak('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            speak(f"{event['summary']} at {start}")

def jokes():
    """Tell a joke."""
    joke = pyjokes.get_joke()
    speak(joke)

def check_and_run_scripts():
    """Check the 'Samples' folder and run scripts accordingly."""
    samples_folder = 'Samples'
    if not os.path.exists(samples_folder):
        os.makedirs(samples_folder)

    files = os.listdir(samples_folder)
    if not files:
        print("No files found in 'Samples'. Running setup scripts.")
        speak("No files found in 'Samples'. Running setup scripts.")
        
        # Run scripts
        subprocess.run(['python', 'Sample generator.py'])
        subprocess.run(['python', 'Model Trainer.py'])
        subprocess.run(['python', 'Facerecognition.py'])
        
        # Prompt for credentials
        speak("Please create a username and password.")
        username = input("Enter username: ")
        password = input("Enter password: ")
        
        credentials_df = pd.DataFrame({
            'username': [username],
            'password': [password]
        })
        credentials_df.to_csv('credentials.txt', index=False)
        
        speak("Credentials saved. Starting Jarvis.")
    else:
        print("Files found in 'Samples'. Running Facerecognition.")
        speak("Files found in 'Samples'. Running Facerecognition.")
        subprocess.run(['python', 'Facerecognition.py'])
    
    start_jarvis()

def start_jarvis():
    
    speak("Access Granted.")
    speak("Initializing Jarvis")
    speak("Starting all system applications")
    speak("Installing and checking all drivers")
    speak("Calibrating and examining all the core processors")
    speak("Checking the internet connection")
    speak("Wait a moment, Sir")
    speak("All drivers are up and running")
    speak("All systems have been activated")
    speak("Now I am online")
    
    print("Access Granted.")
    print("Initializing Jarvis")
    print("Starting all system applications")
    print("Installing and checking all drivers")
    print("Calibrating and examining all the core processors")
    print("Checking the internet connection")
    print("Wait a moment, Sir")
    print("All drivers are up and running")
    print("All systems have been activated")
    print("Now I am online")
    
    while True:
        command = take_command()
        if command:
            if 'open' in command:
                if 'word' in command:
                    create_and_save_file('word')
                elif 'excel' in command:
                    create_and_save_file('excel')
                elif 'powerpoint' in command:
                    create_and_save_file('powerpoint')
                elif 'notepad' in command:
                    handle_notepad()
                elif 'paint' in command:
                    open_paint_and_draw()
                else:
                    open_application(command.replace('open', '').strip())
            elif 'close' in command:
                close_application(command.replace('close', '').strip())
            elif 'weather' in command:
                location = command.split('in')[-1].strip()
                weather_update(location)
            elif 'calendar' in command:
                manage_calendar(command)
            elif 'joke' in command:
                jokes()
            elif 'exit' in command or 'quit' in command:
                speak("Goodbye!")
                break
            else:
                speak("I didn't understand that command.")
        else:
            speak("No command recognized.")
def micro_tasks(self, command):
    if any(phrase in command.lower() for phrase in wake_phrases):
        print("Jarvis is awake!")
        return

   
    if any(phrase in command.lower() for phrase in sleep_phrases):
        print("Jarvis is sleeping, but the code is still running.")
        time.sleep(3)
        return

    # Volume control commands
    if 'volume up' in command.lower():
        pyautogui.press("volumeup")
        print("Volume increased.")
    elif 'volume down' in command.lower():
        pyautogui.press("volumedown")
        print("Volume decreased.")
    elif 'mute' in command.lower():
        pyautogui.press("volumemute")
        print("Volume muted.")
    elif 'unmute' in command.lower():
        pyautogui.press("volumeup")
        print("Volume unmuted.")

    # Speed test command
    elif 'speed test' in command.lower():
        print("Performing speed test...")
        st = speedtest.Speedtest()
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        print(f"Download Speed: {download_speed:.2f} Mbps")
        print(f"Upload Speed: {upload_speed:.2f} Mbps")

    # Press Windows button and search
    elif 'press windows' in command.lower():
        pyautogui.press('win')
        print("Windows key pressed.")

    # Open a file based on the given name
    elif 'open' in command.lower():
        file_name = command.lower().replace("open", "").strip()
        try:
            os.startfile(file_name)
            print(f"Opening file: {file_name}")
        except FileNotFoundError:
            print(f"File '{file_name}' not found.")

    # QR code generation
    elif 'qr code' in command.lower() or 'create qr' in command.lower():
        print("What do you want to create a QR code for? (text, link, file)")
        qr_type = input("Enter QR code type: ").lower()

        if qr_type == 'text':
            text = input("Enter the text for the QR code: ")
            qr = qrcode.make(text)
            qr.save("text_qr_code.png")
            print("QR code for text created and saved as 'text_qr_code.png'.")
        elif qr_type == 'link':
            link = input("Enter the link for the QR code: ")
            qr = qrcode.make(link)
            qr.save("link_qr_code.png")
            print("QR code for link created and saved as 'link_qr_code.png'.")
        elif qr_type == 'file':
            file_path = input("Enter the file path for the QR code: ")
            if os.path.exists(file_path):
                qr = qrcode.make(file_path)
                qr.save("file_qr_code.png")
                print(f"QR code for file '{file_path}' created and saved as 'file_qr_code.png'.")
            else:
                print(f"File '{file_path}' not found.")
        else:
            print("Invalid QR code type.")

    # WhatsApp message command
    elif 'send a message to' in command.lower():
        self.whatsapp(command)

    else:
        print("Command not recognized.")

# WhatsApp message handling
def whatsapp(self, command):
    try:
        # Extract the name or group from the command
        command = command.replace('send a message to', '').strip()
        
        # Search for the contact in the database
        name, numberID, found = self.SearchCont(command)
        
        if found:
            print(f"Contact found: {name}, ID: {numberID}")
            self.talk(f'Boss, what message do you want to send to {name}?')
            
            # Get the message to be sent
            message = self.take_Command()
            
            # Get current time for scheduling
            hour = int(datetime.datetime.now().hour)
            minute = int(datetime.datetime.now().minute) + 1  # Adds a minute to ensure it is sent
            
            print(f"Sending message at: {hour}:{minute}")
            
            # Check if it's a group or individual message
            if "group" in command.lower():
                kit.sendwhatmsg_to_group(numberID, message, hour, minute)
            else:
                kit.sendwhatmsg(numberID, message, hour, minute)
                
            self.talk("Boss, the message has been sent.")
        
        else:
            # Contact not found, ask to add new contact
            self.talk(f'Boss, the contact {command} is not found in our database. Shall I add the contact?')
            add_or_not = self.take_Command().lower()
            print(f"User response: {add_or_not}")
            
            # User confirms to add a contact
            if "yes" in add_or_not or "add" in add_or_not or "yeah" in add_or_not or "yah" in add_or_not:
                self.AddContact()
            else:
                self.talk('Okay Boss, not adding the contact.')
    
    except Exception as e:
        # Catch any errors and print/log them
        print(f"Error occurred: {e}")
        self.talk("An error occurred while sending the message. Please try again.")
if __name__ == "__main__":
    check_and_run_scripts()
