import pandas as pd
import utils as ute
import re
import json


class LableniBot:

    def __init__(self,
                 subject_id, mode_chat,
                 path_to_bot_param, path_to_bot_personality, path_to_save):
        self.subject_id = subject_id
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
            "JaJa ", "JaJa,", "jaja ", "xd ", "XD ", "Xd ", "Xd,", "Ah ", "ah ", "Ah,"
        ]
        for bad_expr in bad_expressions:
            bot_message = bot_message.replace(bad_expr, " ")

        # Find and remove words inside parenthesis as "(Risas)", etc.
        to_find_in_parenthesis = r'\((.*?)\)'
        regex_parenthesis = re.findall(to_find_in_parenthesis, bot_message)
        if len(regex_parenthesis) > 0:
            for regex_par in regex_parenthesis:
                bot_message = bot_message.replace("(" + regex_par + ")", "")

        # Keep only the first X sentences before a dot, to avoid very long message.
        message_split = bot_message.split(".")
        if len(message_split) > self.max_num_sentences:
            bot_message = ".".join(message_split[:self.max_num_sentences])

        if len(bot_message) <= 2 or bot_message == "?" or bot_message == "!":
            bot_message = self.bot_start_sequence + " " + self.sentence_to_repeat

        bot_message = bot_message if bot_message[-1] in [".", "?", "!"] else bot_message + "."

        return bot_message
