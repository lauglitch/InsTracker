import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame
import tkinter as tk
from tkinter import Label, filedialog, ttk
from PIL import ImageTk, Image
from core.logic import load_data

# ===============================
# WINDOW INIT
# ===============================
window = tk.Tk()
width = 950
height = 700
hexaColor = "#C13584"


# ===============================
# PATHS (ROBUSTO PYINSTALLER)
# ===============================
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parents[1]

    return str(base_path / relative_path)


def asset(path):
    return resource_path(path)


# ===============================
# VERSION
# ===============================
def get_version():
    try:
        base = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else ROOT
        return (base / "version.txt").read_text().strip()
    except:
        return "unknown"


# ===============================
# GLOBALS
# ===============================
image_tk = None
btnImage_tk = None


# ===============================
# UI SETUP
# ===============================
def set_window():
    global image_tk, btnImage_tk

    window.geometry(f"{width}x{height}")
    window.title("InsTracker Free v" + get_version())
    window.resizable(False, False)
    window.configure(bg=hexaColor)

    try:
        icon = tk.PhotoImage(file=asset("Assets/instagramLogo.png"))
        window.iconphoto(True, icon)
    except:
        pass

    # assets aquí (OK para PyInstaller)
    titlePNG = Image.open(asset("Assets/instrackerTitle.png")).convert("RGBA")
    image_tk = ImageTk.PhotoImage(titlePNG)

    btnImage = Image.open(asset("Assets/exportButtonPNG.png"))
    btnImage_tk = ImageTk.PhotoImage(btnImage)


def set_instructions():
    instructions = Label(
        window,
        text=(
            "1- Inicia sesión en Instagram\n"
            "2- Descarga tu información\n"
            "3- Selecciona seguidores y seguidos\n"
            "4- Formato JSON\n"
            "5- Descarga ZIP\n"
            "6- Carga el archivo\n"
            "7- Exportado en exportedData.txt\n"
        ),
        font=("Arial", 14),
        bg=hexaColor,
        fg="white",
        justify="left",
        wraplength=800,
    )
    instructions.pack()


# ===============================
# LOGIC
# ===============================
def find_files():
    clear_info()
    show_error(False)

    ruta_archivo = filedialog.askopenfilename(filetypes=[("ZIP", "*.zip")])
    if not ruta_archivo:
        return

    try:
        with open(ruta_archivo, "rb") as f:
            followers, following = load_data(f.read())

        result = [u for u in following if u not in followers]

        show_info(len(followers), len(following), len(result))

        with open("exportedData.txt", "w", encoding="utf-8") as file:
            file.writelines(u + "\n" for u in result)

        play_sound(True)

    except Exception as e:
        print("Error:", e)
        show_error(True)
        play_sound(False)


# ===============================
# UI HELPERS
# ===============================
def clear_info():
    for widget in window.winfo_children():
        if isinstance(widget, tk.Label):
            txt = widget.cget("text").lower()
            if "follower" in txt or "following" in txt or "unmutual" in txt:
                widget.destroy()


def show_error(showError):
    errorText.config(text="Archivo no válido" if showError else "")


def show_info(followerCount, followingCount, unmutualCount):
    tk.Label(
        window,
        text=f"follower: {followerCount}",
        font=("Arial", 16),
        bg=hexaColor,
        fg="white",
    ).place(x=200, y=600)
    tk.Label(
        window,
        text=f"following: {followingCount}",
        font=("Arial", 16),
        bg=hexaColor,
        fg="white",
    ).place(x=400, y=600)
    tk.Label(
        window,
        text=f"unmutual: {unmutualCount}",
        font=("Arial", 16),
        bg=hexaColor,
        fg="white",
    ).place(x=600, y=600)


def play_sound(succeed):
    try:
        path = asset(
            "Assets/successAudio.mp3" if succeed else "Assets/failureAudio.mp3"
        )
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
    except:
        pass


# ===============================
# START
# ===============================
pygame.mixer.init()

set_window()

tk.Label(window, image=image_tk, bg=hexaColor).pack(pady=10)

set_instructions()

styles = ttk.Style()
styles.configure("TButton", borderwidth=0, relief="flat")

ttk.Button(window, image=btnImage_tk, command=find_files, style="TButton").pack(pady=20)

errorText = tk.Label(window, text="", bg=hexaColor, fg="white", font=("Arial", 16))
errorText.place(x=390, y=600)

window.mainloop()
