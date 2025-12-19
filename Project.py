from tkinter import *
from PIL import Image, ImageTk

def getPressedKeys(event):
    global pressedKeys
    pressedKeys.add(event.keysym)
    if event.keysym == 'a' or event.keysym == 'd':
        if not isMoving:
            startMove()

def getReleasedKeys(event):
    global pressedKeys, isMoving
    pressedKeys.discard(event.keysym)

def move():
    global targetX
    if isMoving:
        currentX = canvas.coords(mario)[0]
        if 'a' in pressedKeys:
            targetX = currentX - 10
            canvas.itemconfig(mario, image=marioPhotoFlipped)
        elif 'd' in pressedKeys:
            targetX = currentX + 10
            canvas.itemconfig(mario, image=marioPhoto)
        updateMove(targetX, currentX)
        window.after(16, move)

def startMove():
    global isMoving       
    isMoving = True
    move()

def updateMove(targetX, currentX):
    global isMoving
    step = 0
    distance = targetX - currentX
    if abs(distance) > 1:
        step = distance * 0.8
        currentX += step
    else:
        isMoving = False
        if abs(step) > abs(distance):
            currentX = targetX
    canvas.coords(mario, currentX, canvas.coords(mario)[1])

isMoving = False
targetX = 0
pressedKeys = set()

#Создание окна
window = Tk()
screenWidth = window.winfo_screenwidth()
screenHeight = window.winfo_screenheight()
window.attributes('-fullscreen', True)
window.title('Mario')
icon = PhotoImage(file='mario_icon.png')
window.iconphoto(False, icon)
canvas = Canvas(window, bg='lightblue', width=screenWidth, height=screenHeight)
canvas.pack(anchor='center')

#Создание персонажа
marioPhoto = ImageTk.PhotoImage(Image.open('mario_sprite.png').resize((100, 100)))
marioPhotoFlipped = ImageTk.PhotoImage(Image.open('mario_sprite.png').resize((100, 100)).transpose(Image.FLIP_LEFT_RIGHT))
mario = canvas.create_image(screenWidth // 2, screenHeight // 2, image=marioPhoto)

#Управление
window.bind('<KeyPress>', getPressedKeys)
window.bind('<KeyRelease>', getReleasedKeys)
window.bind('<Escape>', exit)

window.mainloop()
