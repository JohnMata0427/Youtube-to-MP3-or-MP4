from customtkinter import CTk, CTkFrame, CTkLabel, CTkEntry, CTkButton, set_appearance_mode
from tkinter import messagebox, filedialog
from tkinter.ttk import Progressbar, Style
from PIL import Image, ImageTk
from io import BytesIO
from pytube import YouTube
from threading import Thread
from requests import get as send_request
from re import sub

root = CTk() 
root.title("De YouTube a MP4 y MP3")
root.iconbitmap("App.ico")
root.geometry("1040x484")
root.resizable(False, False)
set_appearance_mode("dark")

window1 = CTkFrame(root)
window1.grid(row=0, column=0, padx=10, pady=10)

CTkLabel(window1, text="Introduzca la URL del video de YouTube:").grid(row=0, column=0, columnspan=3)

video_entry = CTkEntry(window1, placeholder_text="URL del video", width=500)
video_entry.grid(row=1, column=0, columnspan=3)

def download(video, extension, button):

    button.configure(state="disabled", text="\nDescargando...\n")
    search_button.configure(state="disabled")
    extension_upper = extension.upper()

    path = filedialog.asksaveasfilename(defaultextension=f".{extension}", filetypes=[(f"Archivos {extension_upper}", f"*.{extension}")], title="Guardar archivo como", initialfile=f"{titulo}.{extension}")

    if path != "":
        try:
            video.download(filename=f"{path.split('/')[-1]}", output_path="/".join(path.split("/")[:-1]))
            messagebox.showinfo("Descarga completada", f"El archivo {extension_upper} se ha descargado correctamente")
            progress_download_label.configure(text="¡Descarga completada!")
        except:
            messagebox.showerror("Error", f"No se ha podido descargar el archivo {extension_upper}.")
        
    button.configure(state="normal", text=f"\nDescargar en formato {extension_upper}\n")
    search_button.configure(state="normal")

def fetch_thumbnail(url):
    if "?v=" in url: video_id = url.split("?v=")[-1][:11]
    else: video_id = url.split("/")[-1][:11]
    
    response = send_request(f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg')    
    if response.status_code == 404: response = send_request(f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg')
    
    return ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((640, 360)))

def showInfo():
    global titulo, highest_resolution, audio

    search_button.configure(state="disabled", text="Buscando...")
    download_mp4_button.configure(state="disabled")
    download_mp3_button.configure(state="disabled")
    url = video_entry.get()

    try:
        yt = YouTube(url, on_progress_callback=progress_func)

        progress_download_label.configure(text="Progreso de la descarga: ")
        progress_bar["value"] = 0
        highest_resolution = yt.streams.get_highest_resolution()
        audio = yt.streams.get_by_itag(251)

        image_video_label.configure(image=fetch_thumbnail(url))
        title_video_label.configure(text=f"Titulo del video: \n{yt.title}")
        duration_video_label.configure(text=f"Duración del video: \n{yt.length//60} min {yt.length%60} s")
        high_resolution_label.configure(text=f"Resolución del video: \n{highest_resolution.resolution}")
        quality_audio_label.configure(text=f"Calidad del audio: \n{audio.abr}")

        file_size = highest_resolution.filesize/1024/1024

        if file_size < 1023: video_size_label.configure(text=f"Tamaño del video: \n{file_size:.2f} MB")
        else: video_size_label.configure(text=f"Tamaño del video: \n{file_size/1024:.2f} GB")
        
        audio_size_label.configure(text=f"Tamaño del audio: \n{audio.filesize/1024/1024:.2f} MB")
        
        titulo = sub(r'[\\/|:<>*¿?"]', '', yt.title)
    except Exception as e:
        messagebox.showerror("Error", f"Proporcione una URL válida de YouTube.\n\nSi el video se encuentra en directo, espere a que termine para descargarlo.\n\nError: {e}")
    finally:
        search_button.configure(state="normal", text="Buscar")
        download_mp4_button.configure(state="normal")
        download_mp3_button.configure(state="normal")

def progress_func(stream, chunk, bytes_remaining):
    progress = (1 - bytes_remaining / stream.filesize) * 100
    progress_download_label.configure(text=f"Progreso de la descarga: {progress:.0f}%")
    progress_bar["value"] = f'{progress:.0f}'

search_button = CTkButton(window1, text="Buscar", command=lambda: Thread(target=showInfo).start(), fg_color="#2c313c", hover_color="#2c313c", width=500)
search_button.grid(row=2, column=0, columnspan=3, pady=10)

video_entry.bind("<Return>", lambda event: Thread(target=showInfo).start())

image_video_label = CTkLabel(window1, image=ImageTk.PhotoImage(file='empty_video.png'), text="", width=640, height=360)
image_video_label.grid(row=3, column=0, rowspan=7)

title_video_label = CTkLabel(window1, text="Titulo del video: ", wraplength=300)
title_video_label.grid(row=3, column=1, columnspan=2)

duration_video_label = CTkLabel(window1, text="Duración del video: ")
duration_video_label.grid(row=4, column=1, columnspan=2)

high_resolution_label = CTkLabel(window1, text="Resolución: ")
high_resolution_label.grid(row=5, column=1)

quality_audio_label = CTkLabel(window1, text="Calidad del audio: ")
quality_audio_label.grid(row=5, column=2)

video_size_label = CTkLabel(window1, text="Tamaño del video: ")
video_size_label.grid(row=6, column=1)

audio_size_label = CTkLabel(window1, text="Tamaño del audio: ")
audio_size_label.grid(row=6, column=2)

download_mp4_button = CTkButton(window1, text="\nDescargar en formato MP4\n", command=lambda: Thread(target=download, args=(highest_resolution, "mp4", download_mp4_button)).start(), width=170, fg_color="#2c313c", hover_color="#2c313c")
download_mp4_button.grid(row=7, column=1, padx=10)

download_mp3_button = CTkButton(window1, text="\nDescargar en formato MP3\n", command=lambda: Thread(target=download, args=(audio, "mp3", download_mp3_button)).start(), width=170, fg_color="#2c313c", hover_color="#2c313c")
download_mp3_button.grid(row=7, column=2, padx=10)

progress_download_label = CTkLabel(window1, text="Progreso de la descarga: ")
progress_download_label.grid(row=8, column=1, columnspan=2)

style = Style()
style.theme_use("clam")
style.configure("TProgressbar", troughcolor="#2c313c", background="#297ce2")

progress_bar = Progressbar(window1, orient="horizontal", length=300, mode="determinate", style="TProgressbar")
progress_bar.grid(row=9, column=1, columnspan=2)

root.mainloop()