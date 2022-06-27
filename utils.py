from datetime import datetime

def get_current_time():

    t = datetime.now()

    year = str(t.year)

    month = str(t.month)
    if len(month) == 1: month = "0" + month 

    day = str(t.day)
    if len(day) == 1: day = "0" + day 

    hour = str(t.hour)
    if len(hour) == 1: hour = "0" + hour 

    mint = str(t.minute)
    if len(mint) == 1: mint = "0" + mint 

    sec = str(t.second)
    if len(sec) == 1: sec = "0" + sec 

    msec = str(t.microsecond)

    date_str = year + "-" + month + "-" + day + " " + hour + ":" + mint + ":" + sec + "." + msec
    date_str_other_form = year + month + day + "_" + hour + mint + sec + "." + msec[:3]

    return date_str, t.timestamp(), date_str_other_form
