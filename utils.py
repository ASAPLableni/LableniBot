from datetime import datetime
import numpy as np
import wave
import pyaudio


def get_current_time(only_unix=False, get_time_str=False):
    t = datetime.now()

    if only_unix:
        return t.timestamp()

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

    mil_sec = str(t.microsecond)

    date_str = year + "-" + month + "-" + day + " " + hour + ":" + mint + ":" + sec + "." + mil_sec

    if get_time_str:
        return year + month + day + "_" + hour + mint + sec

    return date_str, t.timestamp()


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


def check_repetition_s2t(response_results):
    unique_sentences, unique_time = [], []
    for res in response_results:
        text_i = res.alternatives[0].transcript
        if text_i not in unique_sentences:
            unique_sentences.append(text_i)
            unique_time.append(res.result_end_time.total_seconds())

    return np.array(unique_sentences), np.array(unique_time)


def process_googles2t_answer(resp_res):
    # If 'response' has something inside.
    if len(resp_res) > 0:
        repeat_message_label = False

        if len(resp_res) > 1:

            uniq_sentences_array, uniq_time_array = check_repetition_s2t(resp_res)

            if len(uniq_sentences_array) > 1:
                # There is more than one answer in Google S2T result.
                spanish_text = get_google_s2t_sent(uniq_sentences_array, uniq_time_array)
            else:
                # There is only one answer in Google S2T result.
                spanish_text = uniq_sentences_array[0]

        else:
            spanish_text = resp_res[0].alternatives[0].transcript

    else:
        # Here means that Google S2T did not find any message.
        spanish_text = " "
        repeat_message_label = True

    return spanish_text, repeat_message_label


def reproduce_audio(root_bot_audio, chunk):
    # ###############
    # ### PYAUDIO ###
    # ###############

    # open a wav format music
    f = wave.open(root_bot_audio, "rb")
    # instantiate PyAudio
    p = pyaudio.PyAudio()
    # open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    # read data
    data = f.readframes(chunk)

    # play stream
    while data:
        stream.write(data)
        data = f.readframes(chunk)
        # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    p.terminate()
