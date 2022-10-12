from tkinter import *


class BeginInterface(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.subject_id = ""
        self.create_menus()

    def create_menus(self):
        Label(self.master, text="Please enter subject's id").pack()
        entry_id = Entry(self.master)
        entry_id.pack()

        button_close = Button(self.master, text="Start recording open eyes!", command=lambda: self.close_app(entry_id))
        button_close.pack()

    def close_app(self, entry_id):
        self.subject_id = entry_id.get()
        self.master.destroy()


class SecondInterface(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.create_menus()

    def create_menus(self):
        button_close = Button(self.master, text="Start recording closed eyes!", command=self.close_app)
        button_close.pack()

    def close_app(self):
        self.master.destroy()


class EndInterface(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.create_menus()

    def create_menus(self):
        button_close = Button(self.master, text="Finish", command=self.close_app)
        button_close.pack()

    def close_app(self):
        self.master.destroy()
