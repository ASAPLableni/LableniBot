import utils as ute
import pickle
import time
import os

from tkinter import *

from BeginInterface import BeginInterface, SecondInterface, EndInterface

TIME_RECORDING = 2 * 60

# #######################
# ### First Interface ###
# #######################

root = Tk()
root.title("Record GSR Open eyes")
root.geometry("400x400")

app = BeginInterface(master=root)

app.mainloop()

subject_id = app.subject_id
print("Subject ID", subject_id)

# init_first_interface = ute.get_current_time(get_time_str=True)

init_date_str, init_date_unix = ute.get_current_time()
time.sleep(TIME_RECORDING)  # Two minutes recording
end_date_str, end_date_unix = ute.get_current_time()

list_help = [
    {"RealTimeStr": init_date_str, "UnixTime": init_date_unix, "Event": "Open Eyes GSR Begin"},
    {"RealTimeStr": end_date_str, "UnixTime": end_date_unix, "Event": "Open Eyes GSR End"}
]

path_to_folder = "Conversations/" + subject_id

if not os.path.exists(path_to_folder):
    os.mkdir(path_to_folder)

with open(path_to_folder + '/GuideOfTimes.pkl', 'wb') as handle:
    pickle.dump(list_help, handle, protocol=pickle.HIGHEST_PROTOCOL)

# ########################
# ### Second Interface ###
# ########################

root = Tk()
root.title("Record GSR Closed eyes")
root.geometry("400x400")

app = SecondInterface(master=root)

app.mainloop()

init_date_str, init_date_unix = ute.get_current_time()
time.sleep(TIME_RECORDING)  # Two minutes recording
end_date_str, end_date_unix = ute.get_current_time()

list_help.append({"RealTimeStr": init_date_str, "UnixTime": init_date_unix, "Event": "Closed Eyes GSR Begin"})

list_help.append({"RealTimeStr": end_date_str, "UnixTime": end_date_unix, "Event": "Closed Eyes GSR End"})

with open(path_to_folder + '/GuideOfTimes.pkl', 'wb') as handle:
    pickle.dump(list_help, handle, protocol=pickle.HIGHEST_PROTOCOL)

# #####################
# ### END INTERFACE ###
# #####################

root = Tk()
root.title("Recording finished")
root.geometry("400x400")

app = EndInterface(master=root)

app.mainloop()
print("Done")
