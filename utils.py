from datetime import datetime
import numpy as np


def get_current_time():
    t = datetime.now()

    year = str(t.year)

    month = str(t.month)
    month = "0" + month if len(month) == 1 else month

    day = str(t.day)
    day = "0" + day if len(day) == 1 else day

    hour = str(t.hour)
    hour = "0" + hour if len(hour) == 1 else hour

    mint = str(t.minute)
    mint = "0" + mint if len(mint) == 1 else mint

    sec = str(t.second)
    sec = "0" + sec if len(sec) == 1 else sec

    mili_sec = str(t.microsecond)

    date_str = year + "-" + month + "-" + day + " " + hour + ":" + mint + ":" + sec + "." + mili_sec
    date_str_other_form = year + month + day + "_" + hour + mint + sec + "." + mili_sec[:3]

    return date_str, t.timestamp(), date_str_other_form


def from_str_to_was_polly_pcm(input_str):
    input_str_aws = input_str
    input_str_aws = input_str_aws.replace("?", ".").replace("¿", ".")
    input_str_aws = input_str_aws.replace('.', '<break time="0.6s"/>')
    input_str_aws = input_str_aws.replace(',', '<break time="0.25s"/>')
    input_str_aws = '<prosody rate="slow">' + input_str_aws + '</prosody>'
    input_str_aws = "<speak>" + input_str_aws + "</speak>"

    return input_str_aws


def get_google_s2t_sent(example1_sent, example1_time):
    matrix_content = np.zeros((len(example1_sent), len(example1_sent)))

    for i, i_sent in enumerate(example1_sent):
        for j, j_sent in enumerate(example1_sent):
            matrix_content[i][j] = 1 if i_sent in j_sent else 0

    keep_vec_bool = matrix_content.sum(axis=0) > 1

    if np.sum(keep_vec_bool) > 0:
        order_idx = np.argsort(example1_time[keep_vec_bool])
        final_sentence = " ".join(example1_sent[keep_vec_bool][order_idx])
    else:
        final_sentence = " ".join(example1_sent)

    return final_sentence
