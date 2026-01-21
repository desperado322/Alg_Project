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
    if sightSide == 'pyimage6' or sightSide == 'pyimage8' or sightSide == 'pyimage2':
        canvas.itemconfig(mario, image=marioJumpPhoto)
    elif sightSide == 'pyimage7' or sightSide == 'pyimage9' or sightSide == 'pyimage3':
        canvas.itemconfig(mario, image=marioJumpPhotoFlipped)
    jump()

def move():
    '''Передвижение на a/d'''
    global directionX, pressedKeys, process, count, sightSide
    count += 1
    currentX = canvas.coords(mario)[0]
    if 'a' in pressedKeys or 'ф' in pressedKeys:
        if not isJumping:
            if count % 2 == 1:
                canvas.itemconfig(mario, image=marioRunAnimationPhoto1Flipped)
            else:
                canvas.itemconfig(mario, image=marioRunAnimationPhoto2Flipped)
        directionX = -1
        sightSide = marioPhotoFlipped
    elif 'd' in pressedKeys or 'в' in pressedKeys:
        if not isJumping:
            if count % 2 == 1:
                canvas.itemconfig(mario, image=marioRunAnimationPhoto1)
            else:
                canvas.itemconfig(mario, image=marioRunAnimationPhoto2)
        directionX = 1
        sightSide = marioPhoto
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
    global isMoving, process, sightSide
    currentX += directionX * speed
    if directionX == 0:
        isMoving = False
        canvas.itemconfig(mario, image=sightSide)
        window.after_cancel(process)
    canvas.coords(mario, currentX, canvas.coords(mario)[1])
    
def updateJump(currentY):
    '''Анимация прыжка'''
    global isJumping, velocity, sightSide
    velocity += gravity * 0.016
    currentY += velocity
    if currentY + 47 > canvas.coords(groundLine)[1] and canvas.coords(mario)[0] < canvas.coords(groundLine)[2] and canvas.coords(mario)[0] > canvas.coords(groundLine)[0]:  #Проверка на землю
        currentY = canvas.coords(groundLine)[1] - 47
        velocity = 0
        isJumping = False
        if sightSide == 'pyimage6' or sightSide == 'pyimage8' or sightSide == 'pyimage2':
            canvas.itemconfig(mario, image=marioPhoto)
        elif sightSide == 'pyimage7' or sightSide == 'pyimage9' or sightSide == 'pyimage3':
            canvas.itemconfig(mario, image=marioPhotoFlipped)
    canvas.coords(mario, canvas.coords(mario)[0], currentY)

def checkCoords():
    '''Проверка координат персонажа на коллизии'''
    global velocity, keys, pressedKeys, directionX
    currentCoords = canvas.coords(mario)
    #Координаты бездн
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
    if (abs(currentCoords[0] - centerOfAbyss1) < (centerOfAbyss1 - leftSideOfAbyss1) / 2 or abs(currentCoords[0] - centerOfAbyss2) < (centerOfAbyss2 - leftSideOfAbyss2) / 2) and currentCoords[1] > 690:  #Проверка на бездну
        if currentCoords[1] > 700:
            keys.clear()
            pressedKeys.clear()
            directionX = 0
        velocity += gravity * 0.016
        canvas.coords(mario, canvas.coords(mario)[0], canvas.coords(mario)[1] + velocity)
        if currentCoords[1] > screenHeight:
            window.destroy()
    for i in range(3):   #Проверка на столкновение с трубами
        if abs(coordsOfObjects[i][1][0] - currentCoords[0]) < 100 and abs(coordsOfObjects[i][1][1] - currentCoords[1]) < 100:
            canvas.coords(mario, coordsOfObjects[i][1][0] + (currentCoords[0] - coordsOfObjects[i][1][0]) * 1.18, canvas.coords(mario)[1])
    window.after(16, checkCoords)

def resetEnvironment():
    '''Обновление окружения при выходе за границы экрана'''
    global coordsOfObjects
    for i in range(3):   #Создание новых препятствий
        tube = canvas.create_image(random.randrange(700, 1700, 300), screenHeight // 2 + 153, image=tubePhoto)
        canvas.delete(coordsOfObjects[0][0])
        coordsOfObjects.pop(0)
        coordsOfObjects.append([tube, canvas.coords(tube)])
    for i in range(2):   #Создание бездн
        positionX0 = random.randrange(500, 1700, 700)
        if abs(positionX0 - all(coordsOfObjects[i][1][0] for i in range(3))) > 300:
            position = [positionX0, screenHeight // 2 + 195, positionX0 + random.randint(100, 200), screenHeight]
            abyss = canvas.create_rectangle(position, fill='lightblue', outline='')
            canvas.delete(coordsOfObjects[0][0])
            coordsOfObjects.pop(0)
            coordsOfObjects.append([abyss, canvas.coords(abyss)])
    canvas.tag_raise(mario)
    canvas.tag_raise(ground)

def movingOfEnemies():
    pass

#Глобальные переменные
process = None
isJumping = False
isMoving = False
isOnground = True
velocity = 0
gravity = 200
directionX = 0
targetY = 0
speed = 15
count = 0
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
marioRunAnimationPhoto1 = ImageTk.PhotoImage(Image.open('mario_run_animation_1.png').resize((170, 170)))
marioRunAnimationPhoto1Flipped = ImageTk.PhotoImage(Image.open('mario_run_animation_1.png').resize((170, 170)).transpose(Image.FLIP_LEFT_RIGHT))
marioRunAnimationPhoto2 = ImageTk.PhotoImage(Image.open('mario_run_animation_2.png').resize((170, 170)))
marioRunAnimationPhoto2Flipped = ImageTk.PhotoImage(Image.open('mario_run_animation_2.png').resize((170, 170)).transpose(Image.FLIP_LEFT_RIGHT))
mario = canvas.create_image(30, screenHeight // 2 + 153, image=marioPhoto)

#Создание объектов окружения
groundPhoto = ImageTk.PhotoImage(Image.open('ground.png').resize((screenWidth, 500)))
tubePhoto = ImageTk.PhotoImage(Image.open('tube.png').resize((300, 600)))
groundLine = canvas.create_line(0, screenHeight // 2 + 200, screenWidth - 100, screenHeight // 2 + 200, fill='black', width=8)
coordsOfObjects = []
for i in range(3):
    tube = canvas.create_image(random.randrange(700, 1700, 300), screenHeight // 2 + 153, image=tubePhoto)
    coordsOfObjects.append([tube, canvas.coords(tube)])
for i in range(2):   
    positionX0 = random.randrange(500, 1700, 700)
    if abs(positionX0 - all(coordsOfObjects[i][1][0] for i in range(3))) > 300:
        position = [positionX0, screenHeight // 2 + 195, positionX0 + random.randint(100, 200), screenHeight]
        abyss = canvas.create_rectangle(position, fill='lightblue', outline='')
        coordsOfObjects.append([abyss, canvas.coords(abyss)])
        groundPhoto = ImageTk.PhotoImage(Image.open('ground.png').resize((positionX0, 500)))
        ground = canvas.create_image(0, 990, image=groundPhoto)

#Создание врагов
'''mushroomPhoto = ImageTk.PhotoImage(Image.open('mushroom.png').resize((170, 170)))
coordsOfEnemies = []
for i in range(2):
    mushroom = canvas.create_image(random.randrange(700, 1700, 300), screenHeight // 2 + 153, image=mushroomPhoto)
    coordsOfEnemies.append([mushroom, canvas.coords(mushroom)])'''

#Отрисовка поверх других объектов
canvas.tag_raise(mario)
canvas.tag_raise(ground)

#Параллельные циклы
checkCoords()

#Управление клавишами
window.bind('<KeyPress>', getPressedKeys)
window.bind('<KeyRelease>', getReleasedKeys)
window.bind('<Escape>', exit)

window.mainloop()