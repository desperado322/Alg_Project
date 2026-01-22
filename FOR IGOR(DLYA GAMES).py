from tkinter import *
from PIL import Image, ImageTk

class App(Tk):

    def __init__(self):

        super().__init__()

        self.title('Mario')
        self.screenWidth, self.screenHeight = 1920, 1080
        self.geometry(f'{self.screenWidth}x{self.screenHeight}')
        #self.resizable(False, False) #это для прода
        #self.attributes('-fullscreen', True) #это для тестов
        self.iconphoto(False, PhotoImage(file='mario_icon.png'))

        self.init_main_menu()

    def init_main_menu(self):

        #Главная менюшка
        self.menuCanvas = Canvas(self, bg='lightblue', width=self.screenWidth, height=self.screenHeight)

        bgPhoto = ImageTk.PhotoImage((Image.open('bliss.jpg').resize((self.screenWidth, self.screenHeight))))
        bgLabel = Label(self.menuCanvas, image = bgPhoto)
        textPhoto = ImageTk.PhotoImage((Image.open('mario_label.png').resize((530*2, 240*2))))
        textLabel = Label(self.menuCanvas, image = textPhoto, bg = 'red')

        bgLabel.place(x = 0, y = 0)
        textLabel.place(x = 420, y = 90)
        self.menuCanvas.pack(anchor='center')

if __name__ == '__main__':
    
    app = App()
    app.mainloop()