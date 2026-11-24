"""
NOVA - Tamagotchi-Desktop-Overlay (Windows) - rot/schwarz

Optional für eigene Bilder:  pip install pillow
Beim ersten Start kannst du pro Emotion ein Bild und eigene Sprechblasentexte wählen
(Bilder werden nach "emotion_images" kopiert). Ohne Bild für eine Emotion nutzt NOVA
das Normal-Bild, ohne jedes Bild die eingebaute gezeichnete Figur.
Eine vorhandene "sprite.png" wird automatisch als Normal-Bild übernommen.

Tamagotchi: Werte HUN/FUN/NRG, Punkte (ausgeben) und XP (Level), Wortschatz,
Minispiele mit Rekorden, Shop, Schlafen, Fenster-Modus, Mini-Modus bei Vollbild und
quadratischer Telefonmodus mit eigenem Bild oder quadratischem Ausschnitt des Normal-Bilds.
Optionaler Lebensmodus mit Fensterwechseln, Mausreaktionen und expliziten PC-Steuerungen.

Verbesserungen dieser Version:
  - Werkzeuge (Menü > Werkzeuge):
      Timer: 5/15 Min, 25 Min "Fokus" (+3 Punkte) oder eigene Dauer (25, 1h30, 90s, 1:30).
      Erinnerungen: "14:30 Anruf", "20m Pause machen", "in 2 h Wäsche", "täglich 8:00 Tabletten".
      Autoclicker: Intervall, Maustaste, Doppelklick, max. Klicks, Startverzögerung und
      Zielpunkte (Maus hinbewegen, 5 s warten) oder Klicken an der aktuellen Mausposition.
      Notausschalter: F6 (Start/Stopp) und Esc (Stopp). Klicks auf NOVAs eigene Fenster
      werden übersprungen. Timer und Erinnerungen überleben einen Neustart.
  - Daten-Farm (Menü > Spielen > Farm): Idle-Spiel in eigenem Fenster. Generatoren, Upgrades
    und Reboot (Chips = dauerhafter Bonus + Punkte für NOVA). Läuft im Hintergrund weiter,
    solange NOVA läuft; offline 50 % für bis zu 12 Stunden. Wird im Spielstand gespeichert.
  - Neue Minispiele: Pong (Maus bewegt den Schläger, wer zuerst 5 hat), Ausweichen (Daten
    fangen, Glitches meiden, 3 Leben) und Merken (Folge nachklicken). Alle mit Rekorden;
    NOVA bleibt währenddessen stehen.
  - Spotify-Box: Ist Spotify (Windows) offen, wechselt NOVA in die Emotion "Musik" und sitzt
    auf einer Box mit Songtitel, Equalizer und Knöpfen (Lautstärke, zurück, Play/Pause,
    weiter). Auch im Mini- und Telefonmodus. Ein/Aus unter Optionen > Audio > Spotify.
    Für die Emotion "Musik" kann im Emotionseditor ein eigenes Bild/Text gesetzt werden.
  - Radialmenü: Halbkreis wie gehabt (ohne Punkt in der Mitte, "Zurück" als letzte Kugel),
    aktive Schalter leuchten, nicht bezahlbare Shop-Artikel sind gedimmt, das Menü
    schließt automatisch, wenn die Maus länger weg ist.
  - Physik: NOVA lässt sich mit der Maus werfen, fällt mit Schwerkraft auf den Boden, prallt
    an Wänden ab und bleibt manchmal auf Fensterkanten sitzen (Optionen > Physik). Nicht im
    Telefonmodus.
  - Eigene Bilder sind wieder animiert (Atmen, Pendeln, Laufneigung, Spiegelung) und
    werden sparsam im Speicher gehalten. Emotionen wechseln auch kurz beim Streicheln
    und Füttern.
  - Emotionseditor: Vorschau, Bildprüfung, mehrere Sprüche je Emotion mit "|".
  - Minispiele: Rekorde mit Bonus, Reaktionszeit-Bonus, schrumpfender Zielring,
    Sprungspiel wird schneller, NOVA geht danach wieder nach unten.
  - KI-Modus: Gemini, ChatGPT (OpenAI API) oder OpenRouter-Free; standardmäßig
    ausgeschaltet. KI-Sprechblasen und Reaktionen laufen über den gewählten Anbieter;
    Mikrofontext wird lokal erkannt und erst nach Bestätigung gesendet.
  - Sprachausgabe: lokale deutsche Windows-Stimme Microsoft Katja mit
    leicht sprunghafter, synthetischer Prosodie; offline.
  - Speichern: atomar mit Sicherung (.bak), Werte werden beim Laden geprüft.
  - Robustheit: Fehler in der Hauptschleife stoppen NOVA nicht mehr (Log in nova_error.log),
    Hintergrund-KI-Threads fangen jeden Fehler ab, Speicherstand wird strenger geprüft.
  - Performance: Fenstergeometrie wird nur bei Änderung gesetzt.
  - Beenden: zufälliger Abschiedsgruß, beim nächsten Beenden garantiert ein anderer;
    erscheint in der Animation und wird bei aktivierter Sprachausgabe vorgelesen.

  - Musikmodus: Solange Spotify läuft, bleibt NOVA in der Emotion "Musik" (keine Umschaltung
    durch Streicheln, Füttern, Hunger usw.). Geworfen rutscht sie wie auf Eis über den
    Bildschirm und prallt sanft an den Rändern ab, ohne zum Boden zu fallen. Sie bleibt
    dort liegen, wo sie zum Stehen kommt (nicht im Mini-Modus).
  - Soundeffekte (Optionen > Audio > Effekte): kurze, leise, synthetische Töne beim Werfen,
    Aufprall am Boden, Abprallen an Rändern und Landen auf Fenstern. Weiche Aufpraller
    bleiben stumm, es gibt Mindestabstände, nichts wird in Schleife gespielt.

Neu: Emotion "Sitzen" (statt Musik) mit eigener Fußlinie (Größe & Füße), Emotion "Luft" bei
Wurf/Schütteln/Ablegen in der Luft, Pendel um den Greifpunkt beim Schütteln.

Bedienung: Maus über NOVA = Statusanzeige | ziehen und loslassen = werfen
           Doppelklick = streicheln | Rechtsklick = Menü
"""
import atexit
import base64
import ctypes
import datetime
import fnmatch
import hashlib
import importlib.util
import io
import json
import math
import os
import queue
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
import traceback
import wave
import zlib
import webbrowser
from collections import OrderedDict
from tkinter import filedialog as _native_filedialog, messagebox as _native_messagebox

from gemini_api import GeminiAPIError, generate_content
from openai_api import OpenAIAPIError, generate_content as generate_openai_content
from ollama_api import OllamaAPIError, generate_content as generate_ollama_content

try:
    import winsound
except ImportError:           # nicht unter Windows
    winsound = None

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_FREE_MODEL = "openrouter/free"
OLLAMA_DEFAULT_MODEL = "gemma3:12b"
AI_MEMORY_MAX_TURNS = 20
AI_VOICE_QUEUE_MAX = 4
OPENROUTER_SYSTEM_PROMPT = (
    "Diese App nutzt für OpenRouter ausschließlich den Modell-Router openrouter/free und keinen "
    "bezahlten Fallback. Anfragen über diesen Router sind kostenlos, aber es gelten Rate-Limits "
    "und wechselnde Modellverfügbarkeit. Andere OpenRouter-Modelle können kostenpflichtig sein. "
    "Nenne kein festes kostenloses Tokenkontingent: Der Router hat Limits, aber du kennst weder "
    "die aktuellen Kontodaten noch das persönliche Guthaben des Nutzers. Erfinde keine Preise, "
    "Guthaben oder Tokenzahlen; verweise für Kontostände auf das OpenRouter-Dashboard."
)
AI_SPEECH_CONTEXT_TERMS = {
    "feed": ("futter", "ess", "lecker", "schmeck", "happen", "nom nom", "mampf", "biss"),
    "pet": ("streichel", "streich", "kitzel", "kraule", "kuschel"),
}

try:
    from PIL import Image, ImageDraw, ImageGrab, ImageOps, ImageTk
except ImportError:
    Image = None
    ImageDraw = None
    ImageGrab = None
    ImageOps = None
    ImageTk = None

try:
    import winsound
except ImportError:
    winsound = None

IS_WIN = sys.platform == "win32"
IGNORED_CLASSES = {"Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd",
                   "XamlExplorerHostIslandWindow"}
if IS_WIN:
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.IsIconic.argtypes = [wintypes.HWND]
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
    user32.GetLastInputInfo.argtypes = [ctypes.c_void_p]
    user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetParent.argtypes = [wintypes.HWND]
    user32.GetParent.restype = wintypes.HWND
    user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user32.GetAncestor.restype = wintypes.HWND
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.GetSystemMetrics.argtypes = [ctypes.c_int]
    user32.GetSystemMetrics.restype = ctypes.c_int
    user32.SetWindowPos.argtypes = [
        wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int, wintypes.UINT,
    ]
    user32.SetWindowPos.restype = wintypes.BOOL
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.keybd_event.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, wintypes.DWORD, ctypes.c_size_t]
    user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
    user32.SetCursorPos.restype = wintypes.BOOL
    user32.mouse_event.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                                   wintypes.DWORD, ctypes.c_size_t]
    user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
    user32.GetAsyncKeyState.restype = ctypes.c_short
    user32.WindowFromPoint.argtypes = [wintypes.POINT]
    user32.WindowFromPoint.restype = wintypes.HWND
    kernel32 = ctypes.windll.kernel32
    kernel32.GetTickCount64.restype = ctypes.c_ulonglong
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", wintypes.DWORD),
            ("dwMemoryLoad", wintypes.DWORD),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]

    kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MEMORYSTATUSEX)]
    kernel32.GlobalMemoryStatusEx.restype = wintypes.BOOL
    kernel32.GetSystemTimes.argtypes = [
        ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME)
    ]
    kernel32.GetSystemTimes.restype = wintypes.BOOL

HERE = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
SAVE_FILE = os.path.join(HERE, "nova_save.json")
AI_MEMORY_FILE = os.path.join(HERE, "nova_ai_memory.json")
EMOTION_IMAGE_DIR = os.path.join(HERE, "emotion_images")
LEGACY_SPRITE = os.path.join(HERE, "sprite.png")
PHONE_IMAGE_FILE = os.path.join(HERE, "phone_image.png")
PHONE_TALK_IMAGE_FILE = os.path.join(HERE, "phone_talk_image.png")
ERROR_LOG = os.path.join(HERE, "nova_error.log")
IMAGE_FILETYPES = [("Bilder", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                   ("Alle Dateien", "*.*")]

# ---------- Design: rot/schwarz ----------
TRANS = "#010203"
ACCENT = "#ff2e43"    # leuchtendes Rot
EDGE = "#9b1226"      # dunkles Rot (Rahmen)
LIGHT = "#f4e9ea"     # Text / Highlights
PANEL = "#0b0506"     # Schwarz (Flächen)
PANEL2 = "#1a0b0d"    # Schwarz, etwas heller
DIM = "#7d4a50"       # gedämpft (nicht verfügbar)

W, H = 220, 440
PHONE_SIZE = 280
PHONE_IMAGE_SIZE = 236
HUD_H = 52
SPRITE_H = 320
SPRITE_H_SMALL = 150       # Größe auf Fenstern
SPRITE_H_MINI = 100        # Größe im Mini-Modus (Vollbild)
SPRITE_SCALE_MIN = 0.4     # kleinste einstellbare Größe (Faktor auf alle SPRITE_H*)
SPRITE_SCALE_MAX = 1.2     # größte Größe (mehr passt nicht in das 220x440-Fenster)
PHYS_SPIN_THROW = 0.16         # Drehung beim Werfen (Grad/s pro px/s Wurfgeschwindigkeit)
PHYS_SPIN_MAX = 720.0          # maximale Drehgeschwindigkeit (Grad/s)
PHYS_SPIN_DRAG = 0.35          # Dreh-Reibung in der Luft (pro Sekunde)
PHYS_SPIN_BOUNCE = 0.15        # Zusatzdrehung bei Aufprall am Boden
PHYS_UPRIGHT_RATE = 9.0        # wie schnell NOVA sich am Boden wieder aufrichtet
GROUND_OFFSET_MIN, GROUND_OFFSET_MAX = -60, 80   # Bodenhöhe in px (+ = tiefer)
PEND_K, PEND_D, PEND_IN, PEND_MAX = 60.0, 5.0, 0.06, 75.0   # Pendel beim Schütteln: Feder, Dämpfung, Mauseinfluss, max. Grad
FOOT_PCT_MAX = 45.0        # max. Abstand der Füße vom unteren Bildrand (% der Bildhöhe)
STARTUP_ANIMATION = True   # Einschalt-Animation beim Programmstart
BOOT_DURATION = 1.8        # Dauer der Einschalt-Animation (Sekunden)
FRAMES = 10                # Animationsphasen
MAX_FRAME_CACHE = 200      # begrenzt den Bildspeicher
FALLBACK_TO_NEUTRAL = True # Emotion ohne Bild -> Normal-Bild statt Zeichnung
BREAK_MINUTES = 45
RADIAL_SIZE = 340
MUSIC_BOX_H = 64           # Höhe der Musik-Box (normal)
MUSIC_BOX_H_MINI = 40      # Höhe im Mini-Modus
MUSIC_KEYS_FULL = ("volume_down", "prev_track", "play_pause", "next_track", "volume_up")
MUSIC_KEYS_COMPACT = ("prev_track", "play_pause", "next_track")
# Fenstertitel von Spotify ohne Song (Pause / nichts gespielt) und Hilfsfenster, die ignoriert werden
SPOTIFY_IDLE_TITLES = {"spotify", "spotify free", "spotify premium"}
SPOTIFY_IGNORED_TITLES = ("chrome legacy window", "gdi+ window", "default ime",
                          "msctfime ui", "mediaplayer smtc window")

WINDOWS_VOICE_WORKER = os.path.join(HERE, "voice", "windows_voice_worker.ps1")
WINDOWS_SPEECH_INPUT_WORKER = os.path.join(HERE, "voice", "windows_speech_input_worker.ps1")
WHISPER_INPUT_WORKER = os.path.join(HERE, "voice", "whisper_input_worker.py")
WINDOWS_VOICE_TOKEN = (
    r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens"
    r"\MSTTS_V110_deDE_KatjaM"
)


def find_local_whisper_model():
    model_override = os.environ.get("NOVA_WHISPER_MODEL", "").strip()
    if model_override and all(
            os.path.isfile(os.path.join(model_override, filename))
            for filename in ("model.bin", "config.json", "tokenizer.json")):
        return model_override

    hf_home = os.environ.get(
        "HF_HOME", os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
    )
    hf_cache = os.environ.get("HF_HUB_CACHE", os.path.join(hf_home, "hub"))
    model_root = os.path.join(hf_cache, "models--Systran--faster-whisper-small")
    snapshots = os.path.join(model_root, "snapshots")
    candidates = []
    try:
        with open(os.path.join(model_root, "refs", "main"), encoding="utf-8") as ref_file:
            candidates.append(os.path.join(snapshots, ref_file.read().strip()))
    except OSError:
        pass
    try:
        candidates.extend(
            os.path.join(snapshots, name) for name in os.listdir(snapshots)
            if name not in {os.path.basename(path) for path in candidates}
        )
    except OSError:
        return None
    for candidate in candidates:
        if all(
                os.path.isfile(os.path.join(candidate, filename))
                for filename in ("model.bin", "config.json", "tokenizer.json")):
            return candidate
    return None


# Werte pro Sekunde
DECAY = {"food": 0.012, "fun": 0.009, "energy": 0.007}
SLEEP_REGEN = 0.15
OFFLINE_FACTOR = 0.4          # Zerfall, während das Programm aus ist
OFFLINE_MAX = 6 * 3600
GAME_SECONDS = 15
DOT_LIFETIME = 2.0
REFLEX_LIFETIME = 1.5

SHOP = {
    "halo": ("Heiligenschein", 20),
    "cap": ("Cyber-Cap", 40),
    "crown": ("Krone", 100),
    "visor": ("Neon-Visor", 55),
    "scarf": ("Neon-Schal", 35),
    "wings": ("Holo-Flügel", 90),
    "headset": ("Cyber-Headset", 60),
    "tophat": ("Zylinder", 70),
    "ears": ("Katzenohren", 45),
    "antenna": ("Antenne", 30),
    "glasses": ("Nerd-Brille", 40),
    "mustache": ("Schnurrbart", 25),
    "mask": ("Cyber-Maske", 65),
    "bowtie": ("Fliege", 30),
    "chain": ("Kette", 50),
    "cape": ("Cape", 80),
    "backpack": ("Rucksack", 55),
    "party": ("Partyhut", 35),
    "horns": ("Teufelshörner", 60),
    "flower": ("Blume", 25),
    "eyepatch": ("Augenklappe", 30),
    "monocle": ("Monokel", 45),
    "tie": ("Krawatte", 35),
    "medal": ("Medaille", 75),
    "jetpack": ("Jetpack", 120),
}
SHOP_CATS = (
    ("shop_head", "Kopf", "👑", ("halo", "cap", "crown", "tophat", "ears", "antenna", "party", "horns", "flower")),
    ("shop_face", "Gesicht", "🕶️", ("visor", "headset", "glasses", "mustache", "mask", "eyepatch", "monocle")),
    ("shop_body", "Körper", "🧣", ("scarf", "bowtie", "chain", "tie", "medal")),
    ("shop_back", "Rücken", "🦋", ("wings", "cape", "backpack", "jetpack")),
)
SHOP_ICONS = {
    "halo": "😇", "cap": "🧢", "crown": "👑", "visor": "🕶️", "scarf": "🧣", "wings": "🦋",
    "headset": "🎧", "tophat": "🎩", "ears": "🐱", "antenna": "📡", "glasses": "🤓",
    "mustache": "👨", "mask": "😷", "bowtie": "🎀", "chain": "📿", "cape": "🦸", "backpack": "🎒",
}
SHOP_SHORT = {"halo": "Halo", "cap": "Cap", "crown": "Krone", "visor": "Visor",
              "scarf": "Schal", "wings": "Flügel", "headset": "Headset",
              "tophat": "Zylinder", "ears": "Ohren", "antenna": "Antenne", "glasses": "Brille",
              "mustache": "Bart", "mask": "Maske", "bowtie": "Fliege", "chain": "Kette",
              "cape": "Cape", "backpack": "Rucksack"}
SHOP_ICONS.update(party="🥳", horns="😈", flower="🌸", eyepatch="🏴‍☠️", monocle="🧐",
                  tie="👔", medal="🏅", jetpack="🚀")
SHOP_SHORT.update(party="Party", horns="Hörner", flower="Blume", eyepatch="Klappe",
                  monocle="Monokel", tie="Krawatte", medal="Medaille", jetpack="Jetpack")
# Verbrauchs-Items: key -> (Name, Preis, Icon, Kurzname, Wert, Menge)
SHOP_ITEMS = {
    "snack": ("Daten-Snack", 8, "🍙", "Snack", "food", 35),
    "drink": ("Energy-Drink", 10, "🥤", "Drink", "energy", 40),
    "toy": ("Spielzeug", 8, "🧸", "Spielzeug", "fun", 35),
    "mega": ("Mega-Paket", 25, "🎁", "Paket", "all", 40),
    "xp": ("XP-Booster", 30, "⚡", "XP +20", "xp", 20),
}
# Zeichnung neuer Accessoires: (Art, Koordinaten relativ zu Mitte/Kopf, Füllung, Linie, Breite)
_RED, _GOLD = "#c4122f", "#d4a537"
SHOP_DRAW = {
    "party": (("p", (-16, 6, 0, -34, 16, 6), _RED, ACCENT, 2), ("l", (-9, -12, 9, -12), "", LIGHT, 2),
              ("o", (-5, -41, 5, -31), LIGHT, ACCENT, 1)),
    "horns": (("p", (-26, 10, -34, -18, -10, 2), _RED, ACCENT, 2),
              ("p", (26, 10, 34, -18, 10, 2), _RED, ACCENT, 2)),
    "flower": (("o", (19, -14, 29, -4), LIGHT, EDGE, 1), ("o", (19, 2, 29, 12), LIGHT, EDGE, 1),
               ("o", (11, -6, 21, 4), LIGHT, EDGE, 1), ("o", (27, -6, 37, 4), LIGHT, EDGE, 1),
               ("o", (20, -5, 28, 3), ACCENT, "", 1)),
    "eyepatch": (("l", (-28, 22, 16, 34), "", EDGE, 3), ("o", (6, 24, 28, 46), "#1a0206", ACCENT, 2)),
    "monocle": (("o", (6, 24, 28, 46), "", LIGHT, 3), ("l", (26, 44, 33, 62, 28, 82), "", LIGHT, 2)),
    "tie": (("p", (-6, 68, 6, 68, 4, 79, -4, 79), _RED, ACCENT, 2),
            ("p", (-4, 79, 4, 79, 9, 108, 0, 117, -9, 108), _RED, ACCENT, 2)),
    "medal": (("l", (-9, 64, 0, 90), "", _RED, 3), ("l", (9, 64, 0, 90), "", _RED, 3),
              ("o", (-9, 88, 9, 106), _GOLD, LIGHT, 2)),
    "jetpack": (("r", (28, 74, 40, 116), PANEL2, ACCENT, 2), ("r", (42, 74, 54, 116), PANEL2, ACCENT, 2),
                ("p", (30, 116, 38, 116, 34, 132), "#ff7a1a", "", 1),
                ("p", (44, 116, 52, 116, 48, 132), "#ff7a1a", "", 1)),
}
# ---- Kisten (CS-Stil): Seltenheit je Teil nach Preis, oder shop.json -> "rarity": common|uncommon|rare|epic|legend|mythic ----
RARITIES = (("common", "Gewöhnlich", "#8a9bb0"), ("uncommon", "Ungewöhnlich", "#5e98d9"),
            ("rare", "Selten", "#4b69ff"), ("epic", "Episch", "#8847ff"),
            ("legend", "Legendär", "#d32ce6"), ("mythic", "Mythisch", "#eb4b4b"))
# key -> (Name, Preis, Icon, Gewichte je Seltenheit); Duplikate geben 50 % des Teilpreises zurück
CASES = {"basic": ("Standard-Kiste", 40, "📦", (60, 25, 10, 4, 0.9, 0.1)),
         "prem": ("Premium-Kiste", 100, "🎁", (20, 35, 25, 13, 5, 2)),
         "elite": ("Elite-Kiste", 250, "💎", (0, 5, 25, 40, 22, 8))}
SHOP_RARITY = {}
CASE_TILE = 104


def rar_index(key):
    r = SHOP_RARITY.get(key)
    if r:
        return [x[0] for x in RARITIES].index(r)
    price = SHOP[key][1]
    return 0 if price <= 30 else 1 if price <= 45 else 2 if price <= 60 else 3 if price <= 80 else 4 if price <= 100 else 5


def case_picker(case):
    pools = [[k for k in SHOP if rar_index(k) == i] for i in range(len(RARITIES))]
    weights = CASES[case][3]

    def pick():
        i = random.choices(range(len(RARITIES)), weights=weights)[0]
        for j in sorted(range(len(RARITIES)), key=lambda n: (abs(n - i), n > i)):   # leere Stufe -> nächste
            if pools[j]:
                return random.choice(pools[j])
    return pick


# ---- Eigene Shop-Teile: PNG in den Ordner "shop" neben der Datei legen ----
# Dateiname: <kat>_<preis>_<Name>.png   kat = head | face | body | back   (z. B. head_50_Cyber Hut.png)
# Kurzform "Name.png" = Kopf, 30 Pkt. Optional shop/shop.json: {"Dateiname-ohne-.png": {"name","price","cat","icon","x","y","w"}}
SHOP_DIR = os.path.join(HERE, "shop")
SHOP_IMG = {}                 # key -> (Pfad, x, y, Breite); x/y relativ zu Mitte/Kopfoberkante
_CAT_DEF = {"head": (0, -4, 70), "face": (0, 36, 60), "body": (0, 88, 60), "back": (0, 96, 90)}
_BASE_CATS = SHOP_CATS


_KEY = b"nova-shop-7f3a91c2"          # beliebig ändern, dann neu packen (--pack)
PULL_BASE = set()                      # eingebaute Teile, die es NUR aus Kisten gibt, z. B. {"jetpack", "crown"}
SHOP_PULL = set(PULL_BASE)             # + PNGs mit "pull_only": true in shop.json


def _xor(data):
    ks = b"".join(hashlib.sha256(_KEY + i.to_bytes(4, "big")).digest() for i in range(len(data) // 32 + 1))[:len(data)]
    return (int.from_bytes(data, "big") ^ int.from_bytes(ks, "big")).to_bytes(len(data), "big")


def _read_folder():
    files, cfg = {}, {}
    if os.path.isdir(SHOP_DIR):
        for f in sorted(os.listdir(SHOP_DIR)):
            if f.lower().endswith((".png", ".webp", ".gif")):
                with open(os.path.join(SHOP_DIR, f), "rb") as fh:
                    files[f] = fh.read()
        jp = os.path.join(SHOP_DIR, "shop.json")
        if os.path.isfile(jp):
            with open(jp, encoding="utf-8") as fh:
                cfg = json.load(fh)
    return files, cfg


def pack_shop():
    """python nova_overlay.py --pack  ->  shop.dat (PNGs + shop.json, verschlüsselt). Danach Ordner shop/ nicht mitgeben."""
    files, cfg = _read_folder()
    blob = json.dumps({"cfg": cfg, "f": {n: base64.b64encode(b).decode() for n, b in files.items()}}).encode()
    with open(os.path.join(HERE, "shop.dat"), "wb") as fh:
        fh.write(_xor(zlib.compress(blob, 9)))
    print(f"shop.dat: {len(files)} Teile")


def _shop_sources():
    files, cfg = {}, {}
    for d in (HERE, getattr(sys, "_MEIPASS", HERE)):
        p = os.path.join(d, "shop.dat")
        if os.path.isfile(p):
            try:
                with open(p, "rb") as fh:
                    j = json.loads(zlib.decompress(_xor(fh.read())))
                cfg.update(j["cfg"])
                files.update({n: base64.b64decode(v) for n, v in j["f"].items()})
                break
            except (OSError, ValueError, zlib.error, KeyError):
                pass
    f2, c2 = _read_folder()               # Ordner shop/ überschreibt (Entwicklung)
    files.update(f2)
    cfg.update(c2)
    return files, cfg


def load_shop_images():
    """Liest shop.dat bzw. shop/ neu ein (beim Öffnen des Shops, kein Neustart nötig)."""
    global SHOP_CATS
    try:
        os.makedirs(SHOP_DIR, exist_ok=True)
        data, cfg = _shop_sources()
        files = sorted(data)
    except (OSError, ValueError):
        return
    for k in SHOP_IMG:
        SHOP.pop(k, None)
        SHOP_ICONS.pop(k, None)
        SHOP_SHORT.pop(k, None)
    SHOP_IMG.clear()
    SHOP_RARITY.clear()
    SHOP_PULL.clear()
    SHOP_PULL.update(PULL_BASE)
    extra = {c: [] for c in _CAT_DEF}
    for f in files:
        stem = os.path.splitext(f)[0]
        parts = stem.split("_", 2)
        cat, price, name = "head", 30, stem
        if len(parts) == 3 and parts[0] in _CAT_DEF and parts[1].isdigit():
            cat, price, name = parts[0], int(parts[1]), parts[2]
        o = cfg.get(stem, {}) if isinstance(cfg, dict) else {}
        cat = o.get("cat", cat) if o.get("cat") in _CAT_DEF else cat
        dx, dy, w = _CAT_DEF[cat]
        key = "img_" + re.sub(r"\W+", "", stem).lower()
        SHOP[key] = (str(o.get("name", name)), int(o.get("price", price)))
        SHOP_ICONS[key] = o.get("icon", "🖼️")
        SHOP_SHORT[key] = SHOP[key][0][:10]
        if o.get("rarity") in [x[0] for x in RARITIES]:
            SHOP_RARITY[key] = o["rarity"]
        if o.get("pull_only"):
            SHOP_PULL.add(key)
        SHOP_IMG[key] = (data[f], o.get("x", dx), o.get("y", dy), o.get("w", w))
        extra[cat].append(key)
    SHOP_CATS = tuple((pg, lb, ic, tuple(k for k in keys if k not in SHOP_IMG) + tuple(extra[pg[5:]]))
                      for pg, lb, ic, keys in _BASE_CATS)


load_shop_images()
# Quests: id -> (Text, Ziel, Belohnung); 3 pro Tag, Bonus bei allen dreien
QUESTS = {
    "pet": ("Streichle NOVA", 5, 3),
    "feed": ("Füttere NOVA", 3, 3),
    "game": ("Spiele Minispiele", 3, 4),
    "points": ("Sammle Punkte", 25, 5),
    "focus": ("Fokus-Timer schaffen", 1, 4),
    "buy": ("Kaufe im Shop", 1, 3),
}
QUEST_BONUS = 6
DAILY_REWARDS = (3, 4, 5, 6, 8, 10, 20)       # Serientag 1..7, danach wieder von vorn

EMOTIONS = (
    ("neutral", "Normal"),
    ("happy", "Fröhlich"),
    ("hungry", "Hungrig"),
    ("bored", "Langeweile"),
    ("sleepy", "Müde"),
    ("sit", "Sitzen (Musik)"),
    ("air", "Luft (Wurf/Schütteln)"),
    ("phone", "Telefon (Bild)"),
    ("phone_talk", "Telefon sprechend"),
    ("crosshair", "Fadenkreuz"),
)
EMO_ART = {"music": "sit"}          # interne Emotion -> Bild/Text-Schlüssel
GAME_LABELS = {"dots": "Datenpunkte", "reflex": "Reflex", "jump": "Hüpfen",
               "pong": "Pong", "dodge": "Ausweichen", "memory": "Merken"}
STATIC_GAMES = ("pong", "dodge", "memory")       # Spiele mit festem Spielfeld (NOVA bleibt stehen)
FX1, FX2 = 10, W - 10                             # Spielfeld
FY1, FY2 = HUD_H + 30, H - 12
PONG_PADDLE_W = 46
PONG_BALL_R = 5
PONG_START_SPEED = 170.0
PONG_MAX_SPEED = 430.0
PONG_WIN = 5
PONG_AI_Y = FY1 + 16
PONG_PLAYER_Y = FY2 - 16
MEMORY_COLORS = ("#ff2e43", "#f4e9ea", "#ff7a2f", "#c4122f")
MEMORY_SYMBOLS = ("▲", "●", "■", "◆")

# ---------- Physik (Pixel, Sekunden) ----------
PHYS_GRAVITY = 2300.0          # Fallbeschleunigung
PHYS_MAX_FALL = 2600.0         # maximale Fallgeschwindigkeit
PHYS_AIR_DRAG = 0.15           # Luftreibung (pro Sekunde)
PHYS_FLOOR_BOUNCE = 0.42       # Rückprall am Boden
PHYS_WALL_BOUNCE = 0.6         # Rückprall an Wänden und Decke
PHYS_FLOOR_FRICTION = 7.0      # Rutschreibung am Boden
PHYS_REST_SPEED = 220.0        # darunter hüpft NOVA nicht mehr
PHYS_MAX_THROW = 3200.0        # maximale Wurfgeschwindigkeit
PHYS_WALL_MARGIN = 40          # so weit darf das Fenster über den Bildschirmrand ragen
PHYS_PERCH_CHANCE = 0.5        # Chance, auf einem Fenster hängen zu bleiben
# ---------- Eis-Modus (Musik): Wurf = Rutschen, keine Schwerkraft ----------
PHYS_ICE_DRAG = 0.5            # Reibung auf Eis (pro Sekunde), sehr gering
PHYS_ICE_BOUNCE = 0.85         # Rückprall an den Bildschirmrändern
PHYS_ICE_STOP = 35.0           # darunter bleibt NOVA liegen, wo sie ist
PHYS_ICE_SPIN = 0.05           # sanfte Drehung beim Werfen auf Eis

# ---------- Soundeffekte (synthetisch, kurz, leise) ----------
SFX_RATE = 22050
SFX_MIN_GAP = 0.25             # Mindestabstand zwischen zwei Effekten (Sekunden)
SFX_KIND_GAP = 0.6             # Mindestabstand pro Effekt-Art
SFX_KINDS = ("whoosh", "swish", "thud_soft", "thud_hard", "bump", "clink", "land", "tick", "win")
PHYS_THROW_LINES = ("Wheeee!", "Fliegen kann ich auch!", "Houston, wir haben ein Problem!")
PHYS_SHAKE_LINES = ("Hey, mir wird schwindelig!", "Nicht schütteln, Choom!", "Alle Pixel verrutschen!")
PHYS_HIT_LINES = ("Aua!", "Mein Chrom!", "Das war hart, Choom.")
PHYS_PERCH_LINES = ("Hier oben ist die Aussicht gut.", "Fenster-Parkplatz gefunden!",
                    "Ich bleib mal kurz hier.")

CRAVING_LETTERS = "ABDEFGHKLMNPRSTWZ"
MAX_WORDS = 500

QUOTES = [
    "Naumburg schläft nie. Du solltest es trotzdem tun.",
    "Systemcheck: alles grün. Zumindest bei mir.",
    "Zeit ist Geld."
    "YOLO.",
    "Hast du schon Backups gemacht, Cuh?",
    "Trink Wasser. Sonst rostet auch noch dein Hirn.",
]
PET_LINES = ["Hihi, das kitzelt!", "Mehr davon, Choom.", "Ping! Stimmung steigt.", "Du bist ganz okay."]
FEED_LINES = ["Mmh, frische Datenbrösel!", "Nom nom. Danke!", "Energieriegel erkannt. Lecker."]
NEED_LINES = {
    "food": "Mein Magen knurrt. Füttern bitte!",
    "fun": "Mir ist langweilig. Spielen wir?",
    "energy": "Ich bin müde... Schlafenszeit?",
}
GOODBYE_LINES = (
    "Bis zum nächsten Pixel, Choom! Ich fahr runter.",
    "Tschau mit Wow! NOVA loggt sich aus.",
    "Neon aus, Legende an – bis später!",
    "Ich geh in den Energiesparmodus. Ciao!",
    "Bye-bye, Choom! Bis zum nächsten System-Ping.",
    "Tschüssikowski! Ich speicher mir den Moment.",
    "Mach's gut! Mein Prozessor braucht kurz Pause.",
    "Bis bald – und bleib schön glitchig!",
)


def mix_hex(c1, c2, t):
    """Mischt zwei #rrggbb-Farben (t=0 -> c1, t=1 -> c2)."""
    t = min(1.0, max(0.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


class _Pt:
    """Minimaler Ersatz für ein Mausereignis (nur x und y)."""
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y


def clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


def panel(c, x1, y1, x2, y2, cut=7, fill=PANEL, outline=ACCENT, width=2):
    """Rechteck mit angeschnittenen Ecken (oben links / unten rechts)."""
    pts = [x1 + cut, y1, x2, y1, x2, y2 - cut, x2 - cut, y2, x1, y2, x1, y1 + cut]
    return c.create_polygon(pts, fill=fill, outline=outline, width=width)


# ================= Daten-Farm (Idle-Spiel) =================
IDLE_GROWTH = 1.15                 # Preis pro gekauftem Generator
IDLE_MAX_OWNED = 2000
IDLE_OFFLINE_FACTOR = 0.5
IDLE_OFFLINE_MAX = 12 * 3600
IDLE_BITS_CAP = 1e300
IDLE_REBOOT_MIN = 1e6              # Bits in einem Durchlauf für den ersten Chip
IDLE_CHIP_BONUS = 0.10             # +10 % Produktion pro Chip
IDLE_GENS = (                      # (id, Name, Grundpreis, Bits/s)
    ("bot", "Mini-Bot", 15, 0.1),
    ("miner", "Daten-Miner", 100, 1),
    ("rack", "Server-Rack", 1100, 8),
    ("cluster", "GPU-Cluster", 12000, 47),
    ("quantum", "Quantenkern", 130000, 260),
    ("neural", "Neuronetz", 1.4e6, 1400),
    ("core", "NOVA-Kern", 2e7, 7800),
)
IDLE_UPGRADES = (                  # (id, Name, Beschreibung, Preis, Art, Faktor)
    ("click1", "Turbo-Finger", "Klick x2", 100, "click", 2.0),
    ("mult1", "Übertakten", "Alles x1,5", 1000, "mult", 1.5),
    ("click2", "Makro-Taste", "Klick x3", 2500, "click", 3.0),
    ("mult2", "Kühlsystem", "Alles x2", 25000, "mult", 2.0),
    ("click3", "Auto-Klicker-Chip", "Klick x5", 75000, "click", 5.0),
    ("mult3", "Overclock+", "Alles x2", 500000, "mult", 2.0),
    ("mult4", "Quantenkühlung", "Alles x3", 1e7, "mult", 3.0),
    ("mult5", "NOVA-Segen", "Alles x5", 5e9, "mult", 5.0),
)
IDLE_SUFFIXES = ("", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "Dc")


def fmt_num(value):
    """Große Zahlen kurz: 1.23K, 4.50M ..."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "0"
    if not math.isfinite(value) or value < 0:
        return "0"
    if value < 1000:
        return f"{value:.1f}" if value < 10 and value != int(value) else f"{int(value)}"
    exponent = int(math.log10(value)) // 3
    if exponent >= len(IDLE_SUFFIXES):
        return f"{value:.2e}"
    return f"{value / 1000 ** exponent:.2f}{IDLE_SUFFIXES[exponent]}"


def fmt_duration(seconds):
    seconds = int(max(0, seconds))
    hours, rest = divmod(seconds, 3600)
    minutes = rest // 60
    return f"{hours} h {minutes} min" if hours else f"{minutes} min"


def default_idle():
    return {"bits": 0.0, "total": 0.0, "run": 0.0, "gens": {g[0]: 0 for g in IDLE_GENS}, "upgrades": [],
            "chips": 0, "reboots": 0, "clicks": 0}


def sanitize_idle(raw):
    base = default_idle()
    if not isinstance(raw, dict):
        return base
    for key in ("bits", "total", "run"):
        try:
            value = float(raw.get(key, 0.0))
        except (TypeError, ValueError):
            value = 0.0
        base[key] = min(IDLE_BITS_CAP, value) if math.isfinite(value) and value > 0 else 0.0
    for key in ("chips", "reboots", "clicks"):
        try:
            base[key] = max(0, int(raw.get(key, 0)))
        except (TypeError, ValueError, OverflowError):
            base[key] = 0
    gens = raw.get("gens", {})
    for gid, *_ in IDLE_GENS:
        try:
            base["gens"][gid] = min(IDLE_MAX_OWNED, max(0, int(gens.get(gid, 0))))
        except (TypeError, ValueError, AttributeError):
            base["gens"][gid] = 0
    owned = raw.get("upgrades", [])
    valid = {u[0] for u in IDLE_UPGRADES}
    base["upgrades"] = [u for u in dict.fromkeys(owned) if u in valid] if isinstance(owned, list) else []
    return base


# ================= Werkzeuge: Timer, Erinnerungen, Autoclicker =================
AC_BUTTONS = {"left": "Links", "right": "Rechts", "middle": "Mitte"}
AC_MAX_POINTS = 8
AC_BLOCK_SECONDS = 10      # so lange darf die Maus auf einem NOVA-Fenster liegen, bevor gestoppt wird
AC_PRESETS = ((50, "50ms"), (100, "100ms"), (500, "0,5s"), (1000, "1s"), (5000, "5s"))
REMINDER_MAX = 30
_UNIT = r"(?:stunden?|std|h|minuten?|min|m|sekunden?|sek|s)"


def parse_duration(text):
    """'25' (Minuten), '1h30', '90s', '5 min', '1:30' (mm:ss), '1:00:00' -> Sekunden oder None."""
    t = str(text).strip().lower().replace(",", ".")
    if not t:
        return None
    clock = re.fullmatch(r"(\d{1,3}):(\d{2})(?::(\d{2}))?", t)
    if clock:
        a, b, c = clock.groups()
        seconds = (int(a) * 3600 + int(b) * 60 + int(c)) if c is not None else int(a) * 60 + int(b)
    else:
        if not re.fullmatch(rf"(?:\s*\d+(?:\.\d+)?\s*{_UNIT}?)+", t):
            return None
        seconds = 0.0
        for number, name in re.findall(rf"(\d+(?:\.\d+)?)\s*({_UNIT})?", t):
            value = float(number)
            if name.startswith(("h", "std", "stund")):
                seconds += value * 3600
            elif name.startswith("s"):
                seconds += value
            else:                                   # Minuten, auch ohne Einheit
                seconds += value * 60
    seconds = int(round(seconds))
    return seconds if 1 <= seconds <= 86400 else None


def fmt_clock(seconds):
    seconds = int(max(0, math.ceil(seconds)))
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"


def parse_interval(text):
    """'500' / '500ms' (Millisekunden), '1.5s', '2min' -> Millisekunden (10 ms bis 1 h) oder None."""
    t = str(text).strip().lower().replace(",", ".")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(ms|msec|millisekunden?|s|sek|sekunden?|min|minuten?)?", t)
    if not m:
        return None
    value, unit = float(m.group(1)), m.group(2) or "ms"
    if unit.startswith(("ms", "milli")):
        ms = value
    elif unit.startswith("min"):
        ms = value * 60000
    else:
        ms = value * 1000
    ms = int(round(ms))
    return ms if 10 <= ms <= 3600000 else None


def fmt_interval(ms):
    ms = int(ms)
    if ms % 60000 == 0:
        return f"{ms // 60000}min"
    if ms % 1000 == 0:
        return f"{ms // 1000}s"
    return f"{ms}ms"


def fmt_when(ts):
    try:
        moment = datetime.datetime.fromtimestamp(ts)
    except (OverflowError, OSError, ValueError):
        return "?"
    today = datetime.date.today()
    if moment.date() == today:
        return moment.strftime("%H:%M")
    if moment.date() == today + datetime.timedelta(days=1):
        return "morgen " + moment.strftime("%H:%M")
    return moment.strftime("%d.%m. %H:%M")


def parse_reminder(text, now=None):
    """'14:30 Text', '20m Text', 'in 5 min Text', 'täglich 8:00 Text' -> (fällig, Text, Wiederholung)."""
    now = time.time() if now is None else now
    t = re.sub(r"\s+", " ", str(text)).strip()
    repeat = ""
    m = re.match(r"^(?:täglich|taeglich|jeden tag)\s+(.+)$", t, re.IGNORECASE)
    if m:
        repeat, t = "daily", m.group(1)
    t = re.sub(r"^(?:in|um)\s+", "", t, flags=re.IGNORECASE)
    label, due = "", None
    m = re.match(r"^(\d{1,2}):(\d{2})(?:\s*uhr)?\s+(.+)$", t, re.IGNORECASE)
    if m:
        hour, minute, label = int(m.group(1)), int(m.group(2)), m.group(3)
        if hour > 23 or minute > 59:
            return None
        target = datetime.datetime.fromtimestamp(now).replace(
            hour=hour, minute=minute, second=0, microsecond=0)
        if target.timestamp() <= now:
            target += datetime.timedelta(days=1)
        due = target.timestamp()
    else:
        repeat = ""                                    # Wiederholung gibt es nur bei Uhrzeiten
        seconds = None
        m = re.match(rf"^(\d+(?:[.,]\d+)?)\s*({_UNIT})\s+(.+)$", t, re.IGNORECASE)
        if m:
            seconds = parse_duration(m.group(1) + m.group(2))
            label = m.group(3)
        else:
            parts = t.split(" ", 1)
            if len(parts) == 2 and ":" not in parts[0]:
                seconds = parse_duration(parts[0])
                label = parts[1]
        if seconds is None:
            return None
        due = now + seconds
    label = label.strip()[:80]
    return (due, label, repeat) if label else None


def sanitize_timer(raw):
    base = {"end": 0.0, "total": 0.0, "label": ""}
    if not isinstance(raw, dict):
        return base
    try:
        end, total = float(raw.get("end", 0.0)), float(raw.get("total", 0.0))
    except (TypeError, ValueError):
        return base
    if not (math.isfinite(end) and math.isfinite(total)) or end <= 0 or total <= 0:
        return base
    label = raw.get("label", "")
    label = re.sub(r"[\x00-\x1f\x7f]", "", label).strip()[:20] if isinstance(label, str) else ""
    return {"end": end, "total": min(total, 86400.0), "label": label or "Timer"}


def sanitize_reminders(raw):
    items = []
    if not isinstance(raw, list):
        return items
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            due = float(item.get("due", 0.0))
        except (TypeError, ValueError):
            continue
        if not math.isfinite(due) or due <= 0:
            continue
        text = item.get("text", "")
        text = re.sub(r"[\x00-\x1f\x7f]", "", text).strip()[:80] if isinstance(text, str) else ""
        items.append({"due": due, "text": text or "Erinnerung",
                      "repeat": "daily" if item.get("repeat") == "daily" else ""})
    items.sort(key=lambda r: r["due"])
    return items[:REMINDER_MAX]


def default_autoclicker():
    return {"interval_ms": 1000, "button": "left", "double": False, "max_clicks": 0,
            "delay": 3, "points": [], "minimize": True}


def sanitize_autoclicker(raw):
    base = default_autoclicker()
    if not isinstance(raw, dict):
        return base
    for key, lo, hi in (("interval_ms", 10, 3600000), ("max_clicks", 0, 1000000), ("delay", 0, 30)):
        try:
            base[key] = min(hi, max(lo, int(raw.get(key, base[key]))))
        except (TypeError, ValueError, OverflowError):
            pass
    if raw.get("button") in AC_BUTTONS:
        base["button"] = raw["button"]
    base["double"] = bool(raw.get("double", False))
    base["minimize"] = bool(raw.get("minimize", True))
    points = []
    if isinstance(raw.get("points"), list):
        for point in raw["points"]:
            try:
                x, y = int(point[0]), int(point[1])
            except (TypeError, ValueError, IndexError, KeyError, OverflowError):
                continue
            if -32768 <= x <= 32767 and -32768 <= y <= 32767:
                points.append([x, y])
    base["points"] = points[:AC_MAX_POINTS]
    return base


# ================= Soundeffekte =================
def _sfx_wav(samples):
    frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32767)) for v in samples)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SFX_RATE)
        w.writeframes(frames)
    return buf.getvalue()


def synth_sfx(kind):
    """Erzeugt einen kurzen, leisen Effekt als WAV-Bytes (keine Dateien nötig)."""
    rnd = random.Random(7)
    count = lambda dur: int(SFX_RATE * dur)
    out = []
    if kind in ("whoosh", "swish"):
        dur, amp, hi = (0.22, 0.26, 0.35) if kind == "whoosh" else (0.16, 0.14, 0.5)
        y = 0.0
        for i in range(count(dur)):
            p = i / SFX_RATE / dur
            y += (0.04 + hi * math.sin(math.pi * p)) * (rnd.uniform(-1, 1) - y)   # Filter öffnet/schließt
            out.append(y * amp * 1.5 * math.sin(math.pi * p) ** 1.5)
    elif kind in ("thud_soft", "thud_hard"):
        amp = 0.26 if kind == "thud_soft" else 0.42
        phase = 0.0
        for i in range(count(0.18)):
            t = i / SFX_RATE
            phase += 2 * math.pi * (55 + 45 * math.exp(-t * 30)) / SFX_RATE
            out.append(amp * (math.sin(phase) * math.exp(-t * 20)
                              + 0.5 * rnd.uniform(-1, 1) * math.exp(-t * 140)))
    elif kind == "bump":
        for i in range(count(0.09)):
            t = i / SFX_RATE
            out.append(0.2 * (math.sin(2 * math.pi * 260 * t) + 0.5 * math.sin(2 * math.pi * 520 * t))
                       * math.exp(-t * 48))
    elif kind == "clink":
        for i in range(count(0.15)):
            t = i / SFX_RATE
            out.append(0.15 * (math.sin(2 * math.pi * 880 * t) + 0.6 * math.sin(2 * math.pi * 1320 * t))
                       * math.exp(-t * 36))
    elif kind == "land":
        for i in range(count(0.09)):
            t = i / SFX_RATE
            out.append(0.18 * (math.sin(2 * math.pi * 190 * t) * math.exp(-t * 50)
                               + 0.4 * rnd.uniform(-1, 1) * math.exp(-t * 200)))
    elif kind == "tick":
        for i in range(count(0.03)):
            t = i / SFX_RATE
            out.append(0.22 * math.sin(2 * math.pi * 1900 * t) * math.exp(-t * 160))
    elif kind == "win":
        for n, f in enumerate((660, 880, 1320)):
            for i in range(count(0.14)):
                t = i / SFX_RATE
                out.append(0.16 * math.sin(2 * math.pi * f * t) * math.exp(-t * 9))
    else:
        return b""
    fade = min(len(out) // 4, 120)                 # kurz ein-/ausblenden gegen Knacken
    for i in range(fade):
        out[i] *= i / fade
        out[-1 - i] *= i / fade
    return _sfx_wav(out)


# ================= Speicherstand =================
def default_daily():
    return {"claimed": "", "day": "", "streak": 0, "ids": [], "prog": {}, "paid": []}


def sanitize_daily(raw):
    d = default_daily()
    if not isinstance(raw, dict):
        return d
    for k in ("claimed", "day"):
        v = raw.get(k, "")
        d[k] = v[:10] if isinstance(v, str) else ""
    try:
        d["streak"] = max(0, min(9999, int(raw.get("streak", 0))))
    except (TypeError, ValueError):
        pass
    ids = raw.get("ids")
    d["ids"] = [q for q in ids if q in QUESTS][:3] if isinstance(ids, list) else []
    prog = raw.get("prog") if isinstance(raw.get("prog"), dict) else {}
    for q in d["ids"]:
        try:
            d["prog"][q] = max(0, int(prog.get(q, 0)))
        except (TypeError, ValueError):
            d["prog"][q] = 0
    paid = raw.get("paid")
    d["paid"] = [q for q in paid if q in d["ids"] or q == "bonus"] if isinstance(paid, list) else []
    return d


def default_state():
    return {"food": 80.0, "fun": 80.0, "energy": 80.0,
            "points": 0, "xp": 0, "name": "", "owned": [], "worn": [], "acc_pos": {}, "words": {},
            "emotion_images": {}, "emotion_texts": {}, "emotion_setup_done": False,
            "highscores": {}, "window_mode": False, "mini_auto": True,
            "mini_manual": False, "walking": True, "voice_enabled": False,
            "phone_mode": False, "phone_image": "", "phone_talk_image": "",
            "living_mode": False, "sys_monitor": False, "synth_voice": True,
            "controlled_apps": [], "fav_apps": [], "notes": "", "spotify_mode": True, "physics": True, "sfx": True,
            "fps": 30, "bubble_dy": 0, "hud_dy": 0, "sprite_scale": 1.0, "foot_pct": 0.0, "foot_sit": 0.0, "foot_air": 0.0, "ground_offset": 0,
            "idle": default_idle(), "timer": {"end": 0.0, "total": 0.0, "label": ""},
            "reminders": [], "autoclicker": default_autoclicker(),
            "ai_enabled": False, "ai_provider": "gemini",
            "ai_model": os.environ.get("OLLAMA_MODEL") or OLLAMA_DEFAULT_MODEL,
            "daily": default_daily(), "last_goodbye": "", "last": time.time()}


def sanitize_state(state):
    """Prüft geladene Werte, damit eine beschädigte Datei das Programm nicht stoppt."""
    base = default_state()
    for k in ("food", "fun", "energy"):
        try:
            state[k] = clamp(float(state.get(k, base[k])))
        except (TypeError, ValueError):
            state[k] = base[k]
    for k in ("points", "xp"):
        try:
            state[k] = max(0, int(state.get(k, 0)))
        except (TypeError, ValueError):
            state[k] = 0
    try:
        state["last"] = float(state.get("last", time.time()))
    except (TypeError, ValueError):
        state["last"] = time.time()
    name = state.get("name", "")
    state["name"] = name if isinstance(name, str) else ""
    last_goodbye = state.get("last_goodbye", "")
    state["last_goodbye"] = last_goodbye if isinstance(last_goodbye, str) else ""
    state["daily"] = sanitize_daily(state.get("daily"))
    for k in ("owned", "worn"):
        value = state.get(k, [])
        state[k] = [x for x in value if x in SHOP] if isinstance(value, list) else []
    pos = state.get("acc_pos")
    state["acc_pos"] = {k: [float(v[0]), float(v[1]), float(v[2])] for k, v in pos.items()
                        if k in SHOP and isinstance(v, (list, tuple)) and len(v) == 3
                        and all(isinstance(n, (int, float)) for n in v)} if isinstance(pos, dict) else {}
    for k in ("words", "emotion_images", "emotion_texts", "highscores"):
        if not isinstance(state.get(k), dict):
            state[k] = {}
    for k in ("emotion_images", "emotion_texts"):      # alt: "music" -> "sit"
        if "music" in state[k]:
            state[k].setdefault("sit", state[k]["music"])
            del state[k]["music"]
    scores = {}
    for mode in GAME_LABELS:
        try:
            scores[mode] = max(0, int(state["highscores"].get(mode, 0)))
        except (TypeError, ValueError):
            scores[mode] = 0
    state["highscores"] = scores
    words = {}
    for word, count in state["words"].items():
        try:
            words[str(word)[:20]] = max(1, int(count))
        except (TypeError, ValueError):
            words[str(word)[:20]] = 1
    state["words"] = dict(list(words.items())[:MAX_WORDS])
    for k in ("emotion_setup_done", "window_mode", "mini_auto", "mini_manual",
              "walking", "voice_enabled", "phone_mode", "living_mode",
              "sys_monitor", "synth_voice", "ai_enabled", "spotify_mode", "physics", "sfx"):
        state[k] = bool(state.get(k, base[k]))
    for k, lo, hi in (("bubble_dy", -90, 280), ("hud_dy", 0, 320)):
        try:
            state[k] = min(hi, max(lo, int(state.get(k, 0))))
        except (TypeError, ValueError):
            state[k] = 0
    try:
        state["fps"] = min(60, max(30, int(state.get("fps", 30))))
    except (TypeError, ValueError):
        state["fps"] = 30
    for k, lo, hi in (("sprite_scale", SPRITE_SCALE_MIN, SPRITE_SCALE_MAX),
                      ("foot_pct", 0.0, FOOT_PCT_MAX), ("foot_sit", 0.0, FOOT_PCT_MAX),
                      ("foot_air", 0.0, FOOT_PCT_MAX)):
        try:
            value = float(state.get(k, base[k]))
            state[k] = min(hi, max(lo, value)) if math.isfinite(value) else base[k]
        except (TypeError, ValueError):
            state[k] = base[k]
    try:
        state["ground_offset"] = int(min(GROUND_OFFSET_MAX, max(
            GROUND_OFFSET_MIN, round(float(state.get("ground_offset", 0))))))
    except (TypeError, ValueError, OverflowError):
        state["ground_offset"] = 0
    for k in ("phone_image", "phone_talk_image"):
        val = state.get(k, "")
        if not isinstance(val, str):
            val = ""
        state[k] = re.sub(r"[\x00-\x1f\x7f]", "", val).strip()[:2048]
    for old, new in (("phone_image", "phone"), ("phone_talk_image", "phone_talk")):
        if state[old] and not state["emotion_images"].get(new):
            state["emotion_images"][new] = state[old]      # Telefonbilder jetzt als Emotionen
        state[old] = ""
    apps = state.get("controlled_apps", [])
    if not isinstance(apps, list):
        apps = []
    state["controlled_apps"] = list(dict.fromkeys(
        re.sub(r"[\x00-\x1f\x7f]", "", path).strip()[:2048]
        for path in apps
        if isinstance(path, str) and path.lower().endswith(".exe")
    ))[:6]
    notes = state.get("notes", "")
    state["notes"] = notes[:20000] if isinstance(notes, str) else ""
    favs = state.get("fav_apps", [])
    state["fav_apps"] = [x for x in dict.fromkeys(favs if isinstance(favs, list) else [])
                         if x in state["controlled_apps"]][:4]
    if state.get("ai_provider") not in ("gemini", "openai", "openrouter", "ollama"):
        state["ai_provider"] = base["ai_provider"]
    model = state.get("ai_model", base["ai_model"])
    if not isinstance(model, str):
        model = base["ai_model"]
    model = re.sub(r"[\x00-\x1f\x7f]", "", model).strip()[:128]
    if model == "gemma3:4b" and not os.environ.get("OLLAMA_MODEL"):
        model = OLLAMA_DEFAULT_MODEL
    state["ai_model"] = model or OLLAMA_DEFAULT_MODEL
    state["idle"] = sanitize_idle(state.get("idle"))
    state["timer"] = sanitize_timer(state.get("timer"))
    state["reminders"] = sanitize_reminders(state.get("reminders"))
    state["autoclicker"] = sanitize_autoclicker(state.get("autoclicker"))
    return state


def load_state():
    """Lädt den Spielstand (mit Sicherung) und ergänzt neue Optionen."""
    state = default_state()
    for path in (SAVE_FILE, SAVE_FILE + ".bak"):
        try:
            with open(path, encoding="utf-8") as f:
                saved = json.load(f)
            if not isinstance(saved, dict):
                continue
            state.update(saved)
            if "xp" not in saved:
                state["xp"] = max(0, int(state.get("points", 0)))
            break
        except (OSError, ValueError):
            continue
    return sanitize_state(state)


def write_json_atomic(path, data):
    """Schreibt erst in eine Temp-Datei, sichert die alte Datei und ersetzt dann."""
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        if os.path.exists(path):
            try:
                shutil.copy2(path, path + ".bak")
            except OSError:
                pass
        os.replace(tmp, path)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def sanitize_ai_memory(history):
    if not isinstance(history, list):
        raise ValueError("Die lokale KI-Erinnerung hat ein ungültiges Format.")
    cleaned = []
    image_labels = {
        "Dieses Bild zeigt ausschließlich mein neutrales NOVA-Avatarbild.",
        "Dieses Bild ist nur eine visuelle Referenz für mein neutrales Avatar. Beschreibe es nicht ungefragt.",
        "Dieses Bild ist das vom Nutzer bestätigte Bildschirmfoto.",
    }
    for turn in history:
        if not isinstance(turn, dict) or turn.get("role") not in ("user", "model"):
            continue
        parts = turn.get("parts")
        if not isinstance(parts, list):
            continue
        text = "\n".join(
            part["text"] for part in parts
            if isinstance(part, dict) and isinstance(part.get("text"), str)
            and part["text"] not in image_labels
        ).strip()[:4000]
        if text:
            cleaned.append({"role": turn["role"], "parts": [{"text": text}]})
    return cleaned[-AI_MEMORY_MAX_TURNS:]


def load_ai_memory():
    try:
        with open(AI_MEMORY_FILE, encoding="utf-8") as memory_file:
            history = json.load(memory_file)
    except FileNotFoundError:
        return []
    return sanitize_ai_memory(history)


# ================= Bilder =================
def validate_image(path):
    """True, wenn Pillow die Datei als Bild öffnen kann."""
    if Image is None:
        return False
    try:
        with Image.open(path) as im:
            im.verify()
        return True
    except Exception:
        return False


def make_thumb(path, size=44):
    """Kleine Vorschau für den Emotionseditor."""
    if Image is None or not path or not os.path.isfile(path):
        return None
    try:
        im = Image.open(path).convert("RGBA")
        im.thumbnail((size, size))
        bg = Image.new("RGBA", (size, size), (11, 5, 6, 255))
        bg.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
        return ImageTk.PhotoImage(bg)
    except (OSError, ValueError):
        return None


# ---------- Eigenes Interface: rahmenlose Fenster, Dialoge, Dateiauswahl ----------
# Alle NOVA-Fenster (Farm, Autoclicker, Emotionen, Größe, KI-Chat, Dialoge, Dateiauswahl)
# benutzen statt des Windows-Fensterrahmens eine eigene rot/schwarze Titelleiste.
CUSTOM_WINDOWS = []                 # alle offenen NOVA-Fenster (für die Eigene-Fenster-Erkennung)
_LAST_FILE_DIR = {"path": ""}       # zuletzt benutzter Ordner der Dateiauswahl
ORANGE = "#ff7a2f"


def _live_parent(parent):
    """Gibt ein noch existierendes Elternfenster zurück (sonst das Hauptfenster)."""
    for candidate in (parent, tk._default_root):
        if candidate is None:
            continue
        try:
            if candidate.winfo_exists():
                return candidate
        except tk.TclError:
            continue
    return None


def nova_button(parent, text, command, primary=False, width=None):
    """Flacher Knopf im NOVA-Stil (primär = leuchtend rot)."""
    options = {"width": width} if width else {}
    return tk.Button(parent, text=text, command=command, relief="flat", bd=0, cursor="hand2",
                     bg=ACCENT if primary else PANEL2, fg=PANEL if primary else LIGHT,
                     activebackground=LIGHT if primary else EDGE,
                     activeforeground=PANEL if primary else LIGHT,
                     font=("Consolas", 10, "bold" if primary else "normal"),
                     padx=14, pady=5, **options)


class NovaToplevel(tk.Toplevel):
    """Rahmenloses NOVA-Fenster mit eigener Titelleiste statt Windows-Rahmen.

    Verhält sich wie ein normales Toplevel: Inhalt wird einfach in das Fenster gepackt.
    - Titelleiste: ziehen = verschieben, ✕ = schließen (ruft den WM_DELETE_WINDOW-Handler auf)
    - Größen aus geometry()/minsize() gelten für den Inhalt (Titelleiste und Rahmen kommen dazu)
    - ohne Positionsangabe wird das Fenster automatisch zentriert (optional über `anchor`)
    - resizable(True, ...) zeigt unten rechts einen Anfasser zum Vergrößern
    - iconify() blendet das Fenster aus (ohne Rahmen gibt es keine Taskleiste); deiconify() zeigt es
    """
    TITLE_H = 30
    BORDER = 2
    CLOSE_W = 48

    def __init__(self, master=None, anchor=None, **kw):
        super().__init__(master, bg=PANEL, highlightthickness=self.BORDER,
                         highlightbackground=ACCENT, highlightcolor=ACCENT, **kw)
        self._title_text = ""
        self._close_cmd = None
        self._anchor = anchor
        self._placed = False
        self._sized = False
        self._can_resize = True
        self._min_size = (0, 0)
        self._drag = None
        self._press_close = False
        self._close_hot = False
        self._grip_start = None
        self.overrideredirect(True)
        try:
            self.attributes("-alpha", 0.0)       # unsichtbar, bis Größe/Position stehen
        except tk.TclError:
            pass

        self._bar = tk.Canvas(self, height=self.TITLE_H, bg=PANEL2, highlightthickness=0, bd=0)
        self._bar.pack(side="top", fill="x")
        self._bar.bind("<Configure>", self._draw_bar)
        self._bar.bind("<ButtonPress-1>", self._bar_press)
        self._bar.bind("<B1-Motion>", self._bar_motion)
        self._bar.bind("<ButtonRelease-1>", self._bar_release)
        self._bar.bind("<Motion>", self._bar_hover)
        self._bar.bind("<Leave>", self._bar_leave)

        self._grip = tk.Label(self, text="◢", bg=PANEL, fg=ACCENT, bd=0, cursor="size_nw_se",
                              font=("Consolas", 10))
        self._grip.bind("<ButtonPress-1>", self._grip_press)
        self._grip.bind("<B1-Motion>", self._grip_motion)
        self._grip.place(relx=1.0, rely=1.0, x=-3, y=-3, anchor="se")

        self.bind("<Button-1>", self._take_focus, add="+")
        CUSTOM_WINDOWS.append(self)
        self.after_idle(self._show)

    # ---------- Tk-Methoden, die der Rahmen kennen muss ----------
    def title(self, string=None):
        if string is None:
            return self._title_text
        self._title_text = str(string)
        self._draw_bar()
        return super().title(string)

    def protocol(self, name=None, func=None):
        if name == "WM_DELETE_WINDOW" and func is not None:
            self._close_cmd = func
        return super().protocol(name, func)

    def resizable(self, width=None, height=None):
        if width is None and height is None:
            return super().resizable()
        self._can_resize = bool(width) or bool(height)
        if self._can_resize:
            self._grip.place(relx=1.0, rely=1.0, x=-3, y=-3, anchor="se")
            self._grip.tkraise()
        else:
            self._grip.place_forget()
        return super().resizable(width, height)

    def minsize(self, width=None, height=None):
        if width is None and height is None:
            return super().minsize()
        self._min_size = (int(width) + 2 * self.BORDER,
                          int(height) + self.TITLE_H + 2 * self.BORDER)
        return super().minsize(*self._min_size)

    def geometry(self, newGeometry=None):
        if newGeometry is None:
            return super().geometry()
        spec = str(newGeometry)
        match = re.match(r"^(\d+)x(\d+)(.*)$", spec)
        if match:
            self._sized = True
            spec = (f"{int(match.group(1)) + 2 * self.BORDER}x"
                    f"{int(match.group(2)) + self.TITLE_H + 2 * self.BORDER}{match.group(3)}")
        if re.search(r"[+-]-?\d+[+-]-?\d+$", spec):
            self._placed = True
        return super().geometry(spec)

    def iconify(self):
        self.withdraw()

    def deiconify(self):
        super().deiconify()
        try:
            self.attributes("-topmost", True)
        except tk.TclError:
            pass
        self.lift()

    def destroy(self):
        try:
            CUSTOM_WINDOWS.remove(self)
        except ValueError:
            pass
        super().destroy()

    def close(self):
        """✕ in der Titelleiste: wie das Schließen eines normalen Fensters."""
        if self._close_cmd is not None:
            self._close_cmd()
        else:
            self.destroy()

    # ---------- Anzeigen / Platzieren ----------
    def _show(self):
        try:
            if not self.winfo_exists():
                return
            if not self._placed:
                self.update_idletasks()
                width, height = self.winfo_reqwidth(), self.winfo_reqheight()
                if self._sized:
                    match = re.match(r"(\d+)x(\d+)", super().geometry())
                    if match:
                        width, height = int(match.group(1)), int(match.group(2))
                screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
                ax, ay, aw, ah = 0, 0, screen_w, screen_h
                anchor = self._anchor
                if anchor is not None:
                    try:
                        if anchor.winfo_viewable():
                            ax, ay = anchor.winfo_rootx(), anchor.winfo_rooty()
                            aw, ah = anchor.winfo_width(), anchor.winfo_height()
                    except tk.TclError:
                        pass
                x = max(0, min(ax + (aw - width) // 2, screen_w - width))
                y = max(0, min(ay + (ah - height) // 2, screen_h - height))
                super().geometry(f"+{x}+{y}")
                self._placed = True
            self.attributes("-alpha", 1.0)
            self.lift()
            if self._can_resize:
                self._grip.tkraise()
            self.focus_force()
        except tk.TclError:
            pass

    def _take_focus(self, event):
        """Rahmenlose Fenster bekommen unter Windows Tastatureingaben nur per focus_force."""
        try:
            if self.focus_displayof() is None:
                self.focus_force()
                if isinstance(event.widget, (tk.Entry, tk.Text, tk.Listbox, tk.Spinbox)):
                    event.widget.focus_set()
        except tk.TclError:
            pass

    # ---------- Titelleiste ----------
    def _draw_bar(self, _event=None):
        bar = getattr(self, "_bar", None)
        if bar is None:
            return
        try:
            width = max(bar.winfo_width(), 120)
        except tk.TclError:
            return
        h = self.TITLE_H
        bar.delete("all")
        bar.create_rectangle(0, 0, width, h, fill=PANEL2, outline="")
        bar.create_polygon(0, 0, 22, 0, 12, h, 0, h, fill=ACCENT, outline="")
        bar.create_polygon(28, 0, 34, 0, 24, h, 18, h, fill=EDGE, outline="")
        bar.create_text(48, h // 2, text=self._title_text.upper(), anchor="w", fill=LIGHT,
                        font=("Consolas", 10, "bold"))
        cw = self.CLOSE_W
        bar.create_polygon(width - cw + 8, 0, width, 0, width, h, width - cw, h,
                           fill=ACCENT if self._close_hot else EDGE, outline="", tags="closebg")
        bar.create_text(width - cw // 2 + 4, h // 2, text="✕", fill=LIGHT,
                        font=("Consolas", 11, "bold"))
        bar.create_line(0, h - 1, width, h - 1, fill=EDGE)

    def _in_close_zone(self, event):
        return event.x >= self._bar.winfo_width() - self.CLOSE_W

    def _bar_press(self, event):
        self._press_close = self._in_close_zone(event)
        self._drag = None
        if not self._press_close:
            self._drag = (event.x_root - self.winfo_x(), event.y_root - self.winfo_y())

    def _bar_motion(self, event):
        if self._drag is None:
            return
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        x = min(max(event.x_root - self._drag[0], 120 - self.winfo_width()), screen_w - 120)
        y = min(max(event.y_root - self._drag[1], 0), screen_h - self.TITLE_H)
        super().geometry(f"+{x}+{y}")
        self._placed = True

    def _bar_release(self, event):
        pressed_close = self._press_close
        self._press_close = False
        self._drag = None
        if pressed_close and self._in_close_zone(event) and 0 <= event.y <= self.TITLE_H:
            self.close()

    def _bar_hover(self, event):
        hot = self._in_close_zone(event)
        if hot != self._close_hot:
            self._close_hot = hot
            self._bar.itemconfigure("closebg", fill=ACCENT if hot else EDGE)

    def _bar_leave(self, _event):
        if self._close_hot:
            self._close_hot = False
            self._bar.itemconfigure("closebg", fill=EDGE)

    # ---------- Größe ändern (Anfasser unten rechts) ----------
    def _grip_press(self, event):
        self._grip_start = (event.x_root, event.y_root, self.winfo_width(), self.winfo_height())

    def _grip_motion(self, event):
        if self._grip_start is None:
            return
        x0, y0, w0, h0 = self._grip_start
        min_w, min_h = self._min_size
        width = max(min_w, 260, w0 + event.x_root - x0)
        height = max(min_h, 160, h0 + event.y_root - y0)
        super().geometry(f"{width}x{height}")


class _NovaMessageBox:
    """Ersatz für tkinter.messagebox im NOVA-Stil (gleiche Aufrufe, rahmenloses Fenster)."""
    ICONS = {"info": ("i", ACCENT), "warning": ("!", ORANGE),
             "error": ("✕", ACCENT), "question": ("?", ACCENT)}

    def _run(self, kind, title, message, opts, buttons, default, cancel):
        parent = _live_parent(opts.get("parent"))
        text = str(message if message is not None else "")
        if opts.get("detail"):
            text += "\n\n" + str(opts["detail"])
        win = NovaToplevel(parent, anchor=parent if isinstance(parent, NovaToplevel) else None)
        win.title(title or "NOVA")
        win.attributes("-topmost", True)
        result = {"value": cancel}

        def done(value):
            result["value"] = value
            try:
                win.grab_release()
            except tk.TclError:
                pass
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", lambda: done(cancel))
        win.bind("<Return>", lambda e: done(default))
        win.bind("<Escape>", lambda e: done(cancel))

        glyph, color = self.ICONS[kind]
        body = tk.Frame(win, bg=PANEL)
        body.pack(fill="both", expand=True, padx=18, pady=(16, 8))
        icon = tk.Canvas(body, width=46, height=46, bg=PANEL, highlightthickness=0)
        icon.create_polygon(23, 2, 44, 23, 23, 44, 2, 23, fill=PANEL2, outline=color, width=2)
        icon.create_text(23, 23, text=glyph, fill=color, font=("Consolas", 16, "bold"))
        icon.pack(side="left", anchor="n", padx=(0, 14))
        tk.Label(body, text=text, bg=PANEL, fg=LIGHT, font=("Consolas", 10), justify="left",
                 anchor="w", wraplength=420).pack(side="left", fill="both", expand=True)

        row = tk.Frame(win, bg=PANEL)
        row.pack(fill="x", padx=18, pady=(6, 16))
        for label, value in reversed(buttons):
            nova_button(row, label, lambda v=value: done(v),
                        primary=value == default, width=8).pack(side="right", padx=(8, 0))
        _run_modal(win, parent)
        return result["value"]

    def _call(self, native, kind, title, message, opts, buttons, default, cancel):
        try:
            return self._run(kind, title, message, opts, buttons, default, cancel)
        except (tk.TclError, RuntimeError):
            return native(title, message, **opts)

    def showinfo(self, title=None, message=None, **opts):
        return self._call(_native_messagebox.showinfo, "info", title, message, opts,
                          [("OK", "ok")], "ok", "ok")

    def showwarning(self, title=None, message=None, **opts):
        return self._call(_native_messagebox.showwarning, "warning", title, message, opts,
                          [("OK", "ok")], "ok", "ok")

    def showerror(self, title=None, message=None, **opts):
        return self._call(_native_messagebox.showerror, "error", title, message, opts,
                          [("OK", "ok")], "ok", "ok")

    def askyesno(self, title=None, message=None, **opts):
        return bool(self._call(_native_messagebox.askyesno, "question", title, message, opts,
                               [("Ja", True), ("Nein", False)], True, False))


def _run_modal(win, parent):
    """Zeigt ein Fenster modal und merkt sich einen vorher aktiven Grab (z. B. Emotionsfenster)."""
    previous = None
    try:
        previous = parent.grab_current() if parent is not None else None
    except tk.TclError:
        previous = None
    try:
        win.wait_visibility()
        win.grab_set()
    except tk.TclError:
        pass
    win.wait_window(win)
    if previous is not None:
        try:
            if previous.winfo_exists():
                previous.grab_set()
        except tk.TclError:
            pass


class _NovaFileDialog:
    """Ersatz für filedialog.askopenfilename im NOVA-Stil (Ordner, Laufwerke, Dateifilter)."""

    def askopenfilename(self, **opts):
        try:
            return self._run(opts)
        except (tk.TclError, RuntimeError):
            return _native_filedialog.askopenfilename(**opts)

    def _run(self, opts):
        parent = _live_parent(opts.get("parent"))
        filters = []
        for entry in (opts.get("filetypes") or (("Alle Dateien", "*.*"),)):
            label, patterns = entry[0], entry[1]
            if isinstance(patterns, str):
                patterns = patterns.split()
            filters.append((str(label), [str(p).lower() for p in patterns]))
        home = os.path.expanduser("~")
        state = {"dir": "", "filter": 0, "result": "", "entries": []}

        win = NovaToplevel(parent, anchor=parent if isinstance(parent, NovaToplevel) else None)
        win.title(opts.get("title") or "Datei auswählen")
        win.attributes("-topmost", True)
        win.geometry("660x470")
        win.minsize(560, 380)
        win.resizable(True, True)

        path_var = tk.StringVar(master=win)
        name_var = tk.StringVar(master=win)
        filter_var = tk.StringVar(master=win, value=filters[0][0])

        def matches(name):
            lowered = name.lower()
            for pattern in filters[state["filter"]][1]:
                if pattern in ("*", "*.*") or fnmatch.fnmatch(lowered, pattern):
                    return True
            return False

        def is_hidden(entry):
            if entry.name.startswith("."):
                return True
            try:
                return bool(getattr(entry.stat(), "st_file_attributes", 0) & 0x6)
            except OSError:
                return False

        def go(path):
            path = os.path.abspath(path)
            if not os.path.isdir(path):
                status.config(text="Ordner nicht gefunden.")
                return
            dirs, files = [], []
            try:
                with os.scandir(path) as scan:
                    for entry in scan:
                        try:
                            if is_hidden(entry):
                                continue
                            if entry.is_dir():
                                dirs.append(entry.name)
                            elif matches(entry.name):
                                files.append(entry.name)
                        except OSError:
                            continue
            except OSError as err:
                status.config(text=f"Kein Zugriff: {err.strerror or err}")
                return
            dirs.sort(key=str.lower)
            files.sort(key=str.lower)
            state["dir"] = path
            _LAST_FILE_DIR["path"] = path
            path_var.set(path)
            name_var.set("")
            listing.delete(0, "end")
            entries = []
            if os.path.dirname(path) != path:
                entries.append(("up", ".."))
            entries += [("dir", name) for name in dirs] + [("file", name) for name in files]
            for kind, name in entries:
                listing.insert("end", f"▸ {name}" if kind != "file" else f"   {name}")
                if kind != "file":
                    listing.itemconfigure("end", fg=ACCENT)
            state["entries"] = entries
            status.config(text=f"{len(dirs)} Ordner · {len(files)} passende Dateien")

        def selected():
            picked = listing.curselection()
            if not picked:
                return None
            return state["entries"][picked[0]]

        def finish(path):
            state["result"] = os.path.normpath(path)
            _LAST_FILE_DIR["path"] = os.path.dirname(state["result"])
            win.destroy()

        def open_item(_event=None):
            item = selected()
            if item is None:
                return
            kind, name = item
            if kind == "up":
                go(os.path.dirname(state["dir"]))
            elif kind == "dir":
                go(os.path.join(state["dir"], name))
            else:
                finish(os.path.join(state["dir"], name))

        def on_select(_event=None):
            item = selected()
            if item is not None and item[0] == "file":
                name_var.set(item[1])

        def accept(_event=None):
            typed = name_var.get().strip()
            if typed:
                full = typed if os.path.isabs(typed) else os.path.join(state["dir"], typed)
                if os.path.isdir(full):
                    go(full)
                elif os.path.isfile(full):
                    finish(full)
                else:
                    status.config(text="Diese Datei gibt es nicht.")
                return
            open_item()

        def path_enter(_event=None):
            typed = path_var.get().strip().strip('"')
            if os.path.isdir(typed):
                go(typed)
            elif os.path.isfile(typed):
                finish(typed)
            else:
                status.config(text="Pfad nicht gefunden.")

        def change_filter(label):
            for index, (name, _) in enumerate(filters):
                if name == label:
                    state["filter"] = index
            go(state["dir"])

        def cancel():
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", cancel)
        win.bind("<Escape>", lambda e: cancel())

        # Pfadzeile
        top = tk.Frame(win, bg=PANEL)
        top.pack(fill="x", padx=14, pady=(12, 4))
        nova_button(top, "↑", lambda: go(os.path.dirname(state["dir"]) or state["dir"]),
                    width=3).pack(side="left", padx=(0, 6))
        path_entry = tk.Entry(top, textvariable=path_var, bg=PANEL2, fg=LIGHT,
                              insertbackground=ACCENT, relief="flat", font=("Consolas", 10),
                              highlightthickness=1, highlightbackground=EDGE,
                              highlightcolor=ACCENT)
        path_entry.pack(side="left", fill="x", expand=True, ipady=4)
        path_entry.bind("<Return>", path_enter)

        # Schnellzugriff: Laufwerke und häufige Ordner
        quick = tk.Frame(win, bg=PANEL)
        quick.pack(fill="x", padx=14, pady=(2, 6))
        shortcuts = []
        for label, folder in (("Desktop", "Desktop"), ("Dokumente", "Documents"),
                              ("Bilder", "Pictures"), ("Downloads", "Downloads")):
            full = os.path.join(home, folder)
            if os.path.isdir(full):
                shortcuts.append((label, full))
        if IS_WIN:
            try:
                mask = ctypes.windll.kernel32.GetLogicalDrives()
                shortcuts += [(f"{chr(65 + i)}:", f"{chr(65 + i)}:\\") for i in range(26)
                              if mask >> i & 1]
            except (OSError, AttributeError):
                pass
        for label, full in shortcuts[:12]:
            tk.Button(quick, text=label, command=lambda p=full: go(p), relief="flat", bd=0,
                      cursor="hand2", bg=PANEL2, fg=LIGHT, activebackground=EDGE,
                      activeforeground=LIGHT, font=("Consolas", 9), padx=8,
                      pady=2).pack(side="left", padx=(0, 4))

        # Liste
        middle = tk.Frame(win, bg=PANEL)
        middle.pack(fill="both", expand=True, padx=14)
        scrollbar = tk.Scrollbar(middle, bg=EDGE, troughcolor=PANEL2, activebackground=ACCENT,
                                 relief="flat", bd=0)
        scrollbar.pack(side="right", fill="y")
        listing = tk.Listbox(middle, bg=PANEL2, fg=LIGHT, selectbackground=ACCENT,
                             selectforeground=PANEL, activestyle="none", relief="flat",
                             highlightthickness=1, highlightbackground=EDGE,
                             highlightcolor=ACCENT, font=("Consolas", 10), exportselection=False,
                             yscrollcommand=scrollbar.set)
        listing.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listing.yview)
        listing.bind("<<ListboxSelect>>", on_select)
        listing.bind("<Double-Button-1>", open_item)
        listing.bind("<Return>", lambda e: (open_item(), "break")[1])

        # Dateiname, Filter, Knöpfe
        bottom = tk.Frame(win, bg=PANEL)
        bottom.pack(fill="x", padx=14, pady=(8, 2))
        tk.Label(bottom, text="Datei:", bg=PANEL, fg=LIGHT,
                 font=("Consolas", 10, "bold")).pack(side="left")
        name_entry = tk.Entry(bottom, textvariable=name_var, bg=PANEL2, fg=LIGHT,
                              insertbackground=ACCENT, relief="flat", font=("Consolas", 10),
                              highlightthickness=1, highlightbackground=EDGE,
                              highlightcolor=ACCENT)
        name_entry.pack(side="left", fill="x", expand=True, padx=8, ipady=4)
        name_entry.bind("<Return>", accept)
        choices = [label for label, _ in filters]
        menu = tk.OptionMenu(bottom, filter_var, *choices, command=change_filter)
        menu.config(bg=PANEL2, fg=LIGHT, activebackground=EDGE, activeforeground=LIGHT,
                    relief="flat", bd=0, highlightthickness=0, font=("Consolas", 9), width=18)
        menu["menu"].config(bg=PANEL2, fg=LIGHT, activebackground=ACCENT,
                            activeforeground=PANEL, font=("Consolas", 9))
        menu.pack(side="left")

        footer = tk.Frame(win, bg=PANEL)
        footer.pack(fill="x", padx=14, pady=(6, 12))
        status = tk.Label(footer, bg=PANEL, fg=DIM, font=("Consolas", 8), anchor="w")
        status.pack(side="left", fill="x", expand=True)
        nova_button(footer, "Öffnen", accept, primary=True, width=9).pack(side="right")
        nova_button(footer, "Abbrechen", cancel, width=9).pack(side="right", padx=(0, 8))

        start = opts.get("initialdir") or _LAST_FILE_DIR["path"]
        if not start or not os.path.isdir(start):
            pictures = os.path.join(home, "Pictures")
            start = pictures if os.path.isdir(pictures) else home
        go(start)
        _run_modal(win, parent)
        return state["result"]


messagebox = _NovaMessageBox()
filedialog = _NovaFileDialog()



class Nova:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg=TRANS)
        try:
            self.root.attributes("-transparentcolor", TRANS)
        except tk.TclError:
            pass

        self.canvas = tk.Canvas(self.root, width=W, height=H, bg=TRANS, highlightthickness=0)
        self.canvas.pack()

        # Eingabefeld zum Füttern/Benennen (direkt im Overlay, kein Extra-Fenster)
        self.entry = tk.Entry(self.root, font=("Consolas", 10, "bold"), bg=PANEL, fg=LIGHT,
                              insertbackground=ACCENT, relief="flat", justify="center",
                              highlightthickness=2, highlightbackground=EDGE,
                              highlightcolor=ACCENT)
        self.entry.bind("<Return>", self.submit_feed)
        self.entry.bind("<Escape>", lambda e: self.cancel_feed())
        self.entry.bind("<Button-1>", lambda e: self.entry.focus_force())
        self.entry.bind("<FocusOut>", lambda e: self.cancel_feed() if self.feeding else None)

        # ---- Zustand ----
        self.s = load_state()
        away = max(0.0, min(time.time() - float(self.s["last"]), OFFLINE_MAX))
        for k, r in DECAY.items():
            self.s[k] = clamp(self.s[k] - r * away * OFFLINE_FACTOR, 5.0)
        self.idle_away = max(0.0, time.time() - float(self.s["last"]))
        self.idle_last = time.time()
        self.idle_window = None
        self.idle_ui = {}
        self.idle_after_id = None
        self.idle_amount = 1
        self.idle_status = ""
        self.prompt = None                 # "timer" / "reminder": Eingabefeld ist offen
        self.alarm_until = 0.0
        self.alarm_next_beep = 0.0
        self.alarm_title = ""
        self.ac_running = False
        self.ac_count = 0
        self.ac_index = 0
        self.ac_blocked = 0
        self.ac_start_at = 0.0
        self.ac_after_id = None
        self.ac_pick_until = 0.0
        self.ac_hotkey_down = False
        self.ac_window = None
        self.ac_ui = {}
        self.ac_after_ui = None
        self.ac_status = ""

        self.window_mode = self.s["window_mode"]
        self.living_mode = self.s["living_mode"]
        self.platform = None
        self.platform_hwnd = None
        self.own_hwnds = None
        self.returning = False
        self.small = False
        self.mini = False
        self.mini_auto = self.s["mini_auto"]
        self.mini_manual = self.s["mini_manual"]
        self.phone_mode = self.s["phone_mode"]
        self.phone_source = None
        self.phone_talk_source = None
        self.phone_photo = None
        self.phone_photo_key = None
        self.canvas.configure(width=self.display_width(), height=self.display_height())
        self.feeding = False
        self.naming = False
        self.name_before_edit = ""
        self.feed_deadline = 0.0
        self.voice_enabled = self.s["voice_enabled"]
        self.synth_voice = self.s["synth_voice"]
        self.sys_monitor = self.s["sys_monitor"]
        self.spotify_mode = self.s["spotify_mode"]
        self.spotify_open = False
        self.spotify_playing = False
        self.spotify_title = ""
        self.spotify_next_poll = 0.0
        self.pid_names = {}
        self.music_pressed = ("", 0.0)
        self.cpu_percent = 0.0
        self.ram_percent = 0.0
        self.last_cpu_times = None
        self.last_sys_warn = 0.0
        self.voice_process = None
        self.voice_session_id = 0
        self.voice_speech_sequence = 0
        self.voice_events = queue.Queue()
        self.voice_error_message = ""
        self.ai_enabled = self.s["ai_enabled"]
        self.ai_provider = self.s["ai_provider"]
        self.ai_model = self.s["ai_model"]
        self.ai_api_key = self._load_ai_api_key() if self.ai_enabled else ""
        self.ai_history = []
        self.ai_memory_error = ""
        self.ai_memory_load_failed = False
        if self.ai_provider == "ollama":
            self._load_local_ai_memory()
        self.ai_results = queue.Queue()
        self.ai_speech_results = queue.Queue()
        self.ai_voice_results = queue.Queue()
        self.ai_speech_lines = {context: [] for context in ("idle", "feed", "pet", "general")}
        self.ai_speech_pending = []
        self.ai_speech_busy = False
        self.ai_speech_session_id = 0
        self.ai_speech_retry_at = 0.0
        self.ai_speech_error = ""
        self.ai_voice_process = None
        self.ai_voice_busy = False
        self.ai_voice_session_id = 0
        self.ai_voice_auto_send = False
        self.ai_voice_reply_pending = False
        self.ai_voice_continuous = False
        self.ai_voice_continuous_token = 0
        self.ai_voice_restart_after = None
        self.ai_voice_waiting_for_sequence = None
        self.ai_voice_pending_prompts = []
        self.ai_busy = False
        self.ai_session_id = 0
        self.ai_window = None
        self.ai_chat = None
        self.ai_prompt_entry = None
        self.ai_key_entry = None
        self.ai_model_entry = None
        self.ai_status = None
        self.ai_send_button = None
        self.ai_voice_button = None
        self.ai_voice_continuous_button = None
        self.ai_screen_button = None
        self.ai_clear_memory_button = None
        self.ai_preview_window = None
        self.ai_preview_photo = None
        self.ai_pending_image = None
        self.craving = random.Random(time.strftime("%Y%m%d")).choice(CRAVING_LETTERS)

        now = time.time()
        self.last_tick = now
        self.last_bonus = now
        self.last_need = now
        self.last_save = now
        self.last_pet = 0.0
        self.last_break = now
        self.last_hour = time.localtime().tm_hour
        self.sleeping = False
        self.system_dozing = False
        self.next_window_hop = time.time() + random.uniform(8, 15)
        self.teleport_until = 0.0
        self.bump_until = 0.0              # Glitch nach Anstoßen
        self.shake_rev, self.shake_dir, self.shake_cd = [], 0, 0.0   # Schüttel-Erkennung
        self.last_external_window = None
        self.minimized_window = None
        self.last_cursor_position = None
        self.last_cursor_move_at = time.monotonic()
        self.last_cursor_reaction_at = 0.0
        self.cursor_attention_until = 0.0
        self.cursor_pause_until = 0.0
        self.cursor_look_dir = 1
        self.hover = False
        self.hud_until = 0.0
        self._tick_id = None
        self._geometry = None
        self._last_error_log = 0.0

        # Minispiele
        self.game_end = 0.0
        self.game_mode = "dots"
        self.dots = []
        self.game_score = 0
        self.game_bonus = 0
        self.reflex_round = 0
        self.reflex_target = None
        self.reflex_next = 0.0
        self.reflex_times = []
        self.jump_from = None
        self.jump_to = None
        self.jump_started = 0.0
        self.jump_duration = 0.0
        self.jump_height = 0.0
        self.jump_next = 0.0
        self.pong = None
        self.dodge = None
        self.memory = None

        # Beenden-Animation
        self.quitting = False
        self.quit_started = 0.0
        self.boot_started = 0.0
        self.shutdown_photo = None
        self.quit_duration = 2.0

        # Bilder / Emotionen
        self.emotion_sources = {}
        self.art_cache = {}
        self.frame_cache = OrderedDict()
        self.crosshair_mode = False
        self.crosshair_win = None
        self.crosshair_photo = None
        self.emotion_override = ("", 0.0)
        self.emotion = "neutral"

        # ---- Bewegung ----
        self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.x = random.randint(0, max(1, self.sw - self.display_width()))
        self.y = self.sh - self.display_height() - 50
        self.dir = 1
        self.walking, self.dragging = self.s["walking"], False
        self._air_t = 0.0
        self._fly_t = 0.0
        self.t = self._tp = 0                       # virtuelle Ticks, immer 30/s (FPS-unabhängig)
        self.fps = self.s["fps"]
        self._t0 = self._tick_start = time.perf_counter()
        self.blink_until = 0.0
        self.bubble_text, self.bubble_until = "", 0.0
        self.off = (0, 0)

        # ---- Physik ----
        self.physics_enabled = self.s["physics"]
        self.show_foot_line = False        # Hilfslinie im Größen-Dialog
        self.angle = 0.0                   # Drehung in Grad (im Uhrzeigersinn)
        self.spin = 0.0                    # Drehgeschwindigkeit in Grad/s
        self.swing_v = 0.0                 # letzte Mausgeschwindigkeit (Pendel beim Ziehen)
        self.shake_until = 0.0             # bis dahin gilt NOVA als geschüttelt
        self.air_now = False               # Luft-Bild aktiv (pro Tick berechnet)
        self.fly_on = False                # größeres, quadratisches Fenster für die Drehung
        self.fly_size = 0
        self.acc_phase, self.acc_off, self._acc_t = "worn", {}, 0.0
        self.acc_edit, self.acc_sel, self.acc_drag = False, None, None
        self.acc_ranges, self.fav_rects = [], []
        self.fly_origin = (0, 0)           # Lage des normalen Fensters im Flug-Fenster
        self._fly_photo = None
        self.size_window = None
        self.phys_active = False
        self.vx = 0.0
        self.vy = 0.0
        self.perch_hwnd = None             # Fenster, auf dem NOVA gelandet ist
        self.drag_samples = []
        self.drag_moved = False
        self.drag_start = (0, 0)
        self.grab_airborne = False
        self.phys_decided = {}             # Fenster -> hängen bleiben (True/False) in diesem Sturz
        self.phys_win_cache = []
        self.phys_win_time = 0.0
        self.air_hold = False              # losgelassen ohne Wurf: bleibt in der Luft stehen
        self.ice_free = False              # Musikmodus: NOVA liegt nach dem Rutschen frei im Bild
        self.sfx_enabled = self.s["sfx"]
        self.sfx_dir = None
        self.sfx_files = {}
        self.sfx_last = -99.0
        self.sfx_last_kind = {}

        # ---- Radialmenü ----
        self.radial_window = None
        self.radial_canvas = None
        self.radial_items = []
        self.radial_x = None
        self.radial_y = None
        self.radial_origin = (0, 0)
        self.radial_offset = (0, 0)
        self.radial_inside_until = 0.0
        self.radial_animation_id = None
        self.radial_page_name = "main"
        self.ai_radial_action_active = False
        self.ai_radial_action_spoke = False
        self.ai_radial_action_has_message = False

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Button-3>", lambda e: self._acc_reset(e) if getattr(self, "acc_edit", False)
                         else self.show_radial_menu(e.x_root, e.y_root))
        self.canvas.bind("<MouseWheel>", self._acc_wheel)
        self.canvas.bind("<Button-4>", self._acc_wheel)
        self.canvas.bind("<Button-5>", self._acc_wheel)
        self.canvas.bind("<Enter>", lambda e: setattr(self, "hover", True))
        self.canvas.bind("<Leave>", lambda e: setattr(self, "hover", False))

        atexit.register(self.save)
        atexit.register(self.stop_voice)
        if not self.s.get("emotion_setup_done", False):
            self.configure_emotions(first_run=True)
        else:
            self.load_emotion_images()
        self.load_phone_image()
        self.emotion = self.emotion_for_state()
        if self.ai_enabled and self._ai_is_ready():
            self._request_ai_speech_lines()
        if self.voice_enabled and IS_WIN:
            self.ensure_voice_process()
        if self.s.get("name", "").strip():
            self.say(f"{self.s['name']} online. Hast du mich vermisst?", 4)
        else:
            self.start_name_prompt()
        self.apply_idle_offline()
        if STARTUP_ANIMATION and not self.phone_mode:
            self.boot_started = time.monotonic()
        self.tick()
        self.root.mainloop()

    # ================= Speichern =================
    def save(self):
        """Speichert Spielstand und Optionen (atomar, mit Sicherung)."""
        self.s["last"] = time.time()
        try:
            write_json_atomic(SAVE_FILE, self.s)
        except OSError:
            pass

    def quit_app(self):
        if self.quitting:
            return
        self._stop_ai_voice_chat()
        self.ac_stop(silent=True)
        previous = self.s.get("last_goodbye", "")
        choices = [line for line in GOODBYE_LINES if line != previous]
        goodbye = random.choice(choices or GOODBYE_LINES)
        self.s["last_goodbye"] = goodbye
        self.quit_duration = 3.2 if self.voice_enabled else 2.4
        self.stop_voice()
        self.say(goodbye, self.quit_duration, speak=self.voice_enabled)
        self.save()
        self.close_radial_menu()
        self.abort_input()
        self.cancel_game()
        self.quitting = True
        self.quit_started = time.monotonic()

    # ================= Emotionen: Einrichtung =================
    def configure_emotions(self, first_run=False):
        """Bild und Sprechblasentext(e) je Stimmung festlegen (alles optional)."""
        win = NovaToplevel(self.root)
        win.title("NOVA – Emotionen")
        win.attributes("-topmost", True)
        win.resizable(False, False)
        win.configure(bg=PANEL)
        width, height = 960, 690
        x = max(0, (win.winfo_screenwidth() - width) // 2)
        y = max(0, (win.winfo_screenheight() - height) // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

        title = "Richte NOVAs Emotionen ein" if first_run else "Emotionen bearbeiten"
        tk.Label(win, text=title, bg=PANEL, fg=ACCENT,
                 font=("Consolas", 16, "bold")).pack(pady=(16, 4))
        tk.Label(win, text="Optional: Bild und Sprechblasentext je Emotion. Mehrere Sprüche "
                           "mit | trennen, NOVA wählt zufällig. Leere Bilder nutzen das Normal-Bild.",
                 bg=PANEL, fg=LIGHT, font=("Consolas", 9)).pack(pady=(0, 12))
        if Image is None:
            tk.Label(win, text="Für eigene Bilder Pillow installieren (pip install pillow).",
                     bg=PANEL, fg=ACCENT, font=("Consolas", 9, "bold")).pack(pady=(0, 8))

        body = tk.Frame(win, bg=PANEL)
        body.pack(fill="x", padx=18)
        for col, text in ((0, "Emotion"), (2, "Bilddatei (optional)"), (4, "Text / Texte (optional)")):
            tk.Label(body, text=text, bg=PANEL, fg=ACCENT,
                     font=("Consolas", 9, "bold"), anchor="w").grid(row=0, column=col, sticky="w", padx=4)

        image_vars, text_vars, thumbs = {}, {}, {}
        saved_images = self.s.get("emotion_images", {})
        saved_texts = self.s.get("emotion_texts", {})

        def refresh_thumb(var, label, key):
            photo = make_thumb(var.get().strip())
            thumbs[key] = photo
            label.config(image=photo if photo else "", text="" if photo else "–", fg=DIM)

        for row, (key, label) in enumerate(EMOTIONS, start=1):
            image_var = tk.StringVar(value=str(saved_images.get(key, "")))
            text_var = tk.StringVar(value=str(saved_texts.get(key, "")))
            image_vars[key], text_vars[key] = image_var, text_var
            tk.Label(body, text=label, bg=PANEL, fg=LIGHT, font=("Consolas", 10, "bold"),
                     width=11, anchor="w").grid(row=row, column=0, pady=6, sticky="w", padx=4)
            thumb_label = tk.Label(body, bg=PANEL2, width=6, height=3, fg=DIM)
            thumb_label.grid(row=row, column=1, padx=4)
            refresh_thumb(image_var, thumb_label, key)
            tk.Entry(body, textvariable=image_var, width=30, bg=PANEL2, fg=LIGHT,
                     insertbackground=ACCENT, relief="flat").grid(row=row, column=2, padx=4)
            image_var.trace_add("write", lambda *a, v=image_var, l=thumb_label, k=key:
                                refresh_thumb(v, l, k))

            def browse(target=image_var):
                if Image is None:
                    messagebox.showinfo("Pillow erforderlich",
                                        "Installiere Pillow mit: pip install pillow", parent=win)
                    return
                path = filedialog.askopenfilename(
                    parent=win,
                    filetypes=IMAGE_FILETYPES)
                if not path:
                    return
                if not validate_image(path):
                    messagebox.showerror("Kein gültiges Bild", path, parent=win)
                    return
                target.set(path)

            tk.Button(body, text="Durchsuchen", command=browse, bg=PANEL2, fg=LIGHT,
                      activebackground=EDGE, activeforeground=LIGHT,
                      relief="flat").grid(row=row, column=3, padx=4)
            tk.Entry(body, textvariable=text_var, width=34, bg=PANEL2, fg=LIGHT,
                     insertbackground=ACCENT, relief="flat").grid(row=row, column=4, padx=(8, 0))

        def finish(without_images=False):
            images, texts = {}, {}
            for key, _ in EMOTIONS:
                path = "" if without_images else image_vars[key].get().strip()
                if path and not os.path.isfile(path):
                    messagebox.showerror("Bild nicht gefunden", path, parent=win)
                    return
                if path and not validate_image(path):
                    messagebox.showerror("Kein gültiges Bild", path, parent=win)
                    return
                if path:
                    images[key] = path
                text = text_vars[key].get().strip()[:300]
                if text:
                    texts[key] = text
            if images and Image is None:
                messagebox.showerror("Pillow erforderlich",
                                     "Installiere Pillow mit 'pip install pillow'.", parent=win)
                return
            try:
                images = {key: self.copy_emotion_image(key, path) for key, path in images.items()}
            except OSError as err:
                messagebox.showerror("Bild konnte nicht kopiert werden", str(err), parent=win)
                return
            self.cleanup_emotion_images(images.values())
            self.s["emotion_images"] = images
            self.s["emotion_texts"] = texts
            self.s["emotion_setup_done"] = True
            self.load_emotion_images()
            self.save()
            win.destroy()

        buttons = tk.Frame(win, bg=PANEL)
        buttons.pack(side="bottom", pady=16)
        tk.Button(buttons, text="Speichern und starten" if first_run else "Speichern",
                  command=finish, bg=ACCENT, fg=PANEL, activebackground=LIGHT,
                  activeforeground=PANEL, relief="flat", padx=16, pady=6,
                  font=("Consolas", 10, "bold")).pack(side="left", padx=8)
        tk.Button(buttons, text="Ohne Bilder starten" if first_run else "Abbrechen",
                  command=(lambda: finish(without_images=True)) if first_run else win.destroy,
                  bg=PANEL2, fg=LIGHT, activebackground=EDGE, activeforeground=LIGHT,
                  relief="flat", padx=16, pady=6, font=("Consolas", 10)).pack(side="left", padx=8)

        win.protocol("WM_DELETE_WINDOW", finish if first_run else win.destroy)
        win.grab_set()
        win.focus_force()
        self.root.wait_window(win)

    def copy_emotion_image(self, emotion, source):
        """Kopiert das Bild neben das Programm, damit das Original verschoben werden darf."""
        os.makedirs(EMOTION_IMAGE_DIR, exist_ok=True)
        extension = os.path.splitext(source)[1].lower() or ".img"
        destination = os.path.join(EMOTION_IMAGE_DIR, f"{emotion}{extension}")
        if os.path.normcase(os.path.abspath(source)) != os.path.normcase(os.path.abspath(destination)):
            shutil.copy2(source, destination)
        return destination

    def cleanup_emotion_images(self, keep_paths):
        """Löscht übrig gebliebene, nicht mehr genutzte Emotionsbilder (nur eigene Dateinamen)."""
        keep = {os.path.normcase(os.path.abspath(p)) for p in keep_paths}
        keys = {k for k, _ in EMOTIONS}
        try:
            names = os.listdir(EMOTION_IMAGE_DIR)
        except OSError:
            return
        for name in names:
            full = os.path.join(EMOTION_IMAGE_DIR, name)
            if os.path.splitext(name)[0] in keys and os.path.normcase(os.path.abspath(full)) not in keep:
                try:
                    os.remove(full)
                except OSError:
                    pass

    def load_emotion_images(self):
        """Lädt die gewählten Bilder; eine vorhandene sprite.png dient als Normal-Bild."""
        self.emotion_sources = {}
        self.art_cache = {}
        self.frame_cache.clear()
        self.phone_photo = None
        self.phone_photo_key = None
        paths = dict(self.s.get("emotion_images", {}))
        if Image is None:
            if any(isinstance(p, str) and p for p in paths.values()):
                messagebox.showwarning(
                    "Pillow erforderlich",
                    "Eigene Bilder werden ignoriert. Installiere Pillow mit: pip install pillow",
                    parent=self.root)
            return
        if not paths.get("neutral") and os.path.isfile(LEGACY_SPRITE):
            paths["neutral"] = LEGACY_SPRITE
        invalid = []
        for key, _ in EMOTIONS:
            path = paths.get(key)
            if not isinstance(path, str) or not path:
                continue
            if not os.path.isfile(path):
                invalid.append(path)
                continue
            try:
                image = Image.open(path).convert("RGBA")
                bounds = image.getchannel("A").getbbox()
                self.emotion_sources[key] = image.crop(bounds) if bounds else image
            except (OSError, ValueError):
                invalid.append(path)
        if invalid:
            messagebox.showwarning("Bilder konnten nicht geladen werden",
                                   "Diese Bilder werden ignoriert:\n" + "\n".join(invalid),
                                   parent=self.root)

    def load_phone_image(self):
        """Telefonbilder sind Emotionen (phone / phone_talk); hier nur Cache leeren."""
        self.phone_source = None
        self.phone_talk_source = None
        self.phone_photo = None
        self.phone_photo_key = None

    # ================= Größe & Fußlinie =================
    def open_size_settings(self):
        self.close_radial_menu()
        self.root.after_idle(self.configure_size)

    def apply_size_settings(self, scale_pct, foot_pct, save=False, ground=None, sit=None, air=None):
        """Übernimmt Größe/Fußlinie sofort; steht NOVA auf dem Boden, rutscht sie sauber nach."""
        was_on_floor = (not self.phys_active and not self.dragging
                        and self.platform is None
                        and abs(self.y - self.floor_y()) < 4)
        self.s["sprite_scale"] = min(SPRITE_SCALE_MAX, max(SPRITE_SCALE_MIN, scale_pct / 100.0))
        self.s["foot_pct"] = min(FOOT_PCT_MAX, max(0.0, float(foot_pct)))
        if sit is not None:
            self.s["foot_sit"] = min(FOOT_PCT_MAX, max(0.0, float(sit)))
        if air is not None:
            self.s["foot_air"] = min(FOOT_PCT_MAX, max(0.0, float(air)))
        if ground is not None:
            self.s["ground_offset"] = int(min(GROUND_OFFSET_MAX, max(GROUND_OFFSET_MIN, ground)))
        self.art_cache = {}
        self.frame_cache.clear()
        if was_on_floor and not self.phone_mode:
            self.returning = True
        if save:
            self.save()

    def configure_size(self):
        """Dialog: Größe und Lage der Füße im Bild einstellen (Live-Vorschau)."""
        if self.size_window is not None:
            try:
                self.size_window.lift()
                return
            except tk.TclError:
                self.size_window = None
        win = NovaToplevel(self.root)
        self.size_window = win
        win.title("NOVA – Größe & Füße")
        win.attributes("-topmost", True)
        win.resizable(False, False)
        win.configure(bg=PANEL)
        width, height = 460, 640
        x = max(0, (win.winfo_screenwidth() - width) // 2)
        y = max(0, (win.winfo_screenheight() - height) // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(win, text="Größe & Füße", bg=PANEL, fg=ACCENT,
                 font=("Consolas", 16, "bold")).pack(pady=(14, 2))
        tk.Label(win, text="Änderungen siehst du sofort an NOVA.",
                 bg=PANEL, fg=LIGHT, font=("Consolas", 9)).pack(pady=(0, 8))

        scale_var = tk.DoubleVar(value=round(self.s["sprite_scale"] * 100))
        foot_var = tk.DoubleVar(value=round(self.s["foot_pct"], 1))
        sit_var = tk.DoubleVar(value=round(self.s.get("foot_sit", 0.0), 1))
        air_var = tk.DoubleVar(value=round(self.s.get("foot_air", 0.0), 1))
        ground_var = tk.DoubleVar(value=self.s.get("ground_offset", 0))
        line_var = tk.BooleanVar(value=True)

        def changed(*_):
            self.apply_size_settings(scale_var.get(), foot_var.get(), ground=ground_var.get(),
                                     sit=sit_var.get(), air=air_var.get())

        def slider(label, hint, var, lo, hi, step, parent=win, cmd=None):
            tk.Label(parent, text=label, bg=PANEL, fg=ACCENT, anchor="w",
                     font=("Consolas", 10, "bold")).pack(fill="x", padx=22)
            tk.Label(parent, text=hint, bg=PANEL, fg=DIM, anchor="w", justify="left",
                     font=("Consolas", 8)).pack(fill="x", padx=22)
            tk.Scale(parent, variable=var, from_=lo, to=hi, resolution=step,
                     orient="horizontal", length=410, bg=PANEL, fg=LIGHT,
                     troughcolor=PANEL2, activebackground=ACCENT, highlightthickness=0,
                     command=cmd or changed).pack(padx=22, pady=(0, 6))

        slider("Größe (%)", "100 = Standard. Gilt für normale Größe, Fenster und Mini.",
               scale_var, round(SPRITE_SCALE_MIN * 100), round(SPRITE_SCALE_MAX * 100), 1)
        foot_box = tk.Frame(win, bg=PANEL)
        foot_btn = tk.Button(win, bg=PANEL2, fg=LIGHT, activebackground=EDGE,
                             activeforeground=LIGHT, relief="flat", anchor="w", padx=10,
                             font=("Consolas", 10, "bold"))
        foot_btn.pack(fill="x", padx=22, pady=(2, 6))

        feet_open = [False]

        def toggle_feet(state=None):
            feet_open[0] = (not feet_open[0]) if state is None else state
            if feet_open[0]:
                foot_box.pack(fill="x", after=foot_btn)
            else:
                foot_box.pack_forget()
            foot_btn.config(text=("▾ " if feet_open[0] else "▸ ")
                            + "Fußlinien (Normal · Sitzen · Luft)")
            win.geometry(f"{width}x{height + (310 if feet_open[0] else 0) - 60}")

        foot_btn.config(command=toggle_feet)
        slider("Fußlinie Normal (% vom unteren Bildrand)",
               "0 = unterer Bildrand ist der Boden. Mehr = Füße liegen höher im Bild\n"
               "(z. B. bei Schatten oder Leerraum unter den Füßen).",
               foot_var, 0, FOOT_PCT_MAX, 0.5, foot_box)
        slider("Fußlinie Sitzen (%)",
               "Wie tief das Sitz-Bild ist: Die Füße liegen auf der Musik-Box.\n"
               "Vorschau mit Hilfslinie, solange Spotify läuft.",
               sit_var, 0, FOOT_PCT_MAX, 0.5, foot_box)
        slider("Fußlinie Luft (%)",
               "Wie tief das Luft-Bild ist (Wurf, Schütteln, in der Luft abgelegt).",
               air_var, 0, FOOT_PCT_MAX, 0.5, foot_box)
        toggle_feet(False)
        slider("Bodenhöhe (Pixel)",
               "0 = Oberkante der Taskleiste. Plus = tiefer, minus = höher.",
               ground_var, GROUND_OFFSET_MIN, GROUND_OFFSET_MAX, 1)

        bub_var = tk.DoubleVar(value=self.s.get("bubble_dy", 0))
        hud_var = tk.DoubleVar(value=self.s.get("hud_dy", 0))

        def text_changed(*_):
            self.s["bubble_dy"] = int(bub_var.get())
            self.s["hud_dy"] = int(hud_var.get())
            self.hud_until = max(self.hud_until, time.time() + 2)
            self.say("So sieht die Sprechblase hier aus.", 2.5, speak=False)

        slider("Sprechblase Höhe", "Plus = weiter nach unten, minus = höher.",
               bub_var, -90, 280, 1, cmd=text_changed)
        slider("Statusanzeige Höhe", "Plus = weiter nach unten.",
               hud_var, 0, 320, 1, cmd=text_changed)
        fps_var = tk.DoubleVar(value=self.fps)

        def fps_changed(*_):
            self.fps = min(60, max(30, int(fps_var.get())))
            self.s["fps"] = self.fps

        slider("FPS", "Minimum 30. Höher = flüssiger, aber mehr CPU.",
               fps_var, 30, 60, 1, cmd=fps_changed)

        def toggle_line():
            self.show_foot_line = line_var.get()

        tk.Checkbutton(win, text="Fußlinie als Hilfslinie anzeigen", variable=line_var,
                       command=toggle_line, bg=PANEL, fg=LIGHT, selectcolor=PANEL2,
                       activebackground=PANEL, activeforeground=LIGHT,
                       font=("Consolas", 9)).pack(anchor="w", padx=20)
        self.show_foot_line = True

        buttons = tk.Frame(win, bg=PANEL)
        buttons.pack(pady=10)

        def reset():
            scale_var.set(100)
            foot_var.set(0)
            sit_var.set(0)
            air_var.set(0)
            ground_var.set(0)
            fps_var.set(30)
            bub_var.set(0)
            hud_var.set(0)
            fps_changed()
            text_changed()
            changed()

        def close(*_):
            self.show_foot_line = False
            self.apply_size_settings(scale_var.get(), foot_var.get(), save=True,
                                     ground=ground_var.get(), sit=sit_var.get(),
                                     air=air_var.get())
            self.size_window = None
            try:
                win.destroy()
            except tk.TclError:
                pass

        tk.Button(buttons, text="Zurücksetzen", command=reset, bg=PANEL2, fg=LIGHT,
                  activebackground=EDGE, activeforeground=LIGHT, relief="flat",
                  padx=14, pady=5, font=("Consolas", 10)).pack(side="left", padx=6)
        tk.Button(buttons, text="Fertig", command=close, bg=ACCENT, fg=PANEL,
                  activebackground=LIGHT, activeforeground=PANEL, relief="flat",
                  padx=18, pady=5, font=("Consolas", 10, "bold")).pack(side="left", padx=6)
        win.protocol("WM_DELETE_WINDOW", close)

    def open_emotion_settings(self):
        self.close_radial_menu()
        self.root.after_idle(self.configure_emotions)

    # ================= Emotionen: Logik =================
    def emotion_for_state(self):
        if self.sleeping:
            return "sleepy"
        if self.music_active():
            return "music"                 # Musikmodus: keine Umschaltung auf andere Emotionen
        if self.s["energy"] < 25:
            return "sleepy"
        name, until = self.emotion_override
        if name and time.time() < until:
            return name
        if self.s["food"] < 25:
            return "hungry"
        if self.s["fun"] < 25:
            return "bored"
        if min(self.s["food"], self.s["fun"], self.s["energy"]) >= 70:
            return "happy"
        return "neutral"

    def set_emotion_override(self, name, seconds=4.0):
        """Kurzzeitige Reaktion, z. B. fröhlich nach dem Streicheln."""
        self.emotion_override = (name, time.time() + seconds)

    def emotion_text(self, emotion):
        texts = self.s.get("emotion_texts", {})
        raw = texts.get(EMO_ART.get(emotion, emotion), "") if isinstance(texts, dict) else ""
        options = [t.strip() for t in str(raw).split("|") if t.strip()]
        return random.choice(options) if options else ""

    def update_emotion(self):
        """Wechselt Stimmung und Text; kurze Reaktionen lösen keinen eigenen Spruch aus."""
        emotion = self.emotion_for_state()
        if emotion == self.emotion:
            return
        self.emotion = emotion
        name, until = self.emotion_override
        if name == emotion and time.time() < until:
            return
        text = self.emotion_text(emotion)
        if text:
            self.say(text, 6)

    # ================= Bilder: Cache & Größen =================
    def art_key(self):
        """Welches Bild gilt gerade? Emotion -> Normal -> None (gezeichnete Figur)."""
        if Image is None:
            return None
        want = "air" if self.air_now else EMO_ART.get(self.emotion, self.emotion)
        if want in self.emotion_sources:
            return want
        if FALLBACK_TO_NEUTRAL and "neutral" in self.emotion_sources:
            return "neutral"
        return None

    def sprite_scale(self):
        """Vom Nutzer eingestellter Größenfaktor (Optionen -> Größe & Füße)."""
        return self.s.get("sprite_scale", 1.0)

    def current_height(self):
        if self.mini:
            base = SPRITE_H_MINI
        elif self.small:
            base = SPRITE_H_SMALL
        else:
            base = SPRITE_H
        return max(24, round(base * self.sprite_scale()))

    def foot_drop(self):
        """Pixel, die das Bild unterhalb der Füße hat (Schatten, Leerraum). Damit stehen
        die Füße auf Boden und Fensterkante, nicht der untere Bildrand."""
        if self.phone_mode or self.art_key() is None or self.music_visible():
            return 0                       # beim Sitzen bestimmt die Box den Boden (sit_drop)
        pct = self.s.get("foot_air" if self.art_key() == "air" else "foot_pct", 0.0)
        return int(round(self.figure_h() * pct / 100.0))

    def sit_drop(self):
        """Wie tief das Bild unter der Fußlinie liegt; beim Sitzen eigener Wert "foot_sit"."""
        key = self.art_key()
        if self.phone_mode or key is None:
            return 0
        sit = key == "sit" or (key == "air" and self.music_visible())
        pct = self.s.get("foot_sit" if sit else "foot_pct", 0.0)
        return int(round(self.figure_h() * pct / 100.0))

    def display_width(self):
        return PHONE_SIZE if self.phone_mode else W

    def display_height(self):
        return PHONE_SIZE if self.phone_mode else H

    def drawn_scale(self):
        return (0.5 if self.mini else (0.75 if self.small else 1.0)) * self.sprite_scale()

    def accessory_scale(self):
        return (0.4 if self.mini else (0.6 if self.small else 1.0)) * self.sprite_scale()

    def art_base(self, key, height):
        """Skaliertes Bild (normal, gespiegelt); passt auch breite Bilder in die Fensterbreite."""
        ck = (key, height)
        if ck not in self.art_cache:
            src = self.emotion_sources[key]
            scale = min(height / src.height, (W - 16) / src.width)
            scaled = src.resize((max(1, round(src.width * scale)),
                                 max(1, round(src.height * scale))), Image.LANCZOS)
            self.art_cache[ck] = (scaled, ImageOps.mirror(scaled))
        return self.art_cache[ck]

    def art_photo(self, key, height, phase, walking, direction):
        """Liefert ein animiertes Einzelbild; Bilder entstehen erst bei Bedarf (LRU-Cache)."""
        ck = (key, height, phase, walking, direction)
        photo = self.frame_cache.get(ck)
        if photo is not None:
            self.frame_cache.move_to_end(ck)
            return photo
        base, mirrored = self.art_base(key, height)
        img = base if direction >= 0 else mirrored
        p = 2 * math.pi * phase / FRAMES
        sway = math.sin(p)
        if walking:
            step = (1 - math.cos(2 * p)) / 2
            sy = 1 + 0.012 * (1 - step) - 0.008 * step
            sx = 1 - 0.006 * (1 - step) + 0.004 * step
            ang = direction * 2.5 + sway * 1.8
            bob = round(1 + 3 * step)
            shift_x = round(sway * 2)
        else:
            breath = (1 + sway) / 2
            sy = 1 + 0.009 * breath
            sx = 1 - 0.004 * breath
            ang = sway * 0.8
            bob = round(breath)
            shift_x = round(sway * 0.7)
        im = img.resize((max(1, round(img.width * sx)), max(1, round(img.height * sy))),
                        Image.BILINEAR)
        im = im.rotate(-ang, resample=Image.BILINEAR, expand=True)
        canvas = Image.new("RGBA", (W, height + 40), (0, 0, 0, 0))
        left = (W - im.width) // 2 + shift_x
        top = canvas.height - im.height - bob
        canvas.paste(im, (left, top), im)
        alpha = canvas.getchannel("A").point(lambda v: 255 if v > 140 else 0)
        flat = Image.new("RGB", canvas.size, (1, 2, 3))
        flat.paste(canvas.convert("RGB"), (0, 0), alpha)
        photo = ImageTk.PhotoImage(flat)
        self.frame_cache[ck] = photo
        while len(self.frame_cache) > MAX_FRAME_CACHE:
            self.frame_cache.popitem(last=False)
        return photo

    def phone_mode_photo(self, speaking=False):
        if Image is None or ImageOps is None:
            return None
        if speaking and "phone_talk" in self.emotion_sources:
            key = ("emo", "phone_talk")
            source = self.emotion_sources["phone_talk"]
        elif "phone" in self.emotion_sources:
            key = ("emo", "phone")
            source = self.emotion_sources["phone"]
        else:
            art_key = "happy" if (speaking and "happy" in self.emotion_sources) else self.art_key()
            key = ("emotion", art_key, speaking)
            source = self.emotion_sources.get(art_key)
        if self.phone_photo is not None and self.phone_photo_key == key:
            return self.phone_photo
        if source is None:
            self.phone_photo = None
            self.phone_photo_key = key
            return None
        image = ImageOps.fit(
            source, (PHONE_IMAGE_SIZE, PHONE_IMAGE_SIZE),
            method=Image.LANCZOS, centering=(0.5, 0.5))
        background = Image.new("RGBA", image.size, (11, 5, 6, 255))
        background.alpha_composite(image)
        self.phone_photo = ImageTk.PhotoImage(background)
        self.phone_photo_key = key
        return self.phone_photo

    def figure_h(self):
        key = self.art_key()
        if key is not None:
            return self.art_base(key, self.current_height())[0].height
        return int(178 * self.drawn_scale())

    # ================= Punkte & Level =================
    @property
    def level(self):
        """Level aus gesamter XP, nicht aus den ausgebbaren Shop-Punkten."""
        return 1 + int(self.s["xp"]) // 50

    def add_points(self, n, announce=True, quest=False):
        """Vergibt Punkte und XP; Käufe verringern nur die ausgebbaren Punkte."""
        old = self.level
        self.s["points"] = int(self.s["points"]) + n
        self.s["xp"] = int(self.s["xp"]) + n
        leveled = self.level > old
        if leveled and announce:
            self.say(f"Level {self.level}! Du bist der Beste, Choom.", 6)
        if n > 0 and not quest:
            self.quest_event("points", n)
        return leveled

    # ================= Tagesbelohnung & Quests =================
    def daily_check(self):
        """Neuer Tag: Login-Belohnung (Serie) und drei frische Quests."""
        today = datetime.date.today()
        d = self.s["daily"]
        if d["day"] == today.isoformat():
            return
        yesterday = (today - datetime.timedelta(days=1)).isoformat()
        d["streak"] = d["streak"] + 1 if d["claimed"] == yesterday else 1
        d["claimed"] = d["day"] = today.isoformat()
        d["ids"] = random.Random(d["day"]).sample(list(QUESTS), 3)
        d["prog"], d["paid"] = {}, []
        pts = DAILY_REWARDS[(d["streak"] - 1) % len(DAILY_REWARDS)]
        self.add_points(pts, announce=False, quest=True)
        self.say(f"Tagesbelohnung: +{pts} Punkte! Serie: {d['streak']}. Neue Quests warten.", 8)
        self.save()

    def quest_event(self, kind, n=1):
        d = self.s["daily"]
        if kind not in d["ids"] or kind in d["paid"]:
            return
        text, goal, reward = QUESTS[kind]
        d["prog"][kind] = min(goal, d["prog"].get(kind, 0) + n)
        if d["prog"][kind] < goal:
            return
        d["paid"].append(kind)
        extra = ""
        if all(q in d["paid"] for q in d["ids"]):
            d["paid"].append("bonus")
            reward += QUEST_BONUS
            extra = f" Alle Quests fertig: Bonus +{QUEST_BONUS}!"
        if self.add_points(reward, announce=False, quest=True):
            extra += f" Level {self.level}!"
        msg = f"Quest geschafft: {text}! +{reward} Punkte.{extra}"
        self.root.after(2500, lambda: None if self.quitting else self.say(msg, 6))

    def show_quests(self):
        self.daily_check()
        d = self.s["daily"]
        parts = [("✔ " if q in d["paid"] else "") + f"{QUESTS[q][0]} {d['prog'].get(q, 0)}/{QUESTS[q][1]}"
                 f" (+{QUESTS[q][2]})" for q in d["ids"]]
        self.say(f"Quests · Serie {d['streak']} · " + " | ".join(parts), 10, speak=False)

    def buy_item(self, key):
        """Verbrauchs-Item: sofort wirksam, jederzeit wieder kaufbar."""
        name, price, _, _, stat, amt = SHOP_ITEMS[key]
        if self.s["points"] < price:
            self.say(f"Dafür fehlen {price - int(self.s['points'])} Punkte.", 4, speak=False)
            return
        self.s["points"] -= price
        if stat == "xp":
            old = self.level
            self.s["xp"] += amt
            extra = f" Level {self.level}!" if self.level > old else ""
        else:
            for k in (("food", "fun", "energy") if stat == "all" else (stat,)):
                self.s[k] = clamp(self.s[k] + amt)
            extra = ""
        self.set_emotion_override("happy", 3)
        self.say(f"{name}! Danke.{extra}", 4)
        self.quest_event("buy")

    # ================= Radialmenü =================
    def radial_page(self, page):
        """Titel und Einträge der Menüseite. 'on' lässt Schalter leuchten, 'dim' graut aus."""
        go = lambda p: (lambda: self.open_radial_page(p))
        if page == "care":
            return "AKTIONEN", [
                {"label": "Streicheln", "icon": "💖", "action": self.pet},
                {"label": "Füttern", "icon": "🍗", "action": self.feed_word},
                {"label": "Aufwecken" if self.sleeping else "Schlafen",
                 "icon": "☀️" if self.sleeping else "🌙", "action": self.toggle_sleep},
                {"label": f"Quests\n{sum(q in self.s['daily']['paid'] for q in self.s['daily']['ids'])}"
                          f"/{len(self.s['daily']['ids'])}", "icon": "📜", "action": self.show_quests},
                {"label": "Zurück", "icon": "↩️", "action": go("main")},
            ]
        if page == "tools":
            return "WERKZEUGE", [
                {"label": "Timer", "icon": "⏱️", "action": go("timer"), "on": self.timer_active()},
                {"label": "Erinnerungen", "icon": "🔔", "action": go("reminders"),
                 "on": bool(self.s["reminders"])},
                {"label": "Auto-\nclicker", "icon": "🖱️", "action": self.open_ac_window,
                 "on": self.ac_running},
                {"label": "Browser", "icon": "🌐", "action": lambda: self.start_prompt("browse")},
                {"label": "Notizblock", "icon": "📝", "action": self.open_notes,
                 "on": bool(self.s.get("notes"))},
                {"label": "Zurück", "icon": "↩️", "action": go("main")},
            ]
        if page == "timer":
            active = self.timer_active()
            return "TIMER", [
                {"label": "5 Min", "icon": "⏱️", "action": lambda: self.start_timer(300)},
                {"label": "15 Min", "icon": "⏳", "action": lambda: self.start_timer(900)},
                {"label": "25 Min\nFokus", "icon": "🍅",
                 "action": lambda: self.start_timer(1500, "Fokus")},
                {"label": "Eigene", "icon": "✏️", "action": lambda: self.start_prompt("timer")},
                {"label": "+5 Min", "icon": "➕", "action": self.add_timer_minutes,
                 "dim": not active},
                {"label": "Stopp", "icon": "⏹️", "action": self.stop_timer, "dim": not active},
                {"label": "Zurück", "icon": "↩️", "action": go("tools")},
            ]
        if page == "reminders":
            has_items = bool(self.s["reminders"])
            return "ERINNERUNGEN", [
                {"label": "Neue", "icon": "➕", "action": lambda: self.start_prompt("reminder")},
                {"label": "Liste", "icon": "📋", "action": self.show_reminders,
                 "dim": not has_items},
                {"label": "Löschen", "icon": "🗑️", "action": go("remove_reminders"),
                 "dim": not has_items},
                {"label": "Zurück", "icon": "↩️", "action": go("tools")},
            ]
        if page == "remove_reminders":
            items = [
                {"label": f"{fmt_when(r['due'])}\n{r['text'][:10]}", "icon": "❌",
                 "action": lambda item=r: self.remove_reminder(item)}
                for r in self.s["reminders"][:8]
            ]
            items.append({"label": "Zurück", "icon": "↩️", "action": go("reminders")})
            return "ERINNERUNG LÖSCHEN", items
        if page == "play":
            return "SPIELEN", [
                {"label": "Daten", "icon": "🎯", "action": self.start_game},
                {"label": "Reflex", "icon": "⚡", "action": self.start_reflex_game},
                {"label": "Hüpfen", "icon": "🏃", "action": self.start_jump_game},
                {"label": "Pong", "icon": "🏓", "action": self.start_pong_game},
                {"label": "Ausweichen", "icon": "☄️", "action": self.start_dodge_game},
                {"label": "Merken", "icon": "🧠", "action": self.start_memory_game},
                {"label": "Farm", "icon": "⛏️", "action": self.open_idle_window},
                {"label": "Extras", "icon": "✨", "action": go("play_extra")},
                {"label": "Zurück", "icon": "↩️", "action": go("main")},
            ]
        if page == "play_extra":
            return "EXTRAS", [
                {"label": "Wörter", "icon": "📚", "action": self.show_vocab},
                {"label": "Spruch", "icon": "💬", "action": self.say_random},
                {"label": "Rekorde", "icon": "🏆", "action": self.show_highscores},
                {"label": "Zurück", "icon": "↩️", "action": go("play")},
            ]
        if page in ("shop", "shop_store"):
            load_shop_images()
        if page == "shop_items":
            items = [{"label": f"{v[3]}\n{v[1]} Pkt", "icon": v[2], "dim": self.s["points"] < v[1],
                      "action": lambda k=k: self.buy_item(k)} for k, v in SHOP_ITEMS.items()]
            items.append({"label": "Zurück", "icon": "↩️", "action": go("shop_store")})
            return f"ITEMS · {int(self.s['points'])} Pkt", items
        if page == "shop":
            return f"SHOP · {int(self.s['points'])} Pkt", [
                {"label": "Kisten", "icon": "📦", "action": self.open_case_window},
                {"label": "Laden", "icon": "🛍️", "action": go("shop_store")},
                {"label": "Anordnen\nVerschieben", "icon": "✋", "action": self.start_acc_edit},
                {"label": "Zurück", "icon": "↩️", "action": go("main")},
            ]
        if page == "shop_store":
            items = [{"label": label, "icon": icon, "action": go(pg)}
                     for pg, label, icon, _ in SHOP_CATS]
            items.append({"label": "Items", "icon": "🍙", "action": go("shop_items")})
            items.append({"label": "Zurück", "icon": "↩️", "action": go("shop")})
            return f"LADEN · {int(self.s['points'])} Pkt", items
        for pg, label, _, keys in SHOP_CATS:
            if page != pg:
                continue
            items = []
            for key in sorted(keys, key=lambda k: (rar_index(k), SHOP[k][1])):   # links selten -> rechts rar
                price = SHOP[key][1]
                owned = key in self.s["owned"]
                worn = key in self.s["worn"]
                pull = key in SHOP_PULL and not owned
                text = ('Ablegen' if worn else 'Anlegen') if owned else "🔒 Nur Kiste" if pull else f"{price} Pkt"
                items.append({"label": f"{SHOP_SHORT[key]}\n{text}\n{RARITIES[rar_index(key)][1]}",
                              "col": RARITIES[rar_index(key)][2], "icon": SHOP_ICONS[key],
                              "action": lambda k=key: self.buy_or_toggle(k),
                              "on": worn if owned else None,
                              "dim": pull or ((not owned) and self.s["points"] < price)})
            items.append({"label": "Zurück", "icon": "↩️", "action": go("shop_store")})
            return f"{label.upper()} · {int(self.s['points'])} Pkt", items
        if page == "audio":
            return "AUDIO", [
                {"label": "Stimme", "icon": "🔊", "action": self.toggle_voice,
                 "on": self.voice_enabled},
                {"label": "Synth-Effekt", "icon": "🤖", "action": self.toggle_synth_voice,
                 "on": self.synth_voice},
                {"label": "Test", "icon": "🎵", "action": self.test_voice},
                {"label": "Spotify", "icon": "🎧", "action": self.toggle_spotify_mode,
                 "on": self.spotify_mode},
                {"label": "Effekte", "icon": "💥", "action": self.toggle_sfx,
                 "on": self.sfx_enabled},
                {"label": "Zurück", "icon": "↩️", "action": go("settings")},
            ]
        if page == "control":
            return "PC-STEUERUNG", [
                {"label": "Lauter", "icon": "🔊",
                 "action": lambda: self.control_media_key("volume_up")},
                {"label": "Leiser", "icon": "🔉",
                 "action": lambda: self.control_media_key("volume_down")},
                {"label": "Stumm", "icon": "🔇",
                 "action": lambda: self.control_media_key("mute")},
                {"label": "Play/Pause", "icon": "⏯",
                 "action": lambda: self.control_media_key("play_pause")},
                {"label": "Nächster", "icon": "⏭",
                 "action": lambda: self.control_media_key("next_track")},
                {"label": "Apps", "icon": "🧩", "action": go("apps")},
                {"label": "Fenster", "icon": "🪟", "action": go("windows")},
                {"label": "Zurück", "icon": "↩️", "action": go("settings")},
            ]
        if page == "apps":
            items = [
                {"label": os.path.splitext(os.path.basename(path))[0][:12],
                 "icon": "▶️", "action": lambda app=path: self.launch_controlled_app(app)}
                for path in self.s["controlled_apps"]
            ]
            items.extend([
                {"label": "Favoriten\n(am Sprite)", "icon": "⭐", "action": go("fav_apps"),
                 "dim": not self.s["controlled_apps"]},
                {"label": "App\nhinzufügen", "icon": "➕", "action": self.add_controlled_app},
                {"label": "Apps\nentfernen", "icon": "🗑️", "action": go("remove_apps"),
                 "dim": not self.s["controlled_apps"]},
                {"label": "Zurück", "icon": "↩️", "action": go("control")},
            ])
            return "FREIGEGEBENE APPS", items
        if page == "fav_apps":
            items = [
                {"label": os.path.splitext(os.path.basename(path))[0][:12],
                 "icon": "⭐" if path in self.s["fav_apps"] else "☆",
                 "on": path in self.s["fav_apps"],
                 "action": lambda app=path: self.toggle_fav_app(app)}
                for path in self.s["controlled_apps"]
            ]
            items.append({"label": "Zurück", "icon": "↩️", "action": go("apps")})
            return "FAVORITEN (max. 4)", items
        if page == "remove_apps":
            items = [
                {"label": os.path.splitext(os.path.basename(path))[0][:12],
                 "icon": "❌", "action": lambda app=path: self.remove_controlled_app(app)}
                for path in self.s["controlled_apps"]
            ]
            items.append({"label": "Zurück", "icon": "↩️", "action": go("apps")})
            return "APP ENTFERNEN", items
        if page == "windows":
            return "FENSTER", [
                {"label": "Minimieren", "icon": "⬇️", "action": self.minimize_last_window},
                {"label": "Wiederherstellen", "icon": "⬆️", "action": self.restore_last_window},
                {"label": "Zurück", "icon": "↩️", "action": go("control")},
            ]
        if page == "ai":
            return "KI-MODUS", [
                {"label": "Ausschalten" if self.ai_enabled else "Einschalten",
                 "icon": "🧠", "action": self.toggle_ai_mode, "on": self.ai_enabled},
                {"label": "Anbieter", "icon": "🔄", "action": go("ai_provider")},
                {"label": "Chat", "icon": "💬", "action": self.open_ai_window,
                 "dim": not self.ai_enabled},
                {"label": "Stopp" if self.ai_voice_continuous else "Dauerhören",
                 "icon": "🎙", "action": self.start_ai_voice_chat,
                 "on": self.ai_voice_continuous, "dim": not self.ai_enabled},
                {"label": "Zurück", "icon": "↩️", "action": go("settings")},
            ]
        if page == "ai_provider":
            return "KI-ANBIETER", [
                {"label": "Gemini", "icon": "✨",
                 "action": lambda: self.set_ai_provider("gemini"),
                 "on": self.ai_provider == "gemini"},
                {"label": "ChatGPT", "icon": "🤖",
                 "action": lambda: self.set_ai_provider("openai"),
                 "on": self.ai_provider == "openai"},
                {"label": "OpenRouter", "icon": "🌐",
                 "action": lambda: self.set_ai_provider("openrouter"),
                 "on": self.ai_provider == "openrouter"},
                {"label": "Lokal (Ollama)", "icon": "💻",
                 "action": lambda: self.set_ai_provider("ollama"),
                 "on": self.ai_provider == "ollama"},
                {"label": "Zurück", "icon": "↩️", "action": go("ai")},
            ]
        if page == "settings":
            return "OPTIONEN", [
                {"label": "System", "icon": "🖥️", "action": go("system")},
                {"label": "Steuerung", "icon": "🎛️", "action": go("control")},
                {"label": "Laufen", "icon": "🚶", "action": self.toggle_walk,
                 "on": self.walking},
                {"label": "Physik", "icon": "🏀", "action": self.toggle_physics,
                 "on": self.physics_enabled},
                {"label": "Größe &\nFüße", "icon": "📏", "action": self.open_size_settings},
                {"label": "Name", "icon": "✏️", "action": self.start_name_prompt},
                {"label": "Emotionen", "icon": "🎭", "action": self.open_emotion_settings},
                {"label": "Audio", "icon": "🔊", "action": go("audio")},
                {"label": "KI", "icon": "🧠", "action": go("ai"), "on": self.ai_enabled},
                {"label": "Autostart", "icon": "🚀", "action": self.toggle_autostart,
                 "on": self.autostart_enabled()},
                {"label": "Zurück", "icon": "↩️", "action": go("main")},
            ]
        if page == "system":
            return "SYSTEMLEBEN", [
                {"label": "Fenster", "icon": "🖥️", "action": self.toggle_window_mode,
                 "on": self.window_mode},
                {"label": "Mini\nauto", "icon": "📺", "action": self.toggle_mini_auto,
                 "on": self.mini_auto},
                {"label": "Mini\njetzt", "icon": "🔍", "action": self.toggle_mini_manual,
                 "on": self.mini_manual},
                {"label": "Lebensmodus", "icon": "🧬", "action": self.toggle_living_mode,
                 "on": self.living_mode},
                {"label": "PC-Monitor", "icon": "📟", "action": self.toggle_sys_monitor,
                 "on": self.sys_monitor},
                {"label": "Telefon\nmodus", "icon": "📱", "action": self.toggle_phone_mode,
                 "on": self.phone_mode},
                {"label": "Fadenkreuz", "icon": "🎯", "action": self.toggle_crosshair,
                 "on": self.crosshair_mode},
                {"label": "Zurück", "icon": "↩️", "action": go("settings")},
            ]
        return "NOVA", [
            {"label": "Aktionen", "icon": "💖", "action": go("care")},
            {"label": "Spielen", "icon": "🎮", "action": go("play")},
            {"label": "Shop", "icon": "🛒", "action": go("shop")},
            {"label": "Werkzeuge", "icon": "🧰", "action": go("tools")},
            {"label": "Status", "icon": "📊", "action": self.show_status},
            {"label": "Optionen", "icon": "⚙️", "action": go("settings")},
            {"label": "Beenden", "icon": "👋", "action": self.quit_app},
        ]

    def close_radial_menu(self):
        if self.radial_animation_id:
            try:
                self.root.after_cancel(self.radial_animation_id)
            except tk.TclError:
                pass
        self.radial_animation_id = None
        if self.radial_window is not None:
            try:
                self.radial_window.destroy()
            except tk.TclError:
                pass
        self.radial_window = None
        self.radial_canvas = None
        self.radial_items = []

    def open_radial_page(self, page):
        self.root.after_idle(lambda: self.show_radial_menu(page=page))

    def show_radial_menu(self, x=None, y=None, page="main"):
        """Öffnet eine Menüseite als Kreis um die Klickposition."""
        if self.quitting:
            return
        if x is not None:
            self.radial_x = x
        if y is not None:
            self.radial_y = y
        self.close_radial_menu()
        title, entries = self.radial_page(page)
        self.radial_page_name = page
        size = RADIAL_SIZE
        cx = cy = size // 2

        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.config(bg=TRANS)
        try:
            win.attributes("-transparentcolor", TRANS)
        except tk.TclError:
            pass

        px = cx if self.radial_x is None else self.radial_x
        py = cy if self.radial_y is None else self.radial_y
        if IS_WIN:
            # Metriken 76-79 beschreiben den ganzen virtuellen Desktop (auch negative Ursprünge).
            vx, vy = user32.GetSystemMetrics(76), user32.GetSystemMetrics(77)
            vw, vh = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
        else:
            vx, vy = win.winfo_vrootx(), win.winfo_vrooty()
            vw, vh = win.winfo_vrootwidth(), win.winfo_vrootheight()
        left = int(max(vx, min(px - cx, vx + vw - size)))
        top = int(max(vy, min(py - cy, vy + vh - size)))
        win.geometry(f"{size}x{size}+0+0")
        win.update_idletasks()
        self.place_radial(win, left, top)
        self.radial_origin = (left, top)
        self.radial_offset = (left - self.x, top - self.y)      # Abstand zu NOVA merken
        self.radial_inside_until = time.time() + 3.0

        canvas = tk.Canvas(win, width=size, height=size, bg=TRANS, highlightthickness=0)
        canvas.pack()
        canvas.bind("<Motion>", self.on_radial_motion)
        canvas.bind("<Button-1>", self.on_radial_click)
        canvas.bind("<Button-3>", lambda e: self.close_radial_menu())
        win.bind("<Escape>", lambda e: self.close_radial_menu())
        win.focus_force()
        self.radial_window = win
        self.radial_canvas = canvas

        count = len(entries)
        ring = 105 if count <= 6 else 140
        radius = 27 if count <= 6 else 24
        items = []
        for i, entry in enumerate(entries):
            # Halbkreis: von links (180°) über oben nach rechts (0°)
            angle = math.pi / 2 if count == 1 else math.pi - math.pi * i / (count - 1)
            items.append(dict(entry, r0=radius,
                              fx=cx + ring * math.cos(angle), fy=cy - ring * math.sin(angle)))
        for i, item in enumerate(items):
            item.update({"x": cx, "y": cy, "cx": cx, "cy": cy, "r": 4, "hover": False,
                         "oval": None, "text": None, "delay": i * 45, "text_visible": False})
            item.setdefault("on", None)
            item.setdefault("dim", False)
            item.setdefault("icon", "•")
        self.radial_items = items
        self.animate_radial_items(time.monotonic())

    def place_radial(self, win, left, top):
        """Setzt das Menüfenster (Windows: auch auf Monitoren links/oberhalb des Hauptmonitors)."""
        if IS_WIN:
            try:
                hwnd = user32.GetAncestor(win.winfo_id(), 2) or win.winfo_id()
                # NOSIZE | NOACTIVATE | SHOWWINDOW, HWND_TOPMOST
                if user32.SetWindowPos(hwnd, ctypes.c_void_p(-1), int(left), int(top),
                                       0, 0, 0x0001 | 0x0010 | 0x0040):
                    return
            except Exception:
                pass
        win.geometry(f"+{int(left)}+{int(top)}")

    def follow_radial(self):
        """Das Menü bewegt sich mit NOVA mit (Ziehen, Fenster-Modus, Mini-Ecke, Sprung)."""
        if self.radial_window is None:
            return
        left = int(self.x + self.radial_offset[0])
        top = int(self.y + self.radial_offset[1])
        if (left, top) != self.radial_origin:
            self.radial_origin = (left, top)
            self.place_radial(self.radial_window, left, top)

    def draw_radial_items(self):
        canvas = self.radial_canvas
        if canvas is None:
            return
        for item in self.radial_items:
            x, y = item["x"], item["y"]
            r = item["r"] * (1.1 if item["hover"] and item["r"] >= item["r0"] else 1.0)
            if item["dim"]:
                fill, outline, tcolor = PANEL, DIM, DIM
            elif item["hover"]:
                fill, outline, tcolor = EDGE, LIGHT, LIGHT
            elif item["on"]:
                fill, outline, tcolor = EDGE, LIGHT, LIGHT
            else:
                fill, outline, tcolor = PANEL2, ACCENT, LIGHT
            if item.get("col"):
                outline = item["col"]
            icon_font = ("Segoe UI Emoji", 17 if item["r0"] >= 27 else 16)
            label_font = ("Consolas", 10, "bold")
            # Im Ruhezustand bleibt nur das Symbol sichtbar; beim Hover erscheint der große Name.
            display_text = item["label"] if item["hover"] else item["icon"]
            text_font = label_font if item["hover"] else icon_font
            text_width = 120 if item["hover"] else int(item["r0"] * 2 - 4)
            if item["oval"] is None:
                item["oval"] = canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill,
                                                  outline=outline, width=3)
                item["text"] = canvas.create_text(
                    x, y, text=display_text, width=text_width, fill=tcolor,
                    font=text_font, justify="center",
                    state="normal" if item["text_visible"] else "hidden")
            else:
                canvas.coords(item["oval"], x - r, y - r, x + r, y + r)
                canvas.itemconfigure(item["oval"], fill=fill, outline=outline)
                canvas.coords(item["text"], x, y)
                canvas.itemconfigure(item["text"], text=display_text, width=text_width,
                                     font=text_font, fill=tcolor,
                                     state="normal" if item["text_visible"] else "hidden")
        for item in self.radial_items:
            if item["hover"] and item["text"] is not None:
                canvas.tag_raise(item["text"])

    def animate_radial_items(self, start_time):
        """Blendet die Kugeln nacheinander mit weicher Bewegung ein."""
        if self.radial_canvas is None:
            return
        elapsed = (time.monotonic() - start_time) * 1000
        finished = True
        for item in self.radial_items:
            progress = clamp((elapsed - item["delay"]) / 280, 0.0, 1.0)
            if progress < 1.0:
                finished = False
            eased = 1 - (1 - progress) ** 3
            item["x"] = item["cx"] + (item["fx"] - item["cx"]) * eased
            item["y"] = item["cy"] + (item["fy"] - item["cy"]) * eased
            item["r"] = max(4, item["r0"] * (0.12 + 0.88 * eased))
            item["text_visible"] = progress >= 0.7
        self.draw_radial_items()
        if not finished:
            self.radial_animation_id = self.root.after(
                16, lambda: self.animate_radial_items(start_time))
        else:
            self.radial_animation_id = None

    def on_radial_motion(self, event):
        changed = False
        for item in self.radial_items:
            dx, dy = event.x - item["x"], event.y - item["y"]
            hovered = dx * dx + dy * dy <= item["r"] * item["r"]
            if hovered != item["hover"]:
                item["hover"] = hovered
                changed = True
        if changed:
            self.draw_radial_items()

    def on_radial_click(self, event):
        for item in self.radial_items:
            dx, dy = event.x - item["x"], event.y - item["y"]
            if dx * dx + dy * dy <= item["r"] * item["r"]:
                action = item["action"]
                self.close_radial_menu()
                self.ai_radial_action_active = True
                self.ai_radial_action_spoke = False
                self.ai_radial_action_has_message = False
                try:
                    action()
                finally:
                    self.ai_radial_action_active = False
                if self._uses_ai_speech() and not self.ai_radial_action_spoke:
                    if not self.ai_radial_action_has_message or self.voice_enabled:
                        self._say_ai_radial_response()
                return

    def check_radial_idle(self, now):
        """Schließt das Menü, wenn der Mauszeiger es länger verlassen hat (Klicks gehen durch)."""
        try:
            px, py = self.root.winfo_pointerxy()
        except tk.TclError:
            return
        ox, oy = self.radial_origin
        c = RADIAL_SIZE // 2
        if math.hypot(px - (ox + c), py - (oy + c)) <= c + 20:
            self.radial_inside_until = now + 1.6
        elif now > self.radial_inside_until:
            self.close_radial_menu()

    # ================= KI-Modus =================
    def _load_ai_api_key(self):
        if self.ai_provider == "ollama":
            return ""
        if self.ai_provider == "openai":
            return os.environ.get("OPENAI_API_KEY", "").strip()
        if self.ai_provider == "openrouter":
            return os.environ.get("OPENROUTER_API_KEY", "").strip()
        return (os.environ.get("GOOGLE_API_KEY")
                or os.environ.get("GEMINI_API_KEY", "")).strip()

    def _ai_provider_name(self):
        if self.ai_provider == "openai":
            return "ChatGPT (OpenAI API)"
        if self.ai_provider == "openrouter":
            return "OpenRouter"
        if self.ai_provider == "ollama":
            return "Ollama (lokal)"
        return "Google Gemini"

    def _ai_is_ready(self):
        return self.ai_provider == "ollama" or bool(self.ai_api_key)

    def _load_local_ai_memory(self):
        try:
            self.ai_history = load_ai_memory()
            self.ai_memory_error = ""
            self.ai_memory_load_failed = False
        except (OSError, ValueError) as error:
            self.ai_history = []
            self.ai_memory_error = f"Lokale KI-Erinnerung konnte nicht geladen werden: {error}"
            self.ai_memory_load_failed = True

    def _save_local_ai_memory(self):
        if self.ai_provider != "ollama":
            return True
        if self.ai_memory_load_failed:
            if self.ai_status is not None:
                self.ai_status.configure(text=self.ai_memory_error)
            else:
                self.say(self.ai_memory_error, 8, speak=False)
            return False
        try:
            write_json_atomic(AI_MEMORY_FILE, sanitize_ai_memory(self.ai_history))
        except (OSError, TypeError, ValueError) as error:
            self.ai_memory_error = f"Lokale KI-Erinnerung konnte nicht gespeichert werden: {error}"
            if self.ai_status is not None:
                self.ai_status.configure(text=self.ai_memory_error)
            else:
                self.say(self.ai_memory_error, 8, speak=False)
            return False
        self.ai_memory_error = ""
        return True

    def clear_ai_memory(self):
        if self.ai_provider != "ollama":
            return
        if self.ai_busy or self.ai_voice_busy:
            if self.ai_status is not None:
                self.ai_status.configure(text="Bitte warte, bis die aktuelle KI-Anfrage beendet ist.")
            return
        if not messagebox.askyesno(
                "KI-Erinnerung löschen",
                "Den lokal gespeicherten Gesprächsverlauf wirklich löschen?",
                parent=self.ai_window):
            return
        for path in (AI_MEMORY_FILE, AI_MEMORY_FILE + ".bak", AI_MEMORY_FILE + ".tmp"):
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
            except OSError as error:
                self.ai_memory_error = f"KI-Erinnerung konnte nicht gelöscht werden: {error}"
                if self.ai_status is not None:
                    self.ai_status.configure(text=self.ai_memory_error)
                return
        self.ai_history = []
        self.ai_memory_error = ""
        self.ai_memory_load_failed = False
        if self.ai_chat is not None:
            self.ai_chat.configure(state="normal")
            self.ai_chat.delete("1.0", "end")
            self.ai_chat.configure(state="disabled")
            self._append_ai_message(
                self._ai_character_name(), "Frag mich etwas oder lass mich den Bildschirm ansehen."
            )
        if self.ai_status is not None:
            self.ai_status.configure(text="Lokale KI-Erinnerung gelöscht.")

    def _ai_character_name(self):
        name = self.s.get("name", "")
        return name.strip() if isinstance(name, str) and name.strip() else "NOVA"

    def _ai_system_prompt(self, provider):
        name = self._ai_character_name()
        prompt = (
            f"Du bist {name}, die freundliche KI-Persönlichkeit und das Desktop-Haustier. "
            f"Dein Name ist {name}; nenne dich nicht NOVA, außer der Name lautet wirklich NOVA. "
            "Antworte auf Deutsch, klar und eher kurz. Wenn du gefragt wirst, wer du bist, "
            f"stelle dich als {name} vor. NOVA ist der Name der App. "
            f"Spiele konsequent die Rolle von {name}: antworte dialogisch in der Ich-Form, "
            "reagiere direkt auf das Geschehen und vermeide Meta-Einleitungen wie "
            "„Hier sind die Texte“ oder Erklärungen darüber, dass du ein Sprachmodell bist. "
            "Wenn ausdrücklich nach technischen Fakten gefragt wird, antworte ehrlich und "
            "bleibe dabei in deiner Stimme. "
            "Das neutrale Avatarbild ist ausschließlich eine visuelle Referenz für dein "
            "Aussehen; es zeigt keinen Desktop. Beschreibe oder erwähne dein Aussehen nur, "
            "wenn der Nutzer ausdrücklich danach fragt. Begrüße den Nutzer normal und "
            "wiederhole keine frühere Selbstbeschreibung."
        )
        if provider == "openrouter":
            prompt += " " + OPENROUTER_SYSTEM_PROMPT
        return prompt

    def set_ai_provider(self, provider):
        if provider not in ("gemini", "openai", "openrouter", "ollama") or provider == self.ai_provider:
            return
        if self.ai_window is not None:
            self.close_ai_window()
        else:
            self._stop_ai_voice_chat()
        previous_memory_error = self.ai_memory_error
        self.ai_session_id += 1
        self.ai_busy = False
        self.ai_voice_reply_pending = False
        self._set_ai_busy(False)
        self._reset_ai_speech()
        self.ai_provider = provider
        self.s["ai_provider"] = provider
        self.ai_history = []
        self.ai_memory_error = ""
        self.ai_memory_load_failed = False
        if provider == "ollama":
            self._load_local_ai_memory()
        self.ai_api_key = self._load_ai_api_key() if self.ai_enabled else ""
        self.save()
        label = {
            "openai": "ChatGPT",
            "openrouter": "OpenRouter",
            "gemini": "Gemini",
            "ollama": "Ollama lokal",
        }[provider]
        message = f"KI-Anbieter auf {label} gestellt."
        if self.ai_memory_error:
            message += " " + self.ai_memory_error
        elif previous_memory_error:
            message += " " + previous_memory_error
        self.say(message, 6, speak=False)
        if self.ai_enabled and self._ai_is_ready():
            self._request_ai_speech_lines()

    def set_ai_model(self):
        if self.ai_model_entry is None:
            return
        model = re.sub(r"[\x00-\x1f\x7f]", "", self.ai_model_entry.get()).strip()[:128]
        if not model:
            if self.ai_status is not None:
                self.ai_status.configure(text="Bitte einen Ollama-Modellnamen eingeben.")
            return
        self.ai_model = model
        self.s["ai_model"] = model
        self.save()
        self._reset_ai_speech()
        if self.ai_enabled:
            self._request_ai_speech_lines()
        if self.ai_status is not None:
            self.ai_status.configure(text=f"Lokales Modell: {model}")

    def toggle_ai_mode(self):
        self.ai_enabled = not self.ai_enabled
        self.s["ai_enabled"] = self.ai_enabled
        if self.ai_enabled:
            self.ai_api_key = self._load_ai_api_key()
            message = "KI-Modus eingeschaltet. Chat und Bildschirm werden nur auf Anfrage gesendet."
            if self.ai_provider == "ollama":
                message += f" Antworten laufen lokal mit {self.ai_model}."
            if self._ai_is_ready():
                message += f" Sprechtexte werden über {self._ai_provider_name()} vorbereitet."
                self._request_ai_speech_lines()
            else:
                message += " Für KI-Sprechtexte fehlt der API-Key; bis dahin bleiben Standardsprüche aktiv."
        else:
            if self.ai_window is not None:
                self.close_ai_window()
            else:
                self._stop_ai_voice_chat()
                self.ai_session_id += 1
                self.ai_busy = False
                self.ai_voice_reply_pending = False
                self._set_ai_busy(False)
            self.ai_voice_reply_pending = False
            self.ai_api_key = ""
            if self.ai_provider == "ollama":
                self._save_local_ai_memory()
            else:
                self.ai_history = []
            self._reset_ai_speech()
            message = "KI-Modus ausgeschaltet."
            if self.ai_memory_error:
                message += " " + self.ai_memory_error
        self.save()
        self.say(message, 4, speak=False)

    def open_ai_window(self):
        if not self.ai_enabled:
            self.say("KI-Modus ist aus. Schalte ihn zuerst unter Einstellungen ein.",
                     4, speak=False)
            return
        if self.ai_window is not None:
            try:
                if self.ai_window.winfo_exists():
                    self.ai_window.deiconify()
                    self.ai_window.lift()
                    return
            except tk.TclError:
                pass

        win = NovaToplevel(self.root)
        win.title("NOVA – KI-Modus")
        win.attributes("-topmost", True)
        win.resizable(True, True)
        win.configure(bg=PANEL)
        win.geometry("720x620")
        self.ai_window = win
        self.bubble_text = ""
        self.bubble_until = 0.0
        win.protocol("WM_DELETE_WINDOW", self.close_ai_window)

        provider_name = self._ai_provider_name()
        history_note = (
            f"Die letzten {AI_MEMORY_MAX_TURNS} Textnachrichten bleiben lokal gespeichert; "
            "Avatar- und Bildschirmbilder werden nicht in der Erinnerung gespeichert."
            if self.ai_provider == "ollama" else
            "Der Chatverlauf bleibt bis zum Schließen im Arbeitsspeicher."
        )
        if self.ai_provider == "openai":
            billing_note = (
                "OpenAI-API-Nutzung wird separat abgerechnet und ist nicht im ChatGPT-Abo enthalten."
            )
        elif self.ai_provider == "openrouter":
            billing_note = (
                "NOVA nutzt openrouter/free ohne bezahlten Fallback; diese Anfragen sind kostenlos. "
                "KI-Sprüche verwenden nur einen allgemeinen Prompt; Limits und Datenschutz "
                "hängen vom gewählten Modellanbieter ab. Die kostenlose Route unterstützt "
                "Avatar-Bilder nicht immer."
            )
        elif self.ai_provider == "ollama":
            billing_note = (
                f"Ollama verarbeitet Chat und Avatarbild lokal auf diesem Computer. "
                f"Das visionfähige Modell {self.ai_model} muss vorher lokal heruntergeladen sein. "
                "Gemma 3 4B ist klein und schnell; ein größeres Modell wie Gemma 3 12B kann "
                "bessere Antworten liefern, braucht aber deutlich mehr Speicher und Rechenleistung."
            )
        else:
            billing_note = "Gemini-API-Nutzung kann Kontingent oder Kosten verbrauchen."
        tk.Label(win, text=f"NOVA · {provider_name.upper()}", bg=PANEL, fg=ACCENT,
                 font=("Consolas", 16, "bold")).pack(pady=(12, 4))
        tk.Label(
            win,
            text=(f"Chat und automatische Sprechtexte gehen an {provider_name}; {history_note} "
                  f"{billing_note} "
                  f"Das Mikrofon startet nur nach Klick auf Sprechen oder Dauerhören. "
                  f"Sprechen füllt einen einzelnen erkannten Satz zur Prüfung ein; Dauerhören "
                  f"sendet erkannte Sätze automatisch an {provider_name} und bleibt auch während "
                  "meiner gesprochenen Antwort aktiv. Bis zu vier weitere Sätze werden während "
                  "einer Antwort zwischengespeichert. Kopfhörer verhindern, dass meine Antwort "
                  "ins Mikrofon zurückgelangt. Stopp oder Schließen des "
                  "Chatfensters beendet Dauerhören. "
                  "Bei jeder Chatnachricht wird zusätzlich nur das neutrale NOVA-Avatarbild übertragen, "
                  "nicht der Desktop. Bildschirmbilder werden nur nach Vorschau und Bestätigung "
                  "gesendet."),
            bg=PANEL, fg=LIGHT, font=("Consolas", 9), wraplength=680, justify="center",
        ).pack(padx=16, pady=(0, 10))

        self.ai_model_entry = None
        if self.ai_provider == "ollama":
            model_row = tk.Frame(win, bg=PANEL)
            model_row.pack(fill="x", padx=12, pady=(0, 6))
            self.ai_model_entry = tk.Entry(
                model_row, bg=PANEL2, fg=LIGHT, insertbackground=ACCENT,
                relief="flat", highlightthickness=1, highlightbackground=EDGE,
            )
            self.ai_model_entry.insert(0, self.ai_model)
            self.ai_model_entry.pack(side="left", fill="x", expand=True, ipady=5)
            tk.Button(
                model_row, text="Modell übernehmen", command=self.set_ai_model,
                bg=EDGE, fg=LIGHT, activebackground=ACCENT, activeforeground=LIGHT,
                relief="flat", font=("Consolas", 9, "bold"),
            ).pack(side="left", padx=(6, 0), ipady=3)
            self.ai_clear_memory_button = tk.Button(
                model_row, text="Erinnerung löschen", command=self.clear_ai_memory,
                bg=PANEL2, fg=LIGHT, activebackground=EDGE, activeforeground=LIGHT,
                relief="flat", font=("Consolas", 8),
            )
            self.ai_clear_memory_button.pack(side="left", padx=(6, 0), ipady=3)
        else:
            key_row = tk.Frame(win, bg=PANEL)
            key_row.pack(fill="x", padx=12, pady=(0, 6))
            self.ai_key_entry = tk.Entry(
                key_row, show="*", bg=PANEL2, fg=LIGHT, insertbackground=ACCENT,
                relief="flat", highlightthickness=1, highlightbackground=EDGE,
            )
            self.ai_key_entry.pack(side="left", fill="x", expand=True, ipady=5)
            tk.Button(
                key_row, text="Key übernehmen", command=self.set_ai_key,
                bg=EDGE, fg=LIGHT, activebackground=ACCENT, activeforeground=LIGHT,
                relief="flat", font=("Consolas", 9, "bold"),
            ).pack(side="left", padx=(6, 0), ipady=3)
            tk.Button(
                key_row, text="Key erstellen", command=self.open_ai_key_page,
                bg=PANEL2, fg=LIGHT, activebackground=EDGE, activeforeground=LIGHT,
                relief="flat", font=("Consolas", 9),
            ).pack(side="left", padx=(6, 0), ipady=3)

        self.ai_status = tk.Label(
            win,
            text=(f"Ollama-Modell: {self.ai_model}; lokale Erinnerung: "
                  f"{len(self.ai_history)} Textnachrichten."
                  + (f" {self.ai_memory_error}" if self.ai_memory_error else "")
                  if self.ai_provider == "ollama" else
                  "API-Key aus Umgebung geladen." if self.ai_api_key else
                  "API-Key fehlt. Er wird von NOVA nicht gespeichert."),
            bg=PANEL, fg=DIM, font=("Consolas", 8), anchor="w",
        )
        self.ai_status.pack(fill="x", padx=14, pady=(0, 8))

        chat_frame = tk.Frame(win, bg=PANEL2, highlightthickness=1, highlightbackground=EDGE)
        chat_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        scrollbar = tk.Scrollbar(chat_frame)
        scrollbar.pack(side="right", fill="y")
        self.ai_chat = tk.Text(
            chat_frame, bg=PANEL2, fg=LIGHT, insertbackground=ACCENT,
            font=("Consolas", 10), wrap="word", state="disabled",
            yscrollcommand=scrollbar.set, relief="flat", padx=8, pady=8,
        )
        self.ai_chat.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.ai_chat.yview)
        self.ai_chat.tag_configure("user", foreground="#ff7180")
        self.ai_chat.tag_configure("nova", foreground=LIGHT)
        if self.ai_provider == "ollama" and self.ai_history:
            for turn in self.ai_history:
                text = "\n".join(
                    part["text"] for part in turn.get("parts", [])
                    if isinstance(part, dict) and isinstance(part.get("text"), str)
                )
                if text:
                    speaker = "Du" if turn.get("role") == "user" else self._ai_character_name()
                    self._append_ai_message(speaker, text)
        else:
            self._append_ai_message(
                self._ai_character_name(), "Frag mich etwas oder lass mich den Bildschirm ansehen."
            )

        prompt_row = tk.Frame(win, bg=PANEL)
        prompt_row.pack(fill="x", padx=12, pady=(0, 12))
        self.ai_prompt_entry = tk.Entry(
            prompt_row, bg=PANEL2, fg=LIGHT, insertbackground=ACCENT,
            relief="flat", highlightthickness=1, highlightbackground=EDGE,
        )
        self.ai_prompt_entry.pack(side="left", fill="x", expand=True, ipady=7)
        self.ai_prompt_entry.bind("<Return>", self.send_ai_message)
        self.ai_send_button = tk.Button(
            prompt_row, text="Senden", command=self.send_ai_message,
            bg=EDGE, fg=LIGHT, activebackground=ACCENT, activeforeground=LIGHT,
            relief="flat", font=("Consolas", 9, "bold"),
        )
        self.ai_send_button.pack(side="left", padx=(6, 0), ipady=3)
        self.ai_voice_button = tk.Button(
            prompt_row, text="🎙 Sprechen", command=self.start_ai_voice_input,
            bg=PANEL2, fg=LIGHT, activebackground=EDGE, activeforeground=LIGHT,
            relief="flat", font=("Consolas", 9),
        )
        self.ai_voice_button.pack(side="left", padx=(6, 0), ipady=3)
        self.ai_voice_continuous_button = tk.Button(
            prompt_row, text="Dauerhören", command=self.start_ai_voice_chat,
            bg=PANEL2, fg=LIGHT, activebackground=EDGE, activeforeground=LIGHT,
            relief="flat", font=("Consolas", 8),
        )
        self.ai_voice_continuous_button.pack(side="left", padx=(6, 0), ipady=3)
        self._update_ai_voice_chat_button()
        self.ai_screen_button = tk.Button(
            prompt_row, text="Bildschirm ansehen", command=self.capture_ai_screen,
            bg=PANEL2, fg=LIGHT, activebackground=EDGE, activeforeground=LIGHT,
            relief="flat", font=("Consolas", 9, "bold"),
        )
        self.ai_screen_button.pack(side="left", padx=(6, 0), ipady=3)
        self._set_ai_busy(self.ai_busy)
        self.ai_prompt_entry.focus_set()

    def close_ai_window(self):
        self._stop_ai_voice_chat()
        self.ai_session_id += 1
        self.ai_voice_reply_pending = False
        if self.ai_provider == "ollama":
            self._save_local_ai_memory()
        else:
            self.ai_history = []
        self.ai_busy = False
        self._close_ai_preview()
        win, self.ai_window = self.ai_window, None
        self.ai_chat = None
        self.ai_prompt_entry = None
        self.ai_key_entry = None
        self.ai_model_entry = None
        self.ai_status = None
        self.ai_send_button = None
        self.ai_voice_button = None
        self.ai_voice_continuous_button = None
        self.ai_screen_button = None
        self.ai_clear_memory_button = None
        if win is not None:
            try:
                win.destroy()
            except tk.TclError:
                pass
        self.s["ai_enabled"] = self.ai_enabled
        self.s["ai_provider"] = self.ai_provider
        self.save()
        if self.ai_memory_error:
            self.say(self.ai_memory_error, 8, speak=False)

    def set_ai_key(self):
        if not self.ai_enabled or self.ai_key_entry is None:
            return
        key = self.ai_key_entry.get().strip()
        if not key:
            if self.ai_status is not None:
                self.ai_status.configure(text="Bitte zuerst einen API-Key eingeben.")
            return
        self.ai_api_key = key
        self.ai_key_entry.delete(0, "end")
        if self.ai_status is not None:
            self.ai_status.configure(text="API-Key nur im Arbeitsspeicher übernommen.")
        if self.ai_enabled:
            self._request_ai_speech_lines()

    def open_ai_key_page(self):
        if self.ai_provider == "openai":
            url = "https://platform.openai.com/api-keys"
            title = "NOVA – OpenAI"
            error = "Die OpenAI-API-Key-Seite konnte nicht geöffnet werden."
        elif self.ai_provider == "openrouter":
            url = "https://openrouter.ai/settings/keys"
            title = "NOVA – OpenRouter"
            error = "Die OpenRouter-API-Key-Seite konnte nicht geöffnet werden."
        else:
            url = "https://aistudio.google.com/apikey"
            title = "NOVA – Gemini"
            error = "Die Google-AI-Studio-Seite konnte nicht geöffnet werden."
        if not webbrowser.open(url):
            messagebox.showerror(title, error, parent=self.ai_window)

    def _append_ai_message(self, speaker, text):
        if self.ai_chat is None:
            return
        try:
            self.ai_chat.configure(state="normal")
            tag = "user" if speaker == "Du" else "nova"
            self.ai_chat.insert("end", speaker + ": ", tag)
            self.ai_chat.insert("end", text + "\n\n")
            self.ai_chat.configure(state="disabled")
            self.ai_chat.see("end")
        except tk.TclError:
            pass

    def send_ai_message(self, event=None):
        if (not self.ai_enabled or self.ai_busy or self.ai_voice_busy or self.ai_voice_continuous or
                self.ai_prompt_entry is None):
            return "break"
        prompt = self.ai_prompt_entry.get().strip()
        if not prompt:
            return "break"
        if not self._ai_is_ready():
            if self.ai_status is not None:
                self.ai_status.configure(text="API-Key fehlt. Erstelle und übernimm zuerst einen Key.")
            return "break"
        self.ai_prompt_entry.delete(0, "end")
        self._start_ai_request(prompt)
        return "break"

    def start_ai_voice_chat(self):
        if not self.ai_enabled:
            self.say("Schalte zuerst den KI-Modus ein.", 4, speak=False)
            return False
        if self.ai_voice_continuous:
            self._stop_ai_voice_chat(announce=True)
            return False
        self.stop_voice()
        self.ai_voice_continuous = True
        self.ai_voice_continuous_token += 1
        self._update_ai_voice_chat_button()
        if not self.start_ai_voice_input(auto_send=True):
            self.ai_voice_continuous = False
            self.ai_voice_continuous_token += 1
            self._update_ai_voice_chat_button()
            return False
        if self.ai_radial_action_active:
            self.ai_radial_action_spoke = True
        return True

    def _update_ai_voice_chat_button(self):
        if self.ai_voice_continuous_button is None:
            return
        try:
            self.ai_voice_continuous_button.configure(
                text="Stopp" if self.ai_voice_continuous else "Dauerhören",
                bg=ACCENT if self.ai_voice_continuous else PANEL2,
                activebackground=EDGE if self.ai_voice_continuous else ACCENT,
            )
        except tk.TclError:
            self.ai_voice_continuous_button = None

    def _stop_ai_voice_chat(self, announce=False):
        was_active = self.ai_voice_continuous
        self.ai_voice_continuous = False
        self.ai_voice_continuous_token += 1
        if self.ai_voice_restart_after is not None:
            try:
                self.root.after_cancel(self.ai_voice_restart_after)
            except tk.TclError:
                pass
            self.ai_voice_restart_after = None
        self.ai_voice_waiting_for_sequence = None
        self.ai_voice_pending_prompts = []
        self._cancel_ai_voice_input()
        self._update_ai_voice_chat_button()
        if was_active:
            if self.ai_radial_action_active:
                self.ai_radial_action_spoke = True
            message = "Dauerhören beendet."
            if self.ai_status is not None:
                self.ai_status.configure(text=message)
            elif announce:
                self.say(message, 4, speak=False)

    def _schedule_ai_voice_restart(self, delay_ms=500):
        if not self.ai_voice_continuous:
            return
        if self.ai_voice_restart_after is not None:
            try:
                self.root.after_cancel(self.ai_voice_restart_after)
            except tk.TclError:
                pass
        token = self.ai_voice_continuous_token
        try:
            self.ai_voice_restart_after = self.root.after(
                delay_ms, lambda: self._restart_ai_voice_chat(token)
            )
        except tk.TclError:
            self.ai_voice_restart_after = None

    def _restart_ai_voice_chat(self, token):
        self.ai_voice_restart_after = None
        if token != self.ai_voice_continuous_token or not self.ai_voice_continuous:
            return
        if self.ai_voice_busy or len(self.ai_voice_pending_prompts) >= AI_VOICE_QUEUE_MAX:
            return
        if not self.start_ai_voice_input(auto_send=True, announce=False):
            self._stop_ai_voice_chat()

    def _send_next_ai_voice_prompt(self):
        if not self.ai_voice_continuous or not self.ai_voice_pending_prompts:
            return False
        if (self.ai_busy or self.ai_voice_busy or
                self.ai_voice_waiting_for_sequence is not None):
            if self.ai_busy:
                message = "Ich bearbeite noch deine vorige Nachricht; die neue wartet kurz."
            elif self.ai_voice_waiting_for_sequence is not None:
                message = "Ich spreche noch; deine neue Nachricht wartet kurz."
            else:
                message = "Ich höre noch zu; deine Nachricht wartet kurz."
            if self.ai_status is not None:
                self.ai_status.configure(text=message)
            elif self.ai_window is None:
                self.say(message, 5, speak=False)
            return False
        prompt = self.ai_voice_pending_prompts.pop(0)
        self.ai_voice_reply_pending = self._start_ai_request(prompt)
        if not self.ai_voice_reply_pending:
            self.say("Deine Nachricht konnte nicht an die KI gesendet werden.", 5, speak=False)
            return False
        if self.ai_window is None:
            self.say("NOVA denkt über deine Nachricht nach …", 8, speak=False)
        return True

    def process_voice_events(self):
        while True:
            try:
                session_id, process, sequence = self.voice_events.get_nowait()
            except queue.Empty:
                return
            if session_id != self.voice_session_id or process is not self.voice_process:
                continue
            if sequence == self.ai_voice_waiting_for_sequence:
                self.ai_voice_waiting_for_sequence = None
                self._send_next_ai_voice_prompt()
                if not self.ai_voice_busy and len(self.ai_voice_pending_prompts) < AI_VOICE_QUEUE_MAX:
                    self._schedule_ai_voice_restart(300)

    def _local_whisper_input_command(self):
        model_path = find_local_whisper_model()
        if (not IS_WIN or not os.path.isfile(WHISPER_INPUT_WORKER) or
                model_path is None):
            return None
        try:
            if (importlib.util.find_spec("faster_whisper") is None or
                    importlib.util.find_spec("sounddevice") is None):
                return None
        except (ImportError, ValueError):
            return None
        return [
            sys.executable, "-u", WHISPER_INPUT_WORKER,
            model_path,
        ]

    def start_ai_voice_input(self, auto_send=False, announce=True):
        if (not self.ai_enabled or (self.ai_busy and not self.ai_voice_continuous) or
                self.ai_voice_busy or
                (self.ai_voice_continuous and not auto_send)):
            return False
        if not self._ai_is_ready():
            message = "Für den gewählten KI-Anbieter fehlt noch der API-Key."
            if self.ai_status is not None:
                self.ai_status.configure(text=message)
            elif auto_send:
                self.say(message, 4, speak=False)
            return False
        whisper_command = self._local_whisper_input_command()
        powershell = shutil.which("powershell.exe") if whisper_command is None else None
        if (whisper_command is None and
                (not IS_WIN or not powershell or not os.path.isfile(WINDOWS_SPEECH_INPUT_WORKER))):
            message = "Lokale deutsche Spracherkennung ist nicht verfügbar."
            if self.ai_status is not None:
                self.ai_status.configure(text=message)
            elif auto_send:
                self.say(message, 4, speak=False)
            return False

        if not self.ai_voice_continuous:
            self.stop_voice()
        command = whisper_command or [
            powershell, "-NoLogo", "-NoProfile", "-NonInteractive",
            "-ExecutionPolicy", "Bypass", "-File", WINDOWS_SPEECH_INPUT_WORKER,
        ]
        recognition_engine = "Whisper lokal" if whisper_command else "Windows-SAPI"
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError as error:
            message = f"Mikrofon konnte nicht gestartet werden: {error}"
            if self.ai_status is not None:
                self.ai_status.configure(text=message)
            elif auto_send:
                self.say(message, 5, speak=False)
            return False

        self.ai_voice_session_id += 1
        session_id = self.ai_voice_session_id
        self.ai_voice_process = process
        self.ai_voice_busy = True
        self.ai_voice_auto_send = bool(auto_send)
        self._set_ai_busy(self.ai_busy)
        if self.ai_status is not None:
            self.ai_status.configure(
                text=(f"Dauerhören aktiv ({recognition_engine}) – sprich jetzt; danach antworte ich und höre wieder zu."
                      if self.ai_voice_continuous else
                      f"Höre zu ({recognition_engine}) … Der erkannte Text wird danach an die KI gesendet."
                      if auto_send else
                      f"Höre zu ({recognition_engine}) … Zum Senden musst du danach Senden drücken.")
            )
        elif auto_send and announce:
            self.say(
                "Dauerhören aktiv. Sprich jetzt; nach meiner Antwort höre ich wieder zu."
                if self.ai_voice_continuous else "Ich höre zu. Sprich jetzt.",
                5, speak=False,
            )

        def recognize():
            try:
                output, error_text = process.communicate(
                    timeout=120 if whisper_command else 68
                )
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                    process.communicate()
                except (OSError, ValueError):
                    pass
                result = ("error", "Zeitüberschreitung bei der Spracherkennung.")
            except (OSError, ValueError) as error:
                result = ("error", str(error))
            else:
                transcript = re.sub(r"\s+", " ", (output or "")).strip()
                if process.returncode == 0 and transcript:
                    result = ("success", transcript)
                elif process.returncode == 2:
                    result = ("empty", (error_text or "").strip())
                else:
                    detail = (error_text or "").strip()
                    result = (
                        "error",
                        detail or f"Spracherkennung wurde mit Code {process.returncode} beendet.",
                    )
            self.ai_voice_results.put((session_id, result[0], result[1], process))

        try:
            threading.Thread(target=recognize, daemon=True, name="nova-ai-voice-input").start()
        except RuntimeError as error:
            self.ai_voice_process = None
            self.ai_voice_busy = False
            self.ai_voice_auto_send = False
            try:
                process.terminate()
            except OSError:
                pass
            self._set_ai_busy(self.ai_busy)
            if self.ai_status is not None:
                self.ai_status.configure(text=f"Spracherkennung konnte nicht gestartet werden: {error}")
            elif auto_send:
                self.say("Spracherkennung konnte nicht gestartet werden.", 5, speak=False)
            return False
        return True

    def _cancel_ai_voice_input(self):
        self.ai_voice_session_id += 1
        process, self.ai_voice_process = self.ai_voice_process, None
        self.ai_voice_busy = False
        self.ai_voice_auto_send = False
        if process is not None and process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass
        self._set_ai_busy(self.ai_busy)

    def process_ai_voice_results(self):
        while True:
            try:
                session_id, status, result, process = self.ai_voice_results.get_nowait()
            except queue.Empty:
                return
            if session_id != self.ai_voice_session_id:
                continue
            if self.ai_voice_process is process:
                self.ai_voice_process = None
            self.ai_voice_busy = False
            auto_send, self.ai_voice_auto_send = self.ai_voice_auto_send, False
            self._set_ai_busy(self.ai_busy)
            if status == "success":
                if auto_send:
                    if self.ai_voice_continuous:
                        if len(self.ai_voice_pending_prompts) < AI_VOICE_QUEUE_MAX:
                            self.ai_voice_pending_prompts.append(result)
                        elif self.ai_status is not None:
                            self.ai_status.configure(
                                text="Warteschlange voll. Warte kurz, bis eine Antwort fertig ist."
                            )
                        else:
                            self.say("Warteschlange voll. Bitte einen Moment warten.", 5,
                                     speak=False)
                        self._send_next_ai_voice_prompt()
                        if len(self.ai_voice_pending_prompts) < AI_VOICE_QUEUE_MAX:
                            self._schedule_ai_voice_restart(250)
                    else:
                        self.ai_voice_reply_pending = self._start_ai_request(result)
                        if not self.ai_voice_reply_pending:
                            self.say("Deine Nachricht konnte nicht an die KI gesendet werden.", 5,
                                     speak=False)
                        elif self.ai_window is None:
                            self.say("NOVA denkt über deine Nachricht nach …", 8, speak=False)
                    continue
                if self.ai_prompt_entry is not None:
                    self.ai_prompt_entry.delete(0, "end")
                    self.ai_prompt_entry.insert(0, result)
                    self.ai_prompt_entry.focus_set()
                if self.ai_status is not None:
                    self.ai_status.configure(
                        text="Text erkannt. Prüfe ihn und drücke Senden, um ihn an die KI zu schicken."
                    )
            elif status == "empty":
                if self.ai_voice_continuous:
                    if self.ai_status is not None:
                        self.ai_status.configure(text="Keine Sprache erkannt. Dauerhören läuft weiter …")
                    self._send_next_ai_voice_prompt()
                    if len(self.ai_voice_pending_prompts) < AI_VOICE_QUEUE_MAX:
                        self._schedule_ai_voice_restart(300)
                elif self.ai_status is not None:
                    self.ai_status.configure(text="Keine Sprache erkannt. Drücke Sprechen und versuche es erneut.")
                elif auto_send:
                    self.say("Ich habe dich nicht verstanden. Versuch es noch einmal.", 5,
                             speak=False)
            else:
                self._stop_ai_voice_chat()
                if self.ai_status is not None:
                    self.ai_status.configure(text=f"Spracherkennung fehlgeschlagen: {result}")
                elif auto_send:
                    self.say(f"Spracherkennung fehlgeschlagen: {result}", 5, speak=False)

    def capture_ai_screen(self):
        if not self.ai_enabled or self.ai_busy or self.ai_voice_busy or self.ai_voice_continuous:
            return
        if not self._ai_is_ready():
            if self.ai_status is not None:
                self.ai_status.configure(text="Vor dem Screenshot-Upload bitte den API-Key übernehmen.")
            return
        if ImageGrab is None or ImageTk is None:
            messagebox.showerror(
                "NOVA – Bildschirm",
                "Für Bildschirmaufnahmen wird Pillow benötigt. Installiere es mit "
                "'python -m pip install pillow'.",
                parent=self.ai_window,
            )
            return
        if self.ai_window is not None:
            self.ai_window.withdraw()
        self.root.after(300, self._capture_ai_screen_now)

    def _capture_ai_screen_now(self):
        try:
            try:
                screenshot = ImageGrab.grab(all_screens=True)
            except TypeError:
                screenshot = ImageGrab.grab()
            screenshot.thumbnail((1920, 1080), Image.LANCZOS)
            image_buffer = io.BytesIO()
            screenshot.save(image_buffer, format="PNG", optimize=True)
            self.ai_pending_image = image_buffer.getvalue()
        except (OSError, ValueError) as error:
            if self.ai_window is not None:
                self.ai_window.deiconify()
            messagebox.showerror("NOVA – Bildschirm", f"Bildschirmaufnahme fehlgeschlagen: {error}",
                                 parent=self.ai_window)
            return

        if self.ai_window is not None:
            self.ai_window.deiconify()
            self.ai_window.lift()
        self._show_ai_screen_confirmation(screenshot.copy())

    def _show_ai_screen_confirmation(self, screenshot):
        if self.ai_window is None or ImageTk is None:
            self.ai_pending_image = None
            return
        win = NovaToplevel(self.ai_window, anchor=self.ai_window)
        provider_name = self._ai_provider_name()
        win.title(f"Bildschirm an {provider_name} senden?")
        win.transient(self.ai_window)
        win.attributes("-topmost", True)
        win.configure(bg=PANEL)
        win.resizable(False, False)
        self.ai_preview_window = win
        win.protocol("WM_DELETE_WINDOW", self._close_ai_preview)

        tk.Label(
            win,
            text="Das Vorschaubild zeigt alle angeschlossenen Bildschirme und wird beim Senden "
                 f"an {provider_name} übertragen. Verdecke vorher private Inhalte.",
            bg=PANEL, fg=LIGHT, font=("Consolas", 9), wraplength=680, justify="center",
        ).pack(padx=12, pady=10)
        screenshot.thumbnail((680, 420), Image.LANCZOS)
        self.ai_preview_photo = ImageTk.PhotoImage(screenshot)
        tk.Label(win, image=self.ai_preview_photo, bg=PANEL).pack(padx=10, pady=(0, 10))

        buttons = tk.Frame(win, bg=PANEL)
        buttons.pack(pady=(0, 10))
        tk.Button(
            buttons, text="Abbrechen", command=self._close_ai_preview,
            bg=PANEL2, fg=LIGHT, activebackground=EDGE, activeforeground=LIGHT,
            relief="flat", font=("Consolas", 9),
        ).pack(side="left", padx=5, ipady=4, ipadx=8)
        tk.Button(
            buttons, text=f"An {provider_name} senden", command=self.send_ai_screen,
            bg=EDGE, fg=LIGHT, activebackground=ACCENT, activeforeground=LIGHT,
            relief="flat", font=("Consolas", 9, "bold"),
        ).pack(side="left", padx=5, ipady=4, ipadx=8)
        win.grab_set()

    def _close_ai_preview(self):
        win, self.ai_preview_window = self.ai_preview_window, None
        self.ai_pending_image = None
        self.ai_preview_photo = None
        if win is not None:
            try:
                win.grab_release()
                win.destroy()
            except tk.TclError:
                pass

    def send_ai_screen(self):
        image_data = self.ai_pending_image
        if not self.ai_enabled or image_data is None or self.ai_busy:
            return
        self._close_ai_preview()
        prompt = ""
        if self.ai_prompt_entry is not None:
            prompt = self.ai_prompt_entry.get().strip()
            self.ai_prompt_entry.delete(0, "end")
        if not prompt:
            prompt = "Beschreibe kurz, was auf meinem Bildschirm zu sehen ist."
        self._start_ai_request(prompt, image_data)

    def _capture_ai_avatar(self):
        if Image is None or ImageDraw is None:
            raise RuntimeError("Pillow wird für die Avatarbild-Erstellung benötigt.")

        avatar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cx = W // 2
        base = H - 5
        key = "neutral" if "neutral" in self.emotion_sources else None
        figure_height = 178 if key is None else 0
        if key is not None:
            image = self.art_base(key, SPRITE_H)[0]
            figure_height = image.height
            layer = Image.new("RGBA", (W, SPRITE_H + 40), (0, 0, 0, 0))
            layer.alpha_composite(
                image, ((W - image.width) // 2, layer.height - image.height)
            )
            avatar.alpha_composite(layer, (0, base - layer.height))
        else:
            draw = ImageDraw.Draw(avatar)
            scale = 1.0

            def point(x, y):
                return (round(cx + (x - cx) * scale),
                        round(base + (y - base) * scale))

            def rectangle(box, **kwargs):
                if kwargs.get("outline") == "":
                    kwargs["outline"] = None
                draw.rectangle((point(box[0], box[1]), point(box[2], box[3])), **kwargs)

            step = 0
            rectangle((cx - 22, base - 50, cx - 8, base - 5 + step),
                      fill=PANEL2, outline=ACCENT)
            rectangle((cx + 8, base - 50, cx + 22, base - 5 - step),
                      fill=PANEL2, outline=ACCENT)
            rectangle((cx - 32, base - 120, cx + 32, base - 50),
                      fill="#241012", outline=EDGE, width=2)
            draw.line((point(cx - 20, base - 105), point(cx + 20, base - 105)),
                      fill=ACCENT, width=2)
            rectangle((cx - 46, base - 118, cx - 32, base - 65),
                      fill=PANEL2, outline=ACCENT)
            rectangle((cx + 32, base - 118, cx + 46, base - 65),
                      fill=PANEL2, outline=ACCENT)
            rectangle((cx - 28, base - 175, cx + 28, base - 122),
                      fill="#2e1215", outline=ACCENT, width=2)
            glow = ACCENT
            draw.line((point(cx + 14, base - 175), point(cx + 20, base - 195)),
                      fill=ACCENT, width=2)
            x1, y1 = point(cx + 16, base - 201)
            x2, y2 = point(cx + 26, base - 191)
            draw.ellipse((x1, y1, x2, y2), fill=glow)
            eye_height = 12
            look = 0
            rectangle((cx - 22, base - 158, cx + 22, base - 138),
                      fill="#000000", outline=EDGE)
            for offset in (-16, 6):
                rectangle((cx + offset + look, base - 148 - eye_height // 2,
                           cx + offset + 10 + look, base - 148 + eye_height // 2),
                          fill=ACCENT, outline="")

        draw = ImageDraw.Draw(avatar)
        top = base - figure_height
        accessory_scale = 1.0

        def accessory_point(x, y):
            anchor_y = top + 8
            return (round(cx + (x - cx) * accessory_scale),
                    round(anchor_y + (y - anchor_y) * accessory_scale))

        def accessory_polygon(points, **kwargs):
            draw.polygon([accessory_point(x, y) for x, y in points], **kwargs)

        worn = self.s["worn"]
        if "halo" in worn:
            x1, y1 = accessory_point(cx - 26, top - 24)
            x2, y2 = accessory_point(cx + 26, top - 8)
            draw.ellipse((x1, y1, x2, y2), outline=LIGHT, width=3)
        if "cap" in worn:
            x1, y1 = accessory_point(cx - 26, top - 8)
            x2, y2 = accessory_point(cx + 26, top + 8)
            draw.rectangle((x1, y1, x2, y2), fill=PANEL2, outline=ACCENT, width=2)
            x1, y1 = accessory_point(cx + 10, top + 4)
            x2, y2 = accessory_point(cx + 42, top + 10)
            draw.rectangle((x1, y1, x2, y2), fill=ACCENT)
        if "crown" in worn:
            accessory_polygon(
                [(cx - 24, top + 8), (cx - 24, top - 14), (cx - 12, top - 2),
                 (cx, top - 20), (cx + 12, top - 2), (cx + 24, top - 14),
                 (cx + 24, top + 8)],
                fill="#c4122f", outline=ACCENT, width=2,
            )
        if "visor" in worn:
            accessory_polygon(
                [(cx - 30, top + 27), (cx + 30, top + 27), (cx + 24, top + 43),
                 (cx - 24, top + 43)],
                fill="#1a0206", outline=ACCENT, width=2,
            )
            draw.line((accessory_point(cx - 18, top + 31),
                       accessory_point(cx + 18, top + 31)), fill=LIGHT, width=2)
        if "scarf" in worn:
            accessory_polygon(
                [(cx - 28, top + 68), (cx + 28, top + 68), (cx + 21, top + 84),
                 (cx - 21, top + 84)],
                fill=EDGE, outline=ACCENT, width=2,
            )
            accessory_polygon(
                [(cx + 12, top + 80), (cx + 27, top + 78), (cx + 31, top + 111),
                 (cx + 18, top + 105)],
                fill="#c4122f", outline=EDGE, width=2,
            )
        if "wings" in worn:
            accessory_polygon(
                [(cx - 27, top + 79), (cx - 46, top + 57), (cx - 79, top + 62),
                 (cx - 59, top + 82), (cx - 76, top + 96), (cx - 39, top + 96)],
                fill="#1a0b0d", outline=ACCENT, width=2,
            )
            accessory_polygon(
                [(cx + 27, top + 79), (cx + 46, top + 57), (cx + 79, top + 62),
                 (cx + 59, top + 82), (cx + 76, top + 96), (cx + 39, top + 96)],
                fill="#1a0b0d", outline=EDGE, width=2,
            )
        if "headset" in worn:
            x1, y1 = accessory_point(cx - 36, top + 2)
            x2, y2 = accessory_point(cx + 36, top + 66)
            draw.arc((x1, y1, x2, y2), start=0, end=180, fill=ACCENT, width=4)
            for left in (True, False):
                coords = ((cx - 39, top + 27, cx - 27, top + 54) if left else
                          (cx + 27, top + 27, cx + 39, top + 54))
                x1, y1 = accessory_point(coords[0], coords[1])
                x2, y2 = accessory_point(coords[2], coords[3])
                draw.rectangle((x1, y1, x2, y2), fill=PANEL2, outline=EDGE, width=2)

        bounds = avatar.getchannel("A").getbbox()
        if bounds is None:
            raise ValueError("Der Avatar ist leer.")
        avatar = avatar.crop(bounds)
        background = Image.new("RGB", (avatar.width + 24, avatar.height + 24), PANEL)
        background.paste(avatar, (12, 12), avatar.getchannel("A"))
        background.thumbnail((512, 512), Image.LANCZOS)
        output = io.BytesIO()
        background.save(output, format="PNG")
        return output.getvalue()

    def _start_ai_request(self, prompt, image_data=None):
        if not self.ai_enabled or self.ai_busy or self.ai_voice_busy or not self._ai_is_ready():
            return False
        screen_image = image_data is not None
        parts = [{"text": prompt}]
        if not screen_image and re.search(
                r"\b(?:aussehen|aussehe|siehst|avatar|bild|farbe|farben|kleidung|"
                r"outfit|trägst|trage|tragen|beschreib\w*|geformt|appearance|"
                r"look like|wearing)\b",
                prompt, re.IGNORECASE):
            try:
                avatar_data = self._capture_ai_avatar()
            except (OSError, RuntimeError, ValueError, tk.TclError) as error:
                if self.ai_status is not None:
                    self.ai_status.configure(text=f"Avatar konnte nicht erstellt werden: {error}")
                if self.ai_prompt_entry is not None and not self.ai_prompt_entry.get():
                    self.ai_prompt_entry.insert(0, prompt)
                return False
            parts.append({
                "text": "Dieses Bild ist nur eine visuelle Referenz für mein neutrales Avatar. "
                        "Beschreibe es nicht ungefragt."
            })
            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": base64.b64encode(avatar_data).decode("ascii"),
                }
            })
        if screen_image:
            parts.append({"text": "Dieses Bild ist das vom Nutzer bestätigte Bildschirmfoto."})
            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": base64.b64encode(image_data).decode("ascii"),
                }
            })
        user_turn = {"role": "user", "parts": parts}
        if self.ai_provider == "ollama":
            history = sanitize_ai_memory(self.ai_history[-AI_MEMORY_MAX_TURNS:])
        else:
            history = [
                turn for turn in self.ai_history[-10:]
                if not any("inline_data" in part for part in turn.get("parts", []))
            ]
        history.append(user_turn)
        api_key = self.ai_api_key
        provider = self.ai_provider
        provider_name = self._ai_provider_name()
        session_id = self.ai_session_id
        self._append_ai_message("Du", "[Bildschirmbild gesendet]\n" + prompt
                                if screen_image else prompt)
        self.ai_busy = True
        self._set_ai_busy(True)
        if self.ai_status is not None:
            self.ai_status.configure(text=f"{provider_name} antwortet …")

        def request():
            try:
                answer = self._generate_ai_content(provider, api_key, history)
            except (GeminiAPIError, OpenAIAPIError, OllamaAPIError) as error:
                result = ("error", session_id, str(error), None)
            except Exception as error:
                result = ("error", session_id, f"Unerwarteter Fehler: {error}", None)
            else:
                result = ("success", session_id, answer, history)
            self.ai_results.put(result)

        threading.Thread(target=request, daemon=True, name="nova-ai").start()
        return True

    def _generate_ai_content(self, provider, api_key, history):
        if provider == "ollama":
            return generate_ollama_content(
                self.ai_model, history, system_prompt=self._ai_system_prompt(provider)
            )
        if provider == "openai":
            return generate_openai_content(
                api_key, history, system_prompt=self._ai_system_prompt(provider)
            )
        if provider == "openrouter":
            return generate_openai_content(
                api_key, history, api_url=OPENROUTER_API_URL,
                model=OPENROUTER_FREE_MODEL, service_name="OpenRouter",
                system_prompt=self._ai_system_prompt(provider),
            )
        return generate_content(
            api_key, history, system_prompt=self._ai_system_prompt(provider)
        )

    def _reset_ai_speech(self):
        self.ai_speech_session_id += 1
        self.ai_speech_lines = {
            context: [] for context in ("idle", "feed", "pet", "general")
        }
        self.ai_speech_pending = []
        self.ai_speech_busy = False
        self.ai_speech_retry_at = 0.0
        self.ai_speech_error = ""

    def _request_ai_speech_lines(self):
        if (self.ai_window is not None or not self.ai_enabled or not self._ai_is_ready() or
                self.ai_speech_busy or self.ai_busy or
                time.time() < self.ai_speech_retry_at):
            return
        self.ai_speech_busy = True
        session_id = self.ai_speech_session_id
        api_key = self.ai_api_key
        character_name = self._ai_character_name()
        prompt = (
            "Schreibe je 3 kurze, abwechslungsreiche, freundliche deutsche Sprechtexte "
            f"für {character_name}, ein kleines Desktop-Haustier. Gib ausschließlich genau "
            "12 Zeilen ohne Einleitung, Erklärung, Zusammenfassung oder Codeblock aus: "
            "je 3 mit dem Präfix idle|, feed|, pet| und general|. idle sind spontane "
            "Alltagssprüche. Jede feed-Zeile muss eindeutig davon handeln, dass du gerade "
            "gefüttert wurdest, und mindestens eines dieser Wörter enthalten: Futter, Essen, "
            "lecker, schmeckt, Happen, nom nom, mampf oder Biss. Jede pet-Zeile muss eindeutig "
            "vom Streicheln handeln und Streicheln, Kitzeln, Kraulen oder Kuscheln erwähnen. "
            "general sind freundliche kurze Reaktionen auf Knopfdrücke und andere Interaktionen, "
            "ohne ein bestimmtes Ergebnis vorauszusetzen. Pro Zeile nur ein Sprechtext, ohne Nummern "
            "oder Anführungszeichen. Keine Behauptungen über Bildschirm, Nutzer oder unbekannte "
            "Ereignisse. Nenne dich mit dem eingestellten Namen."
        )
        history = [{"role": "user", "parts": [{"text": prompt}]}]
        provider = self.ai_provider

        def request():
            try:
                result = self._generate_ai_content(provider, api_key, history)
            except (GeminiAPIError, OpenAIAPIError, OllamaAPIError) as error:
                self.ai_speech_results.put(("error", session_id, str(error)))
            except Exception as error:
                self.ai_speech_results.put(("error", session_id, f"Unerwarteter Fehler: {error}"))
            else:
                self.ai_speech_results.put(("success", session_id, result))

        threading.Thread(target=request, daemon=True, name="nova-ai-speech").start()

    def _uses_ai_speech(self):
        return self.ai_enabled and self._ai_is_ready()

    def _next_ai_speech(self, context):
        lines = self.ai_speech_lines.get(context, [])
        if not lines:
            self._request_ai_speech_lines()
            return None
        line = lines.pop(0)
        if len(lines) <= 1:
            self._request_ai_speech_lines()
        return line

    def _queue_ai_speech(self, context, seconds, speak=True, preserve_bubble=False):
        if len(self.ai_speech_pending) >= 8:
            self.ai_speech_pending.pop(0)
        self.ai_speech_pending.append((context, seconds, speak, preserve_bubble))

    def _display_ai_speech(self, text, seconds, speak=True, preserve_bubble=False):
        will_speak = speak and self.voice_enabled and not self.game_end and not self.ai_voice_busy
        now = time.time()
        if preserve_bubble and not will_speak:
            current = self.bubble_text.strip()
            self.bubble_text = self.personalize_text(
                f"{current}\n{text}" if current else text
            )
            self.bubble_until = max(self.bubble_until, now + seconds)
        elif not preserve_bubble:
            self.bubble_text = self.personalize_text(text)
            self.bubble_until = now + seconds
        if will_speak:
            self.speak_text(text)

    def _deliver_pending_ai_speech(self):
        if self.ai_window is not None:
            return
        pending, self.ai_speech_pending = self.ai_speech_pending, []
        for context, seconds, speak, preserve_bubble in pending:
            lines = self.ai_speech_lines.get(context, [])
            if not lines:
                self.ai_speech_pending.append((context, seconds, speak, preserve_bubble))
                continue
            self._display_ai_speech(lines.pop(0), seconds, speak, preserve_bubble)
            if len(lines) <= 1:
                self._request_ai_speech_lines()

    def _say_ai_radial_response(self):
        text = self._next_ai_speech("general")
        if text is None:
            self.ai_radial_action_spoke = True
            self._queue_ai_speech(
                "general", 4, preserve_bubble=self.ai_radial_action_has_message
            )
            return
        self.ai_radial_action_spoke = True
        self._display_ai_speech(
            text, 4, preserve_bubble=self.ai_radial_action_has_message
        )

    def process_ai_speech_results(self):
        while True:
            try:
                status, session_id, result = self.ai_speech_results.get_nowait()
            except queue.Empty:
                return
            if session_id != self.ai_speech_session_id:
                continue
            self.ai_speech_busy = False
            speech_ready = False
            all_contexts_ready = False
            if status == "success":
                lines_by_context = {context: [] for context in self.ai_speech_lines}
                for raw_line in result.splitlines():
                    raw_line = re.sub(r"^\s*(?:[-*•]\s*|\d+[.)]\s*)", "", raw_line).strip()
                    if not raw_line or raw_line.startswith("```"):
                        continue
                    context, separator, line = raw_line.partition("|")
                    if not separator:
                        match = re.match(
                            r"^(idle|feed|pet|general)\s*[:\-]\s*(.+)$",
                            raw_line, flags=re.IGNORECASE,
                        )
                        if match:
                            context, line = match.group(1), match.group(2)
                        else:
                            continue
                    context = context.strip().lower()
                    if context not in lines_by_context:
                        continue
                    line = line.strip().strip("\"'“”").strip()
                    terms = AI_SPEECH_CONTEXT_TERMS.get(context, ())
                    if terms and not any(term in line.casefold() for term in terms):
                        continue
                    if line and len(line) <= 140:
                        lines_by_context[context].append(line)
                for context, lines in lines_by_context.items():
                    self.ai_speech_lines[context].extend(lines[:3])
                speech_ready = any(lines_by_context.values())
                all_contexts_ready = all(lines_by_context.values())
                if not speech_ready:
                    self.ai_speech_retry_at = time.time() + 30
                    self.ai_speech_error = "Der Anbieter hat keine KI-Sprechtexte geliefert."
                elif not all_contexts_ready:
                    self.ai_speech_retry_at = time.time() + 30
                    self.ai_speech_error = ""
                else:
                    self.ai_speech_retry_at = 0.0
                    self.ai_speech_error = ""
                if speech_ready:
                    self._deliver_pending_ai_speech()
            else:
                self.ai_speech_retry_at = time.time() + 30
                self.ai_speech_error = "KI-Sprechtexte fehlgeschlagen: " + result
            if self.ai_status is not None:
                if all_contexts_ready:
                    status_text = "KI-Sprüche bereit."
                elif speech_ready:
                    status_text = "KI-Sprüche teilweise bereit."
                else:
                    status_text = "KI-Sprüche konnten nicht geladen werden."
                self.ai_status.configure(text=status_text)

    def _set_ai_busy(self, busy):
        state = "disabled" if busy or self.ai_voice_busy or self.ai_voice_continuous else "normal"
        for button in (self.ai_send_button, self.ai_voice_button, self.ai_screen_button):
            if button is not None:
                try:
                    button.configure(state=state)
                except tk.TclError:
                    pass
        if self.ai_clear_memory_button is not None:
            try:
                self.ai_clear_memory_button.configure(state=state)
            except tk.TclError:
                pass

    def process_ai_results(self):
        while True:
            try:
                status, session_id, result, history = self.ai_results.get_nowait()
            except queue.Empty:
                return
            if session_id != self.ai_session_id:
                continue
            self.ai_busy = False
            self._set_ai_busy(False)
            if status == "success":
                voice_reply, self.ai_voice_reply_pending = (
                    self.ai_voice_reply_pending or self.ai_voice_continuous, False
                )
                speech_sequence = None
                self.ai_history = history + [{"role": "model", "parts": [{"text": result}]}]
                self.ai_history = self.ai_history[-AI_MEMORY_MAX_TURNS:]
                self._append_ai_message(self._ai_character_name(), result)
                if voice_reply:
                    if self.ai_window is None:
                        self.say(result, 8, speak=False)
                    if not self.game_end:
                        speech_sequence = self.speak_text(result)
                elif self.voice_enabled and not self.game_end and not self.ai_voice_busy:
                    self.speak_text(result)
                if self.ai_status is not None:
                    self.ai_status.configure(text=f"Antwort von {self._ai_provider_name()}.")
                if self.ai_provider == "ollama":
                    self._save_local_ai_memory()
                if self.ai_voice_continuous:
                    if speech_sequence is not None:
                        self.ai_voice_waiting_for_sequence = speech_sequence
                    else:
                        self._send_next_ai_voice_prompt()
                    if len(self.ai_voice_pending_prompts) < AI_VOICE_QUEUE_MAX:
                        self._schedule_ai_voice_restart()
            else:
                voice_reply, self.ai_voice_reply_pending = (
                    self.ai_voice_reply_pending or self.ai_voice_continuous, False
                )
                self._append_ai_message("Fehler", result)
                if self.ai_status is not None:
                    self.ai_status.configure(text="Anfrage fehlgeschlagen.")
                elif voice_reply:
                    self.say(f"KI-Fehler: {result}", 8, speak=False)
                if self.ai_voice_continuous:
                    self._send_next_ai_voice_prompt()
                    if len(self.ai_voice_pending_prompts) < AI_VOICE_QUEUE_MAX:
                        self._schedule_ai_voice_restart()

    # ================= Sprachausgabe =================
    def toggle_synth_voice(self):
        self.synth_voice = not self.synth_voice
        self.s["synth_voice"] = self.synth_voice
        self.save()
        msg = ("Synthetischer Cyber-Stimmfilter aktiviert."
               if self.synth_voice else "Normale Sprachausgabe aktiviert.")
        self.say(msg, 4, speak=self.voice_enabled)

    def _apply_synth_prosody(self, text):
        """Formt Text für die TTS-Engine so um, dass er robotischer und stakkatoartiger klingt."""
        # Satzzeichen durch kürzere, abgehackte Pausen ersetzen
        t = re.sub(r"([.!?]+)\s+", r"... ", text)
        t = re.sub(r",\s+", " - ", t)
        # Technische Ausdrücke leicht betonen / zerlegen
        t = re.sub(r" (System|Status|Fehler|Warnung|Prozessor|Speicher|Online|Offline|Update) ",
                   r"\1 -", t, flags=re.IGNORECASE)
        words = t.split()
        if len(words) >= 5:
            # Gezielte Mini-Glitches / Stakkato-Silben bei längeren Wörtern einstreuen
            out = []
            for idx, w in enumerate(words):
                clean_w = re.sub(r"[^A-Za-zÄÖÜäöüß]", "", w)
                if len(clean_w) >= 8 and idx % 3 == 1:
                    mid = len(w) // 2
                    out.append(f"{w[:mid]}-{w[mid:]}")
                else:
                    out.append(w)
            t = " ".join(out)
        return t

    def tts_text(self, text):
        """Bereitet Text fürs Vorlesen auf und verkürzt Pausen zwischen Sätzen."""
        t = self.personalize_text(text).replace("…", "...")
        t = re.sub(r"[.!?]+(?=\s+[A-ZÄÖÜ])", ",", t)
        t = re.sub(r"[*·■□›‹×]", " ", t)
        t = re.sub(r"\s+", " ", t).strip()[:200]
        if self.synth_voice and t:
            t = self._apply_synth_prosody(t)[:220]
        return t

    def personalize_text(self, text):
        """Ersetzt den Standardnamen NOVA durch den gewählten Namen."""
        if not text.strip():
            return text
        name = self.s.get("name", "")
        if not isinstance(name, str) or not name.strip():
            return text
        name = name.strip()
        if name.casefold() == "nova":
            return text
        return re.sub(r"\bNOVA(?P<possessive>s)?\b",
                      lambda m: name + (m.group("possessive") or ""),
                      text, flags=re.IGNORECASE)

    def ensure_voice_process(self):
        """Startet bei Bedarf die lokale Windows-Stimme Microsoft Katja."""
        proc = self.voice_process
        if proc is not None and proc.poll() is None:
            return proc
        self.voice_process = None
        powershell = shutil.which("powershell.exe")
        if not powershell or not os.path.isfile(WINDOWS_VOICE_WORKER):
            self.voice_error_message = "Windows-Sprachsynthese oder der Sprach-Worker fehlt."
            return None
        self.voice_session_id += 1
        session_id = self.voice_session_id
        try:
            self.voice_process = subprocess.Popen(
                [powershell, "-NoLogo", "-NoProfile", "-NonInteractive",
                 "-ExecutionPolicy", "Bypass", "-File", WINDOWS_VOICE_WORKER,
                 WINDOWS_VOICE_TOKEN],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="ascii", errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except OSError as err:
            self.voice_error_message = str(err)
            return None
        proc = self.voice_process
        try:
            threading.Thread(
                target=self._read_voice_events, args=(session_id, proc),
                daemon=True, name="nova-voice-events",
            ).start()
        except RuntimeError as err:
            self.voice_error_message = f"Sprachereignisse konnten nicht überwacht werden: {err}"
            self.stop_voice()
            return None
        return self.voice_process

    def _read_voice_events(self, session_id, process):
        if process.stdout is None:
            return
        try:
            for line in iter(process.stdout.readline, ""):
                match = re.fullmatch(r"NOVA_DONE:(\d+)\s*", line)
                if match:
                    self.voice_events.put((session_id, process, int(match.group(1))))
        except (OSError, ValueError):
            pass

    def speak_text(self, text):
        """Übergibt Text an Katja; der Worker spricht Texte nacheinander."""
        if not IS_WIN:
            self.voice_error_message = "Die Sprachausgabe funktioniert nur unter Windows."
            return
        clean = self.tts_text(text)
        if not clean:
            return
        proc = self.ensure_voice_process()
        if proc is None:
            return
        self.voice_speech_sequence += 1
        sequence = self.voice_speech_sequence
        try:
            encoded = base64.b64encode(clean.encode("utf-8")).decode("ascii")
            proc.stdin.write(f"{sequence}:{encoded}\n")
            proc.stdin.flush()
        except (OSError, ValueError) as err:
            self.voice_error_message = str(err)
            self.stop_voice()
            return None
        return sequence

    def check_voice(self):
        """Erkennt einen beendeten Sprecher und meldet den Fehlertext."""
        proc = self.voice_process
        if proc is None or proc.poll() is None:
            return
        err = ""
        try:
            err = (proc.stderr.read() or "").strip()
        except (OSError, ValueError):
            pass
        self.voice_process = None
        if proc.returncode:
            self.voice_error_message = err[:200] or "Die lokale Sprachausgabe wurde beendet."
        if self.ai_voice_waiting_for_sequence is not None:
            self.ai_voice_waiting_for_sequence = None
            self._schedule_ai_voice_restart(300)

    def stop_voice(self, graceful=False):
        proc, self.voice_process = self.voice_process, None
        self.voice_session_id += 1
        waiting_for_speech = self.ai_voice_waiting_for_sequence is not None
        self.ai_voice_waiting_for_sequence = None
        if proc is None:
            if waiting_for_speech:
                self._schedule_ai_voice_restart(300)
            return
        try:
            proc.stdin.close()
        except (OSError, ValueError, AttributeError):
            pass
        if graceful:
            try:
                proc.wait(timeout=1.0)
                return
            except subprocess.TimeoutExpired:
                pass
        try:
            proc.terminate()
        except OSError:
            pass
        if waiting_for_speech:
            self._schedule_ai_voice_restart(300)

    def toggle_voice(self):
        if not IS_WIN:
            self.say("Die Sprachausgabe ist nur unter Windows verfügbar.", 4, speak=False)
            return
        self.voice_enabled = not self.voice_enabled
        self.s["voice_enabled"] = self.voice_enabled
        if self.voice_enabled:
            self.ensure_voice_process()        # vorwärmen, damit der erste Satz schnell kommt
            if self.ai_enabled:
                self._request_ai_speech_lines()
        else:
            self.stop_voice()
            self._reset_ai_speech()
        self.save()
        self.say("Sprachausgabe eingeschaltet." if self.voice_enabled
                 else "Sprachausgabe ausgeschaltet.", 4, speak=False)

    def test_voice(self):
        text = "Hallo. Ich bin NOVA. Alles funktioniert."
        self.say(text, 5, speak=False)
        self.speak_text(text)

    # ================= Aktionen =================
    def pet(self):
        """Streicheln: Spaß, Punkt, kurz fröhlich."""
        now = time.time()
        if self.sleeping:
            self.say("Zzz...", 2, speak=False)
            return
        if now - self.last_pet < 4:
            return
        self.last_pet = now
        self.s["fun"] = clamp(self.s["fun"] + 8)
        self.add_points(1)
        self.quest_event("pet")
        self.set_emotion_override("happy", 4)
        self.say(random.choice(PET_LINES), 3, ai_context="pet")

    def toggle_sleep(self):
        self.sleeping = not self.sleeping
        if self.sleeping:
            self.cancel_game()
        self.say("Gute Nacht... Zzz" if self.sleeping else "Ich bin wach!", 3)

    def show_status(self):
        self.hud_until = time.time() + 6

    def toggle_walk(self):
        self.walking = not self.walking
        self.s["walking"] = self.walking
        self.save()

    def show_highscores(self):
        best = self.s["highscores"]
        parts = [f"{GAME_LABELS[m]}: {int(best.get(m, 0))}" for m in GAME_LABELS]
        self.say("Rekorde – " + " · ".join(parts), 8, speak=False)

    # ================= Minispiele =================
    def game_blocked(self):
        if self.phone_mode:
            self.say("Im Telefonmodus bin ich zu klein zum Spielen.", 3, speak=False)
            return True
        if self.mini:
            self.say("Im Vollbild bin ich zu klein zum Spielen.", 3, speak=False)
            return True
        if self.sleeping:
            self.say("Ich schlafe gerade...", 3, speak=False)
            return True
        return False

    def cancel_game(self):
        was_jump = bool(self.game_end and self.game_mode == "jump")
        self.game_end = 0.0
        self.dots = []
        self.reflex_target = None
        if was_jump:
            self.returning = True

    def start_game(self):
        if self.game_blocked():
            return
        self.stop_voice()
        self.game_mode = "dots"
        self.game_end = time.time() + GAME_SECONDS
        self.dots = []
        self.reflex_target = None
        self.game_score = 0
        self.game_bonus = 0
        self.say("Fang die Datenpunkte!", 3, speak=False)

    def start_reflex_game(self):
        """Fünf Ziele nacheinander; schnelle Treffer (unter 0,6 s) geben Bonuspunkte."""
        if self.game_blocked():
            return
        self.stop_voice()
        now = time.time()
        self.game_mode = "reflex"
        self.game_end = now + 25
        self.dots = []
        self.game_score = 0
        self.game_bonus = 0
        self.reflex_round = 0
        self.reflex_times = []
        self.reflex_target = None
        self.reflex_next = now + random.uniform(0.7, 1.4)
        self.say("Reaktionstest: Klick die Ziele!", 3, speak=False)

    def start_jump_game(self):
        """NOVA hüpft über den Bildschirm; jeder Treffer macht sie schneller."""
        if self.game_blocked():
            return
        self.stop_voice()
        now = time.time()
        self.game_mode = "jump"
        self.game_end = now + 20
        self.dots = []
        self.reflex_target = None
        self.game_score = 0
        self.game_bonus = 0
        self.schedule_jump(now)
        self.say("Fang mich, wenn du kannst!", 3, speak=False)

    def schedule_jump(self, now):
        self.jump_from = (self.x, self.y)
        self.jump_to = (random.randint(0, max(0, self.sw - W)),
                        random.randint(0, max(0, self.sh - H)))
        self.jump_started = now
        self.jump_duration = max(0.3, random.uniform(0.45, 0.75) - 0.03 * self.game_score)
        self.jump_height = random.randint(25, 80)
        self.jump_next = now + self.jump_duration + random.uniform(0.15, 0.35)

    def finish_game(self, mode, score, points, fun_per_point, label, extra=""):
        """Gemeinsame Belohnung: Spaß, Punkte, Rekordbonus, Ergebnistext."""
        self.game_end = 0.0
        self.dots = []
        self.reflex_target = None
        self.s["fun"] = clamp(self.s["fun"] + min(30, score * fun_per_point))
        msg = f"{label}: {score}{extra}"
        best = int(self.s["highscores"].get(mode, 0))
        if score > best and score > 0:
            self.s["highscores"][mode] = int(score)
            points += 5
            msg += " – Neuer Rekord! +5"
        leveled = False
        if points:
            leveled = self.add_points(points, announce=False)
        if leveled:
            msg += f" · Level {self.level}!"
        if score > 0:
            self.quest_event("game")
        self.set_emotion_override("happy" if score > 0 else "bored", 4)
        self.say(msg, 7)
        if mode == "jump":
            self.returning = True

    def update_game(self, now):
        if not self.game_end:
            return
        if self.game_mode in STATIC_GAMES:
            getattr(self, "update_" + self.game_mode)(now)
            return
        if self.game_mode == "jump":
            if now >= self.game_end:
                score = self.game_score
                self.finish_game("jump", score, score, 3, "Erwischt", " Mal")
                return
            if self.radial_window is not None:
                return
            if now >= self.jump_next:
                self.schedule_jump(now)
            if self.jump_from is not None and self.jump_to is not None:
                progress = clamp((now - self.jump_started) / self.jump_duration)
                eased = 1 - (1 - progress) ** 3
                self.x = self.jump_from[0] + (self.jump_to[0] - self.jump_from[0]) * eased
                self.y = (self.jump_from[1] + (self.jump_to[1] - self.jump_from[1]) * eased
                          - math.sin(math.pi * progress) * self.jump_height)
            return
        if self.game_mode == "reflex":
            if now >= self.game_end or self.reflex_round >= 5:
                hits = self.game_score
                times = self.reflex_times
                extra = f" · Ø {sum(times) / len(times):.2f} s" if times else ""
                self.finish_game("reflex", hits + self.game_bonus, hits + self.game_bonus, 4,
                                 f"Reaktionstest {hits}/5", extra)
                return
            if self.reflex_target and self.reflex_target["until"] <= now:
                self.reflex_target = None
                self.reflex_round += 1
                self.reflex_next = now + random.uniform(0.45, 1.1)
            if self.reflex_target is None and self.reflex_round < 5 and now >= self.reflex_next:
                self.reflex_target = {
                    "x": random.randint(38, W - 38),
                    "y": random.randint(HUD_H + 60, H - 40),
                    "r": 19, "born": now, "until": now + REFLEX_LIFETIME,
                }
            return
        self.dots = [d for d in self.dots if d["until"] > now]
        if now >= self.game_end:
            score = self.game_score
            self.finish_game("dots", score, score, 3, "Runde vorbei", " Punkte")
            return
        if random.random() < 0.05 and len(self.dots) < 4:
            self.dots.append({"x": random.randint(24, W - 24),
                              "y": random.randint(HUD_H + 50, H - 30),
                              "until": now + DOT_LIFETIME})

    # ================= Neue Minispiele: Pong, Ausweichen, Merken =================
    def pointer_in_window(self):
        """Mausposition relativ zum NOVA-Fenster (oder None)."""
        try:
            px, py = self.root.winfo_pointerxy()
        except tk.TclError:
            return None
        return px - int(self.x), py - int(self.y)

    def start_static_game(self, mode, seconds):
        self.stop_voice()
        now = time.time()
        self.game_mode = mode
        self.game_end = now + seconds
        self.dots = []
        self.reflex_target = None
        self.game_score = 0
        self.game_bonus = 0
        return now

    # ---------- Pong ----------
    def start_pong_game(self):
        """Du gegen NOVA: Schläger folgt der Maus, wer zuerst 5 Punkte hat gewinnt."""
        if self.game_blocked():
            return
        now = self.start_static_game("pong", 90)
        mid = (FX1 + FX2) / 2
        self.pong = {"pad": mid, "ai": mid, "ai_off": 0.0, "pl": 0, "ai_score": 0,
                     "returns": 0, "speed": PONG_START_SPEED, "serve_at": now + 1.2,
                     "dir": 1, "last": now, "bx": mid, "by": (FY1 + FY2) / 2,
                     "vx": 0.0, "vy": 0.0}
        self.say("Pong! Bewege die Maus – wer zuerst 5 hat.", 3, speak=False)

    def pong_serve(self, direction):
        p = self.pong
        angle = random.uniform(-0.5, 0.5)
        p["speed"] = PONG_START_SPEED
        p["vx"] = p["speed"] * math.sin(angle)
        p["vy"] = direction * p["speed"] * math.cos(angle)

    def pong_goal(self, now, player_scored):
        p = self.pong
        if player_scored:
            p["pl"] += 1
        else:
            p["ai_score"] += 1
        p["bx"], p["by"] = (FX1 + FX2) / 2, (FY1 + FY2) / 2
        p["vx"] = p["vy"] = 0.0
        p["dir"] = -1 if player_scored else 1          # der Verlierer bekommt den Aufschlag
        p["serve_at"] = now + 0.9

    def pong_bounce(self, offset, direction, speed):
        """Neuer Ballwinkel je nach Trefferstelle am Schläger."""
        p = self.pong
        offset = clamp(offset, -1.0, 1.0)
        p["vx"] = offset * speed * 0.8
        p["vy"] = direction * math.sqrt(max(speed * speed - p["vx"] ** 2, 100.0))

    def update_pong(self, now):
        p = self.pong
        dt = clamp(now - p["last"], 0.0, 0.05)
        p["last"] = now
        half = PONG_PADDLE_W / 2
        pointer = self.pointer_in_window()
        if pointer is not None:
            p["pad"] = clamp(pointer[0], FX1 + half, FX2 - half)
        if now >= self.game_end or p["pl"] >= PONG_WIN or p["ai_score"] >= PONG_WIN:
            pl, ai = p["pl"], p["ai_score"]
            won = pl > ai
            score = p["returns"] + 5 * pl
            extra = f" ({pl}:{ai}){' – Gewonnen!' if won else ''}"
            self.finish_game("pong", score, score // 2 + (5 if won else 0), 1, "Pong", extra)
            return
        ai_speed = min(160.0, 95.0 + 7.0 * p["returns"])
        if p["vy"] == 0.0:
            if now >= p["serve_at"]:
                self.pong_serve(p["dir"])
            target = (FX1 + FX2) / 2
        else:
            target = p["bx"] + p["ai_off"] if p["vy"] < 0 else (FX1 + FX2) / 2
        step = clamp(target - p["ai"], -ai_speed * dt, ai_speed * dt)
        p["ai"] = clamp(p["ai"] + step, FX1 + half, FX2 - half)
        if p["vy"] == 0.0:
            return
        r = PONG_BALL_R
        p["bx"] += p["vx"] * dt
        p["by"] += p["vy"] * dt
        if p["bx"] < FX1 + r:
            p["bx"], p["vx"] = FX1 + r, abs(p["vx"])
        elif p["bx"] > FX2 - r:
            p["bx"], p["vx"] = FX2 - r, -abs(p["vx"])
        speed = math.hypot(p["vx"], p["vy"])
        if (p["vy"] > 0 and p["by"] + r >= PONG_PLAYER_Y - 3 and p["by"] - r <= PONG_PLAYER_Y + 3
                and abs(p["bx"] - p["pad"]) <= half + r):
            p["returns"] += 1
            p["speed"] = min(PONG_MAX_SPEED, max(speed, p["speed"]) * 1.06)
            self.pong_bounce((p["bx"] - p["pad"]) / half, -1, p["speed"])
            p["by"] = PONG_PLAYER_Y - 3 - r
            p["ai_off"] = random.uniform(-16, 16)
        elif (p["vy"] < 0 and p["by"] - r <= PONG_AI_Y + 3 and p["by"] + r >= PONG_AI_Y - 3
                and abs(p["bx"] - p["ai"]) <= half + r):
            self.pong_bounce((p["bx"] - p["ai"]) / half, 1, speed)
            p["by"] = PONG_AI_Y + 3 + r
        elif p["by"] > FY2:
            self.pong_goal(now, player_scored=False)
        elif p["by"] < FY1:
            self.pong_goal(now, player_scored=True)

    def draw_pong(self, now, left):
        c, p = self.canvas, self.pong
        half = PONG_PADDLE_W / 2
        mid_y = (FY1 + FY2) / 2
        c.create_rectangle(FX1, FY1, FX2, FY2, fill=PANEL, outline=ACCENT, width=2)
        c.create_line(FX1 + 4, mid_y, FX2 - 4, mid_y, fill=EDGE, dash=(4, 4))
        c.create_text(FX1 + 16, mid_y - 18, text=str(p["ai_score"]), fill=EDGE,
                      font=("Consolas", 16, "bold"))
        c.create_text(FX1 + 16, mid_y + 18, text=str(p["pl"]), fill=EDGE,
                      font=("Consolas", 16, "bold"))
        c.create_rectangle(p["ai"] - half, PONG_AI_Y - 3, p["ai"] + half, PONG_AI_Y + 3,
                           fill=LIGHT, outline="")
        c.create_rectangle(p["pad"] - half, PONG_PLAYER_Y - 3, p["pad"] + half, PONG_PLAYER_Y + 3,
                           fill=ACCENT, outline="")
        r = PONG_BALL_R
        c.create_oval(p["bx"] - r, p["by"] - r, p["bx"] + r, p["by"] + r, fill=LIGHT, outline="")
        if p["vy"] == 0.0:
            c.create_text(W // 2, mid_y + 44, text="Bereit …", fill=LIGHT,
                          font=("Consolas", 9, "bold"))
        return f"Pong {p['pl']}:{p['ai_score']} · {left}s"

    # ---------- Ausweichen ----------
    def start_dodge_game(self):
        """Daten fangen, orange Glitches meiden; drei Leben, 30 Sekunden."""
        if self.game_blocked():
            return
        now = self.start_static_game("dodge", 30)
        self.dodge = {"x": (FX1 + FX2) / 2, "lives": 3, "items": [], "next": now + 0.6,
                      "last": now, "start": now, "hit_until": 0.0}
        self.say("Fang die Daten, meide die Glitches!", 3, speak=False)

    def update_dodge(self, now):
        d = self.dodge
        dt = clamp(now - d["last"], 0.0, 0.05)
        d["last"] = now
        pointer = self.pointer_in_window()
        if pointer is not None:
            d["x"] = clamp(pointer[0], FX1 + 17, FX2 - 17)
        if now >= self.game_end or d["lives"] <= 0:
            score = self.game_score
            self.finish_game("dodge", score, score, 2, "Ausweichen", " Daten")
            return
        elapsed = now - d["start"]
        if now >= d["next"]:
            data = random.random() < 0.6
            d["items"].append({"x": random.randint(FX1 + 12, FX2 - 12), "y": FY1 + 4,
                               "vy": random.uniform(110, 160) + elapsed * 4,
                               "data": data, "r": 8 if data else 10})
            d["next"] = now + max(0.22, 0.55 - elapsed * 0.01)
        py = PONG_PLAYER_Y
        kept = []
        for it in d["items"]:
            it["y"] += it["vy"] * dt
            if abs(it["x"] - d["x"]) <= 17 + it["r"] and abs(it["y"] - py) <= 6 + it["r"]:
                if it["data"]:
                    self.game_score += 1
                else:
                    d["lives"] -= 1
                    d["hit_until"] = now + 0.4
                continue
            if it["y"] < FY2 + 20:
                kept.append(it)
        d["items"] = kept

    def draw_dodge(self, now, left):
        c, d = self.canvas, self.dodge
        c.create_rectangle(FX1, FY1, FX2, FY2, fill=PANEL, outline=ACCENT, width=2)
        for it in d["items"]:
            x, y, r = it["x"], it["y"], it["r"]
            if it["data"]:
                c.create_oval(x - r, y - r, x + r, y + r, fill=PANEL, outline=ACCENT, width=3)
                c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=LIGHT, outline="")
            else:
                c.create_polygon(x, y - r, x + r, y, x, y + r, x - r, y,
                                 fill="#ff7a2f", outline=LIGHT, width=2)
        flash = now < d["hit_until"] and int(now * 20) % 2 == 0
        c.create_rectangle(d["x"] - 17, PONG_PLAYER_Y - 6, d["x"] + 17, PONG_PLAYER_Y + 6,
                           fill=ACCENT if flash else LIGHT, outline=EDGE, width=2)
        c.create_text(FX1 + 8, FY1 + 12, text="♥" * max(0, d["lives"]), anchor="w",
                      fill=ACCENT, font=("Consolas", 10, "bold"))
        return f"Ausweichen {self.game_score} ♥{d['lives']} · {left}s"

    # ---------- Merken ----------
    def memory_pad_rects(self):
        size, gap = 90, 8
        x0 = (W - 2 * size - gap) // 2
        y0 = FY1 + 70
        return [(x0 + (i % 2) * (size + gap), y0 + (i // 2) * (size + gap),
                 x0 + (i % 2) * (size + gap) + size, y0 + (i // 2) * (size + gap) + size)
                for i in range(4)]

    def start_memory_game(self):
        """Folge von Feldern merken und nachklicken; jede Runde wird sie länger."""
        if self.game_blocked():
            return
        now = self.start_static_game("memory", 240)
        self.memory = {"seq": [random.randrange(4)], "phase": "between", "until": now + 1.0,
                       "show_i": 0, "lit": None, "input_i": 0, "deadline": 0.0, "flash": None}
        self.say("Merk dir die Folge und klick sie nach!", 3, speak=False)

    def end_memory(self):
        rounds = self.game_score
        self.finish_game("memory", rounds, rounds * 2, 3, "Merken", " Runden")

    def update_memory(self, now):
        m = self.memory
        if now >= self.game_end:
            self.end_memory()
            return
        phase = m["phase"]
        if phase == "between":
            if now >= m["until"]:
                m.update(phase="show", show_i=0, lit=None, until=now + 0.2)
        elif phase == "show":
            if now >= m["until"]:
                if m["lit"] is None:
                    if m["show_i"] >= len(m["seq"]):
                        m.update(phase="input", input_i=0, deadline=now + 6.0)
                    else:
                        m["lit"] = m["seq"][m["show_i"]]
                        m["until"] = now + max(0.25, 0.55 - 0.02 * len(m["seq"]))
                else:
                    m["lit"] = None
                    m["show_i"] += 1
                    m["until"] = now + 0.2
        elif now > m["deadline"]:
            self.end_memory()

    def hit_memory(self, x, y, now=None):
        m = self.memory
        if m is None or m["phase"] != "input":
            return
        now = time.time() if now is None else now
        for index, (x1, y1, x2, y2) in enumerate(self.memory_pad_rects()):
            if x1 <= x <= x2 and y1 <= y <= y2:
                m["flash"] = (index, now + 0.2)
                if index != m["seq"][m["input_i"]]:
                    self.end_memory()
                    return
                m["input_i"] += 1
                m["deadline"] = now + 6.0
                if m["input_i"] >= len(m["seq"]):
                    self.game_score += 1
                    if len(m["seq"]) >= 25:
                        self.end_memory()
                        return
                    m["seq"].append(random.randrange(4))
                    m.update(phase="between", until=now + 0.9, show_i=0, lit=None)
                return

    def draw_memory(self, now, left):
        c, m = self.canvas, self.memory
        c.create_rectangle(FX1, FY1, FX2, FY2, fill=PANEL, outline=ACCENT, width=2)
        if m["phase"] == "input":
            status = f"Du bist dran: {m['input_i']}/{len(m['seq'])}"
        else:
            status = "Merk dir die Folge …"
        c.create_text(W // 2, FY1 + 30, text=status, fill=LIGHT, font=("Consolas", 9, "bold"))
        flash = m["flash"]
        for index, (x1, y1, x2, y2) in enumerate(self.memory_pad_rects()):
            lit = (m["phase"] == "show" and m["lit"] == index) or (
                flash is not None and flash[0] == index and now < flash[1])
            color = MEMORY_COLORS[index]
            c.create_rectangle(x1, y1, x2, y2, fill=color if lit else PANEL2,
                               outline=color, width=3)
            c.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=MEMORY_SYMBOLS[index],
                          fill=PANEL if lit else color, font=("Segoe UI Symbol", 26, "bold"))
        return f"Merken: Runde {self.game_score + 1}"

    # ================= Daten-Farm (Idle-Spiel) =================
    def idle_owned(self, gid):
        return int(self.s["idle"]["gens"].get(gid, 0))

    def idle_multiplier(self):
        """Gesamtfaktor aus Chips und Multiplikator-Upgrades."""
        st = self.s["idle"]
        factor = 1.0 + IDLE_CHIP_BONUS * st["chips"]
        for uid, _, _, _, kind, value in IDLE_UPGRADES:
            if kind == "mult" and uid in st["upgrades"]:
                factor *= value
        return factor

    def idle_rate(self):
        raw = sum(self.idle_owned(gid) * rate for gid, _, _, rate in IDLE_GENS)
        return raw * self.idle_multiplier()

    def idle_click_value(self):
        st = self.s["idle"]
        factor = 1.0
        for uid, _, _, _, kind, value in IDLE_UPGRADES:
            if kind == "click" and uid in st["upgrades"]:
                factor *= value
        return (1.0 + 0.03 * self.idle_rate()) * factor * (1.0 + IDLE_CHIP_BONUS * st["chips"])

    def idle_add(self, amount):
        st = self.s["idle"]
        if amount <= 0 or not math.isfinite(amount):
            return
        st["bits"] = min(IDLE_BITS_CAP, st["bits"] + amount)
        st["total"] = min(IDLE_BITS_CAP, st["total"] + amount)
        st["run"] = min(IDLE_BITS_CAP, st["run"] + amount)

    def update_idle(self, now):
        """Läuft immer im Hintergrund. Große Zeitsprünge (Ruhezustand) zählen wie Offline-Zeit."""
        delta = now - self.idle_last
        self.idle_last = now
        if delta <= 0:
            return
        rate = self.idle_rate()
        if rate <= 0:
            return
        if delta > 60:
            gain = rate * min(delta, IDLE_OFFLINE_MAX) * IDLE_OFFLINE_FACTOR
            self.idle_add(gain)
            self.idle_status = f"Ruhezustand ({fmt_duration(delta)}): +{fmt_num(gain)} Bits"
        else:
            self.idle_add(rate * delta)

    def apply_idle_offline(self):
        away, rate = self.idle_away, self.idle_rate()
        if away < 120 or rate <= 0:
            return
        gain = rate * min(away, IDLE_OFFLINE_MAX) * IDLE_OFFLINE_FACTOR
        self.idle_add(gain)
        self.idle_status = f"Während du weg warst ({fmt_duration(away)}): +{fmt_num(gain)} Bits"
        self.root.after(5000, lambda: self.say(self.idle_status, 7, speak=False))

    def idle_generator_cost(self, gid, owned, count):
        base = next(g[2] for g in IDLE_GENS if g[0] == gid)
        first = base * IDLE_GROWTH ** owned
        return first * (IDLE_GROWTH ** count - 1) / (IDLE_GROWTH - 1)

    def idle_buy_plan(self, gid):
        """Wie viele Stück die gewählte Kaufmenge ergibt und was sie kosten: (Anzahl, Preis)."""
        owned = self.idle_owned(gid)
        room = IDLE_MAX_OWNED - owned
        if room <= 0:
            return 0, 0.0
        if self.idle_amount == "max":
            base = next(g[2] for g in IDLE_GENS if g[0] == gid)
            first = base * IDLE_GROWTH ** owned
            bits = self.s["idle"]["bits"]
            count = int(math.log(bits * (IDLE_GROWTH - 1) / first + 1) / math.log(IDLE_GROWTH))
            count = max(0, min(count, room))
            return count, self.idle_generator_cost(gid, owned, max(1, count))
        count = min(int(self.idle_amount), room)
        return count, self.idle_generator_cost(gid, owned, count)

    def idle_buy_generator(self, gid):
        count, cost = self.idle_buy_plan(gid)
        st = self.s["idle"]
        if count < 1 or st["bits"] < cost:
            return
        st["bits"] -= cost
        st["gens"][gid] = self.idle_owned(gid) + count
        self.refresh_idle_window(reschedule=False)

    def idle_buy_upgrade(self, uid):
        st = self.s["idle"]
        upgrade = next((u for u in IDLE_UPGRADES if u[0] == uid), None)
        if upgrade is None or uid in st["upgrades"] or st["bits"] < upgrade[3]:
            return
        st["bits"] -= upgrade[3]
        st["upgrades"].append(uid)
        self.refresh_idle_window(reschedule=False)

    def idle_click(self):
        st = self.s["idle"]
        self.idle_add(self.idle_click_value())
        st["clicks"] += 1
        self.refresh_idle_window(reschedule=False)

    def idle_reboot_gain(self):
        run = self.s["idle"]["run"]
        return int(math.sqrt(run / IDLE_REBOOT_MIN)) if run >= IDLE_REBOOT_MIN else 0

    def idle_reboot(self):
        gain = self.idle_reboot_gain()
        if gain < 1:
            return
        if not messagebox.askyesno(
                "Reboot",
                f"Alles zurücksetzen und {gain} Chips (+{int(gain * IDLE_CHIP_BONUS * 100)} % "
                f"Produktion) sowie {gain * 3} Punkte für NOVA erhalten?",
                parent=self.idle_window):
            return
        st = self.s["idle"]
        st.update(bits=0.0, run=0.0, gens={g[0]: 0 for g in IDLE_GENS}, upgrades=[])
        st["chips"] += gain
        st["reboots"] += 1
        self.add_points(gain * 3, announce=False)
        self.idle_status = f"Reboot! +{gain} Chips, +{gain * 3} Punkte."
        self.save()
        self.say(f"Reboot abgeschlossen: +{gain} Chips!", 5, speak=False)
        self.refresh_idle_window(reschedule=False)

    def set_idle_amount(self, amount):
        self.idle_amount = amount
        self.refresh_idle_window(reschedule=False)

    def open_idle_window(self):
        if self.idle_window is not None:
            try:
                if self.idle_window.winfo_exists():
                    self.idle_window.deiconify()
                    self.idle_window.lift()
                    return
            except tk.TclError:
                pass
        win = NovaToplevel(self.root)
        win.title("NOVA – Daten-Farm")
        win.configure(bg=PANEL)
        win.geometry("900x600")
        win.minsize(820, 560)
        win.protocol("WM_DELETE_WINDOW", self.close_idle_window)
        self.idle_window = win
        ui = {"gens": {}, "ups": {}, "buy": {}}
        self.idle_ui = ui

        tk.Label(win, text="NOVA · DATEN-FARM", bg=PANEL, fg=ACCENT,
                 font=("Consolas", 16, "bold")).pack(pady=(10, 0))
        tk.Label(win, text="Läuft im Hintergrund weiter, solange NOVA läuft. "
                           "Offline gibt es 50 % für bis zu 12 Stunden.",
                 bg=PANEL, fg=DIM, font=("Consolas", 8)).pack(pady=(0, 6))
        ui["bits"] = tk.Label(win, bg=PANEL, fg=LIGHT, font=("Consolas", 22, "bold"))
        ui["bits"].pack()
        ui["rate"] = tk.Label(win, bg=PANEL, fg=ACCENT, font=("Consolas", 10, "bold"))
        ui["rate"].pack(pady=(0, 8))

        body = tk.Frame(win, bg=PANEL)
        body.pack(fill="both", expand=True, padx=12)
        left = tk.Frame(body, bg=PANEL)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(body, bg=PANEL)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        ui["click"] = tk.Button(left, command=self.idle_click, bg=ACCENT, fg=PANEL,
                                activebackground=LIGHT, activeforeground=PANEL, relief="flat",
                                font=("Consolas", 13, "bold"), pady=8)
        ui["click"].pack(fill="x", pady=(0, 8))
        amount_row = tk.Frame(left, bg=PANEL)
        amount_row.pack(fill="x", pady=(0, 6))
        tk.Label(amount_row, text="Kaufmenge:", bg=PANEL, fg=LIGHT,
                 font=("Consolas", 9)).pack(side="left")
        for amount, label in ((1, "x1"), (10, "x10"), ("max", "Max")):
            button = tk.Button(amount_row, text=label, relief="flat", width=5,
                               font=("Consolas", 9, "bold"),
                               command=lambda a=amount: self.set_idle_amount(a))
            button.pack(side="left", padx=3)
            ui["buy"][amount] = button
        for gid, _, _, _ in IDLE_GENS:
            row = tk.Frame(left, bg=PANEL2, highlightthickness=1, highlightbackground=EDGE)
            row.pack(fill="x", pady=2)
            info = tk.Label(row, bg=PANEL2, fg=LIGHT, font=("Consolas", 9, "bold"),
                            anchor="w", justify="left", width=30)
            info.pack(side="left", padx=6, pady=3)
            button = tk.Button(row, relief="flat", font=("Consolas", 9, "bold"), width=22,
                               command=lambda g=gid: self.idle_buy_generator(g))
            button.pack(side="right", padx=4, pady=3)
            ui["gens"][gid] = (info, button)

        tk.Label(right, text="UPGRADES", bg=PANEL, fg=ACCENT,
                 font=("Consolas", 10, "bold")).pack(anchor="w")
        for uid, _, _, _, _, _ in IDLE_UPGRADES:
            button = tk.Button(right, relief="flat", font=("Consolas", 9, "bold"), anchor="w",
                               command=lambda u=uid: self.idle_buy_upgrade(u))
            button.pack(fill="x", pady=2)
            ui["ups"][uid] = button
        tk.Label(right, text="REBOOT", bg=PANEL, fg=ACCENT,
                 font=("Consolas", 10, "bold")).pack(anchor="w", pady=(10, 0))
        ui["reboot_info"] = tk.Label(right, bg=PANEL, fg=LIGHT, font=("Consolas", 9),
                                     anchor="w", justify="left", wraplength=380)
        ui["reboot_info"].pack(fill="x")
        ui["reboot"] = tk.Button(right, text="Reboot ausführen", command=self.idle_reboot,
                                 relief="flat", font=("Consolas", 9, "bold"))
        ui["reboot"].pack(fill="x", pady=(4, 0))
        ui["stats"] = tk.Label(right, bg=PANEL, fg=DIM, font=("Consolas", 8),
                               anchor="w", justify="left")
        ui["stats"].pack(fill="x", pady=(10, 0))
        ui["status"] = tk.Label(win, bg=PANEL, fg=LIGHT, font=("Consolas", 9), anchor="w")
        ui["status"].pack(fill="x", padx=14, pady=(4, 8))
        self.refresh_idle_window()

    def close_idle_window(self):
        if self.idle_after_id is not None and self.idle_window is not None:
            try:
                self.idle_window.after_cancel(self.idle_after_id)
            except tk.TclError:
                pass
        self.idle_after_id = None
        win, self.idle_window = self.idle_window, None
        self.idle_ui = {}
        if win is not None:
            try:
                win.destroy()
            except tk.TclError:
                pass
        self.save()

    def refresh_idle_window(self, reschedule=True):
        win, ui = self.idle_window, self.idle_ui
        if win is None or not ui:
            return
        try:
            if reschedule and self.idle_after_id is not None:
                win.after_cancel(self.idle_after_id)
                self.idle_after_id = None
            st = self.s["idle"]
            bits, rate = st["bits"], self.idle_rate()
            ui["bits"].config(text=f"{fmt_num(bits)} Bits")
            ui["rate"].config(text=f"{fmt_num(rate)} Bits/s · Faktor x{self.idle_multiplier():.2f}")
            ui["click"].config(text=f"⚡ HACKEN  (+{fmt_num(self.idle_click_value())})")
            for amount, button in ui["buy"].items():
                selected = amount == self.idle_amount
                button.config(bg=ACCENT if selected else PANEL2, fg=PANEL if selected else LIGHT)
            multiplier = self.idle_multiplier()
            for gid, name, _, per_second in IDLE_GENS:
                info, button = ui["gens"][gid]
                info.config(text=f"{name} x{self.idle_owned(gid)}  (+{fmt_num(per_second * multiplier)}/s)")
                count, cost = self.idle_buy_plan(gid)
                if count < 1 and self.idle_owned(gid) >= IDLE_MAX_OWNED:
                    button.config(text="Maximum erreicht", state="disabled", bg=PANEL2, fg=DIM)
                    continue
                affordable = count >= 1 and bits >= cost
                button.config(text=f"Kaufen x{max(1, count)} · {fmt_num(cost)}",
                              state="normal" if affordable else "disabled",
                              bg=EDGE if affordable else PANEL2, fg=LIGHT if affordable else DIM)
            for uid, name, desc, cost, _, _ in IDLE_UPGRADES:
                button = ui["ups"][uid]
                if uid in st["upgrades"]:
                    button.config(text=f"✔ {name} – {desc}", state="disabled", bg=PANEL2, fg=DIM)
                else:
                    affordable = bits >= cost
                    button.config(text=f"{name} – {desc} · {fmt_num(cost)}",
                                  state="normal" if affordable else "disabled",
                                  bg=EDGE if affordable else PANEL2, fg=LIGHT if affordable else DIM)
            gain = self.idle_reboot_gain()
            if gain >= 1:
                ui["reboot_info"].config(
                    text=f"Reboot jetzt: +{gain} Chips (+{int(gain * IDLE_CHIP_BONUS * 100)} % "
                         f"Produktion) und +{gain * 3} Punkte für NOVA. Setzt Bits, Generatoren "
                         "und Upgrades zurück.")
                ui["reboot"].config(state="normal", bg=ACCENT, fg=PANEL)
            else:
                ui["reboot_info"].config(
                    text=f"Ab {fmt_num(IDLE_REBOOT_MIN)} Bits in einem Durchlauf "
                         f"({fmt_num(st['run'])} bisher) gibt es Chips für dauerhaften Bonus.")
                ui["reboot"].config(state="disabled", bg=PANEL2, fg=DIM)
            ui["stats"].config(
                text=f"Chips: {st['chips']} (+{int(st['chips'] * IDLE_CHIP_BONUS * 100)} %) · "
                     f"Reboots: {st['reboots']} · Klicks: {st['clicks']}\n"
                     f"Gesamt verdient: {fmt_num(st['total'])} Bits")
            ui["status"].config(text=self.idle_status)
            if reschedule:
                self.idle_after_id = win.after(250, self.refresh_idle_window)
        except tk.TclError:
            self.idle_after_id = None

    # ================= Werkzeuge: gemeinsames Eingabefeld =================
    def start_prompt(self, kind):
        self.abort_input()
        self.prompt = kind
        self.feed_deadline = time.time() + 90
        self.entry.delete(0, "end")
        self.entry.place(x=20, y=HUD_H + 2, width=W - 40, height=22)
        if kind == "timer":
            hint = "Dauer + Enter (z. B. 25, 1h30, 90s). Esc = Abbruch."
        elif kind == "browse":
            hint = "Suchbegriff oder URL + Enter. Esc = Abbruch."
        else:
            hint = "'14:30 Text', '20m Text' oder 'täglich 8:00 Text' + Enter. Esc = Abbruch."
        self.say(hint, 90, speak=False)
        self.grab_focus()

    def finish_prompt(self, text):
        kind = self.prompt
        self.abort_input()
        if kind == "timer":
            seconds = parse_duration(text)
            if seconds is None:
                self.say("Das habe ich nicht verstanden. Beispiel: 25, 1h30 oder 90s.", 5, speak=False)
                return
            self.start_timer(seconds)
        elif kind == "browse":
            self.browse(text)
        elif kind == "reminder":
            parsed = parse_reminder(text)
            if parsed is None:
                self.say("Nicht verstanden. Beispiele: 14:30 Anruf · 20m Pause · täglich 8:00 Tabletten",
                         7, speak=False)
                return
            self.add_reminder(*parsed)

    def browse(self, text):
        """URL öffnen oder im Standardbrowser suchen (nur http/https)."""
        text = text.strip()
        if not text:
            return
        import urllib.parse
        looks_url = (" " not in text and ("." in text or text.lower().startswith("localhost"))
                     or re.match(r"^https?://\S+$", text, re.I))
        if looks_url:
            url = text if re.match(r"^[a-z][a-z0-9+.-]*://", text, re.I) else "https://" + text
            if urllib.parse.urlparse(url).scheme.lower() not in ("http", "https"):
                self.say("Nur http- und https-Adressen.", 4, speak=False)
                return
            note = "Öffne Seite…"
        else:
            url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(text)
            note = f"Suche: {text[:40]}"
        try:
            webbrowser.open(url)
        except webbrowser.Error as err:
            self.say(f"Browser nicht gestartet: {err}", 5, speak=False)
            return
        self.say(note, 3, speak=False)

    # ================= Werkzeuge: Alarm =================
    def trigger_alarm(self, title, text):
        now = time.time()
        self.alarm_until = now + 30
        self.alarm_next_beep = 0.0
        self.alarm_title = title
        self.teleport_until = now + 1.2                 # kurzer Glitch-Effekt
        self.set_emotion_override("happy", 6)
        self.save()
        self.say(text, 12)

    def dismiss_alarm(self):
        self.alarm_until = 0.0

    def alarm_beep(self):
        try:
            if winsound is not None:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            else:
                self.root.bell()
        except (RuntimeError, tk.TclError):
            pass

    def draw_alarm(self, now):
        if not self.alarm_until or now >= self.alarm_until:
            return
        blink = int(now * 4) % 2 == 0
        width, height = (PHONE_SIZE, PHONE_SIZE) if self.phone_mode else (W, H)
        color = ACCENT if blink else LIGHT
        self.canvas.create_rectangle(3, 3, width - 3, height - 3, outline=color, width=4)
        self.canvas.create_text(width // 2, 62, text="⏰ " + (self.alarm_title or "ALARM"),
                                fill=color, font=("Consolas", 11, "bold"))

    # ================= Werkzeuge: Timer =================
    def timer_active(self):
        return self.s["timer"]["end"] > 0

    def timer_remaining(self):
        end = self.s["timer"]["end"]
        return max(0.0, end - time.time()) if end > 0 else 0.0

    def open_notes(self):
        """Notizblock: speichert beim Tippen automatisch, Strg+S/Schließen sichert zusätzlich."""
        win = getattr(self, "notes_win", None)
        try:
            if win is not None and win.winfo_exists():
                win.deiconify()
                win.lift()
                return
        except tk.TclError:
            pass
        win = self.notes_win = NovaToplevel(self.root)
        win.title("NOVA – Notizblock")
        win.attributes("-topmost", True)
        win.configure(bg=PANEL)
        win.geometry(f"360x300+{max(0, int(self.x) - 380)}+{max(0, int(self.y))}")
        info = tk.Label(win, text="", bg=PANEL, fg=EDGE, font=("Consolas", 8), anchor="e")
        info.pack(side="bottom", fill="x", padx=6)
        text = tk.Text(win, bg=PANEL2, fg=LIGHT, insertbackground=ACCENT, relief="flat",
                       font=("Consolas", 10), wrap="word", undo=True, padx=8, pady=8)
        text.pack(fill="both", expand=True, padx=6, pady=6)
        text.insert("1.0", self.s.get("notes", ""))
        job = [None]

        def save_now(_e=None):
            if job[0] is not None:
                try:
                    win.after_cancel(job[0])
                except tk.TclError:
                    pass
                job[0] = None
            self.s["notes"] = text.get("1.0", "end-1c")[:20000]
            self.save()
            info.config(text=f"gespeichert · {len(self.s['notes'])} Zeichen")
            return "break"

        def changed(_e=None):
            if not text.edit_modified():
                return
            text.edit_modified(False)
            info.config(text="…")
            if job[0] is not None:
                win.after_cancel(job[0])
            job[0] = win.after(800, save_now)

        def close():
            save_now()
            win.destroy()

        text.bind("<<Modified>>", changed)
        win.bind("<Control-s>", save_now)
        win.protocol("WM_DELETE_WINDOW", close)
        text.edit_modified(False)
        text.focus_set()

    def start_timer(self, seconds, label="Timer"):
        self.s["timer"] = {"end": time.time() + seconds, "total": float(seconds), "label": label}
        self.dismiss_alarm()
        self.save()
        self.say(f"{label} gestartet: {fmt_clock(seconds)}.", 4, speak=False)

    def add_timer_minutes(self, minutes=5):
        if not self.timer_active():
            self.say("Es läuft kein Timer.", 3, speak=False)
            return
        self.s["timer"]["end"] += minutes * 60
        self.s["timer"]["total"] += minutes * 60
        self.save()
        self.say(f"+{minutes} Min. Noch {fmt_clock(self.timer_remaining())}.", 3, speak=False)

    def stop_timer(self):
        if not self.timer_active():
            self.say("Es läuft kein Timer.", 3, speak=False)
            return
        self.s["timer"] = {"end": 0.0, "total": 0.0, "label": ""}
        self.save()
        self.say("Timer gestoppt.", 3, speak=False)

    def update_timer(self, now):
        timer = self.s["timer"]
        if timer["end"] <= 0 or now < timer["end"]:
            return
        label = timer.get("label") or "Timer"
        overdue = now - timer["end"]
        self.s["timer"] = {"end": 0.0, "total": 0.0, "label": ""}
        if label == "Fokus":
            self.add_points(3, announce=False)
            self.quest_event("focus")
            text = "Fokus geschafft! +3 Punkte. Zeit für eine Pause."
        else:
            text = f"{label} abgelaufen!"
        if overdue > 10:
            text += f" (vor {fmt_duration(overdue)})"
        self.trigger_alarm("TIMER VORBEI!", text)

    # ================= Werkzeuge: Erinnerungen =================
    def add_reminder(self, due, text, repeat=""):
        items = self.s["reminders"]
        if len(items) >= REMINDER_MAX:
            self.say("Zu viele Erinnerungen. Lösche zuerst ein paar.", 4, speak=False)
            return
        items.append({"due": float(due), "text": text, "repeat": repeat})
        items.sort(key=lambda r: r["due"])
        self.save()
        again = " (täglich)" if repeat else ""
        self.say(f"Okay, {fmt_when(due)}{again}: {text}", 6, speak=False)

    def remove_reminder(self, item):
        items = self.s["reminders"]
        for index, current in enumerate(items):
            if current is item:
                del items[index]
                self.save()
                self.say("Erinnerung gelöscht.", 3, speak=False)
                return

    def show_reminders(self):
        items = self.s["reminders"]
        if not items:
            self.say("Keine Erinnerungen eingetragen.", 3, speak=False)
            return
        parts = [f"{fmt_when(r['due'])}{'*' if r['repeat'] else ''} {r['text'][:22]}"
                 for r in items[:4]]
        extra = f" (+{len(items) - 4})" if len(items) > 4 else ""
        self.say("Erinnerungen: " + " · ".join(parts) + extra, 10, speak=False)

    def update_reminders(self):
        items = self.s["reminders"]
        if not items or items[0]["due"] > time.time():
            return
        now = time.time()
        due = [r for r in items if r["due"] <= now]
        overdue = now - min(r["due"] for r in due)
        texts = [r["text"] for r in due]
        for r in due:
            if r["repeat"] == "daily":
                while r["due"] <= now:
                    r["due"] += 86400.0
            else:
                for index, current in enumerate(items):
                    if current is r:
                        del items[index]
                        break
        items.sort(key=lambda r: r["due"])
        text = "🔔 " + " · ".join(texts)
        if overdue > 120:
            text += f" (verpasst, vor {fmt_duration(overdue)})"
        self.trigger_alarm("ERINNERUNG", text)

    # ================= Werkzeuge: Chips (Timer / Autoclicker) =================
    def draw_tool_chips(self, now, top=0):
        if self.game_end:
            return
        chips = []
        timer = self.s["timer"]
        if timer["end"] > 0:
            remaining = self.timer_remaining()
            progress = clamp(1.0 - remaining / max(1.0, timer["total"]), 0.0, 1.0)
            chips.append((f"⏱ {fmt_clock(remaining)}", progress, remaining <= 10))
        if self.ac_running:
            if now < self.ac_start_at:
                chips.append((f"🖱 in {int(self.ac_start_at - now) + 1}s", None, False))
            else:
                chips.append((f"🖱 {self.ac_count}", None, False))
        c = self.canvas
        for i, (text, progress, hot) in enumerate(chips):
            if self.phone_mode:
                x1, y1, x2 = 28, 28 + i * 26, 108
            elif self.mini:
                x1, y1, x2 = W // 2 - 40, max(4, top - 30 - i * 26), W // 2 + 40
            else:
                hud_visible = ((self.hover or now < self.hud_until)
                               and not self.naming and not self.prompt)
                y1 = (HUD_H + 6 if hud_visible else 6) + (40 if self.sys_monitor else 0) + i * 26
                x1, x2 = W // 2 - 44, W // 2 + 44
            y2 = y1 + 22
            panel(c, x1, y1, x2, y2, cut=5, fill=PANEL, outline=ACCENT if hot else EDGE, width=1)
            c.create_text((x1 + x2) / 2, y1 + (9 if progress is not None else 11), text=text,
                          fill=ACCENT if hot else LIGHT, font=("Consolas", 8, "bold"))
            if progress is not None:
                c.create_rectangle(x1 + 6, y2 - 6, x2 - 6, y2 - 3, outline=EDGE)
                c.create_rectangle(x1 + 6, y2 - 6, x1 + 6 + (x2 - x1 - 12) * progress, y2 - 3,
                                   fill=ACCENT, outline="")

    def poll_tools(self, now):
        """Alarmton, Autoclicker-Hotkeys (F6 / Esc) und Punktwahl; läuft in jedem Frame."""
        if self.alarm_until:
            if now >= self.alarm_until:
                self.alarm_until = 0.0
            elif now >= self.alarm_next_beep:
                self.alarm_next_beep = now + 4.0
                self.alarm_beep()
        if not IS_WIN:
            return
        down = bool(user32.GetAsyncKeyState(0x75) & 0x8000)             # F6
        if down and not self.ac_hotkey_down:
            self.ac_toggle()
        self.ac_hotkey_down = down
        if self.ac_running and (user32.GetAsyncKeyState(0x1B) & 0x8000):  # Esc
            self.ac_stop("Autoclicker mit Esc gestoppt.")
        if self.ac_pick_until:
            left = self.ac_pick_until - now
            if left <= 0:
                self.ac_finish_pick()
            else:
                self.bubble_text = f"Maus an den Zielort! Punkt wird in {int(left) + 1} s gesetzt."
                self.bubble_until = now + 1.0

    # ================= Werkzeuge: Autoclicker =================
    def ac_cfg(self):
        return self.s["autoclicker"]

    def ac_toggle(self):
        if self.ac_running:
            self.ac_stop()
        else:
            self.ac_start()

    def ac_apply_settings(self, announce=False, quiet=False):
        """Übernimmt die Werte aus dem Autoclicker-Fenster (falls offen). False bei ungültiger Eingabe.
        quiet=True: bei ungültiger Eingabe keine Fehlermeldung (z. B. während des Tippens)."""
        ui = self.ac_ui
        if not ui:
            return True

        def fail(message):
            if not quiet:
                self.ac_status = message
            return False

        ms = parse_interval(ui["interval"].get())
        if ms is None:
            return fail("Intervall ungültig (z. B. 500ms, 1.5s, 2min; mindestens 10 ms).")
        try:
            max_clicks = int(ui["max"].get().strip() or 0)
            delay = int(ui["delay"].get().strip() or 0)
        except ValueError:
            return fail("Max. Klicks und Startverzögerung müssen ganze Zahlen sein.")
        if max_clicks < 0 or not 0 <= delay <= 30:
            return fail("Max. Klicks: 0 oder mehr, Startverzögerung: 0 bis 30 Sekunden.")
        cfg = dict(self.ac_cfg())
        cfg.update(interval_ms=ms, button=ui["button"].get(), double=bool(ui["double"].get()),
                   minimize=bool(ui["minimize"].get()), max_clicks=max_clicks, delay=delay)
        self.s["autoclicker"] = sanitize_autoclicker(cfg)
        self.save()
        if announce:
            self.ac_status = "Einstellungen übernommen."
        return True

    def ac_settings_changed(self):
        """Wird bei jeder Änderung im Fenster aufgerufen: Werte live übernehmen, Anzeige auffrischen."""
        self.ac_apply_settings(quiet=True)
        self.refresh_ac_window(reschedule=False)

    def ac_set_interval(self, ms):
        if self.ac_ui:
            self.ac_ui["interval"].set(fmt_interval(ms))
        self.ac_settings_changed()

    def ac_set_button(self, key):
        if self.ac_ui:
            self.ac_ui["button"].set(key)
        self.ac_settings_changed()

    def ac_toggle_option(self, name):
        if self.ac_ui:
            var = self.ac_ui[name]
            var.set(not var.get())
        self.ac_settings_changed()

    def ac_start(self):
        if not IS_WIN:
            self.say("Der Autoclicker funktioniert nur unter Windows.", 4, speak=False)
            return
        if self.ac_running:
            return
        if not self.ac_apply_settings():
            self.refresh_ac_window()
            return
        cfg = self.ac_cfg()
        self.ac_running = True
        self.ac_count = 0
        self.ac_index = 0
        self.ac_blocked = 0.0              # Zeitpunkt, seit dem die Maus auf einem NOVA-Fenster liegt
        self.ac_status = ""
        self.ac_start_at = time.time() + cfg["delay"]
        where = f"{len(cfg['points'])} feste Punkte" if cfg["points"] else "an der Mausposition"
        self.say(f"Autoclicker startet in {cfg['delay']} s ({where}). F6 oder Esc stoppt.",
                 5, speak=False)
        self._ac_schedule(0)
        self.refresh_ac_window()

    def ac_start_from_ui(self):
        """Start/Stopp-Knopf im Fenster. Beim Start wird das Fenster minimiert, damit es nicht im Weg ist."""
        if self.ac_running:
            self.ac_stop()
            return
        self.ac_start()
        if self.ac_running and self.ac_cfg().get("minimize", True) and self.ac_window is not None:
            try:
                self.ac_window.iconify()
            except tk.TclError:
                pass

    def ac_stop(self, message=None, silent=False):
        was_running = self.ac_running
        self.ac_running = False
        self.ac_blocked = 0.0
        if self.ac_after_id is not None:
            try:
                self.root.after_cancel(self.ac_after_id)
            except tk.TclError:
                pass
            self.ac_after_id = None
        if was_running:
            text = message or f"Autoclicker gestoppt nach {self.ac_count} Klicks."
            self.ac_status = text
            if not silent:
                self.say(text, 5, speak=False)
        self.refresh_ac_window()

    def _ac_schedule(self, ms):
        if self.ac_after_id is not None:
            try:
                self.root.after_cancel(self.ac_after_id)
            except tk.TclError:
                pass
        try:
            self.ac_after_id = self.root.after(max(0, int(ms)), self._ac_step)
        except tk.TclError:
            self.ac_after_id = None

    def _ac_step(self):
        self.ac_after_id = None
        if not self.ac_running:
            return
        try:
            if time.time() < self.ac_start_at:
                self._ac_schedule(50)
                return
            cfg = self.ac_cfg()
            if self.ac_click_once(cfg):
                self.ac_blocked = 0.0
                self.ac_count += 1
                if cfg["max_clicks"] and self.ac_count >= cfg["max_clicks"]:
                    self.ac_stop(f"Autoclicker fertig: {self.ac_count} Klicks.")
                    return
                self._ac_schedule(cfg["interval_ms"])
                return
            # Ziel liegt auf einem NOVA-Fenster: kurz warten, statt sofort aufzugeben
            now = time.time()
            if not self.ac_blocked:
                self.ac_blocked = now
            elif now - self.ac_blocked >= AC_BLOCK_SECONDS:
                self.ac_stop("Autoclicker gestoppt: Die Maus lag zu lange auf einem NOVA-Fenster.")
                return
            self._ac_schedule(min(cfg["interval_ms"], 250))
        except Exception as err:
            self.ac_stop(f"Autoclicker-Fehler: {err}")

    def _ac_target_is_own(self, x, y):
        """True, wenn an dieser Stelle ein Fenster von NOVA liegt (dort wird nie geklickt)."""
        try:
            hwnd = user32.WindowFromPoint(wintypes.POINT(int(x), int(y)))
            if not hwnd:
                return False
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            return pid.value == os.getpid()
        except Exception:
            return False

    def ac_click_once(self, cfg):
        points = cfg["points"]
        if points:
            x, y = points[self.ac_index % len(points)]
            self.ac_index += 1
        else:
            pos = wintypes.POINT()
            if not user32.GetCursorPos(ctypes.byref(pos)):
                return False
            x, y = pos.x, pos.y
        if self._ac_target_is_own(x, y):
            return False
        if points:
            user32.SetCursorPos(int(x), int(y))
            time.sleep(0.012)              # das Ziel bekommt erst die Mausbewegung, dann den Klick
        down, up = {"left": (0x0002, 0x0004), "right": (0x0008, 0x0010),
                    "middle": (0x0020, 0x0040)}.get(cfg["button"], (0x0002, 0x0004))
        for i in range(2 if cfg["double"] else 1):
            if i:
                time.sleep(0.04)           # Pause zwischen den beiden Klicks des Doppelklicks
            user32.mouse_event(down, 0, 0, 0, 0)
            time.sleep(0.006)              # manche Programme ignorieren Drücken+Loslassen ohne Pause
            user32.mouse_event(up, 0, 0, 0, 0)
        return True

    def ac_pick_point(self):
        if not IS_WIN:
            self.say("Der Autoclicker funktioniert nur unter Windows.", 4, speak=False)
            return
        if len(self.ac_cfg()["points"]) >= AC_MAX_POINTS:
            self.ac_status = f"Höchstens {AC_MAX_POINTS} Punkte. Lösche zuerst welche."
            self.refresh_ac_window(reschedule=False)
            return
        self.ac_pick_until = time.time() + 5.0
        self.refresh_ac_window(reschedule=False)

    def ac_finish_pick(self):
        self.ac_pick_until = 0.0
        pos = wintypes.POINT()
        if not user32.GetCursorPos(ctypes.byref(pos)):
            return
        if self._ac_target_is_own(pos.x, pos.y):
            self.ac_status = "Der Punkt lag auf einem NOVA-Fenster. Bewege die Maus zum Ziel und versuche es erneut."
            self.say("Dort liegt ein NOVA-Fenster. Bitte woanders hin zeigen.", 4, speak=False)
            self.refresh_ac_window(reschedule=False)
            return
        cfg = self.ac_cfg()
        cfg["points"].append([int(pos.x), int(pos.y)])
        self.save()
        message = f"Punkt {len(cfg['points'])} gesetzt: ({pos.x}, {pos.y})"
        self.ac_status = message
        self.say(message, 4, speak=False)
        self.refresh_ac_window(reschedule=False)

    def ac_remove_point(self, index):
        points = self.ac_cfg()["points"]
        if 0 <= index < len(points):
            del points[index]
            self.ac_index = self.ac_index % len(points) if points else 0
            self.save()
            self.ac_status = f"Punkt {index + 1} entfernt."
        self.refresh_ac_window(reschedule=False)

    def ac_clear_points(self):
        self.ac_cfg()["points"] = []
        self.ac_index = 0
        self.save()
        self.ac_status = "Alle Punkte gelöscht: Es wird an der Mausposition geklickt."
        self.refresh_ac_window(reschedule=False)

    def _ac_chip(self, parent, text, command, bold=False):
        """Kleiner flacher Knopf im NOVA-Stil."""
        return tk.Button(parent, text=text, command=command, relief="flat", bd=0, cursor="hand2",
                         bg=PANEL, fg=LIGHT, activebackground=EDGE, activeforeground=LIGHT,
                         font=("Consolas", 9, "bold" if bold else "normal"), padx=10, pady=4)

    def open_ac_window(self):
        if self.ac_window is not None:
            try:
                if self.ac_window.winfo_exists():
                    self.ac_window.deiconify()
                    self.ac_window.lift()
                    return
            except tk.TclError:
                pass
        cfg = self.ac_cfg()
        win = NovaToplevel(self.root)
        win.title("NOVA – Autoclicker")
        win.configure(bg=PANEL)
        win.attributes("-topmost", True)
        win.resizable(False, False)         # Größe richtet sich nach dem Inhalt (auch bei Windows-Skalierung)
        win.protocol("WM_DELETE_WINDOW", self.close_ac_window)
        self.ac_window = win
        ui = {"interval": tk.StringVar(win, value=fmt_interval(cfg["interval_ms"])),
              "button": tk.StringVar(win, value=cfg["button"]),
              "double": tk.BooleanVar(win, value=cfg["double"]),
              "minimize": tk.BooleanVar(win, value=cfg.get("minimize", True)),
              "max": tk.StringVar(win, value=str(cfg["max_clicks"])),
              "delay": tk.StringVar(win, value=str(cfg["delay"])),
              "btns": {}, "presets": {}, "point_btns": [], "points_key": None}
        self.ac_ui = ui
        chip = self._ac_chip

        def card(parent, title):
            outer = tk.Frame(parent, bg=PANEL2, highlightthickness=1, highlightbackground=EDGE)
            outer.pack(fill="x", pady=(0, 10))
            tk.Label(outer, text=title, bg=PANEL2, fg=ACCENT, font=("Consolas", 9, "bold"),
                     anchor="w").pack(fill="x", padx=12, pady=(8, 4))
            inner = tk.Frame(outer, bg=PANEL2)
            inner.pack(fill="x", padx=12, pady=(0, 10))
            return inner

        def row(parent, label):
            line = tk.Frame(parent, bg=PANEL2)
            line.pack(fill="x", pady=3)
            tk.Label(line, text=label, bg=PANEL2, fg=LIGHT, font=("Consolas", 10, "bold"),
                     width=12, anchor="w").pack(side="left")
            return line

        def entry(parent, var, width):
            field = tk.Entry(parent, textvariable=var, width=width, bg=PANEL, fg=LIGHT,
                             insertbackground=ACCENT, relief="flat", justify="center",
                             highlightthickness=1, highlightbackground=EDGE,
                             highlightcolor=ACCENT, font=("Consolas", 11, "bold"))
            field.bind("<Return>", lambda e: self.ac_settings_changed())
            field.bind("<FocusOut>", lambda e: self.ac_settings_changed())
            return field

        body = tk.Frame(win, bg=PANEL)
        body.pack(fill="both", expand=True, padx=16, pady=16)

        # ---- Kopf: Status, Zähler, Fortschritt ----
        head = tk.Frame(body, bg=PANEL2, highlightthickness=2, highlightbackground=ACCENT)
        head.pack(fill="x", pady=(0, 10))
        top = tk.Frame(head, bg=PANEL2)
        top.pack(fill="x", padx=12, pady=(10, 0))
        ui["led"] = tk.Canvas(top, width=14, height=14, bg=PANEL2, highlightthickness=0)
        ui["led"].pack(side="left")
        ui["led_dot"] = ui["led"].create_oval(1, 1, 13, 13, fill=PANEL, outline=LIGHT)
        tk.Label(top, text="NOVA · AUTOCLICKER", bg=PANEL2, fg=ACCENT,
                 font=("Consolas", 14, "bold")).pack(side="left", padx=8)
        ui["state"] = tk.Label(top, bg=PANEL2, fg=DIM, font=("Consolas", 9, "bold"))
        ui["state"].pack(side="right")
        mid = tk.Frame(head, bg=PANEL2)
        mid.pack(fill="x", padx=12)
        ui["count"] = tk.Label(mid, text="0", bg=PANEL2, fg=LIGHT, font=("Consolas", 34, "bold"))
        ui["count"].pack(side="left")
        ui["count_sub"] = tk.Label(mid, bg=PANEL2, fg=DIM, font=("Consolas", 9),
                                   justify="left", anchor="w")
        ui["count_sub"].pack(side="left", padx=10, pady=(16, 0))
        ui["bar"] = tk.Canvas(head, height=6, bg=PANEL2, highlightthickness=0)
        ui["bar"].pack(fill="x", padx=12, pady=(2, 12))

        # ---- Einstellungen ----
        settings = card(body, "EINSTELLUNGEN")
        line = row(settings, "Intervall")
        entry(line, ui["interval"], 9).pack(side="left", ipady=3)
        for ms, text in AC_PRESETS:
            button = chip(line, text, lambda m=ms: self.ac_set_interval(m))
            button.pack(side="left", padx=(6, 0))
            ui["presets"][ms] = button
        line = row(settings, "Maustaste")
        for key, text in AC_BUTTONS.items():
            button = chip(line, text, lambda k=key: self.ac_set_button(k), bold=True)
            button.pack(side="left", padx=(0, 6))
            ui["btns"][key] = button
        line = row(settings, "Optionen")
        ui["double_btn"] = chip(line, "", lambda: self.ac_toggle_option("double"))
        ui["double_btn"].pack(side="left", padx=(0, 6))
        ui["min_btn"] = chip(line, "", lambda: self.ac_toggle_option("minimize"))
        ui["min_btn"].pack(side="left")
        line = row(settings, "Max. Klicks")
        entry(line, ui["max"], 7).pack(side="left", ipady=3)
        tk.Label(line, text="  Start nach", bg=PANEL2, fg=LIGHT,
                 font=("Consolas", 10, "bold")).pack(side="left")
        entry(line, ui["delay"], 4).pack(side="left", padx=(6, 0), ipady=3)
        tk.Label(line, text=" s   (Max. 0 = unbegrenzt)", bg=PANEL2, fg=DIM,
                 font=("Consolas", 8)).pack(side="left")

        # ---- Zielpunkte ----
        targets = card(body, "ZIELPUNKTE")
        ui["points_frame"] = tk.Frame(targets, bg=PANEL2)
        ui["points_frame"].pack(fill="x", pady=(0, 6))
        line = tk.Frame(targets, bg=PANEL2)
        line.pack(fill="x")
        tk.Button(line, text="＋ Punkt setzen (Maus hinbewegen, 5 s)", command=self.ac_pick_point,
                  relief="flat", bd=0, cursor="hand2", bg=EDGE, fg=LIGHT, activebackground=ACCENT,
                  activeforeground=LIGHT, font=("Consolas", 9, "bold"), padx=10,
                  pady=4).pack(side="left")
        chip(line, "Alle löschen", self.ac_clear_points).pack(side="left", padx=(6, 0))
        tk.Label(targets, text="Mehrere Punkte werden reihum angeklickt. Ohne Punkte wird dort "
                               "geklickt, wo die Maus steht. Auf NOVA-Fenster wird nie geklickt.",
                 bg=PANEL2, fg=DIM, font=("Consolas", 8), wraplength=470, justify="left",
                 anchor="w").pack(fill="x", pady=(8, 0))

        # ---- Start ----
        ui["toggle"] = tk.Button(body, command=self.ac_start_from_ui, relief="flat", bd=0,
                                 cursor="hand2", font=("Consolas", 14, "bold"), pady=10)
        ui["toggle"].pack(fill="x")
        ui["status"] = tk.Label(body, bg=PANEL, fg=LIGHT, font=("Consolas", 9), anchor="w",
                                wraplength=500, justify="left")
        ui["status"].pack(fill="x", pady=(8, 0))
        tk.Label(body, text="Notaus überall in Windows: F6 (Start/Stopp) und Esc (Stopp)",
                 bg=PANEL, fg=DIM, font=("Consolas", 8), anchor="w").pack(fill="x", pady=(2, 0))

        self.refresh_ac_window()
        win.update_idletasks()
        x = max(0, (win.winfo_screenwidth() - win.winfo_reqwidth()) // 2)
        y = max(0, (win.winfo_screenheight() - win.winfo_reqheight()) // 2)
        win.geometry(f"+{x}+{y}")            # nur die Position, die Größe bleibt automatisch

    def close_ac_window(self):
        self.ac_apply_settings(quiet=True)
        if self.ac_after_ui is not None and self.ac_window is not None:
            try:
                self.ac_window.after_cancel(self.ac_after_ui)
            except tk.TclError:
                pass
        self.ac_after_ui = None
        win, self.ac_window = self.ac_window, None
        self.ac_ui = {}
        if win is not None:
            try:
                win.destroy()
            except tk.TclError:
                pass
        self.save()

    def refresh_ac_window(self, reschedule=True):
        win, ui = self.ac_window, self.ac_ui
        if win is None or not ui:
            return
        try:
            if reschedule and self.ac_after_ui is not None:
                win.after_cancel(self.ac_after_ui)
                self.ac_after_ui = None
            cfg = self.ac_cfg()
            points = cfg["points"]
            now = time.time()
            orange = "#ff7a2f"
            picking = bool(self.ac_pick_until)
            waiting = self.ac_running and now < self.ac_start_at
            blocked = self.ac_running and not waiting and bool(self.ac_blocked)

            # Statuszeile im Kopf
            if picking:
                state, color = f"PUNKT IN {int(max(0, self.ac_pick_until - now)) + 1} s", orange
            elif waiting:
                state, color = f"START IN {int(self.ac_start_at - now) + 1} s", orange
            elif blocked:
                state, color = "WARTET", orange
            elif self.ac_running:
                state, color = "LÄUFT", ACCENT
            else:
                state, color = "BEREIT", DIM
            ui["state"].config(text=state, fg=color)
            blink = self.ac_running and not waiting and int(now * 2) % 2 == 0
            led = LIGHT if blink else (color if (self.ac_running or picking) else PANEL)
            ui["led"].itemconfigure(ui["led_dot"], fill=led)

            # Zähler, Rate und Fortschritt
            ui["count"].config(text=f"{self.ac_count:,}".replace(",", "."))
            extra = []
            if cfg["max_clicks"]:
                extra.append(f"von {cfg['max_clicks']:,}".replace(",", "."))
            if self.ac_running and not waiting and self.ac_count and now - self.ac_start_at >= 1.0:
                extra.append(f"{self.ac_count / (now - self.ac_start_at):.1f}/s")
            ui["count_sub"].config(text="Klicks" + ("\n" + " · ".join(extra) if extra else ""))
            bar = ui["bar"]
            width = max(1, bar.winfo_width())
            bar.delete("all")
            bar.create_rectangle(0, 0, width - 1, 5, fill=PANEL, outline=EDGE)
            if cfg["max_clicks"] and self.ac_count:
                frac = clamp(self.ac_count / cfg["max_clicks"], 0.0, 1.0)
                bar.create_rectangle(0, 0, (width - 1) * frac, 5, fill=ACCENT, outline="")

            # Auswahl-Knöpfe
            for key, button in ui["btns"].items():
                selected = ui["button"].get() == key
                button.config(bg=ACCENT if selected else PANEL, fg=PANEL if selected else LIGHT)
            current_ms = parse_interval(ui["interval"].get())
            for ms, button in ui["presets"].items():
                selected = current_ms == ms
                button.config(bg=ACCENT if selected else PANEL, fg=PANEL if selected else LIGHT)
            for name, button, text in (("double", ui["double_btn"], "Doppelklick"),
                                       ("minimize", ui["min_btn"], "Beim Start minimieren")):
                on = bool(ui[name].get())
                button.config(text=f"{'✔' if on else '○'} {text}",
                              bg=EDGE if on else PANEL, fg=LIGHT)

            # Zielpunkte als Chips (nur neu aufbauen, wenn sich die Liste geändert hat)
            key = tuple(tuple(p) for p in points)
            if key != ui["points_key"]:
                ui["points_key"] = key
                frame = ui["points_frame"]
                for child in frame.winfo_children():
                    child.destroy()
                ui["point_btns"] = []
                if points:
                    for i, (x, y) in enumerate(points):
                        button = self._ac_chip(frame, f"{i + 1}  ({x}, {y})  ✕",
                                               lambda idx=i: self.ac_remove_point(idx))
                        button.grid(row=i // 2, column=i % 2, sticky="ew", padx=(0, 6), pady=2)
                        ui["point_btns"].append(button)
                    frame.columnconfigure(0, weight=1)
                    frame.columnconfigure(1, weight=1)
                else:
                    tk.Label(frame, text="Kein fester Punkt: Es wird dort geklickt, wo die Maus steht.",
                             bg=PANEL2, fg=DIM, font=("Consolas", 9), anchor="w").pack(fill="x")
            active = ((self.ac_index - 1) % len(points)
                      if (self.ac_running and points and self.ac_index) else -1)
            for i, button in enumerate(ui["point_btns"]):
                button.config(bg=ACCENT if i == active else PANEL, fg=PANEL if i == active else LIGHT)

            # Start/Stopp-Knopf und Hinweistext
            running = self.ac_running
            ui["toggle"].config(text="■  STOPP  (F6)" if running else "▶  START  (F6)",
                                bg=ACCENT if running else EDGE, fg=PANEL if running else LIGHT,
                                activebackground=LIGHT if running else ACCENT, activeforeground=PANEL)
            if blocked:
                status = ("Die Maus liegt auf einem NOVA-Fenster. Bewege sie zum Ziel "
                          f"(Stopp nach {AC_BLOCK_SECONDS} s).")
            elif running:
                status = "Läuft. F6 oder Esc stoppt."
            elif picking:
                status = "Maus an den Zielort bewegen und dort ruhig halten …"
            else:
                status = self.ac_status or ("Bereit. Maus an die Zielstelle halten, dann Start "
                                            "klicken oder F6 drücken.")
            ui["status"].config(text=status)
            if reschedule:
                self.ac_after_ui = win.after(250, self.refresh_ac_window)
        except tk.TclError:
            self.ac_after_ui = None

    # ================= Wörter füttern =================
    def eat_word(self, raw, remember=True):
        """Verarbeitet ein Wort. Gibt (Text, Punkte, Futter) zurück."""
        w = re.sub(r"[^A-Za-zÄÖÜäöüß]", "", raw)[:20]
        if len(w) < 2:
            return "Das schmeckt nach nichts.", 0, 0.0
        lw = w.lower()
        words = self.s["words"]
        known = remember and lw in words
        food = float(min(25, 3 + 2 * len(w)))
        pts = 0
        msgs = []
        if known:
            words[lw] = int(words[lw]) + 1
            food *= 0.4
            msgs.append("Das hatte ich schon...")
        else:
            pts += 1 + len(w) // 4
            self.s["fun"] = clamp(self.s["fun"] + 3)
            if remember and len(words) < MAX_WORDS:
                words[lw] = 1
                if len(words) % 10 == 0:
                    pts += 10
                    msgs.append(f"{len(words)} Wörter im Wortschatz! Bonus!")
        if lw.startswith(self.craving.lower()):
            pts += 3
            food += 5
            msgs.append(f"Genau mein Geschmack: {self.craving}!")
        if len(lw) >= 3 and lw == lw[::-1]:
            pts += 3
            msgs.append("Ein Palindrom! Vorwärts wie rückwärts.")
        if not msgs:
            if len(lw) <= 3:
                msgs.append("Nur ein Häppchen.")
            elif len(lw) >= 10:
                msgs.append("Boah, ein Wortungetüm!")
            else:
                msgs.append(random.choice([f"Mmh, {w}!", f"{w} schmeckt knusprig.", f"{w}... nom nom."]))
        if random.random() < 0.25 and len(lw) >= 4:
            letters = list(lw)
            random.shuffle(letters)
            msgs.append("*rülps* " + "".join(letters))
        return " ".join(msgs), pts, food

    def eat_words(self, raw_words, remember=True):
        if self.sleeping:
            self.say("Zzz...", 3, speak=False)
            return
        if self.s["food"] >= 98:
            self.say("Ich platze gleich! Später wieder.", 3)
            return
        texts, total_pts, total_food, seen = [], 0, 0.0, set()
        for raw in raw_words:
            key = raw.lower()
            if key in seen:
                continue
            seen.add(key)
            text, pts, food = self.eat_word(raw, remember)
            texts.append(text)
            total_pts += pts
            total_food += food
        self.s["food"] = clamp(self.s["food"] + total_food)
        if total_pts:
            self.add_points(total_pts)
        self.quest_event("feed", len(texts))
        self.set_emotion_override("happy", 4)
        self.say(" ".join(texts[-2:]), 7, ai_context="feed")

    def feed_word(self):
        if self.mini:
            self.say("Im Vollbild bin ich zu klein zum Essen.", 3, speak=False)
            return
        if self.sleeping:
            self.say("Zzz...", 3, speak=False)
            return
        self.abort_input()
        self.feeding = True
        self.feed_deadline = time.time() + 30
        self.entry.delete(0, "end")
        self.entry.place(x=20, y=HUD_H + 2, width=W - 40, height=22)
        self.say("Wort tippen + Enter. Leer = Zwischenablage.", 30, speak=False)
        self.grab_focus()

    def start_name_prompt(self):
        """Namensfeld anzeigen; beim Umbenennen steht der bisherige Name markiert drin."""
        self.abort_input()
        self.name_before_edit = self.s.get("name", "").strip()
        self.naming = True
        self.entry.delete(0, "end")
        if self.name_before_edit:
            self.entry.insert(0, self.name_before_edit)
        self.entry.place(x=20, y=HUD_H + 2, width=W - 40, height=22)
        self.say("Wie soll ich heißen? Name + Enter (Esc = NOVA).", 60, speak=False)
        self.grab_focus()
        if self.name_before_edit:
            self.entry.select_range(0, "end")

    def finish_naming(self, value):
        name = (re.sub(r"[\x00-\x1f\x7f]", "", value).strip()[:16]
                or self.name_before_edit or "NOVA")
        self.naming = False
        self.name_before_edit = ""
        self.end_feeding()
        name_changed = name != self.s.get("name", "")
        self.s["name"] = name
        if name_changed:
            if self.ai_provider != "ollama":
                self.ai_history = []
            self._reset_ai_speech()
        self.save()
        self.say(f"{name} online. Schön, dich kennenzulernen!", 5)
        if name_changed and self.ai_enabled and self._ai_is_ready():
            self._request_ai_speech_lines()

    def grab_focus(self):
        """Tastaturfokus für das randlose Fenster holen (Windows ist da zickig)."""
        try:
            self.root.focus_force()
            if IS_WIN:
                wid = self.root.winfo_id()
                user32.SetForegroundWindow(user32.GetAncestor(wid, 2) or wid)
            self.entry.focus_force()
        except Exception:
            pass

    def end_feeding(self):
        self.feeding = False
        self.entry.place_forget()

    def abort_input(self):
        """Blendet das Eingabefeld ohne Speichern aus."""
        self.prompt = None
        self.naming = False
        self.name_before_edit = ""
        self.end_feeding()

    def cancel_feed(self):
        if self.prompt:
            self.abort_input()
            self.bubble_until = 0.0
            return
        if self.naming:
            self.finish_naming(self.name_before_edit or "NOVA")
            return
        if self.feeding:
            self.end_feeding()
            self.bubble_until = 0.0

    def submit_feed(self, event=None):
        text = self.entry.get()
        if self.naming:
            self.finish_naming(text)
            return
        if self.prompt:
            self.finish_prompt(text)
            return
        self.end_feeding()
        if text.strip():
            self.eat_words(text.split()[:5], remember=True)
        else:
            self.feed_clipboard()

    def feed_clipboard(self):
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            self.say("Die Zwischenablage ist leer.", 3, speak=False)
            return
        words = re.findall(r"[A-Za-zÄÖÜäöüß]{2,20}", text)[:5]
        if not words:
            self.say("Da ist nichts Essbares drin.", 3, speak=False)
            return
        self.eat_words(words, remember=False)   # Zwischenablage wird nicht gespeichert

    def show_vocab(self):
        words = self.s["words"]
        if not words:
            self.say("Mein Wortschatz ist leer. Füttere mich!", 4, speak=False)
            return
        self.say(f"Wortschatz: {len(words)} Wörter. Zuletzt: {', '.join(list(words)[-5:])}", 7,
                 speak=False)

    # ================= Fenster-Modus =================
    def toggle_window_mode(self):
        if not IS_WIN:
            self.window_mode = False
            self.say("Der Fenster-Modus geht nur unter Windows.", 4, speak=False)
            return
        self.window_mode = not self.window_mode
        self.s["window_mode"] = self.window_mode
        self.save()
        if self.window_mode:
            self.say("Ich klettere auf deine Fenster!", 4)
        else:
            self.returning = True
            self.platform = None
            self.platform_hwnd = None
            self.small = False
            self.say("Ich bleibe wieder unten.", 3)

    def toggle_sys_monitor(self):
        if not IS_WIN:
            self.say("Der System-Monitor funktioniert nur unter Windows.", 4, speak=False)
            return
        self.sys_monitor = not self.sys_monitor
        self.s["sys_monitor"] = self.sys_monitor
        self.save()
        if self.sys_monitor:
            self.update_system_metrics()
            self.say(f"System-Monitor an. CPU {int(self.cpu_percent)}%, RAM {int(self.ram_percent)}%.", 4)
        else:
            self.say("System-Monitor ausgeblendet.", 3, speak=False)

    def update_system_metrics(self):
        """Liest CPU- und Arbeitsspeicher-Auslastung über die Windows-API ohne Zusatzpakete aus."""
        if not IS_WIN:
            return
        try:
            mem = MEMORYSTATUSEX()
            mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)):
                self.ram_percent = float(mem.dwMemoryLoad)
        except Exception:
            pass
        try:
            idle_ft, kernel_ft, user_ft = FILETIME(), FILETIME(), FILETIME()
            if kernel32.GetSystemTimes(ctypes.byref(idle_ft), ctypes.byref(kernel_ft), ctypes.byref(user_ft)):
                idle = (idle_ft.dwHighDateTime << 32) | idle_ft.dwLowDateTime
                kernel = (kernel_ft.dwHighDateTime << 32) | kernel_ft.dwLowDateTime
                user = (user_ft.dwHighDateTime << 32) | user_ft.dwLowDateTime
                if self.last_cpu_times is not None:
                    p_idle, p_kernel, p_user = self.last_cpu_times
                    d_idle = idle - p_idle
                    d_total = (kernel - p_kernel) + (user - p_user)
                    if d_total > 0:
                        self.cpu_percent = clamp(100.0 * (1.0 - d_idle / d_total))
                self.last_cpu_times = (idle, kernel, user)
        except Exception:
            pass

    def draw_sys_monitor(self):
        """Zeichnet eine kompakte Cyberpunk-Telemetrie-Box für CPU & RAM."""
        if not self.sys_monitor or self.mini:
            return
        c = self.canvas
        y1 = HUD_H + 6 if (self.hover or time.time() < self.hud_until) else 6
        y2 = y1 + 36
        panel(c, 8, y1, W - 8, y2, cut=5, fill=PANEL, outline=EDGE, width=1)
        for label, val, x in (("CPU", self.cpu_percent, 18), ("RAM", self.ram_percent, 114)):
            col = ACCENT if val >= 80 else "#ff7a2f" if val >= 55 else LIGHT
            c.create_text(x, y1 + 10, text=f"{label} {int(val):>2d}%", anchor="w",
                          fill=col, font=("Consolas", 7, "bold"))
            c.create_rectangle(x, y1 + 18, x + 84, y1 + 25, outline=EDGE)
            c.create_rectangle(x, y1 + 18, x + 84 * clamp(val) / 100.0, y1 + 25,
                               fill=col, outline="")

    def toggle_living_mode(self):
        if not IS_WIN:
            self.say("Der Lebensmodus funktioniert nur unter Windows.", 4, speak=False)
            return
        self.living_mode = not self.living_mode
        self.s["living_mode"] = self.living_mode
        self.platform = None
        self.platform_hwnd = None
        self.small = False
        self.returning = True
        self.system_dozing = False
        self.next_window_hop = time.time()
        self.last_cursor_move_at = time.monotonic()
        self.say(
            "Systemleben aktiviert." if self.living_mode else "Systemleben pausiert.",
            3, speak=False)
        self.save()

    def control_media_key(self, action, quiet=False):
        if not IS_WIN:
            self.say("Die PC-Steuerung funktioniert nur unter Windows.", 4, speak=False)
            return
        keys = {
            "volume_up": (0xAF, "Lautstärke erhöht."),
            "volume_down": (0xAE, "Lautstärke gesenkt."),
            "mute": (0xAD, "Stummschaltung umgeschaltet."),
            "play_pause": (0xB3, "Wiedergabe umgeschaltet."),
            "next_track": (0xB0, "Nächster Titel."),
            "prev_track": (0xB1, "Vorheriger Titel."),
        }
        key = keys.get(action)
        if key is None:
            self.say("Diese Steueraktion ist nicht verfügbar.", 4, speak=False)
            return
        try:
            user32.keybd_event(key[0], 0, 0, 0)
            user32.keybd_event(key[0], 0, 0x0002, 0)
        except (OSError, ValueError) as err:
            self.say(f"PC-Steuerung fehlgeschlagen: {err}", 5, speak=False)
            return
        if not quiet:
            self.say(key[1], 2, speak=False)

    def add_controlled_app(self):
        if len(self.s["controlled_apps"]) >= 6:
            self.say("Es können höchstens sechs Apps freigegeben werden.", 4, speak=False)
            return
        path = filedialog.askopenfilename(
            parent=self.root,
            filetypes=[("Windows-Programme", "*.exe"), ("Alle Dateien", "*.*")])
        if not path:
            return
        path = os.path.abspath(path)
        if not path.lower().endswith(".exe") or not os.path.isfile(path):
            messagebox.showerror("Ungültiges Programm",
                                 "Bitte eine vorhandene EXE-Datei auswählen.",
                                 parent=self.root)
            return
        if path not in self.s["controlled_apps"]:
            self.s["controlled_apps"].append(path)
            self.save()
        self.say(f"{os.path.basename(path)} ist jetzt freigegeben.", 3, speak=False)

    def launch_controlled_app(self, path):
        if path not in self.s["controlled_apps"] or not path.lower().endswith(".exe"):
            self.say("Dieses Programm ist nicht freigegeben.", 4, speak=False)
            return
        if not IS_WIN:
            self.say("Das Starten freigegebener Apps geht nur unter Windows.", 4, speak=False)
            return
        if not os.path.isfile(path):
            self.say("Die freigegebene App wurde nicht gefunden.", 4, speak=False)
            return
        try:
            os.startfile(path)
        except OSError as err:
            self.say(f"App konnte nicht gestartet werden: {err}", 5, speak=False)
            return
        self.say(f"{os.path.basename(path)} gestartet.", 3, speak=False)

    def toggle_fav_app(self, path):
        favs = self.s["fav_apps"]
        if path in favs:
            favs.remove(path)
        elif len(favs) >= 4:
            self.say("Höchstens 4 Favoriten.", 3, speak=False)
            return
        else:
            favs.append(path)
        self.save()

    def draw_fav_chips(self):
        """Kleine anklickbare Favoriten-Apps unten links/rechts neben dem Sprite."""
        self.fav_rects = []
        favs = [f for f in self.s["fav_apps"] if f in self.s["controlled_apps"]]
        if (not favs or self.radial_window is None
                or getattr(self, "radial_page_name", "") != "main" or self.mini or self.phone_mode or self.game_end or self.naming
                or self.prompt or self.feeding):
            return
        key = self.art_key()
        fw = self.art_base(key, self.current_height())[0].width if key is not None else 92
        c, cx = self.canvas, W // 2
        n = len(favs)
        foot = H - 5 - self.foot_drop() - 60          # Höhe an der Fußlinie ausrichten
        gap = (W - 16 - 40 * n) / (n + 1) if n > 1 else 0
        for i, path in enumerate(favs):
            x1 = round(8 + gap * (i + 1) + 40 * i) if n > 1 else (W - 40) // 2
            y1 = foot - (6 if i % 2 else 0)
            x2, y2 = x1 + 40, y1 + 16
            panel(c, x1, y1, x2, y2, cut=3, fill=PANEL, outline=EDGE, width=1)
            c.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                          text=os.path.splitext(os.path.basename(path))[0][:6],
                          fill=LIGHT, font=("Consolas", 7, "bold"))
            self.fav_rects.append((x1, y1, x2, y2, path))

    def remove_controlled_app(self, path):
        if path in self.s["fav_apps"]:
            self.s["fav_apps"].remove(path)
        if path in self.s["controlled_apps"]:
            self.s["controlled_apps"].remove(path)
            self.save()
            self.say(f"{os.path.basename(path)} entfernt.", 3, speak=False)

    def own_window_handles(self):
        handles = set()
        for window in (self.root, self.radial_window):
            if window is None:
                continue
            try:
                wid = window.winfo_id()
                handles.update((wid, user32.GetParent(wid), user32.GetAncestor(wid, 2)))
            except tk.TclError:
                continue
        return {handle for handle in handles if handle}

    def is_own_window(self, hwnd):
        return hwnd in self.own_window_handles()

    def remember_foreground_window(self):
        if not IS_WIN:
            return
        hwnd = user32.GetForegroundWindow()
        if hwnd and not self.is_own_window(hwnd) and user32.IsWindow(hwnd):
            if hwnd != self.last_external_window:
                self.last_cursor_move_at = time.monotonic()
                self.system_dozing = False
            self.last_external_window = hwnd

    def minimize_last_window(self):
        if not IS_WIN or not self.last_external_window:
            self.say("Kein App-Fenster zum Minimieren gefunden.", 3, speak=False)
            return
        hwnd = self.last_external_window
        if not user32.IsWindow(hwnd) or self.is_own_window(hwnd):
            self.say("Das App-Fenster ist nicht mehr verfügbar.", 3, speak=False)
            return
        user32.ShowWindow(hwnd, 6)
        self.minimized_window = hwnd
        self.say("App-Fenster minimiert.", 2, speak=False)

    def restore_last_window(self):
        hwnd = self.minimized_window
        if not IS_WIN or not hwnd or not user32.IsWindow(hwnd) or self.is_own_window(hwnd):
            self.say("Kein minimiertes App-Fenster zum Wiederherstellen.", 3, speak=False)
            return
        user32.ShowWindow(hwnd, 9)
        user32.SetForegroundWindow(hwnd)
        self.minimized_window = None
        self.say("App-Fenster wiederhergestellt.", 2, speak=False)

    def min_platform_top(self):
        k = self.sprite_scale()
        small_h = round(SPRITE_H_SMALL * k) if self.art_key() else int(178 * 0.75 * k) + 25
        return small_h + 30 + self.music_offset()

    def find_platform(self):
        """Oberkante des aktiven Fensters als (links, oben, rechts) oder None."""
        if not IS_WIN:
            return None
        try:
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return None
            if self.is_own_window(hwnd):
                return self.platform           # Klick auf NOVA: Plattform behalten
            if user32.IsIconic(hwnd):
                return None
            buf = ctypes.create_unicode_buffer(64)
            user32.GetClassNameW(hwnd, buf, 64)
            if buf.value in IGNORED_CLASSES:
                return None
            r = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            if (r.right - r.left < 150
                    or self.room_above(r.left, r.top, r.right) < self.min_platform_top()):
                return None
            self.platform_hwnd = hwnd
            return (r.left, r.top, r.right)
        except Exception:
            return None

    def window_platform(self, hwnd):
        if not IS_WIN or not hwnd or not user32.IsWindow(hwnd):
            return None
        if self.is_own_window(hwnd) or not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
            return None
        buf = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(hwnd, buf, 64)
        if buf.value in IGNORED_CLASSES:
            return None
        rect = wintypes.RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return None
        vl, vt, vr, vb = self.virtual_bounds()
        if (rect.right - rect.left < 180 or rect.bottom - rect.top < 150 or
                rect.right <= vl or rect.left >= vr or rect.bottom <= vt or rect.top >= vb):
            return None
        return (rect.left, rect.top, rect.right)

    def visible_window_platforms(self):
        if not IS_WIN:
            return []
        windows = []

        def collect(hwnd, _):
            rect = self.window_platform(hwnd)
            if rect is not None:
                windows.append((hwnd, rect))
            return True

        callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        callback = callback_type(collect)
        user32.EnumWindows(callback, 0)
        return windows

    def walk_bounds(self):
        if (self.window_mode or self.living_mode or self.perch_hwnd is not None) and self.platform:
            left, _, right = self.platform
            lo = left - 20
            return lo, max(lo, right - W + 20)
        mon = self.current_monitor()
        return mon[0], max(mon[0], mon[2] - W)

    def follow_platform(self):
        if self.t // 6 != self._tp // 6:
            self.remember_foreground_window()
            if self.perch_hwnd is not None:
                current = self.window_platform(self.perch_hwnd)
                if current is None:
                    self.drop_from_perch()        # Fenster weg oder minimiert: NOVA fällt
                    return
                self.platform = current
                self.platform_hwnd = self.perch_hwnd
            elif self.living_mode:
                current = self.window_platform(self.platform_hwnd)
                if current is None:
                    had_platform = self.platform is not None
                    self.platform_hwnd = None
                    self.platform = None
                    if had_platform and self.start_fall():
                        return
                else:
                    self.platform = current
                if time.time() >= self.next_window_hop:
                    candidates = self.visible_window_platforms()
                    if len(candidates) > 1 and self.platform_hwnd is not None:
                        candidates = [item for item in candidates
                                      if item[0] != self.platform_hwnd] or candidates
                    if candidates:
                        self.platform_hwnd, self.platform = random.choice(candidates)
                        left, top, right = self.platform
                        vl, vt, vr, vb = self.virtual_bounds()
                        lo = max(vl, left - 20)
                        hi = min(max(lo, right - W + 20), max(vl, vr - W))
                        self.x = random.randint(int(lo), int(max(lo, hi)))
                        self.y = max(vt, top - H + 11 + self.foot_drop())
                        self.teleport_until = time.time() + 0.75
                    else:
                        self.platform = self.find_platform()
                    self.next_window_hop = time.time() + random.uniform(18, 35)
            else:
                self.platform = self.find_platform() if self.window_mode else None
                if not self.platform:
                    self.platform_hwnd = None
            self.small = bool(self.platform)
        drop = self.foot_drop()
        floor_y = self.floor_y()
        target = floor_y
        if self.platform:
            target = min(floor_y, max(self.virtual_bounds()[1],
                                      self.platform[1] - H + 11 + drop))
        self.y += (target - self.y) * 0.18
        if abs(target - self.y) < 1:
            self.y = target
            if not self.window_mode:
                self.returning = False
        lo, hi = self.walk_bounds()
        if self.x < lo:
            self.x += (lo - self.x) * 0.2
        elif self.x > hi:
            self.x -= (self.x - hi) * 0.2

    # ================= Spotify / Musik-Box =================
    def toggle_spotify_mode(self):
        if not IS_WIN:
            self.say("Die Spotify-Erkennung funktioniert nur unter Windows.", 4, speak=False)
            return
        self.spotify_mode = not self.spotify_mode
        self.s["spotify_mode"] = self.spotify_mode
        self.spotify_next_poll = 0.0
        if not self.spotify_mode:
            self.reset_spotify_state()
        self.save()
        self.say("Spotify-Box eingeschaltet." if self.spotify_mode else "Spotify-Box ausgeschaltet.",
                 3, speak=False)

    def reset_spotify_state(self):
        self.spotify_open = False
        self.spotify_playing = False
        self.spotify_title = ""

    def _process_name(self, pid):
        """Exe-Name zu einer Prozess-ID (zwischengespeichert, da das Fenster-Scannen jede Sekunde läuft)."""
        cached = self.pid_names.get(pid)
        if cached is not None:
            return cached
        name = ""
        handle = kernel32.OpenProcess(0x1000, False, pid)   # PROCESS_QUERY_LIMITED_INFORMATION
        if handle:
            try:
                buf = ctypes.create_unicode_buffer(520)
                size = wintypes.DWORD(len(buf))
                if kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
                    name = os.path.basename(buf.value).lower()
            finally:
                kernel32.CloseHandle(handle)
        if len(self.pid_names) > 400:
            self.pid_names.clear()
        self.pid_names[pid] = name or "?"
        return self.pid_names[pid]

    def scan_spotify(self):
        """Sucht sichtbare Spotify-Fenster. Gibt (offen, Songtitel) zurück; Titel leer = Pause."""
        titles = []

        def collect(hwnd, _):
            try:
                if not user32.IsWindowVisible(hwnd):
                    return True
                length = user32.GetWindowTextLengthW(hwnd)
                if length <= 0:
                    return True
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value.strip()
                if not title or title.casefold().startswith(SPOTIFY_IGNORED_TITLES):
                    return True
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if self._process_name(pid.value) == "spotify.exe":
                    titles.append(title)
            except Exception:
                pass
            return True

        callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        callback = callback_type(collect)
        user32.EnumWindows(callback, 0)
        if not titles:
            return False, ""
        for title in titles:
            if title.casefold() not in SPOTIFY_IDLE_TITLES:
                return True, title
        return True, ""

    def _spotify_worker(self):
        """Fensterscan im Hintergrund, damit der Hauptthread nicht ruckelt."""
        try:
            self._spotify_result = self.scan_spotify()
        except Exception:
            pass
        finally:
            self._spotify_busy = False

    def update_spotify(self, now):
        result = getattr(self, "_spotify_result", None)
        self._spotify_result = None
        if (not getattr(self, "_spotify_busy", False)
                and now >= getattr(self, "spotify_next_poll", 0.0)):
            self.spotify_next_poll = now + 1.5
            self._spotify_busy = True
            threading.Thread(target=self._spotify_worker, daemon=True).start()
        if result is None:
            return
        is_open, title = result
        if not is_open:
            if self.spotify_open:
                self.reset_spotify_state()
            return
        self.spotify_open = True
        self.spotify_playing = bool(title)
        if title and title != self.spotify_title:
            self.spotify_title = title
            if not self.sleeping and not self.game_end:
                self.say(f"♪ {title}"[:80], 4, speak=False)

    def music_active(self):
        return self.spotify_mode and self.spotify_open

    def music_visible(self):
        """Box sichtbar: Spotify offen, Emotion Musik (nicht müde), kein Minispiel, kein Beenden."""
        return (self.music_active() and self.emotion == "music"
                and not self.game_end and not self.quitting)

    def music_offset(self):
        """Wie weit NOVA nach oben rückt, weil sie auf der Box sitzt (nur normaler/Mini-Modus)."""
        if self.phone_mode or not self.music_visible():
            return 0
        return (MUSIC_BOX_H_MINI if self.mini else MUSIC_BOX_H) - 2 - self.sit_drop()

    def music_layout(self):
        """Gemeinsame Geometrie für Zeichnen und Klick-Erkennung (normal, Mini, Telefon)."""
        if self.phone_mode:
            box = (22, 168, PHONE_SIZE - 22, 214)
            keys, gap, r, bfont, chars, tfont, cx = MUSIC_KEYS_FULL, 34, 10, 9, 34, 7, PHONE_SIZE // 2
            title_y = box[1] + 12
        elif self.mini:
            box = (W // 2 - 75, H - 5 - MUSIC_BOX_H_MINI, W // 2 + 75, H - 5)
            keys, gap, r, bfont, chars, tfont, cx = MUSIC_KEYS_COMPACT, 30, 9, 8, 20, 7, W // 2
            title_y = box[1] + 9
        else:
            box = (12, H - 5 - MUSIC_BOX_H, W - 12, H - 5)
            keys, gap, r, bfont, chars, tfont, cx = MUSIC_KEYS_FULL, 36, 13, 11, 24, 8, W // 2
            title_y = box[1] + 12
        btn_y = box[3] - r - 6
        buttons = []
        for i, key in enumerate(keys):
            radius = r + 2 if key == "play_pause" else r
            buttons.append((key, cx + (i - (len(keys) - 1) / 2) * gap, btn_y, radius))
        return {"box": box, "title": (box[0] + 30, title_y), "eq": (box[0] + 8, title_y - 6),
                "chars": chars, "tfont": tfont, "bfont": bfont, "buttons": buttons}

    def music_button_at(self, x, y):
        if not self.music_visible():
            return None
        for key, bx, by, radius in self.music_layout()["buttons"]:
            if (x - bx) ** 2 + (y - by) ** 2 <= (radius + 3) ** 2:
                return key
        return None

    def press_music_button(self, key):
        now = time.time()
        self.music_pressed = (key, now + 0.18)
        self.spotify_next_poll = now + 0.5      # Titel/Pause-Status bald neu lesen
        self.control_media_key(key, quiet=True)

    def music_display_text(self, chars):
        if self.spotify_playing:
            text = self.spotify_title
        elif self.spotify_title:
            text = "Pause · " + self.spotify_title
        else:
            text = "Spotify · Pause"
        if len(text) <= chars:
            return text
        padded = text + "   ·   "
        start = (self.t // 4) % len(padded)          # Lauftext
        return (padded * 2)[start:start + chars]

    def draw_music_box(self, now):
        if not self.music_visible():
            return
        c = self.canvas
        layout = self.music_layout()
        x1, y1, x2, y2 = layout["box"]
        panel(c, x1, y1, x2, y2, cut=6, fill=PANEL, outline=ACCENT, width=2)
        ex, ey = layout["eq"]
        for i in range(4):
            h = 3 + 8 * (0.5 + 0.5 * math.sin(self.t * 0.45 + i * 1.9)) if self.spotify_playing else 3
            c.create_rectangle(ex + i * 5, ey + 6 - h, ex + i * 5 + 3, ey + 6,
                               fill=ACCENT, outline="")
        tx, ty = layout["title"]
        c.create_text(tx, ty, text=self.music_display_text(layout["chars"]), anchor="w",
                      fill=LIGHT, font=("Consolas", layout["tfont"], "bold"))
        pressed_key, pressed_until = self.music_pressed
        symbols = {"prev_track": "⏮", "next_track": "⏭",
                   "play_pause": "⏸" if self.spotify_playing else "▶",
                   "volume_down": "−", "volume_up": "+"}
        for key, bx, by, radius in layout["buttons"]:
            pressed = key == pressed_key and now < pressed_until
            if pressed:
                fill, outline = ACCENT, LIGHT
            elif key == "play_pause" and self.spotify_playing:
                fill, outline = EDGE, LIGHT
            else:
                fill, outline = PANEL2, ACCENT
            c.create_oval(bx - radius, by - radius, bx + radius, by + radius,
                          fill=fill, outline=outline, width=2)
            font = (("Consolas", layout["bfont"] + 3, "bold") if key.startswith("volume")
                    else ("Segoe UI Symbol", layout["bfont"]))
            c.create_text(bx, by, text=symbols[key], fill=LIGHT, font=font)

    # ================= Mini-Modus =================
    def fullscreen_active(self):
        """True, wenn Windows ein Vollbild-Programm meldet (Video, Spiel, F11 ...)."""
        if not IS_WIN:
            return False
        try:
            state = ctypes.c_int(0)
            if ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state)) != 0:
                return False
            return state.value in (2, 3, 4)   # BUSY, D3D_FULL_SCREEN, PRESENTATION_MODE
        except Exception:
            return False

    def update_mini(self):
        if self.phone_mode:
            return
        want = self.mini_manual or (self.mini_auto and self.fullscreen_active())
        if want == self.mini:
            return
        self.mini = want
        if want:
            self.hover = False
            self.abort_input()
            self.cancel_game()
        else:
            self.returning = True

    def toggle_mini_auto(self):
        self.mini_auto = not self.mini_auto
        self.s["mini_auto"] = self.mini_auto
        self.save()
        self.update_mini()

    def toggle_mini_manual(self):
        self.mini_manual = not self.mini_manual
        self.s["mini_manual"] = self.mini_manual
        self.save()
        self.update_mini()

    def toggle_phone_mode(self):
        old_width, old_height = self.display_width(), self.display_height()
        self.phone_mode = not self.phone_mode
        self.s["phone_mode"] = self.phone_mode
        new_width, new_height = self.display_width(), self.display_height()
        self.canvas.configure(width=new_width, height=new_height)
        self.x = int(clamp(
            self.x + (old_width - new_width) / 2, 0, max(0, self.sw - new_width)))
        self.y = int(clamp(
            self.y + (old_height - new_height) / 2, 0, max(0, self.sh - new_height)))
        if self.phone_mode:
            self.abort_input()
            self.cancel_game()
            self.mini = False
            self.returning = False
            self.phys_active = False
            self.vx = self.vy = 0.0
            self.perch_hwnd = None
            self.platform = None
            self.small = False
            self.say("Telefonmodus aktiviert.", 3, speak=False)
        else:
            self.update_mini()
            if self.window_mode:
                self.returning = True
            self.start_fall()
            self.say("Telefonmodus beendet.", 3, speak=False)
        self.root.geometry(
            f"{new_width}x{new_height}+{int(self.x)}+{int(self.y)}")
        self.save()

    # ================= Fadenkreuz-Modus =================
    CROSSHAIR_SIZE = 120
    CROSSHAIR_EXIT_DIST = 150      # so weit wegziehen = Modus aus

    def crosshair_center(self):
        mon = self.current_monitor()
        return (mon[0] + mon[2]) // 2, (mon[1] + mon[3]) // 2

    def toggle_crosshair(self):
        if self.crosshair_mode:
            self.stop_crosshair()
        else:
            self.start_crosshair()

    def start_crosshair(self):
        self.close_radial_menu()
        self.abort_input()
        self.cancel_game()
        n = self.CROSSHAIR_SIZE
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.config(bg=TRANS)
        try:
            win.attributes("-transparentcolor", TRANS)
        except tk.TclError:
            pass
        cv = tk.Canvas(win, width=n, height=n, bg=TRANS, highlightthickness=0, cursor="fleur")
        cv.pack()
        self.crosshair_photo = None
        src = self.emotion_sources.get("crosshair")
        if src is not None and ImageOps is not None:
            img = ImageOps.contain(src, (n, n), method=Image.LANCZOS)
            self.crosshair_photo = self._flat_photo(img)   # hartes Alpha -> echte Transparenz
            cv.create_image(n // 2, n // 2, image=self.crosshair_photo)
        else:
            c, r = n // 2, n // 2 - 4
            cv.create_oval(c - r, c - r, c + r, c + r, fill="#020304", outline="")  # fast unsichtbare Greiffläche
            cv.create_oval(c - r, c - r, c + r, c + r, outline=ACCENT, width=2)
            cv.create_oval(c - r // 2, c - r // 2, c + r // 2, c + r // 2, outline=EDGE, width=1)
            cv.create_line(c, 2, c, c - 8, fill=ACCENT, width=2)
            cv.create_line(c, c + 8, c, n - 2, fill=ACCENT, width=2)
            cv.create_line(2, c, c - 8, c, fill=ACCENT, width=2)
            cv.create_line(c + 8, c, n - 2, c, fill=ACCENT, width=2)
            cv.create_oval(c - 2, c - 2, c + 2, c + 2, fill=ACCENT, outline="")
        drag = {}

        def press(e):
            drag["dx"], drag["dy"] = e.x, e.y

        def motion(e):
            if "dx" in drag:
                win.geometry(f"{n}x{n}+{e.x_root - drag['dx']}+{e.y_root - drag['dy']}")

        def release(e):
            if "dx" not in drag:
                return
            drag.clear()
            cx, cy = self.crosshair_center()
            mx = win.winfo_x() + n // 2
            my = win.winfo_y() + n // 2
            if math.hypot(mx - cx, my - cy) > self.CROSSHAIR_EXIT_DIST:
                self.stop_crosshair()
            else:
                win.geometry(f"{n}x{n}+{cx - n // 2}+{cy - n // 2}")

        cv.bind("<ButtonPress-1>", press)
        cv.bind("<B1-Motion>", motion)
        cv.bind("<ButtonRelease-1>", release)
        cx, cy = self.crosshair_center()
        win.geometry(f"{n}x{n}+{cx - n // 2}+{cy - n // 2}")
        self.crosshair_win = win
        self.crosshair_mode = True
        self.root.withdraw()

    def stop_crosshair(self):
        win, self.crosshair_win = self.crosshair_win, None
        self.crosshair_mode = False
        self.crosshair_photo = None
        if win is not None:
            try:
                win.destroy()
            except tk.TclError:
                pass
        try:
            self.root.deiconify()
            self.root.attributes("-topmost", True)
        except tk.TclError:
            pass
        self.last_tick = time.time()

    def follow_corner(self):
        mon = self.current_monitor()
        self.x += ((mon[2] - W + 10) - self.x) * 0.2
        self.y += ((mon[3] - H - 8 + self.foot_drop()) - self.y) * 0.2

    def update_living_cursor(self, now):
        if not self.living_mode or not IS_WIN or self.phone_mode:
            return
        point = wintypes.POINT()
        if not user32.GetCursorPos(ctypes.byref(point)):
            return
        position = (point.x, point.y)
        monotonic_now = time.monotonic()
        cursor_moved = position != self.last_cursor_position
        woke_up = False
        if cursor_moved:
            self.last_cursor_position = position
            self.last_cursor_move_at = monotonic_now
            if self.system_dozing:
                self.system_dozing = False
                woke_up = True
                self.say("Oh, du bist wieder da.", 3, speak=False)
        idle = self.system_idle_seconds()
        if idle is not None and idle >= 120 and not self.system_dozing:
            self.system_dozing = True
            self.cursor_attention_until = 0.0
        elif idle is not None and idle < 2 and self.system_dozing:
            self.system_dozing = False
            woke_up = True
            self.say("Oh, du bist wieder da.", 3, speak=False)
        elif idle is None and monotonic_now - self.last_cursor_move_at >= 120 and not self.system_dozing:
            self.system_dozing = True
            self.cursor_attention_until = 0.0
        center_x = self.x + self.display_width() / 2
        center_y = self.y + self.display_height() - 90
        dx, dy = point.x - center_x, point.y - center_y
        if (cursor_moved and not woke_up and dx * dx + dy * dy <= 155 ** 2
                and monotonic_now - self.last_cursor_reaction_at >= 10):
            self.cursor_look_dir = 1 if dx >= 0 else -1
            self.cursor_attention_until = now + 3.0
            self.cursor_pause_until = now + 1.5
            self.last_cursor_reaction_at = monotonic_now
            self.system_dozing = False
            self.say(random.choice(("Hab dich gesehen.", "Na, was machst du da?",
                                    "Ich passe auf.")), 3, speak=False)

    def system_idle_seconds(self):
        if not IS_WIN:
            return None
        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(info)
        if not user32.GetLastInputInfo(ctypes.byref(info)):
            return None
        now = kernel32.GetTickCount64() & 0xFFFFFFFF
        return ((now - info.dwTime) & 0xFFFFFFFF) / 1000

    # ================= Kisten (CS-Stil) =================
    def case_sfx(self, kind):
        """Ton ohne Mindestabstand (für das schnelle Ticken)."""
        if not self.sfx_enabled or self.quitting:
            return
        path = self.sfx_file(kind)
        if path:
            try:
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
            except (RuntimeError, OSError):
                pass

    def case_thumb(self, key, bg):
        cache = self.__dict__.setdefault("_case_th", {})
        if (key, bg) not in cache:
            ph, info = None, SHOP_IMG.get(key)
            if info and Image is not None and ImageTk is not None:
                try:
                    im = Image.open(io.BytesIO(info[0])).convert("RGBA")
                    im.thumbnail((60, 60))
                    base = Image.new("RGBA", im.size, bg)
                    base.alpha_composite(im)
                    ph = ImageTk.PhotoImage(base.convert("RGB"))
                except (OSError, ValueError):
                    ph = None
            cache[(key, bg)] = ph
        return cache[(key, bg)]

    def open_case_window(self):
        w = getattr(self, "case_win", None)
        try:
            if w is not None and w.winfo_exists():
                w.deiconify()
                w.lift()
                return
        except tk.TclError:
            pass
        load_shop_images()
        win = self.case_win = NovaToplevel(self.root)
        win.title("NOVA – Kisten")
        win.configure(bg=PANEL)
        win.geometry("640x380")
        win.protocol("WM_DELETE_WINDOW", self.close_case_window)
        self.case_busy, self.case_state, self.case_after = False, None, None
        self.case_sel = getattr(self, "case_sel", "basic")
        top = tk.Frame(win, bg=PANEL)
        top.pack(fill="x", padx=12, pady=(10, 4))
        self.case_pts = tk.Label(top, bg=PANEL, fg=LIGHT, font=("Consolas", 12, "bold"))
        self.case_pts.pack(side="right")
        self.case_btns = {}
        for k, (n, pr, ic, _) in CASES.items():
            b = nova_button(top, f"{ic} {n}\n{pr} Pkt", lambda k=k: self.case_select(k))
            b.pack(side="left", padx=(0, 6))
            self.case_btns[k] = b
        self.case_cv = tk.Canvas(win, width=616, height=CASE_TILE + 16, bg=PANEL2, highlightthickness=0)
        self.case_cv.pack(padx=12, pady=8)
        self.case_cv.bind("<Button-1>", lambda e: self.case_state and self.case_state.update(skip=True))
        self.case_odds = tk.Frame(win, bg=PANEL)
        self.case_odds.pack()
        self.case_res = tk.Label(win, bg=PANEL, fg=LIGHT, font=("Consolas", 11, "bold"), height=2)
        self.case_res.pack()
        self.case_open_btn = nova_button(win, "ÖFFNEN", self.case_open, primary=True, width=16)
        self.case_open_btn.pack(pady=(0, 8))
        self.case_select(self.case_sel)

    def case_select(self, k):
        if self.case_busy:
            return
        self.case_sel = k
        for n, b in self.case_btns.items():
            b.configure(bg=ACCENT if n == k else PANEL2, fg=PANEL if n == k else LIGHT)
        for ch in self.case_odds.winfo_children():
            ch.destroy()
        w = CASES[k][3]
        for (rid, name, col), x in zip(RARITIES, w):
            if x:
                tk.Label(self.case_odds, text=f"{name} {x / sum(w) * 100:.1f}%", bg=PANEL, fg=col,
                         font=("Consolas", 8, "bold")).pack(side="left", padx=4)
        self.case_pts.configure(text=f"{int(self.s['points'])} Pkt")
        pick = case_picker(k)
        self.case_build_reel([pick() for _ in range(8)])
        self.case_res.configure(text="Klick aufs Band = überspringen", fg=DIM)

    def case_build_reel(self, items):
        c, T = self.case_cv, CASE_TILE
        c.delete("all")
        for i, key in enumerate(items):
            col = RARITIES[rar_index(key)][2]
            x1, x2 = i * T + 3, (i + 1) * T - 3
            c.create_rectangle(x1, 8, x2, 8 + T, fill=PANEL, outline=col, width=2, tags=("reel", f"r{i}"))
            c.create_rectangle(x1, 8 + T - 8, x2, 8 + T, fill=col, outline="", tags="reel")
            ph = self.case_thumb(key, PANEL)
            if ph:
                c.create_image((x1 + x2) / 2, 8 + T / 2 - 8, image=ph, tags="reel")
            else:
                c.create_text((x1 + x2) / 2, 8 + T / 2 - 8, text=SHOP_ICONS.get(key, "🎁"),
                              font=("Segoe UI Emoji", 28), fill=LIGHT, tags="reel")
            c.create_text((x1 + x2) / 2, 8 + T - 18, text=SHOP_SHORT[key], font=("Consolas", 8, "bold"),
                          fill=LIGHT, tags="reel")
        cw = int(c["width"])
        c.create_line(cw / 2, 0, cw / 2, T + 16, fill="#ffd700", width=3, tags="mark")
        c.create_polygon(cw / 2 - 8, 0, cw / 2 + 8, 0, cw / 2, 10, fill="#ffd700", outline="", tags="mark")

    def case_open(self):
        if self.case_busy:
            return
        k = self.case_sel
        price = CASES[k][1]
        if self.s["points"] < price:
            self.case_res.configure(text=f"Dafür fehlen {price - int(self.s['points'])} Punkte.", fg=ACCENT)
            return
        self.s["points"] -= price
        pick = case_picker(k)
        N, WIN = 64, 52
        items = [pick() for _ in range(N)]
        items[WIN] = pick()
        cw = int(self.case_cv["width"])
        self.case_state = {"items": items, "win": WIN, "t0": time.monotonic(), "dur": 6.0, "pos": 0.0, "last": -1,
                           "target": WIN * CASE_TILE + CASE_TILE / 2 - cw / 2 + random.uniform(-0.4, 0.4) * CASE_TILE,
                           "cw": cw, "done": False}
        self.case_busy = True
        self.case_open_btn.configure(state="disabled")
        self.case_pts.configure(text=f"{int(self.s['points'])} Pkt")
        self.case_res.configure(text="…", fg=LIGHT)
        self.case_build_reel(items)
        self.case_step()

    def case_step(self):
        st = self.case_state
        if not st or st["done"]:
            return
        p = 1.0 if st.get("skip") else min(1.0, (time.monotonic() - st["t0"]) / st["dur"])
        pos = st["target"] * (1 - (1 - p) ** 4)
        self.case_cv.move("reel", st["pos"] - pos, 0)
        st["pos"] = pos
        tile = int((pos + st["cw"] / 2) // CASE_TILE)
        if tile != st["last"]:
            st["last"] = tile
            self.case_sfx("tick")
        if p >= 1.0:
            self.case_finish()
        else:
            self.case_after = self.case_win.after(16, self.case_step)

    def case_finish(self):
        st = self.case_state
        if not st or st["done"]:
            return
        st["done"] = True
        key = st["items"][st["win"]]
        name, price = SHOP[key]
        ri = rar_index(key)
        rname, rcol = RARITIES[ri][1], RARITIES[ri][2]
        if key in self.s["owned"]:
            back = price // 2
            self.s["points"] += back
            msg = f"{name} ({rname}) · Duplikat +{back} Pkt"
        else:
            self.s["owned"].append(key)
            self.s["worn"].append(key)
            msg = f"{name} ({rname}) · NEU!"
        try:
            self.case_cv.itemconfigure(f"r{st['win']}", outline="#ffffff", width=4)
            self.case_res.configure(text=msg, fg=rcol)
            self.case_pts.configure(text=f"{int(self.s['points'])} Pkt")
            self.case_open_btn.configure(state="normal")
        except tk.TclError:
            pass
        self.case_busy = False
        if ri >= 3:
            self.case_sfx("win")
        self.say(f"{name}! {rname}.", 4, speak=False)
        self.quest_event("buy")
        self.save()

    def close_case_window(self):
        if self.case_busy:
            self.case_finish()
        win, self.case_win = self.case_win, None
        try:
            win.destroy()
        except tk.TclError:
            pass

    # ================= Shop & Sprechblase =================
    def buy_or_toggle(self, key):
        """Kauft ein Accessoire einmalig; danach kostenlos an-/ablegen."""
        name, price = SHOP[key]
        if key in self.s["owned"]:
            if key in self.s["worn"]:
                self.s["worn"].remove(key)
            else:
                self.s["worn"].append(key)
            return
        if key in SHOP_PULL:
            self.say("Das gibt es nur aus Kisten!", 3, speak=False)
            return
        if self.s["points"] >= price:
            self.s["points"] -= price
            self.s["owned"].append(key)
            self.s["worn"].append(key)
            self.say(f"{name}! Steht mir, oder?", 4)
            self.quest_event("buy")
        else:
            self.say(f"Dafür fehlen {price - int(self.s['points'])} Punkte.", 4, speak=False)

    def _rotate_items(self, ids, ox, oy, th):
        """Dreht Canvas-Items um (ox, oy); Rechtecke/Ovale/Bögen werden zu Polygonen/Linien."""
        c = self.canvas
        co, si = math.cos(th), math.sin(th)

        def rot(pts):
            out = []
            for x, y in zip(pts[0::2], pts[1::2]):
                out += [ox + (x - ox) * co - (y - oy) * si, oy + (x - ox) * si + (y - oy) * co]
            return out

        for t in ids:
            kind = c.type(t)
            if kind not in ("polygon", "line", "rectangle", "oval", "arc"):
                continue
            cf = lambda o: c.itemcget(t, o)
            x = c.coords(t)
            if kind in ("polygon", "line"):
                c.coords(t, *rot(x))
                continue
            x1, y1, x2, y2 = x
            if kind == "rectangle":
                pts = [x1, y1, x2, y1, x2, y2, x1, y2]
                closed = True
            else:
                a0, ext = (0.0, 360.0) if kind == "oval" else (float(cf("start")), float(cf("extent")))
                mx, my, rx, ry = (x1 + x2) / 2, (y1 + y2) / 2, (x2 - x1) / 2, (y2 - y1) / 2
                n = 18
                pts = []
                for i in range(n + 1):
                    a = math.radians(a0 + ext * i / n)
                    pts += [mx + rx * math.cos(a), my - ry * math.sin(a)]
                closed = kind == "oval"
            fill, outline, width = cf("fill"), cf("outline"), float(cf("width") or 1)
            c.delete(t)
            if closed:
                c.create_polygon(*rot(pts), fill=fill, outline=outline, width=width, tags="acc")
            else:
                c.create_line(*rot(pts), fill=outline, width=width, tags="acc")

    # ---- Cosmetics fallen beim Wurf ab und fliegen mit Glitch zurück ----
    def acc_begin_fall(self, kick=0.0):
        if not self.s["worn"]:
            return
        old = getattr(self, "acc_off", {}) if getattr(self, "acc_phase", "worn") != "worn" else {}
        if self.acc_phase == "falling" and old:
            now = time.time()
            if not kick or now - getattr(self, "_acc_kick_t", 0.0) < 0.35:
                return                             # läuft schon / Kick nicht jeden Frame
            self._acc_kick_t = now
            for o in old.values():                 # Aufprall: Teile hüpfen nochmal hoch
                o[3] -= kick * random.uniform(0.6, 1.2)
                o[2] += random.uniform(-80, 80)
            return
        self.acc_off = {k: (old.get(k) or [0.0, 0.0, random.uniform(-90, 90), random.uniform(-260, -80)])
                        for k in self.s["worn"]}
        self.acc_phase, self._acc_t = "falling", time.time()

    def _acc_fx(self, c, marks):
        now = time.time()
        dt = min(0.05, max(0.0, now - self._acc_t))
        self._acc_t = now
        offs = self.acc_off
        if self.acc_phase == "falling":
            for key, o in offs.items():
                o[3] += 1100 * dt
                o[0] += o[2] * dt
                o[1] += o[3] * dt
                o[1] = max(o[1], -170.0)
                o[0] = max(-130.0, min(130.0, o[0]))
            if not (self.phys_active or self.dragging or self.fly_active()):
                self.acc_phase, self._acc_t0 = "returning", now
                self._acc_start = {k: [o[0], max(o[1], 160.0)] for k, o in offs.items()}
        if self.acc_phase == "returning":
            p = min(1.0, (now - self._acc_t0) / 0.8)
            q = (1 - p) ** 3
            if p >= 1.0:
                self.acc_phase, self.acc_off = "worn", {}
                return
        all_ids = c.find_withtag("acc")
        for n, (key, mid) in enumerate(marks):
            end = marks[n + 1][1] if n + 1 < len(marks) else 1 << 60
            ids = [t for t in all_ids if mid < t < end]
            if key not in offs or not ids:
                continue
            if self.acc_phase == "falling":
                ox, oy = offs[key][0], offs[key][1]
                glitch = False
            else:
                st = self._acc_start.get(key, [0.0, 160.0])
                ox, oy, glitch = st[0] * q, st[1] * q, True
                offs[key][0], offs[key][1] = ox, oy
            if glitch:
                ox += random.randint(-7, 7) * (1 - p) * 1.5
                if random.random() < 0.35 * (1 - p * 0.6):
                    for t in ids:
                        c.itemconfigure(t, state="hidden")
                    continue
            for t in ids:
                c.move(t, ox, oy)
            if not glitch:                         # Boden: liegen bleiben, kleiner Hüpfer
                boxes = [c.bbox(t) for t in ids if c.bbox(t)]
                gy = int(float(c.cget("height"))) - 5
                if boxes and max(b[3] for b in boxes) > gy:
                    over = max(b[3] for b in boxes) - gy
                    for t in ids:
                        c.move(t, 0, -over)
                    o = offs[key]
                    o[1] -= over
                    o[3] = -o[3] * 0.3 if o[3] > 150 else 0.0
                    o[2] *= 0.7
            if glitch:
                boxes = [c.bbox(t) for t in ids if c.bbox(t)]
                if boxes:
                    x1 = min(b[0] for b in boxes); y1 = min(b[1] for b in boxes)
                    x2 = max(b[2] for b in boxes); y2 = max(b[3] for b in boxes)
                    for _ in range(3):
                        gy = random.uniform(y1, y2)
                        c.create_rectangle(x1 - random.randint(0, 10), gy,
                                           x2 + random.randint(0, 10), gy + random.randint(1, 3),
                                           fill=random.choice((ACCENT, LIGHT)), outline="")

    # ---- Accessoires frei anordnen ----
    def start_acc_edit(self):
        if not self.s["worn"]:
            self.say("Erst ein Accessoire anlegen!", 3, speak=False)
            return
        self.acc_edit, self.acc_sel, self.acc_drag = True, None, None
        self.say("Zieh die Teile dahin, wo du sie willst.", 4, speak=False)

    def _acc_hit(self, x, y):
        k = self.accessory_scale()
        ids = self.canvas.find_overlapping(x - 4, y - 4, x + 4, y + 4)
        best = None
        for key, mid, end in getattr(self, "acc_ranges", []):
            if any(mid < t < end for t in ids):
                best = key
        return best

    def _acc_press(self, e):
        key = self._acc_hit(e.x, e.y)
        if not key:
            self.acc_edit = self.acc_drag = self.acc_sel = None
            self.save()
            self.say("Gespeichert.", 2, speak=False)
            return
        self.acc_sel = key
        self.acc_drag = (e.x, e.y)

    def _acc_motion(self, e):
        if not self.acc_drag or not self.acc_sel:
            return
        k = self.accessory_scale() or 1.0
        pos = self.s["acc_pos"].setdefault(self.acc_sel, [0.0, 0.0, 1.0])
        pos[0] += (e.x - self.acc_drag[0]) / k
        pos[1] += (e.y - self.acc_drag[1]) / k
        self.acc_drag = (e.x, e.y)

    def _acc_wheel(self, e):
        if not getattr(self, "acc_edit", False):
            return
        key = self.acc_sel or self._acc_hit(e.x, e.y)
        if not key:
            return
        up = getattr(e, "delta", 0) > 0 or getattr(e, "num", 0) == 4
        pos = self.s["acc_pos"].setdefault(key, [0.0, 0.0, 1.0])
        pos[2] = min(3.0, max(0.3, pos[2] * (1.08 if up else 0.92)))

    def _acc_reset(self, e):
        key = self._acc_hit(e.x, e.y)
        if key:
            self.s["acc_pos"].pop(key, None)
            self.save()

    def say(self, text, seconds=5, speak=True, ai_context=None):
        """Zeigt Text. Nur Idle-/Streichel-Sprüche werden durch KI-Zeilen ersetzt, beim Füttern
        wird die KI-Zeile ergänzt. Ergebnisse, Level-ups, Abschied usw. bleiben Originaltext."""
        if self.ai_radial_action_active:
            self.ai_radial_action_has_message = True
        use_ai = (ai_context is not None and speak and self._uses_ai_speech()
                  and not self.ai_voice_continuous)
        if use_ai:
            line = self._next_ai_speech(ai_context)
            if ai_context == "feed":
                self.bubble_text = self.personalize_text(text)
                self.bubble_until = time.time() + seconds
                if line:
                    if self.ai_radial_action_active:
                        self.ai_radial_action_spoke = True
                    self._display_ai_speech(line, seconds, preserve_bubble=True)
                return
            if line:
                if self.ai_radial_action_active:
                    self.ai_radial_action_spoke = True
                self._display_ai_speech(line, seconds)
                return
            # keine KI-Zeile verfügbar: Standardtext zeigen statt leerer Sprechblase
        self.bubble_text = self.personalize_text(text)
        self.bubble_until = time.time() + seconds
        if (speak and self.voice_enabled and not self.game_end and not self.ai_voice_busy
                and not self.ai_voice_continuous):
            self.speak_text(text)

    def say_random(self):
        if (self.ai_window is None and not self.ai_busy and not self.ai_voice_busy
                and not self.ai_voice_continuous and not self.sleeping
                and not self.system_dozing and not self.game_end and not self.spotify_mode):
            self.say(random.choice(QUOTES), 6, ai_context="idle")

    # ================= Maus =================
    def on_press(self, e):
        if self.fly_on:
            e = _Pt(e.x - self.fly_origin[0], e.y - self.fly_origin[1])
        if getattr(self, "acc_edit", False):
            self._acc_press(e)
            return
        if self.alarm_until:
            self.dismiss_alarm()
        if self.naming or self.feeding or self.prompt:
            self.grab_focus()
        if self.game_end and self.game_mode == "memory":
            self.hit_memory(e.x, e.y)
            return
        if self.game_end and self.game_mode in ("pong", "dodge"):
            return
        if self.game_end and self.game_mode == "jump":
            self.hit_jump_character(e.x, e.y)
            return
        if self.game_end and self.game_mode == "reflex":
            self.hit_reflex_target(e.x, e.y)
            return
        if self.game_end and self.hit_dot(e.x, e.y):
            return
        for x1, y1, x2, y2, path in getattr(self, "fav_rects", ()):
            if x1 <= e.x <= x2 and y1 <= e.y <= y2:
                self.launch_controlled_app(path)
                return
        key = self.music_button_at(e.x, e.y)
        if key:
            self.press_music_button(key)
            return
        self.dragging, self.off = True, (e.x, e.y)
        self.begin_grab()

    def on_double_click(self, e):
        """Zweiter schneller Klick: zählt im Spiel als normaler Klick, sonst Musik-Knopf oder Streicheln."""
        if self.game_end:
            self.on_press(e)
            return
        key = self.music_button_at(e.x, e.y)
        if key:
            self.press_music_button(key)
        else:
            self.pet()

    def check_shake(self, now):
        """Schnelles Hin-und-her-Ziehen (>= 4 Richtungswechsel in 0,9 s): Glitch + Spruch."""
        if len(self.drag_samples) < 2:
            return
        dx = self.drag_samples[-1][1] - self.drag_samples[-2][1]
        d = (dx > 6) - (dx < -6)
        if d and d != self.shake_dir:
            if self.shake_dir:
                self.shake_rev.append(now)
            self.shake_dir = d
        self.shake_rev = [t for t in self.shake_rev if now - t < 0.9]
        if len(self.shake_rev) >= 3:
            self.bump_until = time.time() + 0.3       # Glitch läuft, solange geschüttelt wird
            self.shake_until = time.time() + 0.5      # Luft-Bild
            if now > self.shake_cd:
                self.sfx_play("clink")
                if time.time() > self.bubble_until:
                    self.say(self.emotion_text("air") or random.choice(PHYS_SHAKE_LINES), 3, speak=False)
            self.acc_begin_fall()                     # Cosmetics fliegen beim Schütteln ab
            self.shake_cd = now + 1.5                 # Spruch erst wieder nach einer Pause

    def on_drag(self, e):
        if getattr(self, "acc_edit", False):
            self._acc_motion(e)
            return
        if self.dragging:
            self.x = self.root.winfo_pointerx() - self.off[0]
            self.y = self.root.winfo_pointery() - self.off[1]
            now = time.monotonic()
            self.drag_samples.append((now, self.x, self.y))
            while len(self.drag_samples) > 2 and now - self.drag_samples[0][0] > 0.12:
                self.drag_samples.pop(0)
            self.check_shake(now)
            if (not self.drag_moved
                    and math.hypot(self.x - self.drag_start[0], self.y - self.drag_start[1]) > 4):
                self.drag_moved = True         # wirklich gezogen: vom Fensterrand lösen
                if self.can_physics():
                    self.release_perch()

    def hit_dot(self, x, y):
        for d in self.dots:
            if (d["x"] - x) ** 2 + (d["y"] - y) ** 2 <= 16 ** 2:
                self.dots.remove(d)
                self.game_score += 1
                return True
        return False

    def hit_reflex_target(self, x, y):
        target = self.reflex_target
        if target and (target["x"] - x) ** 2 + (target["y"] - y) ** 2 <= target["r"] ** 2:
            now = time.time()
            reaction = now - target["born"]
            self.reflex_times.append(reaction)
            self.game_score += 1
            if reaction < 0.6:
                self.game_bonus += 1
            self.reflex_round += 1
            self.reflex_target = None
            self.reflex_next = now + random.uniform(0.45, 1.1)

    def hit_jump_character(self, x, y):
        """Trefferfläche = Ellipse um die tatsächlich gezeichnete Figur."""
        fh = self.figure_h()
        cy = H - 5 - fh / 2
        rx = max(30, fh * 0.2)
        dx, dy = (x - W / 2) / rx, (y - cy) / (fh / 2)
        if dx * dx + dy * dy <= 1:
            self.game_score += 1
            self.schedule_jump(time.time())

    # ================= Physik =================
    def can_physics(self):
        """Physik gilt in allen Modi außer Telefonmodus (und nicht während Minispielen/Beenden)."""
        return (self.physics_enabled and not self.phone_mode and not self.quitting
                and not self.game_end)

    def monitors(self):
        """Alle Bildschirme als (links, oben, rechts, unten, Arbeitsfläche-unten); kurz gepuffert."""
        now = time.monotonic()
        cached = getattr(self, "_mon_cache", None)
        if cached and now - cached[0] < 2.0:
            return cached[1]
        mons = []
        if IS_WIN:
            try:
                class MONITORINFO(ctypes.Structure):
                    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                                ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]

                proc_type = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
                                               ctypes.POINTER(wintypes.RECT), ctypes.c_void_p)

                def collect(hmon, hdc, rect, data):
                    info = MONITORINFO()
                    info.cbSize = ctypes.sizeof(MONITORINFO)
                    if user32.GetMonitorInfoW(ctypes.c_void_p(hmon), ctypes.byref(info)):
                        m, w = info.rcMonitor, info.rcWork
                        mons.append((m.left, m.top, m.right, m.bottom, w.bottom))
                    return 1

                callback = proc_type(collect)
                user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
                user32.GetMonitorInfoW.restype = wintypes.BOOL
                user32.EnumDisplayMonitors.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                                       proc_type, ctypes.c_void_p]
                user32.EnumDisplayMonitors.restype = wintypes.BOOL
                user32.EnumDisplayMonitors(None, None, callback, 0)
            except Exception:
                mons = []
        if not mons:
            mons = [(0, 0, self.sw, self.sh, self.sh - 48)]
        self._mon_cache = (now, mons)
        return mons

    def virtual_bounds(self):
        """Umgebendes Rechteck aller Bildschirme: (links, oben, rechts, unten)."""
        mons = self.monitors()
        return (min(m[0] for m in mons), min(m[1] for m in mons),
                max(m[2] for m in mons), max(m[3] for m in mons))

    def monitor_at(self, px, py):
        """Bildschirm, der den Punkt enthält (sonst der nächstgelegene)."""
        best, best_d = None, None
        for m in self.monitors():
            dx = max(m[0] - px, 0, px - m[2])
            dy = max(m[1] - py, 0, py - m[3])
            d = dx * dx + dy * dy
            if best_d is None or d < best_d:
                best, best_d = m, d
        return best

    def current_monitor(self):
        return self.monitor_at(self.x + W / 2, self.y + H / 2)

    def room_above(self, left, top, right):
        """Platz zwischen Bildschirmoberkante und einer Fensterkante (für NOVAs Höhe)."""
        mon = self.monitor_at((left + right) / 2, top)
        return top - mon[1]

    def ground_line(self):
        """Bildschirm-y der Standfläche: Arbeitsfläche (über der Taskleiste) des aktuellen Bildschirms."""
        return self.current_monitor()[4]

    def floor_y(self):
        """Fensterposition (oben), bei der NOVA auf dem Boden steht."""
        mon = self.current_monitor()
        if self.mini:
            return mon[3] - H - 8 + self.foot_drop()
        ground = mon[4] + self.s.get("ground_offset", 0)
        return ground - (H - 5) + self.foot_drop()

    def toggle_physics(self):
        self.physics_enabled = not self.physics_enabled
        self.s["physics"] = self.physics_enabled
        if not self.physics_enabled:
            if self.phys_active:
                self.returning = True          # mitten in der Luft: zurück auf den Boden gleiten
            self.phys_active = False
            self.vx = self.vy = 0.0
        self.save()
        self.say("Physik an: Wirf mich ruhig herum!" if self.physics_enabled
                 else "Physik aus: Ich bleibe, wo du mich hinlegst.", 4, speak=False)

    def release_perch(self):
        """Löst NOVA von einem Fensterrand."""
        self.perch_hwnd = None
        self.platform = None
        self.platform_hwnd = None
        self.small = False

    def begin_grab(self):
        """NOVA wird angefasst: Flug anhalten und Mausbewegung für den Wurf aufzeichnen."""
        self.ice_free = False
        self.grab_airborne = self.phys_active
        self.phys_active = False
        self.vx = self.vy = 0.0
        self.angle = self.spin = self.swing_v = 0.0
        self.drag_samples = []
        self.drag_moved = False
        self.drag_start = (self.x, self.y)

    def throw_velocity(self):
        """Wurfgeschwindigkeit (Pixel/s) aus den letzten ~0,1 s der Mausbewegung."""
        samples = self.drag_samples
        if len(samples) < 2 or time.monotonic() - samples[-1][0] > 0.08:
            return 0.0, 0.0                    # Maus lag still: sanft fallen lassen
        t0, x0, y0 = samples[0]
        t1, x1, y1 = samples[-1]
        span = t1 - t0
        if span < 0.015:
            return 0.0, 0.0
        vx, vy = (x1 - x0) / span, (y1 - y0) / span
        speed = math.hypot(vx, vy)
        if speed > PHYS_MAX_THROW:
            vx, vy = vx * PHYS_MAX_THROW / speed, vy * PHYS_MAX_THROW / speed
        return vx, vy

    def on_release(self, e=None):
        if getattr(self, "acc_edit", False):
            if self.acc_drag:
                self.acc_drag = None
                self.save()
            return
        if not self.dragging:
            return
        self.dragging = False
        if not self.can_physics():
            self.air_hold = False
            return
        if not self.drag_moved:                # nur geklickt, nicht gezogen
            if self.grab_airborne:
                self.start_physics(0.0, 0.0)   # mitten im Flug gefangen: weiterfallen
            return
        vx, vy = self.throw_velocity()
        if math.hypot(vx, vy) < 150:           # nur verschoben, kein Wurf: in der Luft stehen lassen
            if not self.try_drop_on_window():
                self.air_hold = True
            return
        self.start_physics(vx, vy)
        self.acc_begin_fall()
        if math.hypot(vx, vy) > 900:
            self.sfx_play("swish" if self.music_ice_active() else "whoosh")
        if math.hypot(vx, vy) > 900 and time.time() > self.bubble_until:
            self.say(self.emotion_text("air") or random.choice(PHYS_THROW_LINES), 3, speak=False)

    def can_rotate(self):
        """Drehen geht nur mit Bild (eine gezeichnete Figur lässt sich nicht drehen)."""
        return (self.physics_enabled and not self.phone_mode and not self.quitting
                and not self.game_end and Image is not None and self.art_key() is not None)

    def ease_upright(self, dt, rate=PHYS_UPRIGHT_RATE):
        """Richtet NOVA zur nächsten aufrechten Stellung auf (Vielfache von 360 Grad)."""
        target = round(self.angle / 360.0) * 360.0
        self.angle += (target - self.angle) * min(1.0, rate * dt)
        if abs(target - self.angle) < 0.6:
            self.angle = 0.0
            self.spin = 0.0

    def update_rotation(self, dt):
        """Zwischen den Flügen: Drehung zurücknehmen bzw. am Boden aufrichten."""
        if self.dragging:
            if self.can_rotate():
                self.update_swing(dt)
            else:
                self.angle = self.spin = 0.0
            return
        if self.angle == 0.0 and self.spin == 0.0:
            return
        if not self.can_rotate():
            self.angle = self.spin = 0.0
            return
        if not self.phys_active:
            self.spin = 0.0
            self.ease_upright(clamp(dt, 0.0, 0.05))

    def update_swing(self, dt):
        """Beim Ziehen/Schütteln hängt NOVA wie ein Pendel am Greifpunkt (Cursor)."""
        smp, v = self.drag_samples, 0.0
        if len(smp) >= 2 and time.monotonic() - smp[-1][0] < 0.1 and smp[-1][0] - smp[0][0] > 0.015:
            v = (smp[-1][1] - smp[0][1]) / (smp[-1][0] - smp[0][0])
        dt = clamp(dt, 0.01, 0.05)
        acc, self.swing_v = (v - self.swing_v) / dt, v
        self.spin = clamp(self.spin + (-PEND_K * self.angle - PEND_D * self.spin
                                       - PEND_IN * acc) * dt, -PHYS_SPIN_MAX, PHYS_SPIN_MAX)
        self.angle = clamp(self.angle + self.spin * dt, -PEND_MAX, PEND_MAX)

    def fly_active(self):
        if not self.can_rotate():
            return False
        now = time.time()
        if abs(self.angle) > 0.5:
            self._fly_t = now
            return True
        # Hysterese: beim Schütteln pendelt der Winkel um 0, nicht ständig das Fenster umschalten
        return self.fly_on and (self.dragging or now - self._fly_t < 0.3)

    def art_photo_rotated(self, key, height, direction, angle):
        """Gedrehtes Bild (Winkel auf 2 Grad gerundet, damit der Cache greift)."""
        q = int(round(angle / 2.0)) * 2 % 360
        ck = ("rot", key, height, direction >= 0, q)
        photo = self.frame_cache.get(ck)
        if photo is not None:
            self.frame_cache.move_to_end(ck)
            return photo
        base, mirrored = self.art_base(key, height)
        img = base if direction >= 0 else mirrored
        rotated = img.rotate(-q, resample=Image.BICUBIC, expand=True)
        alpha = rotated.getchannel("A").point(lambda v: 255 if v > 140 else 0)
        flat = Image.new("RGB", rotated.size, (1, 2, 3))
        flat.paste(rotated.convert("RGB"), (0, 0), alpha)
        photo = ImageTk.PhotoImage(flat)
        self.frame_cache[ck] = photo
        while len(self.frame_cache) > MAX_FRAME_CACHE:
            self.frame_cache.popitem(last=False)
        return photo

    def draw_fly_view(self):
        """Gedrehte NOVA in einem quadratischen Fenster, das um den Bildmittelpunkt liegt."""
        key = self.art_key()
        height = self.current_height()
        base, _ = self.art_base(key, height)
        size = int(math.hypot(base.width, base.height)) + 16
        size = max(size + size % 2, W)       # mind. so breit wie das Normalfenster (Textfelder)
        if self.fly_on:
            size = max(size, self.fly_size)   # nie schrumpfen: weniger Fenster-Resizes (Box-Blitzer)
        # Kopfraum wie im Normalfenster: Fenster nach oben verlängern, damit Textfelder/HUD
        # an derselben Stelle bleiben wie im Normalbetrieb (sonst rutschen sie auf den Sprite)
        extra = max(0, H - 5 - base.height // 2 - size // 2)
        if not self.fly_on or self.fly_size != size:
            self.canvas.configure(width=size, height=size + extra)
            self.fly_size = size
            self.fly_on = True
        direction = (self.cursor_look_dir
                     if time.time() < self.cursor_attention_until else self.dir)
        photo = self.art_photo_rotated(key, height, direction, self.angle)
        self._fly_photo = photo
        self.canvas.delete("all")
        self.canvas.create_image(size // 2, size // 2 + extra, image=photo)
        ng = len(self.canvas.find_all())
        self.draw_bump_glitch(time.time(), size // 2, size - 8, size - 16, size // 2 - 8)
        for item in self.canvas.find_all()[ng:]:
            self.canvas.move(item, 0, extra)
        c, n0, now = self.canvas, len(self.canvas.find_all()), time.time()
        if (self.hover or now < self.hud_until) and not self.mini and not self.naming and not self.prompt:
            self.shifted("hud_dy", self.draw_hud)
        self.shifted("bubble_dy", self.draw_bubble, now)
        dx = (size - W) // 2                 # Textfelder bleiben beim Schütteln/Werfen sichtbar
        # Textfelder an der Sprite-Oberkante halten (wie im Normalfenster), nie unter/außerhalb
        dy = 0                                   # Textfelder bleiben oben im Fenster (wie im Normalbetrieb)
        new_items = c.find_all()[n0:]
        for item in new_items:
            c.move(item, dx, dy)
        boxes = [c.bbox(i) for i in new_items if c.bbox(i)]
        if boxes:
            lift = 4 - min(b[1] for b in boxes)
            if lift > 0:
                for item in new_items:
                    c.move(item, 0, lift)
        for item in new_items:
            c.tag_raise(item)
        n1 = len(c.find_all())
        self.draw_accessories((size - base.height) // 2 + extra)
        new_acc = c.find_all()[n1:]
        if getattr(self, "acc_phase", "worn") == "worn" and abs(self.angle) > 0.5:
            self._rotate_items(new_acc, W // 2, size // 2 + extra, math.radians(self.angle))
            new_acc = c.find_all()[n1:]
        for item in new_acc:
            c.move(item, dx, 0)
        cx = self.x + W / 2
        cy = self.y + (H - 5) - base.height / 2
        if self.dragging:                  # Drehpunkt = Greifpunkt unter dem Cursor
            px, py = self.off[0] - W / 2, self.off[1] - (H - 5 - base.height / 2)
            a = math.radians(self.angle)
            cx = self.x + self.off[0] - (px * math.cos(a) - py * math.sin(a))
            cy = self.y + self.off[1] - (px * math.sin(a) + py * math.cos(a))
        left, top = int(round(cx - size / 2)), int(round(cy - size / 2))
        top -= extra
        self.fly_origin = (self.x - left, self.y - top)
        self._set_geometry(size, size + extra, left, top)

    def start_physics(self, vx, vy):
        self.air_hold = False
        self.release_perch()
        self.vx, self.vy = float(vx), float(vy)
        self.phys_active = True
        self.phys_decided = {}
        self.returning = False
        if self.can_rotate():
            self.spin = max(-PHYS_SPIN_MAX, min(PHYS_SPIN_MAX,
                            self.vx * (PHYS_ICE_SPIN if self.music_ice_active() else PHYS_SPIN_THROW)
                            + random.uniform(-40.0, 40.0)))

    def start_fall(self):
        """Lässt NOVA fallen (z. B. wenn ihr Fenster verschwindet). False, wenn Physik aus ist."""
        if not self.can_physics():
            return False
        self.air_hold = False
        self.phys_active = True
        self.phys_decided = {}
        self.small = False
        if self.can_rotate():
            self.spin = random.uniform(-60.0, 60.0)
        return True

    def drop_from_perch(self):
        self.release_perch()
        if not self.start_fall():
            self.returning = True

    def physics_windows(self, now):
        """Sichtbare Fenster als mögliche Landeplätze, von oben nach unten (kurz zwischengespeichert)."""
        if now - self.phys_win_time < 0.15:
            return self.phys_win_cache
        self.phys_win_time = now
        items = []
        if IS_WIN:
            try:
                own_pid = os.getpid()
                cloaked = wintypes.DWORD()
                dwm_attr = ctypes.windll.dwmapi.DwmGetWindowAttribute
                dwm_attr.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
                dwm_attr.restype = ctypes.c_long
                for hwnd, rect in self.visible_window_platforms():
                    pid = wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    if pid.value == own_pid:
                        continue
                    cloaked.value = 0
                    try:
                        if dwm_attr(hwnd, 14, ctypes.byref(cloaked), 4) == 0 and cloaked.value:
                            continue           # unsichtbares (gecloaktes) Fenster
                    except (OSError, AttributeError):
                        pass
                    full = wintypes.RECT()
                    if not user32.GetWindowRect(hwnd, ctypes.byref(full)):
                        continue
                    items.append((hwnd, rect, full.bottom))
            except Exception:
                items = []
        self.phys_win_cache = items
        return items

    def try_land_on_window(self, feet_old, feet_new, now):
        """Fällt NOVA durch eine Fensterkante, bleibt sie dort mit einer gewissen Wahrscheinlichkeit hängen."""
        if self.mini or not IS_WIN:
            return False
        center = self.x + W / 2
        min_top = self.min_platform_top()
        above = []                             # Fenster, die weiter oben in der z-Reihenfolge liegen
        hits = []
        for hwnd, rect, bottom in self.physics_windows(now):
            left, top, right = rect
            line = top + 6
            if (self.room_above(left, top, right) >= min_top
                    and left + 50 <= center <= right - 50
                    and feet_old <= line + 2 and feet_new >= line):
                py = top + 4
                covered = any(l <= center <= r and t <= py <= b for (l, t, r, b) in above)
                if not covered:
                    hits.append((top, hwnd, rect))
            above.append((left, top, right, bottom))
        if not hits:
            return False
        top, hwnd, rect = min(hits)
        decided = self.phys_decided.get(hwnd)
        if decided is None:                    # pro Sturz nur einmal pro Fenster würfeln
            decided = random.random() < PHYS_PERCH_CHANCE
            self.phys_decided[hwnd] = decided
        if not decided:
            return False
        self.land_on_window(hwnd, rect, now)
        return True

    def try_drop_on_window(self):
        """Losgelassen nahe einer Fensterkante (Füße ±40 px): bleibt direkt dort stehen."""
        if self.mini or not IS_WIN:
            return False
        now, center = time.time(), self.x + W / 2
        feet = self.y + H - 5 - self.foot_drop()
        min_top, above, hits = self.min_platform_top(), [], []
        for hwnd, rect, bottom in self.physics_windows(now):
            left, top, right = rect
            if (self.room_above(left, top, right) >= min_top and left + 50 <= center <= right - 50
                    and abs(feet - (top + 6)) <= 40
                    and not any(l <= center <= r and t <= top + 4 <= b for (l, t, r, b) in above)):
                hits.append((top, hwnd, rect))
            above.append((left, top, right, bottom))
        if not hits:
            return False
        _, hwnd, rect = min(hits)
        self.air_hold = False
        self.land_on_window(hwnd, rect, now)
        return True

    def land_on_window(self, hwnd, rect, now):
        self.sfx_play("land")
        self.vx = self.vy = 0.0
        self.spin = 0.0
        self.phys_active = False
        self.y = rect[1] - H + 11 + self.foot_drop()
        self.platform = rect
        self.platform_hwnd = hwnd
        self.perch_hwnd = None if self.living_mode else hwnd
        self.bump_until = time.time() + 0.35
        self.small = True
        if self.living_mode:
            self.next_window_hop = now + random.uniform(15, 30)
        if now > self.bubble_until:
            self.say(random.choice(PHYS_PERCH_LINES), 3, speak=False)

    def music_ice_active(self):
        """Musikmodus: Wurf = Rutschen wie auf Eis, ohne Schwerkraft (nicht im Mini-Modus)."""
        return self.music_active() and not self.mini

    def ice_hold(self):
        """NOVA liegt nach dem Rutschen frei im Bild und wird nicht zum Boden zurückgezogen."""
        return self.air_hold or (self.ice_free and self.music_ice_active())

    def update_ice(self, now, dt):
        """Gleitet reibungsarm über den Bildschirm und prallt sanft an den Rändern ab."""
        drag = math.exp(-PHYS_ICE_DRAG * dt)
        self.vx *= drag
        self.vy *= drag
        if self.can_rotate():
            self.angle += self.spin * dt
            self.spin *= math.exp(-1.2 * dt)
        self.x += self.vx * dt
        self.y += self.vy * dt
        if abs(self.vx) > 80:
            self.dir = 1 if self.vx > 0 else -1
        vl, vt, vr, vb = self.virtual_bounds()
        lo, hi = vl - PHYS_WALL_MARGIN, vr - W + PHYS_WALL_MARGIN
        floor = self.floor_y()
        hit = 0.0
        if self.x < lo:
            hit = abs(self.vx)
            self.x, self.vx = lo, abs(self.vx) * PHYS_ICE_BOUNCE
        elif self.x > hi:
            hit = abs(self.vx)
            self.x, self.vx = hi, -abs(self.vx) * PHYS_ICE_BOUNCE
        if self.y < vt:
            hit = max(hit, abs(self.vy))
            self.y, self.vy = float(vt), abs(self.vy) * PHYS_ICE_BOUNCE
        elif self.y > floor:
            hit = max(hit, abs(self.vy))
            self.y, self.vy = floor, -abs(self.vy) * PHYS_ICE_BOUNCE
        if hit > 200:
            self.bump_fx(hit)
        if hit > 350:
            self.sfx_play("clink", now=time.monotonic())
        if math.hypot(self.vx, self.vy) < PHYS_ICE_STOP:
            self.vx = self.vy = 0.0
            self.spin = 0.0
            self.phys_active = False
            self.ice_free = self.y < floor - 4

    # ---------- Soundeffekte ----------
    def sfx_file(self, kind):
        """WAV-Datei im Temp-Ordner (wird erst bei Bedarf erzeugt); None, wenn nicht möglich."""
        path = self.sfx_files.get(kind)
        if path is not None:
            return path
        if not IS_WIN or winsound is None or kind not in SFX_KINDS:
            return None
        try:
            if self.sfx_dir is None:
                self.sfx_dir = tempfile.mkdtemp(prefix="nova_sfx_")
                atexit.register(self.sfx_cleanup)
            path = os.path.join(self.sfx_dir, kind + ".wav")
            with open(path, "wb") as f:
                f.write(synth_sfx(kind))
        except OSError:
            return None
        self.sfx_files[kind] = path
        return path

    def sfx_cleanup(self):
        if winsound is not None:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except (RuntimeError, OSError):
                pass
        if self.sfx_dir:
            shutil.rmtree(self.sfx_dir, ignore_errors=True)
            self.sfx_dir, self.sfx_files = None, {}

    def sfx_play(self, kind, now=None):
        """Spielt einen kurzen, leisen Effekt. Begrenzt, damit es nie nervt."""
        if not self.sfx_enabled or self.phone_mode or self.quitting:
            return False
        now = time.monotonic() if now is None else now
        if (now - self.sfx_last < SFX_MIN_GAP
                or now - self.sfx_last_kind.get(kind, -99.0) < SFX_KIND_GAP):
            return False
        path = self.sfx_file(kind)
        if path is None:
            return False
        try:
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC
                               | winsound.SND_NODEFAULT)
        except (RuntimeError, OSError):
            return False
        self.sfx_last = now
        self.sfx_last_kind[kind] = now
        return True

    def sfx_impact(self, impact):
        """Boden-Aufprall: leise Aufpraller bleiben stumm, harte klingen dumpfer."""
        self.bump_fx(impact)
        if impact > 650:
            self.sfx_play("thud_hard" if impact > 1300 else "thud_soft")

    def bump_fx(self, speed):
        if speed > 200:
            self.bump_until = time.time() + 0.35

    def sfx_wall(self, speed):
        if speed > 250:
            self.acc_begin_fall(min(520, speed * 0.4))
        self.bump_fx(speed)
        if speed > 650:
            self.sfx_play("bump")

    # ---- Autostart (Windows, aktueller Benutzer) ----
    AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def _autostart_command(self):
        if getattr(sys, "frozen", False):                  # als EXE kompiliert
            return f'"{sys.executable}"'
        py = sys.executable
        pyw = os.path.join(os.path.dirname(py), "pythonw.exe")
        if os.path.isfile(pyw):
            py = pyw
        return f'"{py}" "{os.path.abspath(sys.argv[0])}"'

    def autostart_enabled(self):
        if not IS_WIN:
            return False
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.AUTOSTART_KEY) as key:
                return bool(winreg.QueryValueEx(key, "NOVA")[0])
        except OSError:
            return False

    def toggle_autostart(self):
        if not IS_WIN:
            self.say("Autostart gibt es nur unter Windows.", 4, speak=False)
            return
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.AUTOSTART_KEY, 0,
                                winreg.KEY_SET_VALUE) as key:
                if self.autostart_enabled():
                    winreg.DeleteValue(key, "NOVA")
                    self.say("Autostart aus.", 3, speak=False)
                else:
                    winreg.SetValueEx(key, "NOVA", 0, winreg.REG_SZ, self._autostart_command())
                    self.say("Autostart an: NOVA startet mit Windows.", 4, speak=False)
        except OSError as err:
            self.say(f"Autostart fehlgeschlagen: {err}", 5, speak=False)

    def toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled
        self.s["sfx"] = self.sfx_enabled
        self.save()
        self.say("Soundeffekte an." if self.sfx_enabled else "Soundeffekte aus.", 3, speak=False)
        if self.sfx_enabled:
            self.sfx_play("thud_soft")

    def update_physics(self, now, dt):
        """Schwerkraft, Abprallen an Wänden/Decke/Boden und Landung auf Fenstern."""
        if self.dragging or not self.physics_enabled or self.phone_mode:
            self.phys_active = False
            return
        if self.game_end:
            self.vx = self.vy = 0.0            # Minispiel läuft: einfrieren, danach weiterfallen
            return
        dt = clamp(dt, 0.0, 0.05)
        if dt <= 0:
            return
        if self.music_ice_active():
            self.update_ice(now, dt)               # Musikmodus: Rutschen statt Fallen
            return
        self.vy = min(PHYS_MAX_FALL, self.vy + PHYS_GRAVITY * dt)
        self.vx *= math.exp(-PHYS_AIR_DRAG * dt)
        drop = self.foot_drop()
        if self.can_rotate():
            self.angle += self.spin * dt
            self.spin *= math.exp(-PHYS_SPIN_DRAG * dt)
        feet_old = self.y + H - 5 - drop
        self.x += self.vx * dt
        self.y += self.vy * dt
        if abs(self.vx) > 80:
            self.dir = 1 if self.vx > 0 else -1
        vl, vt, vr, vb = self.virtual_bounds()       # Wände = Außenkanten aller Bildschirme
        lo, hi = vl - PHYS_WALL_MARGIN, vr - W + PHYS_WALL_MARGIN
        if self.x < lo:
            self.sfx_wall(abs(self.vx))
            self.x, self.vx = lo, abs(self.vx) * PHYS_WALL_BOUNCE
            self.spin = -self.spin * 0.7
        elif self.x > hi:
            self.sfx_wall(abs(self.vx))
            self.x, self.vx = hi, -abs(self.vx) * PHYS_WALL_BOUNCE
            self.spin = -self.spin * 0.7
        vt -= max(0, H - 5 - self.figure_h())      # Decke = Kopf des Sprites, nicht der leere Fensterrand
        if self.y < vt:
            self.sfx_wall(abs(self.vy))
            self.y, self.vy = float(vt), abs(self.vy) * PHYS_WALL_BOUNCE
            self.spin = -self.spin * 0.7
        if self.vy > 0 and self.try_land_on_window(feet_old, self.y + H - 5 - drop, now):
            return
        floor = self.floor_y()
        if self.y >= floor:
            impact = self.vy
            self.y = floor
            self.phys_decided = {}             # nach einem Aufprall gibt es neue Chancen auf Fenster
            if impact > PHYS_REST_SPEED:
                self.sfx_impact(impact)
                self.vy = -impact * PHYS_FLOOR_BOUNCE
                self.vx *= 0.85
                if self.can_rotate():
                    self.spin = (self.spin * 0.5 + random.uniform(-1.0, 1.0)
                                 * min(impact, 2000.0) * PHYS_SPIN_BOUNCE)
                if impact > 1100:
                    self.teleport_until = now + 0.3          # kurzer Glitch beim harten Aufprall
                    if now > self.bubble_until:
                        self.say(random.choice(PHYS_HIT_LINES), 3, speak=False)
            else:
                self.vy = 0.0
                self.spin = 0.0
                self.ease_upright(dt)
                self.vx *= math.exp(-PHYS_FLOOR_FRICTION * dt)
                if abs(self.vx) < 15.0:
                    self.vx = 0.0
                    self.phys_active = False

    # ================= Spielwerte =================
    def update_stats(self, dt, now):
        s = self.s
        if self.sleeping:
            s["energy"] = clamp(s["energy"] + SLEEP_REGEN * dt)
            rate = 0.5
            if s["energy"] >= 95:
                self.sleeping = False
                self.say("Ausgeschlafen!", 4)
        else:
            s["energy"] = clamp(s["energy"] - DECAY["energy"] * dt)
            rate = 1.0
            if s["energy"] <= 3:
                self.sleeping = True
                self.cancel_game()
                self.say("Mir fallen die Augen zu... Zzz", 4)
        s["food"] = clamp(s["food"] - DECAY["food"] * rate * dt)
        s["fun"] = clamp(s["fun"] - DECAY["fun"] * rate * dt)

        if now - self.last_bonus >= 60:
            self.last_bonus = now
            if min(s["food"], s["fun"], s["energy"]) >= 40:
                self.add_points(1)
        if not self.sleeping and now - self.last_need >= 120 and now > self.bubble_until:
            worst = min(("food", "fun", "energy"), key=lambda k: s[k])
            if s[worst] < 25:
                self.last_need = now
                self.say(NEED_LINES[worst], 6)
        if now - self.last_save >= 30:
            self.last_save = now
            self.save()

    # ================= Zeichnen =================
    def air_floor(self):
        """Boden fürs Luft-Erkennen, unabhängig vom aktuellen Bild (Normal- und Luft-Bild haben
        verschiedene Fußlinien; sonst schaltet das Bild den Boden um und flackert)."""
        mon = self.current_monitor()
        drop = 0
        if not (self.phone_mode or self.art_key() is None or self.music_visible()):
            pct = min(self.s.get("foot_pct", 0.0), self.s.get("foot_air", 0.0))
            drop = int(round(self.figure_h() * pct / 100.0))
        if self.mini:
            return mon[3] - H - 8 + drop
        return mon[4] + self.s.get("ground_offset", 0) - (H - 5) + drop

    def air_pose(self):
        """Luft-Bild: geschüttelt, in der Luft abgelegt oder im Wurf (nicht beim Eis-Rutschen)."""
        if (self.phone_mode or "air" not in self.emotion_sources
                or self.game_end or self.quitting):
            return False
        now = time.time()
        if now < self.shake_until:
            self._air_t = now
            return True
        if self.music_ice_active():
            return False
        if self.air_hold or (self.phys_active and self.y < self.air_floor() - 8):
            self._air_t = now
            return True
        return now - self._air_t < 0.18      # Hysterese: kein Flackern bei kleinen Aufprallen

    def airborne(self):
        """Frei in der Luft: abgelegt (air_hold) oder weder auf Boden noch auf Fenster."""
        return self.air_hold or (self.physics_enabled and not self.mini and not self.phys_active
                                 and self.platform is None and self.perch_hwnd is None
                                 and not self.music_visible() and self.y < self.air_floor() - 8)

    def moving(self):
        return (self.walking and not self.dragging and not self.sleeping and not self.mini
                and not self.system_dozing and time.time() >= self.cursor_pause_until
                and not self.phone_mode and self.radial_window is None and not self.quitting
                and not (self.game_end and self.game_mode == "jump")
                and not self.music_visible() and not self.phys_active and not self.airborne()
                and not (self.game_end and self.game_mode in STATIC_GAMES))

    def draw_character(self, top, base):
        c = self.canvas
        cx = W // 2
        key = self.art_key()
        if key is not None:
            moving = self.moving()
            phase = 0 if self.airborne() else int(self.t * (0.6 if moving else 0.3)) % FRAMES
            direction = (self.cursor_look_dir
                         if time.time() < self.cursor_attention_until else self.dir)
            photo = self.art_photo(key, self.current_height(), phase, moving, direction)
            c.create_image(cx, base, image=photo, anchor="s")
            if self.show_foot_line:
                line_y = base - (self.sit_drop() if self.music_visible() else self.foot_drop())
                c.create_line(cx - 90, line_y, cx + 90, line_y, fill=LIGHT, width=2, dash=(6, 4))
            return
        step = math.sin(self.t * 0.4) * 8 if self.moving() else 0
        c.create_rectangle(cx - 22, base - 50, cx - 8, base - 5 + step, fill=PANEL2, outline=ACCENT)
        c.create_rectangle(cx + 8, base - 50, cx + 22, base - 5 - step, fill=PANEL2, outline=ACCENT)
        c.create_rectangle(cx - 32, base - 120, cx + 32, base - 50, fill="#241012", outline=EDGE, width=2)
        c.create_line(cx - 20, base - 105, cx + 20, base - 105, fill=ACCENT, width=2)
        c.create_rectangle(cx - 46, base - 118, cx - 32, base - 65, fill=PANEL2, outline=ACCENT)
        c.create_rectangle(cx + 32, base - 118, cx + 46, base - 65, fill=PANEL2, outline=ACCENT)
        c.create_rectangle(cx - 28, base - 175, cx + 28, base - 122, fill="#2e1215", outline=ACCENT, width=2)
        glow = ACCENT if int(self.t / 10) % 2 == 0 else LIGHT
        c.create_line(cx + 14, base - 175, cx + 20, base - 195, fill=ACCENT, width=2)
        c.create_oval(cx + 16, base - 201, cx + 26, base - 191, fill=glow, outline="")
        closed = self.sleeping or time.time() < self.blink_until
        eye_h = 2 if closed else 12
        look_dir = (self.cursor_look_dir
                    if time.time() < self.cursor_attention_until else self.dir)
        look = 0 if self.sleeping else 6 * look_dir
        c.create_rectangle(cx - 22, base - 158, cx + 22, base - 138, fill="#000", outline=EDGE)
        for ox in (-16, 6):
            c.create_rectangle(cx + ox + look, base - 148 - eye_h // 2,
                               cx + ox + 10 + look, base - 148 + eye_h // 2, fill=ACCENT, outline="")
        k = self.drawn_scale()
        if k != 1.0:
            c.scale("all", cx, base, k, k)

    def draw_air_glitch(self, base):
        """In der Luft stehen gelassen: NOVA regt sich nicht, unter den Füßen flackert Glitch."""
        if not self.airborne() or self.phone_mode:
            return
        c, cx = self.canvas, W // 2
        y0 = base - self.foot_drop()
        for i in range(7):
            y = y0 + 2 + i * 3 + random.randint(-1, 1)
            w = random.randint(14, 70)
            off = random.randint(-30, 30)
            col = random.choice((ACCENT, ACCENT, EDGE, "#a64dff", "#3d8bff", LIGHT))
            if random.random() < 0.8:
                c.create_line(cx - w + off, y, cx + w + off, y, fill=col, width=random.choice((1, 2)))
        if random.random() < 0.5:
            x = cx + random.randint(-50, 50)
            c.create_rectangle(x, y0 + 4, x + random.randint(4, 14), y0 + random.randint(8, 20),
                               fill=ACCENT, outline="")

    def draw_bump_glitch(self, now, cx, base, h, wmax=60):
        """Kurzer Glitch am ganzen Körper nach dem Anstoßen: Rot, etwas Lila und Blau."""
        if now >= self.bump_until or self.phone_mode:
            return
        c = self.canvas
        cols = (ACCENT, ACCENT, ACCENT, "#a64dff", "#3d8bff", LIGHT)
        for _ in range(9):
            y = base - random.randint(0, int(h))
            w = random.randint(12, wmax)
            off = random.randint(-28, 28)
            c.create_line(cx - w + off, y, cx + w + off, y, fill=random.choice(cols),
                          width=random.choice((1, 2, 3)))

    def draw_glitch_effect(self, now):
        if now >= self.teleport_until:
            return
        progress = self.teleport_until - now
        for i in range(5):
            y = H - 185 + ((i * 37 + self.t * 11) % 120)
            offset = ((self.t * 17 + i * 29) % 25) - 12
            width = 24 + ((self.t + i * 13) % 48)
            self.canvas.create_line(
                W // 2 - width + offset, y, W // 2 + width + offset, y,
                fill=LIGHT if (self.t + i) % 3 == 0 else ACCENT,
                width=1 if progress < 0.25 else 2)

    def draw_phone_view(self, now):
        c = self.canvas
        c.create_rectangle(6, 6, PHONE_SIZE - 6, PHONE_SIZE - 6,
                           fill=PANEL2, outline=ACCENT, width=3)
        speaking = now <= self.bubble_until and bool(self.bubble_text)
        photo = self.phone_mode_photo(speaking=speaking)
        if photo is not None:
            c.create_image(PHONE_SIZE // 2, PHONE_SIZE // 2, image=photo)
        else:
            cx = PHONE_SIZE // 2
            c.create_rectangle(cx - 48, 82, cx + 48, 142,
                               fill="#2e1215", outline=ACCENT, width=2)
            c.create_rectangle(cx - 58, 145, cx + 58, 220,
                               fill=PANEL2, outline=EDGE, width=2)
            c.create_rectangle(cx - 28, 102, cx - 10, 112, fill=ACCENT, outline="")
            c.create_rectangle(cx + 10, 102, cx + 28, 112, fill=ACCENT, outline="")
        c.create_rectangle(21, 21, PHONE_SIZE - 21, PHONE_SIZE - 21,
                           outline=EDGE, width=1)
        self.draw_music_box(now)
        self.draw_tool_chips(now, 0)
        self.draw_alarm(now)
        display_name = (self.s.get("name") or "").strip() or "NOVA"
        c.create_text(PHONE_SIZE // 2, 13, text=display_name, fill=LIGHT,
                      font=("Consolas", 7, "bold"))
        footer_txt = (f"CPU {int(self.cpu_percent)}% · RAM {int(self.ram_percent)}%"
                      if self.sys_monitor else "TELEFONMODUS")
        c.create_text(PHONE_SIZE // 2, PHONE_SIZE - 13, text=footer_txt,
                      fill=ACCENT if (self.sys_monitor and max(self.cpu_percent, self.ram_percent) >= 85) else LIGHT,
                      font=("Consolas", 7, "bold"))
        if now <= self.bubble_until and self.bubble_text:
            text = self.bubble_text.replace("\n", " ")[:64]
            c.create_rectangle(22, PHONE_SIZE - 54, PHONE_SIZE - 22, PHONE_SIZE - 30,
                               fill=PANEL, outline=ACCENT)
            c.create_text(PHONE_SIZE // 2, PHONE_SIZE - 42, text=text,
                          width=PHONE_SIZE - 54, fill=LIGHT,
                          font=("Consolas", 7, "bold"))

    def draw_accessories(self, top):
        """Zeichnet angelegte Shop-Accessoires; in Klein/Mini werden sie mit verkleinert."""
        if self.music_visible():                   # Musikmodus: keine Cosmetics
            self.acc_ranges = []
            return
        c = self.canvas
        cx = W // 2
        worn = self.s["worn"]
        marks = []
        if "halo" in worn:
            marks.append(("halo", c.create_text(0, 0, text="", tags="acc")))
            c.create_oval(cx - 26, top - 24, cx + 26, top - 8, outline=LIGHT, width=3, tags="acc")
        if "cap" in worn:
            marks.append(("cap", c.create_text(0, 0, text="", tags="acc")))
            c.create_rectangle(cx - 26, top - 8, cx + 26, top + 8, fill=PANEL2, outline=ACCENT,
                               width=2, tags="acc")
            c.create_rectangle(cx + 10, top + 4, cx + 42, top + 10, fill=ACCENT, outline="", tags="acc")
        if "crown" in worn:
            marks.append(("crown", c.create_text(0, 0, text="", tags="acc")))
            c.create_polygon(cx - 24, top + 8, cx - 24, top - 14, cx - 12, top - 2, cx, top - 20,
                             cx + 12, top - 2, cx + 24, top - 14, cx + 24, top + 8,
                             fill="#c4122f", outline=ACCENT, width=2, tags="acc")
        if "visor" in worn:
            marks.append(("visor", c.create_text(0, 0, text="", tags="acc")))
            c.create_polygon(cx - 30, top + 27, cx + 30, top + 27, cx + 24, top + 43,
                             cx - 24, top + 43, fill="#1a0206", outline=ACCENT, width=2, tags="acc")
            c.create_line(cx - 18, top + 31, cx + 18, top + 31, fill=LIGHT, width=2, tags="acc")
        if "scarf" in worn:
            marks.append(("scarf", c.create_text(0, 0, text="", tags="acc")))
            c.create_polygon(cx - 28, top + 68, cx + 28, top + 68, cx + 21, top + 84,
                             cx - 21, top + 84, fill=EDGE, outline=ACCENT, width=2, tags="acc")
            c.create_polygon(cx + 12, top + 80, cx + 27, top + 78, cx + 31, top + 111,
                             cx + 18, top + 105, fill="#c4122f", outline=EDGE, width=2, tags="acc")
        if "wings" in worn:
            marks.append(("wings", c.create_text(0, 0, text="", tags="acc")))
            c.create_polygon(cx - 27, top + 79, cx - 46, top + 57, cx - 79, top + 62,
                             cx - 59, top + 82, cx - 76, top + 96, cx - 39, top + 96,
                             fill="#1a0b0d", outline=ACCENT, width=2, tags="acc")
            c.create_polygon(cx + 27, top + 79, cx + 46, top + 57, cx + 79, top + 62,
                             cx + 59, top + 82, cx + 76, top + 96, cx + 39, top + 96,
                             fill="#1a0b0d", outline=EDGE, width=2, tags="acc")
        if "headset" in worn:
            marks.append(("headset", c.create_text(0, 0, text="", tags="acc")))
            c.create_arc(cx - 36, top + 2, cx + 36, top + 66, start=0, extent=180,
                         style=tk.ARC, outline=ACCENT, width=4, tags="acc")
            c.create_rectangle(cx - 39, top + 27, cx - 27, top + 54, fill=PANEL2, outline=EDGE,
                               width=2, tags="acc")
            c.create_rectangle(cx + 27, top + 27, cx + 39, top + 54, fill=PANEL2, outline=EDGE,
                               width=2, tags="acc")
        if "tophat" in worn:
            marks.append(("tophat", c.create_text(0, 0, text="", tags="acc")))
            c.create_rectangle(cx - 30, top - 4, cx + 30, top + 4, fill=PANEL2, outline=ACCENT, width=2, tags="acc")
            c.create_rectangle(cx - 19, top - 34, cx + 19, top - 4, fill=PANEL2, outline=ACCENT, width=2, tags="acc")
            c.create_rectangle(cx - 19, top - 14, cx + 19, top - 7, fill="#c4122f", outline="", tags="acc")
        if "ears" in worn:
            marks.append(("ears", c.create_text(0, 0, text="", tags="acc")))
            c.create_polygon(cx - 30, top + 12, cx - 26, top - 14, cx - 8, top + 2,
                             fill=PANEL2, outline=ACCENT, width=2, tags="acc")
            c.create_polygon(cx + 30, top + 12, cx + 26, top - 14, cx + 8, top + 2,
                             fill=PANEL2, outline=ACCENT, width=2, tags="acc")
        if "antenna" in worn:
            marks.append(("antenna", c.create_text(0, 0, text="", tags="acc")))
            c.create_line(cx, top + 2, cx + 4, top - 26, fill=ACCENT, width=3, tags="acc")
            c.create_oval(cx - 2, top - 34, cx + 10, top - 22, fill=LIGHT, outline=ACCENT, width=2, tags="acc")
        if "glasses" in worn:
            marks.append(("glasses", c.create_text(0, 0, text="", tags="acc")))
            for gx in (-15, 15):
                c.create_oval(cx + gx - 10, top + 24, cx + gx + 10, top + 44, outline=LIGHT, width=3, tags="acc")
            c.create_line(cx - 5, top + 33, cx + 5, top + 33, fill=LIGHT, width=3, tags="acc")
        if "mustache" in worn:
            marks.append(("mustache", c.create_text(0, 0, text="", tags="acc")))
            c.create_polygon(cx - 22, top + 52, cx - 6, top + 46, cx, top + 50, cx + 6, top + 46,
                             cx + 22, top + 52, cx + 10, top + 58, cx, top + 54, cx - 10, top + 58,
                             fill="#2a0d12", outline=ACCENT, width=2, tags="acc")
        if "mask" in worn:
            marks.append(("mask", c.create_text(0, 0, text="", tags="acc")))
            c.create_polygon(cx - 27, top + 46, cx + 27, top + 46, cx + 21, top + 68, cx - 21, top + 68,
                             fill=PANEL2, outline=ACCENT, width=2, tags="acc")
            for lx in (-12, 0, 12):
                c.create_line(cx + lx, top + 50, cx + lx, top + 64, fill=EDGE, width=2, tags="acc")
        if "bowtie" in worn:
            marks.append(("bowtie", c.create_text(0, 0, text="", tags="acc")))
            c.create_polygon(cx, top + 78, cx - 20, top + 68, cx - 20, top + 88,
                             fill="#c4122f", outline=ACCENT, width=2, tags="acc")
            c.create_polygon(cx, top + 78, cx + 20, top + 68, cx + 20, top + 88,
                             fill="#c4122f", outline=ACCENT, width=2, tags="acc")
            c.create_oval(cx - 5, top + 73, cx + 5, top + 83, fill=ACCENT, outline="", tags="acc")
        if "chain" in worn:
            marks.append(("chain", c.create_text(0, 0, text="", tags="acc")))
            c.create_arc(cx - 26, top + 54, cx + 26, top + 102, start=200, extent=140,
                         style=tk.ARC, outline=LIGHT, width=3, tags="acc")
            c.create_polygon(cx, top + 96, cx - 7, top + 104, cx, top + 114, cx + 7, top + 104,
                             fill=ACCENT, outline=LIGHT, width=2, tags="acc")
        if "cape" in worn:
            marks.append(("cape", c.create_text(0, 0, text="", tags="acc")))
            c.create_polygon(cx - 30, top + 72, cx - 52, top + 135, cx - 14, top + 128,
                             fill="#8a0f22", outline=ACCENT, width=2, tags="acc")
            c.create_polygon(cx + 30, top + 72, cx + 52, top + 135, cx + 14, top + 128,
                             fill="#8a0f22", outline=EDGE, width=2, tags="acc")
        if "backpack" in worn:
            marks.append(("backpack", c.create_text(0, 0, text="", tags="acc")))
            c.create_rectangle(cx + 28, top + 78, cx + 52, top + 118, fill=PANEL2, outline=ACCENT, width=2, tags="acc")
            c.create_rectangle(cx + 32, top + 98, cx + 48, top + 112, outline=EDGE, width=2, tags="acc")
        for key, (path, ix, iy, iw) in SHOP_IMG.items():
            if key not in worn or Image is None or ImageTk is None:
                continue
            sc = (self.s["acc_pos"].get(key) or (0, 0, 1.0))[2]
            ck = (key, round(sc, 2))
            cache = self.__dict__.setdefault("_shop_ph", {})
            if ck not in cache:
                try:
                    im = Image.open(io.BytesIO(path)).convert("RGBA")
                    r = iw * sc / im.width
                    im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
                    cache[ck] = (self._flat_photo(im), self._flat_photo(ImageOps.mirror(im)))
                except (OSError, ValueError):
                    cache[ck] = None
            if not cache[ck]:
                continue
            marks.append((key, c.create_text(0, 0, text="", tags="acc")))
            c.create_image(cx + ix, top + iy, image=cache[ck][0], tags=("acc", "shopimg", key))
        for key, shapes in SHOP_DRAW.items():
            if key not in worn:
                continue
            marks.append((key, c.create_text(0, 0, text="", tags="acc")))
            for kind, co, fill, line, wd in shapes:
                pts = [cx + v if i % 2 == 0 else top + v for i, v in enumerate(co)]
                if kind == "l":
                    c.create_line(*pts, fill=line, width=wd, tags="acc")
                else:
                    make = {"p": c.create_polygon, "o": c.create_oval, "r": c.create_rectangle}[kind]
                    make(*pts, fill=fill, outline=line, width=wd, tags="acc")
        self.acc_ranges = []
        mirrored, walk_dx, walk_dy, lean = False, 0, 0, 0.0
        if marks and not getattr(self, "acc_edit", False) and self.art_key() is not None:
            direction = (self.cursor_look_dir
                         if time.time() < self.cursor_attention_until else self.dir)
            mirrored = direction < 0
            moving = self.moving()
            ph = 0 if self.airborne() else int(self.t * (0.6 if moving else 0.3)) % FRAMES
            pa = 2 * math.pi * ph / FRAMES
            sway = math.sin(pa)
            if moving:
                st = (1 - math.cos(2 * pa)) / 2
                walk_dy, walk_dx = -round(1 + 3 * st), round(sway * 2)
                lean = math.radians(direction * 2.5 + sway * 1.8)
            else:
                walk_dy, walk_dx = -round((1 + sway) / 2), round(sway * 0.7)
                lean = math.radians(sway * 0.8)
            if mirrored:
                c.scale("acc", cx, 0, -1, 1)
                for t in c.find_withtag("shopimg"):
                    key = c.gettags(t)[2]
                    x, y = c.coords(t)
                    c.coords(t, 2 * cx - x, y)
                    ck = (key, round((self.s["acc_pos"].get(key) or (0, 0, 1.0))[2], 2))
                    c.itemconfigure(t, image=self._shop_ph[ck][1])
        all_ids = c.find_withtag("acc") if marks else ()
        for n, (key, mid) in enumerate(marks):
            end = marks[n + 1][1] if n + 1 < len(marks) else 1 << 60
            self.acc_ranges.append((key, mid, end))
            pos = self.s["acc_pos"].get(key)
            if not pos:
                continue
            ids = [t for t in all_ids if mid < t < end]
            if not ids:
                continue
            dx, dy, sc = pos
            if mirrored:
                dx = -dx
            boxes = [c.bbox(t) for t in ids]
            boxes = [b for b in boxes if b]
            if sc != 1.0 and boxes:
                mx = (min(b[0] for b in boxes) + max(b[2] for b in boxes)) / 2
                my = (min(b[1] for b in boxes) + max(b[3] for b in boxes)) / 2
                for t in ids:
                    c.scale(t, mx, my, sc, sc)
            for t in ids:
                c.move(t, dx, dy)
        if marks and (walk_dx or walk_dy or lean):
            base_y = top + self.figure_h()
            for n, (key, mid) in enumerate(marks):
                end = marks[n + 1][1] if n + 1 < len(marks) else 1 << 60
                gids = [t for t in all_ids if mid < t < end]
                boxes = [c.bbox(t) for t in gids]
                boxes = [b for b in boxes if b]
                lean_x = 0.0
                if boxes and lean:
                    lean_x = (base_y - (min(b[1] for b in boxes) + max(b[3] for b in boxes)) / 2
                              - self.figure_h() / 2) * math.sin(lean)   # Drehpunkt = Bildmitte
                for t in gids:
                    c.move(t, walk_dx + lean_x, walk_dy)
        k = self.accessory_scale()
        if k != 1.0:
            c.scale("acc", cx, top + 8, k, k)
        if getattr(self, "acc_phase", "worn") != "worn":
            self._acc_fx(c, marks)
        if getattr(self, "acc_edit", False):
            c.create_text(cx, top - 30, text="ANORDNEN: ziehen · Mausrad = Größe · Rechtsklick = Reset · Leerklick = fertig",
                          fill=LIGHT, font=("Consolas", 7, "bold"), width=W - 20)

    def draw_ai_orb(self, top):
        if not self.ai_enabled:
            return
        x = W - 21
        y = top + 20
        radius = 7 + round(1.5 * (1 + math.sin(self.t * 0.12)))
        self.canvas.create_oval(
            x - radius - 4, y - radius - 4, x + radius + 4, y + radius + 4,
            fill="", outline=EDGE, width=2,
        )
        self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=ACCENT, outline=LIGHT, width=1,
        )
        self.canvas.create_oval(
            x - 3, y - 3, x + 1, y + 1, fill=LIGHT, outline="",
        )

    def draw_status_marks(self, top):
        c = self.canvas
        cx = W // 2
        if self.sleeping or self.system_dozing:
            off = (self.t % 60) / 6
            for i, size in enumerate((9, 12, 15)):
                c.create_text(cx + 34 + i * 14, top + 14 - i * 14 - off, text="Z",
                              fill=ACCENT, font=("Consolas", size, "bold"))
        elif min(self.s["food"], self.s["fun"], self.s["energy"]) < 25:
            c.create_text(cx + 58, top + 12, text="!", fill=ACCENT, font=("Consolas", 20, "bold"))

    def draw_hud(self):
        """Statusbalken, Level mit XP-Balken, Punkte und Tageslust."""
        c = self.canvas
        panel(c, 8, 4, W - 8, HUD_H)
        for label, key, x in (("HUN", "food", 18), ("FUN", "fun", 80), ("NRG", "energy", 142)):
            v = self.s[key]
            col = ACCENT if v >= 50 else "#ff7a2f" if v >= 25 else LIGHT
            c.create_text(x, 13, text=label, anchor="w", fill=ACCENT, font=("Consolas", 7, "bold"))
            c.create_rectangle(x, 20, x + 56, 26, outline=EDGE)
            c.create_rectangle(x, 20, x + 56 * v / 100, 26, fill=col, outline="")
        xp_progress = (int(self.s["xp"]) % 50) / 50
        c.create_text(14, 36, text=f"Lv{self.level}", anchor="w", fill=LIGHT,
                      font=("Consolas", 8, "bold"))
        c.create_rectangle(46, 33, W - 16, 39, outline=EDGE)
        c.create_rectangle(46, 33, 46 + (W - 62) * xp_progress, 39, fill=ACCENT, outline="")
        c.create_text(W // 2, 46, fill=LIGHT, font=("Consolas", 7, "bold"),
                      text=f"{int(self.s['xp']) % 50}/50 XP · {int(self.s['points'])} Pkt · Lust {self.craving}")

    def draw_game(self, now):
        if not self.game_end:
            return
        c = self.canvas
        left = max(0, int(self.game_end - now))
        best = int(self.s["highscores"].get(self.game_mode, 0))
        if self.game_mode in STATIC_GAMES:
            title = getattr(self, "draw_" + self.game_mode)(now, left)
        elif self.game_mode == "jump":
            title = f"Fang mich: {self.game_score} · {left}s"
        elif self.game_mode == "reflex":
            title = f"Reflex {self.game_score}/5 · Ziel {min(5, self.reflex_round + 1)}/5"
            t = self.reflex_target
            if t:
                x, y, r = t["x"], t["y"], t["r"]
                frac = clamp((t["until"] - now) / REFLEX_LIFETIME, 0.0, 1.0)
                ring = r + 4 + 16 * frac                  # Ring schrumpft = Restzeit
                c.create_oval(x - ring, y - ring, x + ring, y + ring, outline=EDGE, width=2)
                c.create_oval(x - r, y - r, x + r, y + r, fill=PANEL, outline=ACCENT, width=3)
                c.create_oval(x - 5, y - 5, x + 5, y + 5, fill=LIGHT, outline="")
        else:
            title = f"Daten {self.game_score} · {left}s"
            for d in self.dots:
                col = LIGHT if (d["until"] - now) < 0.7 and int(self.t / 3) % 2 == 0 else ACCENT
                c.create_oval(d["x"] - 11, d["y"] - 11, d["x"] + 11, d["y"] + 11,
                              fill=PANEL, outline=col, width=3)
                c.create_oval(d["x"] - 4, d["y"] - 4, d["x"] + 4, d["y"] + 4, fill=LIGHT, outline="")
        c.create_text(W // 2, HUD_H + 14, fill=LIGHT, font=("Consolas", 8, "bold"),
                      text=f"{title} · Rekord {best}")

    def shifted(self, key, fn, *args):
        """Zeichnet fn und verschiebt das Ergebnis senkrecht um den eingestellten Wert."""
        c, n0 = self.canvas, len(self.canvas.find_all())
        fn(*args)
        dy = self.s.get(key, 0)
        if dy:
            for item in c.find_all()[n0:]:
                c.move(item, 0, dy)

    def draw_bubble(self, now, top=0):
        if now > self.bubble_until or not self.bubble_text:
            return
        c = self.canvas
        if self.mini:
            y, width = max(30, top - 34), 150
        else:
            y, width = (106 if (self.feeding or self.naming or self.prompt) else 92), W - 30
        t = c.create_text(W // 2, y, text=self.bubble_text, width=width,
                          fill=LIGHT, font=("Consolas", 9, "bold"))
        x1, y1, x2, y2 = c.bbox(t)
        r = panel(c, x1 - 8, y1 - 6, x2 + 8, y2 + 6)
        c.tag_lower(r, t)
        c.create_polygon(W // 2 - 8, y2 + 6, W // 2 + 8, y2 + 6, W // 2, y2 + 16, fill=ACCENT, outline="")

    def _flat_photo(self, im):
        """RGBA-Bild -> PhotoImage mit Transparenzfarbe (hartes Alpha wie bei den Figurenbildern)."""
        alpha = im.getchannel("A").point(lambda v: 255 if v > 140 else 0)
        flat = Image.new("RGB", im.size, (1, 2, 3))
        flat.paste(im.convert("RGB"), (0, 0), alpha)
        return ImageTk.PhotoImage(flat)

    def glitch_bands(self, im, strength, bands):
        """Verschiebt zufällige waagerechte Streifen seitlich (Glitch-Effekt)."""
        w, h = im.size
        out = im.copy()
        for _ in range(max(0, bands)):
            y0 = random.randint(0, max(0, h - 4))
            y1 = min(h, y0 + random.randint(4, max(5, h // 10)))
            dx = random.randint(-strength, strength)
            if dx == 0:
                continue
            band = im.crop((0, y0, w, y1))
            out.paste((0, 0, 0, 0), (0, y0, w, y1))
            out.paste(band, (dx, y0))
        return out

    def draw_fx_figure(self, key, cx, mid, sx, sy, dx, glitch=0, bands=0):
        """Figur (Bild oder gezeichnet) um die Mitte mid skaliert, verschoben und optional geglitcht."""
        c = self.canvas
        if key is not None:
            src, _ = self.art_base(key, self.current_height())
            im = self.glitch_bands(src, glitch, bands) if glitch else src
            w2, h2 = max(1, round(im.width * sx)), max(1, round(im.height * sy))
            if (w2, h2) != im.size:
                im = im.resize((w2, h2), Image.BILINEAR)
            self.fx_photo = self._flat_photo(im)
            c.create_image(cx + dx, mid + h2 / 2, image=self.fx_photo, anchor="s")
        else:
            self.draw_character(mid - self.figure_h() / 2, H - 5)
            c.scale("all", cx, mid, sx, max(sy, 0.02))
            if dx:
                c.move("all", dx, 0)

    def draw_lightning(self, cx, cy, count, rmin=55, rmax=125):
        c = self.canvas
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(rmin, rmax)
            sx, sy = cx + math.cos(angle) * 24, cy + math.sin(angle) * 35
            ex, ey = cx + math.cos(angle) * length, cy + math.sin(angle) * length
            bx = (sx + ex) / 2 + random.randint(-24, 24)
            by = (sy + ey) / 2 + random.randint(-24, 24)
            c.create_line(sx, sy, bx, by, ex, ey,
                          fill=random.choice((ACCENT, "#ff334f", "#ff6878")),
                          width=random.choice((2, 3, 4)))

    def draw_startup(self):
        """Einschalt-Animation: Lichtpunkt -> Linie -> Figur klappt auf, Glitch klingt ab, Ring am Boden."""
        elapsed = time.monotonic() - self.boot_started
        p = clamp(elapsed / BOOT_DURATION)
        cx = W // 2
        base = H - 5
        fh = self.figure_h()
        top = base - fh
        mid = base - fh / 2
        c = self.canvas
        c.delete("all")
        key = self.art_key()
        fw = self.art_base(key, self.current_height())[0].width if key is not None else 92
        a, b = 0.22, 0.58
        if p < a:
            # 1) Punkt wächst zur leuchtenden Linie
            q = smooth(p / a)
            half = fw * 0.6 * q
            r = 2 + 3 * (1 - q)
            c.create_line(cx - half, mid, cx + half, mid, fill="#5a0a14", width=8)
            c.create_line(cx - half, mid, cx + half, mid, fill=LIGHT, width=2)
            c.create_oval(cx - r, mid - r, cx + r, mid + r, fill=LIGHT, outline=ACCENT)
        elif p < b:
            # 2) Linie klappt zur vollen Figur auf, starker Glitch
            q = smooth((p - a) / (b - a))
            sy = max(0.03, q)
            self.draw_fx_figure(key, cx, mid, 1.15 - 0.15 * q, sy, random.randint(-4, 4),
                                glitch=round(12 * (1 - q)) + 2, bands=int(7 * (1 - q)) + 1)
            half = fw * 0.6
            c.create_line(cx - half, mid, cx + half, mid,
                          fill=mix_hex(LIGHT, TRANS, q), width=max(1, round(4 * (1 - q))))
            self.draw_lightning(cx, mid, int(3 * (1 - q)))
        else:
            # 3) Figur steht: Glitch und Flackern klingen ab, Ring wandert vom Boden nach außen
            q = (p - b) / (1 - b)
            flicker = q < 0.5 and random.random() < 0.3 * (1 - q * 2)
            if not flicker:
                self.draw_fx_figure(key, cx, mid, 1.0, 1.0, 0,
                                    glitch=round(6 * (1 - q)) if q < 0.7 else 0,
                                    bands=int(4 * (1 - q)) if q < 0.7 else 0)
            ring = 25 + q * 95
            col = mix_hex(ACCENT, TRANS, q ** 1.5)
            c.create_oval(cx - ring, base - ring * 0.22, cx + ring, base + ring * 0.22,
                          outline=col, width=max(1, round(4 * (1 - q))))
            if q > 0.1:
                ring2 = 15 + (q - 0.1) * 70
                c.create_oval(cx - ring2, base - ring2 * 0.2, cx + ring2, base + ring2 * 0.2,
                              outline=mix_hex(LIGHT, TRANS, min(1.0, (q - 0.1) * 1.3)), width=2)
        label = "NOVA.SYS  BOOT" if p < b else ("ONLINE" if int(elapsed * 10) % 2 or p > 0.85
                                                 else "ONLINE _")
        c.create_text(cx, max(14, top - 14), text=label, fill=ACCENT if p < b else LIGHT,
                      font=("Consolas", 9, "bold"))
        if p > 0.6:
            self.draw_bubble(time.time(), top)
        self._set_geometry(W, H)
        self._schedule_tick()

    def draw_shutdown(self):
        """Kurze rote Abschiedsanimation: Figur schrumpft, Blitze, pulsierender Schein."""
        elapsed = time.monotonic() - self.quit_started
        progress = clamp(elapsed / self.quit_duration)
        if self.phone_mode:
            self.canvas.delete("all")
            self.draw_phone_view(time.time())
            self.canvas.create_rectangle(
                6, 6, PHONE_SIZE - 6, PHONE_SIZE - 6,
                outline=LIGHT if int(elapsed * 12) % 2 else ACCENT, width=3)
            self.root.geometry(
                f"{PHONE_SIZE}x{PHONE_SIZE}+{int(self.x)}+{int(self.y)}")
            if progress >= 1:
                self.stop_voice(graceful=True)
                self.root.destroy()
                return
            self._schedule_tick()
            return
        if self.fly_on:
            self.fly_on = False
            self.canvas.configure(width=W, height=H)
        self.angle = self.spin = 0.0
        cx = W // 2
        base = H - 5
        fh = self.figure_h()
        top = base - fh
        mid = base - fh / 2
        c = self.canvas
        c.delete("all")
        key = self.art_key()
        fw = self.art_base(key, self.current_height())[0].width if key is not None else 92
        p1, p2 = 0.40, 0.78
        if progress < p1:
            # 1) Überladung: Figur zittert, Glitch-Streifen, Schein und Blitze nehmen zu
            q = progress / p1
            shake = round(2 + 6 * q)
            dx = random.randint(-shake, shake)
            self.draw_fx_figure(key, cx, mid, 1.0, 1.0, dx,
                                glitch=round(3 + 9 * q), bands=2 + int(6 * q))
            self.draw_accessories(top)
            c.move("acc", dx, 0)
            pulse = 0.5 + 0.5 * math.sin(elapsed * 38)
            glow_r = 45 + 45 * q + pulse * 8
            glow = c.create_oval(cx - glow_r, mid - glow_r, cx + glow_r, mid + glow_r,
                                 fill="#260008", outline=ACCENT, width=3)
            c.tag_lower(glow)
            self.draw_lightning(cx, mid, 2 + int(5 * q))
        elif progress < p2:
            # 2) Röhrenfernseher-Aus: Figur klappt zu einer Linie zusammen, dann zu einem Punkt
            q = (progress - p1) / (p2 - p1)
            if q < 0.7:
                t = smooth(q / 0.7)
                sy, sx = max(0.0, 1 - t), 1 + 0.15 * t
                if sy > 0.04:
                    self.draw_fx_figure(key, cx, mid, sx, sy, 0)
                half = fw * sx / 2
                c.create_line(cx - half, mid, cx + half, mid, fill="#5a0a14",
                              width=8 + int(8 * t))
                c.create_line(cx - half, mid, cx + half, mid,
                              fill=LIGHT if t > 0.55 else ACCENT, width=2 + int(3 * t))
            else:
                t = smooth((q - 0.7) / 0.3)
                half = fw * 1.15 / 2 * (1 - t)
                width = max(2, round(5 * (1 - t)))
                c.create_line(cx - half, mid, cx + half, mid, fill="#5a0a14", width=width + 6)
                c.create_line(cx - half, mid, cx + half, mid, fill=LIGHT, width=width)
                r = 3 + 6 * t
                c.create_oval(cx - r, mid - r, cx + r, mid + r, fill=LIGHT, outline=ACCENT)
        else:
            # 3) Letzter Funke: Punkt verglüht, Druckwelle und Funken fliegen nach außen
            q = (progress - p2) / (1 - p2)
            r = max(0.0, 9 * (1 - q * 1.6))
            if r > 0.5:
                c.create_oval(cx - r, mid - r, cx + r, mid + r, fill=LIGHT, outline=ACCENT)
            ring = 10 + q * 105
            c.create_oval(cx - ring, mid - ring, cx + ring, mid + ring,
                          outline=mix_hex(ACCENT, TRANS, q ** 2), width=max(1, round(5 * (1 - q))))
            ring2 = 6 + q * 60
            c.create_oval(cx - ring2, mid - ring2, cx + ring2, mid + ring2,
                          outline=mix_hex(LIGHT, TRANS, q), width=2)
            for i in range(14):
                ang = i * math.pi / 7 + 0.2
                r1 = q * (55 + 45 * ((i * 7) % 5) / 4)
                r2 = r1 + 16 * (1 - q) + 3
                c.create_line(cx + math.cos(ang) * r1, mid + math.sin(ang) * r1,
                              cx + math.cos(ang) * r2, mid + math.sin(ang) * r2,
                              fill=mix_hex("#ff6878", TRANS, q ** 1.5), width=2)
        self.draw_bubble(time.time(), top)
        self.root.geometry(f"{W}x{H}+{int(self.x)}+{int(self.y)}")
        if progress >= 1:
            self.stop_voice(graceful=True)
            self.root.destroy()
            return
        self._schedule_tick()

    # ================= Hauptschleife =================
    def _set_geometry(self, width, height, x=None, y=None):
        """Setzt die Fensterposition nur, wenn sie sich geändert hat (spart Tk-Aufrufe)."""
        px = int(self.x) if x is None else int(x)
        py = int(self.y) if y is None else int(y)
        geometry = f"{width}x{height}+{px}+{py}"
        if geometry != self._geometry:
            self._geometry = geometry
            self.root.geometry(geometry)

    def _schedule_tick(self, delay=None):
        if delay is None:      # Zielrate minus bereits verbrauchte Frame-Zeit
            spent = (time.perf_counter() - self._tick_start) * 1000
            delay = max(1, int(1000 / self.fps - spent))
        try:
            self._tick_id = self.root.after(delay, self.tick)
        except tk.TclError:
            self._tick_id = None

    def _log_error(self):
        """Schreibt den Traceback höchstens alle 5 Sekunden in nova_error.log."""
        now = time.time()
        if now - self._last_error_log < 5:
            return
        self._last_error_log = now
        try:
            if os.path.isfile(ERROR_LOG) and os.path.getsize(ERROR_LOG) > 200_000:
                os.remove(ERROR_LOG)
            with open(ERROR_LOG, "a", encoding="utf-8") as log:
                log.write(f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                log.write(traceback.format_exc() + "\n")
        except OSError:
            pass

    def tick(self):
        """Ein Fehler in einem Frame darf NOVA nicht einfrieren: loggen und weiterlaufen."""
        self._tick_id = None
        self._tick_start = time.perf_counter()
        try:
            self._tick()
        except Exception:
            self._log_error()
            if self.quitting:
                try:
                    self.root.destroy()
                except tk.TclError:
                    pass
                return
            if self._tick_id is None:
                try:
                    if self.root.winfo_exists():
                        self._schedule_tick(100)
                except tk.TclError:
                    pass

    def _tick(self):
        self._tp = self.t
        self.t = int((time.perf_counter() - self._t0) * 30)
        now = time.time()
        if self.quitting:
            self.draw_shutdown()
            return
        if self.boot_started:
            if time.monotonic() - self.boot_started < BOOT_DURATION and not self.phone_mode:
                self.draw_startup()
                return
            self.boot_started = 0.0
        if self.crosshair_mode:          # alles andere aus
            self.last_tick = now
            self._schedule_tick(150)
            return
        self.process_ai_results()
        self.process_ai_speech_results()
        self.process_ai_voice_results()
        self.process_voice_events()
        speech_contexts_to_fill = {"idle", "general"}
        speech_contexts_to_fill.update(item[0] for item in self.ai_speech_pending)
        if (self.ai_window is None and self.ai_enabled and self._ai_is_ready() and not self.ai_busy and
                not self.ai_speech_busy and now >= self.ai_speech_retry_at and
                any(not self.ai_speech_lines.get(context)
                    for context in speech_contexts_to_fill)):
            self._request_ai_speech_lines()
        if self.ai_window is None and self.ai_speech_error and now > self.bubble_until:
            self.bubble_text = self.ai_speech_error[:140]
            self.bubble_until = now + 8
            self.ai_speech_error = ""
        if self.t // 30 != self._tp // 30:
            self.check_voice()
        if self.voice_error_message:
            error = self.voice_error_message
            self.voice_error_message = ""
            self.voice_enabled = False
            self.s["voice_enabled"] = False
            self.stop_voice()
            self.save()
            self.bubble_text = "Sprachausgabe-Fehler: " + error[:140]
            self.bubble_until = now + 8
        dt = min(now - self.last_tick, 5.0)
        self.last_tick = now
        fk = min(dt * 30, 3.0)       # Frames-Faktor (1.0 bei 30 FPS)

        self.update_stats(dt, now)
        self.update_idle(now)
        self.update_timer(now)
        self.update_reminders()
        self.poll_tools(now)
        if self.t // 30 != self._tp // 30 and (self.sys_monitor or self.living_mode):
            self.update_system_metrics()
            if (self.sys_monitor and not self.sleeping and now - self.last_sys_warn > 90
                    and now > self.bubble_until):
                if self.cpu_percent >= 88:
                    self.last_sys_warn = now
                    self.teleport_until = now + 0.6
                    self.say(f"Warnung: CPU bei {int(self.cpu_percent)}%! Mein Kern glüht!", 5)
                elif self.ram_percent >= 90:
                    self.last_sys_warn = now
                    self.say(f"Speicher kritisch: {int(self.ram_percent)}% RAM belegt!", 5)
        if IS_WIN and self.spotify_mode:
            self.update_spotify(now)
        self.update_emotion()
        self.air_now = self.air_pose()
        self.update_game(now)
        if self.t // 15 != self._tp // 15 and not self.phone_mode:
            self.update_mini()
        if self.t // 6 != self._tp // 6:
            self.remember_foreground_window()
        if self.t // 300 != self._tp // 300:      # alle ~10 s: neuer Tag?
            self.daily_check()
        self.update_living_cursor(now)
        if (self.feeding or self.prompt) and now > self.feed_deadline:
            self.cancel_feed()
        if self.radial_window is not None:
            self.check_radial_idle(now)

        if self.moving():
            speed = 1 if self.s["energy"] < 20 else 2
            self.x += speed * fk * self.dir
            lo, hi = self.walk_bounds()
            if self.x <= lo:
                self.dir = 1
            elif self.x >= hi:
                self.dir = -1
            if random.random() < 0.004 * fk:
                self.dir *= -1
        menu_open = self.radial_window is not None
        jump_game = bool(self.game_end and self.game_mode == "jump")
        static_game = bool(self.game_end and self.game_mode in STATIC_GAMES)
        if not self.phone_mode:
            if self.phys_active:
                self.update_physics(now, dt)
            elif self.mini and not jump_game:
                if not self.dragging:
                    self.follow_corner()
            elif ((self.window_mode or self.returning or self.living_mode
                   or self.perch_hwnd is not None) and not self.dragging
              and not jump_game and not static_game and not self.ice_hold()):
                self.follow_platform()
        self.update_rotation(dt)
        if menu_open:
            self.follow_radial()

        if random.random() < 0.01 * fk:
            self.blink_until = now + 0.15
        if (self.ai_window is None and not self.ai_busy and not self.ai_voice_busy
                and not self.ai_voice_continuous
                and random.random() < 0.0005 * fk
                and now > self.bubble_until):
            self.say_random()

        lt = time.localtime()
        if lt.tm_hour != self.last_hour:
            self.last_hour = lt.tm_hour
            if not self.system_dozing:
                self.say(f"Es ist {lt.tm_hour}:00 Uhr.", 6)
        if now - self.last_break > BREAK_MINUTES * 60:
            self.last_break = now
            if not self.system_dozing:
                self.say("Pause! Steh auf, streck dich, trink was.", 10)

        if self.phone_mode:
            self.canvas.delete("all")
            self.draw_phone_view(now)
            self._set_geometry(PHONE_SIZE, PHONE_SIZE)
            self._schedule_tick()
            return

        if self.fly_active():
            self.draw_fly_view()
            self._schedule_tick()
            return
        if self.fly_on:                    # Drehung vorbei: zurück zum normalen Fenster
            self.fly_on = False
            self.canvas.configure(width=self.display_width(), height=self.display_height())

        sitting = self.music_visible()
        hover = (math.sin(self.t * 0.08) * (7 if self.airborne() else 4)
                 if not self.sleeping and not menu_open and not sitting else 0)
        if sitting and self.spotify_playing and not self.sleeping and not menu_open:
            # Mitwippen im Takt (~120 BPM): kleiner Hüpfer nach oben + sanftes Wiegen
            hover = -abs(math.sin(self.t * 0.21)) * 4
        base = H - 5 - self.music_offset() + hover
        top = base - self.figure_h()

        self.canvas.delete("all")
        self.draw_character(top, base)
        self.draw_air_glitch(base)
        self.draw_bump_glitch(now, W // 2, base, self.figure_h())
        self.draw_music_box(now)
        self.draw_glitch_effect(now)
        self.draw_accessories(top)
        self.draw_ai_orb(top)
        self.draw_status_marks(top)
        if (self.hover or now < self.hud_until) and not self.mini and not self.naming and not self.prompt:
            self.shifted("hud_dy", self.draw_hud)
        if self.sys_monitor and not self.mini and not self.naming and not self.feeding and not self.prompt:
            self.draw_sys_monitor()
        self.draw_tool_chips(now, top)
        self.draw_fav_chips()
        self.draw_game(now)
        self.draw_alarm(now)
        self.shifted("bubble_dy", self.draw_bubble, now, top)
        self._set_geometry(self.display_width(), self.display_height())
        self._schedule_tick()


if __name__ == "__main__":
    if "--pack" in sys.argv:
        pack_shop()
    else:
        Nova()