import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame
import tkinter as tk
from tkinter import Label, filedialog, ttk
from PIL import ImageTk, Image
from core.logic import load_data

window = tk.Tk()
width = 950
height = 700
hexaColor = "#C13584"


# ===============================
# PATHS (CLEAN & CONSISTENT)
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
        base = (
            Path(sys.executable).parent
            if getattr(sys, "frozen", False)
            else Path(__file__).resolve().parents[1]
        )
        file = base / "version.txt"
        return file.read_text().strip()
    except:
        return "unknown"


# ===============================
# IGNORE FEATURE (PRO)
# ===============================
def load_ignore():
    try:
        base = (
            Path(sys.executable).parent
            if getattr(sys, "frozen", False)
            else Path(__file__).resolve().parents[1]
        )
        file_path = base / "followignore.txt"

        with open(file_path, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    except:
        return set()


# ===============================
# UI
# ===============================
def set_window():
    window.geometry(f"{width}x{height}")
    window.title("InsTracker Pro v" + get_version())
    window.resizable(False, False)
    window.configure(bg=hexaColor)

    try:
        icon = tk.PhotoImage(file=asset("Assets/instagramLogo.png"))
        window.iconphoto(True, icon)
    except Exception as e:
        print("Icon error:", e)


def set_instructions():
    instructions = Label(
        window,
        text=(
            "1- Inicia sesión en tu cuenta de Instagram: accountscenter.instagram.com/info_and_permissions/\n"
            "2- Pulsa 'Exportar tu información', 'Crear exportación', selecciona tu cuenta y pulsa 'Exportar al dispositivo'\n"
            "3- Pulsa 'Información que se incluirá' y marca Conexiones: 'Seguidores y seguidos'\n"
            "4- Selecciona Intervalo de fechas: 'Cualquier fecha'; Formato: 'JSON'; Calidad del contenido multimedia: 'Más baja'\n"
            "5- Pulsa en 'Iniciar exportación' y espera el correo\n"
            "6- Descarga el ZIP y en InsTracker pulsa 'EXPORTAR DATOS' y selecciona el fichero\n"
            "7- Archivo listo en la carpeta de InsTracker: 'exportedData.txt'\n\n"
        ),
        font=("Arial", 14),
        bg=hexaColor,
        fg="white",
        justify="left",
        wraplength=800,
    )
    instructions.pack(pady=(0, 0))


# ===============================
# LOGIC
# ===============================
def find_files():
    clear_info()
    show_error(False)

    ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivo ZIP", "*.zip")])
    if not ruta_archivo:
        return

    try:
        with open(ruta_archivo, "rb") as f:
            followers, following = load_data(f.read())

        ignored = load_ignore()

        result = [
            u for u in following if u not in followers and u.lower() not in ignored
        ]

        show_info(len(followers), len(following), len(result))

        with open("exportedData.txt", "w", encoding="utf-8") as file:
            for username in result:
                file.write(username + "\n")

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
        if isinstance(widget, tk.Label) and any(
            key in widget.cget("text").lower()
            for key in ["follower", "following", "unmutual"]
        ):
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
set_window()

titlePNG = Image.open(asset("Assets/instrackerTitle.png")).convert("RGBA")
image_tk = ImageTk.PhotoImage(titlePNG)
tk.Label(window, image=image_tk, bg=hexaColor).pack(pady=(10, 10))

set_instructions()

style = ttk.Style()
style.configure("TButton", borderwidth=0, relief="flat")

btnImage = Image.open(asset("Assets/exportButtonPNG.png"))
btnImage_tk = ImageTk.PhotoImage(btnImage)

ttk.Button(window, image=btnImage_tk, command=find_files, style="TButton").pack(
    pady=(0, 60)
)

errorText = tk.Label(window, text="", bg=hexaColor, font=("Arial", 16), fg="white")
errorText.place(x=390, y=600)

pygame.mixer.init()
window.mainloop()
