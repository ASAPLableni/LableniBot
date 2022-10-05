import pandas as pd


class LableniChatbot:

    def __init__(self, subject_id, mode_chat, config_name, path_to_save):
        self.subject_id = subject_id
        self.mode_chat = mode_chat
        self.config_name = config_name
        self.path_to_save = path_to_save

        self.sentence_to_repeat = "Puedes repetir, por favor? No te he entendido bien"
        self.chat_conversation = []
        self.counter_conv_id = 0

    def save_data(self,
                  t_str_start, t_str_end, t_unix_start, t_unix_end,
                  source, source_message, global_message, openai_time_s, aws_time_s, s2t_time_s,
                  time_bot_talk, time_person_talk):
        self.chat_conversation.append({
            "ConversationSentenceId": self.counter_conv_id,
            "SubjectId": self.subject_id,
            "TimeInitStr": t_str_start,
            "TimeEndStr": t_str_end,
            "UnixTimestampInit": t_unix_start,
            "UnixTimestampEnd": t_unix_end,
            "Source": source,
            "SpanishMessage": source_message,
            "Mode": self.mode_chat,
            "GlobalMessage": global_message,
            "ConfigName": self.config_name,
            "OpenAItime_s": openai_time_s,
            "AWStime_s": aws_time_s,
            "S2Ttime_s": s2t_time_s,
            "TimeBotTalk_s": time_bot_talk,
            "TimePersonTalk_s": time_person_talk
        })
        df_to_save = pd.DataFrame(self.chat_conversation)
        df_to_save.to_excel(self.path_to_save + ".xlsx", index=False)
