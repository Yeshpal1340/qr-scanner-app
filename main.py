from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

# Import Android-specific modules only on Android
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        activity.setRequestedOrientation(1)  # Portrait mode
        ANDROID_AVAILABLE = True
    except ImportError:
        ANDROID_AVAILABLE = False
        print("Android modules not available")
else:
    ANDROID_AVAILABLE = False

try:
    from PIL import Image
    from pyzbar.pyzbar import decode, ZBarSymbol
    SCANNING_AVAILABLE = True
except ImportError:
    SCANNING_AVAILABLE = False
    print("Scanning libraries not available")

try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("TTS not available")

import os
import tempfile

# Set window background color
Window.clearcolor = (1, 1, 1, 1)

# Language folder mapping
LANGUAGE_FOLDERS = {
    "Hindi": "hindi1", 
    "Bengali": "bangoli", 
    "Tamil": "tamil", 
    "Kannada": "kannada",
    "Malayalam": "malyalam", 
    "Urdu": "urdu", 
    "Gujarati": "gujarati", 
    "Punjabi": "punjabi",
    "Telugu": "telugu", 
    "Nepali": "nepali", 
    "Sanskrit": "sanskrit", 
    "Marathi": "marathi", 
    "English": "english"
}

class StableCamera(Camera):
    def _camera_loaded(self, *largs):
        try:
            super()._camera_loaded(*largs)
        except Exception as e:
            print(f"Camera load failed: {e}")

class LanguageSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Request permissions on Android
        if ANDROID_AVAILABLE:
            try:
                request_permissions([
                    Permission.CAMERA, 
                    Permission.READ_EXTERNAL_STORAGE, 
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_MEDIA_AUDIO
                ])
            except Exception as e:
                print(f"Permission request failed: {e}")
        
        self.selected_folder = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Title
        title = Label(
            text="[b][color=#2E7D32]QR Code Scanner[/color][/b]",
            markup=True,
            font_size='28sp',
            size_hint=(1, 0.15)
        )
        layout.add_widget(title)
        
        # Subtitle
        subtitle = Label(
            text="Select Language for Audio Playback",
            font_size='18sp',
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(1, 0.1)
        )
        layout.add_widget(subtitle)
        
        # Language selection spinner
        self.lang_spinner = Spinner(
            text="Choose Language",
            values=list(LANGUAGE_FOLDERS.keys()),
            size_hint=(1, 0.12),
            font_size='16sp'
        )
        self.lang_spinner.bind(text=self.on_language_select)
        layout.add_widget(self.lang_spinner)
        
        # Selected folder display
        self.folder_label = Label(
            text="No language selected",
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.folder_label)
        
        # Status info
        status_text = "Scanning: " + ("Available" if SCANNING_AVAILABLE else "Not Available")
        status_text += "\nTTS: " + ("Available" if TTS_AVAILABLE else "Not Available")
        status_text += "\nAndroid: " + ("Available" if ANDROID_AVAILABLE else "Not Available")
        
        status_label = Label(
            text=status_text,
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint=(1, 0.15)
        )
        layout.add_widget(status_label)
        
        # Continue button
        self.continue_btn = Button(
            text="Continue to Scanner",
            size_hint=(1, 0.12),
            font_size='18sp',
            disabled=True,
            background_color=(0.18, 0.49, 0.20, 1)
        )
        self.continue_btn.bind(on_press=self.go_to_scanner)
        layout.add_widget(self.continue_btn)
        
        # Instructions
        instructions = Label(
            text="Audio files should be placed in:\n/storage/emulated/0/qr_scanner/[language_folder]/",
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint=(1, 0.15),
            text_size=(None, None),
            halign='center'
        )
        layout.add_widget(instructions)
        
        self.add_widget(layout)
    
    def on_language_select(self, spinner, text):
        if text in LANGUAGE_FOLDERS:
            folder = LANGUAGE_FOLDERS[text]
            self.selected_folder = f"/storage/emulated/0/qr_scanner/{folder}"
            self.folder_label.text = f"Selected: {self.selected_folder}"
            self.continue_btn.disabled = False
            
            # Create folder if it doesn't exist
            try:
                os.makedirs(self.selected_folder, exist_ok=True)
            except Exception as e:
                print(f"Error creating folder: {e}")
    
    def go_to_scanner(self, instance):
        scanner_screen = self.manager.get_screen('scanner')
        scanner_screen.set_audio_folder(self.selected_folder)
        self.manager.current = 'scanner'

class ScannerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_qr = ""
        self.audio_folder = None
        self.scanning_active = False
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        back_btn = Button(
            text="← Back",
            size_hint=(0.3, 1),
            font_size='16sp'
        )
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        
        title = Label(
            text="[b]QR Scanner[/b]",
            markup=True,
            font_size='20sp',
            size_hint=(0.7, 1)
        )
        header_layout.add_widget(title)
        
        layout.add_widget(header_layout)
        
        # Camera
        self.camera = StableCamera(
            play=False,
            resolution=(640, 480),
            index=0,
            size_hint=(1, 0.6)
        )
        layout.add_widget(self.camera)
        
        # Status label
        self.status_label = Label(
            text="Ready to scan QR codes",
            font_size='16sp',
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.status_label)
        
        # Control buttons
        btn_layout = BoxLayout(size_hint=(1, 0.12), spacing=10)
        
        self.start_btn = Button(text="Start Camera", font_size='14sp')
        self.stop_btn = Button(text="Stop Camera", font_size='14sp')
        
        self.start_btn.bind(on_press=self.start_camera)
        self.stop_btn.bind(on_press=self.stop_camera)
        
        btn_layout.add_widget(self.start_btn)
        btn_layout.add_widget(self.stop_btn)
        
        layout.add_widget(btn_layout)
        
        # Footer
        footer = Label(
            text="Point camera at QR code to scan and play audio",
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint=(1, 0.08)
        )
        layout.add_widget(footer)
        
        self.add_widget(layout)
        
        # Schedule QR scanning
        Clock.schedule_interval(self.scan_qr, 1.0)
    
    def set_audio_folder(self, folder_path):
        self.audio_folder = folder_path
        self.status_label.text = f"Audio folder: {os.path.basename(folder_path) if folder_path else 'None'}"
    
    def start_camera(self, instance):
        try:
            self.camera.play = True
            self.scanning_active = True
            self.status_label.text = "Scanning for QR codes..."
        except Exception as e:
            self.status_label.text = f"Camera start error: {e}"
    
    def stop_camera(self, instance):
        try:
            self.camera.play = False
            self.scanning_active = False
            self.status_label.text = "Camera stopped"
        except Exception as e:
            self.status_label.text = f"Camera stop error: {e}"
    
    def scan_qr(self, dt):
        if not self.scanning_active or not self.camera.play or not self.camera.texture or not self.audio_folder:
            return
        
        if not SCANNING_AVAILABLE:
            return
        
        try:
            texture = self.camera.texture
            size = texture.size
            pixels = texture.pixels
            
            # Convert texture to PIL Image
            img = Image.frombytes('RGBA', size, pixels)
            img = img.transpose(Image.FLIP_TOP_BOTTOM).convert('L')
            
            # Decode QR codes
            decoded_objects = decode(img, symbols=[ZBarSymbol.QRCODE])
            
            if decoded_objects:
                qr_data = decoded_objects[0].data.decode('utf-8-sig').strip()
                
                if qr_data != self.last_qr:
                    self.last_qr = qr_data
                    self.status_label.text = f"Detected: {qr_data}"
                    self.play_audio(qr_data)
                    
        except Exception as e:
            self.status_label.text = f"Scan error: {str(e)}"
    
    def play_audio(self, text):
        if not self.audio_folder:
            return
            
        filename = f"{text.strip()}.mp3"
        audio_path = os.path.join(self.audio_folder, filename)
        
        if os.path.exists(audio_path):
            try:
                if ANDROID_AVAILABLE:
                    # Use Android MediaPlayer
                    MediaPlayer = autoclass('android.media.MediaPlayer')
                    File = autoclass('java.io.File')
                    
                    self.player = MediaPlayer()
                    self.player.setDataSource(audio_path)
                    self.player.prepare()
                    self.player.start()
                    
                    self.status_label.text = f"Playing: {text}"
                else:
                    # For desktop testing
                    print(f"Would play audio: {audio_path}")
                    self.status_label.text = f"Audio file found: {text}"
                    
            except Exception as e:
                self.status_label.text = f"Audio error: {str(e)}"
                # Fallback to TTS
                self.generate_and_play_tts(text)
        else:
            # Generate TTS if audio file doesn't exist
            self.generate_and_play_tts(text)
    
    def generate_and_play_tts(self, text):
        if not TTS_AVAILABLE:
            self.status_label.text = f"Text: {text} (TTS not available)"
            return
            
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            
            if ANDROID_AVAILABLE:
                temp_path = "/storage/emulated/0/qr_scanner/temp_tts.mp3"
            else:
                temp_path = os.path.join(tempfile.gettempdir(), "temp_tts.mp3")
            
            tts.save(temp_path)
            
            if ANDROID_AVAILABLE:
                MediaPlayer = autoclass('android.media.MediaPlayer')
                
                self.player = MediaPlayer()
                self.player.setDataSource(temp_path)
                self.player.prepare()
                self.player.start()
                
                self.status_label.text = f"TTS: {text}"
            else:
                print(f"Generated TTS: {temp_path}")
                self.status_label.text = f"TTS generated: {text}"
                
        except Exception as e:
            self.status_label.text = f"TTS error: {str(e)}"
    
    def go_back(self, instance):
        try:
            self.camera.play = False
            self.scanning_active = False
        except:
            pass
        self.manager.current = 'language_selection'

class QRScannerApp(App):
    def build(self):
        self.title = "QR Code Scanner"
        
        sm = ScreenManager()
        sm.add_widget(LanguageSelectionScreen(name='language_selection'))
        sm.add_widget(ScannerScreen(name='scanner'))
        
        return sm

if __name__ == '__main__':
    QRScannerApp().run()
