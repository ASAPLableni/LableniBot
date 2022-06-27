import numpy as np
import pandas as pd
import subprocess
from datetime import datetime
import wave, time, os, pyaudio, pyttsx3, sys
import speech_recognition as sr

# from googletrans import Translator
from gtts import gTTS 

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
from tempfile import gettempdir

import utils as ute

print(" ***** Models loaded ***** ")

session = Session(
    aws_access_key_id="AKIA5253QQ44EM6O6P4Q", 
    aws_secret_access_key="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"
)
polly = session.client("polly", region_name='eu-west-1')

# ### Some parameters ###
# Time to wait until ask the user to repeat.
waitTime = 15
# Audio record parameters. 
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 8

# #################
# ### CONSTANTS ###
# #################

# Begin of the session
_, _, init_of_session = ute.get_current_time()
os.mkdir("Conversations/Audio/" + str(init_of_session))

WAVE_OUTPUT_FILENAME = "Conversations/Audio/" + str(init_of_session) + "/subjectOutput_t_id_"
WAVE_OUTPUT_BOT_FILENAME = "Conversations/Audio/" + str(init_of_session) + "/botOutput_t_id_"

ROOT_TO_OMNIVERSE = "C:/Users/demos/AppData/Local/ov/pkg/audio2face-2021.3.3/exts/omni.audio2face.player/omni/audio2face/player/scripts/streaming_server"
AUDIO_NAME = "/audio_bot_aws.wav"
OMNIVERSE_AVATAR = "/audio2face/player_instance"
# Parameters
# /World/Debra/ManRoot/Debra_gamebase_A2F/Debra_gamebase_A2F/CC_Game_Body/CC_Game_Body_result
# /audio2face/player_instance
# /World/charTransfer/mark
# /World/audio2face/player_streaming_instance
# audio2face/player_streaming_instance_03
# /World/audio2face/player_streaming_instance_01
# /World/audio2face/player_streaming_instance

OUTPUT_FILE_IN_WAVE = "audio_bot_aws.wav" # WAV format Output file  name
NATIVE_LENGUAGE = "es"

# ### Initial message ###

initial_message = "Como te llamas?"
counter = 0

# Modes avaible: 'voice' or 'write'.
CHAT_MODE = "write"

# ###############################
# ### INITIAL MESSAGE TO GPT3 ###
# ###############################

bot_start_sequence = "Yolo:"
human_start_sequence = "Human: "

global_message = "The following is a conversation with Yolo. Yolo is helpful, creative, clever, and very friendly." \
                 "Human: Hello, who are you?" \
                 "Yolo: My name is Yolo. What is your name ? "

# ##############
# ### INPUTS ###
# ##############

# SubjectId
print("Please write your subject id")
subject_id = input()

# SubjectName
print("Please write your name")
subject_name = input()

bot_result_list = []
ct_voice_id = 0
try:
    while True:
        if counter > 0:
            if CHAT_MODE == "voice":
                p = pyaudio.PyAudio()
                stream = p.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK)

                print("*** Recording ***")
                frames = []
                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK, exception_on_overflow = False)
                    frames.append(data)
                print("*** Done recording ***")

                stream.stop_stream()
                stream.close()
                p.terminate()

                wf = wave.open(WAVE_OUTPUT_FILENAME + str(ct_voice_id)+".wav", 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()

                r = sr.Recognizer()
                with sr.AudioFile(WAVE_OUTPUT_FILENAME + str(ct_voice_id)+".wav") as source:
                    audio = r.record(source)

                spanish_text = r.recognize_google(audio, language=NATIVE_LENGUAGE+"-EU")
                ct_voice_id += 1

            elif CHAT_MODE == "write":
                print("Write something....")
                spanish_text = input()
                print("* done recording")

            else:
                print("Please select between 'write' or 'voice' method")

            print("Your input message", spanish_text)

        else:
            spanish_text = initial_message

        t_str, t_unix, _ = ute.get_current_time()
        bot_result_list.append({
            "SubjectId": subject_id
            "SubjectName": subject_name,
            "TimeStr": t_str,
            "UnixTimestamp": t_unix,
            "Source": "Person",
            "Message": spanish_text,
            "Mode": mode
        })
        df_to_save = pd.DataFrame(bot_result_list)
        df_to_save.to_excel("Conversations/Conv_"+str(init_of_session)+".xlsx", index=False)

        # ###################
        # ### TRANSLATION ###
        # ###################
        # Here the message is translated from spanish to english.
        x = google_translator.translate(spanish_text)
        person_message = x.text
        global_message += human_start_sequence + " " + person_message

        # ###########
        # ### BOT ###
        # ###########

        response = openai.Completion.create(
          engine="davinci",
          prompt=message,
          temperature=0.9,
          max_tokens=initial_tokens,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0.6,
          stop=["Human:"] 
        )
        bot_answer = response["choices"][0]["text"]
        bot_message = bot_answer.replace("Yolo:", "") if "Yolo:" in bot_answer else bot_answer
        print("Time of the answer", np.round(time.time()-t0, 5), "s")
        
        global_message += bot_start_sequence + " " + bot_message

        # ###################
        # ### TRANSLATION ###
        # ###################
        # Here the message is translated from english to spanish.

        x = google_translator.translate(bot_message, dest=NATIVE_LENGUAGE) 
        bot_message_spanish = x.text 
        
        t_str, t_unix, _ = ute.get_current_time()
        bot_result_list.append({
            "SubjectId": subject_id
            "SubjectName": subject_name,
            "TimeStr": t_str,
            "UnixTimestamp": t_unix,
            "Source": "Bot",
            "Message": bot_message_spanish,
            "Mode": mode
        })
        df_to_save = pd.DataFrame(bot_result_list)
        df_to_save.to_excel("Conversations/Conv_"+str(init_of_session)+".xlsx", index=False)

        print("Bot message", bot_message_spanish)

        # #################
        # ### USING AWS ###
        # #################
        RATE = 16000 # Polly supports 16000Hz and 8000Hz output for PCM format
        response = polly.synthesize_speech(
            Text=bot_message_spanish, 
            OutputFormat="pcm", 
            VoiceId="Lucia",
            SampleRate=str(RATE),
            Engine="neural"
        )
        
        # Initializing variables
        CHANNELS = 1 # Polly's output is a mono audio stream
        FRAMES = []
        WAV_SAMPLE_WIDTH_BYTES = 2 # Polly's output is a stream of 16-bits (2 bytes) samples

        # Processing the response to audio stream
        STREAM = response.get("AudioStream")
        FRAMES.append(STREAM.read())

        WAVEFORMAT = wave.open(ROOT_TO_OMNI + "/" + OUTPUT_FILE_IN_WAVE, 'wb')
        WAVEFORMAT.setnchannels(CHANNELS)
        WAVEFORMAT.setsampwidth(WAV_SAMPLE_WIDTH_BYTES)
        WAVEFORMAT.setframerate(RATE)
        WAVEFORMAT.writeframes(b''.join(FRAMES))
        WAVEFORMAT.close()

        # #################
        # ### OMNIVERSE ###
        # #################
        call_to_omniverse = " python " + ROOT_TO_OMNIVERSE + "/my_test_client.py "

        call_to_omniverse += " " + ROOT_TO_OMNIVERSE + AUDIO_NAME + " " + OMNIVERSE_AVATAR
        print(call_to_omniverse)
        subprocess.call(call_to_omniverse, shell=True)

except KeyboardInterrupt:
    pass
