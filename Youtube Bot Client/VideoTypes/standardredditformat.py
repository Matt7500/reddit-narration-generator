from PIL import ImageFont, ImageDraw, Image, ImageQt
import numpy as np
import videosettings
from VideoTypes import videoformat, imageframe
import ast
import textwrap
import statistics

class StandardReddit(videoformat.VideoFormat):

    def __init__(self, savename, dictionary):
        self.scriptsaveidentifier = savename
        self.loadFormat(dictionary)

    def generateImage(self, text):
        background = Image.new('RGBA', (1920, 1080), (100, 100, 100, 255))
        img = Image.new('RGBA', (1920, 1080), (200, 200, 200, 0))
        W, H = img.size
        paragraphs = text.split('\n\n')
        font = ImageFont.truetype(f"{videosettings.assetPath}\Verdana.ttf", 42)
        draw = ImageDraw.Draw(img)
        line_width = []
        (width, height), (offset_x, offset_y) = font.font.getsize('|')
        line_count = 0
        for num, para in enumerate(paragraphs):
            text_lines = textwrap.wrap(para, 90)
            for line in text_lines:
                w, h = draw.textsize(line, font=font)
                line_width.append(W / 2 - w / 2)
                line_count += 45
            line_count += 45 if num + 1 < len(paragraphs) else 0
        overlay = Image.new('RGBA', (1920, line_count + 40), (0, 0, 0, 205))
        new_draw = ImageDraw.Draw(overlay)
        y = 0
        for num, para in enumerate(paragraphs):
            text_lines = textwrap.wrap(para, 90)
            for t in text_lines:
                new_draw.text((min(line_width), y - offset_y + 20), t, font=font, fill='white', stroke_width=2, stroke_fill='black')
                y += 45
            y += 45 if num + 1 < len(paragraphs) else 0
        background.paste(overlay, (0, int((1080 - (line_count + 40)) / 2)), mask=overlay)
        final = background.tobytes('raw', 'RGBA')
        return final

    def stillImage(self, commentThread):
        commentThread = commentThread[0]
        if type(commentThread) == tuple:
            for comment in commentThread:
                background = Image.new('RGBA', (1920, 1080), (100, 100, 100, 255))
                img = Image.new('RGBA', (1920, 1080), (200, 200, 200, 0))
                W, H = img.size
                comment_text = comment.text
                paragraphs = comment_text.split('\n\n')
                font = ImageFont.truetype(f"{videosettings.assetPath}\Verdana.ttf", 42)
                draw = ImageDraw.Draw(img)
                line_width = []
                (width, height), (offset_x, offset_y) = font.font.getsize('|')
                line_count = 0
                for num, para in enumerate(paragraphs):
                    text_lines = textwrap.wrap(para, 90)
                    for line in text_lines:
                        w, h = draw.textsize(line, font=font)
                        line_width.append(W / 2 - w / 2)
                        line_count += 45
                    line_count += 45 if num + 1 < len(paragraphs) else 0
                overlay = Image.new('RGBA', (1920, line_count + 40), (0, 0, 0, 205))
                new_draw = ImageDraw.Draw(overlay)
                y = 0
                for num, para in enumerate(paragraphs):
                    text_lines = textwrap.wrap(para, 90)
                    for t in text_lines:
                        new_draw.text((min(line_width), y - offset_y + 20), t, font=font, fill='white', stroke_width=2, stroke_fill='black')
                        y += 45
                    y += 45 if num + 1 < len(paragraphs) else 0
                background.paste(overlay, (0, int((1080 - (line_count + 40)) / 2)), mask=overlay)
        final = background.tobytes('raw', 'RGBA')
        return final


    #1280 x 720 youtube max
    def renderThumbnail(self, commentThread):
        commentThread = commentThread[0]
        upvotes = commentThread[0].upvotes
        subcomments = commentThread[0].subcomments
        fontpath = ("%s/Verdana.ttf" % (videosettings.assetPath))
        fontpathbold = ("%s/verdanab.ttf" % (videosettings.assetPath))

        font_subreddit = ImageFont.truetype(fontpath, 80)
        font_below_icons = ImageFont.truetype(fontpathbold, 60)

        my_img = np.zeros((720, 1280, 3), dtype="uint8")
        my_img[:, :, :] = self.settings.background_color
        img_pil = Image.fromarray(my_img, mode='RGBA')
        draw = ImageDraw.Draw(img_pil, mode="RGBA")


        xPosLogo, yPosLogo = (30, 30)
        logowidth, logoheight = ((font_subreddit.getsize("test")[1]), (font_subreddit.getsize("test")[1]))
        upvoteiconwidth, upvoteiconheight = ((font_below_icons.getsize("test")[1]), (font_below_icons.getsize("test")[1]))
        icon = Image.open(videosettings.assetPath + "/askredditlogo.png").resize((logowidth, logoheight), Image.NEAREST)
        img_pil.paste(icon, (xPosLogo, yPosLogo), icon)
        xPosCommentIcon, yPosCommentIcon = (30, img_pil.height - logoheight * 2)
        iconbannerOffsetX = 20
        iconbannergap = 90


        icon_upvotes = Image.open(videosettings.assetPath + "/upvotewhitethumbnail.png").resize((upvoteiconwidth, upvoteiconheight), Image.NEAREST)
        icon_comments = Image.open(videosettings.assetPath + "/chatwhite.png").resize((upvoteiconwidth, upvoteiconheight), Image.NEAREST)
        img_pil.paste(icon_upvotes, (xPosCommentIcon, yPosCommentIcon), icon_upvotes)
        img_pil.paste(icon_comments, (iconbannergap + xPosCommentIcon + upvoteiconwidth + font_below_icons.getsize(imageframe.redditPointsFormat(upvotes, False))[0] + iconbannerOffsetX * 2, yPosCommentIcon), icon_comments)

        draw.text((xPosLogo + logowidth, yPosLogo - 5), "r/AskReddit", font=font_subreddit,
                  fill="#FFFFFF")

        draw.text((xPosCommentIcon + upvoteiconwidth + iconbannerOffsetX, yPosCommentIcon), str(imageframe.redditPointsFormat(upvotes, False)), font=font_below_icons,
                  fill="#FFFFFF")

        draw.text((iconbannergap + xPosCommentIcon + (upvoteiconwidth * 2) + font_below_icons.getsize(imageframe.redditPointsFormat(upvotes, False))[0] + iconbannerOffsetX * 3, yPosCommentIcon),
                  str(imageframe.redditPointsFormat(subcomments, False)), font=font_below_icons,
                  fill="#FFFFFF")


        #my_img = deepcopy(np.array(img_pil))
        return my_img



    def calculateFontSize(self, commentThread, fontSize=videosettings.preferred_font_size, thumbnail = False):
        fontSize = fontSize
        fontpath = ("%s/Verdana.ttf" % (videosettings.assetPath))
        #fontpathbold = ("%s/verdanab.ttf" % (settings.assetPath))

        lineWidths = [9999]
        lineHeights = [9999]
        timesLooped = 0
        endLoop = False
        upvoteMarginX = 0
        upvoteGapX = 0
        upvoteGapY = 0

        while True:
            if endLoop:
                break

            font = ImageFont.truetype(fontpath, fontSize - timesLooped)

            font_header = ImageFont.truetype(fontpath, int(fontSize - timesLooped * self.settings.comment_author_factor))


            upvoteGapX = font.getsize("1" * self.settings.upvote_gap_scale_x)[0]
            upvoteGapY = font.getsize("1")[1] * self.settings.upvote_gap_scale_y

            upvoteMarginX = font.getsize("1" * self.settings.upvote_fontsize_scale)[0] + upvoteGapX


            poffsetX = upvoteMarginX
            poffsetY = upvoteGapY
            lineWidths.clear()
            lineHeights.clear()

            if type(commentThread) == tuple:
                for comment in commentThread:
                    author = comment.author
                    upvotes = comment.upvotes
                    script = imageframe.VideoScript(comment.text)
                    if not thumbnail:
                        script.insertLineWrappingTags(self.settings.characters_per_line)
                    else:
                        script.insertLineWrappingTags(30)

                    script.insertAudioBreakTags()
                    instructions = script.getTags()

                    lastText = ""
                    currentline = ""

                    poffsetY += font_header.getsize(author)[1]

                    for instr in instructions:
                        text = ast.literal_eval(repr(instr[0]))
                        tag = instr[1]

                        if tag == "<LW>" or tag == "":
                            lastText += text
                            currentline += text
                            lineWidths.append(poffsetX + font.getsize(currentline)[0])
                            currentline = ""
                            poffsetY += (font.getsize("asd")[1])
                        else:
                            pass

                        if tag == "<BRK>" or tag == "":
                            lastText += text
                            currentline += text

                            lastText = ""
                    tempWidth = font.getsize("1" * self.settings.reply_characters_factorX)[0]
                    tempHeight = font.getsize("random")[1]
                    poffsetX += (tempWidth * self.settings.reply_fontsize_factorX)
                    poffsetY += (tempHeight * self.settings.reply_fontsize_factorY)
                    lineHeights.append(poffsetY)

            # yeah, I know this code below is a bit messy but we need to loop the code one more time with the correct
            # font size in order to get the right values we need for lineWidths and lineHeights for margin calculations

            timesLooped += 1

            if max(lineHeights) < self.settings.imageSize[1] and max(lineWidths) < self.settings.imageSize[0]:

                endLoop = True


        fontSizeReturn = fontSize - timesLooped
        marginOffsetX = (self.settings.imageSize[0] - max(lineWidths)) / 2
        marginOffsetY = (self.settings.imageSize[1] - max(lineHeights)) / 2

        return (fontSizeReturn, marginOffsetX, marginOffsetY, upvoteMarginX, upvoteGapX, upvoteGapY)

