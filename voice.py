from responsive_voice import ResponsiveVoice

# Voice Generator class - generates voices into an mp3 file
class VoiceGenerator:
    def __init__(self):
        return

# Generates a voice by creating a ResponsiveVoice engine, and passing in prompt/path
    def generate(self, prompt, path):
        engine = ResponsiveVoice()
        engine.get_mp3(prompt, mp3_file=path, gender=ResponsiveVoice.FEMALE)

        

