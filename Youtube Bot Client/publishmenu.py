from PyQt5 import QtWidgets
import configparser
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5 import uic
from VideoTypes import standardredditformat
import videoscriptcore
import keywordgenerator
import client
import scripteditor
import os
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import cv2
from PyQt5.QtGui import *
import sys
import numpy as np
from PIL import Image
import subprocess
from PyQt5 import QtWidgets
import settings


currentPath = os.path.dirname(os.path.realpath(__file__))

def get_platform():
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]

platform = get_platform()

currentPath = os.path.dirname(os.path.realpath(__file__))

if platform == 'linux':
    thumbnailFolder = currentPath + "/Thumbnails"
else:
    thumbnailFolder = currentPath + "\Thumbnails"


# https://unicode.org/emoji/charts/full-emoji-list.html#1f637
def generateDescription(videoscript):
    standard_description = loadTextFile("description.txt").replace("**TITLE**", generateTitle(videoscript.title))


    return standard_description


def loadTextFile(file):
    f = open("%s\\" % settings.currentPath + file, "r", encoding="utf8")
    content = f.read()
    f.close()
    return content

def generateTitle(title):
    return title

def clickable(widget):

    class Filter(QObject):
           clicked = pyqtSignal()
           def eventFilter(self, obj, event):
               if obj == widget:
                   if event.type() == QEvent.MouseButtonRelease:
                       if obj.rect().contains(event.pos()):
                           self.clicked.emit()
                           # The developer can opt for .emit(obj) to get the object within the slot.
                           return True
               return False
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked

currentPublishMenu = None

class PublishMenu(QMainWindow):

    upload_success_true = pyqtSignal()
    upload_success_false = pyqtSignal()

    def __init__(self, videoscript):
        QWidget.__init__(self)
        uic.loadUi("UI/videoeditor.ui", self)
        global currentPublishMenu
        currentPublishMenu = self
        self.videoScript = videoscript
        self.genVid.clicked.connect(self.sendToVideoGenerator)
        self.openeditor.clicked.connect(self.openVideoEditor)
        self.upload_success_true.connect(self.uploadSuccess)
        self.upload_success_false.connect(self.uploadFail)
        self.safeClose = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateDisplay)
        self.timer.start(3000)


    def openVideoEditor(self):
        self.safeClose = True
        self.close()
        self.videoEditor = scripteditor.VideoEditor(self.videoScript)
        self.videoEditor.show()

    def fistTimeUpdateDisplay(self):
        self.setWindowTitle("Publish Video No.%s" % self.videoScript.vidNo)
        self.videoQuestion.setText("Video Question: %s" % self.videoScript.title)
        self.editTitle.setText(generateTitle(self.videoScript.title))
        self.updateDescription(generateDescription(self.videoScript))
        self.commentthreads.setText("Comment Threads: %s"%self.scriptWrapper.getEditedCommentThreadsAmount())
        self.commentamount.setText("Comments: %s"%self.scriptWrapper.getEditedCommentAmount())
        self.totalwords.setText("Total Words: %s"%self.scriptWrapper.getEditedWordCount())
        self.estvidtime.setText("Estimated Video Time: %s"%self.scriptWrapper.getEstimatedVideoTime())
        self.thumbnailareageometry = self.thumbnailarea.frameGeometry()
        self.generateThumbnail()

    def uploadSuccess(self):
        self.safeClose = True
        message = "Video Upload Successful! \n The script is now in the video generator queue"
        self.createPopup("Information", QMessageBox.Information, "Upload Success!", message)
        if self.retMsg == QMessageBox.Ok:
            self.close()

    def uploadFail(self):
        message = "Upload Failed. \n Please try a different script or consult the admin."
        self.createPopup("Information", QMessageBox.Information, "Upload Failed", message)
        if self.retMsg == QMessageBox.Ok:
            return

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Enter:
            self.generateGoogleTags()

    def sendToVideoGenerator(self):
            message = "Are you sure you're ready to export?"
            self.createPopup("Confirm", QMessageBox.Warning, "Ready to Upload?", message)
            if self.retMsg == QMessageBox.Ok:
                #self.videoScript.sendToServer()
                self.videoScript.exportOffline()

    def createPopup(self, messagetype, icon, text, message):
        self.msg = QMessageBox()
        self.msg.setIcon(icon)
        self.msg.setText(text)
        self.msg.setInformativeText(message)
        self.msg.setWindowTitle(messagetype)
        if messagetype == "Error":
            self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        if messagetype == "Warning":
            self.msg.setStandardButtons(QMessageBox.Ignore | QMessageBox.Cancel)
        if messagetype == "Confirm":
            self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        if messagetype == "Information":
            self.msg.setStandardButtons(QMessageBox.Ok)
        else:
            self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        self.retMsg = self.msg.exec_()

    def closeEvent(self, event):
        if not self.safeClose:
            client.quitEditing(self.videoScript.scriptno)
            scripteditor.scriptsMenu.isEditing = False


    def updateDisplay(self):
        self.charCount.setText("Current Characters: %s" % len(self.tags.toPlainText()))
        self.charCounttitle.setText("Current Characters: %s" % len(self.editTitle.text()))
        self.title_final.setText(self.editTitle.text())
        self.descriptionDisplay.setText(self.descriptionEdit.toPlainText())
        if len(self.tags.toPlainText()) > 450 or len(self.editTitle.text()) > 100:
            self.genVid.setEnabled(False)
            self.videoStatus.setText("Too many characters in tags or title!")
        else:
            self.genVid.setEnabled(True)
            self.videoStatus.setText("Good to upload!")

    def mouseMoveEvent(self, event):
        self.updateDisplay()

    def mousePressEvent(self, event):
        self.updateDisplay()

