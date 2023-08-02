from tkinter import *
import ctypes
from guts import Guts
import random
from numpy import *
print('etf')
ctypes.windll.shcore.SetProcessDpiAwareness(True)


window = Tk()
entranceFrame = Frame()
playFrame = Frame(window)
window.geometry("1500x1200")
window.title("Vector Vision - Primitives")

canvas = Canvas(playFrame)
guts = Guts(matrix([[-1,-1,-1,-1, 1, 1,1,1,0,3,0,0,  1,  2,1.5,1.7],
                    [-1,-1, 1, 1,-1,-1,1,1,0,0,2,0,1.5,1.3,  2,1.4],
                    [ 1, 3, 1, 3, 1, 3,1,3,0,0,0,1,1.3,1.1,1.2,  2]], float32), 
        
            matrix([[0,2,4,6,0,4,6,2,1,5,7,3,8, 8, 8,12,12,13,12,13,14],
                    [1,3,5,7,4,6,2,0,5,7,3,1,9,10,11,13,14,14,15,15,15]], int32))

buttons = []

def key_down(event):
    if not event.keycode in buttons:
        buttons.append(event.keycode)

def key_up(event):
    if event.keycode in buttons:
        buttons.pop(buttons.index(event.keycode))
        guts.interact(event.keycode, canvas)

def respond():
    if buttons:
        guts.act(buttons, canvas)
    window.after(16, respond)


window.bind("<KeyPress>", key_down)
window.bind("<KeyRelease>", key_up)
respond()


canvas.config(bg='sky blue')
canvas.pack(fill="both",expand=True)

playFrame.pack(expand=1,fill=BOTH)
window.mainloop()
