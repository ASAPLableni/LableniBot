# importing whole module
from tkinter import *
from tkinter.ttk import *

# importing strftime function to
# retrieve system's time
import datetime
import time

T0_GLOBAL = time.time()

# creating tkinter window
root = Tk()
root.title('Clock')
root.geometry("200x100")


# This function is used to
# display time on the label
def show_time():
    sec_diff = time.time() - T0_GLOBAL
    string = str(datetime.timedelta(seconds=sec_diff)).split(".")[0]
    lbl.config(text=string)
    lbl.after(1000, show_time)


# Styling the label widget so that clock
# will look more attractive
lbl = Label(root, font=('calibri', 40, 'bold'),
            background='purple',
            foreground='white')

# Placing clock at the centre
# of the tkinter window
lbl.pack(anchor='center')
show_time()

mainloop()
