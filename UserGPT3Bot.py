import pandas as pd
import numpy as np
import subprocess
import wave
import time
import pyaudio
import os
import json
# import sys
# import random
# import pyttsx3

# import speech_recognition as sr
import openai
from transformers import pipeline
# from contextlib import closing
# from pydub import AudioSegment
from google.cloud import speech

from googletrans import Translator

from boto3 import Session
# from botocore.exceptions import BotoCoreError, ClientError
# from tempfile import gettempdir

from pyannote.audio.pipelines import VoiceActivityDetection

from tkinter import *

from Interface import Interface
import utils as ute
from ChatbotGlobals import LableniChatbot

# ######################################
# ### Opening PARAMETERS CONFIG file ###
# ######################################

# ### Interface ###

root = Tk()
root.title("LabLeni BOT")
root.geometry("400x400")

app = Interface(master=root)

app.mainloop()

print(app.bot_config)

subject_id = app.subject_id
print("Subject ID", subject_id)

subject_name = app.subject_name
print("Subject Name", subject_name)

# ### End of the Interface ###

bot_txt, bot_state = app.bot_config.split(" ; ")
bot_txt_to_root, bot_state_to_root = bot_txt.replace(" ", "_"), bot_state.replace(" ", "_")

root_to_parameters = "LableniBotConfig/Parameters/" + bot_txt_to_root + "/" + bot_state_to_root + ".json"

with open(root_to_parameters, "r", encoding='utf-8') as read_file:
    parameters_dict = json.load(read_file)

SUMMARIZE_MODULE = parameters_dict["SUMMARIZE_MODULE"]
TRANSLATION_MODULE = parameters_dict["TRANSLATION_MODULE"]
OMNIVERSE_MODULE = parameters_dict["OMNIVERSE_MODULE"]

CONFIG_NAME = parameters_dict["CONFIG_NAME"]
INITIAL_TOKENS_OPENAI = parameters_dict["INITIAL_TOKENS_OPENAI"]
BOT_VOICE_ID = parameters_dict["BOT_VOICE_ID"]
ENGINE_TYPE = parameters_dict["ENGINE_TYPE"]

BOT_MODEL = parameters_dict["BOT_MODEL"]
BOT_TEMPERATURE = parameters_dict["BOT_TEMPERATURE"]
BOT_FREQUENCY_PENALTY = parameters_dict["BOT_FREQUENCY_PENALTY"]
BOT_PRESENCE_PENALTY = parameters_dict["BOT_PRESENCE_PENALTY"]

# ### Initial message to de chatbot

BOT_NAME = parameters_dict["BOT_NAME"]
BOT_START_SEQUENCE = BOT_NAME + ":"

HUMAN_NAME = parameters_dict["HUMAN_NAME"]
HUMAN_START_SEQUENCE = HUMAN_NAME + ":"

CONTEXT_MESSAGE = parameters_dict["CONTEXT_MESSAGE"]
INITIAL_MESSAGE = parameters_dict["INITIAL_MESSAGE"]
counter = 0

GLOBAL_MESSAGE = CONTEXT_MESSAGE + "\n"

# ###########################
# ### Opening CONFIG file ###
# ###########################

config_json = open("LableniBotConfig/config.json")
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

# if TRANSLATION_MODULE:
# Initialize the translator model
google_translator = Translator()

# ################################
# ### SUMMARIZATION PARAMETERS ###
# ################################

if SUMMARIZE_MODULE:
    summarizer_model = pipeline("summarization", model="facebook/bart-large-cnn")
    keep_last_summarizer = 4

# ########################
# ### RANDOM QUESTIONS ###
# ########################

with open("LableniBotConfig/RandomQuestions.txt", "r", encoding='utf-8') as txt:
    RANDOM_QUESTIONS = txt.readlines()
RANDOM_QUESTIONS = [q.replace("\n", "") for q in RANDOM_QUESTIONS]

# #################
# ### CONSTANTS ###
# #################

# Begin of the session
_, _, init_of_session = ute.get_current_time()

OUTPUT_FILE_IN_WAVE = "audio_bot_aws.wav"  # WAV format Output file  name
NATIVE_LENGUAGE = "es" # TODO: Put the parameter in the config or in the interface.

# Modes avaible: 'voice' or 'write'.
CHAT_MODE = "voice" # TODO: Put the parameter in the interface.

# Time to wait until ask the user to repeat.
waitTime = 15
# Audio record parameters.
CHUNK = parameters_dict["CHUNK"]
FORMAT = pyaudio.paInt16
CHANNELS = parameters_dict["CHANNELS"]
RATE = parameters_dict["RATE"]
RECORD_SECONDS = parameters_dict["RECORD_SECONDS"]
TIME_TO_CUT = parameters_dict["TIME_TO_CUT"]

# ########################
# ### OMNIVERSE MODULE ###
# ########################

if OMNIVERSE_MODULE:
    ROOT_TO_OMNIVERSE = config_dict["ROOT_TO_OMNIVERSE"]
    OMNIVERSE_AVATAR = parameters_dict["OMNIVERSE_AVATAR"]

# ##############
# ### INPUTS ###
# ##############

PATH_TO_DATA = "Conversations/" + subject_id + "_" + str(init_of_session)
os.mkdir(PATH_TO_DATA)
os.mkdir(PATH_TO_DATA + "/Audios")
WAVE_OUTPUT_FILENAME = PATH_TO_DATA + "/Audios/Subject_" + subject_id

# ###################################
# ### DEFINE OF THE CLASS CHATBOT ###
#####################################

my_chatbot = LableniChatbot(
    subject_id = subject_id,
    subject_name = subject_name, 
    mode_chat = CHAT_MODE, 
    config_name = CONFIG_NAME,
    path_to_save=PATH_TO_DATA + "/Conv_" + str(init_of_session)
)

bot_result_list = []
ct_voice_id = 0
spanish_text = " "
# random_question_label  = False
repeat_message_label = False
try:
    while True:

        # ###########
        # ### BOT ###
        # ###########

        t_str_start, t_unix_start, _ = ute.get_current_time()

        if spanish_text is not None and not repeat_message_label:
            # if counter > 0 and not random_question_label:
            if counter > 0:

                t_i_openai = time.time()

                response = openai.Completion.create(
                    engine=BOT_MODEL,
                    prompt=GLOBAL_MESSAGE,
                    temperature=BOT_TEMPERATURE,
                    max_tokens=INITIAL_TOKENS_OPENAI,
                    top_p=1,
                    frequency_penalty=BOT_FREQUENCY_PENALTY,
                    presence_penalty=BOT_PRESENCE_PENALTY,
                    stop=["Humano:", "Human:", subject_name + ":"]
                )

                t_f_openai = time.time()

                bot_answer = response["choices"][0]["text"]
                bot_answer = ":".join(bot_answer.split(":")[:2]) if len(bot_answer.split(":")) > 2 else bot_answer
                    
            # elif random_question_label:
            #     t_i_openai = time.time()
            #     bot_answer = BOT_START_SEQUENCE + " " + my_chatbot.sentence_to_repeat
            #     t_f_openai = time.time()
                # bot_answer = random.choices(RANDOM_QUESTIONS)[0]
                # RANDOM_QUESTIONS = RANDOM_QUESTIONS.remove(bot_answer)
            #     random_question_label = False
            else:
                t_i_openai = time.time()
                bot_answer = BOT_START_SEQUENCE + " " + INITIAL_MESSAGE
                t_f_openai = time.time()
        else:
            t_i_openai = time.time()
            bot_answer = BOT_START_SEQUENCE + " " + my_chatbot.sentence_to_repeat
            t_f_openai = time.time()
            repeat_message_label = False

        bot_message = bot_answer.replace(BOT_NAME + ":", "") if BOT_NAME + ":" in bot_answer else bot_answer
        bot_message = bot_message.replace("\n", "") if "\n" in bot_message else bot_message
        # bot_message = bot_message[1:] if bot_message[0] == " " else bot_message

        if len(bot_message) <= 2 or bot_message == "?" or bot_message == "!":
            bot_message = BOT_START_SEQUENCE + " " + my_chatbot.sentence_to_repeat

        bot_message = bot_message if bot_message[-1] in [".", "?", "!"] else bot_message + "."
        detect_language = google_translator.detect(bot_message)
        if detect_language.lang != "es":
            x = google_translator.translate(bot_message, dest=NATIVE_LENGUAGE)
            bot_message_filtered = x.text
        else:
            bot_message_filtered = bot_message

        # GLOBAL_MESSAGE += "\n" + BOT_START_SEQUENCE + " " + bot_message_filtered
        GLOBAL_MESSAGE += bot_message_filtered
        print("*** Global message *** \n", GLOBAL_MESSAGE)

        t_str_end, t_unix_end, _ = ute.get_current_time()

        # #################
        # ### SAVE DATA ###
        # #################

        '''
        # TODO: Put all this saves in the ChatbotGlobals.py script.
        bot_result_list.append({
            "SubjectId": subject_id,
            "ConversationSentenceId": counter,
            "SubjectName": subject_name,
            "TimeInitStr": t_str_start,
            "TimeEndStr": t_str_end,
            "UnixTimestampInit": t_unix_start,
            "UnixTimestampEnd": t_unix_end,
            "Source": "Bot",
            "SpanishMessage": bot_message_filtered,
            # "EnglishMessage": person_message,
            "Mode": CHAT_MODE,
            "GlobalMessage": GLOBAL_MESSAGE,
            "ConfigName": CONFIG_NAME,
            "OpenAItime_s": (t_f_openai - t_i_openai),
            "AWStime_s": np.nan,
            "S2Ttime_s": np.nan
        })
        '''

        my_chatbot.save_data(
            counter = counter,
            t_str_start = t_str_start, t_str_end = t_str_end, t_unix_start = t_unix_start, t_unix_end = t_unix_end, 
            source = "Bot", 
            source_message = bot_message_filtered, 
            global_message = GLOBAL_MESSAGE, 
            openai_time_s = (t_f_openai - t_i_openai), aws_time_s = np.nan, s2t_time_s = np.nan
        )

        # df_to_save = pd.DataFrame(bot_result_list)
        # df_to_save.to_excel(PATH_TO_DATA + "/Conv_" + str(init_of_session) + ".xlsx", index=False)

        # #################
        # ### USING AWS ###
        # #################

        t_i_aws = time.time()

        # Message string transform to AWS Polly PCM format. 
        bot_message_spanish_aws = ute.from_str_to_was_polly_pcm(bot_message_filtered)

        RATE = 16000  # Polly supports 16000Hz and 8000Hz output for PCM format
        response = polly.synthesize_speech(
            Text=bot_message_spanish_aws,
            OutputFormat="pcm",
            VoiceId=BOT_VOICE_ID,
            # SampleRate=str(RATE),
            Engine=ENGINE_TYPE,
            TextType="ssml"
        )

        t_f_aws = time.time()

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
            # print(call_to_omniverse)
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

        # #############
        # ### HUMAN ###
        # #############

        t_str_start, t_unix_start, _ = ute.get_current_time()

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
                        cond_listen = (time.time() - t0_start_talk) > 5
                        if time.time() - (last_time_talk + t0_start_talk) > TIME_TO_CUT and cond_listen:
                            break
                        else:
                            silence_th += len(x) - 1

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

            t_i_s2t = time.time()

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

            t_f_s2t = time.time()

            if len(response.results) > 0:
                repeat_message_label = False
                spanish_text = response.results[0].alternatives[0].transcript

                vad = silence_detection_pipeline(WAVE_OUTPUT_FILENAME + "_T=" + str(ct_voice_id) + ".wav")
                x = vad.get_timeline().segments_set_
                time_start_talking = list(x)[0].start

                # if time_start_talking > 3.5 and (t0 - t0_start_talk) - time_start_talking <= 1:
                #     random_question_label = True
            else:
                spanish_text = " "
                repeat_message_label = True

            # spanish_text = r.recognize_google(audio, language=NATIVE_LENGUAGE + "-EU")
            ct_voice_id += 1

        elif CHAT_MODE == "write":
            print("Write something....")
            t_i_s2t = time.time()
            spanish_text = input()
            t_f_s2t = time.time()
        else:
            t_f_s2t, t_i_s2t = 0, 0
            print("Please select between 'write' or 'voice' method")
            break

        t_str_end, t_unix_end, _ = ute.get_current_time()

        # ###################
        # ### TRANSLATION ###
        # ###################

        if TRANSLATION_MODULE:
            # Here the message is translated from spanish to english.
            x = google_translator.translate(spanish_text)
            person_message = x.text + " ."
        else:
            person_message = spanish_text

        person_message = person_message if person_message[-1] in [".", "?", "!"] else person_message + "."
        GLOBAL_MESSAGE += "\n" + HUMAN_START_SEQUENCE + " " + person_message
        print("*** Global message *** \n", GLOBAL_MESSAGE)

        # To start the message with Bot sequence.
        GLOBAL_MESSAGE += "\n" + BOT_START_SEQUENCE

        '''
        bot_result_list.append({
            "SubjectId": subject_id,
            "ConversationSentenceId": counter,
            "SubjectName": subject_name,
            "TimeInitStr": t_str_start,
            "TimeEndStr": t_str_end,
            "UnixTimestampInit": t_unix_start,
            "UnixTimestampEnd": t_unix_end,
            "Source": "Person",
            "SpanishMessage": spanish_text,
            # "EnglishMessage": person_message,
            "Mode": CHAT_MODE,
            "GlobalMessage": GLOBAL_MESSAGE,
            "ConfigName": CONFIG_NAME,
            "OpenAItime_s": np.nan,
            "AWStime_s": (t_f_aws - t_i_aws),
            "S2Ttime_s": (t_f_s2t - t_i_s2t),
        })
        '''

        my_chatbot.save_data(
            counter = counter,
            t_str_start = t_str_start, t_str_end = t_str_end, t_unix_start = t_unix_start, t_unix_end = t_unix_end, 
            source = "Person", 
            source_message = spanish_text, 
            global_message = GLOBAL_MESSAGE, 
            openai_time_s = np.nan, aws_time_s = (t_f_aws - t_i_aws), s2t_time_s = (t_f_s2t - t_i_s2t)
        )
        
        df_to_save = pd.DataFrame(bot_result_list)
        # df_to_save.to_excel(PATH_TO_DATA + "/Conv_" + str(init_of_session) + ".xlsx", index=False)

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
                    GLOBAL_MESSAGE = CONTEXT_MESSAGE + " " + whole_answer + " " + whole_text_small

        counter += 1

        if person_message == "Adiós" or person_message == "Hasta luego" or person_message == "Adios":
            break

except KeyboardInterrupt:
    pass
