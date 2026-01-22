from tkinter import *
from PIL import Image, ImageTk
import random
import sys
import time
from pygame import mixer

'''переменные окружения'''

process = None
processOfMoving = None
processOfCheckCoords = None
isJumping = False
isMoving = False
isOnground = True
isOnTube = False
goingLeft = True
velocity = 0
gravity = 200
directionX = 0
speedEnemy = 3
directionMoving = 0
velocityOfJump = 0
targetY = 0
speed = 8
count = 0
countOfLocations = 1
volume = 0.03
pressedKeys = set()
keys = ['a', 'ф', 'd', 'в'] 
tubePhotos = []

class App(Tk):

    def __init__(self):

        super().__init__()

        self.title('Mario')
        self.screenWidth, self.screenHeight = 1920, 1080
        self.geometry(f'{self.screenWidth}x{self.screenHeight}')
        #self.resizable(False, False) #это для прода
        self.attributes('-fullscreen', True) #это для тестов
        self.iconphoto(False, PhotoImage(file='mario_icon.png'))

        self.init_main_menu() #Главная менюшка

    def init_main_menu(self):

        '''инициализация всех элементов первого окна'''
        
        if hasattr(self, 'canvas'):
            self.canvas.destroy()

        self.menuCanvas = Canvas(self, bg='lightblue', width=self.screenWidth, height=self.screenHeight)

        self.bgPhoto = ImageTk.PhotoImage((Image.open('bliss.jpg').resize((self.screenWidth, self.screenHeight))))
        self.bgLabel = Label(self.menuCanvas, image = self.bgPhoto)
        self.textPhoto = ImageTk.PhotoImage((Image.open('mario_label.png').resize((530*2, 240*2))))
        self.textLabel = Label(self.menuCanvas, image = self.textPhoto)

        self.groundPhoto = Image.open('ground.png').resize((70, 70)).convert('RGBA')
        self.groundTextures = Image.new('RGBA', (self.screenWidth, 500))
        for y in range(0, 200, 70):
            for x in range(0, self.screenWidth, 70):
                self.groundTextures.paste(self.groundPhoto, (x, y))
        
        self.groundTextures = ImageTk.PhotoImage(self.groundTextures)
        self.ground = Label(self.menuCanvas, image = self.groundTextures)

        self.playButton = Button(self.menuCanvas, text='ИГРАТЬ', font=('Arial', 30, 'bold'), width=20, 
            bg = '#B2611B', fg = '#FCB3B2', command=self.init_mario)
        self.quitButton = Button(self.menuCanvas, text='ВЫЙТИ', font=('Arial', 30, 'bold'), width=20, 
            bg = '#B2611B', fg = '#FCB3B2', command=lambda: sys.exit())

        self.play_id = self.menuCanvas.create_window(720, 600, window=self.playButton)
        self.quit_id = self.menuCanvas.create_window(720, 700, window=self.quitButton)

        self.button_y = 620
        self.button_dir = 1
        self.text_y = 80
        self.text_dir = 0.5

        self.animate_menu()

        self.bgLabel.place(x = 0, y = 0)
        self.textLabel.place(x = 420, y = 90)
        #self.playButton.place(x = 720, y = 600)
        #self.quitButton.place(x = 720, y = 700)
        self.ground.place(x=0, y=self.screenHeight - 140)
        self.menuCanvas.pack(anchor='center')

    def animate_menu(self):

        """Анимация движения всего меню"""

        self.button_y += self.button_dir
        if self.button_y > 630 or self.button_y < 610:
            self.button_dir *= -1
        
        self.text_y += self.text_dir
        if self.text_y > 86 or self.text_y < 74:
            self.text_dir *= -1
        
        self.playButton.place(x=720, y=self.button_y)
        self.quitButton.place(x=720, y=self.button_y + 100)  # Вторая кнопка ниже
        self.textLabel.place(x=420, y=self.text_y)
        
        self.menuCanvas.after(50, self.animate_menu)

    def init_mario(self):

        '''функция для запуска функция для инициализации самой игры'''

        global speed, speedEnemy

        speed, speedEnemy = 8, 3

        self.menuCanvas.destroy()
        
        self.canvas = Canvas(self, bg='lightblue', width=self.screenWidth, height=self.screenHeight)
        self.canvas.pack(anchor='center')

        mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        mixer.music.load('mario_sound.mp3')
        mixer.music.play()
        mixer.music.set_volume(volume)
        self.coinSound = mixer.Sound('coin.mp3')
        self.coinSound.set_volume(volume)
        self.winSound = mixer.Sound('win.mp3')
        self.winSound.set_volume(volume)


        # Создание интерфейса
        
        self.create_interface()
        self.create_mario()
        self.create_objects()

        self.canvas.tag_raise(self.mario)
        self.canvas.tag_raise(self.ground)

        self.setup_z_order()
        self.is_menu_on = False
        self.is_menu_unpaused = False
        self.is_dead = False

        self.checkCoords()
        self.movingOfEnemies()

        self.bind('<KeyPress>', self.getPressedKeys)
        self.bind('<KeyRelease>', self.getReleasedKeys)
        self.bind('<Escape>', self.menu)

    def create_interface(self):

        '''Создание интерфейса игры'''

        self.moneyPhoto = ImageTk.PhotoImage(Image.open('money.png').resize((170, 170)))
        self.moneyLabel = Label(self.canvas, image=self.moneyPhoto, bg='lightblue')
        self.moneyLabel.place(x=self.screenWidth - 300, y=0)
        
        self.countOfMoney = Label(self.canvas, text='0', font=('Arial', 50), bg='lightblue')
        self.countOfMoney.place(x=self.screenWidth - 120, y=50)
        
        self.frame = Frame(self.canvas, bg='lightblue')
        self.value = IntVar()

    def create_mario(self):

        '''Создание персонажа и инициализация всех его спрайтов'''

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

        self.marioSprites = {
            'marioPhoto': marioPhoto, 'marioPhotoFlipped': marioPhotoFlipped, 
            'marioJumpPhoto': marioJumpPhoto, 'marioJumpPhotoFlipped': marioJumpPhotoFlipped, 
            'marioRunAnimationPhoto1': marioRunAnimationPhoto1, 
            'marioRunAnimationPhoto1Flipped': marioRunAnimationPhoto1Flipped, 
            'marioRunAnimationPhoto2': marioRunAnimationPhoto2, 
            'marioRunAnimationPhoto2Flipped': marioRunAnimationPhoto2Flipped,
            'marioRunAnimationPhoto3': marioRunAnimationPhoto3,
            'marioRunAnimationPhoto3Flipped': marioRunAnimationPhoto3Flipped
        }

        self.mario = self.canvas.create_image(30, self.screenHeight // 2 + 153, image=marioPhoto)

    def create_objects(self):

        '''Создание обьектов окружения'''

        global countOfLocations

        self.groundPhoto = Image.open('ground.png').resize((100, 100)).convert('RGBA')
        self.groundTextures = Image.new('RGBA', (self.screenWidth, 500))
        for y in range(0, 500, 100):
            for x in range(0, self.screenWidth, 100):
                self.groundTextures.paste(self.groundPhoto, (x, y))
                
        self.groundTextures = ImageTk.PhotoImage(self.groundTextures)
        self.ground = self.canvas.create_image(self.screenWidth / 2, 990, image=self.groundTextures)
        
        self.flagPhoto = ImageTk.PhotoImage(Image.open('flag.png').resize((170, 170)))
        self.mushroomPhoto = ImageTk.PhotoImage(Image.open('mushroom.png').resize((90, 90)))
        self.turtlePhoto = ImageTk.PhotoImage(Image.open('turtle.png').resize((90, 90)).transpose(Image.FLIP_LEFT_RIGHT))
        self.shellPhoto = ImageTk.PhotoImage(Image.open('shell.png').resize((90, 90)))
        
        self.groundLine = self.canvas.create_line(0, self.screenHeight // 2 + 200, 
            self.screenWidth, self.screenHeight // 2 + 200, fill='black', width=8)
        
        self.ground = self.canvas.create_image(self.screenWidth / 2, 990, image=self.groundTextures)

        self.coordsOfObjects = []

        self.createTubes()
        self.createAbysses()
        self.createEnemies()

    def createTubes(self):

        '''Создание препятствий'''

        global tubePhotos

        tubePhotos.clear()
        for i in range(2):

            self.tubePhoto = ImageTk.PhotoImage(Image.open('tube.png').resize((130, random.randrange(100, 301, 50))))
            tubePhotos.append(self.tubePhoto)

            self.tube = self.canvas.create_image(random.randrange(400, 1600, 300), self.canvas.coords(self.groundLine)[1], image=tubePhotos[i])
            self.canvas.coords(self.tube, self.canvas.coords(self.tube)[0], self.convertCoords(self.canvas.coords(self.tube), [tubePhotos[i].width(), tubePhotos[i].height()])[3])
            self.coordsOfObjects.append([self.tube, self.canvas.coords(self.tube)])
            
            if i == 1:
                if self.canvas.coords(self.tube)[0] == self.coordsOfObjects[0][1][0]:
                    self.canvas.itemconfig(self.tube, state='hidden')

            self.canvas.tag_raise(self.tube, self.mario)

    def createAbysses(self):

        '''Создание бездн'''

        positionX0 = random.randrange(800, 1600, 50)
        if all(abs(positionX0 - self.coordsOfObjects[i][1][0]) > 230 for i in range(2)):
            position = [positionX0, self.screenHeight // 2 + 195, positionX0 + random.randint(100, 200), self.screenHeight]
            abyss = self.canvas.create_rectangle(position, fill='lightblue', outline='')
            self.coordsOfObjects.append([abyss, self.canvas.coords(abyss)])
        else:
            self.createAbysses()

    def setup_z_order(self):

        '''Настройка порядка отрисовки объектов'''

        self.canvas.tag_raise(self.mario)

        for i in range(2):  # Трубы
            if i < len(self.coordsOfObjects):
                self.canvas.tag_raise(self.coordsOfObjects[i][0])
        
        self.canvas.tag_raise(self.mario, self.coordsOfObjects[2][0]) #марио выше бездны
        
        if len(self.coordsOfObjects) > 3: #Враги
            for i in range(3, len(self.coordsOfObjects)):
                self.canvas.tag_lower(self.coordsOfObjects[i][0])

        self.canvas.tag_lower(self.ground)
        self.canvas.tag_lower(self.groundLine)

    def overlaps(self, playerLeft, playerTop, playerRight, playerBottom, objectLeft, objectTop, objectRight, objectBottom):
        '''Просчитывание пересечений объектов'''
        horizontal = (playerLeft < objectRight) and (playerRight > objectLeft)
        vertical = (playerTop > objectBottom) and (playerBottom < objectTop)

        return horizontal and vertical
    
    def convertCoords(self, objectCoords, objectsSprites):
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

    def getPressedKeys(self, event):

        '''Получение нажатых кнопок'''

        global pressedKeys, isMoving

        if event.keysym == 'space':
            if not isJumping:
                self.startJump()

        elif event.char in keys:
            pressedKeys.add(event.char)
            if not isMoving or self.is_menu_unpaused:
                isMoving = True
                self.is_menu_unpaused = False       
                self.move()

    def getReleasedKeys(self, event):

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
    
    def move(self):

        '''Передвижение влево/вправо на a/d'''

        global directionX, pressedKeys, process, count

        if self.is_menu_on == True:
            return

        count += 1
        currentX = self.canvas.coords(self.mario)[0]

        if 'a' in pressedKeys or 'ф' in pressedKeys:
            if not isJumping:
                if count % 9 == 1:
                    self.canvas.itemconfig(self.mario, image=self.marioSprites['marioRunAnimationPhoto1Flipped'])
                elif count % 9 >= 4 and count % 9 <= 6:
                    self.canvas.itemconfig(self.mario, image=self.marioSprites['marioRunAnimationPhoto2Flipped'])
                else:
                    self.canvas.itemconfig(self.mario, image=self.marioSprites['marioRunAnimationPhoto3Flipped'])
            directionX = -1
            self.sightSide = self.marioSprites['marioPhotoFlipped']

        elif 'd' in pressedKeys or 'в' in pressedKeys:
            if not isJumping:
                if count % 9 == 1:
                    self.canvas.itemconfig(self.mario, image=self.marioSprites['marioRunAnimationPhoto1'])
                elif count % 9 >= 4 and count % 9 <= 6:
                    self.canvas.itemconfig(self.mario, image=self.marioSprites['marioRunAnimationPhoto2'])
                else:
                    self.canvas.itemconfig(self.mario, image=self.marioSprites['marioRunAnimationPhoto3'])
            directionX = 1
            self.sightSide = self.marioSprites['marioPhoto']

        self.updateMove(directionX, currentX)

        if directionX != 0:
            process = self.after(16, self.move)

    def updateMove(self, directionX, currentX):

        '''Анимация передвижения'''

        global isMoving, process

        currentX += directionX * speed
        if directionX == 0:
            isMoving = False
            self.canvas.itemconfig(self.mario, image=self.sightSide)
            if process:
                self.after_cancel(process)

        self.canvas.coords(self.mario, currentX, self.canvas.coords(self.mario)[1])

    def startJump(self):

        '''Вспомогательная функция начала движения'''

        global isJumping, velocityOfJump

        if self.is_menu_on == True:
            return

        isJumping = True
        if self.canvas.coords(self.mario)[1] == 693:
            velocityOfJump = -30
        else:
            velocityOfJump = -35
            self.sightSide = self.canvas.itemcget(self.mario, "image")

        if self.sightSide in ['pyimage3', 'pyimage7', 'pyimage9', 'pyimage11']:
            self.canvas.itemconfig(self.mario, image=self.marioSprites['marioJumpPhoto'])

        elif self.sightSide in ['pyimage4', 'pyimage8', 'pyimage10', 'pyimage12']:
            self.canvas.itemconfig(self.mario, image=self.marioSprites['marioJumpPhotoFlipped'])

        self.jump()
    
    def jump(self):

        '''Прыжок)'''

        global velocityOfJump

        currentY = self.canvas.coords(self.mario)[1]
        self.updateJump(currentY)

        if velocityOfJump != 0:
            self.after(16, self.jump)
        
        
    def updateJump(self, currentY):

        '''Анимация прыжка'''

        global isJumping, velocityOfJump

        velocityOfJump += gravity * 0.016 - 2
        currentY += velocityOfJump

        if currentY + 47 > self.canvas.coords(self.groundLine)[1] and self.canvas.coords(self.mario)[0] < self.canvas.coords(self.groundLine)[2] and \
            self.canvas.coords(self.mario)[0] > self.canvas.coords(self.groundLine)[0]:  #Проверка на землю

            currentY = self.canvas.coords(self.groundLine)[1] - 47
            velocityOfJump = 0
            isJumping = False

            if self.sightSide in ['pyimage3', 'pyimage7', 'pyimage9', 'pyimage11']:
                self.canvas.itemconfig(self.mario, image=self.marioSprites['marioPhoto'])

            elif self.sightSide in ['pyimage4', 'pyimage8', 'pyimage10', 'pyimage12']:
                self.canvas.itemconfig(self.mario, image=self.marioSprites['marioPhotoFlipped'])

        self.canvas.coords(self.mario, self.canvas.coords(self.mario)[0], currentY)
    
    def checkCoords(self):

        '''Проверка координат персонажа на коллизии'''

        global velocityOfJump, speed, processOfMoving, processOfCheckCoords, isOnground, isJumping, centerOfAbyss1, leftSideOfAbyss1

        #координаты гриба, черепахи и марио
        try:
            mushroomCoords = self.convertCoords(self.canvas.coords(self.coordsOfObjects[3][0]), [90, 90])
            turtleCoords = self.convertCoords(self.canvas.coords(self.coordsOfObjects[4][0]), [90, 90])
            currentCoords = self.convertCoords(self.canvas.coords(self.mario), [90, 90])
        except:
            return

        #Координаты бездн
        leftSideOfAbyss1 = self.coordsOfObjects[2][1][0]
        rightSideOfAbyss1 = self.coordsOfObjects[2][1][2]
        centerOfAbyss1 = (leftSideOfAbyss1 + rightSideOfAbyss1) // 2
        #Проверка на столкновение с грибом
        if mushroomCoords and self.overlaps(*currentCoords, *mushroomCoords) and self.canvas.itemcget(self.coordsOfObjects[3][0], "state") != 'hidden':
            if currentCoords[3] - 5 <= mushroomCoords[1] and velocityOfJump > 0:
                self.canvas.itemconfig(self.coordsOfObjects[3][0], state='hidden')
                self.countOfMoney.configure(text=str(int(self.countOfMoney.cget('text')) + 1))
                self.coinSound.play()
            else:
                if not self.is_dead:
                    self.gameOver()
                    self.canvas.itemconfig(self.mario, image=self.moneyPhoto)
        #Проверка на столкновение с черепахой
        if turtleCoords and self.overlaps(*currentCoords, *turtleCoords) and self.canvas.itemcget(self.coordsOfObjects[4][0], "state") != 'hidden':
            if currentCoords[3] - 5 <= turtleCoords[1] and velocityOfJump > 0:
                if int(self.canvas.itemcget(self.coordsOfObjects[4][0], "image")[-2:]) == int(str(self.turtlePhoto)[-2:]):
                    self.canvas.itemconfig(self.coordsOfObjects[4][0], image=self.shellPhoto)
                    self.canvas.coords(self.coordsOfObjects[4][0], self.canvas.coords(self.coordsOfObjects[4][0])[0], 
                    self.canvas.coords(self.coordsOfObjects[4][0])[1])
                    self.startJump()
                elif int(self.canvas.itemcget(self.coordsOfObjects[4][0], "image")[-2:]) == int(str(self.shellPhoto)[-2:]):
                    self.canvas.itemconfig(self.coordsOfObjects[4][0], state='hidden')
                    self.countOfMoney.configure(text=str(int(self.countOfMoney.cget('text')) + 1))
                    self.coinSound.play()
            elif self.canvas.itemcget(self.coordsOfObjects[4][0], "image") == self.turtlePhoto:
                if not self.is_dead:
                    self.gameOver()
                    self.canvas.itemconfig(self.mario, image=self.moneyPhoto)
            else:
                self.canvas.coords(self.mario, self.canvas.coords(self.coordsOfObjects[4][0])[0] - 100 * directionX, self.canvas.coords(self.mario)[1])
    
        #Проверка на правую границу экрана
        if self.canvas.coords(self.mario)[0] > self.winfo_screenwidth():
            self.canvas.coords(self.mario, 30, self.canvas.coords(self.mario)[1])
            self.resetEnvironment()
    
        #Проверка на левую границу экрана
        if self.canvas.coords(self.mario)[0] < 30:
            self.canvas.coords(self.mario, 30, self.canvas.coords(self.mario)[1])
        
        #Проверка на бездну
        if abs(self.canvas.coords(self.mario)[0] - centerOfAbyss1) < (centerOfAbyss1 - leftSideOfAbyss1) / 2 and self.canvas.coords(self.mario)[1] > 690:  #Проверка на бездну
            if self.canvas.coords(self.mario)[1] > 710:
                speed = 0
                if not self.is_dead:
                    self.gameOver()
            self.falling(self.mario, *self.canvas.coords(self.mario))
    
        #Проверка на столкновение с трупами
        for i in range(2):
            if abs(self.coordsOfObjects[i][1][0] - self.canvas.coords(self.mario)[0]) < 100 and abs(self.coordsOfObjects[i][1][0] - self.canvas.coords(self.mario)[0]) > 75  and self.canvas.coords(self.mario)[1] > self.convertCoords(self.canvas.coords(self.coordsOfObjects[i][0]), [tubePhotos[i].width(), tubePhotos[i].height()])[3]:
                self.canvas.coords(self.mario, (self.coordsOfObjects[i][1][0] + (self.canvas.coords(self.mario)[0] - self.coordsOfObjects[i][1][0]) - 15 * directionX), self.canvas.coords(self.mario)[1])
            elif abs(self.coordsOfObjects[i][1][0] - self.canvas.coords(self.mario)[0]) < 70 and self.canvas.coords(self.mario)[1] > self.convertCoords(self.canvas.coords(self.coordsOfObjects[i][0]), [tubePhotos[i].width(), tubePhotos[i].height()])[3]:
                self.canvas.coords(self.mario, self.coordsOfObjects[i][1][0], self.canvas.coords(self.mario)[1])
    
        #Проверка на последнюю локацию
        if countOfLocations == 6:
            self.after_cancel(processOfMoving)
            if abs(self.canvas.coords(self.mario)[0] - 1800) < 50:
                winLabel = Label(self.canvas, text='Вы выиграли!', font=('Arial', 100), bg='lightblue')
                winLabel.place(x=self.screenWidth // 2 - 400, y=self.screenHeight // 2 - 400)
                self.after_cancel(processOfCheckCoords)
                self.winSound.play()
                speed = 0
                exitButton = Button(self.canvas, text='Рестарт', font=('Arial', 30, 'bold'), width=20,
            bg = '#FCB3B2', fg = '#352626', command=self.restartGame)
                exitButton.place(x=self.screenWidth // 2 - 400, y=self.screenHeight // 2 - 200, bg='#FCB3B2')
        processOfCheckCoords = self.after(16, self.checkCoords)
    
    def falling(self, object, positionX, positionY):

        '''Падение в бездну'''

        global velocity

        velocity += gravity * 0.016
        self.canvas.coords(object, positionX, positionY + velocity)

    def resetEnvironment(self):

        '''Обновление окружения при выходе за границы экрана'''

        global countOfLocations, goingLeft, processOfMoving

        for i in range(len(self.coordsOfObjects)):   #Удаление старых объектов
            self.canvas.delete(self.coordsOfObjects[0][0])
            self.coordsOfObjects.pop(0)

        self.createTubes() #Создание новых препятствий
        self.canvas.tag_raise(self.ground)
        self.createAbysses() #Создание бездны
    
        self.createEnemies()
        if countOfLocations == 5:
            self.canvas.create_image(1800, self.screenHeight // 2 + 118, image=self.flagPhoto)
            self.canvas.itemconfig(self.coordsOfObjects[3][0], state='hidden')
            self.canvas.itemconfig(self.coordsOfObjects[4][0], state='hidden')
            
        self.canvas.tag_raise(self.mario, self.coordsOfObjects[2][0])
        self.canvas.tag_lower(self.groundLine)

        for i in range(2):
            self.canvas.tag_raise(self.coordsOfObjects[i][0], self.mario)

        goingLeft = True
        countOfLocations += 1
        self.countOfMoney.configure(text=str(int(self.countOfMoney.cget('text')) + 1))
        self.coinSound.play()
        
    def movingOfEnemies(self):

        '''Движение врагов'''

        global directionMoving, goingLeft, processOfMoving, speedEnemy

        if self.is_menu_on == True:
            return

        currentMoving = self.canvas.coords(self.coordsOfObjects[3][0])[0]
        if abs(currentMoving - centerOfAbyss1) + 10 < (centerOfAbyss1 - leftSideOfAbyss1) / 2 and self.coordsOfObjects[3][1][1] > 690:  #Проверка на бездну
            speedEnemy = 0
            self.falling(self.coordsOfObjects[3][0], self.coordsOfObjects[3][1][0], self.coordsOfObjects[3][1][1])
        if currentMoving >= self.positionOfMushroom - 50 and goingLeft:
            directionMoving = -1
            if currentMoving < self.positionOfMushroom - 40:
                goingLeft = False
        elif currentMoving <= self.positionOfMushroom + 50:
            directionMoving = 1
            if currentMoving > self.positionOfMushroom + 40:
                goingLeft = True
        currentMoving += directionMoving * speedEnemy
        self.canvas.coords(self.coordsOfObjects[3][0], currentMoving, self.canvas.coords(self.coordsOfObjects[3][0])[1])
        processOfMoving = self.after(16, self.movingOfEnemies)

    def createMushroom(self):

        '''Создание врага-гриба'''

        global coordsOfObjects

        self.positionOfMushroom = random.randrange(400, 1500, 75)
        if all(abs(self.positionOfMushroom - self.coordsOfObjects[i][1][0]) > 100 for i in range(3)):
            mushroom = self.canvas.create_image(self.positionOfMushroom, self.screenHeight // 2 + 153, image=self.mushroomPhoto)
            self.coordsOfObjects.append([mushroom, self.canvas.coords(mushroom)])
        else:
            self.createMushroom()
    
    def createTurtle(self):

        '''Создание врага-черепахи'''

        global coordsOfObjects

        positionOfTurtle = random.randrange(400, 1500, 50)
        if all(abs(positionOfTurtle - self.coordsOfObjects[i][1][0]) > 100 for i in range(4)):
            turtle = self.canvas.create_image(positionOfTurtle, self.screenHeight // 2 + 153, image=self.turtlePhoto)
            self.coordsOfObjects.append([turtle, self.canvas.coords(turtle)])
            if random.randint(1, 2) == 1:
                self.canvas.itemconfigure(turtle, state='hidden')
        else:
            self.createTurtle()
    
    def createEnemies(self):

        '''Создание врагов'''

        self.createMushroom()
        self.createTurtle()


    def menu(self, event = None, back = None):

        '''Создание меню'''

        for widget in self.frame.winfo_children():
            widget.destroy()
        
        continueButton = Button(self.frame, text='Продолжить', font=('Arial', 30, 'bold'), width=20,
            bg = '#FCB3B2', fg = '#352626', command=self.chechPause)
        settingsButton = Button(self.frame, text='Настройки', font=('Arial', 30, 'bold'), width=20,
            bg = '#FCB3B2', fg = '#352626', command=self.settings)
        exitButton = Button(self.frame, text='Выход', font=('Arial', 30, 'bold'), width=20,
            bg = '#FCB3B2', fg = '#352626', command=self.init_main_menu)

        continueButton.pack(side='top')
        settingsButton.pack(side='top', pady=10)
        exitButton.pack(side='top', pady=10)

        if not back:
            self.chechPause()

    def chechPause(self):
        if self.is_menu_on == False:
            self.frame.place(x=self.screenWidth // 2 - 280, y=self.screenHeight // 2 - 200)
            self.is_menu_on = True
            self.is_menu_unpaused = False
        else:
            self.frame.place_forget()
            self.is_menu_on = False
            self.is_menu_unpaused = True
            self.movingOfEnemies()

    def settings(self):

        '''Настройки'''

        global volume
        
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        musicLabel = Label(self.frame, text='Уровень громкости', font=('Arial', 30), width=20, bg='lightblue')
        musicLabel.pack(side='top')
        
        self.value.set(volume * 1000)
        musicSlider = Scale(self.frame, from_=0, to=100, orient=HORIZONTAL, length=350, 
                          variable=self.value, font=('Arial', 30), width=30, 
                          command=lambda e: self.setVolume(musicSlider.get()), 
                          bg='lightblue', highlightthickness=0)
        musicSlider.pack(side='top', pady=10)
        
        returnButton = Button(self.frame, text='Вернуться в меню', font=('Arial', 30, 'bold'), width=20,
            bg = '#FCB3B2', fg = '#352626', command=lambda: self.menu(back = True))
        returnButton.pack(side='top')
        
        self.frame.place(x=self.screenWidth // 2 - 280, y=self.screenHeight // 2 - 200)

    def setVolume(self, value):

        '''Установка громкости'''

        global volume
        volume = value / 1000
        #mixer.music.set_volume(volume)

    def gameOver(self):

        '''Экран проигрыша'''

        for widget in self.frame.winfo_children():
            widget.destroy()

        self.is_menu_on, self.is_menu_unpaused, self.is_dead = False, False, True
        self.unbind('<Escape>')
        self.chechPause()
        
        gameOverLabel = Label(self.frame, text='Вы проиграли', font=('Arial', 30, 'bold'), width=20,
            bg = 'lightblue', fg = '#352626')
        restartButton = Button(self.frame, text='Рестарт', font=('Arial', 30, 'bold'), width=20,
            bg = '#FCB3B2', fg = '#352626', command=self.restartGame)

        gameOverLabel.pack(side='top')
        restartButton.pack(side='top', pady=10)
        
        self.frame.place(x=self.screenWidth // 2 - 280, y=self.screenHeight // 2 - 200)

    def restartGame(self):

        '''Рестарт игры'''

        global countOfLocations, speed, isJumping, isMoving, velocity, directionX
        
        self.frame.place_forget()
        countOfLocations = 1
        speed = 8
        isJumping = False
        isMoving = False
        self.is_dead = False
        velocity = 0
        directionX = 0
        
        for obj in self.coordsOfObjects:
            self.canvas.delete(obj[0])
        self.coordsOfObjects = []
        
        self.canvas.coords(self.mario, 30, self.screenHeight // 2 + 153)
        self.create_objects()
        
        self.countOfMoney.configure(text='0')

        self.bind('<Escape>', self.menu)
        self.chechPause()

if __name__ == '__main__':
    
    app = App()
    app.mainloop()