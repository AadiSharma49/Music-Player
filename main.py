import json
import sys
import os
import random
import pygame  # ✅ Using pygame.mixer for better sound control
import speech_recognition as sr
import pyttsx3
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.icon_definitions import md_icons 
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineAvatarListItem
import pyrebase
from kivymd.uix.dialog import MDDialog

# ✅ Initialize Pygame Mixer
pygame.mixer.init()

# ✅ SCREEN MANAGER
class WindowManager(ScreenManager):
    pass

import os
import sys
config_path = os.path.join(os.path.dirname(__file__), "config.json")

if not os.path.exists(config_path):
    raise FileNotFoundError("config.json is missing! Place it in the same folder as the EXE.")

with open(config_path) as f:
    firebase_config = json.load(f)


firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# ✅ Initialize Voice Assistant
engine = pyttsx3.init()

import os
import sys

# Get the absolute path (Works in both EXE and script mode)
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # If running as EXE, get the correct path
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

SONGS_FOLDER = resource_path("assets/songs")

# Ensure the folder exists
if not os.path.exists(SONGS_FOLDER):
    os.makedirs(SONGS_FOLDER)  # ✅ Create it if missing
# ✅ Path to MP3 songs folder
SONGS_FOLDER = "assets/songs/"
current_song_index = 0  # Track current song index
song_list = []  # Store all songs
paused_position = 0  # ✅ Store paused position


def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()


def listen():
    """Listen for voice commands."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio).lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "Speech recognition service is down."


def list_local_songs():
    """Get the list of MP3 songs from the local folder."""
    global song_list
    song_list = [file for file in os.listdir(SONGS_FOLDER) if file.endswith(".mp3")]
    return song_list


class MusicSystemApp(MDApp):
    def build(self):
        
        return Builder.load_string(KV)

    def on_start(self):
        """Initialize songs when app starts"""
        list_local_songs()

    def stop_current_song(self):
        """Stop the currently playing song and save position."""
        global paused_position
        if pygame.mixer.music.get_busy():
            paused_position = pygame.mixer.music.get_pos()  # ✅ Save paused position
            pygame.mixer.music.stop()
            speak("Song stopped.")

    def play_song(self, song_name):
        """Stop the previous song and play the new one."""
        global paused_position
        self.stop_current_song()  # Stop any currently playing song

        song_path = os.path.join(SONGS_FOLDER, song_name)
        if os.path.exists(song_path):
            speak(f"Playing {song_name}")
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play(start=paused_position / 1000.0)  # ✅ Resume from stop
            paused_position = 0  # Reset paused position
        else:
            speak("Song not found.")

    def play_random_song(self):
        """Play a random song when user clicks play."""
        global current_song_index
        if song_list:
            current_song_index = random.randint(0, len(song_list) - 1)
            self.play_song(song_list[current_song_index])
        else:
            speak("No songs found in the folder.")

    def resume_song(self):
        """Resume the song from where it was stopped."""
        global paused_position
        if paused_position > 0:
            pygame.mixer.music.play(start=paused_position / 1000.0)  # ✅ Resume song
            speak("Resuming song.")
        else:
            speak("No song to resume.")

    def next_song(self):
        """Play the next song in the list."""
        global current_song_index
        if current_song_index < len(song_list) - 1:
            current_song_index += 1
            self.play_song(song_list[current_song_index])
        else:
            speak("This is the last song.")

    def previous_song(self):
        """Play the previous song in the list."""
        global current_song_index
        if current_song_index > 0:
            current_song_index -= 1
            self.play_song(song_list[current_song_index])
        else:
            speak("This is the first song.")

    def voice_command(self):
        """Jarvis Voice Assistant"""
        speak("Hello sir, I am J.A.R.V.I.S. How can I help you?")
        command = listen()

        if "how are you jarvis" in command:
            speak("I am fully operational and at your service.")
        elif "play song jarvis" in command:
            self.play_random_song()
        elif "bye jarvis" in command:
            speak("Goodbye, sir. Have a great day!")
        elif "play song jarvis" in command:
            self.play_random_song()
        elif "stop song jarvis" in command:
            self.stop_current_song()
        elif "resume song jarvis" in command:
            self.resume_song()
        elif "next song jarvis" in command:
            self.next_song()
        elif "previous song jarvis" in command:
            self.previous_song()
        else:
            speak("I didn't understand that, sir.")


# ✅ LOGIN SCREEN
class LoginScreen(Screen):
    def login(self):
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()
        if not email or not password:
            self.show_error("All fields are required!")
            return
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            if "localId" in user:
                self.manager.current = "home"
        except:
            self.show_error("Invalid email or password.")

    def show_error(self, message):
        MDDialog(title="Error", text=message).open()


# ✅ SIGNUP SCREEN
class SignupScreen(Screen):
    def signup(self):
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()
        if not email or not password:
            self.show_error("All fields are required!")
            return
        try:
            user = auth.create_user_with_email_and_password(email, password)
            if "localId" in user:
                self.manager.current = "login"
        except:
            self.show_error("Email already exists.")

    def show_error(self, message):
        MDDialog(title="Error", text=message).open()


# ✅ HOME SCREEN WITH SONGS DISPLAY & CONTROL BUTTONS
class HomeScreen(Screen):
    def on_enter(self):
        """Show local songs when user logs in."""
        self.display_local_songs()

    def display_local_songs(self):
        """Display songs from local storage."""
        self.ids.song_list.clear_widgets()
        songs = list_local_songs()
        for song in songs:
            item = TwoLineAvatarListItem(text=song, secondary_text="Tap to Play")
            item.bind(on_release=lambda x, s=song: self.play_selected_song(s))
            self.ids.song_list.add_widget(item)

    def play_selected_song(self, song_name):
        """Play a song when selected."""
        MDApp.get_running_app().play_song(song_name)


# ✅ SCREENMANAGER UI FIXED
KV = '''
WindowManager:
    LoginScreen:
    SignupScreen:
    HomeScreen

<LoginScreen>:
    name: "login"
    MDBoxLayout:
        orientation: "vertical"
        padding: "40dp"
        spacing: "30dp"
        md_bg_color: 0.1, 0.1, 0.1, 1  # Dark background

        MDLabel:
            text: "Login"
            font_style: "H3"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1  # White text

        MDTextField:
            id: email
            hint_text: "Enter Email"
            icon_right: "email"
            mode: "fill"
            fill_color: 0.2, 0.2, 0.2, 1
            text_color: 1, 1, 1, 1
            radius: [25, 25, 25, 25]

        MDTextField:
            id: password
            hint_text: "Enter Password"
            icon_right: "lock"
            mode: "fill"
            fill_color: 0.2, 0.2, 0.2, 1
            text_color: 1, 1, 1, 1
            password: True
            radius: [25, 25, 25, 25]

        MDBoxLayout:
            orientation: "vertical"
            spacing: "15dp"
            MDRaisedButton:
                text: "Login"
                md_bg_color: 0.1, 0.6, 1, 1
                font_size: "18sp"
                on_release: root.login()
            MDRaisedButton:
                text: "Sign Up"
                md_bg_color: 1, 0.4, 0.7, 1
                font_size: "18sp"
                on_release: app.root.current = "signup"

<SignupScreen>:
    name: "signup"
    MDBoxLayout:
        orientation: "vertical"
        padding: "40dp"
        spacing: "30dp"
        md_bg_color: 0.1, 0.1, 0.1, 1  # Dark background

        MDLabel:
            text: "Sign Up"
            font_style: "H3"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1

        MDTextField:
            id: email
            hint_text: "Enter Email"
            icon_right: "email"
            mode: "fill"
            fill_color: 0.2, 0.2, 0.2, 1
            text_color: 1, 1, 1, 1
            radius: [25, 25, 25, 25]

        MDTextField:
            id: password
            hint_text: "Enter Password"
            icon_right: "lock"
            mode: "fill"
            fill_color: 0.2, 0.2, 0.2, 1
            text_color: 1, 1, 1, 1
            password: True
            radius: [25, 25, 25, 25]

        MDBoxLayout:
            orientation: "vertical"
            spacing: "15dp"
            MDRaisedButton:
                text: "Sign Up"
                md_bg_color: 0.1, 0.6, 1, 1
                font_size: "18sp"
                on_release: root.signup()
            MDRaisedButton:
                text: "Login"
                md_bg_color: 1, 0.4, 0.7, 1
                font_size: "18sp"
                on_release: app.root.current = "login"

<HomeScreen>:
    name: "home"
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "15dp"
        md_bg_color: 0.03, 0.03, 0.03, 0  # Darker background for contrast

        # ✅ Top Header Section
        MDBoxLayout:
            size_hint_y: None
            height: "60dp"
            md_bg_color: 0.2, 0.2, 0.2, 1  # Dark Grey Header
            radius: [10, 10, 0, 0]

            MDLabel:
                text: "Music Player"
                font_style: "H4"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                bold: True

        # ✅ Song List Display
        ScrollView:
            MDList:
                id: song_list
                padding: "10dp"

        # ✅ Button Section with Alignment
        MDBoxLayout:
            orientation: "horizontal"
            spacing: "10dp"
            size_hint_y: None
            height: "50dp"

            MDRaisedButton:
                text: "Play Random"
                md_bg_color: 0.2, 0.7, 1, 1
                font_size: "14sp"
                size_hint_x: 1
                bold: True
                on_release: app.play_random_song()

            MDRaisedButton:
                text: "Stop"
                md_bg_color: 1, 0.2, 0.2, 1
                font_size: "14sp"
                size_hint_x: 1
                bold: True
                on_release: app.stop_current_song()

            MDRaisedButton:
                text: "Resume"
                md_bg_color: 0.3, 1, 0.4, 1
                font_size: "14sp"
                size_hint_x: 1
                bold: True
                on_release: app.resume_song()

        # ✅ Second Row of Buttons
        MDBoxLayout:
            orientation: "horizontal"
            spacing: "10dp"
            size_hint_y: None
            height: "50dp"

            MDRaisedButton:
                text: "Next"
                md_bg_color: 0.9, 0.7, 0.2, 1
                font_size: "14sp"
                size_hint_x: 1
                bold: True
                on_release: app.next_song()

            MDRaisedButton:
                text: "Previous"
                md_bg_color: 0.7, 0.4, 1, 1
                font_size: "14sp"
                size_hint_x: 1
                bold: True
                on_release: app.previous_song()

            MDRaisedButton:
                text: " Voice Assistant"
                md_bg_color: 0.9, 0.3, 0.9, 1
                font_size: "14sp"
                size_hint_x: 1
                bold: True
                on_release: app.voice_command()

'''

if __name__ == "__main__":
    MusicSystemApp().run()