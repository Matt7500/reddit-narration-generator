import pickle
import textwrap
from PIL import ImageFont, ImageDraw, Image
import videosettings
import settings
import subprocess
from moviepy.editor import *
import moviepy.editor as mp
import random
import json
from tqdm import tqdm

currentPath = os.path.dirname(os.path.realpath(__file__))
rawvideosaves = f"{currentPath}/VIDEOQUEUE/RAWSAVES"
combinevideosaves = f"{currentPath}/VIDEOQUEUE/COMBINE_SAVES"

def getFileNames(file_path):
    files = [os.path.splitext(filename)[0] for filename in os.listdir(file_path)]
    return files

class VideoGeneration:
    def __init__(self):
        self.save_names = getFileNames(rawvideosaves)
        self.combine_save_names = getFileNames(combinevideosaves)
        self.scriptno = 0

    def generateImage(self):
        for num, name in enumerate(self.save_names):
            for f in os.listdir(f"{settings.tempPath}/images"):
                os.remove(os.path.join(f"{settings.tempPath}/images", f))
            for f in os.listdir(f"{settings.tempPath}/audio"):
                os.remove(os.path.join(f"{settings.tempPath}/audio", f))
            if os.path.exists(f'{settings.tempPath}\\audio.mp3'):
                os.remove(f'{settings.tempPath}\\audio.mp3')
            print(f'Rendering {name} ({num + 1}/{len(self.save_names)})\n')
            split_name = name.split('rawvid')
            self.scriptno = split_name[1]
            #Loading the text from the post
            inputText = pickle.load(open(f'{rawvideosaves}/{name}.save', 'rb'))
            new_text = []
            #Checking for split operators in the text
            for x, text in enumerate(inputText):
                split_text = text.split('-split-')
                new_text += split_text
            frame_count = 0
            total_frames = 0
            for t in new_text:
                count = t.split('\n\n')
                for p in count:
                    total_frames += 1
            char_count = 0
            with tqdm(total=total_frames) as progressBar:
                for i, body in enumerate(new_text):
                    # Split text by paragraphs
                    text_body = self.replaceWords(body, isImage=True)
                    paragraphs = text_body.split('\n\n')
                    #Initialize images
                    background = Image.new('RGBA', (1920, 1080), (100, 100, 100, 0))
                    img = Image.new('RGBA', (1920, 1080), (200, 200, 200, 0))
                    W, H = img.size
                    font = ImageFont.truetype(f"{videosettings.assetPath}\Verdana.ttf", 42)
                    draw = ImageDraw.Draw(img)
                    line_width = []
                    (width, height), (offset_x, offset_y) = font.font.getsize('|')
                    line_count = 0
                    paragraph_count = []
                    #Iterate through text to get the height and width calculations
                    for y, para in enumerate(paragraphs):
                        text_lines = textwrap.wrap(para, 90)
                        for x, line in enumerate(text_lines):
                            w, h = draw.textsize(line, font=font)
                            line_width.append(W / 2 - w / 2)
                            line_count += 45
                        line_count += 45 if y + 1 < len(paragraphs) else 0
                        paragraph_count.append(line_count)
                    y = 0
                    rect = 0
                    for pNum, para in enumerate(paragraphs):
                        audio_lines = self.replaceWords(para)
                        char_count += len(audio_lines)
                        self.generateAudio(f"<speak><prosody rate='-15%'><break time='500ms'/>{audio_lines}<break time='500ms'/></prosody></speak>", frame_count)
                        overlay = Image.new('RGBA', (1920, line_count + 40), (0, 0, 0, 0))
                        new_draw = ImageDraw.Draw(overlay)
                        text_lines = textwrap.wrap(para, 90)
                        new_draw.rectangle([(0, 0 if pNum == 0 else paragraph_count[pNum - 1] + 1), (1920, paragraph_count[pNum] if pNum + 1 < len(paragraphs) else line_count + 40)], fill=(0, 0, 0, 205))
                        rect += 45
                        for text in text_lines:
                            new_draw.text((min(line_width), y - offset_y + 20), text, font=font, fill='white', stroke_width=2, stroke_fill='black')
                            y += 45
                        y += 45 if pNum + 1 < len(paragraphs) else 0
                        background.paste(overlay, (0, int((1080 - (line_count + 40)) / 2)), mask=overlay)
                        background.save(f'{settings.tempPath}\\images\\tempframe{frame_count}.png')
                        frame_count += 1
                        progressBar.update(1)
            print(f'Total Characters: {char_count}')
            #progressBar.close()
            self.generateVideo()

    def replaceWords(self, text, isImage=None):
        self.text = text
        if isImage is None:
            self.text = self.text.replace("f**k", "duck")
            self.text = self.text.replace("sh*t", "sheet")
            self.text = self.text.replace("d*ck", "deck")
            self.text = self.text.replace("c*ck", "cook")
            self.text = self.text.replace("F**k", "duck")
            self.text = self.text.replace("sh*t", "sheet")
            self.text = self.text.replace("b*tch", "beach")
            self.text = self.text.replace("B*tch", "beach")
            self.text = self.text.replace("D*ck", "deck")
            self.text = self.text.replace("C*ck", "cook")
            self.text = self.text.replace("*", "")
            self.text = self.text.replace("&", " and ")
            self.text = self.text.replace("@", "")
            self.text = self.text.replace("#", "")
            self.text = self.text.replace("^", "")
            self.text = self.text.replace("%", " percent ")
            self.text = self.text.replace("<", "")
            self.text = self.text.replace(">", "")
            self.text = self.text.replace("(", "")
            self.text = self.text.replace(")", "")
            self.text = self.text.replace("[", "")
            self.text = self.text.replace("]", "")
            self.text = self.text.replace("\"", "")
            self.text = self.text.replace("\n", "")
            self.text = self.text.replace("OP ", " O-P ")
            self.text = self.text.replace(" OP", " O-P ")
            self.text = self.text.replace(" s*x", " s-x")
            self.text = self.text.replace(" S*x", " s-x")
            self.text = self.text.replace("m)", " male ")
            self.text = self.text.replace("(m", " male ")
            self.text = self.text.replace("M)", " male ")
            self.text = self.text.replace("(M", " male ")
            self.text = self.text.replace("m]", " male ")
            self.text = self.text.replace("f)", " female ")
            self.text = self.text.replace("(f", " female ")
            self.text = self.text.replace("f]", " female ")
            self.text = self.text.replace("M]", " male ")
            self.text = self.text.replace("F)", " female ")
            self.text = self.text.replace("(F", " female ")
            self.text = self.text.replace("F]", " female ")
            self.text = self.text.replace(" gf ", " girlfriend ")
            self.text = self.text.replace(" GF ", " girlfriend ")
            self.text = self.text.replace(" bf ", " boyfriend ")
            self.text = self.text.replace(" BF ", " boyfriend ")
            self.text = self.text.replace(" AP ", " affair partner ")
            self.text = self.text.replace("a**hole", "a-hole")
            self.text = self.text.replace("A**hole", "a-hole")
            self.text = self.text.replace(" r*pe", "grape")
            self.text = self.text.replace("...", ". ")
            self.text = self.text.replace("AITA", "Am I the a-hole?")
            self.text = self.text.replace(" omg ", "oh my god")
            self.text = self.text.replace(" OMG ", "oh my god")
            self.text = self.text.replace(" idk ", "I don't know")
            self.text = self.text.replace(" idc ", "I don't care")
            self.text = self.text.replace("STBXGF", "soon to be ex girlfriend")
            self.text = self.text.replace("stbxgf", "soon to be ex girlfriend")
            self.text = self.text.replace("STBXBF", "soon to be ex boyfriend")
            self.text = self.text.replace("stbxbf", "soon to be ex boyfriend")
            self.text = self.text.replace("STBX", "soon to be ex")
            self.text = self.text.replace("stbx", "soon to be ex")
            self.text = self.text.replace("p*rn", "pron")
            self.text = self.text.replace("P*rn", "Pron")
            #self.text = "<speak><prosody rate='-10%'><break time='1s'/>" + self.text
            #self.text += "<break time='500ms'/></prosody></speak>"
        else:
            self.text = self.text.replace(" rape", "r*pe")
            self.text = self.text.replace("fuck", "f**k")
            self.text = self.text.replace(" shit", " sh*t")
            self.text = self.text.replace("shit ", "sh*t ")
            self.text = self.text.replace(" bitch", "b*tch")
            self.text = self.text.replace("Fuck", "F**k")
            self.text = self.text.replace("porn", "p*rn")
            self.text = self.text.replace("Porn", "P*rn")
            self.text = self.text.replace("Shit ", "Sh*t ")
            self.text = self.text.replace(" Shit", " Sh*t")
            self.text = self.text.replace("Bitch", "B*tch")
            self.text = self.text.replace("Dick", "D*ck")
            self.text = self.text.replace("Cock", "C*ck")
            self.text = self.text.replace("asshole", "a**hole")
            self.text = self.text.replace("sex", "s*x")
            self.text = self.text.replace("Asshole", "A**hole")
            self.text = self.text.replace("Sex", "S*x")

        return self.text

    def generateAudio(self, text, frame):
        aws_profiles = ['default', 'user1']
        profile = random.choice(aws_profiles)
        self.audio_path = f"{settings.tempPath}\\audio\\tempaudio{frame}.mp3"
        #new_text = self.replaceWords(text, isImage=None)
        #command = f'aws polly synthesize-speech --text-type "ssml" --output-format "mp3" --voice-id "Matthew" --text "{new_text}" "{self.audio_path}"'
        command = f'aws polly synthesize-speech --engine "neural" --text-type "ssml" --output-format "mp3" --voice-id "Matthew" --text "{text}" "{self.audio_path}" --profile {profile}'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def generateAudio2(self, text, frame):
        self.audio_path = f"{settings.tempPath}\\audio\\tempaudio{frame}.mp3"
        new_text = self.replaceWords(text, isImage=None)
        data = {"text": f"{new_text}"}
        with open('input.json', 'w') as f:
            json.dump(data, f)
        os.system(f'curl -X POST -u "apikey:80PBPM4tIrT9q7EzpLs1EsrsU0ykdsN5eHNS0yedfYKN" --header "Content-Type: application/json" --header "Accept: audio/mp3" --data @input.json --output "{self.audio_path}" "https://api.us-east.text-to-speech.watson.cloud.ibm.com/instances/ec9a9a3d-b48c-4b8d-b340-05248714cfbe/v1/synthesize?voice=en-US_MichaelV3Voice"')

    def generateVideo(self):
        #Creating audio sequence and getting the durations of each audio file
        #audio_files = [AudioFileClip(f'{settings.tempPath}\\audio\\tempaudio{frameno}.mp3') for frameno in range(len(os.listdir(f'{settings.tempPath}\\audio')))]
        #durations = [audio.duration for audio in audio_files]
        audio_sequence = open(f'{settings.tempPath}\\audio_concat.txt', 'w')
        audio_files = [f"file '{settings.tempPath}\\audio\\tempaudio{frameno}.mp3'\n" for frameno in range(len(os.listdir(f'{settings.tempPath}\\audio')))]
        audio_sequence.writelines(audio_files)
        command = f'ffmpeg -f concat -safe 0 -i "{settings.tempPath}\\audio_concat.txt" -c copy "{settings.tempPath}\\audio.mp3"'
        audio_sequence.close()
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        voice = AudioFileClip(f'{settings.tempPath}\\audio.mp3')
        #audio_sequence = [AudioFileClip(f'{settings.tempPath}\\audio\\tempaudio{frameno}.mp3') for frameno in range(len(os.listdir(f'{settings.tempPath}\\audio')))]
        #for frameno in range(len(os.listdir(f'{settings.tempPath}\\audio'))):
            #audio_sequence.append(AudioFileClip(f'{settings.tempPath}\\audio\\tempaudio{frameno}.mp3'))
            #audio_sequence.append(AudioFileClip(f'{settings.assetPath}\\silence.mp3'))
        durations = voice.duration
        durations += 15
        #Making music loop
        background_song = AudioFileClip(f'{settings.assetPath}\\Music\\music.mp3')
        loop = afx.audio_loop(background_song, duration=durations)
        #Combine audio clips together then add the music loop
        #concat_audio = concatenate_audioclips(audio_sequence)
        final_audio = mp.CompositeAudioClip([loop, voice])
        #Choosing random background video
        background = VideoFileClip(f'{settings.assetPath}\\BackgroundVids\\{random.choice(getFileNames(f"{settings.assetPath}/BackgroundVids"))}.mp4', target_resolution=(1080, 1920))
        background = background.set_duration(durations)
        background = background.set_audio(final_audio)
        outro_image = f"{settings.assetPath}\OutroImage.png"
        #Getting all the images created put into a list
        image_sequence = [f'{settings.tempPath}\\images\\tempframe{frameno}.png' for frameno in range(len(os.listdir(f'{settings.tempPath}\\images')))]
        image_sequence.append(outro_image)
        #Creating image sequence with the corresponding durations
        audios = [AudioFileClip(f'{settings.tempPath}\\audio\\tempaudio{frameno}.mp3') for frameno in range(len(os.listdir(f'{settings.tempPath}\\audio')))]
        audio_durations = [audio.duration for audio in audios]
        audio_durations.append(15)
        image = ImageSequenceClip(image_sequence, durations=audio_durations)
        #Putting images over background video
        final = mp.CompositeVideoClip([background, image])
        intro = VideoFileClip(f"{settings.assetPath}\intro.mov")
        final_final = mp.CompositeVideoClip([final, intro])
        #Checking for folder relating to the video
        if not os.path.exists(f'{settings.finishedvideosdirectory}/vid{self.scriptno}'):
            os.mkdir(f'{settings.finishedvideosdirectory}/vid{self.scriptno}')
        #Render final video
        final.write_videofile(f'{settings.finishedvideosdirectory}/vid{self.scriptno}/vid{self.scriptno}.mp4', fps=24)
        #Removing save file and temporary files
        os.remove(f'{settings.rawvideosaves}\\rawvid{self.scriptno}.save')
        os.remove(f'{settings.tempPath}\\audio.mp3')
        for a in audios:
            a.close()
        for f in os.listdir(f"{settings.tempPath}\\images"):
            os.remove(os.path.join(f"{settings.tempPath}\\images", f))
        for f in os.listdir(f"{settings.tempPath}\\audio"):
            os.remove(os.path.join(f"{settings.tempPath}\\audio", f))

    def generateVideo_ffmpeg(self):
        audio_files = [AudioFileClip(f'{settings.tempPath}\\audio\\tempaudio{frameno}.mp3') for frameno in range(len(os.listdir(f'{settings.tempPath}\\audio')))]
        durations = [audio.duration for audio in audio_files]
        audio_sequence = open(f'{settings.tempPath}\\audio_concat.txt', 'w')
        audio_files = [f"file '{settings.tempPath}\\audio\\tempaudio{frameno}.mp3'\n" for frameno in range(len(os.listdir(f'{settings.tempPath}\\audio')))]
        audio_sequence.writelines(audio_files)
        audio_sequence.close()
        command = f'ffmpeg -stream_loop -1 -i "{settings.assetPath}\\Music\\music.mp3" -f concat -safe 0 -i "{settings.tempPath}\\audio_concat.txt" -filter_complex amix=inputs=2:duration=shortest  "{settings.tempPath}\\audio.mp3"'
        process = subprocess.call(command, shell=True)
        image_sequence = open(f'{settings.tempPath}\\image_concat.txt', 'w')
        image_files = [f"file '{settings.tempPath}\\images\\tempframe{frameno}.png'\nduration {durations[frameno]}\n" for frameno in range(len(os.listdir(f'{settings.tempPath}\\images')))]
        image_sequence.writelines(image_files)
        image_sequence.close()
        #command = f'ffmpeg -hwaccel cuda -i "{settings.assetPath}\\BackgroundVids\\background20.mp4" -f concat -safe 0 -i "{settings.tempPath}\\image_concat.txt" -i "{settings.tempPath}\\audio.mp3" -filter_complex amix=inputs=2:duration=shortest -c:v h264_nvenc "{settings.tempPath}\\test.mp4"'
        command = f'ffmpeg -hwaccel cuda -f concat -safe 0 -i "{settings.tempPath}\\image_concat.txt" -i "{settings.tempPath}\\audio.mp3" -c:v h264_nvenc "{settings.tempPath}\\test.mp4"'
        process = subprocess.call(command, shell=True)


if __name__ == '__main__':
    vidGen = VideoGeneration()
    vidGen.generateImage()
    #vidGen.generateVideo_ffmpeg()
