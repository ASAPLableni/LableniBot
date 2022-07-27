import pandas as pd
import numpy as np
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
from transformers import pipeline

from googletrans import Translator

from boto3 import Session
# from botocore.exceptions import BotoCoreError, ClientError
# from contextlib import closing
# from tempfile import gettempdir

from pyannote.audio.pipelines import VoiceActivityDetection

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
INITIAL_TOKENS_OPENAI = 150

summarizer_model = pipeline("summarization", model="facebook/bart-large-cnn")
keep_last_summarizer = 3
summarize_module = True

# ### Some parameters ###
# Time to wait until ask the user to repeat.
waitTime = 15
# Audio record parameters. 
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 30

# #################
# ### CONSTANTS ###
# #################

# Begin of the session
_, _, init_of_session = ute.get_current_time()

ROOT_TO_OMNIVERSE = config_dict["ROOT_TO_OMNIVERSE"]
AUDIO_NAME = "/audio_bot_aws.wav"
OMNIVERSE_AVATAR = "/World/audio_player_streaming"  # "/audio2face/player_instance"
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
CHAT_MODE = "voice"

silence_detection_pipeline = VoiceActivityDetection(segmentation="pyannote/segmentation")
HYPER_PARAMETERS = {
    # onset/offset activation thresholds
    "onset": 0.5, "offset": 0.5,
    # remove speech regions shorter than that many seconds.
    "min_duration_on": 0.0,
    # fill non-speech regions shorter than that many seconds.
    "min_duration_off": 0.0
}
silence_detection_pipeline.instantiate(HYPER_PARAMETERS)

# ###############################
# ### INITIAL MESSAGE TO GPT3 ###
# ###############################

bot_start_sequence = "Maria:"
human_start_sequence = "Human: "

global_message = '''
The following is a conversation with Maria. Maria is helpful, creative, clever, and very friendly woman. Maria always 
wants to ask questions to other people to talk a lot with them. 
Human: Hello, who are you ?
Maria: I am fine, thanks to ask.
'''

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

TIME_TO_CUT = 1.5

bot_result_list = []
ct_voice_id = 0
try:
    while True:
        t_str_start, t_unix_start, _ = ute.get_current_time()
        if counter > 0:
            if CHAT_MODE == "voice":

                t0 = time.time()
                t0_start_talk = time.time()
                silence_th = 0

                p = pyaudio.PyAudio()
                stream = p.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK)

                print("*** Recording ***")
                frames = []
                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK)  # , exception_on_overflow=False
                    frames.append(data)

                    # Silence Detection module
                    if time.time() - t0 > 3:

                        # print("Hola", time.time() - t0_start_talk)

                        wf = wave.open(WAVE_OUTPUT_FILENAME + "_T=" + str(ct_voice_id) + ".wav", 'wb')
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(p.get_sample_size(FORMAT))
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames))
                        wf.close()

                        vad = silence_detection_pipeline(WAVE_OUTPUT_FILENAME + "_T=" + str(ct_voice_id) + ".wav")

                        x = vad.get_timeline().segments_set_

                        if len(x) > 0:
                            last_time_talk = np.max([x_elt.end for x_elt in list(x)])
                            if time.time() - (last_time_talk + t0_start_talk) > TIME_TO_CUT:
                                break
                            else:
                                silence_th += len(x) - 1
                                # silence_th = len(x)

                        t0 = time.time()

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

        counter += 1

        t_str_end, t_unix_end, _ = ute.get_current_time()

        # ###################
        # ### TRANSLATION ###
        # ###################
        # Here the message is translated from spanish to english.
        x = google_translator.translate(spanish_text)
        person_message = x.text
        global_message += human_start_sequence + " " + person_message

        print("*** Global message *** ", global_message)

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
            "Summary": ""
        })
        df_to_save = pd.DataFrame(bot_result_list)
        df_to_save.to_excel(PATH_TO_DATA + "/Conv_" + str(init_of_session) + ".xlsx", index=False)

        # ##################
        # ### SUMMARIZER ###
        # ##################

        if summarize_module:
            n_data = df_to_save.shape[0]
            if n_data >= keep_last_summarizer + 2:

                df_cut = df_to_save.iloc[:(n_data - keep_last_summarizer)]
                df_small = df_to_save.iloc[(n_data - keep_last_summarizer):]

                all_text_paired = list(zip(df_cut["Source"].values, df_cut["EnglishMessage"].values))
                text_list = [": ".join(text) for text in all_text_paired]
                whole_text = " ".join(text_list)

                if len(whole_text.split()) > 50:
                    answer = summarizer_model(whole_text, max_length=60, min_length=10)
                    whole_answer = answer[0]["summary_text"]
                    print("Summary model ...")

                    all_text_paired = list(zip(df_small["Source"].values, df_small["EnglishMessage"].values))
                    text_list = [": ".join(text) for text in all_text_paired]
                    whole_text_small = " ".join(text_list)

                    print("*** Summary ***", whole_answer + " " + whole_text_small)
                    global_message = whole_answer + " " + whole_text_small

        # ###########
        # ### BOT ###
        # ###########

        t_str_start, t_unix_start, _ = ute.get_current_time()
        # t0 = time.time()
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=global_message,
            temperature=0.9,
            max_tokens=INITIAL_TOKENS_OPENAI,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=["Human:", "Person:", "Subject:"]
        )
        bot_answer = response["choices"][0]["text"]
        # bot_answer = "Maria: Hello man, how are you ?"
        bot_message = bot_answer.replace("Maria:", "") if "Maria:" in bot_answer else bot_answer
        bot_message = bot_message.replace("Bot:", "") if "Bot:" in bot_message else bot_message
        # print("Time of the answer", np.round(time.time() - t0, 5), "s")

        if len(bot_message) < 3 or bot_message == "?" or bot_message == "!":
            bot_message = "Can you repeat, please ?"

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
            "Summary": ""
        })

        df_to_save = pd.DataFrame(bot_result_list)
        df_to_save.to_excel(PATH_TO_DATA + "/Conv_" + str(init_of_session) + ".xlsx", index=False)

        print("Bot message", bot_message_spanish)

        # #################
        # ### USING AWS ###
        # #################
        bot_message_spanish_aws = bot_message_spanish
        bot_message_spanish_aws = bot_message_spanish_aws.replace('.', '<break time="1s"/>')
        bot_message_spanish_aws = bot_message_spanish_aws.replace(',', '<break time="0.5s"/>')
        bot_message_spanish_aws = "<speak>"+bot_message_spanish_aws+"</speak>"
        RATE = 16000  # Polly supports 16000Hz and 8000Hz output for PCM format
        response = polly.synthesize_speech(
            Text=bot_message_spanish,
            OutputFormat="pcm",
            VoiceId="Lucia",
            SampleRate=str(RATE),
            Engine="neural",
            TextType="ssml"
        )

        # Initializing variables
        CHANNELS = 1  # Polly's output is a mono audio stream
        WAV_SAMPLE_WIDTH_BYTES = 2  # Polly's output is a stream of 16-bits (2 bytes) samples
        FRAMES = []

        # Processing the response to audio stream
        STREAM = response.get("AudioStream")
        FRAMES.append(STREAM.read())

        WAVE_FORMAT = wave.open(ROOT_TO_OMNIVERSE + "/" + OUTPUT_FILE_IN_WAVE, 'wb')
        # WAVE_FORMAT = wave.open(OUTPUT_FILE_IN_WAVE, 'wb')
        WAVE_FORMAT.setnchannels(CHANNELS)
        WAVE_FORMAT.setsampwidth(WAV_SAMPLE_WIDTH_BYTES)
        WAVE_FORMAT.setframerate(RATE)
        WAVE_FORMAT.writeframes(b''.join(FRAMES))
        WAVE_FORMAT.close()

        '''
        # open a wav format music
        f = wave.open(OUTPUT_FILE_IN_WAVE, "rb")
        # instantiate PyAudio
        p = pyaudio.PyAudio()
        # open stream
        stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True)
        # read data
        data = f.readframes(CHUNK)

        # play stream
        while data:
            stream.write(data)
            data = f.readframes(CHUNK)

            # stop stream
        stream.stop_stream()
        stream.close()

        # close PyAudio
        p.terminate()
        '''

        # #################
        # ### OMNIVERSE ###
        # #################

        call_to_omniverse = " python " + ROOT_TO_OMNIVERSE + "/my_test_client.py "

        call_to_omniverse += " " + ROOT_TO_OMNIVERSE + AUDIO_NAME + " " + OMNIVERSE_AVATAR
        print(call_to_omniverse)
        subprocess.call(call_to_omniverse, shell=True)


except KeyboardInterrupt:
    pass
