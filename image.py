from io import BytesIO
import requests
from PIL import Image, ImageOps, ImageFilter
import random
import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords
from dotenv import load_dotenv
import os
load_dotenv()
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
stop_words = set(stopwords.words('english'))
# Gets Pexels API Key
key = str(os.getenv('PEXELS_KEY'))

# Image Generator class which generates a relevant image given a sentence
class ImageGenerator:
    def __init__(self):
        return
    
    # Gets a keyword for each sentence, gets an image from Pexels stock image 
    # library, and processes it
    def generate(self, sentence):
        keyword = self.processSentence(sentence)
        raw = self.getImage(keyword)
        return self.processImage(raw)

    # Processes a sentence by getting the appropiate keyword by getting it's middlemost
    # noun
    def processSentence(self, sentence):

        # Tokenizes sentence into words and tags them by part of speech
        words = word_tokenize(sentence)
        tagged_words = pos_tag(words)

        # Initalizes storage for verbs and nouns
        verbs = []
        nouns = []

        # Stores verbs and nouns
        for word, tag in tagged_words:
            if 'VB' in tag:
                verbs.append(word)
            elif 'NN' in tag:
                nouns.append(word)

        # Attemps to get the middlemost noun, if not then verb, if not then 'fallback'
        # word
        try:
            mid = len(verbs) // 2
            return nouns[mid]
        except:
            try:
                mid = len(nouns) // 2
                return verbs[mid]
            except:
                return "sky"

    # Gets an image given a prompt using Pexels stock image library
    def getImage(self, prompt):

        # Gets a random number between 0-1
        rand = random.random()

        # Gets an image using Pexels API
        url = f"https://api.pexels.com/v1/search?query={prompt}&per_page=3&page=1"
        headers = {"Authorization": key}
        response = requests.get(url, headers=headers)
        response = response.json()

        # Gets a random image of the top 3 and saves into memory
        if rand < .33:
            try:
                image = Image.open(BytesIO(requests.get(response['photos'][2]['src']['large']).content))
                return image
            except:
                pass
        if rand < .66:
            try:
                image = Image.open(BytesIO(requests.get(response['photos'][1]['src']['large']).content))
                return image
            except:
                pass
        try:
            image = Image.open(BytesIO(requests.get(response['photos'][0]['src']['large']).content))
        except:
            raise Exception("Image Unavailable")
            
    # Returns a backup image for use in edge cases
    def returnBackup(self):
        url1 = f"https://api.pexels.com/v1/search?query=ocean&per_page=3&page=1"
        headers1 = {"Authorization": key}
        response1 = requests.get(url1, headers=headers1)
        response1 = response1.json()
        image = Image.open(BytesIO(requests.get(response1['photos'][2]['src']['large']).content))
        return image

    # Processes the image for use in video by formatting it and fitting it as needed
    def processImage(self, image):

        # Generates two images - a blurred out background and a front image
        backimage = ImageOps.fit(image, (1080, 1920), Image.LANCZOS)
        backimage = backimage.filter(ImageFilter.GaussianBlur(15))
        frontimage = image.copy()

        # Gets the ratio and target ratio of the image for resizing
        ratio = frontimage.size[0] / frontimage.size[1]
        target_ratio = 1080 / 1920

        # Resizes the front image to fit into the desired video size
        if ratio > target_ratio:
            # If the image is wider than the target, resize based on width
            h = int(1080 / ratio)
            frontimage = frontimage.resize((1080, h), Image.LANCZOS)
        else:
            # If the image is taller than the target, resize based on height
            w = int(1920 * ratio)
            frontimage = frontimage.resize((w, 1920), Image.LANCZOS)

        # Resizes front image while preserving aspect ratio
        width, height = frontimage.size
        x = (1080 - width) // 2
        y = (1920 - height) // 2

        # Adds front image to blurred back image
        image = backimage
        image.paste(frontimage, (x, y))

        # Returns image
        return image


