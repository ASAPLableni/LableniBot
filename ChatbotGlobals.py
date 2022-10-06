import pandas as pd


class LableniBot:

    def __init__(self, subject_id, mode_chat, config_name, global_message, path_to_save):
        self.subject_id = subject_id
        self.mode_chat = mode_chat
        self.config_name = config_name
        self.global_message = global_message
        self.path_to_save = path_to_save

        self.sentence_to_repeat = "Puedes repetir, por favor? No te he entendido bien"
        self.chat_conversation = []
        self.counter_conv_id = 0
        self.aws_prosody = "slow"

    def append_data(self,
                    t_str_loop_start, t_unix_loop_start,
                    source, source_message,
                    bot_start_unix, bot_end_unix,
                    aws_start_unix, aws_end_unix,
                    s2t_start_unix, s2t_end_unix,
                    bot_talk_start_unix, bot_talk_end_unix,
                    person_talk_start_unix, person_talk_end_unix):
        self.chat_conversation.append({
            "ConversationSentenceId": self.counter_conv_id,
            "SubjectId": self.subject_id,
            "TimeLoopInitStr": t_str_loop_start,
            "UnixTimestampLoopInit": t_unix_loop_start,
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
        df_to_save = pd.DataFrame(self.chat_conversation)
        df_to_save.to_pickle(self.path_to_save + ".pkl")

    def from_str_to_aws_polly_pcm(self, input_str):
        input_str_aws = input_str
        input_str_aws = input_str_aws.replace("?", ".").replace("¿", ".")
        input_str_aws = input_str_aws.replace('.', '<break time="0.6s"/>')
        input_str_aws = input_str_aws.replace(',', '<break time="0.25s"/>')
        input_str_aws = '<prosody rate="' + self.aws_prosody + '">' + input_str_aws + '</prosody>'
        input_str_aws = "<speak>" + input_str_aws + "</speak>"

        return input_str_aws
