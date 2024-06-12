from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
import os, sys, time
import threading

class Pixmap(QPixmap):
    def scaling(self, w):
        self.ratio = w / self.width()
        new_size = self.size() * self.ratio
        return Pixmap(self.scaled(QSize(new_size.width(), new_size.height()), transformMode = Qt.SmoothTransformation))
    
    def flip(self):
        transform = QTransform()
        transform.scale(-1, 1)
        return Pixmap(self.transformed(transform))

class Sticker(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.opacity = 1

        self.img_num = 0
        self.fliped = False
        self.old_w = self.width()
        try:
            self.img = img_list[0]     
            self.pixmap = Pixmap(self.img)
        except:
            sys.exit("NO IMAGE")

        self.w = self.pixmap.width()
        self.h = self.pixmap.height()
        
        self.updateWin()
        flag=QtCore.Qt.WindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flag)

        self.move(300, 300)
        self.resize(self.pixmap.width(), self.pixmap.height())
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.show()


#------------------------------------------------------------------------#
#------------------------------------------------------------------------#
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.drawPixmap(int((self.width() - self.pixmap.width()) / 2), int((self.height() - self.pixmap.height()) / 2), self.pixmap)
        self.resize(self.pixmap.width(), self.pixmap.height())

    def updateWin(self):
        if ".gif" in (self.img).lower():
            self.movie = QMovie(self.img)
            self.movie.frameChanged.connect(self.animationing)
            self.movie.start() 

        self.update()

    def animationing(self):
        self.pixmap = Pixmap(self.movie.currentPixmap())
        if self.fliped:
            self.pixmap = self.pixmap.flip()
        self.pixmap = self.pixmap.scaling(self.old_w)
        self.update()
#------------------------------------------------------------------------#
#------------------------------------------------------------------------#


    def mousePressEvent(self, e):#--------------------------# 마우스 클릭 이벤트
        if e.buttons() == QtCore.Qt.LeftButton: # 좌클릭 시 -> 드래그 위치 저장
            self.dragPosition = e.globalPos() - self.frameGeometry().topLeft() 
            e.accept()


        elif e.buttons() == QtCore.Qt.MidButton:#--------------------------# 휠 버튼 클릭 시 -> 좌우 반전
            try:
                self.pixmap = self.pixmap.flip()

                self.update()
                if self.fliped:
                    self.fliped = False 
                else: self.fliped = True
                time.sleep(0.2)
                
            except:
                print("카시코미 카시코미 츠츠신데 오카에시모-오스!!")


    def mouseMoveEvent(self, event):#--------------------------# 마우스 이동 이벤트
        if event.buttons() == QtCore.Qt.LeftButton:#--------------------------# 왼쪽 버튼이 눌려있으면
            self.move(event.globalPos() - self.dragPosition)#--------------------------# 드래그 위치만큼 창 이동
            event.accept()


    def wheelEvent(self, e: QWheelEvent): 

        if e.buttons() == QtCore.Qt.RightButton:#--------------------------#우클릭 한 채로 스크롤 시 투명도 조절
            degree = e.angleDelta().y()/1200
            if self.opacity+degree > 0.1 and self.opacity+degree <= 1:#--------------------------#0.1 < self.opacity + degree <= 1
                self.opacity += degree
                self.setWindowOpacity(self.opacity)



        elif e.modifiers() == Qt.ControlModifier:#--------------------------#ctrl + 스크롤 시 사진의 크기 조절
            self.pixmap = Pixmap(self.img)

            if self.fliped:
                self.pixmap = self.pixmap.flip()

            dsize = e.angleDelta().y()/12
            self.w += dsize
            self.h *= self.w/(self.w - dsize)
            self.pixmap = self.pixmap.scaling(self.w)
            self.old_w = self.pixmap.width()


        else:#--------------------------#스크롤 시 사진 바꾸기
            self.fliped = False
            if ".gif" in self.img: 
                self.movie.stop()
                self.movie = None

            self.img_num += int(e.angleDelta().y()/120)                           

            if self.img_num > len(img_list)-1 or  self.img_num < -len(img_list)+1:#--------------------------#-img_list index가 초과하면 0으로 초기화
                    self.img_num = 0     
            
            try:
                self.img = img_list[self.img_num]
                self.old_w = self.pixmap.width()
                self.pixmap = Pixmap(self.img)
                self.pixmap = self.pixmap.scaling(self.old_w)#--------------------------#이전 사진에 맞추어 크기 변경
                if (self.geometry().y() <= -self.pixmap.height()) and self.geometry().y() < 0:#--------------------------#
                    self.move(self.geometry().x(), 0)
                
            except: 
                self.img_num -= 1
                print("No image")

        self.updateWin()
        

    def mouseDoubleClickEvent(self, e): #더블클릭하면 종료
        if e.buttons() == QtCore.Qt.LeftButton: QtWidgets.qApp.quit()

img_list = []

def getImages():
    while True:
        img_list.clear() 
        img_path_list = open("image_path.txt", "r", encoding="Utf-8").readlines()

        #사진 파일 읽어오기
        for img_path in img_path_list:
            try:
                img_path = img_path.strip("\n")
                for file in os.listdir(img_path):          
                    if ".png" in file.lower() or ".jpg" in file.lower() or ".gif" in file.lower():
                        file_path = os.path.join(img_path, file)
                        
                        img_list.append(file_path.replace("\\", "/"))
            except: 
                print(f"error path: {img_path}")
                break
        time.sleep(0.2)

get_images = threading.Thread(target=getImages)
get_images.daemon = True
get_images.start()

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = Sticker()
   sys.exit(app.exec_())
