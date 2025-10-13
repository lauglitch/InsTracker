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


# ---------- Helpers: rutas de assets (dev, PyInstaller onefile/onedir) ----------
def resource_path(relative_path: str) -> str:
    base_path = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return str(Path(base_path) / relative_path)


def asset(path: str) -> str:
    return resource_path(path)


# ---------- UI base ----------
window = tk.Tk()
width = 950
height = 700
hexaColor = "#C13584"
zipBuffer = None  # guardamos el ZIP en memoria para relecturas


# 1- Ventana
def set_window():
    window.geometry(f"{width}x{height}")
    window.title("InsTracker (Free)")
    window.resizable(False, False)
    window.configure(bg=hexaColor)
    try:
        icon = tk.PhotoImage(file=asset("Assets/instagramLogo.png"))
        window.iconphoto(True, icon)
    except Exception:
        pass


# 2- Instrucciones
def set_instructions():
    instructions = Label(
        window,
        text=(
            "1) Entra: accountscenter.instagram.com/info_and_permissions/\n"
            "2) 'Descarga tu información' → 'Descargar o transferir información' → tu cuenta\n"
            "3) 'Parte de tu información' → marca 'Seguidores y seguidos'\n"
            "4) 'Descargar en el dispositivo': Intervalo 'Desde el principio', Formato 'JSON', Calidad 'Baja'\n"
            "5) Crea el archivo y descarga el ZIP que te envían\n"
            "6) Pulsa 'EXPORTAR DATOS' y selecciona el ZIP\n"
            "7) Se genera 'exportedData.txt' con quién sigues y no te sigue de vuelta\n"
        ),
        font=("Arial", 14),
        bg=hexaColor,
        fg="white",
        justify="left",
        wraplength=800,
    )
    instructions.pack(pady=(0, 0))


# 3- Botón: buscar ZIP
def find_files():
    clear_info()
    show_error(False)
    ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivo ZIP", "*.zip")])
    if not ruta_archivo:
        return
    try:
        with zipfile.ZipFile(ruta_archivo, "r") as z:
            archivos = z.namelist()

            # detecta followers*.json (puede venir followers.json, followers_1.json, followers_2.json…)
            follower_paths = sorted(
                a
                for a in archivos
                if a.startswith("connections/followers_and_following/")
                and re.search(r"followers(_\d+)?\.json$", a)
            )

            # detecta following.json (o future following_*.json)
            following_paths = sorted(
                a
                for a in archivos
                if a.startswith("connections/followers_and_following/")
                and re.search(r"following(_\d+)?\.json$", a)
            )

            if follower_paths and following_paths:
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


# 4- Limpiar labels antiguos
def clear_info():
    for widget in window.winfo_children():
        if isinstance(widget, tk.Label) and any(
            key in widget.cget("text").lower()
            for key in ["follower", "following", "unmutual"]
        ):
            widget.destroy()


# 5- Extracción robusta username
def _extract_username(entry):
    # a) valor clásico
    try:
        val = entry.get("string_list_data", [])[0].get("value", "").strip()
        if val:
            return val
    except Exception:
        pass
    # b) nuevo esquema: viene en title
    t = entry.get("title", "")
    if isinstance(t, str) and t.strip():
        return t.strip()
    # c) fallback desde href
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


# 6- Carga y cálculo
def _load_followers_and_following_from_zip_bytes(
    zip_bytes, follower_paths, following_path
):
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as z:
        # followers: lista de entradas
        followers = []
        for fp in follower_paths:
            data = json.loads(z.read(fp).decode("utf-8"))
            if isinstance(data, list):
                followers.extend(data)
            elif isinstance(data, dict):
                followers.extend(data.get("relationships_followers", []))

        # following: dict con relationships_following o lista
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


def export_data(follower_paths, following_path):
    try:
        followers_set, following_list = _load_followers_and_following_from_zip_bytes(
            zipBuffer, follower_paths, following_path
        )

        # unmutual: gente a la que sigues y no te sigue
        intersection = set(following_list) & followers_set
        result = [user for user in following_list if user not in intersection]

        show_info(len(followers_set), len(following_list), len(result))

        with open("exportedData.txt", "w", encoding="utf-8") as f:
            for u in result:
                f.write(u + "\n")

        play_sound(True)
    except Exception as e:
        play_sound(False)
        show_error(True)
        print(f"Error en exportación: {e}")


# 7- Error label
def show_error(showError):
    errorText.config(text="Archivo no válido" if showError else "")


# 8- Contadores
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


# 9- Sonido
def play_sound(succeed):
    try:
        path = (
            asset("Assets/successAudio.mp3")
            if succeed
            else asset("Assets/failureAudio.mp3")
        )
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
    except Exception:
        pass


# ---------- Main ----------
set_window()

# Logo
try:
    titlePNG = Image.open(asset("Assets/instrackerTitle.png")).convert("RGBA")
    image_tk = ImageTk.PhotoImage(titlePNG)
    tk.Label(window, image=image_tk, bg=hexaColor).pack(pady=(10, 10))
except Exception:
    pass

set_instructions()

# Botón EXPORTAR DATOS
styles = ttk.Style()
styles.configure("TButton", borderwidth=0, relief="flat")
try:
    btnImage_tk = ImageTk.PhotoImage(Image.open(asset("Assets/exportButtonPNG.png")))
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
