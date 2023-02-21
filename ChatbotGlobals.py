import pandas as pd
import utils as ute
import re
import json
import pickle


class LableniBot:

    def __init__(self,
                 subject_id, subject_name, mode_chat,
                 path_to_bot_param, path_to_bot_personality, path_to_save):
        self.subject_id = subject_id
        self.subject_name = subject_name
        self.mode_chat = mode_chat
        self.path_to_save = path_to_save

        # Parameters from BOT personality JSON.
        with open(path_to_bot_personality, "r", encoding='utf-8') as read_file:
            personalities_dict = json.load(read_file)

        self.bot_name = personalities_dict["BOT_NAME"]
        self.bot_start_sequence = self.bot_name + ":"
        self.global_message = personalities_dict["CONTEXT_MESSAGE"]
        self.initial_message = personalities_dict["INITIAL_MESSAGE"]
        self.aws_prosody = personalities_dict["AWS_PROSODY"]
        self.config_name = personalities_dict["CONFIG_NAME"]
        self.farewell_message = personalities_dict["FAREWELL_MESSAGE"]
        self.bot_voice_id = personalities_dict["BOT_VOICE_ID"]
        self.engine_type = personalities_dict["ENGINE_TYPE"]
        self.omniverse_avatar = personalities_dict["OMNIVERSE_AVATAR"]

        # Parameters from BOT parameters JSON.
        with open(path_to_bot_param, "r", encoding='utf-8') as read_file:
            parameters_dict = json.load(read_file)

        self.max_num_sentences = parameters_dict["MAX_NUM_SENTENCES"]
        self.native_language = parameters_dict["NATIVE_LANGUAGE"]

        # Initializations.
        self.sentence_to_repeat = "Puedes repetir, por favor? No te he entendido bien"

        self.chat_conversation = []
        self.counter_conv_id = 0
        self.good_bye_message = False

        del personalities_dict, parameters_dict

    def append_data(self,
                    t_str_loop_start, t_unix_loop_start,
                    source, source_message,
                    bot_start_unix, bot_end_unix,
                    aws_start_unix, aws_end_unix,
                    s2t_start_unix, s2t_end_unix,
                    bot_talk_start_unix, bot_talk_end_unix,
                    person_talk_start_unix, person_talk_end_unix):
        t_str_loop_save, t_unix_loop_save = ute.get_current_time()

        self.chat_conversation.append({
            "ConversationSentenceId": self.counter_conv_id,
            "SubjectId": self.subject_id,
            "ChatbotName": self.bot_name,
            "TimeLoopInitStr": t_str_loop_start,
            "UnixTimestampLoopInit": t_unix_loop_start,
            "TimeSaveStr": t_str_loop_save,
            "UnixTimeSave": t_unix_loop_save,
            "Source": source,
            "SpanishMessage": source_message,
            "Mode": self.mode_chat,
            "GlobalMessage": self.global_message,
            "ConfigName": self.config_name,
            "BotStartUnix": bot_start_unix,
            "BotEndUnix": bot_end_unix,
            "AWSStartUniX": aws_start_unix,
            "AWSEndUniX": aws_end_unix,
            "S2TStartUnix": s2t_start_unix,
            "S2TEndUnix": s2t_end_unix,
            "BotTalkStartUnix": bot_talk_start_unix,
            "BotTalkEndUnix": bot_talk_end_unix,
            "PersonTalkStartUnix": person_talk_start_unix,
            "PersonTalkEndUnix": person_talk_end_unix,
        })

    def save_data(self):
        pd.DataFrame(self.chat_conversation).to_pickle(self.path_to_save + ".pkl")

    def from_pkl_to_csv(self):
        df_pkl = pd.read_pickle(self.path_to_save + ".pkl")
        df_pkl.to_csv(self.path_to_save + ".csv", index=False, sep=";")

    def from_str_to_aws_polly_pcm(self, input_str):
        input_str_aws = input_str
        input_str_aws = input_str_aws.replace("?", ".").replace("¿", ".")
        input_str_aws = input_str_aws.replace('.', '<break time="0.6s"/>')
        input_str_aws = input_str_aws.replace(',', '<break time="0.25s"/>')
        input_str_aws = '<prosody rate="' + self.aws_prosody + '">' + input_str_aws + '</prosody>'
        input_str_aws = "<speak>" + input_str_aws + "</speak>"

        return input_str_aws

    def clean_bot_message(self, bot_answer):
        bot_message = bot_answer.replace(self.bot_name + ":", "") if self.bot_name + ":" in bot_answer else bot_answer
        bot_message = bot_message.replace("\n", "") if "\n" in bot_message else bot_message

        # Remove certain expressions as "JaJa".
        bad_expressions = [
            "JaJa", "Jaja", "jaja", "xd", "XD", "Xd", "Ah ", "ah ", "Ah,", "ah,"
        ]
        for bad_expr in bad_expressions:
            bot_message = bot_message.replace(bad_expr, "")

        # Find and remove words inside parenthesis or brackets as "(Risas)" or "[Risas]", etc.
        bot_message = re.sub(r'[\(\[].*?[\)\]]', "", bot_message)

        # Keep only the first X sentences before a dot, to avoid very long message.
        message_split = bot_message.split(".")
        if len(message_split) > self.max_num_sentences:
            bot_message = ".".join(message_split[:self.max_num_sentences])

        if len(bot_message) <= 2 or bot_message == "?" or bot_message == "!":
            bot_message = self.bot_start_sequence + " " + self.sentence_to_repeat

        bot_message = bot_message if bot_message[-1] in [".", "?", "!"] else bot_message + "."

        return bot_message

    def remove_spanish_accents(self, message):
        words_accent_list = ["á", "é", "í", "ó", "ú"]
        words_no_accent_list = ["a", "e", "i", "o", "u"]
        break_loop = False
        for word in message.split():
            for i_word, word_accent in enumerate(words_accent_list):
                if word_accent in word:
                    if self.subject_name == word.replace(word_accent, words_no_accent_list[i_word]):
                        subject_sent_name = word.replace(word_accent, words_no_accent_list[i_word])
                        message = message.replace(word, subject_sent_name)
                        break_loop = True
                        break

            if break_loop:
                break

        return message

    def save_guide_of_times(self):
        end_str_time, unix_time = ute.get_current_time()

        with open("Conversations/" + self.subject_id + '/GuideOfTimes.pkl', 'rb') as f:
            guide_of_times = pickle.load(f)

        guide_of_times.append({
            "RealTimeStr": end_str_time,
            "UnixTime": unix_time,
            "Event": self.config_name + "_end"
        })

        with open("Conversations/" + self.subject_id + '/GuideOfTimes.pkl', 'wb') as handle:
            pickle.dump(guide_of_times, handle, protocol=pickle.HIGHEST_PROTOCOL)

        pd.DataFrame(guide_of_times).to_csv(
            "Conversations/" + self.subject_id + '/GuideOfTimes.csv', sep=";", index=False
        )
