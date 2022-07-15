from datetime import datetime


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
