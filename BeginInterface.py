from tkinter import *


class BeginInterface(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.subject_id = ""
        self.task = ""
        self.create_menus()

    def create_menus(self):
        Label(self.master, text="Please enter subject's id").pack()
        entry_id = Entry(self.master)
        entry_id.pack()

        Label(self.master, text="Enter your task").pack()
        entry_task = Entry(self.master)
        entry_task.pack()

        button_close = Button(self.master, text="Done !", command=lambda: self.close_app(entry_id, entry_task))
        # button_close.grid(column=1, row=0, sticky='e', padx=100, pady=2)
        button_close.pack()

    def close_app(self, entry_id, entry_task):
        self.subject_id = entry_id.get()
        self.task = entry_task.get()
        self.master.destroy()

# root = Tk()
# root.title("LabLeni BOT")
# root.geometry("400x400")

# app = Interface(master=root)

# app.mainloop()

# print(app.bot_config)
