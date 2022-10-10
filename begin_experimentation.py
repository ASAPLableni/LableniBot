import utils as ute
import pickle
import time

from tkinter import *

from BeginInterface import BeginInterface

# ### Interface ###

root = Tk()
root.title("LabLeni BOT")
root.geometry("400x400")

app = BeginInterface(master=root)

app.mainloop()

subject_id = app.subject_id
print("Subject ID", subject_id)

subject_task = app.task
print("Subject Task", subject_task)

init_date_str, init_date_unix = ute.get_current_time()
time.sleep(10)
end_date_str, end_date_unix = ute.get_current_time()

dict_help = {
    subject_task: {
        "InitRealTimeStr": init_date_str,
        "InitUnixTime": init_date_unix,
        "EndRealTimeStr": end_date_str,
        "EndUnixTime": end_date_unix,
    }
}

with open('filename.pkl', 'wb') as handle:
    pickle.dump(dict_help, handle, protocol=pickle.HIGHEST_PROTOCOL)

print("Done")
