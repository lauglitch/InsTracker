import pygame
import tkinter as tk
from tkinter import Label, filedialog, ttk
import zipfile
from PIL import ImageTk, Image
import json
import io
import re
from urllib.parse import urlparse

window = tk.Tk()
width = 950
height = 700
hexaColor = "#C13584"  # Instagram magenta color in hexadecimal format
followerFile = None
followingFile = None
zipBuffer = None  # keep opened ZIP bytes so we can re-read multiple files if needed


# 1- Set window's properties
def set_window():
    window.geometry(f"{width}x{height}")
    window.title("InsTracker")
    window.resizable(False, False)
    window.configure(bg=hexaColor)
    try:
        icon = tk.PhotoImage(file="Assets/instagramLogo.png")
        window.iconphoto(True, icon)
    except Exception:
        pass


# 2- Set instructions' text and its properties
def set_instructions():
    instructions = Label(
        window,
        text=(
            "1- Inicia sesión en tu cuenta de Instagram: accountscenter.instagram.com/info_and_permissions/\n"
            "2- Pulsa 'Descarga tu información' > 'Descargar o transferir información' y selecciona tu cuenta\n"
            "3- Pulsa 'Parte de tu información' y marca 'Seguidores y seguidos'\n"
            "4- Pulsa 'Descargar en el dispositivo' y selecciona: Intervalo: 'Desde el principio'; Formato: 'JSON'; Calidad: 'Baja'\n"
            "5- Pulsa en 'Crear archivos' y espera el correo\n"
            "6- Descarga el ZIP y en InsTracker pulsa 'EXPORTAR DATOS' y selecciona el fichero\n"
            "7- Archivo listo en la carpeta de InsTracker: 'exportedData.txt'\n\n"
            "NOTA: Puedes ignorar usuarios listándolos en 'followignore.txt' (1 por línea)\n"
        ),
        font=("Arial", 14),
        bg=hexaColor,
        fg="white",
        justify="left",
        wraplength=800,
    )
    instructions.pack(pady=(0, 0))


# 4- Method called when "EXPORTAR DATOS" button is pressed
def find_files():
    clear_info()
    show_error(False)
    ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivo ZIP", "*.zip")])
    if not ruta_archivo:
        return
    try:
        with zipfile.ZipFile(ruta_archivo, "r") as zip_ref:
            archivos = zip_ref.namelist()

            # Detect followers files: followers.json, followers_1.json, followers_2.json, etc.
            follower_paths = sorted(
                [
                    a
                    for a in archivos
                    if a.startswith("connections/followers_and_following/")
                    and re.search(r"followers(_\d+)?\.json$", a)
                ]
            )

            # Detect following file(s): following.json (or following_*.json as fallback)
            following_paths = sorted(
                [
                    a
                    for a in archivos
                    if a.startswith("connections/followers_and_following/")
                    and re.search(r"following(_\d+)?\.json$", a)
                ]
            )

            if follower_paths and following_paths:
                # Store raw bytes of the ZIP so export_data can reopen it safely
                global zipBuffer
                with open(ruta_archivo, "rb") as f:
                    zipBuffer = f.read()

                export_data(follower_paths, following_paths[0])
            else:
                show_error(True)
                play_sound(False)
    except zipfile.BadZipFile:
        show_error(True)
        play_sound(False)


# 5-  Method to clear resulting tags from last data loaded
def clear_info():
    for widget in window.winfo_children():
        if isinstance(widget, tk.Label) and any(
            key in widget.cget("text").lower()
            for key in ["follower", "following", "unmutual"]
        ):
            widget.destroy()


def _extract_username(entry):
    # Preferred: string_list_data[0]['value']
    try:
        val = entry.get("string_list_data", [])[0].get("value", "").strip()
        if val:
            return val
    except Exception:
        pass
    # Fallback: 'title' (Meta moved usernames here for "following")
    t = entry.get("title", "")
    if isinstance(t, str) and t.strip():
        return t.strip()
    # Fallback: parse from 'href'
    try:
        href = entry.get("string_list_data", [])[0].get("href", "")
        if href:
            path = urlparse(href).path.strip("/")
            if path.startswith("_u/"):
                path = path[3:]
            return path.split("/")[0]
    except Exception:
        pass
    return None


def _load_followers_and_following_from_zip_bytes(
    zip_bytes, follower_paths, following_path
):
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as z:
        followers = []
        for fp in follower_paths:
            data = json.loads(z.read(fp).decode("utf-8"))
            if isinstance(data, list):
                followers.extend(data)
            elif isinstance(data, dict):
                followers.extend(data.get("relationships_followers", []))

        following_raw = json.loads(z.read(following_path).decode("utf-8"))
        if (
            isinstance(following_raw, dict)
            and "relationships_following" in following_raw
        ):
            following_entries = following_raw["relationships_following"]
        else:
            following_entries = following_raw if isinstance(following_raw, list) else []

        followerIDs = set(filter(None, (_extract_username(e) for e in followers)))
        followingIDs = list(
            filter(None, (_extract_username(e) for e in following_entries))
        )
        return followerIDs, followingIDs


# 6- Method called after the files are detected
def export_data(follower_paths, following_path):
    try:
        followers_set, following_list = _load_followers_and_following_from_zip_bytes(
            zipBuffer, follower_paths, following_path
        )

        try:
            with open("followignore.txt", "r", encoding="utf-8") as ignore_file:
                ignored_users = set(
                    line.strip() for line in ignore_file if line.strip()
                )
        except FileNotFoundError:
            ignored_users = set()

        intersection = set(following_list) & followers_set
        result = [
            user
            for user in following_list
            if user not in intersection and user not in ignored_users
        ]

        show_info(len(followers_set), len(following_list), len(result))

        with open("exportedData.txt", "w", encoding="utf-8") as file:
            for username in result:
                file.write(username + "\n")

        play_sound(True)
    except Exception as e:
        play_sound(False)
        show_error(True)
        print(f"Error en exportación: {e}")


# 7- Method to show or hide error label
def show_error(showError):
    errorText.config(text="Archivo no válido" if showError else "")


# 8- Method to display follower, following, and unmutual counts
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


# 9 - Method to play success or failure sound
def play_sound(succeed):
    try:
        path = "Assets/successAudio.mp3" if succeed else "Assets/failureAudio.mp3"
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
    except Exception:
        pass


# --- Start program ---
set_window()

# Logo
try:
    titlePNG = Image.open("Assets/instrackerTitle.png").convert("RGBA")
    image_tk = ImageTk.PhotoImage(titlePNG)
    tk.Label(window, image=image_tk, bg=hexaColor).pack(pady=(10, 10))
except Exception:
    pass

# Instructions
set_instructions()

# button EXPORTAR DATOS
styles = ttk.Style()
styles.configure("TButton", borderwidth=0, relief="flat")
try:
    btnImage = Image.open("Assets/exportButtonPNG.png")
    btnImage_tk = ImageTk.PhotoImage(btnImage)
    ttk.Button(window, image=btnImage_tk, command=find_files, style="TButton").pack(
        pady=(0, 60)
    )
except Exception:
    ttk.Button(window, text="EXPORTAR DATOS", command=find_files).pack(pady=(0, 60))

# Error Label
errorText = tk.Label(window, text="", bg=hexaColor, font=("Arial", 16), fg="white")
errorText.place(x=390, y=600)

# Init mixer
try:
    pygame.mixer.init()
except Exception:
    pass

window.mainloop()
