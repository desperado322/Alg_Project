from tkinter import *
from PIL import Image, ImageTk
from pygame import mixer
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
    if canvas.coords(mario)[1] == 693:
        velocity = -30
    else:
        velocity = -35
    sightSide = canvas.itemcget(mario, "image")
    if sightSide in ['pyimage3', 'pyimage7', 'pyimage9', 'pyimage11']:
        canvas.itemconfig(mario, image=marioJumpPhoto)
    elif sightSide in ['pyimage4', 'pyimage8', 'pyimage10', 'pyimage12']:
        canvas.itemconfig(mario, image=marioJumpPhotoFlipped)
    jump()

def move():
    '''Передвижение на a/d'''
    global directionX, pressedKeys, process, count, sightSide
    count += 1
    currentX = canvas.coords(mario)[0]
    if 'a' in pressedKeys or 'ф' in pressedKeys:
        if not isJumping:
            if count % 9 == 1:
                canvas.itemconfig(mario, image=marioRunAnimationPhoto1Flipped)
            elif count % 9 >= 4 and count % 9 <= 6:
                canvas.itemconfig(mario, image=marioRunAnimationPhoto2Flipped)
            else:
                canvas.itemconfig(mario, image=marioRunAnimationPhoto3Flipped)
        directionX = -1
        sightSide = marioPhotoFlipped
    elif 'd' in pressedKeys or 'в' in pressedKeys:
        if not isJumping:
            if count % 9 == 1:
                canvas.itemconfig(mario, image=marioRunAnimationPhoto1)
            elif count % 9 >= 4 and count % 9 <= 6:
                canvas.itemconfig(mario, image=marioRunAnimationPhoto2)
            else:
                canvas.itemconfig(mario, image=marioRunAnimationPhoto3)
        directionX = 1
        sightSide = marioPhoto
    updateMove(directionX, currentX)
    if directionX != 0:
        process = window.after(16, move)

def jump():
    '''Прыжок'''
    global velocity
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
    velocity += gravity * 0.016 - 2
    currentY += velocity
    if currentY + 47 > canvas.coords(groundLine)[1] and canvas.coords(mario)[0] < canvas.coords(groundLine)[2] and canvas.coords(mario)[0] > canvas.coords(groundLine)[0]:  #Проверка на землю
        currentY = canvas.coords(groundLine)[1] - 47
        velocity = 0
        isJumping = False
        if sightSide in ['pyimage3', 'pyimage7', 'pyimage9', 'pyimage11']:
            canvas.itemconfig(mario, image=marioPhoto)
        elif sightSide in ['pyimage4', 'pyimage8', 'pyimage10', 'pyimage12']:
            canvas.itemconfig(mario, image=marioPhotoFlipped)
    canvas.coords(mario, canvas.coords(mario)[0], currentY)

def checkCoords():
    '''Проверка координат персонажа на коллизии'''
    global velocity, speed, processOfMoving, processOfCheckCoords, isOnground, isJumping, countOfMoney, centerOfAbyss1, leftSideOfAbyss1
    currentCoords = convertCoords(canvas.coords(mario), [90, 90])
    mushroomCoords = convertCoords(canvas.coords(coordsOfObjects[3][0]), [90, 90])
    turtleCoords = convertCoords(canvas.coords(coordsOfObjects[4][0]), [90, 90])
    #Координаты бездн
    leftSideOfAbyss1 = coordsOfObjects[2][1][0]
    rightSideOfAbyss1 = coordsOfObjects[2][1][2]
    centerOfAbyss1 = (leftSideOfAbyss1 + rightSideOfAbyss1) // 2

    #Проверка на столкновение с грибом
    if mushroomCoords and overlaps(*currentCoords, *mushroomCoords) and canvas.itemcget(coordsOfObjects[3][0], "state") != 'hidden':
        if currentCoords[3] - 5 <= mushroomCoords[1] and velocity > 0:
            canvas.itemconfig(coordsOfObjects[3][0], state='hidden')
            countOfMoney.configure(text=str(int(countOfMoney.cget('text')) + 1))
        else:
            gameOver()
            canvas.itemconfig(mario, image=moneyPhoto)
    
    #Проверка на столкновение с черепахой
    if turtleCoords and overlaps(*currentCoords, *turtleCoords) and canvas.itemcget(coordsOfObjects[4][0], "state") != 'hidden':
        if currentCoords[3] - 5 <= turtleCoords[1] and velocity > 0:
            if canvas.itemcget(coordsOfObjects[4][0], "image") == 'pyimage18':
                canvas.itemconfig(coordsOfObjects[4][0], image=shellPhoto)
                canvas.coords(coordsOfObjects[4][0], canvas.coords(coordsOfObjects[4][0])[0], canvas.coords(coordsOfObjects[4][0])[1])
                startJump()
            else:
                canvas.itemconfig(coordsOfObjects[4][0], state='hidden')
                countOfMoney.configure(text=str(int(countOfMoney.cget('text')) + 1))
        elif canvas.itemcget(coordsOfObjects[4][0], "image") == 'pyimage18':
            gameOver()
            canvas.itemconfig(mario, image=moneyPhoto)
        else:
            canvas.coords(mario, canvas.coords(coordsOfObjects[4][0])[0] - 100 * directionX, canvas.coords(mario)[1])

    #Проверка на правую границу экрана
    if canvas.coords(mario)[0] > window.winfo_screenwidth():
        canvas.coords(mario, 30, canvas.coords(mario)[1])
        resetEnvironment()

    #Проверка на левую границу экрана
    if canvas.coords(mario)[0] < 30:
        canvas.coords(mario, 30, canvas.coords(mario)[1])
    if abs(canvas.coords(mario)[0] - centerOfAbyss1) < (centerOfAbyss1 - leftSideOfAbyss1) / 2 and canvas.coords(mario)[1] > 690:  #Проверка на бездну
        if canvas.coords(mario)[1] > 700:
            speed = 0
            isJumping = True
        falling(mario, *canvas.coords(mario))
        if canvas.coords(mario)[1] > screenHeight:
            gameOver()

    #Проверка на столкновение с трубами
    for i in range(2):
        if abs(coordsOfObjects[i][1][0] - canvas.coords(mario)[0]) < 100 and abs(coordsOfObjects[i][1][0] - canvas.coords(mario)[0]) > 75  and canvas.coords(mario)[1] > convertCoords(canvas.coords(coordsOfObjects[i][0]), [tubePhotos[i].width(), tubePhotos[i].height()])[3]:
            canvas.coords(mario, (coordsOfObjects[i][1][0] + (canvas.coords(mario)[0] - coordsOfObjects[i][1][0]) - 15 * directionX), canvas.coords(mario)[1])
        elif abs(coordsOfObjects[i][1][0] - canvas.coords(mario)[0]) < 70 and canvas.coords(mario)[1] > convertCoords(canvas.coords(coordsOfObjects[i][0]), [tubePhotos[i].width(), tubePhotos[i].height()])[3]:
            canvas.coords(mario, coordsOfObjects[i][1][0], canvas.coords(mario)[1])

    #Проверка на последнюю локацию
    if countOfLocations == 6:
        window.after_cancel(processOfMoving)
        if abs(canvas.coords(mario)[0] - 1800) < 50:
            winLabel = Label(canvas, text='Вы выиграли!', font=('Arial', 100), bg='lightblue')
            winLabel.place(x=screenWidth // 2 - 400, y=screenHeight // 2 - 200)
            window.after_cancel(processOfCheckCoords)
            speed = 0
    processOfCheckCoords = window.after(16, checkCoords)

def falling(object, positionX, positionY):
    '''Падение'''
    global velocity
    velocity += gravity * 0.016
    canvas.coords(object, positionX, positionY + velocity)

def resetEnvironment():
    '''Обновление окружения при выходе за границы экрана'''
    global countOfLocations, coordsOfObjects, goingLeft, processOfMoving, countOfMoney
    for i in range(len(coordsOfObjects)):   #Удаление старых объектов
        canvas.delete(coordsOfObjects[0][0])
        coordsOfObjects.pop(0)
    createTubes() #Создание новых препятствий
    canvas.tag_raise(ground)
    createAbysses() #Создание бездн
    createEnemies()
    if countOfLocations == 5:
        canvas.create_image(1800, screenHeight // 2 + 118, image=flagPhoto)
        canvas.itemconfig(coordsOfObjects[3][0], state='hidden')
        canvas.itemconfig(coordsOfObjects[4][0], state='hidden')
    canvas.tag_raise(mario, coordsOfObjects[2][0])
    canvas.tag_lower(groundLine)
    for i in range(2):
        canvas.tag_raise(coordsOfObjects[i][0], mario)
    goingLeft = True
    countOfLocations += 1
    countOfMoney.configure(text=str(int(countOfMoney.cget('text')) + 1))

def movingOfEnemies():
    '''Движение врагов'''
    global directionMoving, goingLeft, processOfMoving, speedEnemy, centerOfAbyss1, leftSideOfAbyss1
    currentMoving = canvas.coords(coordsOfObjects[3][0])[0]
    if abs(currentMoving - centerOfAbyss1) + 10 < (centerOfAbyss1 - leftSideOfAbyss1) / 2 and coordsOfObjects[3][1][1] > 690:  #Проверка на бездну
        speedEnemy = 0
        falling(coordsOfObjects[3][0], coordsOfObjects[3][1][0], coordsOfObjects[3][1][1])
    if currentMoving >= positionOfMushroom - 50 and goingLeft:
        directionMoving = -1
        if currentMoving < positionOfMushroom - 40:
            goingLeft = False
    elif currentMoving <= positionOfMushroom + 50:
        directionMoving = 1
        if currentMoving > positionOfMushroom + 40:
            goingLeft = True
    currentMoving += directionMoving * speedEnemy
    canvas.coords(coordsOfObjects[3][0], currentMoving, canvas.coords(coordsOfObjects[3][0])[1])
    processOfMoving = window.after(16, movingOfEnemies)

def createMushroom():
    '''Создание врага-гриба'''
    global coordsOfObjects, positionOfMushroom
    positionOfMushroom = random.randrange(400, 1500, 75)
    if all(abs(positionOfMushroom - coordsOfObjects[i][1][0]) > 100 for i in range(3)):
        mushroom = canvas.create_image(positionOfMushroom, screenHeight // 2 + 153, image=mushroomPhoto)
        coordsOfObjects.append([mushroom, canvas.coords(mushroom)])
    else:
        createMushroom()

def createTurtle():
    '''Создание врага-черепахи'''
    global coordsOfObjects
    positionOfTurtle = random.randrange(400, 1500, 50)
    if all(abs(positionOfTurtle - coordsOfObjects[i][1][0]) > 100 for i in range(4)):
        turtle = canvas.create_image(positionOfTurtle, screenHeight // 2 + 153, image=turtlePhoto)
        coordsOfObjects.append([turtle, canvas.coords(turtle)])
        if random.randint(1, 2) == 1:
            canvas.itemconfigure(turtle, state='hidden')
    else:
        createTurtle()

def createEnemies():
    '''Создание врагов'''
    createMushroom()
    createTurtle()

def createAbysses():
    '''Создание бездн'''
    global coordsOfObjects
    positionX0 = random.randrange(400, 1600, 50)
    if all(abs(positionX0 - coordsOfObjects[i][1][0]) > 230 for i in range(2)):
        position = [positionX0, screenHeight // 2 + 195, positionX0 + random.randint(100, 200), screenHeight]
        abyss = canvas.create_rectangle(position, fill='lightblue', outline='')
        coordsOfObjects.append([abyss, canvas.coords(abyss)])
    else:
        createAbysses()

def createTubes():
    '''Создание препятствий'''
    global coordsOfObjects, tubePhotos
    tubePhotos.clear()
    for i in range(2):
        tubePhoto = ImageTk.PhotoImage(Image.open('tube.png').resize((130, random.randrange(100, 301, 50))))
        tubePhotos.append(tubePhoto)
        tube = canvas.create_image(random.randrange(400, 1600, 300), canvas.coords(groundLine)[1], image=tubePhotos[i])
        canvas.coords(tube, canvas.coords(tube)[0], convertCoords(canvas.coords(tube), [tubePhotos[i].width(), tubePhotos[i].height()])[3])
        coordsOfObjects.append([tube, canvas.coords(tube)])
        if i == 1:
            if canvas.coords(tube)[0] == coordsOfObjects[0][1][0]:
                canvas.itemconfig(tube, state='hidden')
        canvas.tag_raise(tube, mario)

def menu(event = None):
    '''Создание меню'''
    global frame
    for widget in frame.winfo_children():
        widget.destroy()
    continueButton = Button(frame, text='Продолжить', font=('Arial', 30), width=20, command=continueGame)
    continueButton.pack(side='top')
    settingsButton = Button(frame, text='Настройки', font=('Arial', 30), width=20, command=settings)
    settingsButton.pack(side='top', pady=10)
    exitButton = Button(frame, text='Выход', font=('Arial', 30), width=20, command=exit)
    exitButton.pack(side='top', pady=10)
    frame.place(x=screenWidth // 2 - 280, y=screenHeight // 2 - 200)

def continueGame():
    '''Продолжение игры'''
    global frame
    frame.place_forget()

def settings():
    '''Настройки'''
    global volume, frame, value
    for widget in frame.winfo_children():
        widget.destroy()
    musicLabel = Label(frame, text='Уровень громкости', font=('Arial', 30), width=20, bg='lightblue')
    musicLabel.pack(side='top')
    value.set(volume * 1000)
    musicSlider = Scale(frame, from_=0, to=100, orient=HORIZONTAL, length=350, variable=value, font=('Arial', 30), width=30, command=lambda e: setVolume(musicSlider.get()), bg='lightblue', highlightthickness=0)
    musicSlider.pack(side='top', pady=10)
    returnButton = Button(frame, text='Вернуться в меню', font=('Arial', 30), width=20, command=menu)
    returnButton.pack(side='top')
    frame.place(x=screenWidth // 2 - 280, y=screenHeight // 2 - 200)

def setVolume(value):
    '''Изменение громкости музыки'''
    global volume
    volume = value / 1000
    mixer.music.set_volume(volume)

def overlaps(playerLeft, playerTop, playerRight, playerBottom, objectLeft, objectTop, objectRight, objectBottom):
    '''Просчитывание пересечений объектов'''
    horizontal = (playerLeft < objectRight) and (playerRight > objectLeft)
    vertical = (playerTop > objectBottom) and (playerBottom < objectTop)
    return horizontal and vertical

def convertCoords(objectCoords, objectsSprites):
    '''Конвертер координат'''
    objectWidth, objectHeight = objectsSprites
    # Преобразуем объект в bbox [x1, y1, x2, y2]
    cx, cy = objectCoords
    object_x1 = cx - objectWidth // 2
    object_y1 = cy - objectHeight // 2
    object_x2 = cx + objectWidth // 2
    object_y2 = cy + objectHeight // 2
    objectCoords = [object_x1, object_y2, object_x2, object_y1]
    return objectCoords

def gameOver():
    '''Окончание игры'''
    global frame
    for widget in frame.winfo_children():
        widget.destroy()
    gameOverLabel = Label(frame, text='Вы проиграли', font=('Arial', 30), width=20, bg='lightblue')
    gameOverLabel.pack(side='top')
    restartButton = Button(frame, text='Рестарт', font=('Arial', 30), width=20)
    restartButton.pack(side='top', pady=10)
    frame.place(x=screenWidth // 2 - 280, y=screenHeight // 2 - 200)

mixer.init()

#Глобальные переменные
process = None
processOfMoving = None
processOfCheckCoords = None
isJumping = False
isMoving = False
isOnground = True
goingLeft = True
velocity = 0
gravity = 200
directionX = 0
directionMoving = 0
targetY = 0
speed = 8
count = 0
countOfLocations = 1
volume = 0.03
speedEnemy = 3
pressedKeys = set()
keys = ['a', 'ф', 'd', 'в']
tubePhotos = []

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
moneyPhoto = ImageTk.PhotoImage(Image.open('money.png').resize((170, 170)))
moneyLabel = Label(canvas, image=moneyPhoto, bg='lightblue')
moneyLabel.place(x=screenWidth - 300, y=0)
countOfMoney = Label(canvas, text='0', font=('Arial', 50), bg='lightblue')
countOfMoney.place(x=screenWidth - 120, y=50)
frame = Frame(canvas, bg='lightblue')
value = IntVar()

#Воспроизведение музыки
mixer.music.load('mario_sound.mp3')
mixer.music.play()
mixer.music.set_volume(volume)

#Создание персонажа
marioPhoto = ImageTk.PhotoImage(Image.open('mario_sprite.png').resize((90, 90)))
marioPhotoFlipped = ImageTk.PhotoImage(Image.open('mario_sprite.png').resize((90, 90)).transpose(Image.FLIP_LEFT_RIGHT))
marioJumpPhoto = ImageTk.PhotoImage(Image.open('mario_jump.png').resize((90, 90)))
marioJumpPhotoFlipped = ImageTk.PhotoImage(Image.open('mario_jump.png').resize((90, 90)).transpose(Image.FLIP_LEFT_RIGHT))
marioRunAnimationPhoto1 = ImageTk.PhotoImage(Image.open('mario_run_animation_1.png').resize((90, 90)))
marioRunAnimationPhoto1Flipped = ImageTk.PhotoImage(Image.open('mario_run_animation_1.png').resize((90, 90)).transpose(Image.FLIP_LEFT_RIGHT))
marioRunAnimationPhoto2 = ImageTk.PhotoImage(Image.open('mario_run_animation_2.png').resize((90, 90)))
marioRunAnimationPhoto2Flipped = ImageTk.PhotoImage(Image.open('mario_run_animation_2.png').resize((90, 90)).transpose(Image.FLIP_LEFT_RIGHT))
marioRunAnimationPhoto3 = ImageTk.PhotoImage(Image.open('mario_run_animation_3.png').resize((90, 90)))
marioRunAnimationPhoto3Flipped = ImageTk.PhotoImage(Image.open('mario_run_animation_3.png').resize((90, 90)).transpose(Image.FLIP_LEFT_RIGHT))
mario = canvas.create_image(30, 693, image=marioPhoto)
canvas.tag_raise(mario)

#Создание объектов окружения
flagPhoto = ImageTk.PhotoImage(Image.open('flag.png').resize((170, 170)))
groundLine = canvas.create_line(0, screenHeight // 2 + 200, screenWidth, screenHeight // 2 + 200, fill='black', width=8)
groundPhoto = Image.open('ground.png').resize((100, 100)).convert('RGBA')
groundTextures = Image.new('RGBA', (screenWidth, 500))
for y in range(0, 500, 100):
    for x in range(0, screenWidth, 100):
        groundTextures.paste(groundPhoto, (x, y))
        
groundTextures = ImageTk.PhotoImage(groundTextures)
ground = canvas.create_image(screenWidth / 2, 990, image=groundTextures)
coordsOfObjects = []
createTubes()

canvas.tag_raise(ground)

createAbysses()

#Создание врагов
mushroomPhoto = ImageTk.PhotoImage(Image.open('mushroom.png').resize((90, 90)))
turtlePhoto = ImageTk.PhotoImage(Image.open('turtle.png').resize((90, 90)).transpose(Image.FLIP_LEFT_RIGHT))
shellPhoto = ImageTk.PhotoImage(Image.open('shell.png').resize((90, 90)))
createEnemies()

#Отрисовка поверх других объектов
canvas.tag_raise(mario, coordsOfObjects[2][0])
canvas.tag_lower(groundLine)
for i in range(2):
    canvas.tag_raise(coordsOfObjects[i][0])

#Параллельные циклы
checkCoords()
movingOfEnemies()

#Управление клавишами
window.bind('<KeyPress>', getPressedKeys)
window.bind('<KeyRelease>', getReleasedKeys)
window.bind('<Escape>', menu)

window.mainloop()