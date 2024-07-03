from email.mime import image
from fileinput import filename
from gettext import install
from glob import glob
from multiprocessing.sharedctypes import Value
from tkinter import ttk
from tkinter.tix import IMAGE
from turtle import bgcolor, color, width
from webbrowser import get
import audio_metadata
from tkinter import *
import tkinter as tk
from PIL import ImageTk, Image
from io import BytesIO
from click import style
import pygame
from pygame import mixer
import os
import time
import soundfile as sf
import librosa as sa

# import ttkbootstrap as ttk

# from mutagen.mp3 import MP3

## INITIALISE
window = Tk()
# window = ttk.Window(themename="lumen")
# style = ttk.Style("darkly")
# style.configure("TButton", borderwidth=0)
window.title("theMusicPlayer")
window.geometry("450x800")
window.configure(bg="#292B59")
mixer.init()
songstatus = StringVar()
songstatus.set("Choosing")
global paused
paused = False
global playlist
global currentsong
song_length = 0
global canvas
global new_img
global img
global image_container
canvas = Canvas(window, width=300, height=300)
canvas.pack(pady=(20, 0))


new_img = Image.open(r"Assets\placeholder.png")
new_img = new_img.resize((300, 300), Image.LANCZOS)
new_img = ImageTk.PhotoImage(new_img)
image_container = canvas.create_image(150, 150, anchor=CENTER, image=new_img)
img = ""
playlistframe = Frame(window)
playlist = Listbox(
    playlistframe,
    selectmode=SINGLE,
    fg="black",
    font=("arial", 10),
    width=40,
    borderwidth=0,
    highlightcolor="lightgrey",
)
currentsong = playlist.get(ACTIVE)

## FUNCTIONS

## ALBUM ART
def albumart(audiofile):
    global canvas
    # global img
    global new_img
    global image_container
    metadata = audio_metadata.load(audiofile)
    try:
        metadata.pictures[0].data
    except IndexError:
        print("No Image Found.")
        new_img = Image.open(r"Assets\placeholder.png")
        new_img = new_img.resize((300, 300), Image.LANCZOS)
        new_img = ImageTk.PhotoImage(new_img)
    else:
        artwork = metadata.pictures[0].data
        stream = BytesIO(artwork)
        img = ImageTk.PhotoImage(Image.open(stream))
        img = ImageTk.getimage(img)
        new_img = img.resize((300, 300), Image.LANCZOS)
        new_img = ImageTk.PhotoImage(new_img)
    image_container = canvas.create_image(150, 150, anchor=CENTER, image=new_img)


def playsong(x):
    # currentsong=playlist.get(ACTIVE)
    # global song_length
    # print(currentsong)
    global currentsong
    if playlist.curselection():
        global canvas
        mixer.music.load(currentsong)
        albumart(currentsong)
        canvas.itemconfig(image_container, image=new_img)
        songstatus.set("Playing")
        mixer.music.play(start=x)
        play_time()
        slider_pos = int(song_length)
        position_slider.config(to=slider_pos, value=0)
        songname.config(text=currentsong)
        # pauseplaybtn.config(
        #     image=ImageTk.PhotoImage(
        #         Image.open("D:\Projects\PyCharmProjects\MusicPlayer\pause.png").resize(
        #             (30, 30), Image.ANTIALIAS
        #         )
        # )
        # )
    else:
        songname.config(text="No song selected.")


def stopsong():
    songstatus.set("Stopped")
    mixer.music.stop()
    playlist.selection_clear(0, END)


def issongpaused(is_paused):
    global paused
    global currentsong
    paused = is_paused
    if currentsong == playlist.get(ACTIVE):
        if paused:
            mixer.music.unpause()
            paused = False
            songstatus.set("Resuming")
            pausephoto = ImageTk.PhotoImage(
                Image.open(r"Assets\pause.png")
            )
        else:
            songstatus.set("Paused")
            mixer.music.pause()

            paused = True
    else:
        currentsong = playlist.get(ACTIVE)
        playsong(0)


def nextsong():
    global currentsong
    currentsong = playlist.get(ACTIVE)
    next_song = playlist.curselection()
    # print(next_song[0])
    next_song = next_song[0] + 1
    if next_song < playlist.size():
        currentsong = playlist.get(next_song)
        playsong(0)
    else:
        issongpaused(paused)
    playlist.selection_clear(0, END)
    playlist.activate(next_song)
    playlist.selection_set(next_song, last=None)


def prevsong():
    global currentsong
    currentsong = playlist.get(ACTIVE)
    if pygame.mixer.music.get_pos() / 1000 > 1:
        playsong(0)
        prev_song = playlist.curselection()
        prev_song = prev_song[0]
    else:
        prev_song = playlist.curselection()
        # print(next_song[0])
        prev_song = prev_song[0] - 1

        currentsong = playlist.get(prev_song)
        playsong(0)
    playlist.selection_clear(0, END)
    playlist.activate(prev_song)
    playlist.selection_set(prev_song, last=None)


def play_time():
    current_time = pygame.mixer.music.get_pos() / 1000
    converted_current_time = time.strftime("%M:%S", time.gmtime(current_time))
    f = sf.SoundFile(currentsong)
    global song_length
    song_length = f.frames / f.samplerate
    converted_song_length = time.strftime("%M:%S", time.gmtime(song_length))
    position_slider.config(value=current_time)
    status_bar.config(text=f"{converted_current_time}")
    endtime.config(text=f"{converted_song_length}")
    status_bar.after(1000, play_time)


def slide(x):
    # print(f"{int(position_slider.get())} of {int(song_length)}")
    playsong(position_slider.get())


## Slider
slider_frame = Frame(window, bg="#292B59")
slider_frame.pack(pady=(0, 20))
songname = Label(slider_frame, text="", bg="#292B59")
position_slider = ttk.Scale(
    slider_frame,
    from_=0,
    to=100,
    orient=HORIZONTAL,
    length=300,
    value=0,
    # bg="#292B59",
    command=slide,
)
# Status Bar
status_bar = Label(slider_frame, text="00:00", bd=1, anchor=CENTER)
endtime = Label(slider_frame, text="00:00")
songname.grid(row=0, column=1, pady=10)
status_bar.grid(row=1, column=0, padx=(0, 5))
position_slider.grid(row=1, column=1)
endtime.grid(row=1, column=2, padx=(5, 0))

## BUTTONS

controls_frame = Frame(window, bg="#292B59")
controls_frame.pack(pady=(None))


# playbtnimg = Image.open(r'Assets\playbuttonarrowhead.png')
# newimg1 = playbtnimg.resize((20,20), Image.ANTIALIAS)
# newimg1 = ImageTk.PhotoImage(newimg1)
# playbtn=Button(window,height=30,width=50,bg='white',image=newimg1,command=playsong)

pauseplaybtnimg = Image.open(r"Assets\play.png")
newimg2 = pauseplaybtnimg.resize((60, 60), Image.ANTIALIAS)
newimg2 = ImageTk.PhotoImage(newimg2)
pauseplaybtn = Button(
    controls_frame,
    height=60,
    width=60,
    bg="#292B59",
    borderwidth=0,
    image=newimg2,
    command=lambda: issongpaused(paused),
)

# stopbtnimg = Image.open(r"Assets\black-square.png")
# newimg3 = stopbtnimg.resize((20, 20), Image.ANTIALIAS)
# newimg3 = ImageTk.PhotoImage(newimg3)
# stopbtn = Button(
#     controls_frame,
#     height=50,
#     width=50,
#     bg="white",
#     borderwidth=0,
#     image=newimg3,
#     command=stopsong,
# )

nextbtnimg = Image.open(r"Assets\nextpng.png")
newimg4 = nextbtnimg.resize((20, 30), Image.ANTIALIAS)
newimg4 = ImageTk.PhotoImage(newimg4)
nextbtn = Button(
    controls_frame,
    height=60,
    width=80,
    bg="#292B59",
    borderwidth=0,
    image=newimg4,
    command=nextsong,
)

prevbtnimg = Image.open(r"Assets\prevpng.png")
newimg5 = prevbtnimg.resize((20, 30), Image.ANTIALIAS)
newimg5 = ImageTk.PhotoImage(newimg5)
prevbtn = Button(
    controls_frame,
    height=60,
    width=80,
    bg="#292B59",
    borderwidth=0,
    image=newimg5,
    command=prevsong,
)
prevbtn.grid(row=1, column=0, padx=10)
pauseplaybtn.grid(row=1, column=1, padx=10)
nextbtn.grid(row=1, column=2, padx=10)
# canvas.create_window(60,320,anchor=CENTER,window=prevbtn)
# # canvas.create_window(130,320,anchor=CENTER,window=playbtn)
# canvas.create_window(200,320,anchor=CENTER,window=pauseplaybtn)
# # canvas.create_window(270,320,anchor=CENTER,window=stopbtn)
# canvas.create_window(340,320,anchor=CENTER,window=nextbtn)


## Playlist
# playlistframe = Frame(window)
playlistframe.pack(pady=(30, 0))

playlist.pack(side="left", fill="y")
scrollbarplaylist = Scrollbar(playlistframe, orient="vertical", borderwidth=0)
scrollbarplaylist.config(command=playlist.yview)
scrollbarplaylist.pack(side="right", fill="y")
playlist.config(yscrollcommand=scrollbarplaylist.set)
os.chdir(r"Assets\Songs")
songs = os.listdir()
for s in songs:
    playlist.insert(END, s)


## BG SHIT
# bg = PhotoImage(file = "Cinnamint.png")
# canvas1 = Canvas(window,width=400,height=600)
# canvas1.pack(fill= "both", expand = True)
# canvas1.create_image(0,0, image=bg, anchor="nw")

window.mainloop()
