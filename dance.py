import sys, os
import eventBasedAnimation
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
import tkMessageBox

from aubio import source, onset

from pygame.locals import *
from pygame.mixer import music
import pygame as pg
import string
import random





#song class where the analysis method lies
class Song(object):
    def __init__(self):
        self.stepSize = 5 #stepping size of arrow
    
    def beatsInAubio(self, song):
    	win_s = 1024
        hop_s = win_s/2
        samplerate = 44100
        s = source(song, samplerate, hop_s)
        samplerate = s.samplerate
        o = onset("default", win_s, hop_s, samplerate)
        # list of onsets, in samples
        onsets = []
        second_list = []
        # total number of frames read
        total_frames = 0
        while True:
            samples, read = s()
            if o(samples):
                second_list.append("%f" % o.get_last_s())
                onsets.append(o.get_last())
            total_frames += read
            if read < hop_s: break
        #conver to numbers
        for i in range(len(second_list)):
            second_list[i] = eval(second_list[i])
        return second_list
    
    #makes the arrows based on the music beat analysis provided by aubio
    def makeArrows(self, beatTimes, player):
    	directions = ["left", "right", "up", "down"]
    	arrows = []
        #these arrows are chosen at random but a seed keeps it 
        #at the same time
        arrowY = 50

    	random.seed(42)
        for arrow in range(0, len(beatTimes), 2):
            arrows.append(movingArrow(random.choice(directions), 0, 
            	          self.stepSize*arrowY/2*beatTimes[arrow] + arrowY, 
                          0, 0, 1, player))
        return arrows

#if player is 1, that means it's the right hand side of a multiplayer game
#if player is 2, that means it's the left hand side of a multiplayer game
#if player is 0, that means it's single player and it's in the center

#class to keep track of the moving arrow itself
class movingArrow(object):
    def __init__(self, direction, x, y, beat, song, combo, player):
    	self.width, self.height = 800, 600
    	self.leftArrowUnclicked = PhotoImage(file = "gifs/leftArrowUnclicked.gif")
        self.rightArrowUnclicked = PhotoImage(file = "gifs/rightArrowUnclicked.gif")
        self.downArrowUnclicked = PhotoImage(file = "gifs/downArrowUnclicked.gif")
        self.upArrowUnclicked = PhotoImage(file = "gifs/upArrowUnclicked.gif")
        self.direction = direction
        self.player = player
        self.singlePlayer = True
        self.score = None
        self.rightCenter = 650
        self.leftCenter = 230

        #setting the arrows position based on player
        if self.player == 1:
            if self.direction == "left":
                self.x = self.rightCenter - 2*self.leftArrowUnclicked.width()
            elif self.direction == "down":
                self.x = self.rightCenter - self.downArrowUnclicked.width()
            elif self.direction == "up":
                self.x = self.rightCenter
            elif self.direction == "right":
                self.x = self.rightCenter + self.rightArrowUnclicked.width()
        if self.player == 2:
            if self.direction == "left":
                self.x = self.leftCenter - 2*self.leftArrowUnclicked.width()
            elif self.direction == "down":
                self.x = self.leftCenter - self.downArrowUnclicked.width()
            elif self.direction == "up":
                self.x = self.leftCenter
            elif self.direction == "right":
                self.x = self.leftCenter + self.rightArrowUnclicked.width()
        if self.player == 0: #single player
            if self.direction == "left":
                self.x = self.width/2 - 2*self.leftArrowUnclicked.width()
            elif self.direction == "down":
                self.x = self.width/2 - self.downArrowUnclicked.width()
            elif self.direction == "up":
                self.x = self.width/2
            elif self.direction == "right":
                self.x = self.width/2 + self.rightArrowUnclicked.width()
        self.y = y
        self.song = song
        self.combo = combo
        #subject to change based on song
        self.stepSize = 5
        #if tried to score the movingArrow
        self.attempt = False
        #keeps track of when to show the arrow 
        #performance after hitting on the arrow
        self.counter = 0

    def drawMovingArrow(self, canvas):
        if self.direction == "left":
            canvas.create_image(self.x, self.y, image =self.leftArrowUnclicked)
        elif self.direction == "right":
            canvas.create_image(self.x, self.y, image =self.rightArrowUnclicked)
        elif self.direction == "up":
            canvas.create_image(self.x, self.y, image =self.upArrowUnclicked)
        elif self.direction == "down":
            canvas.create_image(self.x, self.y, image =self.downArrowUnclicked)
    

    def onStep(self):
        self.y -= self.stepSize

class HomePage(object):  

    def __init__(self):
        self.width = 800
        self.height = 600
        self.aboutText = self.windowTitle = "Dance Dance Creation!"
        self.leftArrowUnclicked = PhotoImage(file = "gifs/leftArrowUnclicked.gif")
        self.rightArrowUnclicked = PhotoImage(file = "gifs/rightArrowUnclicked.gif")
        self.downArrowUnclicked = PhotoImage(file = "gifs/downArrowUnclicked.gif")
        self.upArrowUnclicked = PhotoImage(file = "gifs/upArrowUnclicked.gif")
        self.background = PhotoImage(file = "gifs/FireDancer.gif")
        self.arrowY = 50
        self.gameTextStartColor = "red"
        self.settingTextStartColor = "red"
        #title location
        self.danceTextDisplace = 220
        self.danceTextY = 100
        self.danceMidTextDisplace = 200
        self.danceMidTextY = 250
        self.creationTextDisplace = 170
        self.creationTextY = 400
        #game start location
        self.gameTextStartX = 320
        self.gameTextWidth = 160
        self.gameTextStartY = 520
        self.gameTextStartTop = 530
        self.gameTextHeight = 25
        #setting start location
        self.settingTextStartX = 345
        self.settingTextWidth = 110
        self.settingTextStartY = 560
        self.settingTextStartTop = 570
        self.settingTextHeight = 30
        self.clickX = 0
        self.clickY = 0

    def onMouseHomeGameStart(self, event):
        self.clickX, self.clickY = event.x, event.y
        if (self.clickX > self.gameTextStartX and 
            self.clickX < self.gameTextStartX + self.gameTextWidth and 
            self.clickY > self.gameTextStartY and 
            self.clickY < self.gameTextStartY + self.gameTextHeight):
            return True
        else: return False

    def onMouseHomeSetting(self, event):
        self.clickX, self.clickY = event.x, event.y
        if (self.clickX > self.settingTextStartX and 
            self.clickX < self.settingTextStartX + self.settingTextWidth and 
            self.clickY > self.settingTextStartY and 
            self.clickY < self.settingTextStartY + self.settingTextHeight):
            return True
        else: return False

    def onMouseHomeMove(self, event):
        if (event.x > self.gameTextStartX and 
            event.x < self.gameTextStartX + self.gameTextWidth and 
            event.y > self.gameTextStartY and 
            event.y < self.gameTextStartY + self.gameTextHeight):
            self.gameTextStartColor = "white"
        else:
            self.gameTextStartColor = "red"
        if (event.x > self.settingTextStartX and 
            event.x < self.settingTextStartX + self.settingTextWidth and 
            event.y > self.settingTextStartY and 
            event.y < self.settingTextStartY + self.settingTextHeight):
            self.settingTextStartColor = "white"
        else:
            self.settingTextStartColor = "red"

    def drawHomePage(self, canvas):
        #background with red dancer
        canvas.create_image(self.width/2, self.height/2,image = self.background)
        #Dance on the left
        canvas.create_text(self.width/2 - self.danceTextDisplace, 
                           self.danceTextY, text = "Dance", 
                           font = "impact 72 bold", fill = "red")
        #Dance on the right
        canvas.create_text(self.width/2 + self.danceMidTextDisplace, 
                           self.danceMidTextY, text = "Dance", 
                           font = "impact 72 bold", fill = "red")
        #creation on the left
        canvas.create_text(self.width/2 - self.creationTextDisplace, 
                           self.creationTextY, text = "Creation!", 
                           font = "impact 72 bold", fill = "red")
        #arrows in the top right corner
        canvas.create_image(self.width - 
                           ((2*2)+1)*self.leftArrowUnclicked.width(), 
                            self.arrowY, 
                            image = self.leftArrowUnclicked)
        canvas.create_image(self.width - (2*2)*self.downArrowUnclicked.width(), 
                            self.arrowY, 
                            image = self.downArrowUnclicked)
        canvas.create_image(self.width - 3*self.upArrowUnclicked.width(), 
                            self.arrowY, 
                            image = self.upArrowUnclicked)
        canvas.create_image(self.width - 2*self.downArrowUnclicked.width(), 
                            self.arrowY, 
                            image = self.downArrowUnclicked)
        canvas.create_text(self.width/2, self.gameTextStartTop, 
                           text = "Game Start", 
                           font = "Arial 30 bold", 
                           fill = self.gameTextStartColor)
        canvas.create_text(self.width/2, self.settingTextStartTop, 
                           text = "Options", 
                           font = "Arial 30 bold", 
                           fill = self.settingTextStartColor)
class GameScreen(object):

    def __init__(self):
        self.width = 800
        self.height = 600
        self.rightCenter = 650
        self.leftCenter = 230
        self.leftArrowClicked = PhotoImage(file = "gifs/leftArrowClicked.gif")
        self.rightArrowClicked = PhotoImage(file = "gifs/rightArrowClicked.gif")
        self.downArrowClicked = PhotoImage(file = "gifs/downArrowClicked.gif")
        self.upArrowClicked = PhotoImage(file = "gifs/upArrowClicked.gif")
        self.leftArrowUnclicked = PhotoImage(file = "gifs/leftArrowUnclicked.gif")
        self.rightArrowUnclicked = PhotoImage(file = "gifs/rightArrowUnclicked.gif")
        self.downArrowUnclicked = PhotoImage(file = "gifs/downArrowUnclicked.gif")
        self.upArrowUnclicked = PhotoImage(file = "gifs/upArrowUnclicked.gif")
        self.arrowY = 50
        self.directions = ["left", "up", "left", "right"]
        

        #first player variables (RHS)
        self.leftPressed = False
        self.rightPressed = False
        self.upPressed = False
        self.downPressed = False
        self.lifeBar = 0
        self.comboSingle = 0
        self.maxComboSingle = 0
        self.successfulHitSingle = 0
        self.perfectSingle = 0
        self.greatSingle = 0
        self.goodSingle = 0
        self.booSingle = 0

        #second player variables (LHS)
        self.leftPressedSP = False
        self.rightPressedSP = False
        self.upPressedSP = False
        self.downPressedSP = False
        self.lifeBarSP = 0
        self.comboSP = 0
        self.maxComboSP = 0
        self.successfulHitSP = 0
        self.perfectSP = 0
        self.greatSP = 0
        self.goodSP = 0
        self.booSP = 0
        
        #RGB colors 
        self.RGB255 = 255
        self.forestR = 34
        self.forestG = 134
        self.pinkG = 150
        self.pinkB = 200

        #to count when the game is over
        self.arrowCount = 0

        #text locations
        self.comboFPX = 775
        self.comboFPY = 100
        self.maxComboFPY = 500
        self.comboSPX = 37
        self.scoreFPX = 600
        self.scoreSPX = 200
        self.redXStart = 400
        self.redXEnd = 600
        self.redXWidth = 10

        #life bar measurements
        self.lifeBarX = 760
        self.lifeBarXSP = 30
        self.lifeBarWidth = 20
        self.lifeBarY = 150
        self.lifeBarHeight = 300
 
        #score thresholds to evaluate performances of arrows
        self.greatTH = 5
        self.goodTH = 10
        self.booTH = 15

        self.counterTop = 5
        self.isPlaying = False
        self.isGameOverSingle = False
        self.isGameOverSP = False
    
    #if it's multi player, call this to draw for second player
    def drawLifeBarSP(self, canvas):
        canvas.create_rectangle(self.lifeBarXSP, self.lifeBarY, 
                                self.lifeBarXSP + self.lifeBarWidth, 
                                self.lifeBarY + self.lifeBarHeight, 
                                fill = "red")
        
        #stop drawing if green gets to the bottom
        if (self.lifeBarHeight - self.lifeBarSP > 
            self.lifeBarY + self.lifeBarHeight):
            self.isGameOverSP = True
        else:
            #stop drawing if green gets to the top
            if self.lifeBarHeight - self.lifeBarSP == self.lifeBarY:
                canvas.create_rectangle(self.lifeBarXSP, self.lifeBarY, 
                                        self.lifeBarXSP + self.lifeBarWidth, 
                                        self.lifeBarY + self.lifeBarHeight, 
                                        fill = "green")
            else: #draw regular lifeBar
                canvas.create_rectangle(self.lifeBarXSP, 
                                        self.lifeBarHeight - self.lifeBarSP, 
                                        self.lifeBarXSP + self.lifeBarWidth,
                                        self.lifeBarY + self.lifeBarHeight, 
                                        fill = "green")
       
    #if it's single player, just draw this life bar
    def drawLifeBar(self, canvas):
        canvas.create_rectangle(self.lifeBarX, self.lifeBarY, 
                                self.lifeBarX + self.lifeBarWidth, 
                                self.lifeBarY + self.lifeBarHeight, 
                                fill = "red")
        
        #stop drawing if green gets to the bottom
        if (self.lifeBarHeight - self.lifeBar > 
            self.lifeBarY + self.lifeBarHeight):
            self.isGameOverSingle = True
        else:
            #stop drawing if green gets to the top
            if self.lifeBarHeight - self.lifeBar == self.lifeBarY:
                canvas.create_rectangle(self.lifeBarX, self.lifeBarY, 
                                        self.lifeBarX + self.lifeBarWidth, 
                                        self.lifeBarY + self.lifeBarHeight, 
                                        fill = "green")
            else: #draw regular lifeBar
                canvas.create_rectangle(self.lifeBarX, 
                                        self.lifeBarHeight - self.lifeBar, 
                                        self.lifeBarX + self.lifeBarWidth,
                                        self.lifeBarY + self.lifeBarHeight, 
                                        fill = "green")

    #draws the screen background depending on settings
    def drawGameScreenBackground(self, canvas, color):
        if color == "black":
            canvas.create_rectangle(0, 0, self.width, self.height, 
                                    fill = "black")
        if color == "orange":
            canvas.create_rectangle(0,0,self.width, self.height, 
                                    fill = "orange")
        if color == "purple":
            canvas.create_rectangle(0,0,self.width, self.height, 
                                    fill = "purple")
        if color == "blue":
            canvas.create_rectangle(0,0,self.width, self.height, 
                                    fill = "blue")
        if color == "forestGreen":
            canvas.create_rectangle(0,0,self.width, self.height, 
                                    fill = "dark green")
        if color == "pink":
            canvas.create_rectangle(0,0,self.width, self.height, 
                                    fill = "pink")
        if self.isPlaying == False:
            canvas.create_text(self.width/2, self.height/2, 
                               text = "Press the spacebar to start!", 
                               fill = "red", font = "Impact 40 bold")
    
    #draws the text above and below the life bar 
    def drawCombos(self, canvas, color):
        #first player combo score
        canvas.create_text(self.comboFPX, self.comboFPY, 
                           text = "Combo: \n" + str(self.comboSingle), 
                           font = "Impact 15 bold", fill = color)
        #first player max combo score
        canvas.create_text(self.comboFPX, self.maxComboFPY, 
                           text = "Max \nCombo: \n" + str(self.maxComboSingle), 
                           font = "Impact 15 bold", fill = color)
        
    #draws the text above the life bars in multiplayer
    def drawCombosMP(self, canvas, leftColor, rightColor):
        #first player combo score
        canvas.create_text(self.comboFPX, self.comboFPY, 
                           text = "Combo: \n" + str(self.comboSingle), 
                           font = "Impact 15 bold", fill = rightColor)
        #first player max combo score
        canvas.create_text(self.comboFPX, self.maxComboFPY, 
                           text = "Max \nCombo: \n" + str(self.maxComboSingle), 
                           font = "Impact 15 bold", fill = rightColor)
        #second player combo score
        canvas.create_text(self.comboSPX, self.comboFPY, 
                           text = "Combo: \n" + str(self.comboSP), 
                           font = "Impact 15 bold", fill = leftColor)
        #second player max combo score
        canvas.create_text(self.comboSPX, self.maxComboFPY, 
                           text = "Max \nCombo: \n" + str(self.maxComboSP), 
                           font = "Impact 15 bold", fill = leftColor)

    #draws the game screen for multiplayer
    def drawGameScreenMP(self, canvas, movingArrowsFirstPlayer, 
                                       movingArrowsSecondPlayer):
        #first player
        if self.leftPressed == False:
            canvas.create_image(self.rightCenter - 
                                2*self.leftArrowClicked.width(), 
                                self.arrowY, image = self.leftArrowClicked)
        if self.downPressed == False:
            canvas.create_image(self.rightCenter - 
                                self.downArrowClicked.width(), 
                                self.arrowY, image = self.downArrowClicked)
        if self.upPressed == False:
            canvas.create_image(self.rightCenter, 
                                self.arrowY, image = self.upArrowClicked)
        if self.rightPressed == False:
            canvas.create_image(self.rightCenter + 
                                self.rightArrowClicked.width(), self.arrowY, 
                                image = self.rightArrowClicked)

        if self.leftPressed == True:
            canvas.create_image(self.rightCenter - 
                                2*self.leftArrowClicked.width(), self.arrowY, 
                                image = self.leftArrowUnclicked)
        if self.downPressed == True:
            canvas.create_image(self.rightCenter - 
                                self.downArrowClicked.width(), self.arrowY, 
                                image = self.downArrowUnclicked)
        if self.upPressed == True:
            canvas.create_image(self.rightCenter, self.arrowY, 
                                image = self.upArrowUnclicked)
        if self.rightPressed == True:
            canvas.create_image(self.rightCenter + 
                                self.rightArrowClicked.width(), self.arrowY, 
                                image = self.rightArrowUnclicked)

        #second player
        if self.leftPressedSP == False:
            canvas.create_image(self.leftCenter - 
                                2*self.leftArrowClicked.width(), self.arrowY, 
                                image = self.leftArrowClicked)
        if self.downPressedSP == False:
            canvas.create_image(self.leftCenter - 
                                self.downArrowClicked.width(), self.arrowY, 
                                image = self.downArrowClicked)
        if self.upPressedSP == False:
            canvas.create_image(self.leftCenter, self.arrowY, 
                                image = self.upArrowClicked)
        if self.rightPressedSP == False:
            canvas.create_image(self.leftCenter+ self.rightArrowClicked.width(), 
                                self.arrowY, image = self.rightArrowClicked)

        if self.leftPressedSP == True:
            canvas.create_image(self.leftCenter - 
                                2*self.leftArrowClicked.width(), self.arrowY, 
                                image = self.leftArrowUnclicked)
        if self.downPressedSP == True:
            canvas.create_image(self.leftCenter - self.downArrowClicked.width(), 
                                self.arrowY, image = self.downArrowUnclicked)
        if self.upPressedSP == True:
            canvas.create_image(self.leftCenter, self.arrowY, 
                                image = self.upArrowUnclicked)
        if self.rightPressedSP == True:
            canvas.create_image(self.leftCenter + 
                                self.rightArrowClicked.width(), self.arrowY, 
                                image = self.rightArrowUnclicked)

        for arrow in range(len(movingArrowsSecondPlayer)):

        #don't draw the arrow if get "Great" or "Perfect" in the attempt
        #draw the performance score of each arrow in the middle
            if (movingArrowsSecondPlayer[arrow].score != None and 
                movingArrowsSecondPlayer[arrow].counter < self.counterTop):
                canvas.create_text(self.scoreSPX, self.height/2, 
                                   text = movingArrowsSecondPlayer[arrow].score, 
                                   font = "Impact " + str((2**3) * 
                                   movingArrowsSecondPlayer[arrow].counter) + 
                                   " bold", fill = "white")
      
            if (movingArrowsSecondPlayer[arrow].score != "Perfect" and 
                movingArrowsSecondPlayer[arrow].score != "Great"):
                movingArrowsSecondPlayer[arrow].drawMovingArrow(canvas)
        
        for arrow in range(len(movingArrowsFirstPlayer)):
        #don't draw the arrow if get "Great" or "Perfect" in the attempt
            if (movingArrowsFirstPlayer[arrow].score != None and 
                movingArrowsFirstPlayer[arrow].counter < self.counterTop):
                canvas.create_text(self.scoreFPX, self.height/2, 
                                   text = movingArrowsFirstPlayer[arrow].score, 
                                   font = "Impact " + str((2**3) * 
                                   movingArrowsFirstPlayer[arrow].counter) + 
                                   " bold", fill = "white")
      
            if (movingArrowsFirstPlayer[arrow].score != "Perfect" and 
                movingArrowsFirstPlayer[arrow].score != "Great"):
                movingArrowsFirstPlayer[arrow].drawMovingArrow(canvas)
    
    #draws when both players fail in multiplayer
    def gameOverTextMP(self, canvas):
        canvas.create_text(self.width/2, self.height/2, 
                    text = "Good attempt both of you...\npress 'q' to continue", 
                           fill = "red", font = "impact 20")
    
    #draws when the first player fails during multiplayer
    def drawGameOverFP(self, canvas):
        canvas.create_line(self.redXStart, 0, self.width, self.redXEnd, 
                           fill = "red", width = self.redXWidth)
        canvas.create_line(self.redXStart, self.redXEnd, self.width, 0, 
                           fill = "red", width = self.redXWidth)
    #draws when the second player fails during multiplayer
    def drawGameOverSP(self, canvas):
        canvas.create_line(0, 0, self.redXStart, self.redXEnd, fill= "red", 
                           width = self.redXWidth)
        canvas.create_line(0, self.redXEnd, self.redXStart, 0, fill = "red", 
                           width = self.redXWidth)
    
    #draws when single player fails
    def drawGameOver(self, canvas):
        canvas.create_line(self.redXStart/2, self.redXEnd-self.arrowY, 
                           self.redXEnd, self.arrowY, fill = "red", 
                           width = self.redXWidth)
        canvas.create_line(self.redXStart/2, self.arrowY, self.redXEnd, 
                           self.redXEnd-self.arrowY, fill = "red", 
                           width = self.redXWidth)
        canvas.create_text(self.width - self.redXStart/2, self.height/2, 
                           text = "Good attempt...\npress 'q' to continue", 
                           fill = "white", font = "impact 20")

    #draws game screen for single player
    def drawGameScreen(self, canvas, movingArrows):
        
        if self.leftPressed == False:
            canvas.create_image(self.width/2 - 2*self.leftArrowClicked.width(), 
                                self.arrowY, image = self.leftArrowClicked)
        if self.downPressed == False:
            canvas.create_image(self.width/2 - self.downArrowClicked.width(), 
                                self.arrowY, image = self.downArrowClicked)
        if self.upPressed == False:
            canvas.create_image(self.width/2, self.arrowY, 
                                image = self.upArrowClicked)
        if self.rightPressed == False:
            canvas.create_image(self.width/2 + self.rightArrowClicked.width(), 
                                self.arrowY, image = self.rightArrowClicked)

        if self.leftPressed == True:
            canvas.create_image(self.width/2 - 2*self.leftArrowClicked.width(), 
                                self.arrowY, image = self.leftArrowUnclicked)
        if self.downPressed == True:
            canvas.create_image(self.width/2 - self.downArrowClicked.width(), 
                                self.arrowY, image = self.downArrowUnclicked)
        if self.upPressed == True:
            canvas.create_image(self.width/2, self.arrowY, 
                                image = self.upArrowUnclicked)
        if self.rightPressed == True:
            canvas.create_image(self.width/2 + self.rightArrowClicked.width(), 
                                self.arrowY, image = self.rightArrowUnclicked)

        for arrow in range(len(movingArrows)):
            #don't draw the arrow if get "Great" or "Perfect" in the attempt
            if (movingArrows[arrow].score != None and 
                movingArrows[arrow].counter < self.counterTop):
                canvas.create_text(self.width/2, self.height/2, 
                                   text = movingArrows[arrow].score, 
                                   font = "Impact " + str((2**3) * 
                                   movingArrows[arrow].counter)+ " bold", 
                                   fill = "white")
       
            if (movingArrows[arrow].score != "Perfect" and 
                movingArrows[arrow].score != "Great"):
                movingArrows[arrow].drawMovingArrow(canvas)

    #evaluates performance of arrow and changes life bar depending on 
    #performance of second player
    def arrowScoreSP(self, movingArrowsSecondPlayer):
        for arrow in range(len(movingArrowsSecondPlayer)):
            if movingArrowsSecondPlayer[arrow].direction == "left":
                if (movingArrowsSecondPlayer[arrow].y == self.arrowY and 
                    self.leftPressedSP == True and 
                    movingArrowsSecondPlayer[arrow].attempt == False):  
                    movingArrowsSecondPlayer[arrow].score = "Perfect"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.lifeBarWidth
                    self.perfectSP += 1
                    self.successfulHitSP += 1
                    self.comboSP += 1
                    if self.comboSP > self.maxComboSP:
                        self.maxComboSP = self.comboSP

                if (movingArrowsSecondPlayer[arrow].y > 
                    self.arrowY - self.greatTH and 
                    movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.greatTH and 
                    self.leftPressedSP == True and 
                    movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Great"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.lifeBarWidth/2
                    self.greatSP += 1
                    self.successfulHitSP += 1
                    self.comboSP += 1
                    if self.comboSP > self.maxComboSP:
                        self.maxComboSP = self.comboSP

                if (movingArrowsSecondPlayer[arrow].y > 
                    self.arrowY - self.goodTH and 
                    movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.goodTH and 
                    self.leftPressedSP == True and 
                    movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Good"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.greatTH
                    self.goodSP += 1
                    self.successfulHitSP += 1
                    self.comboSP = 0

                if (movingArrowsSecondPlayer[arrow].y > 
                    self.arrowY - self.booTH and 
                    movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.booTH and self.leftPressedSP == True and 
                    movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Boo"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP > -self.lifeBarY - self.greatTH:
                        self.lifeBarSP -= self.lifeBarWidth/2
                    self.booSP += 1
                    self.comboSP = 0

                if (movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY - self.booTH and 
                    movingArrowsSecondPlayer[arrow].attempt == False):        
                    movingArrowsSecondPlayer[arrow].score = "Boo"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP > -self.lifeBarY - self.greatTH:
                        self.lifeBarSP -= self.lifeBarWidth/2
                    self.booSP += 1
                    self.comboSP = 0
              
            if movingArrowsSecondPlayer[arrow].direction == "right":
                
                if (movingArrowsSecondPlayer[arrow].y == self.arrowY and 
                    self.rightPressedSP == True and 
                    movingArrowsSecondPlayer[arrow].attempt == False):  
                    movingArrowsSecondPlayer[arrow].score = "Perfect"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.lifeBarWidth
                    self.perfectSP += 1
                    self.successfulHitSP += 1
                    self.comboSP += 1
                    if self.comboSP > self.maxComboSP:
                        self.maxComboSP = self.comboSP
                if (movingArrowsSecondPlayer[arrow].y > 
                    self.arrowY - self.greatTH and 
                    movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.greatTH and self.rightPressedSP == True 
                    and movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Great"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.lifeBarWidth/2
                    self.greatSP += 1
                    self.successfulHitSP += 1
                    self.comboSP += 1
                    if self.comboSP > self.maxComboSP:
                        self.maxComboSP = self.comboSP
                if (movingArrowsSecondPlayer[arrow].y > 
                    self.arrowY - self.goodTH and 
                    movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.goodTH and self.rightPressedSP == True 
                    and movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Good"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.greatTH
                    self.goodSP += 1
                    self.successfulHitSP += 1
                    self.comboSP = 0
                if (movingArrowsSecondPlayer[arrow].y > 
                    self.arrowY - self.booTH and 
                    movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.booTH and self.rightPressedSP == True 
                    and movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Boo"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP > -self.lifeBarY - self.greatTH:
                        self.lifeBarSP -= self.lifeBarWidth/2
                    self.booSP += 1
                    self.comboSP = 0
                if (movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY - self.booTH and 
                    movingArrowsSecondPlayer[arrow].attempt == False):        
                    movingArrowsSecondPlayer[arrow].score = "Boo"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP > -self.lifeBarY - self.greatTH:
                        self.lifeBarSP -= self.lifeBarWidth/2
                    self.booSP += 1
                    self.comboSP = 0
        
            
            if movingArrowsSecondPlayer[arrow].direction == "up":
            
                if (movingArrowsSecondPlayer[arrow].y == self.arrowY and 
                    self.upPressedSP == True and 
                    movingArrowsSecondPlayer[arrow].attempt == False):  
                    movingArrowsSecondPlayer[arrow].score = "Perfect"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.lifeBarWidth
                    self.perfectSP += 1
                    self.successfulHitSP += 1
                    self.comboSP += 1
                    if self.comboSP > self.maxComboSP:
                        self.maxComboSP = self.comboSP
                if (movingArrowsSecondPlayer[arrow].y > 
                    self.arrowY - self.greatTH and 
                    movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.greatTH and self.upPressedSP == True 
                    and movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Great"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.lifeBarWidth/2
                    self.greatSP += 1
                    self.successfulHitSP += 1
                    self.comboSP += 1
                    if self.comboSP > self.maxComboSP:
                        self.maxComboSP = self.comboSP
                if (movingArrowsSecondPlayer[arrow].y > 
                    self.arrowY - self.goodTH and 
                    movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.goodTH and self.upPressedSP == True and 
                    movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Good"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.greatTH
                    self.goodSP += 1
                    self.successfulHitSP += 1
                    self.comboSP = 0
                if (movingArrowsSecondPlayer[arrow].y > self.arrowY - self.booTH 
                    and movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.booTH and self.upPressedSP == True and 
                    movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Boo"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP > -self.lifeBarY - self.greatTH:
                        self.lifeBarSP -= self.lifeBarWidth/2
                    self.booSP += 1
                    self.comboSP = 0
                if (movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY - self.booTH and 
                    movingArrowsSecondPlayer[arrow].attempt == False):        
                    movingArrowsSecondPlayer[arrow].score = "Boo"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP > -self.lifeBarY - self.greatTH:
                        self.lifeBarSP -= self.lifeBarWidth/2
                    self.booSP += 1
                    self.comboSP = 0
            
            if movingArrowsSecondPlayer[arrow].direction == "down":
                
                if (movingArrowsSecondPlayer[arrow].y == self.arrowY and 
                    self.downPressedSP == True and 
                    movingArrowsSecondPlayer[arrow].attempt == False):  
                    movingArrowsSecondPlayer[arrow].score = "Perfect"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.lifeBarWidth
                    self.perfectSP += 1
                    self.successfulHitSP += 1
                    self.comboSP += 1
                    if self.comboSP > self.maxComboSP:
                        self.maxComboSP = self.comboSP
                if (movingArrowsSecondPlayer[arrow].y > 
                    self.arrowY - self.greatTH and 
                    movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.greatTH and self.downPressedSP == True 
                    and movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Great"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.lifeBarWidth/2
                    self.greatSP += 1
                    self.successfulHitSP += 1
                    self.comboSP += 1
                    if self.comboSP > self.maxComboSP:
                        self.maxComboSP = self.comboSP
                if (movingArrowsSecondPlayer[arrow].y > 
                    self.arrowY - self.goodTH and 
                    movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.goodTH and self.downPressedSP == True and 
                    movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Good"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP < self.lifeBarY:
                        self.lifeBarSP += self.greatTH
                    self.goodSP += 1
                    self.successfulHitSP += 1
                    self.comboSP = 0
                if (movingArrowsSecondPlayer[arrow].y > self.arrowY - self.booTH 
                    and movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY + self.booTH and self.downPressedSP == True and 
                    movingArrowsSecondPlayer[arrow].attempt == False):
                    movingArrowsSecondPlayer[arrow].score = "Boo"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP > -self.lifeBarY - self.greatTH:
                        self.lifeBarSP -= self.lifeBarWidth/2
                    self.booSP += 1
                    self.comboSP = 0
                if (movingArrowsSecondPlayer[arrow].y < 
                    self.arrowY - self.booTH and 
                    movingArrowsSecondPlayer[arrow].attempt == False):        
                    movingArrowsSecondPlayer[arrow].score = "Boo"
                    movingArrowsSecondPlayer[arrow].attempt = True
                    if self.lifeBarSP > -self.lifeBarY - self.greatTH:
                        self.lifeBarSP -= self.lifeBarWidth/2
                    self.booSP += 1
                    self.comboSP = 0
    
    #(first player is on the right, counterintuitively)
    #see what happens to arrows, and how
    #this affects lifeBar and performance of each arrow
    def arrowScore(self, movingArrows):

        #text for score
        for arrow in range(len(movingArrows)):
            if movingArrows[arrow].direction == "left":
                if (movingArrows[arrow].y == self.arrowY and 
                    self.leftPressed == True and 
                    movingArrows[arrow].attempt == False):  
                    movingArrows[arrow].score = "Perfect"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.lifeBarWidth
                    self.perfectSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle += 1
                    if self.comboSingle > self.maxComboSingle:
                        self.maxComboSingle = self.comboSingle
                if (movingArrows[arrow].y > self.arrowY - self.greatTH and 
                    movingArrows[arrow].y < self.arrowY + self.greatTH and 
                    self.leftPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Great"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.lifeBarWidth/2
                    self.greatSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle += 1
                    if self.comboSingle > self.maxComboSingle:
                        self.maxComboSingle = self.comboSingle
                if (movingArrows[arrow].y > self.arrowY - self.goodTH and 
                    movingArrows[arrow].y < self.arrowY + self.goodTH and 
                    self.leftPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Good"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.greatTH
                    self.goodSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle = 0
                if (movingArrows[arrow].y > self.arrowY - self.booTH and 
                    movingArrows[arrow].y < self.arrowY + self.booTH and 
                    self.leftPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Boo"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar > -self.lifeBarY - self.greatTH:
                        self.lifeBar -= self.lifeBarWidth/2
                    self.booSingle += 1
                    self.comboSingle = 0
                if (movingArrows[arrow].y < self.arrowY - self.booTH and 
                    movingArrows[arrow].attempt == False):        
                    movingArrows[arrow].score = "Boo"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar > -self.lifeBarY - self.greatTH:
                        self.lifeBar -= self.lifeBarWidth/2
                    self.booSingle += 1
                    self.comboSingle = 0
              

            if movingArrows[arrow].direction == "right":
                
                if (movingArrows[arrow].y == self.arrowY and 
                    self.rightPressed == True and 
                    movingArrows[arrow].attempt == False):  
                    movingArrows[arrow].score = "Perfect"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.lifeBarWidth
                    self.perfectSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle += 1
                    if self.comboSingle > self.maxComboSingle:
                        self.maxComboSingle = self.comboSingle
                if (movingArrows[arrow].y > self.arrowY - self.greatTH and 
                    movingArrows[arrow].y < self.arrowY + self.greatTH and 
                    self.rightPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Great"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.lifeBarWidth/2
                    self.greatSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle += 1
                    if self.comboSingle > self.maxComboSingle:
                        self.maxComboSingle = self.comboSingle
                if (movingArrows[arrow].y > self.arrowY - self.goodTH and 
                    movingArrows[arrow].y < self.arrowY + self.goodTH and 
                    self.rightPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Good"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.greatTH
                    self.goodSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle = 0
                if (movingArrows[arrow].y > self.arrowY - self.booTH and 
                    movingArrows[arrow].y < self.arrowY + self.booTH and 
                    self.rightPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Boo"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar > -self.lifeBarY - self.greatTH:
                        self.lifeBar -= self.lifeBarWidth/2
                    self.booSingle += 1
                    self.comboSingle = 0
                if (movingArrows[arrow].y < self.arrowY - self.booTH and 
                    movingArrows[arrow].attempt == False):        
                    movingArrows[arrow].score = "Boo"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar > -self.lifeBarY - self.greatTH:
                        self.lifeBar -= self.lifeBarWidth/2
                    self.booSingle += 1
                    self.comboSingle = 0
        
            
            if movingArrows[arrow].direction == "up":
                
                if (movingArrows[arrow].y == self.arrowY and 
                    self.upPressed == True and 
                    movingArrows[arrow].attempt == False):  
                    movingArrows[arrow].score = "Perfect"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.lifeBarWidth
                    self.perfectSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle += 1
                    if self.comboSingle > self.maxComboSingle:
                        self.maxComboSingle = self.comboSingle
                if (movingArrows[arrow].y > self.arrowY - self.greatTH and 
                    movingArrows[arrow].y < self.arrowY + self.greatTH and 
                    self.upPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Great"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.lifeBarWidth/2
                    self.greatSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle += 1
                    if self.comboSingle > self.maxComboSingle:
                        self.maxComboSingle = self.comboSingle
                if (movingArrows[arrow].y > self.arrowY - self.goodTH and 
                    movingArrows[arrow].y < self.arrowY + self.goodTH and 
                    self.upPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Good"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.greatTH
                    self.goodSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle = 0
                if (movingArrows[arrow].y > self.arrowY - self.booTH and 
                    movingArrows[arrow].y < self.arrowY + self.booTH and 
                    self.upPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Boo"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar > -self.lifeBarY - self.greatTH:
                        self.lifeBar -= self.lifeBarWidth/2
                    self.booSingle += 1
                    self.comboSingle = 0
                if (movingArrows[arrow].y < self.arrowY - self.booTH and 
                    movingArrows[arrow].attempt == False):        
                    movingArrows[arrow].score = "Boo"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar > -self.lifeBarY - self.greatTH:
                        self.lifeBar -= self.lifeBarWidth/2
                    self.booSingle += 1
                    self.comboSingle = 0
            
            if movingArrows[arrow].direction == "down":
                
                if (movingArrows[arrow].y == self.arrowY and 
                    self.downPressed == True and 
                    movingArrows[arrow].attempt == False):  
                    movingArrows[arrow].score = "Perfect"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.lifeBarWidth
                    self.perfectSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle += 1
                    if self.comboSingle > self.maxComboSingle:
                        self.maxComboSingle = self.comboSingle
                if (movingArrows[arrow].y > self.arrowY - self.greatTH and 
                    movingArrows[arrow].y < self.arrowY + self.greatTH and 
                    self.downPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Great"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.lifeBarWidth/2
                    self.greatSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle += 1
                    if self.comboSingle > self.maxComboSingle:
                        self.maxComboSingle = self.comboSingle
                if (movingArrows[arrow].y > self.arrowY - self.goodTH and 
                    movingArrows[arrow].y < self.arrowY + self.goodTH and 
                    self.downPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Good"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar < self.lifeBarY:
                        self.lifeBar += self.greatTH
                    self.goodSingle += 1
                    self.successfulHitSingle += 1
                    self.comboSingle = 0
                if (movingArrows[arrow].y > self.arrowY - self.booTH and 
                    movingArrows[arrow].y < self.arrowY + self.booTH and 
                    self.downPressed == True and 
                    movingArrows[arrow].attempt == False):
                    movingArrows[arrow].score = "Boo"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar > -self.lifeBarY - self.greatTH:
                        self.lifeBar -= self.lifeBarWidth/2
                    self.booSingle += 1
                    self.comboSingle = 0
                if (movingArrows[arrow].y < self.arrowY - self.booTH and 
                    movingArrows[arrow].attempt == False):        
                    movingArrows[arrow].score = "Boo"
                    movingArrows[arrow].attempt = True
                    if self.lifeBar > -self.lifeBarY - self.greatTH:
                        self.lifeBar -= self.lifeBarWidth/2
                    self.booSingle += 1
                    self.comboSingle = 0

class SettingPage(object):
    #no-fail mode
    #backgrounds: orange, purple, blue, cyan, forest green, pink
    #multiplayer vs single player

    def __init__(self):
        self.width = 800
        self.height = 600
        self.aboutText = self.windowTitle = "Settings"
        self.leftArrowUnclicked = PhotoImage(file = "gifs/leftArrowUnclicked.gif")
        self.rightArrowUnclicked = PhotoImage(file = "gifs/rightArrowUnclicked.gif")
        self.downArrowUnclicked = PhotoImage(file = "gifs/downArrowUnclicked.gif")
        self.upArrowUnclicked = PhotoImage(file = "gifs/upArrowUnclicked.gif")
        self.settingsBackground = PhotoImage(file = "gifs/settingsBackground.gif")
        self.arrowY = 50
        
        #player mode information
        self.multiPlayerTextColor = "red"
        self.singlePlayerTextColor = "white"
        self.multiPlayerFontSize = 40
        self.singlePlayerFontSize = 45
        self.singlePlayer = True
        
        #no Fail Mode information
        self.noFailTextColor = "red"
        self.yesTextColor = "red"
        self.noTextColor = "white"
        self.noFailFontSize = 40
        self.yesFontSize = 30
        self.noFontSize = 35
        self.noFail = False
        
        #color mode information
        self.backgroundsTextColor = "red"
        self.blackTextColor = "white"
        self.orangeTextColor = "red"
        self.purpleTextColor = "red"
        self.blueTextColor = "red"
        self.forestGreenTextColor = "red"
        self.pinkTextColor = "red"
        self.backgroundsFontSize = 40
        self.blackFontSize = 35
        self.orangeFontSize = 30
        self.purpleFontSize = 30
        self.blueFontSize = 30
        self.forestGreenFontSize = 30
        self.pinkFontSize = 30
        self.blackBackground = True
        self.orangeBackground = False
        self.purpleBackground = False
        self.blueBackground = False
        self.forestGreenBackground = False
        self.pinkBackground = False
        
        #main menu text information
        self.mainMenuLeft = 285
        self.mainMenuRight = 500
        self.mainMenuTop = 490
        self.mainMenuBot = 515
        self.mainMenuEnlarged = 40
        self.mainMenuRegular = 30
        self.mainMenuFontSize = 40
        self.mainMenuTextColor = "red"

        #text locations
        self.displaceMP = 200
        self.textMPY = 150
        self.textNoFailY = 290
        self.backgroundsY = 400
        self.purpleX = 300
        self.blueX = 400
        self.forestGX = 550
        self.pinkX = 700
        
        #text boundaries
        self.SPLeft = 80
        self.SPRight = 325
        self.SPTop = 130
        self.SPBot = 175
        self.MPLeft = 510
        self.MPRight = 700
        self.regularPlayerSize = 40
        self.enlargedPlayerSize = 45
        
        self.yesFailLeft = 330
        self.yesFailRight = 375
        self.yesFailTop = 275
        self.yesFailBot = 305
        self.noFailLeft = 440
        self.noFailRight = 465
        self.regularFailSize = 30
        self.enlargedFailSize = 35
    
        self.blackLeft = 60
        self.blackRight = 142
        self.orangeLeft = 155
        self.orangeRight = 245
        self.purpleLeft = 260
        self.purpleRight = 340
        self.blueLeft = 375
        self.blueRight = 425
        self.forestGLeft = 475
        self.forestGRight = 630
        self.pinkLeft = 675
        self.pinkRight = 730
        self.blackTop = 435
        self.blackBot = 465
        self.enlargedColorSize = 35
        self.regularColorSize = 30

        self.homeLeft = 250
        self.honeRight = 555
        self.homeTop = 535
        self.homeBot = 570
        self.homeRegularSize = 40
        self.homeEnlarged = 45

        self.clickX = 0
        self.clickY = 0

    def drawSettingPage(self, canvas):
        #arrows in the corners
        canvas.create_image(self.width/2, self.height/2, 
                            image = self.settingsBackground)
        canvas.create_image(self.arrowY, self.arrowY, 
                            image = self.leftArrowUnclicked)
        canvas.create_image(self.width - self.arrowY, self.arrowY, 
                            image = self.upArrowUnclicked)
        canvas.create_image(self.arrowY, self.height - self.arrowY, 
                            image = self.downArrowUnclicked)
        canvas.create_image(self.width - self.arrowY, self.height - self.arrowY, 
                            image = self.rightArrowUnclicked)
        
        #Settings Text 
        canvas.create_text(self.width/2, self.arrowY, text = "Settings", 
                           font = "impact 50 bold", fill = "white")
        canvas.create_text(self.width/2 + self.displaceMP, self.textMPY, 
                           text = "Multiplayer", font = "impact " + 
                           str(self.multiPlayerFontSize) + " bold", 
        	               fill = self.multiPlayerTextColor)
        canvas.create_text(self.width/2 - self.displaceMP, self.textMPY, 
                           text = "Single Player", font = "impact " + 
                           str(self.singlePlayerFontSize) + " bold",
        	               fill = self.singlePlayerTextColor)
        #No Fail Mode
        canvas.create_text(self.width/2, self.displaceMP + self.arrowY, 
                           text = "No-Fail Mode", font = "impact " + 
                           str(self.noFailFontSize) + " bold",
        	               fill = self.noFailTextColor)
        canvas.create_text(self.width/2 - self.arrowY, self.textNoFailY, 
                           text = "Yes", font = "impact " + 
                           str(self.yesFontSize) + " bold", 
                           fill = self.yesTextColor)
        canvas.create_text(self.width/2 + self.arrowY, self.textNoFailY, 
                           text = "No", font = "impact " + str(self.noFontSize) 
                           + " bold", fill = self.noTextColor)
        #Different backgrounds
        canvas.create_text(self.width/2, self.backgroundsY, text= "Backgrounds",
        	               font = "impact " + str(self.backgroundsFontSize) + 
                           " bold", fill = self.backgroundsTextColor)
        canvas.create_text(self.textMPY - self.arrowY, self.backgroundsY + 
                           self.arrowY, text = "Black", font = "impact " + 
                           str(self.blackFontSize) + " bold", 
        	               fill = self.blackTextColor)
        canvas.create_text(self.displaceMP, self.backgroundsY + self.arrowY, 
                           text = "Orange", font = "impact " + 
                           str(self.orangeFontSize) + " bold",
        	               fill = self.orangeTextColor)
        canvas.create_text(self.purpleX, self.backgroundsY + self.arrowY, 
                           text = "Purple", font = "impact " + 
                           str(self.purpleFontSize) + " bold",
        	               fill = self.purpleTextColor)
        canvas.create_text(self.blueX, self.backgroundsY + self.arrowY, 
                           text = "Blue", font = "impact " + 
                           str(self.blueFontSize) + " bold",
        	               fill = self.blueTextColor)
        canvas.create_text(self.forestGX, self.backgroundsY + self.arrowY, 
                           text = "Forest Green", font = "impact " + 
                           str(self.forestGreenFontSize) + " bold",
        	               fill = self.forestGreenTextColor)
        canvas.create_text(self.pinkX, self.backgroundsY + self.arrowY, 
                           text = "Pink", font = "impact " + 
                           str(self.pinkFontSize) + " bold", 
                           fill = self.pinkTextColor)
        #back to main menu
        canvas.create_text(self.width/2, self.height - self.arrowY, 
                           text = "Back to Main Menu",
        	               font = "impact "+str(self.mainMenuFontSize)+" bold",
        	               fill = self.mainMenuTextColor)

    def playerModePressed(self, event):
        #single player
        if (self.clickX > self.SPLeft and self.clickX < self.SPRight and
            self.clickY > self.SPTop and self.clickY < self.SPBot):
            if self.singlePlayer == False:
                self.singlePlayer = True
        #multi player
        elif (self.clickX > self.MPLeft and self.clickX < self.MPRight and
            self.clickY > self.SPTop and self.clickY < self.SPBot):
            if self.singlePlayer == True:
                self.singlePlayer = False

    def noFailModePressed(self, event):
        #yes fail mode
        if (self.clickX > self.yesFailLeft and 
            self.clickX < self.yesFailRight and
            self.clickY > self.yesFailTop and self.clickY < self.yesFailBot):
            if self.noFail == False:
                self.noFail = True 
        #no fail mode
        elif (self.clickX > self.noFailLeft and 
            self.clickX < self.noFailRight and
              self.clickY > self.yesFailTop and self.clickY < self.yesFailBot):
            if self.noFail == True:
                self.noFail = False 
    
    
    def backgroundsPressed(self, event):
    	#black text
        if (self.clickX > self.blackLeft and self.clickX < self.blackRight and
            self.clickY > self.blackTop and self.clickY < self.blackBot):
            if self.blackBackground == False:
                self.blackBackground = True
                self.orangeBackground = False
                self.purpleBackground = False
                self.blueBackground = False
                self.forestGreenBackground = False
                self.pinkBackground = False
        #orange text
        elif (self.clickX > self.orangeLeft and 
              self.clickX < self.orangeRight and
              self.clickY > self.blackTop and self.clickY < self.blackBot):
            if self.orangeBackground == False:
                self.orangeBackground = True
                self.blackBackground = False
                self.purpleBackground = False
                self.blueBackground = False
                self.forestGreenBackground = False
                self.pinkBackground = False        
        #purple text
        elif (self.clickX > self.purpleLeft and 
              self.clickX < self.purpleRight and
              self.clickY > self.blackTop and self.clickY < self.blackBot):
            if self.purpleBackground == False:
                self.purpleBackground = True
                self.blackBackground = False
                self.orangeBackground = False
                self.blueBackground = False
                self.forestGreenBackground = False
                self.pinkBackground = False
        #blue text
        elif (self.clickX > self.blueLeft and self.clickX < self.blueRight and
              self.clickY > self.blackTop and self.clickY < self.blackBot):
            if self.blueBackground == False:
                self.blueBackground = True
                self.blackBackground = False
                self.purpleBackground = False
                self.orangeBackground = False
                self.forestGreenBackground = False
                self.pinkBackground = False 
        #forest green text
        elif (self.clickX > self.forestGLeft and 
              self.clickX < self.forestGRight and
              self.clickY > self.blackTop and self.clickY < self.blackBot):
            if self.forestGreenBackground == False:
                self.forestGreenBackground = True
                self.blackBackground = False
                self.purpleBackground = False
                self.blueBackground = False
                self.orangeBackground = False
                self.pinkBackground = False
        #pink text
        elif (self.clickX > self.pinkLeft and self.clickX < self.pinkRight and
              self.clickY > self.blackTop and self.clickY < self.blackBot):
            if self.pinkBackground == False:
                self.pinkBackground = True
                self.blackBackground = False
                self.purpleBackground = False
                self.blueBackground = False
                self.forestGreenBackground = False
                self.orangeBackground = False        
        
    def playerModeMove(self, event):
        #single player vs. multiplayer
        if (event.x > self.SPLeft and event.x < self.SPRight and
            event.y > self.SPTop and event.y < self.SPBot):
            self.singlePlayerFontSize = self.enlargedPlayerSize
            self.singlePlayerTextColor = "white"
        elif (event.x > self.MPLeft and event.x < self.MPRight  and
            event.y > self.SPTop and event.y < self.SPBot):
            self.multiPlayerFontSize = self.enlargedPlayerSize
            self.multiPlayerTextColor = "white"
        else:
            if self.singlePlayer == True:
                self.singlePlayerFontSize = self.enlargedPlayerSize
                self.singlePlayerTextColor = "white"
                self.multiPlayerFontSize = self.regularPlayerSize
                self.multiPlayerTextColor = "red"
            elif self.singlePlayer == False:
                self.singlePlayerFontSize = self.regularPlayerSize
                self.singlePlayerTextColor = "red"
                self.multiPlayerFontSize = self.enlargedPlayerSize
                self.multiPlayerTextColor = "white"

    def noFailModeMove(self, event):
        if (event.x > self.yesFailLeft and event.x < self.yesFailRight and
            event.y > self.yesFailTop and event.y < self.yesFailBot):
            self.yesFontSize = self.enlargedFailSize
            self.yesTextColor = "white" 
        elif (event.x > self.noFailLeft and event.x < self.blackBot and
            event.y > self.yesFailTop and event.y < self.yesFailBot):
            self.noFontSize = self.enlargedFailSize
            self.noTextColor = "white" 
        else:
            if self.noFail == False:
                self.yesFontSize = self.regularFailSize
                self.yesTextColor = "red"
                self.noFontSize = self.enlargedFailSize
                self.noTextColor = "white"
            elif self.noFail == True:
            	self.yesFontSize = self.enlargedFailSize
                self.yesTextColor = "white"
                self.noFontSize = self.regularFailSize
                self.noTextColor = "red"

    def backgroundsMove(self, event):
        #black text
        if (event.x > self.blackLeft and event.x < self.blackRight and
            event.y > self.blackTop and event.y < self.blackBot):
            self.blackFontSize = self.enlargedColorSize
            self.blackTextColor = "white"
        #orange text
        elif (event.x > self.orangeLeft and event.x < self.orangeRight and
            event.y > self.blackTop and event.y < self.blackBot):
            self.orangeFontSize = self.enlargedColorSize
            self.orangeTextColor = "white" 
        #purple text
        elif (event.x > self.purpleLeft and event.x < self.purpleRight and
            event.y > self.blackTop and event.y < self.blackBot):
            self.purpleFontSize = self.enlargedColorSize
            self.purpleTextColor = "white" 
        #blue text
        elif (event.x > self.blueLeft and event.x < self.blueRight and
            event.y > self.blackTop and event.y < self.blackBot):
            self.blueFontSize = self.enlargedColorSize
            self.blueTextColor = "white" 
        #forest green text
        elif (event.x > self.forestGLeft and event.x < self.forestGRight and
            event.y > self.blackTop and event.y < self.blackBot):
            self.forestGreenFontSize = self.enlargedColorSize
            self.forestGreenTextColor = "white" 
        #pink text
        elif (event.x > self.pinkLeft and event.x < self.pinkRight and
            event.y > self.blackTop and event.y < self.blackBot):
            self.pinkFontSize = self.enlargedColorSize
            self.pinkTextColor = "white"
        else:
            if self.blackBackground == True:
                self.blackFontSize = self.enlargedColorSize
                self.blackTextColor = "white"
                self.orangeFontSize = self.regularColorSize
                self.orangeTextColor = "red"
                self.purpleFontSize = self.regularColorSize
                self.purpleTextColor = "red"
                self.blueFontSize = self.regularColorSize
                self.blueTextColor = "red"
                self.forestGreenFontSize = self.regularColorSize
                self.forestGreenTextColor = "red"
                self.pinkFontSize = self.regularColorSize
                self.pinkTextColor = "red"
            elif self.orangeBackground == True:
                self.orangeFontSize = self.enlargedColorSize
                self.orangeTextColor = "white"
                self.blackFontSize = self.regularColorSize
                self.blackTextColor = "red"
                self.purpleFontSize = self.regularColorSize
                self.purpleTextColor = "red"
                self.blueFontSize = self.regularColorSize
                self.blueTextColor = "red"
                self.forestGreenFontSize = self.regularColorSize
                self.forestGreenTextColor = "red"
                self.pinkFontSize = self.regularColorSize
                self.pinkTextColor = "red"
            elif self.purpleBackground == True:
                self.purpleFontSize = self.enlargedColorSize
                self.purpleTextColor = "white"
                self.blackFontSize = self.regularColorSize
                self.blackTextColor = "red"
                self.orangeFontSize = self.regularColorSize
                self.orangeTextColor = "red"
                self.blueFontSize = self.regularColorSize
                self.blueTextColor = "red"
                self.forestGreenFontSize = self.regularColorSize
                self.forestGreenTextColor = "red"
                self.pinkFontSize = self.regularColorSize
                self.pinkTextColor = "red"
            elif self.blueBackground == True:
                self.blueFontSize = self.enlargedColorSize
                self.blueTextColor = "white"
                self.blackFontSize = self.regularColorSize
                self.blackTextColor = "red"
                self.orangeFontSize = self.regularColorSize
                self.orangeTextColor = "red"
                self.purpleFontSize = self.regularColorSize
                self.purpleTextColor = "red"
                self.forestGreenFontSize = self.regularColorSize
                self.forestGreenTextColor = "red"
                self.pinkFontSize = self.regularColorSize
                self.pinkTextColor = "red"
            elif self.forestGreenBackground == True:
                self.forestGreenFontSize = self.enlargedColorSize
                self.forestGreenTextColor = "white"
                self.blackFontSize = self.regularColorSize
                self.blackTextColor = "red"
                self.orangeFontSize = self.regularColorSize
                self.orangeTextColor = "red"
                self.purpleFontSize = self.regularColorSize
                self.purpleTextColor = "red"
                self.blueFontSize = self.regularColorSize
                self.blueTextColor = "red"
                self.pinkFontSize = self.regularColorSize
                self.pinkTextColor = "red"
            elif self.pinkBackground == True:
                self.pinkFontSize = self.enlargedColorSize
                self.pinkTextColor = "white"
                self.blackFontSize = self.regularColorSize
                self.blackTextColor = "red"
                self.orangeFontSize = self.regularColorSize
                self.orangeTextColor = "red"
                self.purpleFontSize = self.regularColorSize
                self.purpleTextColor = "red"
                self.blueFontSize = self.regularColorSize
                self.blueTextColor = "red"
                self.forestGreenFontSize = self.regularColorSize
                self.forestGreenTextColor = "red"

    def onMouseSettings(self, event):
        self.clickX, self.clickY = event.x, event.y
        self.playerModePressed(event)
        self.noFailModePressed(event)
        self.backgroundsPressed(event)

    #checks if clicks back to main menu
    def backToHome(self, event):
        if (self.clickX > self.homeLeft and self.clickX < self.honeRight and
        	self.clickY > self.homeTop and self.clickY < self.homeBot):
            return True

    def onMouseSettingsMove(self, event):
        self.playerModeMove(event)
        self.noFailModeMove(event)
        self.backgroundsMove(event)
        if (event.x > self.homeLeft and event.x < self.honeRight and
            event.y > self.homeTop and event.y < self.homeBot):
            self.mainMenuFontSize = self.homeEnlarged
            self.mainMenuTextColor = "white"
        else:
            self.mainMenuFontSize = self.homeRegularSize
            self.mainMenuTextColor = "red"

class StatisticsPage(object):
    
    def __init__(self):
        self.width = 800
        self.height = 600
        self.aboutText = self.windowTitle = "Statistics"
        self.leftArrowUnclicked = PhotoImage(file = "gifs/leftArrowUnclicked.gif")
        self.rightArrowUnclicked = PhotoImage(file = "gifs/rightArrowUnclicked.gif")
        self.downArrowUnclicked = PhotoImage(file = "gifs/downArrowUnclicked.gif")
        self.upArrowUnclicked = PhotoImage(file = "gifs/upArrowUnclicked.gif")
        self.backgroundStatistics = PhotoImage(file ="gifs/statisticsBackground.gif")
        self.mainMenuFontSize = 30
        self.textDisplace = 200
        self.textTopDisplace = 100
        self.arrowY = 50
        #letter grades
        self.scoreD = 60
        self.scoreC = 70
        self.scoreB = 80
        self.scoreA = 90
        #main menu location
        self.mainMenuLeft = 285
        self.mainMenuRight = 500
        self.mainMenuTop = 490
        self.mainMenuBot = 515
        self.mainMenuFontSize = 30
        self.mainMenuEnlarged = 40
        self.mainMenuRegular = 30

    #performance of each arrow
    def drawArrowScores(self, canvas, perfect, great, good, boo):
        canvas.create_text(self.textDisplace, self.height/2 - self.textDisplace, 
                           text = "Perfect: " + str(perfect), 
                           font = "Impact 30 bold", fill = "white")
        canvas.create_text(self.textDisplace, 
                           self.height/2 - self.textTopDisplace, 
                           text = "Great: " + str(great), 
                           font = "Impact 30 bold", fill = "white")
        canvas.create_text(self.textDisplace, self.height/2, 
                           text = "Good: " + str(good), 
                           font = "Impact 30 bold", fill = "white")
        canvas.create_text(self.textDisplace, 
                           self.height/2 + self.textTopDisplace, 
                           text = "Boo: " + str(boo), font = "Impact 30 bold", 
                           fill = "white")
    
    #draws performance of each arrow for multiplayer (two columns)
    def drawArrowScoresMP(self, canvas, perfect, great, good, boo, 
                                        perfectSP, greatSP, goodSP, booSP):
        canvas.create_text(self.width/2 - self.textDisplace, 
                           self.height/2 - self.textDisplace, 
                           text = "Perfect: " + str(perfectSP), 
                           font = "Impact 30 bold", fill = "white")
        canvas.create_text(self.width/2 - self.textDisplace, 
                           self.height/2 - (self.textTopDisplace + self.arrowY), 
                           text = "Great: " + str(greatSP), 
                           font = "Impact 30 bold", fill = "white")
        canvas.create_text(self.width/2 - self.textDisplace, 
                           self.height/2 - self.textTopDisplace, 
                           text = "Good: " + str(goodSP), 
                           font = "Impact 30 bold", fill = "white")
        canvas.create_text(self.width/2 - self.textDisplace, 
                           self.height/2 - self.arrowY, 
                           text = "Boo: " + str(booSP), 
                           font = "Impact 30 bold", fill = "white")
        
        canvas.create_text(self.width/2 + self.textDisplace, 
                           self.height/2 - self.textDisplace, 
                           text = "Perfect: " + str(perfect), 
                           font = "Impact 30 bold", fill = "white")
        canvas.create_text(self.width/2 + self.textDisplace, 
                           self.height/2 - (self.textTopDisplace + self.arrowY), 
                           text = "Great: " + str(great), 
                           font = "Impact 30 bold", fill = "white")
        canvas.create_text(self.width/2 + self.textDisplace, 
                           self.height/2 - self.textTopDisplace, 
                           text = "Good: " + str(good), font = "Impact 30 bold", 
                           fill = "white")
        canvas.create_text(self.width/2 + self.textDisplace, 
                           self.height/2 - self.arrowY, 
                           text = "Boo: " + str(boo), font = "Impact 30 bold", 
                           fill = "white")
    
    #draws max combo, percentage of notes hit, and grades
    def drawComboPercentage(self, canvas, maxCombo, successfulHits, totalNotes):
        canvas.create_text(self.width/2 + self.textTopDisplace, 
                           self.height/2 - self.textDisplace, 
                           text = "Max Combo: " + str(maxCombo), 
                           font = "Impact 30 bold", fill = "white")
        percentage = round((successfulHits/float(totalNotes)) * 
                            self.textTopDisplace)
        canvas.create_text(self.width/2 + self.textTopDisplace, 
                           self.height/2, text = "Percentage Hit: " + 
                           str(percentage), font = "Impact 30 bold", 
                           fill = "white")
        self.drawGrade(canvas, percentage)
    
    def drawComboPercentageMP(self, canvas, maxCombo, successfulHits, 
                                    maxComboSP, successfulHitSP, totalNotes):
        canvas.create_text(self.width/2 - self.textDisplace, self.height/2, 
                           text = "Max Combo: " + str(maxComboSP), 
                           font = "Impact 30 bold", fill = "white")
        percentage = round((successfulHitSP/float(totalNotes)) * 
                            self.textTopDisplace)
        canvas.create_text(self.width/2 - self.textDisplace, 
                           self.height/2 + self.arrowY, 
                           text = "Percentage Hit: " + str(percentage), 
                           font = "Impact 30 bold", fill = "white")
        self.drawGradeMP(canvas, percentage)
        canvas.create_text(self.width/2 + self.textDisplace, 
                           self.height/2, text = "Max Combo: " + str(maxCombo), 
                           font = "Impact 30 bold", fill = "white")
        percentage = round((successfulHits/float(totalNotes)) * 
                            self.textTopDisplace)
        canvas.create_text(self.width/2 + self.textDisplace, 
                           self.height/2 + self.arrowY, 
                           text = "Percentage Hit: " + str(percentage), 
                           font = "Impact 30 bold", fill = "white")
        self.drawGrade(canvas, percentage)

    def drawGrade(self, canvas, percentage):
        if percentage < self.scoreD:
            canvas.create_text(self.width/2 + self.textDisplace, 
                               self.height/2 + self.textTopDisplace, 
                               text = "Grade: F", font = "Impact 30 bold", 
                               fill = "white")
        elif percentage <= self.scoreC:
            canvas.create_text(self.width/2 + self.textDisplace, 
                               self.height/2 + self.textTopDisplace, 
                               text = "Grade: D", font = "Impact 30 bold", 
                               fill = "white")
        elif percentage <= self.scoreB:
            canvas.create_text(self.width/2 + self.textDisplace, 
                               self.height/2 + self.textTopDisplace, 
                               text = "Grade: C", font = "Impact 30 bold", 
                               fill = "white")
        elif percentage <= self.scoreA:
            canvas.create_text(self.width/2 + self.textDisplace, 
                               self.height/2 + self.textTopDisplace, 
                               text = "Grade: B", font = "Impact 30 bold", 
                               fill = "white")
        elif percentage <= self.textTopDisplace:
            canvas.create_text(self.width/2 + self.textDisplace, 
                               self.height/2 + self.textTopDisplace, 
                               text = "Grade: A", font = "Impact 30 bold", 
                               fill = "white")

    def drawGradeMP(self, canvas, percentage):
        if percentage < self.scoreD:
            canvas.create_text(self.width/2 - self.textDisplace, 
                               self.height/2 + self.textTopDisplace, 
                               text = "Grade: F", font = "Impact 30 bold", 
                               fill = "white")
        elif percentage <= self.scoreC:
            canvas.create_text(self.width/2 - self.textDisplace, 
                               self.height/2 + self.textTopDisplace, 
                               text = "Grade: D", font = "Impact 30 bold", 
                               fill = "white")
        elif percentage <= self.scoreB:
            canvas.create_text(self.width/2 - self.textDisplace, 
                               self.height/2 + self.textTopDisplace, 
                               text = "Grade: C", font = "Impact 30 bold", 
                               fill = "white")
        elif percentage <= self.scoreA:
            canvas.create_text(self.width/2 - self.textDisplace,
                               self.height/2 + self.textTopDisplace, 
                               text = "Grade: B", font = "Impact 30 bold", 
                               fill = "white")
        elif percentage <= self.textTopDisplace:
            canvas.create_text(self.width/2 - self.textDisplace, 
                               self.height/2 + self.textTopDisplace, 
                               text = "Grade: A", font = "Impact 30 bold", 
                               fill = "white")

    def drawStatisticsPage(self, canvas, perfect, great, good, boo, 
                                         maxCombo, successfulHits, totalNotes):
        canvas.create_image(self.width/2, self.height/2, 
                            image = self.backgroundStatistics)
        self.drawArrowScores(canvas, perfect, great, good, boo)
        self.drawComboPercentage(canvas, maxCombo, successfulHits, totalNotes)
        canvas.create_text(self.width/2, self.height - self.textTopDisplace, 
                           text = "Back to Main Menu", font = "Impact " + 
                           str(self.mainMenuFontSize) + " bold", fill = "white")

   #for multiplayer, use the same return to main menu though
    def drawStatisticsPageMP(self, canvas, perfect, great, good, boo, 
                             perfectSP, greatSP, goodSP, booSP, maxCombo, 
                             successfulHits, maxComboSP, successfulHitSP, 
                             totalNotes):
        canvas.create_image(self.width/2, self.height/2, 
                            image = self.backgroundStatistics)
        self.drawArrowScoresMP(canvas, perfect, great, good, boo, 
                               perfectSP, greatSP, goodSP, booSP)
        self.drawComboPercentageMP(canvas, maxCombo, successfulHits, 
                                   maxComboSP, successfulHitSP, totalNotes)
        canvas.create_text(self.width/2, self.height - self.textTopDisplace, 
                           text = "Back to Main Menu", font = "Impact " + 
                           str(self.mainMenuFontSize) + " bold", fill = "white")

    #back to main menu
    def onMouseStatistics(self, event):
        if (event.x > self.mainMenuLeft and event.x < self.mainMenuRight and
            event.y > self.mainMenuTop and event.y < self.mainMenuBot):
            return True
    
    def onMouseStatisticsMove(self, event):
        if (event.x > self.mainMenuLeft and event.x < self.mainMenuRight and
            event.y > self.mainMenuTop and event.y < self.mainMenuBot):
            self.mainMenuFontSize = self.mainMenuEnlarged
        else:
            self.mainMenuFontSize = self.mainMenuRegular

#Select a song page
class SelectASong(Tkinter.Frame):
    def __init__(self):
        self.width = 800
        self.height = 600
        self.selectASongBackground = PhotoImage(file = "gifs/redBackground.gif")
        self.playFontSize = 20
        self.playEnlarged = 30
        self.playRegular = 20
        self.playLeft = 330
        self.playRight = 475
        self.playTop = 395
        self.playBot = 410
        self.browseLeft = 300
        self.browseRight = 500
        self.browseTop = 290
        self.browseBot = 310
        self.browseFontSize = 20
        self.browseFontColor = "white"
        
        self.selectedASong = False

        self.file_opt = options = {}
        #options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('wav files', '.wav')]
        options['initialdir'] = 'C:\\'
    
    def askOpenFileName(self):
        #get filename
        filename = tkFileDialog.askopenfilename(**self.file_opt)
        return filename

    def drawSelectASong(self, canvas):
        canvas.create_image(self.width/2, self.height/2, 
                            image = self.selectASongBackground)
        canvas.create_text(self.width/2, self.height/(2*3), 
                           text = "Pick a song here! Only .wav files please...", 
                           font = "impact 26 bold", fill = "white")
        canvas.create_text(self.width/2, self.height/2, 
                           text = "Click to browse!", 
                           font = "impact " + str(self.browseFontSize)+" bold", 
                           fill = self.browseFontColor)
        canvas.create_text(self.width/2, self.height - (self.height/3), 
                           text = "Click here to play!", font = "impact "+ 
                           str(self.playFontSize) + " bold", fill = "white")

    def onMouseSelectPlay(self, event):
        if (event.x > self.playLeft and event.x < self.playRight and 
            event.y > self.playTop and event.y < self.playBot):
            if self.selectedASong == True:
                return True
            else:
                return False
    
    def onMouseSelectBrowse(self, event):
        if (event.x > self.browseLeft and event.x < self.browseRight and 
            event.y > self.browseTop and event.y < self.browseBot):
            return True

    def onMouseSelectMove(self, event):
        if (event.x > self.playLeft and event.x < self.playRight and 
            event.y > self.playTop and event.y < self.playBot):
            self.playFontSize = self.playEnlarged
        else:
            self.playFontSize = self.playRegular
        if (event.x > self.browseLeft and event.x < self.browseRight and 
            event.y > self.browseTop and event.y < self.browseBot):
            self.browseFontColor = "black"
        else:
            self.browseFontColor = "white"

class DDR(eventBasedAnimation.Animation):

    def onInit(self):
        self.aboutText = self.windowTitle = "Play!"
        self.width = 800
        self.height = 600
        self.arrowY = 50
        
        #make instances of all the screens
        self.gameScreen = GameScreen()
        self.settingPage = SettingPage()
        self.statisticsPage = StatisticsPage()
        self.homePage = HomePage()
        self.selectASong = SelectASong()
        self.songClass = Song()
        self.song = None
        #where the list of arrows will be
        self.movingArrows = []
        self.movingArrowsFirstPlayer = []
        self.movingArrowsSecondPlayer = []
        
        #keeps track of what to draw when on the same canvas
        self.isHomeScreen = True
        self.isSettings = False
        self.isStatistics = False
        self.isGameScreen = False
        self.isSelect = False
    
    #takes the beat times for each song and puts in a list. 
    def songBeatTimes(self, song):
        beatTimes = self.songClass.beatsInAubio(song)
        #single player only
        self.movingArrows = self.songClass.makeArrows(beatTimes, 0)

        #values are initialized but won't use them unless multiplayer
        self.movingArrowsFirstPlayer = self.songClass.makeArrows(beatTimes, 1)
        self.movingArrowsSecondPlayer = self.songClass.makeArrows(beatTimes, 2)
        self.totalNotes = len(self.movingArrows)

    #uses pygame to play music
    def playMusic(self, song):
        music_file = song
        pg.mixer.init()
        pg.mixer.music.load(music_file)
        pg.mixer.music.play()
        self.stopMusic()

    def stopMusic(self):
        pg.mixer.music.pause()

    def unPause(self):
        pg.mixer.music.unpause()

    def onKey(self, event):
        if event.keysym == "Up":
            self.gameScreen.upPressed = True
        elif event.keysym == "Down":
            self.gameScreen.downPressed = True
        elif event.keysym == "Left":
            self.gameScreen.leftPressed = True
        elif event.keysym == "Right":
            self.gameScreen.rightPressed = True
        elif event.keysym == "w":
            self.gameScreen.upPressedSP = True
        elif event.keysym == "s":
            self.gameScreen.downPressedSP = True
        elif event.keysym == "a":
            self.gameScreen.leftPressedSP = True
        elif event.keysym == "d":
            self.gameScreen.rightPressedSP = True
        elif event.keysym == "p": #pauses
            if self.gameScreen.isPlaying == False:
                self.gameScreen.isPlaying = True
                self.unPause()
            elif self.gameScreen.isPlaying == True:
                self.stopMusic() 
                self.gameScreen.isPlaying = False
        #starts the game
        elif event.keysym == "space" and self.isGameScreen == True: 
            self.unPause()
            self.gameScreen.isPlaying = True
        
        elif event.keysym == "r":
            self.onInit()

        #STATISTICS PAGE!!
        elif event.keysym == "q": #quits the game even in middle of game
            self.stopMusic()
            self.isStatistics = True
            self.isGameScreen = False
            self.isHomeScreen = False
            self.isSettings = False
            self.isSelect = False
            
    
    def onKeyRelease(self, event):
        if event.keysym == "Up":
            self.gameScreen.upPressed = False
        elif event.keysym == "Down":
            self.gameScreen.downPressed = False
        elif event.keysym == "Left":
            self.gameScreen.leftPressed = False
        elif event.keysym == "Right":
            self.gameScreen.rightPressed = False
        elif event.keysym == "w":
            self.gameScreen.upPressedSP = False
        elif event.keysym == "s":
            self.gameScreen.downPressedSP = False
        elif event.keysym == "a":
            self.gameScreen.leftPressedSP = False
        elif event.keysym == "d":
            self.gameScreen.rightPressedSP = False

    def onDraw(self, canvas):
        if self.isHomeScreen == True:
            self.homePage.drawHomePage(canvas)
        elif self.isSelect == True:
            self.selectASong.drawSelectASong(canvas)
        elif self.isSettings == True:
            self.settingPage.drawSettingPage(canvas)
        elif self.isStatistics == True:
            if self.settingPage.singlePlayer == True:
                self.statisticsPage.drawStatisticsPage(canvas, 
                                            self.gameScreen.perfectSingle, 
                                            self.gameScreen.greatSingle, 
                                            self.gameScreen.goodSingle, 
                                            self.gameScreen.booSingle, 
                                            self.gameScreen.maxComboSingle, 
                                            self.gameScreen.successfulHitSingle, 
                                            self.totalNotes)
            elif self.settingPage.singlePlayer == False:
                self.statisticsPage.drawStatisticsPageMP(canvas, 
                                            self.gameScreen.perfectSingle,
                                            self.gameScreen.greatSingle,
                                            self.gameScreen.goodSingle,
                                            self.gameScreen.booSingle,
                                            self.gameScreen.perfectSP,
                                            self.gameScreen.greatSP,
                                            self.gameScreen.goodSP,
                                            self.gameScreen.booSP,
                                            self.gameScreen.maxComboSingle,
                                            self.gameScreen.successfulHitSingle,
                                            self.gameScreen.maxComboSP,
                                            self.gameScreen.successfulHitSP,
                                            self.totalNotes)
        elif self.isGameScreen == True:
            if self.settingPage.blackBackground:
                self.gameScreen.drawGameScreenBackground(canvas, "black")
                if self.settingPage.singlePlayer == True:
                    self.gameScreen.drawCombos(canvas, "white")
                if self.settingPage.singlePlayer == False:
                    self.gameScreen.drawCombosMP(canvas, "white", "white")
            if self.settingPage.orangeBackground:
                self.gameScreen.drawGameScreenBackground(canvas, "orange")
                if self.settingPage.singlePlayer == True:
                    self.gameScreen.drawCombos(canvas, "white")
                if self.settingPage.singlePlayer == False:
                    self.gameScreen.drawCombosMP(canvas, "black", "white")
            if self.settingPage.purpleBackground:
                self.gameScreen.drawGameScreenBackground(canvas, "purple")
                if self.settingPage.singlePlayer == True:
                    self.gameScreen.drawCombos(canvas, "white")
                if self.settingPage.singlePlayer == False:
                    self.gameScreen.drawCombosMP(canvas, "black", "white")
            if self.settingPage.blueBackground:
                self.gameScreen.drawGameScreenBackground(canvas, "blue")
                if self.settingPage.singlePlayer == True:
                    self.gameScreen.drawCombos(canvas, "grey")
                if self.settingPage.singlePlayer == False:
                    self.gameScreen.drawCombosMP(canvas, "black", "grey")
            if self.settingPage.forestGreenBackground:
                self.gameScreen.drawGameScreenBackground(canvas, "forestGreen")
                if self.settingPage.singlePlayer == True:
                    self.gameScreen.drawCombos(canvas, "grey")
                if self.settingPage.singlePlayer == False:
                    self.gameScreen.drawCombosMP(canvas, "grey", "grey")
            if self.settingPage.pinkBackground:
                self.gameScreen.drawGameScreenBackground(canvas, "pink")
                if self.settingPage.singlePlayer == True:
                    self.gameScreen.drawCombos(canvas, "white")
                if self.settingPage.singlePlayer == False:
                    self.gameScreen.drawCombosMP(canvas, "black", "white")
            if self.settingPage.singlePlayer == True:
                if self.settingPage.noFail == False:
                    self.gameScreen.drawLifeBar(canvas)
                self.gameScreen.drawGameScreen(canvas, self.movingArrows)
                if self.gameScreen.isGameOverSingle == True:
                    self.stopMusic()
                    self.gameScreen.drawGameOver(canvas)
            elif self.settingPage.singlePlayer == False: #if multiplayer
                if self.settingPage.noFail == False:
                    self.gameScreen.drawLifeBar(canvas)
                    self.gameScreen.drawLifeBarSP(canvas)
                self.gameScreen.drawGameScreenMP(canvas, 
                                                 self.movingArrowsFirstPlayer, 
                                                 self.movingArrowsSecondPlayer)
                if (self.gameScreen.isGameOverSingle == True and 
                    self.gameScreen.isGameOverSP == True):
                    self.stopMusic()
                    self.gameScreen.gameOverTextMP(canvas)
                if self.gameScreen.isGameOverSingle == True:
                    self.gameScreen.drawGameOverFP(canvas)
                if self.gameScreen.isGameOverSP == True:
                    self.gameScreen.drawGameOverSP(canvas)


    
    def onMouse(self, event):
        #navigating from home screen
        if self.isHomeScreen == True:
            if self.homePage.onMouseHomeGameStart(event):
                self.isSelect = True
                self.isGameScreen = False
                self.isHomeScreen = False
                self.isSettings = False
                self.isStatistics = False
            elif self.homePage.onMouseHomeSetting(event):
                self.isSettings = True
                self.isSelect = False
                self.isGameScreen = False
                self.isHomeScreen = False
                self.isStatistics = False
        #navigating from settings 
        if self.isSettings == True:
            self.settingPage.onMouseSettings(event)
            #click to go back to main menu (home page)
            if self.settingPage.backToHome(event):
                self.isHomeScreen = True
                self.isSelect = False
                self.isGameScreen = False
                self.isSettings = False
                self.isStatistics = False
        #navigate from Statistics
        if self.isStatistics == True:
            #resets everything when go back to main menu
            if self.statisticsPage.onMouseStatistics(event):
                self.isHomeScreen = True
                self.isSelect = False
                self.isGameScreen = False
                self.isSettings = False
                self.isStatistics = False
                #reset everything
                self.movingArrows = []
                self.movingArrowsFirstPlayer = []
                self.movingArrowsSecondPlayer = []
                self.gameScreen.isPlaying = False
                self.gameScreen.isGameOverSingle = False
                self.gameScreen.isGameOverSP = False
                self.gameScreen.lifeBar = 0
                self.gameScreen.lifeBarSP = 0
                self.song = None
                self.selectASong.selectedASong = False

                self.gameScreen.arrowCount = 0
                self.gameScreen.comboSingle = 0
                self.gameScreen.maxComboSingle = 0
                self.gameScreen.successfulHitSingle = 0
                self.gameScreen.perfectSingle = 0
                self.gameScreen.greatSingle = 0
                self.gameScreen.goodSingle = 0
                self.gameScreen.booSingle = 0
        
                self.gameScreen.comboSP = 0
                self.gameScreen.maxComboSP = 0
                self.gameScreen.successfulHitSP = 0
                self.gameScreen.perfectSP = 0
                self.gameScreen.greatSP = 0
                self.gameScreen.goodSP = 0
                self.gameScreen.booSP = 0

        #navigate from select a song
        if self.isSelect == True:
            if self.selectASong.onMouseSelectBrowse(event):
                #does beat analyzing and sets up the arrows here
                self.song = self.selectASong.askOpenFileName()
                self.songBeatTimes(self.song)
                self.playMusic(self.song)
                self.selectASong.selectedASong = True
            if self.selectASong.onMouseSelectPlay(event) == False:
                tkMessageBox.showinfo("error", "Pick a song!")
            if self.selectASong.onMouseSelectPlay(event):
                self.isGameScreen = True
                self.isHomeScreen = False
                self.isSelect = False
                self.isSettings = False
                self.isStatistics = False


    def onMouseMove(self, event):
        if self.isHomeScreen == True:
            self.homePage.onMouseHomeMove(event)
        if self.isSettings == True:
            self.settingPage.onMouseSettingsMove(event)
        if self.isStatistics == True:
            self.statisticsPage.onMouseStatisticsMove(event)
        if self.isSelect == True:
            self.selectASong.onMouseSelectMove(event)


    def onStep(self):

        if (self.isGameScreen == True and self.gameScreen.isPlaying == True and 
            self.settingPage.singlePlayer == True):
            if self.gameScreen.isGameOverSingle == False:
                self.gameScreen.arrowScore(self.movingArrows)
                for arrow in range(len(self.movingArrows)):
                    self.movingArrows[arrow].onStep()
                    if (self.movingArrows[arrow].attempt == True and 
                        self.movingArrows[arrow].counter < 
                        self.gameScreen.counterTop):
                        self.movingArrows[arrow].counter += 1
                    if self.movingArrows[-1].y < (-self.arrowY * (2*2)):
                        self.gameScreen.arrowCount+= 1
                        if self.gameScreen.arrowCount == self.arrowY*2:
                            self.gameScreen.isPlaying = False
                            self.isStatistics = True
                            self.isGameScreen = False
        elif (self.isGameScreen == True and self.gameScreen.isPlaying == True 
              and self.settingPage.singlePlayer == False):
            self.gameScreen.arrowScore(self.movingArrowsFirstPlayer)
            self.gameScreen.arrowScoreSP(self.movingArrowsSecondPlayer)
            if self.gameScreen.isGameOverSingle == False:
                for arrow in range(len(self.movingArrowsFirstPlayer)):
                    self.movingArrowsFirstPlayer[arrow].onStep()
                    if (self.movingArrowsFirstPlayer[arrow].attempt == True and 
                        self.movingArrowsFirstPlayer[arrow].counter < 
                        self.gameScreen.counterTop):
                        self.movingArrowsFirstPlayer[arrow].counter += 1
                    if self.movingArrowsFirstPlayer[-1].y < (-self.arrowY * 10):
                        self.gameScreen.arrowCount+= 1
                        if self.gameScreen.arrowCount == self.arrowY*2:
                            self.gameScreen.isPlaying = False
                            self.isStatistics = True
                            self.isGameScreen = False
            if self.gameScreen.isGameOverSP == False:
                for arrow in range(len(self.movingArrowsSecondPlayer)):
                    self.movingArrowsSecondPlayer[arrow].onStep()
                    if (self.movingArrowsSecondPlayer[arrow].attempt == True and
                        self.movingArrowsSecondPlayer[arrow].counter < 
                        self.gameScreen.counterTop):
                        self.movingArrowsSecondPlayer[arrow].counter += 1
                    if self.movingArrowsSecondPlayer[-1].y < (-self.arrowY*10):
                        self.gameScreen.arrowCount+= 1
                        if self.gameScreen.arrowCount == self.arrowY*2:
                            self.gameScreen.isPlaying = False
                            self.isStatistics = True
                            self.isGameScreen = False

#timerDelay in milliseconds, 
#1000 milliseconds in 1 second
def playDDR():
    DDR(width = 800, height = 600, timerDelay = 30).run()

playDDR()

if __name__ == '__main__':
    playDDR()

