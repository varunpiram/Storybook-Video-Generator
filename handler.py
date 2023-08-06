from huey import RedisHuey
from video import VideoGenerator
huey = RedisHuey()

# Makes a huey task which calls on the generator to make a video
@huey.task()
def generate(prompt, email):
    vg = VideoGenerator()
    vg.make(prompt, email)

