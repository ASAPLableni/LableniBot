import pandas as pd
import numpy as np
import subprocess
import wave
import time
import os
import pyaudio
import json
# import pyttsx3
# import sys
# import speech_recognition as sr
import openai
from transformers import pipeline
from contextlib import closing
from pydub import AudioSegment
from google.cloud import speech

from googletrans import Translator

from boto3 import Session
# from botocore.exceptions import BotoCoreError, ClientError
# from tempfile import gettempdir

from pyannote.audio.pipelines import VoiceActivityDetection

import utils as ute

# ######################################
# ### Opening PARAMETERS CONFIG file ###
# ######################################

with open("parameters.json", "r", encoding='utf-8') as read_file:
    parameters_dict = json.load(read_file)

SUMMARIZE_MODULE = parameters_dict["SUMMARIZE_MODULE"]
TRANSLATION_MODULE = parameters_dict["TRANSLATION_MODULE"]
OMNIVERSE_MODULE = parameters_dict["OMNIVERSE_MODULE"]

INITIAL_TOKENS_OPENAI = parameters_dict["INITIAL_TOKENS_OPENAI"]

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

# ###########################
# ### Opening GOOGLE file ###
# ###########################

GOOGLE_ROOT = config_dict["GOOGLE_ROOT"]
google_client = speech.SpeechClient.from_service_account_json(GOOGLE_ROOT)

# ###############################
# ### SILENCE DETECTION MODEL ###
# ###############################

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

# ##########################
# ### TRANSLATION MODULE ###
# ##########################

if TRANSLATION_MODULE:
    # Initialize the translator model
    google_translator = Translator()

# ################################
# ### SUMMARIZATION PARAMETERS ###
# ################################

if SUMMARIZE_MODULE:
    summarizer_model = pipeline("summarization", model="facebook/bart-large-cnn")
    keep_last_summarizer = 4

# #################
# ### CONSTANTS ###
# #################

# Begin of the session
_, _, init_of_session = ute.get_current_time()

AUDIO_NAME = "/audio_bot_aws.wav"
OUTPUT_FILE_IN_WAVE = "audio_bot_aws.wav"  # WAV format Output file  name
NATIVE_LENGUAGE = "es"

# Modes avaible: 'voice' or 'write'.
CHAT_MODE = "voice"

# Time to wait until ask the user to repeat.
waitTime = 15
# Audio record parameters.
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 30

# ########################
# ### OMNIVERSE MODULE ###
# ########################

if OMNIVERSE_MODULE:
    ROOT_TO_OMNIVERSE = config_dict["ROOT_TO_OMNIVERSE"]
    OMNIVERSE_AVATAR = parameters_dict["OMNIVERSE_AVATAR"]

# ###############################
# ### INITIAL MESSAGE TO GPT3 ###
# ###############################

BOT_NAME = parameters_dict["BOT_NAME"]
BOT_START_SEQUENCE = BOT_NAME + ": "

HUMAN_NAME = parameters_dict["HUMAN_NAME"]
HUMAN_START_SEQUENCE = HUMAN_NAME + ": "

CONTEXT_MESSAGE = parameters_dict["CONTEXT_MESSAGE"]
INITIAL_MESSAGE = parameters_dict["INITIAL_MESSAGE"]
counter = 0

global_message = CONTEXT_MESSAGE + "\n"

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

TIME_TO_CUT = parameters_dict["TIME_TO_CUT"]

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

                # r = sr.Recognizer()
                # with sr.AudioFile(WAVE_OUTPUT_FILENAME + "_T=" + str(ct_voice_id) + ".wav") as source:
                #     audio = r.record(source)

                speech_file = WAVE_OUTPUT_FILENAME + "_T=" + str(ct_voice_id) + ".wav"
                with open(speech_file, "rb") as audio_file:
                    content = audio_file.read()

                audio = speech.RecognitionAudio(content=content)
                google_config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    # sample_rate_hertz=44100,
                    language_code=NATIVE_LENGUAGE + "-EU",
                    audio_channel_count=2,
                    enable_separate_recognition_per_channel=True,
                    enable_automatic_punctuation=True
                )
                response = google_client.recognize(config=google_config, audio=audio)
                spanish_text = response.results[0].alternatives[0].transcript

                # spanish_text = r.recognize_google(audio, language=NATIVE_LENGUAGE + "-EU")
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
            spanish_text = INITIAL_MESSAGE

        counter += 1

        t_str_end, t_unix_end, _ = ute.get_current_time()

        # ###################
        # ### TRANSLATION ###
        # ###################
        if TRANSLATION_MODULE:
            # Here the message is translated from spanish to english.
            x = google_translator.translate(spanish_text)
            person_message = x.text + " .\n"
            global_message += HUMAN_START_SEQUENCE + " " + person_message
        else:
            global_message += HUMAN_START_SEQUENCE + " " + spanish_text + " .\n"

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
            # "EnglishMessage": person_message,
            "Mode": CHAT_MODE,
            "GlobalMessage": global_message,
        })
        df_to_save = pd.DataFrame(bot_result_list)
        df_to_save.to_excel(PATH_TO_DATA + "/Conv_" + str(init_of_session) + ".xlsx", index=False)

        # ##################
        # ### SUMMARIZER ###
        # ##################

        if SUMMARIZE_MODULE:
            n_data = df_to_save.shape[0]
            if n_data >= 8:

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
                    global_message = CONTEXT_MESSAGE + " " + whole_answer + " " + whole_text_small

        # ###########
        # ### BOT ###
        # ###########

        t_str_start, t_unix_start, _ = ute.get_current_time()
        # t0 = time.time()

        global_message += " " + BOT_START_SEQUENCE + " "

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=global_message,
            temperature=0.9,
            max_tokens=INITIAL_TOKENS_OPENAI,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.9,
            stop=["Human:", "Person:", "Subject:", "AI:"]
        )
        bot_answer = response["choices"][0]["text"]
        print("Bot answer", bot_answer)

        # bot_answer = "Maria: Hola, que tal estas ?"
        bot_message = bot_answer.replace("Maria:", "") if "Maria:" in bot_answer else bot_answer
        bot_message = bot_message.replace("Bot:", "") if "Bot:" in bot_message else bot_message
        # print("Time of the answer", np.round(time.time() - t0, 5), "s")

        if len(bot_message) < 2 or bot_message == "?" or bot_message == "!":
            bot_message = "Can you repeat, please ?"

        global_message += BOT_START_SEQUENCE + " " + bot_message

        t_str_end, t_unix_end, _ = ute.get_current_time()

        # ###################
        # ### TRANSLATION ###
        # ###################

        if TRANSLATION_MODULE:
            # Here the message is translated from english to spanish.
            x = google_translator.translate(bot_message, dest=NATIVE_LENGUAGE)
            bot_message_spanish = x.text
        else:
            bot_message_spanish = bot_message

        bot_result_list.append({
            "SubjectId": subject_id,
            "SubjectName": subject_name,
            "TimeInitStr": t_str_start,
            "TimeEndStr": t_str_end,
            "UnixTimestampInit": t_unix_start,
            "UnixTimestampEnd": t_unix_end,
            "Source": "Bot",
            "SpanishMessage": bot_message_spanish,
            # "EnglishMessage": person_message,
            "Mode": CHAT_MODE,
            "GlobalMessage": global_message,
        })

        df_to_save = pd.DataFrame(bot_result_list)
        df_to_save.to_excel(PATH_TO_DATA + "/Conv_" + str(init_of_session) + ".xlsx", index=False)

        print("Bot message", bot_message_spanish)

        # #################
        # ### USING AWS ###
        # #################
        bot_message_spanish_aws = bot_message_spanish
        bot_message_spanish_aws = bot_message_spanish_aws.replace("?", ".").replace("¿", ".")
        bot_message_spanish_aws = bot_message_spanish_aws.replace('.', '<break time="0.6s"/>')
        bot_message_spanish_aws = bot_message_spanish_aws.replace(',', '<break time="0.25s"/>')
        bot_message_spanish_aws = "<speak>" + bot_message_spanish_aws + "</speak>"
        RATE = 16000  # Polly supports 16000Hz and 8000Hz output for PCM format
        response = polly.synthesize_speech(
            Text=bot_message_spanish_aws,
            OutputFormat="pcm",  # "pcm",
            VoiceId='Lucia',  # "Lucia",
            # SampleRate=str(RATE),
            Engine="neural",
            TextType="ssml"
        )

        '''
        with closing(response["AudioStream"]) as save_stream:
            # output = os.path.join(gettempdir(), "speech.mp3")
            with open(OUTPUT_FILE_IN_WAVE.replace(".wav", ".mp3"), "wb") as file:
                file.write(save_stream.read())

        # convert .mp3 to .wav
        sound = AudioSegment.from_mp3(OUTPUT_FILE_IN_WAVE.replace(".wav", ".mp3"))
        sound.export(OUTPUT_FILE_IN_WAVE, format="wav")
        '''

        # #################
        # ### OMNIVERSE ###
        # #################
        if OMNIVERSE_MODULE:

            # Initializing variables
            OMNI_CHANNELS = 1  # Polly's output is a mono audio stream
            WAV_SAMPLE_WIDTH_BYTES = 2  # Polly's output is a stream of 16-bits (2 bytes) samples
            FRAMES = []

            # Processing the response to audio stream
            STREAM = response.get("AudioStream")
            FRAMES.append(STREAM.read())

            WAVE_FORMAT = wave.open(ROOT_TO_OMNIVERSE + "/" + OUTPUT_FILE_IN_WAVE, 'wb')
            WAVE_FORMAT.setnchannels(OMNI_CHANNELS)
            WAVE_FORMAT.setsampwidth(WAV_SAMPLE_WIDTH_BYTES)
            WAVE_FORMAT.setframerate(RATE)
            WAVE_FORMAT.writeframes(b''.join(FRAMES))
            WAVE_FORMAT.close()

            # OMNIVERSE_AVATAR = "/Woman/audio_player_streaming"
            call_to_omniverse = " python " + ROOT_TO_OMNIVERSE + "/my_test_client.py "
            call_to_omniverse += " " + ROOT_TO_OMNIVERSE + "/" + OUTPUT_FILE_IN_WAVE + " " + OMNIVERSE_AVATAR
            # call_to_omniverse += " " + OUTPUT_FILE_IN_WAVE.replace(".wav", ".mp3") + " " + OMNIVERSE_AVATAR
            print(call_to_omniverse)
            subprocess.call(call_to_omniverse, shell=True)
        else:
            # Initializing variables
            OMNI_CHANNELS = 1  # Polly's output is a mono audio stream
            WAV_SAMPLE_WIDTH_BYTES = 2  # Polly's output is a stream of 16-bits (2 bytes) samples
            FRAMES = []

            # Processing the response to audio stream
            STREAM = response.get("AudioStream")
            FRAMES.append(STREAM.read())

            WAVE_FORMAT = wave.open(OUTPUT_FILE_IN_WAVE, 'wb')
            WAVE_FORMAT.setnchannels(OMNI_CHANNELS)
            WAVE_FORMAT.setsampwidth(WAV_SAMPLE_WIDTH_BYTES)
            WAVE_FORMAT.setframerate(RATE)
            WAVE_FORMAT.writeframes(b''.join(FRAMES))
            WAVE_FORMAT.close()

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

except KeyboardInterrupt:
    pass
