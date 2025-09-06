import base64

import time

import os

from picamera2 import Picamera2

from libcamera import controls

from openai import OpenAI

from pydantic import BaseModel

import RPi.GPIO as GPIO



import subprocess


key = "replace with key" # Replace with your OpenAI key

client = OpenAI(api_key=key)

mplayer_process = subprocess.Popen(
    ['mplayer', '-slave', '-quiet', '-idle', '-speed', '0.3', '-af', 'scaletempo'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

def send_command(command):
    mplayer_process.stdin.write(command + "\n")
    mplayer_process.stdin.flush()
    
def play_mp3(mp3_file_path):
    send_command(f'loadfile "{mp3_file_path}"')

def take_picture(picam2, image_path):


    

    #picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})

    #capture_config = picam2.create_still_configuration()
    
    #warn that about to be captured
    play_mp3("audio/warning.mp3")
    
    # delay before capturing, idk why but maybe delete?
    time.sleep(4)
    
    picam2.autofocus_cycle()
    
    
    #picam2.switch_mode_and_capture_file(capture_config, image_path)
    picam2.capture_file(image_path)
    
    # maybe return this to the original commented position?
    #picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
        
class GeneratedResult(BaseModel):
    proof_statement: str
    is_blurry_or_cut_off_or_doesnt_exist: bool
    

def get_image_text(image_path):
    base64_image = encode_image(image_path)

    response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What are the text and mathematical symbols in this image of a mathematical proof statement? Respond with the proof statement. Say if the image is too blurry or the proof statement is cut off or if no proof statements can be found in the image.",
        },
        {
          "type": "image_url",
          "image_url": {
            "url":  f"data:image/jpeg;base64,{base64_image}"
          },
        },
      ],
    }
    ],
    response_format = GeneratedResult,
    )
    
    message = response.choices[0].message.parsed
    
    print(message.proof_statement)
    
    return [message.proof_statement, message.is_blurry_or_cut_off_or_doesnt_exist]
    #print(response.choices[0].message.content)
    #return response.choices[0].message.content
    
    
def get_answer(prompt):
    completion = client.beta.chat.completions.parse(
    model = "o1-preview",
    messages = [
        {
            "role": "user",
            "content": "Write a formal mathematical proof fit for a mathematical paper without explaining. In your proof, write words instead of mathematical symbols (example: instead of 'x > y' write 'x is greater than y and instead of '1/x' and 'x^n' write '1 over x' and 'x to the n'). " + prompt
        }
    ],
    #response_format=UserFeedback,
)
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content
    
# file output should be mp3
def create_tts_file(speech_output_path, text):
    tts_response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    # use unpacked dictionary to avoid "input" keyword conflicting with input function
    #tts_response = client.audio.speech.create(**{"model": "tts-1", "voice": "alloy", "input": text})
    tts_response.stream_to_file(speech_output_path)
    
    
if __name__ == "__main__":

    picam2 = Picamera2()
    picam2.start(show_preview=True)


    image_root = "images/test"
    audio_root = "audio/testing"
    while True:
        
        img_path = image_root +  ".jpg"
        
        take_picture(picam2, img_path)

        
        try:
            image_data = get_image_text(img_path)


            if image_data[1]:
                print("too blurry")
                continue
                
                
            image_txt = image_data[0]

            
            answer_txt = get_answer(image_txt)

            audio_path = audio_root + ".mp3"

            create_tts_file(audio_path, answer_txt)

            play_mp3(audio_path)

            # calculate time to sleep based on length of output
            # replace with a more dynamic way in the future
            time.sleep(len(answer_txt)/5)
        except Exception:
            pass
