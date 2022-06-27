import time
import numpy as np

import torch

from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration

import paho.mqtt.client as mqtt

from googletrans import Translator
google_translator = Translator()

my_global_mssg = ''
broker = "127.0.0.1" 
port = 1883

torch.random.manual_seed(1)
# torch.random.initial_seed()
# torch.random.seed()

print(" ***** Loading models... ***** ")

# To see all the models: https://huggingface.co/models?pipeline_tag=conversational

# model_name = "facebook/blenderbot-3B"
# model_name = "hyunwoongko/blenderbot-9B"
# model_name = "iamalpharius/GPT-Small-BenderBot"
# model_name = "microsoft/DialoGPT-large"
# model_name = "facebook/blenderbot-1B-distill"
model_name = "facebook/blenderbot-400M-distill"

# tokenizer = BlenderbotTokenizer.from_pretrained(model_name, local_files_only=True)
# model = BlenderbotForConditionalGeneration.from_pretrained(model_name, local_files_only=True)
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
model.to("cuda")
# model = torch.nn.DataParallel(model)

print(" ***** Models loaded ***** ")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("topic/person_to_bot")

def on_message(client, userdata, msg):
    
    #t = datetime.now()
    global my_global_mssg

    message = msg.payload.decode()
    my_global_mssg = message

    client.disconnect()
    client.loop_stop()

while True:
    
    # ############################
    # ### RECIEVE MQTT MESSAGE ###
    # ############################

    client = mqtt.Client()
    client.connect("127.0.0.1", 1883)

    client.on_connect = on_connect
    client.on_message = on_message

    print("Loop forever")

    client.loop_forever()  
    
    # ###################
    # ### TRANSLATION ###
    # ###################
    # Here the message is translated from spanish to english.

    person_message_sp = my_global_mssg
    # x = google_translator.translate(person_message_sp, dest='es')
    x = google_translator.translate(person_message_sp)
    person_message = x.text

    t0 = time.time()
    
    inputs = tokenizer([person_message], return_tensors='pt', device="cuda")
    inputs.to("cuda")
    reply_ids = model.generate(**inputs)
    
    bot_message_en = tokenizer.batch_decode(reply_ids)[0].replace("<s>", "").replace("</s>", "")
    
    print("Time of the answer", np.round(time.time()-t0, 5), "s")
    
    # ###################
    # ### TRANSLATION ###
    # ###################
    # Here the message is translated from english to spanish.

    x = google_translator.translate(bot_message_en, dest='es')
    bot_message_sp = x.text

    print("Message of the bot: ", bot_message_sp)
    
    client = mqtt.Client()
    client.connect("127.0.0.1", 1883)
    client.publish("topic/bot_to_person", bot_message_sp)
    time.sleep(0.5)
    
    my_global_mssg = ""