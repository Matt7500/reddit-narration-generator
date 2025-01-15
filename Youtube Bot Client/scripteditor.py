from PyQt5 import QtWidgets
import configparser
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import settings
import pickle
import publishmenu
import videosettings
import textwrap
import videoscriptcore
import client
import cv2
import ast
from VideoTypes import standardredditformat
import traceback, sys
from PyQt5.QtGui import QPalette, QColor
import rawscriptsmenu
import generateVideo
from PIL import ImageFont, ImageDraw, Image
from PIL.ImageQt import ImageQt

scriptsMenu = None

class VideoEditor(QMainWindow):
    def __init__(self, videoscript, scriptmenu = None):
        QWidget.__init__(self)
        global scriptsMenu
        if scriptsMenu is None:
            scriptsMenu = scriptmenu
            self.scriptmenu = scriptsMenu
        else:
            self.scriptmenu = scriptsMenu
        self.rawscriptsmenu = rawscriptsmenu.ScriptsMenu('user')
        self.videoScript = videoscript
        uic.loadUi("UI/scripteditor.ui", self)
        self.progressBar.setValue(0)
        self.setWindowTitle("Video no. %s" % videoscript.vidNo)
        #self.treeWidget.currentItemChanged.connect(self.changeSelected)
        #self.addToTree()
        self.addTreeInformation()
        self.parentIndex = 0
        self.childIndex = -1
        self.paragraphCount = len(self.videoScript.selftext)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(93, 93, 93, 0))
        palette.setColor(QPalette.HighlightedText, QColor("cyan"))
        self.treeWidget.setPalette(palette)
        self.maxMainComments = len(self.videoScript.commentInformation)
        self.scriptWrapper = self.videoScript.scriptWrapper
        #self.returnSelected()
        self.keep.clicked.connect(self.keepButton)
        self.skip.clicked.connect(self.skipButton)
        self.treeWidget.clicked.connect(self.changeSelection)
        self.publish.clicked.connect(self.publishVideo)
        self.editrendervalues.triggered.connect(self.openValueEditor)
        self.nightmode.triggered.connect(self.toggleNightMode)
        self.safeClose = False
        self.nightMode = True
        self.setConstants()
        self.updateText.clicked.connect(self.editTextView)
        self.updateTitle.clicked.connect(self.editPostTitle)
        self.insertSplit.clicked.connect(self.insertSplitButton)
        self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(0))
        self.scriptno = self.scriptWrapper.scriptno
        self.updateDisplay()
        self.updateColors()

    def changeSelection(self):
        self.getCurrentIndexes()
        self.treeWidget.setCurrentItem(self.treeWidget.currentItem())
        self.updateDisplay()

    def updateColors(self):
        for x, mainComment in enumerate(self.scriptWrapper.postMap):
            self.selectedParagraph = None
            for y, subComments in enumerate(mainComment):
                if y == 0:
                    self.selectedParagraph = self.treeWidget.topLevelItem(x)
                    if subComments is True:
                        self.selectedParagraph.setForeground(0, QtGui.QBrush(QtGui.QColor(57, 255, 20)))
        for x, mainComment in enumerate(self.scriptWrapper.scriptMap):
            self.selectedMainComment = None
            for y, subComments in enumerate(mainComment):
                if y == 0:
                    self.selectedMainComment = self.treeWidget.topLevelItem(self.paragraphCount + x)
                    if subComments is True:
                        self.selectedMainComment.setForeground(0, QtGui.QBrush(QtGui.QColor(57, 255, 20)))
                else:
                    if subComments is True:
                        self.selectedMainComment.child(y - 1).setForeground(0, QtGui.QBrush(QtGui.QColor(57, 255, 20)))

    def getCurrentIndexes(self):
        self.currentItem = self.treeWidget.currentItem()
        if self.currentItem is not None:
            if self.currentItem.parent() is None:
                self.parentIndex = self.treeWidget.indexOfTopLevelItem(self.currentItem)
                self.childIndex = -1
            else:
                self.parentIndex = self.treeWidget.indexOfTopLevelItem(self.currentItem.parent())
                self.childIndex = self.currentItem.parent().indexOfChild(self.currentItem)
        self.currentItem = self.treeWidget.currentItem()

    def openValueEditor(self):
        self.valueEditor = ValueEditor(self.videoScript)
        self.valueEditor.onFinish.connect(self.updateValues)
        self.valueEditor.show()


    def updateValues(self):
        self.videoScript.videosettings = self.valueEditor.videoScript.videosettings
        self.updateDisplay()

    def setConstants(self):
        self.avgwordsmin.setText("Avg Words/Min: %s"%settings.wordsPerMinute)
        self.timebetweencommentthread.setText("Time Between Comment Thread: %s"%settings.timeBetweenCommentThread)
        self.subreddit.setText("r/%s"%self.videoScript.sub_reddit)

    def updateDisplay(self, keep=None):
        newIndex = 0
        self.scriptWrapper.saveScriptWrapper()
        if self.childIndex == -1:
            newIndex = 0
        else:
            newIndex = self.childIndex + 1
        try:
            comment_wrapper = self.scriptWrapper.getCommentData(self.parentIndex - self.paragraphCount, newIndex)
            comment_text = comment_wrapper.text
            comment_author = comment_wrapper.author
            comment_upvotes = comment_wrapper.upvotes
        except AttributeError:
            comment_text = 'None'
            comment_author = 'None'
            comment_upvotes = 'None'

        text = self.scriptWrapper.getData(self.parentIndex)
        self.updateTextView(text if self.parentIndex < self.paragraphCount else comment_text)
        self.updateTitleLineEdit()
        #self.textView.setText("Text View: %s"%(self.getCurrentWidget(self.parentIndex, self.childIndex).text(0)))
        self.videoTitle.setText(self.scriptWrapper.title)
        self.author.setText("Author: %s"%comment_author)
        self.upvotes.setText("Upvotes: %s"%comment_upvotes)
        self.wordscomment.setText("Words: %s"%len(comment_text.split(" ")))
        self.characterscomment.setText("Characters: %s"%len(comment_text))
        self.commentthreads.setText("Comment Threads: %s"%self.scriptWrapper.getEditedCommentThreadsAmount())
        self.commentamount.setText("Comments: %s"%self.scriptWrapper.getEditedCommentAmount())
        self.totalwords.setText("Total Words: %s"%self.scriptWrapper.getEditedWordCount())
        self.estvidtime.setText("Estimated Video Time: %s"%self.scriptWrapper.getEstimatedVideoTime())
        self.totalcharacters.setText("Total Characters: %s"%self.scriptWrapper.getEditedCharacterCount())
        self.progressBar.setValue((self.scriptWrapper.getEstimatedVideoTime() / settings.recommendedLength) * 100)

        animation_group_on_change = [self.commentamount, self.commentthreads, self.totalwords, self.estvidtime, self.totalaudiolines]
        if keep is True:
            self.animategroup(animation_group_on_change, QtGui.QColor(0, 128, 0))
        elif keep is False:
            self.animategroup(animation_group_on_change, QtGui.QColor(255, 0, 0))
        try:
            if self.childIndex == -1:
                self.newIndex = 0
            else:
                self.newIndex = self.childIndex + 1
            if self.parentIndex < self.paragraphCount:
                image = standardredditformat.StandardReddit("standardredditformat", self.videoScript.videosettings).generateImage(text)
            else:
                image = standardredditformat.StandardReddit("standardredditformat", self.videoScript.videosettings).stillImage(self.scriptWrapper.getCommentInformation(self.parentIndex - self.paragraphCount, self.newIndex))
            qImg = QImage(image, 1920, 1080, QImage.Format_RGBA8888).scaled(self.imageArea.frameGeometry().width(), self.imageArea.frameGeometry().height(), QtCore.Qt.KeepAspectRatio)
            self.imageArea.setPixmap(QPixmap(qImg))
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            self.imageArea.setText("Rendering Error for Post, skipping")
            print("Need to log this comment")
            self.skipButton()

    def skipButton(self):
        # checking if the current item is a child or a parent
        if self.treeWidget.currentItem().parent() is None:
            self.treeWidget.currentItem().setForeground(0, QtGui.QBrush(QtGui.QColor("red")))
            #if the current item has children turn them all red
            if self.treeWidget.currentItem().childCount() > 0:
                for x in range(0, self.treeWidget.topLevelItem(self.parentIndex).childCount()):
                    self.treeWidget.currentItem().child(x).setForeground(0, QtGui.QBrush(QtGui.QColor("red")))
        #if the current item is a child then turn the rest of the children red too
        if self.treeWidget.currentItem() == self.treeWidget.topLevelItem(self.parentIndex).child(self.childIndex):
            for x in range(self.childIndex, self.treeWidget.topLevelItem(self.parentIndex).childCount()):
                self.treeWidget.topLevelItem(self.parentIndex).child(x).setForeground(0, QtGui.QBrush(QtGui.QColor("red")))
        for i in range(self.childIndex + 1, self.scriptWrapper.getCommentAmount(), 1):
            self.scriptWrapper.skip(self.parentIndex, i)
        self.incrementSelection(keep=False)
        self.updateDisplay(False)

    def keepButton(self):
        for i in range(self.childIndex + 1, -1, -1):
            self.scriptWrapper.keep(self.parentIndex, i)
            #checking if the current item is a child or a parent
            if self.treeWidget.currentItem().parent() is None:
                self.treeWidget.currentItem().setForeground(0, QtGui.QBrush(QtGui.QColor(57, 255, 20)))
            else:
                #if it's a child then turn the parent and the children above green
                self.treeWidget.topLevelItem(self.parentIndex).setForeground(0, QtGui.QBrush(QtGui.QColor(57, 255, 20)))
                for x in range(0, self.childIndex + 1):
                    self.treeWidget.topLevelItem(self.parentIndex).child(x).setForeground(0, QtGui.QBrush(QtGui.QColor(57, 255, 20)))
        self.incrementSelection(keep=True)
        self.updateDisplay(True)

    def incrementSelection(self, keep=None):
        if keep is True:
            #print(f'{self.parentIndex}, {self.childIndex}')
            #if parent child count is greater than 0 and less than the number of children increase childIndex by 1
            if self.treeWidget.topLevelItem(self.parentIndex).childCount() > 0 and self.childIndex < self.treeWidget.topLevelItem(self.parentIndex).childCount() - 1:
                self.childIndex += 1
                self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(self.parentIndex).child(self.childIndex))

            #if parentIndex is equal to the total number of items go back to the top
            elif self.parentIndex == self.treeWidget.topLevelItemCount() - 1:
                self.parentIndex = 0
                self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(self.parentIndex))
            else:
                #if there are no children increase parentIndex by 1 and childIndex is 0
                self.parentIndex += 1
                self.childIndex = -1
                self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(self.parentIndex))
        elif keep is False:
            #if parentIndex is equal to the total number of items go back to the top
            if self.parentIndex == self.treeWidget.topLevelItemCount() - 1:
                self.parentIndex = 0
                self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(self.parentIndex))
            else:
                #if keep is false then just increment the parentIndex by 1
                self.parentIndex += 1
                self.childIndex = -1
                self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(self.parentIndex))
        self.currentItem = self.treeWidget.currentItem()

    def insertSplitButton(self):
        #cursor = QTextCursor(self.textDisplay.document())
        self.textDisplay.insertPlainText('-split-')

    def updateTextView(self, text):
        self.textDisplay.clear()
        self.textDisplay.append(text)

    def editTextView(self):
        newtext = self.textDisplay.toPlainText()
        newIndex = 0
        if self.childIndex == -1:
            newIndex = 0
        else:
            newIndex = self.childIndex + 1
        if self.parentIndex < self.paragraphCount:
            self.scriptWrapper.changeParagraphText(self.parentIndex, newtext)
        else:
            self.scriptWrapper.changeCommentText(self.parentIndex - self.paragraphCount, newIndex, newtext)
        self.updateDisplay()

    def updateTitleLineEdit(self):
        self.editTitle.clear()
        self.editTitle.setText(self.scriptWrapper.title)

    def editPostTitle(self):
        new_title = self.editTitle.text()
        self.scriptWrapper.changePostTitle(new_title)
        print(self.scriptWrapper.title)
        self.updateDisplay()

    def addTreeInformation(self):
        self.treeWidget.clear()
        for i, commentTree in enumerate(self.videoScript.selftext):
            treeParentName = "Paragraph %s" % str(i)
            self.addTopLevel(treeParentName)
            self.selectedMainParagraph = self.getTopLevelByName(treeParentName)
        for i, commentTree in enumerate(self.videoScript.commentInformation):
            treeParentName = "Main Comment %s"%str(i)
            self.addTopLevel(treeParentName)
            if i == 0:
                self.selectedMainComment = self.getTopLevelByName(treeParentName)
            for i, comment in enumerate(commentTree):
                if not i == 0:
                    self.addChild(treeParentName, "Top Comment %s"%str(i))
        self.treeWidget.expandToDepth(0)


    def getAllTopLevel(self):
        items = []
        for index in range(self.treeWidget.topLevelItemCount()):
            items.append(self.treeWidget.topLevelItem(index))
        return items

    def addTopLevel(self, name):
        if self.getTopLevelByName(name) is None:
            QTreeWidgetItem(self.treeWidget, [name])

    def addChild(self, parent, child):
        self.addTopLevel(parent)
        QTreeWidgetItem(self.getTopLevelByName(parent), [child])

    def getTopLevelByName(self, name):
        for index in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(index)
            if item.text(0) == name:
                return item
        return None

    def animategroup(self, widgets, color):
        self.changeanimationgroup = QParallelAnimationGroup()
        for widget in widgets:
            effect = QtWidgets.QGraphicsColorizeEffect(widget)
            widget.setGraphicsEffect(effect)
            anim = QtCore.QPropertyAnimation(effect, b"color")
            anim.setDuration(500)
            anim.setStartValue(QtGui.QColor(0, 0, 0))
            anim.setKeyValueAt(0.25, color)
            anim.setEndValue(QtGui.QColor(0, 0, 0))
            self.changeanimationgroup.addAnimation(anim)
        self.changeanimationgroup.start()


    def publishVideo(self):
        self.checkVideo()


    def checkVideo(self):
        self.scriptWrapper.title = self.videoTitle.text()
        if not self.scriptWrapper.isRecommendedLength():
            message = "Time: %s < %s" % (self.scriptWrapper.getEstimatedVideoTime(), settings.recommendedLength)
            self.createPopup("Warning", QMessageBox.Information, "Estimated Video Time Under 10 Minutes", message)
            if self.retMsg == QMessageBox.Ignore:
                self.scriptWrapper.convertToFormat()
                client.flagscript(self.scriptno, "COMPLETE")
                videoscriptcore.updateScriptStatus(self.scriptno, "COMPLETE", "user")
                self.rawscriptsmenu.update_table.emit()
                self.safeClose = True
                self.close()
            else:
                pass
        else:
            self.sendToVideoGenerator()
            self.safeClose = True
            self.close()

    def sendToVideoGenerator(self):
            message = "Are you sure you're ready to export?"
            self.createPopup("Confirm", QMessageBox.Warning, "Ready to Upload?", message)
            if self.retMsg == QMessageBox.Ok:
                self.scriptWrapper.convertToFormat()
                client.flagscript(self.scriptno, "COMPLETE")
                videoscriptcore.updateScriptStatus(self.scriptno, "COMPLETE", "user")
                self.rawscriptsmenu.update_table.emit()

    def createPopup(self, messagetype, icon, text, message):
        self.msg = QMessageBox()
        self.msg.setIcon(icon)
        self.msg.setText(text)
        self.msg.setInformativeText(message)
        self.msg.setWindowTitle(messagetype)
        if messagetype == "Warning":
            self.msg.setStandardButtons(QMessageBox.Ignore | QMessageBox.Cancel)
        else:
            self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)

        self.retMsg = self.msg.exec_()

    def toggleNightMode(self):
        self.nightMode = not self.nightMode
        if self.nightMode:
            self.videoScript.videosettings['comment_text_color'] = [215, 218, 220]
            self.videoScript.videosettings['background_color'] = [25, 25, 25]
            self.videoScript.videosettings['author_details_color'] = [74, 175, 238]
        else:
            self.videoScript.videosettings['comment_text_color'] = [0, 0, 0]
            self.videoScript.videosettings['background_color'] = [255, 255, 255]
            self.videoScript.videosettings['author_details_color'] = [25, 25, 25]

        self.updateDisplay()

    def closeEvent(self, event):
        if not self.safeClose:
            client.quitEditing(self.videoScript.scriptno)
            scriptsMenu.isEditing = False




class ValueEditor(QMainWindow):
    onFinish = pyqtSignal()
    def __init__(self, videoscript):
        QWidget.__init__(self)
        uic.loadUi("UI/videotypeeditor.ui", self)
        self.videoScript = videoscript
        self.setWindowTitle("Video Settings")
        self.oldSettings = self.videoScript.videosettings
        nice_layout = ("\n\n".join("{}: {}".format("'%s'"%k, v) for k, v in videoscript.videosettings.items()))

        self.resetDefault.clicked.connect(self.setDefaultSettings)
        self.textEdit.setText(str(nice_layout))
        self.cancel.clicked.connect(self.cancelUpdate)
        self.ok.clicked.connect(self.completeChange)
        self.update.clicked.connect(self.setValues)

    def setDefaultSettings(self):
        self.videoScript.loadDefaultVideoSettings()
        self.onFinish.emit()
        nice_layout = ("\n\n".join("{}: {}".format("'%s'"%k, v) for k, v in self.videoScript.videosettings.items()))
        self.textEdit.setText(str(nice_layout))

    def cancelUpdate(self):
        self.videoScript.videosettings = self.oldSettings
        self.onFinish.emit()
        self.close()

    def completeChange(self):
        self.setValues()
        self.close()

    def setValues(self):
        try:
            text = self.textEdit.toPlainText()
            #for line in text.split("\n", ""):
            line_by_line = text.split("\n\n")
            dict_string = "{"
            for i, line in enumerate(line_by_line):
                split = line.split(": ")
                keyword = split[0]
                value = split[1]
                value_evaluated = ast.literal_eval(value)
                if i == len(line_by_line) - 1:
                    dict_string += "%s : %s}" % (keyword, value_evaluated)
                else:
                    dict_string += "%s : %s, " % (keyword, value_evaluated)
            new_settings = (ast.literal_eval(dict_string))
        except Exception as e:
            base_text = "Formatting of the inputs is broken!. \n"

            self.createPopup("Error", QMessageBox.Critical, "Couldn't convert to settings dict.", "%s%s"%(base_text, e))
            return
        self.videoScript.videosettings = new_settings
        self.onFinish.emit()


    def createPopup(self, messagetype, icon, text, message):
        self.msg = QMessageBox()
        self.msg.setIcon(icon)
        self.msg.setText(text)
        self.msg.setInformativeText(message)
        self.msg.setWindowTitle(messagetype)
        if messagetype == "Error":
            self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        self.retMsg = self.msg.exec_()