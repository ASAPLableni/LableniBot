import subprocess
import json

config_json = open('config.json')
config_dict = json.load(config_json)

ROOT_TO_OMNIVERSE = config_dict["ROOT_TO_OMNIVERSE"]

call_to_omniverse = " python " + ROOT_TO_OMNIVERSE + "/my_test_client.py"

# ##################
# ### Parameters ###
# ##################

# /World/Debra/ManRoot/Debra_gamebase_A2F/Debra_gamebase_A2F/CC_Game_Body/CC_Game_Body_result
# /audio2face/player_instance
# /World/charTransfer/mark
# /World/audio2face/player_streaming_instance
# audio2face/player_streaming_instance_03
# /World/audio2face/player_streaming_instance_01
# /World/audio2face/player_streaming_instance

AUDIO_NAME = "AudioExamples/audio_bot_aws.wav"
OMNIVERSE_AVATAR = "/World/audio2face/player_streaming_instance"

call_to_omniverse += " " + AUDIO_NAME + " " + OMNIVERSE_AVATAR
print("Message to Omniverse ", call_to_omniverse)
subprocess.call(call_to_omniverse, shell=True)
