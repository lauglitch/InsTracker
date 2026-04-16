import pygame
import tkinter as tk
from tkinter import Label, filedialog, ttk
import zipfile
from PIL import ImageTk, Image
import json
import io
import re
import sys
from urllib.parse import urlparse
from pathlib import Path


# ===============================
# PATHS
# ===============================
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return str(Path(base_path) / relative_path)


def asset(path):
    return resource_path(path)


# ===============================
# UI
# ===============================
window = tk.Tk()
width = 950
height = 700
hexaColor = "#C13584"
zipBuffer = None


def set_window():
    window.geometry(f"{width}x{height}")
    window.title("InsTracker")
    window.resizable(False, False)
    window.configure(bg=hexaColor)
    try:
        icon = tk.PhotoImage(file=asset("Assets/instagramLogo.png"))
        window.iconphoto(True, icon)
    except:
        pass


def set_instructions():
    Label(
        window,
        text=(
            "1- Inicia sesión en tu cuenta de Instagram: accountscenter.instagram.com/info_and_permissions/\n"
            "2- Pulsa 'Exportar tu información', 'Crear exportación', selecciona tu cuenta y pulsa 'Exportar al dispositivo'\n"
            "3- Pulsa 'Información que se incluirá' y marca Conexiones: 'Seguidores y seguidos'\n"
            "4- Selecciona Intervalo de fechas: 'Cualquier fecha'; Formato: 'JSON'; Calidad del contenido multimedia: 'Más baja'\n"
            "5- Pulsa en 'Iniciar exportación' y espera el correo\n"
            "6- Descarga el ZIP y en InsTracker pulsa 'EXPORTAR DATOS' y selecciona el fichero\n"
            "7- Archivo listo en la carpeta de InsTracker: 'exportedData.txt'\n\n"
            "NOTA: Puedes ignorar usuarios listándolos en 'followignore.txt' (1 por línea)\n"
        ),
        font=("Arial", 14),
        bg=hexaColor,
        fg="white",
        justify="left",
        wraplength=800,
    ).pack()


# ===============================
#
# ===============================
FOLLOWERS_REGEX = re.compile(r"followers(_\d+)?\.json$", re.IGNORECASE)
FOLLOWING_REGEX = re.compile(r"following(_\d+)?\.json$", re.IGNORECASE)


def find_json_files(names):
    followers = [n for n in names if FOLLOWERS_REGEX.search(n)]
    following = [n for n in names if FOLLOWING_REGEX.search(n)]
    return sorted(followers), sorted(following)


# ===============================
# EXTRACT USERNAME
# ===============================
def normalize(username):
    if not username:
        return None
    return username.strip().lower()


def extract_username(entry):
    # value
    try:
        for item in entry.get("string_list_data", []):
            val = item.get("value")
            if val:
                return normalize(val)
    except:
        pass

    # title
    t = entry.get("title")
    if isinstance(t, str):
        return normalize(t)

    # href
    try:
        for item in entry.get("string_list_data", []):
            href = item.get("href", "")
            if href:
                path = urlparse(href).path.strip("/")
                if path.startswith("_u/"):
                    path = path[3:]
                return normalize(path.split("/")[0])
    except:
        pass

    return None


# ===============================
# LOAD DATA
# ===============================
def load_data(zip_bytes, follower_files, following_files):
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as z:

        # ✅ FOLLOWERS (SOLO listas válidas)
        followers_entries = []
        for file in follower_files:
            data = json.loads(z.read(file).decode("utf-8"))

            if isinstance(data, list):
                followers_entries.extend(data)

            elif isinstance(data, dict):
                if "relationships_followers" in data:
                    followers_entries.extend(data["relationships_followers"])

        # ✅ FOLLOWING (todas las partes)
        following_entries = []
        for file in following_files:
            data = json.loads(z.read(file).decode("utf-8"))

            if isinstance(data, dict) and "relationships_following" in data:
                following_entries.extend(data["relationships_following"])

            elif isinstance(data, list):
                following_entries.extend(data)

        followers = set(filter(None, (extract_username(e) for e in followers_entries)))
        following = list(filter(None, (extract_username(e) for e in following_entries)))

        return followers, following


# ===============================
# CORE
# ===============================
def export_data(follower_files, following_files):
    try:
        followers, following = load_data(zipBuffer, follower_files, following_files)

        try:
            with open("followignore.txt", "r", encoding="utf-8") as f:
                ignored = set(line.strip() for line in f if line.strip())
        except:
            ignored = set()

        followers_set = set(followers)
        following_set = set(following)

        result = [
            u for u in following_set if u not in followers_set and u not in ignored
        ]

        show_info(len(followers), len(following), len(result))

        with open("exportedData.txt", "w", encoding="utf-8") as f:
            for u in result:
                f.write(u + "\n")

        play_sound(True)

    except Exception as e:
        print("ERROR:", e)
        show_error(True)
        play_sound(False)


# ===============================
# UI HELPERS
# ===============================
def clear_info():
    for widget in window.winfo_children():
        if isinstance(widget, tk.Label) and any(
            k in widget.cget("text").lower()
            for k in ["follower", "following", "unmutual"]
        ):
            widget.destroy()


def show_error(show):
    errorText.config(text="Archivo no válido" if show else "")


def show_info(f1, f2, f3):
    tk.Label(
        window, text=f"follower: {f1}", font=("Arial", 16), bg=hexaColor, fg="white"
    ).place(x=200, y=600)
    tk.Label(
        window, text=f"following: {f2}", font=("Arial", 16), bg=hexaColor, fg="white"
    ).place(x=400, y=600)
    tk.Label(
        window, text=f"unmutual: {f3}", font=("Arial", 16), bg=hexaColor, fg="white"
    ).place(x=600, y=600)


def play_sound(success):
    try:
        path = (
            asset("Assets/successAudio.mp3")
            if success
            else asset("Assets/failureAudio.mp3")
        )
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
    except:
        pass


# ===============================
# FILE SELECT
# ===============================
def find_files():
    clear_info()
    show_error(False)

    file = filedialog.askopenfilename(filetypes=[("ZIP", "*.zip")])
    if not file:
        return

    try:
        with zipfile.ZipFile(file, "r") as z:
            names = z.namelist()

        follower_files, following_files = find_json_files(names)

        if not follower_files or not following_files:
            show_error(True)
            play_sound(False)
            return

        global zipBuffer
        with open(file, "rb") as f:
            zipBuffer = f.read()

        export_data(follower_files, following_files)

    except:
        show_error(True)
        play_sound(False)


# ===============================
# START
# ===============================
set_window()

try:
    img = Image.open(asset("Assets/instrackerTitle.png"))
    img_tk = ImageTk.PhotoImage(img)
    tk.Label(window, image=img_tk, bg=hexaColor).pack(pady=10)
except:
    pass

set_instructions()

ttk.Button(window, text="EXPORTAR DATOS", command=find_files).pack(pady=40)

errorText = tk.Label(window, text="", bg=hexaColor, fg="white")
errorText.place(x=390, y=600)

pygame.mixer.init()

window.mainloop()
