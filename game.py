from tkinter import *
import ctypes
from tkinter.font import *
from guts import Guts
from numpy import *
class MyGame(Tk):
    '''
    This class represents the game itself. It has a window with several kinds of frames.
    '''
    def __init__(self, *args, bg='sky blue', **kwargs):
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
        Tk.__init__(self, *args, **kwargs)
        bin = Frame(self)
        bin.pack(side = "top", fill = "both", expand = True)
        self.geometry("1500x1200")
        self.title("Vector Vision - Primitives")
        self.bg = bg
        self.gameRunning = False
        self.main = self.MainMenu(bin, self, bg)
        self.help = self.HelpMenu(bin, self, bg)
        self.gameplay = self.Gameplay(bin, self, bg)
        self.main.grid(row = 0, column = 0, sticky = "nsew")
        self.help.grid(row = 0, column = 0, sticky = "nsew")
        self.gameplay.grid(row = 0, column = 0, sticky = "nsew")
        self.frames = {"MainMenu": self.main, "HelpMenu": self.help, "Gameplay": self.gameplay}
        bin.grid_rowconfigure(0, weight=1)
        bin.grid_columnconfigure(0, weight=1)
        self.showFrame("MainMenu")
        self.bind("<KeyPress>", self.gameplay.key_down)
        self.bind("<KeyRelease>", self.gameplay.key_up)
        self.refresh()

    def showFrame(self, frame):
        self.gameplay.guts.act([], self.gameplay.canvas)
        self.frames[frame].tkraise()

    def refresh(self):
        self.gameplay.respond()
        if self.gameRunning:
            self.after(16, self.refresh)

    class MainMenu(Frame):
        '''
        This class represents the opening menu of the game
        '''
        def __init__(self, parent, controller, bg):
            Frame.__init__(self, parent)
            self.controller = controller
            titleMessage = Label(self, text = "Welcome to Vector Vision!", font = Font(family = "Helvetica", size = 40, weight = "bold"))
            titleMessage.pack(pady = 10)
            description = Label(self, text = "Use WASD to move and arrow keys to look around \n\n Press [I] to enter editor mode, where you can add lines and vertices: \n-->[Q] connects a new line to an existing point; \n-->[R] creates a new point; \n\n Press M to switch movement modes (not yet a feature) \n\n Press H for help", font = Font(size = 15, family = "Helvetica"))
            description.pack(pady = 60)
            button = Button(self, text = "Play", width = 20, height = 5, command = self.play)
            button.pack()
            self.config(bg=bg)

        def play(self):
            self.controller.showFrame("Gameplay")

        def tkraise(self, *args, **kwargs):
            Frame.tkraise(self, *args, **kwargs)
            self.controller.gameRunning = False
    
    class HelpMenu(Frame):
        '''
        This class represents a help screen
        '''
        def __init__(self, parent, controller, bg):
            Frame.__init__(self, parent)
            self.controller = controller
            titleMessage = Label(self, text = "Help Screen", font = Font(family = "Helvetica", size = 30, weight = "bold"))
            titleMessage.pack(pady = 10)
            description = Label(self, text = "Use WASD to move and arrow keys to look around \n\n Press [I] to enter editor mode, where you can add lines and vertices: \n-->[Q] connects a new line to an existing point; \n-->[R] creates a new point; \n\n Press M to switch movement modes (not yet a feature) \n\n Press H for help", font = Font(size = 15, family = "Helvetica"))
            description.pack(pady = 10)
            button = Button(self, text = "Play", width = 20, height = 5, command = self.play)
            button.pack()
            self.config(bg=bg)
        
        def play(self):
            self.controller.showFrame("Gameplay")

        def tkraise(self, *args, **kwargs):
            Frame.tkraise(self, *args, **kwargs)
            self.controller.gameRunning = False

    class Gameplay(Frame):
        '''
        This class represents the actual gameplay
        '''
        def __init__(self, parent, controller, bg):
            Frame.__init__(self, parent)
            self.controller = controller
            self.canvas = Canvas(self)
            self.guts = Guts(pointLocations = matrix([[-1,-1,-1,-1, 1, 1,1,1,0,3,0,0,  1,  2,1.5,1.7],
                                [-1,-1, 1, 1,-1,-1,1,1,0,0,2,0,1.5,1.3,  2,1.4],
                                [ 1, 3, 1, 3, 1, 3,1,3,0,0,0,1,1.3,1.1,1.2,  2]], float32), 
                    
                        linePointIndices = matrix([[0,2,4,6,0,4,6,2,1,5,7,3,8, 8, 8,12,12,13,12,13,14],
                                [1,3,5,7,4,6,2,0,5,7,3,1,9,10,11,13,14,14,15,15,15]], int32))

            self.buttons = []
            self.canvas.config(bg=bg)
            self.canvas.pack(fill="both", expand=True)

        def key_down(self, event):
            if not event.keycode in self.buttons:
                self.buttons.append(event.keycode)

        def key_up(self, event):
            if event.keycode in self.buttons:
                self.buttons.pop(self.buttons.index(event.keycode))
                self.guts.interact(event.keycode, self.canvas)
                if event.keycode == 72:
                    self.help()

        def respond(self):
            if self.buttons:
                self.guts.act(self.buttons, self.canvas)

        def help(self):
            self.controller.showFrame("HelpMenu")

        def tkraise(self,*args,**kwargs):
            Frame.tkraise(self, *args, **kwargs)
            self.controller.gameRunning = True
            self.controller.refresh()

        
if __name__ == "__main__":
    game = MyGame(bg="indigo")
    game.mainloop()

        
            
