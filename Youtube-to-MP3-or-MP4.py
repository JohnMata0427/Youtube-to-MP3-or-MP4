from customtkinter import CTk, CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkProgressBar, CTkImage, set_appearance_mode
from tkinter import messagebox, filedialog
from PIL import Image
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
set_appearance_mode("system")

app = CTkFrame(root)
app.grid(row=0, column=0, padx=10, pady=10)

CTkLabel(app, text="Introduzca la URL del video de YouTube:").grid(row=0, column=0, columnspan=3)

video_entry = CTkEntry(app, placeholder_text="URL del video", width=500)
video_entry.grid(row=1, column=0, columnspan=3)

def download(video, extension, button):

    button.configure(state="disabled", text="\nDescargando...\n", width=170)
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
            progress_download_label.configure(text="Error al descargar")

    button.configure(state="normal", text=f"\nDescargar en formato {extension_upper}\n", width=170)
    search_button.configure(state="normal")

def fetch_thumbnail(url):
    if "?v=" in url: video_id = url.split("?v=")[-1][:11]
    else: video_id = url.split("/")[-1][:11]
    
    response = send_request(f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg')    
    if response.status_code == 404: response = send_request(f'https://i.ytimg.com/vi/{video_id}/mqdefault.jpg')
    
    return CTkImage(Image.open(BytesIO(response.content)), size=(640, 360))

def showInfo():
    global titulo, highest_resolution, audio

    search_button.configure(state="disabled", text="Buscando...")
    download_mp4_button.configure(width=170, state="disabled")
    download_mp3_button.configure(width=170, state="disabled")
    url = video_entry.get()

    try:
        yt = YouTube(url, on_progress_callback=progress_func)

        progress_download_label.configure(text="Progreso de la descarga: ")
        progress_bar.set(0)
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
        
        audio_size = audio.filesize/1024/1024

        if audio_size < 1023: audio_size_label.configure(text=f"Tamaño del audio: \n{audio_size:.2f} MB")
        else: audio_size_label.configure(text=f"Tamaño del audio: \n{audio_size/1024:.2f} GB")

        titulo = sub(r'[\\/|:<>*¿?"]', '', yt.title)
    except Exception as e:
        messagebox.showerror("Error", f"Proporcione una URL válida de YouTube.\n\nSi el video se encuentra en directo, espere a que termine para descargarlo.\n\nError: {e}")
    finally:
        search_button.configure(state="normal", text="Buscar")
        download_mp4_button.configure(width=170, state="normal")
        download_mp3_button.configure(width=170, state="normal")

def progress_func(stream, chunk, bytes_remaining):
    progress = (1 - bytes_remaining / stream.filesize)
    progress_download_label.configure(text=f"Progreso de la descarga: {progress * 100:.0f}%")
    progress_bar.set(progress)

search_button = CTkButton(app, text="Buscar", command=lambda: Thread(target=showInfo).start(), width=500)
search_button.grid(row=2, column=0, columnspan=3, pady=10)

video_entry.bind("<Return>", lambda event: Thread(target=showInfo).start())

image_video_label = CTkLabel(app, image=CTkImage(Image.open('assets/empty_video.png'), size=(640, 360)), text="", width=640, height=360)
image_video_label.grid(row=3, column=0, rowspan=7)

title_video_label = CTkLabel(app, text="Titulo del video: ", wraplength=300)
title_video_label.grid(row=3, column=1, columnspan=2)

duration_video_label = CTkLabel(app, text="Duración del video: ")
duration_video_label.grid(row=4, column=1, columnspan=2)

high_resolution_label = CTkLabel(app, text="Resolución: ")
high_resolution_label.grid(row=5, column=1)

quality_audio_label = CTkLabel(app, text="Calidad del audio: ")
quality_audio_label.grid(row=5, column=2)

video_size_label = CTkLabel(app, text="Tamaño del video: ")
video_size_label.grid(row=6, column=1)

audio_size_label = CTkLabel(app, text="Tamaño del audio: ")
audio_size_label.grid(row=6, column=2)

download_mp4_button = CTkButton(app, text="\nDescargar en formato MP4\n", command=lambda: Thread(target=download, args=(highest_resolution, "mp4", download_mp4_button)).start(), width=170)
download_mp4_button.grid(row=7, column=1, padx=10)

download_mp3_button = CTkButton(app, text="\nDescargar en formato MP3\n", command=lambda: Thread(target=download, args=(audio, "mp3", download_mp3_button)).start(), width=170)
download_mp3_button.grid(row=7, column=2, padx=10)

progress_download_label = CTkLabel(app, text="Progreso de la descarga: ")
progress_download_label.grid(row=8, column=1, columnspan=2)

progress_bar = CTkProgressBar(app, width=300, height=15)
progress_bar.grid(row=9, column=1, columnspan=2)
progress_bar.set(0)

root.mainloop()