from tkinter import *
import ctypes
from tkinter.font import *
from guts import Guts
from numpy import *
class MyGame(Tk):
    '''
    This class represents the game itself. It has a window with several kinds of frames.
    '''
    def __init__(self, *args, **kwargs):
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
        Tk.__init__(self, *args, **kwargs)
        bin = Frame(self)
        self.geometry("1500x1200")
        self.title("Vector Vision - Primitives")
        bin.pack(fill="both",expand=True)
        self.main = self.MainMenu(bin, controller = self)
        self.help = self.HelpMenu(bin, controller = self)
        self.gameplay = self.Gameplay(bin, controller = self)
        self.main.grid(x = 0, y = 0, sticky = "nsew")
        self.help.grid(x = 0, y = 0, sticky = "nsew")
        self.gameplay.grid(x = 0, y = 0, sticky = "nsew")
        self.frames = {self.main.__name__: self.main, self.help.__name__: self.help, self.gameplay.__name__: self.gameplay}

    def showFrame(self, frame):
        self.frames[frame].tkraise()

    # this is a test edit of no consequence
    
    # random edit that has no effect

    # yet another edit with no effect

    class MainMenu(Frame):
        '''
        This class represents the opening menu of the game
        '''
        def __init__(self, parent, controller):
            Frame.__init__(self, parent)
            self.controller = controller
            titleMessage = Label(self, text = "Welcome to Vector Vision!", font = Font(family = "Comic Sans", size = 20, weight = "bold"))
            titleMessage.pack(pady = 10)
            description = Label(self, text = "Use WASD to move and arrow keys to look around \n Press I to enter editor mode, where:\n -->new line from/to existing point: Q \n --> new line from/to new point: R \n Press M to switch movement modes (not yet a feature) \n Press H for help", font = "Comic Sans")
            description.pack(pady = 10)
            button = Button(self, text = "Play", command = self.play)
            button.pack()

        def play(self):
            self.controller.showFrame("Gameplay")

    
    class HelpMenu(Frame):
        '''
        This class represents a help screen
        '''
        def __init__(self, parent, controller):
            Frame.__init__(self, parent)
            self.controller = controller
            titleMessage = Label(self, text = "Help Screen", font = Font(family = "Comic Sans", size = 20, weight = "bold"))
            titleMessage.pack(pady = 10)
            description = Label(self, text = "Use WASD to move and arrow keys to look around \n Press I to enter editor mode, where:\n -->new line from/to existing point: Q \n --> new line from/to new point: R \n Press M to switch movement modes (not yet a feature) \n Press H for help", font = "Comic Sans")
            description.pack(pady = 10)
            button = Button(self, text = "Play", command = self.play)
            button.pack()
        
        def play(self):
            self.controller.showFrame("Gameplay")

    class Gameplay(Frame):
        '''
        This class represents the actual gameplay
        '''
        def __init__(self, parent, controller):
            Frame.__init__(self, parent)
            self.controller = controller
            self.canvas = Canvas(self)
            self.guts = Guts(pointLocations = matrix([[-1,-1,-1,-1, 1, 1,1,1,0,3,0,0,  1,  2,1.5,1.7],
                                [-1,-1, 1, 1,-1,-1,1,1,0,0,2,0,1.5,1.3,  2,1.4],
                                [ 1, 3, 1, 3, 1, 3,1,3,0,0,0,1,1.3,1.1,1.2,  2]], float32), 
                    
                        linePointIndices = matrix([[0,2,4,6,0,4,6,2,1,5,7,3,8, 8, 8,12,12,13,12,13,14],
                                [1,3,5,7,4,6,2,0,5,7,3,1,9,10,11,13,14,14,15,15,15]], int32))

            self.buttons = []

            self.bind("<KeyPress>", self.key_down)
            self.bind("<KeyRelease>", self.key_up)
            self.config(bg='sky blue')
            self.pack(fill="both",expand=True)
            self.respond()

        def key_down(self, event):
            if not event.keycode in self.buttons:
                self.buttons.append(event.keycode)

        def key_up(self, event):
            if event.keycode in self.buttons:
                self.buttons.pop(self.buttons.index(event.keycode))
                self.interact(event.keycode, self.canvas)
                if event.keycode == 72:
                    self.help()

        def respond(self):
            if self.buttons:
                self.guts.act(self.buttons, self.canvas)
            self.after(16, self.respond)

        def help(self):
            self.controller.showFrame("HelpMenu")

        respond()

        
if __name__ == "__main__":
    game = MyGame()
    game.mainloop()

        
            
