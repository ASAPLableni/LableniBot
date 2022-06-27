import pandas as pd
import subprocess
from datetime import datetime
import wave, time, os, pyaudio, pyttsx3, sys
import speech_recognition as sr

# from googletrans import Translator
from gtts import gTTS 
  
# This module is imported so that we can  
# play the converted audio 
import paho.mqtt.client as mqtt

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
from tempfile import gettempdir

import utils as ute

# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(
    aws_access_key_id="AKIA5253QQ44EM6O6P4Q", 
    aws_secret_access_key="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"
)
polly = session.client("polly", region_name='eu-west-1')

my_global_mssg = ''
# broker = "158.42.170.142"
broker = "127.0.0.1"
port = 1883
# Time to wait until ask the user to repeat.
waitTime = 15
# Audio record parameters. 
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 8

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("topic/bot_to_person")

def on_message(client, userdata, msg):
    
    #t = datetime.now()
    global my_global_mssg

    message = msg.payload.decode()
    my_global_mssg = message

    client.disconnect()
    client.loop_stop()

_, _, init_of_session = ute.get_current_time()

os.mkdir("Conversations/Audio/" + str(init_of_session))

# #################
# ### CONSTANTS ###
# #################

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

# Initial message 

initial_message = "Como te llamas?"
counter = 0

# Modes avaible: 'voice' or 'write'.
mode = "write"

bot_result_list = []

print("Please write your subject id")
subject_id = input()

print("Please write your name")
subject_name = input()

ct_voice_id = 0
try:
    while True:
        if counter > 0:

            if mode == "voice":

                p = pyaudio.PyAudio()

                stream = p.open(format=FORMAT,
	                            channels=CHANNELS,
	                            rate=RATE,
	                            input=True,
	                            frames_per_buffer=CHUNK)

                print("* recording")

                frames = []
                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK, exception_on_overflow = False)
                    frames.append(data)

                print("* done recording")

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

                spanish_text = r.recognize_google(audio, language="es-EU")
                ct_voice_id += 1

            elif mode == "write":

                print("Write something....")
                spanish_text = input()
                print("* done recording")

            else:
                print("Please select between 'write' or 'voice' method")

            print("Your spanish message", spanish_text)

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

        # translator = Translator()
        # x = translator.translate(spanish_text)
        # english_text = x.text
        # dict_bot["english_message"].append(english_text)

        df_to_save = pd.DataFrame(bot_result_list)

        df_to_save.to_excel("Conversations/Conv_"+str(init_of_session)+".xlsx", index=False)

        client = mqtt.Client()
        client.connect("127.0.0.1", 1883)
        client.publish("topic/person_to_bot", spanish_text)
        #client.disconnect()

        counter += 1

        print("message send")

        client = mqtt.Client()
        client.connect("127.0.0.1" , 1883)

        # client.loop_start()

        print( "Mensaje anterior:....", my_global_mssg )

        client.on_connect = on_connect
        client.on_message = on_message

        print( "Mensaje nuevo:....", my_global_mssg )

        # client.loop_forever()

        startTime = time.time()

        client.loop_start()
        while True:
            # client.loop()
            elapsedTime = time.time() - startTime
            if elapsedTime > waitTime or len(my_global_mssg) > 0:
                client.disconnect()
                client.loop_stop()
                break

        translate_msgg = "Por favor, repite" if len(my_global_mssg) <= 0 else my_global_mssg

        # translator = Translator()
        # print("Before translate", my_global_mssg_english)
        # x = translator.translate(my_global_mssg_english, dest='es')
        # translate_msgg = x.text
        # print("After translate", translate_msgg)

        t_str, t_unix, _ = ute.get_current_time()
        bot_result_list.append({
            "SubjectId": subject_id
            "SubjectName": subject_name,
            "TimeStr": t_str,
            "UnixTimestamp": t_unix,
            "Source": "Bot",
            "Message": translate_msgg,
            "Mode": mode
        })

        df_to_save = pd.DataFrame(bot_result_list)

        df_to_save.to_excel("Conversations/Conv_"+str(init_of_session)+".xlsx", index=False)

        print("Lo que la máquina va a decir", translate_msgg)

        # #################
        # ### USING AWS ###
        # #################

        RATE = 16000 # Polly supports 16000Hz and 8000Hz output for PCM format

        response = polly.synthesize_speech(
            Text=translate_msgg, 
            OutputFormat="pcm", 
            VoiceId="Lucia",
            SampleRate=str(RATE),
            Engine="neural"
        )
        
        #Initializing variables
        CHANNELS = 1 #Polly's output is a mono audio stream
        OUTPUT_FILE_IN_WAVE = "audio_bot_aws.wav" #WAV format Output file  name
        FRAMES = []
        WAV_SAMPLE_WIDTH_BYTES = 2 # Polly's output is a stream of 16-bits (2 bytes) samples

        #Processing the response to audio stream
        STREAM = response.get("AudioStream")
        FRAMES.append(STREAM.read())

        WAVEFORMAT = wave.open(ROOT_TO_OMNI + "/" + OUTPUT_FILE_IN_WAVE, 'wb')
        WAVEFORMAT.setnchannels(CHANNELS)
        WAVEFORMAT.setsampwidth(WAV_SAMPLE_WIDTH_BYTES)
        WAVEFORMAT.setframerate(RATE)
        WAVEFORMAT.writeframes(b''.join(FRAMES))
        WAVEFORMAT.close()

        '''
        engine = pyttsx3.init()

        engine.setProperty('rate', 120) 
        engine.setProperty('volume', 1) 

        # engine.say(translate_msgg)
        # We can use file extension as mp3 and wav, both will work
        # engine.save_to_file(string, WAVE_OUTPUT_BOT_FILENAME+str(ct_voice_id)+".wav")
        engine.save_to_file(translate_msgg, ROOT_TO_OMNI+"/audio_bot.wav")
        engine.runAndWait()
        
        '''

        call_to_omniverse = " python " + ROOT_TO_OMNIVERSE + "/my_test_client.py "

        call_to_omniverse += " " + ROOT_TO_OMNIVERSE + AUDIO_NAME + " " + OMNIVERSE_AVATAR
        print(call_to_omniverse)
        subprocess.call(call_to_omniverse, shell=True)

        my_global_mssg, translate_msgg = '', ''

except KeyboardInterrupt:
    pass