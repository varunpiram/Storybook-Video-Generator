# Automated Storybook-Style Video Generator:

## Description:
This project automatically generates and emails you a storybook-style short-form video with narration and word-by-word captioning based on a given topic. It is powered by OpenAI's gpt, ResponsiveVoice, and Pexels stock image library. 

It works by taking in an email address and topic, which is then passed into the VideoGenerator class which uses MoviePy. Here, the topic is passed into the StoryGenerator, which then requests and processes a story through OpenAI's API. 

The story is then broken into sentences, where images and voice are generated through Pexels and ResponsiveVoice, and then turned into clips. In each clip, the sentences are further broken into words, for which captions are generated using Matplotlib, and then overlayed.

Finally, all the clips are combined, and then sent out to an email address.

This project can be locally hosted, and implements asynchronous programming via huey to allow multiple requests without waiting for generation to complete.

## Usage:
### Setup:
Clone this repository, and install necessary libraries via:

`pip install -r requirements.txt`

This project requires multiple API keys, so store these in a .env file
in the project root directory like so:
```
OPENAI_KEY=[key]
PEXELS_KEY=[key]
```
Additionally, you will need an SMTP server, so store your information in the
same file as such:
```
EMAIL_ADDRESS=[address]
EMAIL_PASSWORD=[password]
EMAIL_SERVER=[server]
EMAIL_PORT=[port]
PORT=[]
```
### Use:
To run this program, run `app.py` and in a separate terminal, run:

`huey_consumer.py handler.huey`

Make sure Redis is installed and running (`redis-server`) as huey implements it.

To clear all tasks in the queue, use:

`redis-cli FLUSHALL`

This will delete all data so be careful.