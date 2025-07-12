import pygame
import tkinter as tk
from tkinter import Label, filedialog, ttk
import zipfile
from PIL import ImageTk, Image
import json

window = tk.Tk()
width = 950
height = 700
hexaColor = "#C13584"  # Instagram magenta color in hexadecimal format
followerFile = None
followingFile = None


# 1- Set window's properties
def set_window():
    window.geometry(f"{width}x{height}")
    window.title("InsTracker")
    window.resizable(False, False)
    window.configure(bg=hexaColor)
    icon = tk.PhotoImage(file="Assets/instagramLogo.png")
    window.iconphoto(True, icon)


# 2- Set instructions' text and its properties
def set_instructions():
    instructions = Label(
        window,
        text="1- Inicia sesión en tu cuenta de Instagram con la siguiente url:\n    accountscenter.instagram.com/info_and_permissions/\n"
        "2- Pulsa los botones 'Descarga tu información' y 'Descargar o transferir información', y selecciona tu cuenta\n"
        "3- Pulsa el botón 'Parte de tu información' y marca 'Seguidores y seguidos'\n"
        "4- Pulsa 'Descargar en el dispositivo' y selecciona:\n"
        "   Intervalo de fechas: 'Desde el principio'; formato: 'JSON'; Calidad: 'Baja';\n"
        "5- Pulsa en 'Crear archivos'.\n"
        "6- Cuando recibas el fichero en tu correo, descárgalo.\n"
        "7- En Instracker, pulsa el botón 'EXPORTAR DATOS' y selecciona el fichero descargado.\n"
        "8- Archivo listo en la carpeta de InsTracker con el nombre 'exportedData.txt'.\n\n",
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
    if ruta_archivo:
        try:
            with zipfile.ZipFile(ruta_archivo, "r") as zip_ref:
                archivos = zip_ref.namelist()

                # Verifica que existen los dos archivos necesarios
                if (
                    "connections/followers_and_following/followers_1.json" in archivos
                    and "connections/followers_and_following/following.json" in archivos
                ):
                    global followerFile, followingFile
                    followerFile = zip_ref.read(
                        "connections/followers_and_following/followers_1.json"
                    ).decode("utf-8")
                    followingFile = zip_ref.read(
                        "connections/followers_and_following/following.json"
                    ).decode("utf-8")
                    export_data()
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


# 6- Method called after "follower.js" and "following.js" are found
def export_data():
    import json

    # Cargar los datos de followers (es una lista de dicts)
    followers_json = json.loads(followerFile)
    followerID = [
        entry["string_list_data"][0]["value"]
        for entry in followers_json
        if entry.get("string_list_data")
    ]

    # Cargar los datos de following (es un dict con lista bajo 'relationships_following')
    following_json = json.loads(followingFile)
    followingID = [
        entry["string_list_data"][0]["value"]
        for entry in following_json.get("relationships_following", [])
        if entry.get("string_list_data")
    ]

    intersection = list(set(followingID) & set(followerID))
    result = [user for user in followingID if user not in intersection]

    show_info(len(followerID), len(followingID), len(result))

    try:
        play_sound(True)
        with open("exportedData.txt", "w", encoding="utf-8") as file:
            for username in result:
                file.write(username + "\n")
    except Exception as e:
        play_sound(False)
        print(f"Error al guardar: {e}")


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
    path = "Assets/successAudio.mp3" if succeed else "Assets/failureAudio.mp3"
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()


# --- Start program ---
set_window()

# Logo
titlePNG = Image.open("Assets/instrackerTitle.png").convert("RGBA")
image_tk = ImageTk.PhotoImage(titlePNG)
tk.Label(window, image=image_tk, bg=hexaColor).pack(pady=(10, 10))

# Instructions
set_instructions()

# button EXPORTAR DATOS
styles = ttk.Style()
styles.configure("TButton", borderwidth=0, relief="flat")
btnImage = Image.open("Assets/exportButtonPNG.png")
btnImage_tk = ImageTk.PhotoImage(btnImage)
ttk.Button(window, image=btnImage_tk, command=find_files, style="TButton").pack(
    pady=(0, 60)
)

# Error Label
errorText = tk.Label(window, text="", bg=hexaColor, font=("Arial", 16), fg="white")
errorText.place(x=390, y=600)

# Init mixer
pygame.mixer.init()

window.mainloop()
