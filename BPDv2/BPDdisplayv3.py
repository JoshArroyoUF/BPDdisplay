
# importing the required libraries
 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import BPDclass
import random
import itertools
import copy
import configparser
import math
import ast
from collections import defaultdict

parser = configparser.ConfigParser()
parser.read("config.txt")

default_size = int(parser.get("config", "default_size"))
default_color= parser.get("config", "default_color")

scale = int(parser.get("config", "default_scale"))
highlight = False
goodpats = ast.literal_eval(parser.get("config", "goodpats"))
badpats = ast.literal_eval(parser.get("config", "badpats"))

#default_size = 7
#default_color = 'Green'
colors = ['Blue', 'Brown', 'Chartreuse', 'Cyan', 'Gold', 'Green', 'Navy', 'Orange', 'Pink', 'Plum', 'Purple', 'Red', 'Turquoise']

class Insertion(QDialog):
    def __init__(self, widget):
        super(Insertion, self).__init__(widget)
        self.main = widget
        self.setWindowTitle("Insert Biword")
        
        #Creates insertion inputs
        self.biwordtop = QLineEdit(self)
        self.biwordtop.resize(40,40)
        self.biwordtop.move(50, 50)
        self.biwordtop.setFont(QFont('Arial', 10))
        
        self.biwordbot = QLineEdit(self)
        self.biwordbot.resize(40,40)
        self.biwordbot.move(50, 100)
        self.biwordbot.setFont(QFont('Arial', 10))
        
        #Creates insertion buttons
        
        self.leftinsert = QPushButton(self)
        self.leftinsert.setText("Left")
        self.leftinsert.clicked.connect(self.left_clicked)
        self.leftinsert.setFont(QFont('Arial', 10))
        self.leftinsert.move(100, 50)
        
        self.rightinsert = QPushButton(self)
        self.rightinsert.setText("Right")
        self.rightinsert.clicked.connect(self.right_clicked)
        self.rightinsert.setFont(QFont('Arial', 10))
        self.rightinsert.move(100, 100)

        self.show()
        
    def left_clicked(self):
        biword = [0,0]
        biword[0] = int(self.biwordtop.text())
        biword[1] = int(self.biwordbot.text())
        if biword[0] > biword[1]:
            error_dialog = QErrorMessage(self.main)
            error_dialog.showMessage('k too small!')
        else:
            self.main.BPD.leftinsertionstep(biword)
            self.main.Dream(self.main.BPD)
    
    def right_clicked(self):
        biword = [0,0]
        biword[0] = int(self.biwordtop.text())
        biword[1] = int(self.biwordbot.text())
        if biword[0] > biword[1]:
            error_dialog = QErrorMessage(self.main)
            error_dialog.showMessage('k too small!')
        else:
            self.main.BPD.rightinsertionstep(biword)
            self.main.Dream(self.main.BPD)
        
        
class ClickWidget(QLabel):
    def __init__(self, widget, r, c):
        super(ClickWidget, self).__init__(widget)
        self.main = widget
        self.clickcount = 0
        self.row = r
        self.col = c
        
    def mousePressEvent(self, event):
        
        
        if self.main.mode == 0:
            if [self.row,self.col] not in self.main.BPD.elbows:
                self.main.BPD.elbows.append([self.row,self.col])
            else:
                self.main.BPD.elbows.remove([self.row,self.col])
            
            self.main.Dream(self.main.BPD)
            
        if self.main.mode == 1:
            if [self.row, self.col] in self.main.BPD.elbows:
                self.main.BPD.mindroop([self.row, self.col])
                self.main.Dream(self.main.BPD)
                
        if self.main.mode == 2:
            self.main.BPD.__init__(self.main.BPD.size, self.main.BPD.elbows, co=self.main.co)
            crosspipes = []
            for pipe in self.main.BPD.pipes:
                if [self.row, self.col] in pipe:
                    crosspipes.append(pipe)
            if len(crosspipes) == 2:
                if [self.row, self.col] in self.main.BPD.elbows:
                    self.main.BPD.crossbumpswap([self.row, self.col])
                    self.main.Dream(self.main.BPD)
                    return
                else:
                    for place in crosspipes[0]:
                        if place in crosspipes[1]:
                            if place in self.main.BPD.elbows:
                                self.main.BPD.crossbumpswap(place)
                                self.main.Dream(self.main.BPD)
                                return
                    self.main.BPD.elbows.append([self.row, self.col])
                    self.main.BPD.__init__(self.main.BPD.size, self.main.BPD.elbows, co=self.main.co)
                    self.main.Dream(self.main.BPD)

        
class PermBox(QDialog):
    def __init__(self, widget):
        super(PermBox, self).__init__(widget)
        self.main = widget
        self.setWindowTitle("Set Permutation")
        
        self.permbox = QLineEdit(self)
        self.permbox.resize(250,40)
        self.permbox.move(50, 50)
        self.permbox.setFont(QFont('Arial', 10))
        
        self.permbox.editingFinished.connect(self.enterPress)
        
        self.show()
    
    def enterPress(self):
        setperm = self.permbox.text().split(',')
        for i in range(len(setperm)):
            setperm[i] = int(setperm[i])
        if len(setperm) > 1:
            for i in range(len(setperm)):
                if i+1 not in setperm:
                    error_dialog = QErrorMessage(self.main)
                    error_dialog.showMessage('Not a permutation!')
                    return
        else:
            if setperm[0] < 1:
                return
            sizey = setperm[0]
            setperm = [i+1 for i in range(sizey)]
        self.main.BPD = BPDclass.RothaBPD(setperm)
        self.main.Dream(self.main.BPD)
        
class ScaleBox(QDialog):
    def __init__(self, widget):
        super(ScaleBox, self).__init__(widget)
        self.main = widget
        self.setWindowTitle("Change Scale")
        
        self.permbox = QLineEdit(self)
        self.permbox.resize(250,40)
        self.permbox.move(50, 50)
        self.permbox.setFont(QFont('Arial', 10))
        
        self.permbox.editingFinished.connect(self.enterPress)
        self.pressed = False
        
        self.show()
    
    def enterPress(self):
        factor = self.permbox.text()
        if float(factor) > 0 and self.pressed == False:
            global scale
            scale = float(scale)*float(factor)
            scale = int(scale)
            self.pressed = True
        else:
            return
        
        self.main.n = 0
        self.main.Dream(self.main.BPD)
        self.close()

class Window(QMainWindow):
    def __init__(self,n=default_size,BPD=[]):
        super().__init__()
        self.acceptDrops()
        # set the title
        self.setWindowTitle("Bumpless Pipe Dream - Elbow Mode")
        self.mode = 0
        self.n = n
        self.color = [colors.index(default_color) for i in range(n)]
        self.co = False
 
        # setting  the geometry of window
        if BPD == []:
            self.perm = []
            for i in range(self.n):
                self.perm.append(i+1)
            self.BPD = BPDclass.RothaBPD(self.perm)
        else:
            self.perm = BPD.perm
            self.BPD = BPD
        self.setGeometry(QRect(0, 0, scale*(self.n)+150, scale*(self.n)+150))
        #self.setStyleSheet("background-color: white;")
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(Qt.white))
        self.setPalette(palette)
        
        self.setupUI(self)
        
        
        # show all the widgets
        self.show()
    
    def Dream(self, BPD):
        BPD = BPDclass.BPD(BPD.size,BPD.elbows,co=self.co)
        if BPD.size != self.n:
            self.close()
            self.__init__(BPD.size, BPD)
            return
        for i in range(self.n):
            self.labels[i][self.n].setText(str(BPD.perm[i]))
        
        # Loads images
        self.pixmaps = []
        for i in range(self.n):
            self.pixmaps.append([])
            for j in range(self.n):
                self.pixmaps[i].append(QPixmap(scale, scale))
                self.pixmaps[i][j].fill(Qt.transparent)
                painter = QPainter(self.pixmaps[i][j])
                painter.drawPixmap(0,0,scale,scale,QPixmap('images/empty.png'))
                if [j+1,i+1] in BPD.elbows:
                    painter.drawPixmap(0,0,scale,scale,QPixmap('images/elbow.png'))
                painter.end()
                self.labels[i][j].setPixmap(self.pixmaps[i][j])
                
        
        global highlight
        if highlight:
            for loc in BPDclass.getBadCoLocations(self.BPD):
                painter = QPainter(self.pixmaps[loc[1]-1][loc[0]-1])
                painter.drawPixmap(0,0,scale,scale,QPixmap('images/highlight.png'))
                painter.end()
        
        pnum = 0
        for pipe in BPD.pipes:
            direction = 1
            for place in pipe:
                painter = QPainter(self.pixmaps[place[1]-1][place[0]-1])
                if place in BPD.elbows:
                    if direction == 1:
                        if pipe not in BPD.badpipes:
                            if not self.co:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/se'+colors[self.color[pnum]]+'.png'))
                            else:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/ne'+colors[self.color[pnum]]+'.png'))
                        else:
                            if not self.co:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/seBAD.png'))
                            else:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/neBAD.png'))
                    else:
                        if pipe not in BPD.badpipes:
                            if not self.co:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/nw'+colors[self.color[pnum]]+'.png'))
                            else:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/sw'+colors[self.color[pnum]]+'.png'))
                        else:
                            if not self.co:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/nwBAD.png'))
                            else:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/swBAD.png'))
                    direction = -1*direction
                    
                else:
                    if direction == 1:
                        if pipe not in BPD.badpipes:
                            if place not in BPD.bumps:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/vert'+colors[self.color[pnum]]+'.png'))
                            else:
                                if not self.co:
                                    painter.drawPixmap(0,0,scale,scale,QPixmap('images/se'+colors[self.color[pnum]]+'.png'))
                                else:
                                    painter.drawPixmap(0,0,scale,scale,QPixmap('images/ne'+colors[self.color[pnum]]+'.png'))
                                direction = -1*direction
                        else:
                            if place not in BPD.bumps:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/vertBAD.png'))
                            else:
                                if not self.co:
                                    painter.drawPixmap(0,0,scale,scale,QPixmap('images/seBAD.png'))
                                else:
                                    painter.drawPixmap(0,0,scale,scale,QPixmap('images/neBAD.png'))
                                direction = -1*direction
                    else:
                        if pipe not in BPD.badpipes:
                            if place not in BPD.bumps:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/hort'+colors[self.color[pnum]]+'.png'))
                            else:
                                if not self.co:
                                    painter.drawPixmap(0,0,scale,scale,QPixmap('images/nw'+colors[self.color[pnum]]+'.png'))
                                else:
                                    painter.drawPixmap(0,0,scale,scale,QPixmap('images/sw'+colors[self.color[pnum]]+'.png'))
                                direction = -1*direction
                        else:
                            if place not in BPD.bumps:
                                painter.drawPixmap(0,0,scale,scale,QPixmap('images/hortBAD.png'))
                            else:
                                if not self.co:
                                    painter.drawPixmap(0,0,scale,scale,QPixmap('images/nwBAD.png'))
                                else:
                                    painter.drawPixmap(0,0,scale,scale,QPixmap('images/swBAD.png'))
                                direction = -1*direction
                            
                            
                painter.end()
                self.labels[place[1]-1][place[0]-1].setPixmap(self.pixmaps[place[1]-1][place[0]-1])
            pnum += 1
            
    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key_I:
            Insertion(self)
            
        elif event.key() == Qt.Key_Q:
            global badpats
            global goodpats
            badflag = True
            goodflag = True
            while badflag or goodflag:
                badflag = False
                options = [i+1 for i in range(self.BPD.size)]
                testperm = []
                for i in range(self.BPD.size):
                    nextele = random.choice(options)
                    testperm.append(nextele)
                    options.remove(nextele)
                
                for pat in badpats:
                    if BPDclass.permpatterncontainment(testperm, pat):
                        badflag = True
                        break
                
                if not badflag:
                    for pat in goodpats:
                        if BPDclass.permpatterncontainment(testperm, pat, True):
                            goodflag = False
                            break
                    if len(goodpats) == 0:
                        goodflag = False
                        
                        #goodflag = False
                        #if not BPDclass.permpatterncontainment(testperm, pat):
                        #    goodflag = True
                        #    break
                
            self.BPD = BPDclass.RothaBPD(testperm)
            self.Dream(self.BPD)
            
        elif event.key() == Qt.Key_P:
            PermBox(self)
            
        elif event.key() == Qt.Key_S:
            ScaleBox(self)
            
        elif event.key() == Qt.Key_E:
            self.mode = 0
            self.setWindowTitle("Bumpless Pipe Dream - Elbow Mode")
            
        elif event.key() == Qt.Key_D:
            self.mode = 1
            self.setWindowTitle("Bumpless Pipe Dream - Droop Mode")
            
        elif event.key() == Qt.Key_B:
            self.mode = 2
            self.setWindowTitle("Bumpless Pipe Dream - Cross-Bump Swap Mode")
            
        elif event.key() == Qt.Key_Z:
            self.mode = (self.mode+1)%3
            if self.mode == 0:
                self.setWindowTitle("Bumpless Pipe Dream - Elbow Mode")
            elif self.mode == 1:
                self.setWindowTitle("Bumpless Pipe Dream - Droop Mode")
            elif self.mode == 2:
                self.setWindowTitle("Bumpless Pipe Dream - Cross-Bump Swap Mode")
                
        elif event.key() == Qt.Key_C:
            if self.co:
                self.co = False
            else:
                self.co = True
            self.Dream(self.BPD)
                
        elif event.key() == Qt.Key_O:
            for i in range(len(self.color)):
                self.color[i] = (self.color[i]+1)%len(colors)
            self.Dream(self.BPD)
            
        elif event.key() == Qt.Key_R:
            for i in range(len(self.color)):
                randc = random.randint(0,len(colors)-1)
                self.color[i] = randc
            self.Dream(self.BPD)
            
        elif event.key() == Qt.Key_H:
            global highlight
            highlight = not highlight
            self.Dream(self.BPD)
            
        elif event.key() == Qt.Key_F:
            choices = BPDclass.nonreducedCoBPDsofPerm(self.BPD.perm)
            print(len(choices))
            if choices == []:
                return
            else:
                pick = random.choice(choices)
                pick.coBPD()
                self.BPD = pick
                self.Dream(self.BPD)
            
        elif event.key() == Qt.Key_L:
            Lidellenum = random.randint(1,14)
            Lidelletext = 'Lidelle/Lidelle'+str(Lidellenum)+'.png'
            oImage = QImage(Lidelletext)
            sImage = oImage.scaled(QSize(scale*(self.n)+150, scale*(self.n)+150))
            palette = QPalette()
            palette.setBrush(QPalette.Background, QBrush(sImage))                        
            self.setPalette(palette)
            
    def setupUI(self, Interface):
        
        self.centralWidget = QWidget(Interface)
        layout = QGridLayout(self.centralWidget)
        
        self.scrollArea = QScrollArea(self.centralWidget)
        layout.addWidget(self.scrollArea)
        
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, scale*(self.n)+scale, scale*(self.n)+scale))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        layout = QGridLayout(self.scrollAreaWidgetContents)
        
        # creating labels
        self.labels = []
        for i in range(self.n):
            self.labels.append([])
            for j in range(self.n):
                self.labels[i].append(ClickWidget(self, j+1, i+1))
                layout.addWidget(self.labels[i][j], j, i)
        
        self.labels.append([])
        for j in range(self.n):
            self.labels[self.n].append(QLabel(self))
            self.labels[self.n][j].setText(str(j+1))
            self.labels[self.n][j].setAlignment(Qt.AlignCenter)
            self.labels[self.n][j].setFont(QFont('Arial', int(scale/4)))
            layout.addWidget(self.labels[self.n][j], self.n, j)
            
        for i in range(self.n):
            self.labels[i].append(QLabel(self))
            self.labels[i][self.n].setText(str(self.perm[i]))
            self.labels[i][self.n].setAlignment(Qt.AlignCenter)
            self.labels[i][self.n].setFont(QFont('Arial', int(scale/4)))
            layout.addWidget(self.labels[i][self.n], i, self.n)
                    
        self.Dream(self.BPD)
        
        
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        Interface.setCentralWidget(self.centralWidget)
        
    def closeEvent(self, event):
        QApplication.closeAllWindows()
        event.accept()
            
 
# create pyqt5 app
App = QApplication(sys.argv)
 
# create the instance of our Window
window = Window()
 
# start the app
sys.exit(App.exec())