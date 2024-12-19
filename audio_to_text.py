import os
import json
import tempfile
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from moviepy.editor import VideoFileClip
import customtkinter as ctk
from tkinter import filedialog
import threading
from PIL import Image
import tkinter as tk

def convert_webp_to_ico(webp_path, ico_path):
    try:
        # Open and convert webp to RGBA
        img = Image.open(webp_path)
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        # Save as ICO
        img.save(ico_path, format='ICO')
        return True
    except Exception as e:
        print(f"Error converting icon: {e}")
        return False

class APIKeyDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_key=''):
        super().__init__(parent)
        
        # Configure window
        self.title("Enter GROQ API Key")
        try:
            self.after(200, lambda: self.wm_iconbitmap(os.path.abspath("TranscribeX.ico")))
        except:
            pass
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Instructions
        self.instructions = ctk.CTkTextbox(
            self,
            height=120,
            font=("Inter", 13),
            fg_color="#000000",
            text_color="#FFFFFF",
            wrap="word"
        )
        self.instructions.grid(row=0, column=0, padx=25, pady=(25, 15), sticky="ew")
        self.instructions.insert("1.0", "To get your Groq API key:\n\n1. Visit Groq Console (click the button below)\n2. Sign up or log in\n3. Click on 'API Keys' in the left sidebar\n4. Click 'Create API Key'\n5. Copy and paste the key here")
        self.instructions.configure(state="disabled")
        
        # Groq Console button
        self.console_button = ctk.CTkButton(
            self,
            text="Open Groq Console",
            command=lambda: webbrowser.open('https://console.groq.com/playground'),
            width=200,
            height=38,
            font=("Inter", 13),
            fg_color="#000000",
            hover_color="#333333"
        )
        self.console_button.grid(row=1, column=0, padx=25, pady=(0, 15))
        
        # API Key entry
        self.entry = ctk.CTkEntry(
            self,
            width=450,
            height=38,
            font=("Inter", 13),
            placeholder_text="Enter your Groq API key..."
        )
        self.entry.grid(row=2, column=0, padx=25, pady=(0, 15))
        self.entry.insert(0, current_key)
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=3, column=0, padx=25, pady=(0, 25))
        
        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Save",
            command=self.save,
            width=120,
            height=38,
            font=("Inter", 13),
            fg_color="#000000",
            hover_color="#333333"
        )
        self.save_button.grid(row=0, column=0, padx=5)
        
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            command=self.cancel,
            width=120,
            height=38,
            font=("Inter", 13),
            fg_color="#333333",
            hover_color="#666666"
        )
        self.cancel_button.grid(row=0, column=1, padx=5)
        
        self.center_window()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def save(self):
        api_key = self.entry.get().strip()
        if api_key:
            self.save_api_key(api_key)
            self.api_key = api_key
            os.environ['GROQ_API_KEY'] = api_key
            self.destroy()
        
    def cancel(self):
        self.destroy()

    def save_api_key(self, api_key):
        try:
            config = {'api_key': api_key}
            with open('config.json', 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving API key: {e}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Create config directory if it doesn't exist
        self.config_dir = os.path.join(os.getenv('APPDATA'), 'TranscribeX')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        os.makedirs(self.config_dir, exist_ok=True)

        # Load saved API key
        self.api_key = self.load_api_key()
        
        # Configure window
        self.title("TranscribeX")
        try:
            self.after(200, lambda: self.wm_iconbitmap(os.path.abspath("TranscribeX.ico")))
        except:
            pass
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self,
            text="TranscribeX",
            font=("Inter", 24, "bold"),
            text_color="#FFFFFF"
        )
        self.title_label.grid(row=0, column=0, pady=(20, 0))
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, pady=20)
        
        # Buttons
        self.select_button = ctk.CTkButton(
            self.button_frame,
            text="Select File",
            command=self.select_file,
            width=150,
            height=40,
            font=("Inter", 13),
            fg_color="#000000",
            hover_color="#333333"
        )
        self.select_button.grid(row=0, column=0, padx=10)
        
        self.api_key_button = ctk.CTkButton(
            self.button_frame,
            text="Set API Key",
            command=self.show_api_key_dialog,
            width=150,
            height=40,
            font=("Inter", 13),
            fg_color="#333333",
            hover_color="#666666"
        )
        self.api_key_button.grid(row=0, column=1, padx=10)
        
        # Main frame with flexible scaling
        self.main_frame = ctk.CTkFrame(self, fg_color="#000000", corner_radius=0)
        self.main_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Select an audio or video file to begin",
            font=("Inter", 13),
            text_color="#CCCCCC"
        )
        self.status_label.grid(row=0, column=0, padx=25, pady=(25, 5), sticky="w")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame,
            mode="indeterminate",
            height=2,
            fg_color="#333333",
            progress_color="#FFFFFF"
        )
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=25, pady=(0, 25))
        self.progress_bar.set(0)
        
        # Text area (with flexible scaling)
        self.text_area = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            font=("Inter", 14),
            fg_color="#111111",
            text_color="#FFFFFF",
            border_color="#333333",
            border_width=1
        )
        self.text_area.grid(row=2, column=0, padx=25, pady=(0, 25), sticky="nsew")
        
        # Bottom frame for save button and credits
        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, pady=(0, 25))
        
        # Save button
        self.save_button = ctk.CTkButton(
            self.bottom_frame,
            text="Save Transcription",
            command=self.save_transcription,
            width=180,
            height=40,
            font=("Inter", 13),
            state="disabled",
            fg_color="#000000",
            hover_color="#333333"
        )
        self.save_button.grid(row=0, column=0, pady=(0, 15))
        
        # Credits
        self.credits_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.credits_frame.grid(row=1, column=0)
        
        self.credits_label = ctk.CTkLabel(
            self.credits_frame,
            text="By ",
            font=("Inter", 12),
            text_color="#999999"
        )
        self.credits_label.grid(row=0, column=0)
        
        self.github_link = ctk.CTkButton(
            self.credits_frame,
            text="Jithin Garapati",
            command=lambda: webbrowser.open('https://github.com/Jithin-Garapati'),
            font=("Inter", 12, "bold"),
            fg_color="transparent",
            hover_color="#333333",
            text_color="#FFFFFF"
        )
        self.github_link.grid(row=0, column=1)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        
        # Load API key
        os.environ['GROQ_API_KEY'] = self.api_key
        
        # Center the window
        self.center_window()
        
        # Bind resize event
        self.bind("<Configure>", self.on_resize)
    
    def on_resize(self, event):
        # Only handle window resize events
        if event.widget == self:
            pass
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def load_api_key(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('api_key', '')
        except Exception as e:
            print(f"Error loading API key: {e}")
        return ''

    def save_api_key(self, api_key):
        try:
            config = {'api_key': api_key}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving API key: {e}")
    
    def show_api_key_dialog(self):
        current_key = self.api_key
        dialog = APIKeyDialog(self, current_key)
        self.wait_window(dialog)
        if dialog.api_key:
            self.save_api_key(dialog.api_key)
            self.api_key = dialog.api_key
            os.environ['GROQ_API_KEY'] = self.api_key
            self.status_label.configure(text="API Key saved successfully!")

    def extract_audio_from_video(self, video_path):
        """Extract audio from video file and save it temporarily"""
        temp_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(
            temp_audio.name,
            codec='libmp3lame',
            verbose=False,
            logger=None
        )
        video.close()
        return temp_audio.name

    def transcribe_file(self, file_path):
        """Transcribe audio file using Groq"""
        if not os.getenv('GROQ_API_KEY'):
            self.status_label.configure(text="Please set your Groq API Key first")
            return None

        client = Groq()
        file_ext = Path(file_path).suffix.lower()
        audio_path = file_path
        
        try:
            # If it's a video file, extract the audio first
            if file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                self.status_label.configure(text="Extracting audio from video...")
                self.update()
                audio_path = self.extract_audio_from_video(file_path)

            self.status_label.configure(text="Transcribing... Please wait...")
            self.update()
            
            with open(audio_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(audio_path, file.read()),
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json",
                )
                return transcription.text
        finally:
            # Clean up temporary audio file if it was created
            if audio_path != file_path:
                os.unlink(audio_path)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Media files", "*.mp3 *.m4a *.wav *.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.text_area.delete("0.0", "end")
            self.save_button.configure(state="disabled")
            self.progress_bar.start()
            
            def process_file():
                try:
                    transcription = self.transcribe_file(file_path)
                    if transcription:
                        self.text_area.delete("0.0", "end")
                        self.text_area.insert("0.0", transcription)
                        self.status_label.configure(text="Transcription complete!")
                        self.save_button.configure(state="normal")
                except Exception as e:
                    self.status_label.configure(text=f"Error: {str(e)}")
                    self.text_area.delete("0.0", "end")
                finally:
                    self.progress_bar.stop()
                    self.progress_bar.set(0)
            
            # Run transcription in a separate thread
            threading.Thread(target=process_file, daemon=True).start()

    def save_transcription(self):
        text = self.text_area.get("0.0", "end").strip()
        if text:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.status_label.configure(text="Transcription saved successfully!")

def main():
    load_dotenv()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
