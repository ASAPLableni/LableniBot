import pandas as pd
import subprocess
# from datetime import datetime
import wave
import time
import os
import pyaudio
import json
# import pyttsx3
# import sys
import speech_recognition as sr
import openai

from googletrans import Translator

from boto3 import Session
# from botocore.exceptions import BotoCoreError, ClientError
# from contextlib import closing
# from tempfile import gettempdir

import utils as ute

# Initialize the translator model
google_translator = Translator()

print(" ***** Models loaded ***** ")

# ###########################
# ### Opening CONFIG file ###
# ###########################
config_json = open('config.json')
config_dict = json.load(config_json)

session = Session(
    aws_access_key_id=config_dict["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=config_dict["AWS_SECRET_ACCESS_KEY"]
)
polly = session.client("polly", region_name='eu-west-1')

openai.api_key = config_dict["OPENAI_KEY"]
INITIAL_TOKENS_OPENAI = 50

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

ROOT_TO_OMNIVERSE = config_dict["ROOT_TO_OMNIVERSE"]
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

OUTPUT_FILE_IN_WAVE = "audio_bot_aws.wav"  # WAV format Output file  name
NATIVE_LENGUAGE = "es"

# #######################
# ### INITIAL MESSAGE ###
# #######################

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

PATH_TO_DATA = "Conversations/" + subject_id + "_" + str(init_of_session)
os.mkdir(PATH_TO_DATA)
os.mkdir(PATH_TO_DATA + "/Audios")
WAVE_OUTPUT_FILENAME = PATH_TO_DATA + "/Audios/Subject_" + subject_id

# SubjectName
print("Please write your name")
subject_name = input()

bot_result_list = []
ct_voice_id = 0
try:
    while True:
        t_str_start, t_unix_start, _ = ute.get_current_time()
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
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                print("*** Done recording ***")

                stream.stop_stream()
                stream.close()
                p.terminate()

                wf = wave.open(WAVE_OUTPUT_FILENAME + "_T=" + str(ct_voice_id) + ".wav", 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()

                r = sr.Recognizer()
                with sr.AudioFile(WAVE_OUTPUT_FILENAME + "_T=" + str(ct_voice_id) + ".wav") as source:
                    audio = r.record(source)

                spanish_text = r.recognize_google(audio, language=NATIVE_LENGUAGE + "-EU")
                ct_voice_id += 1

            elif CHAT_MODE == "write":
                print("Write something....")
                spanish_text = input()
                print("* done recording")

            else:
                print("Please select between 'write' or 'voice' method")
                break

            print("Your input message", spanish_text)

        else:
            spanish_text = initial_message

        t_str_end, t_unix_end, _ = ute.get_current_time()

        # ###################
        # ### TRANSLATION ###
        # ###################
        # Here the message is translated from spanish to english.
        x = google_translator.translate(spanish_text)
        person_message = x.text
        global_message += human_start_sequence + " " + person_message

        bot_result_list.append({
            "SubjectId": subject_id,
            "SubjectName": subject_name,
            "TimeInitStr": t_str_start,
            "TimeEndStr": t_str_end,
            "UnixTimestampInit": t_unix_start,
            "UnixTimestampEnd": t_unix_end,
            "Source": "Person",
            "SpanishMessage": spanish_text,
            "EnglishMessage": person_message,
            "Mode": CHAT_MODE,
        })
        df_to_save = pd.DataFrame(bot_result_list)
        df_to_save.to_excel(PATH_TO_DATA + "/Conv_" + str(init_of_session) + ".xlsx", index=False)

        # ###########
        # ### BOT ###
        # ###########

        t_str_start, t_unix_start, _ = ute.get_current_time()

        # t0 = time.time()

        response = openai.Completion.create(
            engine="davinci",
            prompt=global_message,
            temperature=0.9,
            max_tokens=INITIAL_TOKENS_OPENAI,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=["Human:"]
        )
        bot_answer = response["choices"][0]["text"]
        bot_message = bot_answer.replace("Yolo:", "") if "Yolo:" in bot_answer else bot_answer
        # print("Time of the answer", np.round(time.time() - t0, 5), "s")

        global_message += bot_start_sequence + " " + bot_message

        t_str_end, t_unix_end, _ = ute.get_current_time()

        # ###################
        # ### TRANSLATION ###
        # ###################
        # Here the message is translated from english to spanish.

        x = google_translator.translate(bot_message, dest=NATIVE_LENGUAGE)
        bot_message_spanish = x.text

        bot_result_list.append({
            "SubjectId": subject_id,
            "SubjectName": subject_name,
            "TimeInitStr": t_str_start,
            "TimeEndStr": t_str_end,
            "UnixTimestampInit": t_unix_start,
            "UnixTimestampEnd": t_unix_end,
            "Source": "Bot",
            "SpanishMessage": spanish_text,
            "EnglishMessage": person_message,
            "Mode": CHAT_MODE,
        })

        df_to_save = pd.DataFrame(bot_result_list)
        df_to_save.to_excel(PATH_TO_DATA + "/Conv_" + str(init_of_session) + ".xlsx", index=False)

        print("Bot message", bot_message_spanish)

        # #################
        # ### USING AWS ###
        # #################
        RATE = 16000  # Polly supports 16000Hz and 8000Hz output for PCM format
        response = polly.synthesize_speech(
            Text=bot_message_spanish,
            OutputFormat="pcm",
            VoiceId="Lucia",
            SampleRate=str(RATE),
            Engine="neural"
        )

        # Initializing variables
        CHANNELS = 1  # Polly's output is a mono audio stream
        WAV_SAMPLE_WIDTH_BYTES = 2  # Polly's output is a stream of 16-bits (2 bytes) samples
        FRAMES = []

        # Processing the response to audio stream
        STREAM = response.get("AudioStream")
        FRAMES.append(STREAM.read())

        WAVE_FORMAT = wave.open(ROOT_TO_OMNIVERSE + "/" + OUTPUT_FILE_IN_WAVE, 'wb')
        WAVE_FORMAT.setnchannels(CHANNELS)
        WAVE_FORMAT.setsampwidth(WAV_SAMPLE_WIDTH_BYTES)
        WAVE_FORMAT.setframerate(RATE)
        WAVE_FORMAT.writeframes(b''.join(FRAMES))
        WAVE_FORMAT.close()

        # #################
        # ### OMNIVERSE ###
        # #################
        call_to_omniverse = " python " + ROOT_TO_OMNIVERSE + "/my_test_client.py "

        call_to_omniverse += " " + ROOT_TO_OMNIVERSE + AUDIO_NAME + " " + OMNIVERSE_AVATAR
        print(call_to_omniverse)
        subprocess.call(call_to_omniverse, shell=True)

except KeyboardInterrupt:
    pass
