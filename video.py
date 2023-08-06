from image import ImageGenerator
from voice import VoiceGenerator
from story import StoryGenerator
from moviepy.editor import ImageSequenceClip, concatenate_videoclips, AudioFileClip, ImageClip, CompositeVideoClip
from dotenv import load_dotenv
import os
import numpy as np
import matplotlib
# Uses Agg for matplotlib as no visual graphs are being generated
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from PIL import Image
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from tempfile import NamedTemporaryFile
load_dotenv()
# Gets email/password to send out email
emfrom = str(os.getenv('EMAIL_ADDRESS'))
empass = str(os.getenv('EMAIL_PASSWORD'))
emserv = str(os.getenv('EMAIL_SERVER'))
emport = int(str(os.getenv('EMAIL_PORT')))

# Video Generator class - generates the video and sends it out
class VideoGenerator:
    # Initializes w/ array to store used filepaths
    def __init__(self):
        self.paths = []

    # Generates a video given a prompt 
    def generate(self, story):
        
        # Initializes generators and storage for clips
        ig = ImageGenerator()
        vg = VoiceGenerator()
        clips = []

        # Creates a backup image in case first sentence has no images in pexels lib
        self.imageStore = ig.returnBackup()

        # For every list of words in the story object, generates an image for sentence,
        # adds voiceover, adds captions, and makes a video clip
        for wordList in story:

            # Reconstructs sentence from wordList
            sentence = wordList[0]
            for i in range(1, len(wordList)):
                word = wordList[i]
                sentence += " "
                sentence += word

            # Gets an image for each sentence (& saves as backup), uses backup if it can't
            try:
                image = ig.generate(sentence)
                self.imageStore = image
            except:
                image = self.imageStore
            
            # Creates a temporary file and generates a voiceover of the sentence onto it
            with NamedTemporaryFile(suffix=".mp3", delete=False) as voicefile:
                vfpath = voicefile.name
                self.paths.append(vfpath)
                vg.generate(sentence, vfpath)
                voiceClip = AudioFileClip(vfpath)
                voiceTime = voiceClip.duration

            # Turns the image into a static video and adds voiceover onto it
            npImg = np.array(image)
            rawclip = ImageSequenceClip([npImg], durations=[voiceTime])
            rawclip = rawclip.set_audio(voiceClip)

            # Initializes storage for word-by-word captions
            wordclips = []

            # For every word in list of words (sentences), generate a caption as a video
            # clip and add to wordclips storage
            for word in wordList:
                
                # Generates a caption image using matplotlib
                fig, ax = plt.subplots()
                text = ax.text(0.5, 0.5, word, color='white', fontsize=24, ha='center', va='center', weight='bold')
                text.set_path_effects([pe.withStroke(linewidth=5, foreground='black')]) # type: ignore
                plt.axis('off')
                fig.patch.set_visible(False) # type: ignore
                ax.axis('off')

                # Stores the caption image using memory
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0, transparent=True)
                buf.seek(0)
                img_arr = np.array(Image.open(buf))

                # Turns the caption image into a clip with duration voiceover divided by word
                # count with an .825x adjustment (can be changed for preference)
                txt_clip = ImageClip(img_arr).set_duration((0.825 * voiceTime / len(wordList)))

                # Adds to wordclips storage
                wordclips.append(txt_clip)
       
            # Combines all the captions into one
            captions = concatenate_videoclips(wordclips, method="compose")

            # Adds the captions onto the clip
            clip = CompositeVideoClip([rawclip, captions.set_pos(('center', 'center'))]) # type: ignore

            # Adds the clip to clips storage
            clips.append(clip)

        # Combines all the clips into video
        video = concatenate_videoclips(clips)

        # Saves video into temporary mp4 file
        with NamedTemporaryFile(suffix=".mp4", delete=False) as videofile:
            vdfpath = videofile.name
            self.paths.append(vdfpath)
            video.write_videofile(vdfpath, fps=12, bitrate='500k')
            return vdfpath
    
    # Sends out a video given path and address
    def send(self, address, path):
            emto = address

            # Sets up framework for sending message
            msg = MIMEMultipart()
            msg['From'] = emfrom
            msg['To'] = emto
            msg['Subject'] = "Your video is ready!"

            # Sets body message
            body = "Here is the video you generated!"
            msg.attach(MIMEText(body, 'plain'))

            # Opens file from path
            filename = path
            attachment = open(filename, "rb")

            # Attaches file to email
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename=storybook.mp4")
            msg.attach(part)

            # Sends out email using SMTP server (brevo)
            server = smtplib.SMTP(emserv, emport)
            server.starttls()
            server.login(emfrom, empass)
            text = msg.as_string()
            server.sendmail(emfrom, emto, text)
            server.quit()

    # Puts it all together by making a story, then creating a video, and sending it out
    # Also clears all temporary files
    def make(self, prompt, address):
        sg = StoryGenerator()
        story = sg.generate(prompt)
        vid = self.generate(story)
        self.send(address, vid)
        for path in self.paths:
            os.remove(path)
