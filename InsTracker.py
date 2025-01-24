import pygame
import tkinter as tk
from tkinter import Label, filedialog, ttk
import zipfile
from PIL import ImageTk, Image
import json

window = tk.Tk()
width = 800
height = 600
hexaColor = '#C13584'   #Instagram blue color in hexadecimal format
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
        text="1- Inicia sesión en tu cuenta de Instagram con la siguiente url:\n    instagram.com/accounts/privacy_and_security\n"
             "2- En 'Descarga de datos', haz click en 'Solicitar descarga.'\n"
             "3- Selecciona el formato 'JSON' y haz click en 'Siguiente'.\n"
             "4- Vuelve a introducir tu contraseña y haz click en 'Solicitar descarga'.\n"
             "5- Cuando recibas el fichero en tu correo, descárgalo.\n"
             "6- Pulsa el botón 'EXPORTAR DATOS' y selecciona el fichero descargado.\n"
             "7- Archivo listo en la carpeta de InsTracker con el nombre 'exportedData.txt'.",
        font=("Arial", 16),
        bg=hexaColor,
        fg="white",
        justify=tk.LEFT
    )
    instructions.place(relx=0.5, rely=0.41, anchor=tk.CENTER)

# 4- Method called when "EXPORTAR DATOS" button is pressed
def find_files():
    """Acción al presionar el botón 'EXPORTAR DATOS'."""
    # Borrar resultados anteriores antes de continuar
    clear_info()
    show_error(False)

    # Abrir el cuadro de diálogo para seleccionar el archivo ZIP
    ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivo ZIP", "*.zip")])

    if ruta_archivo:  # Si se seleccionó un archivo
        try:
            with zipfile.ZipFile(ruta_archivo, 'r') as zip_ref:
                carpetas = [nombre for nombre in zip_ref.namelist() if nombre.endswith('/')]
                if 'connections/followers_and_following/' in carpetas:
                    archivos = zip_ref.namelist()
                    if 'connections/followers_and_following/followers_1.json' in archivos and 'connections/followers_and_following/following.json' in archivos:
                        global followerFile 
                        followerFile = zip_ref.read('connections/followers_and_following/followers_1.json')
                        global followingFile 
                        followingFile = zip_ref.read('connections/followers_and_following/following.json')
                        print("'followers_1.json' and 'following.json' files found.")
                        export_data()
                    else:
                        print("Archivos 'followers_1.json' y 'following.json' no encontrados.")
                        show_error(True)
                        play_sound(False)
                else:
                    print("Carpeta 'followers_and_following' no encontrada en el ZIP.")
                    show_error(True)
                    play_sound(False)
        except zipfile.BadZipFile:
            print("El archivo ZIP seleccionado no es válido.")
            show_error(True)
            play_sound(False)
    else:
        print("No se seleccionó ningún archivo ZIP.")

# 5-  Method to clear resulting tags from last data loaded
def clear_info():
    for widget in window.winfo_children():
        if isinstance(widget, tk.Label) and any(key in widget.cget("text").lower() for key in ["follower", "following", "unmutual"]):
            widget.destroy()


# 6- Method called after "follower.js" and "following.js" are found
def export_data():
    lines1 = followerFile.splitlines()
    indexToStart = 9
    firstChar = 18
    followerID = lines1[indexToStart::13]
    followerID = [line[firstChar:-2] for line in followerID]

    lines2 = followingFile.splitlines()
    indexToStart = 10
    firstChar = 20
    followingID = lines2[indexToStart::13]
    followingID = [line[firstChar:-2] for line in followingID]

    intersection = list(set(followingID) & set(followerID))
    result = [x for x in followingID if x not in intersection]

    show_info(len(followerID), len(followingID), len(result))

    try:
        play_sound(True)
        with open("exportedData.txt", 'w') as file:
            for linea in result:
                linea = linea.decode("utf-8")
                file.writelines(linea + "\n")
        print("Data saved successfully.")
    except: 
        play_sound(False)
        print("Data couldn't be saved.")

# 7- Method to show or hide error label
def show_error(showError):
    if showError:
        errorText.config(text="Archivo no válido")
    else:
        errorText.config(text="")

# 8- Method to display follower, following, and unmutual counts
def show_info(followerCount, followingCount, unmutualCount):
    followerText = Label(window, text=("follower: " + str(followerCount)), font=("Arial", 16), bg=hexaColor, fg="white")
    followerText.place(x=125, y=500)

    followingText = Label(window, text=("following: " + str(followingCount)), font=("Arial", 16), bg=hexaColor, fg="white")
    followingText.place(x=325, y=500)
    
    unmutualText = Label(window, text=("unmutual: " + str(unmutualCount)), font=("Arial", 16), bg=hexaColor, fg="white")
    unmutualText.place(x=525, y=500)

# 9 - Method to play success or failure sound
def play_sound(succeed):
    if succeed:
        pygame.mixer.music.load("Assets/successAudio.mp3")
        pygame.mixer.music.play()
    else:
        pygame.mixer.music.load("Assets/failureAudio.mp3")
        pygame.mixer.music.play()

# Set up the window
set_window()
set_instructions()

# Set title
titlePNG = Image.open("Assets/instrackerTitle.png").convert("RGBA")
image_tk = ImageTk.PhotoImage(titlePNG)
titleImage = tk.Label(window, image=image_tk, bg=hexaColor)
titleImage.pack()

# Set buttons
styles = ttk.Style()
styles.configure('TButton', borderwidth=0, relief="flat")

btnImage = Image.open("Assets/exportButtonPNG.png")
btnImage_tk = ImageTk.PhotoImage(btnImage)

exportButton = ttk.Button(window, image=btnImage_tk, command=find_files, style="TButton")
exportButton.place(x=(height / 2 - 30), y=(width / 2 - 10))

# Set error Label
errorText = tk.Label(window, text="", bg=hexaColor, font=("Arial", 16), fg="white")
errorText.place(x=320, y=460)

# Init mixer
pygame.mixer.init()

window.mainloop()
