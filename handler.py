from huey import RedisHuey
from video import VideoGenerator
huey = RedisHuey()

# Makes a huey task which calls on the generator to make a video
@huey.task(retries=2, retry_delay=60)
def generate(prompt, email):
    vg = VideoGenerator()
    vg.make(prompt, email)

