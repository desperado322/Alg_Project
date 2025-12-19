from tkinter import *
from PIL import Image, ImageTk

def getPressedKeys(event):
    '''Получение нажатых кнопок'''
    global pressedKeys
    pressedKeys.add(event.keysym)
    if event.keysym == 'a' or event.keysym == 'd':
        if not isMoving:
            startMove()

def getReleasedKeys(event):
    '''Получение отжатых кнопок'''
    global pressedKeys, isMoving, directionX
    if event.keysym == 'space':
        if not isJumping:
            startJump()
    else:
        directionX = 0
    pressedKeys.discard(event.keysym)

def move():
    '''Передвижение на a/d'''
    global directionX
    if isMoving:
        currentX = canvas.coords(mario)[0]
        if 'a' in pressedKeys:
            canvas.itemconfig(mario, image=marioPhotoFlipped)
            directionX = -1
        elif 'd' in pressedKeys:
            canvas.itemconfig(mario, image=marioPhoto)
            directionX = 1
        updateMove(directionX, currentX)
        window.after(16, move)
def jump():
    '''Прыжок'''
    global targetY
    global velocity
    if isJumping:
        currentY = canvas.coords(mario)[1]
        updateJump(currentY)
        window.after(16, jump)
        
def startMove():
    global isMoving       
    isMoving = True
    move()

def startJump():
    global isJumping
    global velocity
    isJumping = True
    velocity = -30
    jump()

def updateMove(directionX, currentX):
    '''Анимация передвижения'''
    global isMoving
    currentX += directionX * 8 
    if directionX == 0:
        isMoving = False
    canvas.coords(mario, currentX, canvas.coords(mario)[1])
    
def updateJump(currentY):
    '''Анимация прыжка'''
    global isJumping
    global velocity
    velocity = velocity + gravity * 0.016
    currentY += velocity
    if currentY + 55 > canvas.coords(ground)[1] and canvas.coords(mario)[0] < canvas.coords(ground)[2]:
        currentY = canvas.coords(ground)[1] - 55
        velocity = 0
        isJumping = False
    canvas.coords(mario, canvas.coords(mario)[0], currentY)

isJumping = False
isMoving = False
isOnGround = True
velocity = 0
gravity = 200
directionX = 0
targetY = 0
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
ground = canvas.create_line(0, screenHeight // 2 + 200, screenWidth - 100, screenHeight // 2 + 200, fill='black', width=8) 

#Создание персонажа
marioPhoto = ImageTk.PhotoImage(Image.open('mario_sprite.png').resize((100, 100)))
marioPhotoFlipped = ImageTk.PhotoImage(Image.open('mario_sprite.png').resize((100, 100)).transpose(Image.FLIP_LEFT_RIGHT))
mario = canvas.create_image(screenWidth // 2, screenHeight // 2 + 145, image=marioPhoto)

#Управление
window.bind('<KeyPress>', getPressedKeys)
window.bind('<KeyRelease>', getReleasedKeys)
window.bind('<Escape>', exit)

window.mainloop()
