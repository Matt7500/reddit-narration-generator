import datetime
import settings
import os
import pickle
import client
import settings
import generateVideo

video_scripts = []
currentPath = os.path.dirname(os.path.realpath(__file__))

class VideoScript():
    def __init__(self, vidno, scriptno, submission_id, category, title, author, upvotes, comments, videotype, commentInformation, selftext, music_type, status, commentsamount, editedby=None):
        self.sub_reddit = category
        self.title = title
        self.youtube_title = None
        self.youtube_description = None
        self.youtube_tags = None
        self.submission_id = submission_id
        self.videoType = videotype
        self.upvotes = upvotes
        self.author = author
        self.commentInformation = commentInformation
        self.selftext = selftext
        self.loadDefaultVideoSettings()
        self.music_type = music_type
        self.final_script = None
        self.parsedCommentInformation = []
        self.comments = comments
        self.beingEdited = False
        self.vidNo = vidno
        self.scriptno = scriptno
        vidsaves = os.listdir(settings.scriptsaves)
        self.scriptWrapper = ScriptWrapper(self.commentInformation, self.title, self.scriptno, self.selftext)

        self.thumbnail = None
        self.charactersAmount = None
        self.amount_comments = commentsamount
        self.status = status
        self.editedby = editedby
        video_scripts.append(self)

    def loadDefaultVideoSettings(self):
        self.videosettings = loadDefaultVideoSettings(self.videoType)

    def exportOffline(self):
        export_path = currentPath + "/Export/video%s.vid" % self.vidNo
        with open(export_path, 'wb') as pickle_file:
            pickle.dump((self.title, self.videoType, self.upvotes, self.author, self.videosettings, self.music_type, self.final_script), pickle_file)
        client.flagscript(self.scriptno, "MANUALCOMPLETE")

    def sendToServer(self):
        self.charactersAmount = self.scriptWrapper.getEditedCharacterCount()
        client.formatVideoScript(self)



def loadDefaultVideoSettings(videoformattype):
    if videoformattype == "standardredditformat":
        return    {"imageSize": [1920, 1080],
                  "hasBoundingBox" : True,
                   "hasUpvoteButton": False,
                   "bounding_box_colour": [10, 10, 10],
                  "background_color": [50, 50, 50],
                  "comment_text_color": [215, 218, 220],
                  "author_text_color": [10, 10, 10],
                  "author_details_color": [74, 175, 238],
                  "characters_per_line": 125,
                  "punctuationList": [",", ".", "!", "?"],
                   "upvote_gap_scale_x": 1,
                   "upvote_gap_scale_y": 0.2,
                   "upvote_fontsize_scale": 2,
                  "reply_characters_factorX": 3,
                  "reply_fontsize_factorX": 0.625,
                  "reply_fontsize_factorY": 1.15384,
                  "comment_author_factor": 0.9,
                  "preferred_font_size": 33}



class CommentWrapper():
    def __init__(self, author, text, upvotes, subcomments = None):
        self.author = author
        self.text = text
        self.upvotes = upvotes
        self.subcomments = subcomments


class ScriptWrapper():
    def __init__(self, script, title, scriptno, post_text):
        self.title = title
        self.rawScript = script
        self.scriptno = scriptno
        self.post_text = post_text
        self.paragraphCount = 0
        self.postMap = []
        self.scriptMap = []
        self.setupScriptMap()

    def setupScriptMap(self):
        for paragraph in self.post_text:
            line = ()
            line = line + (False,)
            self.postMap.append(line)
        for mainComment in self.rawScript:
            line = ()
            for subComment in mainComment:
                line = line + (False,)
            self.scriptMap.append(line)
        self.paragraphCount = len(self.postMap)

    def keep(self, parentIndex, childIndex):
        if parentIndex < self.paragraphCount:
            newThread = ()
            newThread = newThread + (True,)
            self.postMap[parentIndex] = newThread
        else:
            commentThread = self.scriptMap[parentIndex - self.paragraphCount]
            newThread = ()
            for i, comment in enumerate(commentThread):
                if not i == childIndex:
                    newThread = newThread + (comment,)
                else:
                    newThread = newThread + (True,)
            self.scriptMap[parentIndex - self.paragraphCount] = newThread

    def skip(self, parentIndex, childIndex):
        if parentIndex < self.paragraphCount:
            newThread = ()
            newThread = newThread + (False,)
            self.postMap[parentIndex] = newThread
        else:
            commentThread = self.scriptMap[parentIndex - self.paragraphCount]
            newThread = ()
            for i, comment in enumerate(commentThread):
                if not i == childIndex:
                    newThread = newThread + (comment,)
                else:
                    newThread = newThread + (False,)
            self.scriptMap[parentIndex - self.paragraphCount] = newThread

    def moveDown(self, i):
        if i > 0:
            copy1 = self.scriptMap[i-1]
            copy2 = self.rawScript[i-1]

            self.scriptMap[i-1] = self.scriptMap[i]
            self.rawScript[i-1] = self.rawScript[i]

            self.scriptMap[i] = copy1
            self.rawScript[i] = copy2
        else:
            print("already at bottom!")

    def moveUp(self, i):
        if i < len(self.scriptMap) - 1:
            copy1 = self.scriptMap[i+1]
            copy2 = self.rawScript[i+1]

            self.scriptMap[i+1] = self.scriptMap[i]
            self.rawScript[i+1] = self.rawScript[i]

            self.scriptMap[i] = copy1
            self.rawScript[i] = copy2
        else:
            print("already at top!")

    def setCommentData(self, x, y, text):
        self.rawScript[x][y].text = text

    def getCommentData(self, x, y):
        try:
            return self.rawScript[x][y]
        except IndexError:
            pass

    def changeCommentText(self, x, y, text):
        self.rawScript[x][y].text = text

    def changeParagraphText(self, x, text):
        self.post_text[x] = text

    def changePostTitle(self, text):
        self.title = text

    def getData(self, x):
        try:
            return self.post_text[x]
        except IndexError:
            pass

    def getCommentAmount(self):
        return len(self.scriptMap)

    def getCommentThreadsAmount(self):
        return len(self.scriptMap)

    def getEditedCommentThreadsAmount(self):
        return len([commentThread for commentThread in self.scriptMap if commentThread[0] is True])

    def getEditedCommentAmount(self):
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        count = 0
        for commentThread in commentThreads:
            for comment in commentThread:
                if comment is True:
                    count += 1
        return count

    def getEditedWordCount(self):
        word_count = 0
        posttext = ([commentThread for commentThread in self.postMap])
        for x, commentThread in enumerate(posttext):
            for y, comment in enumerate(commentThread):
                if comment is True:
                    word_count += len(self.post_text[x].split(" "))
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        for x, commentThread in enumerate(commentThreads):
            for y, comment in enumerate(commentThread):
                if comment is True:
                    word_count += len(self.rawScript[x][y].text.split(" "))
        return word_count

    def getEditedCharacterCount(self):
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        word_count = 0
        for x, commentThread in enumerate(commentThreads):
            for y, comment in enumerate(commentThread):
                if comment is True:
                    word_count += len(self.rawScript[x][y].text)
        return word_count

    def getEstimatedVideoTime(self):
        """
        estimation:
        -animation time between different commentthreads
        -total words
        """
        time = datetime.timedelta()
        word_count = self.getEditedWordCount()
        word_count += len(self.title.replace(" ", ""))
        if not word_count == 0:
            mins = word_count / settings.wordsPerMinute
            time += datetime.timedelta(minutes=mins)
        return time

    def getCommentInformation(self, x, y):
        comments = []
        commentThread = []
        for i, commentWrapper in enumerate(self.rawScript[x]):
            if i < y + 1:
                commentThread.append(commentWrapper)
        comments.append(tuple(commentThread))
        return comments

    def isRecommendedLength(self):
        if self.getEstimatedVideoTime() < settings.recommendedLength:
            return False
        return True

    def saveScriptWrapper(self):
        path_name = settings.scriptsaves + "/rawvideo%s.save" % self.scriptno
        with open(path_name, 'wb') as pickle_file:
            pickle.dump(self, pickle_file)

    def convertToFormat(self):
        save_file = f'{generateVideo.rawvideosaves}/rawvid{self.scriptno}.save'
        final_script = []
        final_script.append(self.title)
        for x, selftext in enumerate(self.post_text):
            if self.postMap[x][0] is True:
                final_script.append(self.post_text[x])
        for x, commentThread in enumerate(self.rawScript):
            for y, comment in enumerate(commentThread):
                if self.scriptMap[x][y] is True:
                    final_script.append(comment.text)
        pickle.dump(final_script, open(save_file, 'wb'))
        #return final_script


def getCategories():
    return [value.sub_reddit for value in video_scripts]

def getScripts():
    return [value.vidNo for value in video_scripts]

def updateScriptStatus(scriptno, status, editedby):
    if scriptno is not None:
        try:
            scriptnos = [script.scriptno for script in video_scripts]
            index = (scriptnos.index(scriptno))
            video_scripts[index].status = status
            video_scripts[index].editedby = editedby
            if editedby is None:
                video_scripts[index].editedby = None

        except IndexError:
            print("couldn't find script %s" % scriptno)