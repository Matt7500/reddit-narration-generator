from PIL import ImageFont, ImageDraw, Image
import numpy as np
import os
import videosettings
from string import ascii_letters
import textwrap
from moviepy.editor import *
import moviepy.editor as mp
import statistics

path = os.path.dirname(os.path.realpath(__file__))
parentPath = os.path.abspath(os.path.join(path, os.pardir))

class DocumentWrapper(textwrap.TextWrapper):

    def wrap(self, text):
        split_text = text.split('\n\n')
        lines = [line for para in split_text for line in textwrap.TextWrapper.wrap(self, para)]
        return lines

class ImageGeneration:
    def __init__(self):
        self.inputText = ["Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."]

    def insertLineWrappingTags(self):
        characters = 125
        end = []
        textToAppend = ""
        for i, char in enumerate(repr(self.inputString)):
            textToAppend += char  # official string
            if "\\n" in textToAppend:
                end.append(textToAppend)
                textToAppend = ""

            if len(textToAppend) % characters == 0 and not i == 0:
                if not repr(self.inputString)[i + 1] == " ":
                    indWords = textToAppend.split(" ")
                    lastWord = indWords[len(indWords) - 1]
                    textToAppend = textToAppend[0:len(textToAppend) - len(lastWord):]
                    if not textToAppend == "":
                        end.append(textToAppend)
                    textToAppend = lastWord
                else:
                    if not textToAppend == "":
                        end.append(textToAppend)
                    textToAppend = ""

        characterAmount = 0
        for char in end:
            characterAmount += len(char)

        final_line = repr(self.inputString)[characterAmount:len(repr(self.inputString))]
        end.append(final_line)

        output = ""
        for i, line in enumerate(end):
            if i == len(end) - 1:
                line = line.replace("\\n", "")
                line = line[0: len(line) - 1]  # removes the ' at the end of the string on the last line
                output += line
                # print(len(line))
                # print(line)
                break
            if i == 0:
                pass
                # line = line[1: len(line)] # removes the ' at the start of the string on the first line
            line = line.replace("\\n", "")
            # print(len(line))
            # print(line)
            output += line + "<LW>"
        output = output[1: len(output)]
        self.inputString = output
        print(self.inputString)

    def drawImage(self):
        #for x, text in enumerate(self.inputText):
            #split_text = text.split('-split-')
            #inputText = self.inputText[:x] + split_text + self.inputText[x + 1:]
            #print(split_text)
        for num, text in enumerate(self.inputText):
            #self.generateAudio(text, num)
            #text = self.replaceWords(text, isImage=True)
            paragraphs = text.split('\n\n')
            img = Image.new('RGBA', (1920, 1080), (100, 100, 100, 0))
            W, H = (1920, 1080)
            draw = ImageDraw.Draw(img)
            # Load custom font
            font = ImageFont.truetype(f"{videosettings.assetPath}\Verdana.ttf", 42)
            ascent, descent = font.getmetrics()
            # Create DrawText object
            #d = DocumentWrapper(width=90)
            draw = ImageDraw.Draw(img)
            #text = textwrap.fill(text, replace_whitespace=False)
            TINT_COLOR = (0, 0, 0)  # Black
            TRANSPARENCY = .5  # Degree of transparency, 0-100%
            OPACITY = int(255 * TRANSPARENCY)
            # Create a context for drawing things on it.
            text_h = []
            text_w = []
            for x, para in enumerate(paragraphs):
                text = textwrap.fill(para, width=90)
                w, h = draw.textsize(text, font=font)
                text_h.append(h + (50 if x > 0 else 0))
                text_w.append(W / 2 - w / 2)
            hh = 0
            hh += int(sum(text_h) + 44)
            top = ((H - hh) / 2)
            bottom = 1080 - ((H - hh) / 2)
            overlay = Image.new('RGBA', img.size, TINT_COLOR + (OPACITY,))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle((0, top, 1920, bottom), fill=TINT_COLOR + (OPACITY,))

            # Alpha composite these two images together to obtain the desired result.
            new_img = Image.alpha_composite(img, overlay)
            new_draw = ImageDraw.Draw(im=new_img)
            test = ((H - int(sum(text_h))) / 2) - descent
            for x, para in enumerate(paragraphs):
                text = textwrap.fill(para, width=90)
                w, h = draw.textsize(text, font=font)
                (width, baseline), (offset_x, offset_y) = font.font.getsize(text)
                new_draw.text((min(text_w), test), text=text, fill='white', font=font, stroke_fill='black', stroke_width=2)
                test += h + 60 - offset_y

            #new_img.show()
            new_img.save('test.png')

    def test(self):
        img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        W, H = img.size
        base_width, base_height = img.size
        font = ImageFont.truetype(f"{videosettings.assetPath}\Verdana.ttf", 42)
        TINT_COLOR = (0, 0, 0)  # Black
        TRANSPARENCY = .5  # Degree of transparency, 0-100%
        OPACITY = int(255 * TRANSPARENCY)
        for index, comment in enumerate(self.inputText):
            paragraphs = comment.split('\n\n')
            x = []
            y = []
            for i, para in enumerate(paragraphs):
                text = textwrap.wrap(para, width=90)
                ascent, descent = font.getmetrics()
                draw = ImageDraw.Draw(img)
                for line in text:
                    (width, height), (offset_x, offset_y) = font.font.getsize(line)
                    w, h = draw.textsize(line, font=font)
                    hh = ascent + offset_y + descent - 6
                    print(h, hh)
                    x.append((W - w) / 2)
                    y.append(hh)
            top = sum(y)
            #print(top)
            for i, para in enumerate(paragraphs):
                #text = 'AQj'
                text = textwrap.wrap(para, width=90)
                ascent, descent = font.getmetrics()
                draw = ImageDraw.Draw(img)
                overlay = Image.new('RGBA', img.size, TINT_COLOR + (0,))
                draw = ImageDraw.Draw(overlay)
                top2 = top
                for line in text:
                    (width, height), (offset_x, offset_y) = font.font.getsize(line)
                    draw.rectangle([(0, top2 + offset_y + descent), (1920, top2 + ascent + descent + offset_y)], fill=TINT_COLOR + (OPACITY,))
                    top2 += 48
                new_img = Image.alpha_composite(img, overlay)
                new_draw = ImageDraw.Draw(im=new_img)
                for num, line in enumerate(text):
                    (width, height), (offset_x, offset_y) = font.font.getsize(line)
                    #new_draw.rectangle([(0, top + offset_y + descent), (1920, top + ascent + descent + offset_y)], outline='red', width=3)
                    new_draw.text((min(x), (1080 - top) / 2), line, font=font, fill='black', stroke_fill='black', stroke_width=2)
                    top += 48
                top += 48
                    #print(y)
                    #img.save('result.jpg')
                    #print(h)
                    #print(ascent, descent, offset_y)
                    #print(ascent + descent - offset_y - 5)
        new_img.show()
        new_img.save('test.png')

def get_y_and_heights(text_wrapped, dimensions, margin, font):
    """Get the first vertical coordinate at which to draw text and the height of each line of text"""
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    # Calculate the height needed to draw each line of text (including its bottom margin)
    line_heights = [
        font.getmask(text_line).getbbox()[3] + descent + margin
        for text_line in text_wrapped
    ]
    # The last line doesn't have a bottom margin
    line_heights[-1] -= margin

    # Total height needed
    height_text = sum(line_heights)

    # Calculate the Y coordinate at which to draw the first line of text
    y = (dimensions[1] - height_text) // 2

    # Return the first Y coordinate and a list with the height of each line
    return (y, line_heights)

def test2():

    FONT_FAMILY = "arial.ttf"
    WIDTH = 1920
    HEIGHT = 1080
    FONT_SIZE = 250
    V_MARGIN = -5
    CHAR_LIMIT = 90
    BG_COLOR = "black"
    TEXT_COLOR = "white"

    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
    split_text = text.split('\n\n')
    # Create the font
    font = ImageFont.truetype(f"{videosettings.assetPath}\Verdana.ttf", 42)
    # New image based on the settings defined above
    img = Image.new("RGBA", (WIDTH, HEIGHT), color=(0, 0, 0, 0))
    # Interface to draw on the image
    draw_interface = ImageDraw.Draw(img)

    # Wrap the `text` string into a list of `CHAR_LIMIT`-character strings
    text_lines = textwrap.wrap(text, CHAR_LIMIT)
    # Get the first vertical coordinate at which to draw text and the height of each line of text
    y, line_heights = get_y_and_heights(text_lines, (WIDTH, HEIGHT), V_MARGIN, font)
    print(y)
    xy = (0, y, 1920, (1080 - y) / 2)
    x = [(WIDTH - font.getmask(line).getbbox()[2]) / 2 for line in text_lines]
    for text in split_text:
        text_lines = textwrap.wrap(text, CHAR_LIMIT)
        # Draw each line of text
        for i, line in enumerate(text_lines):
            # Calculate the horizontally-centered position at which to draw this line
            # Draw this line
            draw_interface.rectangle(xy, outline='red', width=3)
            draw_interface.text((min(x), y), line, font=font, fill=TEXT_COLOR, stroke_fill='black', stroke_width=2)

            # Move on to the height at which the next line should be drawn at
            y += line_heights[i]
        y += 50
    print(sum(line_heights) + 50)

    # Save the resulting image
    img.save('test.png')
    img.show()

def test():
    background = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    img = Image.new('RGBA', (1920, 1080), (200, 200, 200, 0))
    W, H = img.size
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    paragraphs = text.split('\n\n')
    font = ImageFont.truetype(f"{videosettings.assetPath}\Verdana.ttf", 42)
    draw = ImageDraw.Draw(img)
    line_width = []
    (width, height), (offset_x, offset_y) = font.font.getsize('|')
    line_count = 0
    paragraph_count = []
    for num, para in enumerate(paragraphs):
        text_lines = textwrap.wrap(para, 90)
        for x, line in enumerate(text_lines):
            w, h = draw.textsize(line, font=font)
            line_width.append(W / 2 - w / 2)
            line_count += 45
        line_count += 45 if num + 1 < len(paragraphs) else 0
        paragraph_count.append(line_count)
    y = 0
    rect = 0
    for num, para in enumerate(paragraphs):
        overlay = Image.new('RGBA', (1920, line_count + 40), (0, 0, 0, 0))
        new_draw = ImageDraw.Draw(overlay)
        text_lines = textwrap.wrap(para, 90)
        new_draw.rectangle([(0, 0 if num == 0 else paragraph_count[num - 1]), (1920, paragraph_count[num] if num + 1 < len(paragraphs) else line_count + 40)], fill=(0, 0, 0, 205))
        rect += 45
        for t in text_lines:
            new_draw.text((min(line_width), y - offset_y + 20), t, font=font, fill='white', stroke_width=2, stroke_fill='black')
            y += 45
        y += 45 if num + 1 < len(paragraphs) else 0
        background.paste(overlay, (0, int((1080 - (line_count + 40)) / 2)), mask=overlay)
        background.save(f'tempframe{num}.png')
    #background.show()

if __name__ == "__main__":
    #ImgGen = ImageGeneration()
    #ImgGen.test()
    test()
