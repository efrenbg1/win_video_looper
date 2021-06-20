from tkinter import messagebox, Label, Tk
from PIL import ImageTk
from PIL import Image
import os
from src import vlc, browser
import settings

title = "Video Looper"

root = Tk()
root.attributes("-fullscreen", True)
root.title(title)
root.config(cursor="none")


_bg = root.cget('bg')
_label = None
_img = None
_path = os.path.join(os.getcwd(), 'img')


def paint():
    global _label, _img, _path, _bg

    for ele in root.winfo_children():
        ele.destroy()

    root.configure(background=_bg)

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
    _label.config(text='\n\nPara añadir archivos o proyectar la\npantalla vaya a:\n\nhttps://{}\n\n\n(Esc para salir)'.format(settings.domain, settings.domain))
    img = ImageTk.PhotoImage(file=os.path.join(_path, "usb.png"))
    _img.configure(image=img)
    _img.image = img


def reading():
    global _label, _img, _path
    _label.config(text='Buscando archivos para\nreproducir...')
    imge = Image.open(os.path.join(_path, "loading.png"))
    img = ImageTk.PhotoImage(imge)
    _img.configure(image=img)
    _img.image = img


def playing():
    global _label, _img, _path, root
    for ele in root.winfo_children():
        ele.destroy()
    root.configure(background='black')


def esc(event):
    close()


def close():
    if messagebox.askokcancel("Quit", "Si se cierra el programa no se auto reproducirán los videos. ¿Seguro desea salir?"):
        vlc.stop()
        browser.stop()
        root.destroy()


root.bind('<Escape>', esc)
root.protocol("WM_DELETE_WINDOW", close)


def loop():
    root.mainloop()
