from tkinter import *
from PIL import Image, ImageTk
import random

def getPressedKeys(event):
    '''Получение нажатых кнопок'''
    global pressedKeys
    if event.keysym == 'space':
        if not isJumping:
            startJump()
    elif event.char in keys:
        pressedKeys.add(event.char)
        if not isMoving:
            startMove()

def getReleasedKeys(event):
    '''Получение отжатых кнопок'''
    global pressedKeys, isMoving, directionX    
    if event.keysym != 'space':
        directionX = 0  
    try:
        pressedKeys.discard(event.char)
        pressedKeys.discard('ф')
        pressedKeys.discard('в')
    except KeyError:
        pass
    
def startMove():
    global isMoving       
    isMoving = True
    move()

def startJump():
    global isJumping, velocity, sightSide
    isJumping = True
    velocity = -35
    sightSide = canvas.itemcget(mario, "image")
    if sightSide == 'pyimage2':
        canvas.itemconfig(mario, image=marioJumpPhoto)
    else:
        canvas.itemconfig(mario, image=marioJumpPhotoFlipped)
    jump()

def move():
    '''Передвижение на a/d'''
    global directionX, pressedKeys, process
    currentX = canvas.coords(mario)[0]
    if 'a' in pressedKeys or 'ф' in pressedKeys:
        if not isJumping:
            canvas.itemconfig(mario, image=marioPhotoFlipped)
        directionX = -1
    elif 'd' in pressedKeys or 'в' in pressedKeys:
        if not isJumping:
            canvas.itemconfig(mario, image=marioPhoto)
        directionX = 1
    updateMove(directionX, currentX)
    if directionX != 0:
        process = window.after(16, move)

def jump():
    '''Прыжок'''
    global targetY, velocity
    currentY = canvas.coords(mario)[1]
    updateJump(currentY)
    if velocity != 0:
        window.after(16, jump)
        
def updateMove(directionX, currentX):
    '''Анимация передвижения'''
    global isMoving, process
    currentX += directionX * speed
    if directionX == 0:
        isMoving = False
        window.after_cancel(process)
    canvas.coords(mario, currentX, canvas.coords(mario)[1])
    
def updateJump(currentY):
    '''Анимация прыжка'''
    global isJumping, velocity, sightSide
    velocity += gravity * 0.016
    currentY += velocity
    if currentY + 47 > canvas.coords(ground)[1] and canvas.coords(mario)[0] < canvas.coords(ground)[2] and canvas.coords(mario)[0] > canvas.coords(ground)[0]:  #Проверка на землю
        currentY = canvas.coords(ground)[1] - 47
        velocity = 0
        isJumping = False
        canvas.itemconfig(mario, image=sightSide)
    canvas.coords(mario, canvas.coords(mario)[0], currentY)

def checkCoords():
    '''Проверка координат персонажа на выход за границы экрана'''
    global velocity
    currentCoords = canvas.coords(mario)
    leftSideOfAbyss1 = coordsOfObjects[3][1][0]
    rightSideOfAbyss1 = coordsOfObjects[3][1][2]
    leftSideOfAbyss2 = coordsOfObjects[4][1][0]
    rightSideOfAbyss2 = coordsOfObjects[4][1][2]
    centerOfAbyss1 = (leftSideOfAbyss1 + rightSideOfAbyss1) // 2
    centerOfAbyss2 = (leftSideOfAbyss2 + rightSideOfAbyss2) // 2
    if currentCoords[0] > window.winfo_screenwidth():   #Проверка на правую границу экрана
        canvas.coords(mario, 30, canvas.coords(mario)[1])
        resetEnvironment()
    if currentCoords[0] < 30:   #Проверка на левую границу экрана
        canvas.coords(mario, 30, canvas.coords(mario)[1])
    if (abs(currentCoords[0] - centerOfAbyss1) < centerOfAbyss1 - leftSideOfAbyss1 or abs(currentCoords[0] - centerOfAbyss2) < centerOfAbyss2 - leftSideOfAbyss2) and currentCoords[1] > 690:  #Проверка на бездну
        velocity += gravity * 0.016
        canvas.coords(mario, canvas.coords(mario)[0], canvas.coords(mario)[1] + velocity)
        if currentCoords[1] > screenHeight:
            window.destroy()
    for i in range(3):   #Изменение окружения при пересечении правой границы экрана
        if abs(coordsOfObjects[i][1][0] - currentCoords[0]) < 20 and abs(coordsOfObjects[i][1][1] - currentCoords[1]) < 50:
            canvas.coords(mario, 30, canvas.coords(mario)[1])
    window.after(16, checkCoords)

def resetEnvironment():
    '''Обновление окружения при выходе за границы экрана'''
    global coordsOfObjects
    for i in range(3):   #Создание новых препятствий
        tube = canvas.create_image(random.randrange(700, 1700, 300), screenHeight // 2 + 153, image=marioPhoto)
        canvas.delete(coordsOfObjects[0][0])
        coordsOfObjects.pop(0)
        coordsOfObjects.append([tube, canvas.coords(tube)])
    for i in range(2):   #Создание бездн
        positionX0 = random.randrange(500, 1700, 700)
        if abs(positionX0 - all(coordsOfObjects[i][1][0] for i in range(3))) > 300:
            position = [positionX0, screenHeight // 2 + 195, positionX0 + random.randint(100, 200), screenHeight // 2 + 208]
            abyss = canvas.create_rectangle(position, fill='lightblue', outline='')
            canvas.delete(coordsOfObjects[0][0])
            coordsOfObjects.pop(0)
            coordsOfObjects.append([abyss, canvas.coords(abyss)])

#Глобальные переменные
process = None
isJumping = False
isMoving = False
isOnGround = True
velocity = 0
gravity = 200
directionX = 0
targetY = 0
speed = 15
pressedKeys = set()
keys = ['a', 'ф', 'd', 'в']

#Создание окна приложения
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
marioPhoto = ImageTk.PhotoImage(Image.open('mario_sprite.png').resize((170, 170)))
marioPhotoFlipped = ImageTk.PhotoImage(Image.open('mario_sprite.png').resize((170, 170)).transpose(Image.FLIP_LEFT_RIGHT))
marioJumpPhoto = ImageTk.PhotoImage(Image.open('mario_jump.png').resize((170, 170)))
marioJumpPhotoFlipped = ImageTk.PhotoImage(Image.open('mario_jump.png').resize((170, 170)).transpose(Image.FLIP_LEFT_RIGHT))
mario = canvas.create_image(30, screenHeight // 2 + 153, image=marioPhoto)

#Создание объектов окружения
ground = canvas.create_line(0, screenHeight // 2 + 200, screenWidth - 100, screenHeight // 2 + 200, fill='black', width=8)
coordsOfObjects = []
for i in range(3):
    tube = canvas.create_image(random.randrange(700, 1700, 300), screenHeight // 2 + 153, image=marioPhoto)
    coordsOfObjects.append([tube, canvas.coords(tube)])
for i in range(2):   
    positionX0 = random.randrange(500, 1700, 700)
    if abs(positionX0 - all(coordsOfObjects[i][1][0] for i in range(3))) > 300:
        position = [positionX0, screenHeight // 2 + 195, positionX0 + random.randint(100, 200), screenHeight // 2 + 208]
        abyss = canvas.create_rectangle(position, fill='lightblue', outline='')
        coordsOfObjects.append([abyss, canvas.coords(abyss)])

canvas.tag_raise(mario)    #Отрисовка поверх других объектов
#Параллельные циклы
checkCoords()

#Управление клавишами
window.bind('<KeyPress>', getPressedKeys)
window.bind('<KeyRelease>', getReleasedKeys)
window.bind('<Escape>', exit)

window.mainloop()