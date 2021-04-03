from tkinter import messagebox, Label, Tk
from PIL import Image, ImageTk
import os
import vlc
import worker

title = "Video Looper"

root = Tk()
root.title(title)
root.geometry("280x180")

_label = None
_img = None
_path = os.path.join(os.getcwd(), 'img')


def paint():
    global _label, _img, _path

    Label(root, text='').pack()

    _label = Label(root, text="Cargando...", font=('helvetica', 12, 'bold'))
    _label.pack()

    Label(root, text='').pack()

    img = ImageTk.PhotoImage(file=os.path.join(_path, "usb.png"))
    _img = Label(image=img)
    _img.image = img
    _img.pack()

    Label(root, text='').pack()


def waiting():
    global _label, _img, _path
    _label.config(text='Inserte un dispositivo USB\npara reproducir en bucle')
    img = ImageTk.PhotoImage(file=os.path.join(_path, "usb.png"))
    _img.configure(image=img)
    _img.image = img


def reading():
    global _label, _img, _path
    _label.config(text='Buscando archivos para\nreproducir...')
    img = ImageTk.PhotoImage(file=os.path.join(_path, "loading.png"))
    _img.configure(image=img)
    _img.image = img


def playing():
    global _label, _img, _path
    _label.config(text='Reproduciendo...\n')
    img = ImageTk.PhotoImage(file=os.path.join(_path, "playing.png"))
    _img.configure(image=img)
    _img.image = img


def empty():
    global _label, _img, _path
    _label.config(text='No se han encontrado archivos\npara reproducir!')
    img = ImageTk.PhotoImage(file=os.path.join(_path, "empty.png"))
    _img.configure(image=img)
    _img.image = img


def close():
    if messagebox.askokcancel("Quit", "Si se cierra el programa no se auto reproducirá al insertar un USB. Está seguro desea salir?"):
        vlc.stop()
        worker.stop()
        root.destroy()


root.protocol("WM_DELETE_WINDOW", close)


def loop():
    root.mainloop()
