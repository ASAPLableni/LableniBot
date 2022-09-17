from tkinter import *


class Interface(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.bot_config = "Neutral"
        self.create_menus()

    def select_bot(self, bot_txt, bot_state):
        Label(self.master, text="You select " + bot_txt + " with state " + bot_state).pack()
        text = bot_txt + " ; " + bot_state
        my_label = Label(self.master, text=text)
        self.bot_config = my_label.cget("text")

    def close_app(self):
        self.master.destroy()

    def create_menus(self):
        my_menu = Menu(self.master)
        self.master.config(menu=my_menu)

        file_menu = Menu(my_menu)
        my_menu.add_cascade(label="Select a Bot", menu=file_menu)

        menu_female_1 = Menu(my_menu)
        menu_female_1.add_command(label="Happy State", command=lambda: self.select_bot("Female Bot 1", "Happy State"))
        menu_female_1.add_separator()
        menu_female_1.add_command(label="Sad State", command=lambda: self.select_bot("Female Bot 1", "Sad State"))
        menu_female_1.add_separator()
        menu_female_1.add_command(label="Relax State", command=lambda: self.select_bot("Female Bot 1", "Relax State"))
        menu_female_1.add_separator()
        menu_female_1.add_command(label="Angry State", command=lambda: self.select_bot("Female Bot 1", "Angry State"))
        file_menu.add_cascade(label="Female Bot 1", menu=menu_female_1)

        file_menu.add_separator()

        menu_male_1 = Menu(my_menu)
        menu_male_1.add_command(label="Happy State", command=lambda: self.select_bot("Male Bot 1", "Happy State"))
        menu_male_1.add_separator()
        menu_male_1.add_command(label="Sad State", command=lambda: self.select_bot("Male Bot 1", "Sad State"))
        menu_male_1.add_separator()
        menu_male_1.add_command(label="Relax State", command=lambda: self.select_bot("Male Bot 1", "Relax State"))
        menu_male_1.add_separator()
        menu_male_1.add_command(label="Angry State", command=lambda: self.select_bot("Male Bot 1", "Angry State"))
        file_menu.add_cascade(label="Male Bot 1", menu=menu_male_1)

        file_menu.add_separator()

        menu_female_2 = Menu(my_menu)
        menu_female_2.add_command(label="Happy State", command=lambda: self.select_bot("Female Bot 2", "Happy State"))
        menu_female_2.add_separator()
        menu_female_2.add_command(label="Sad State", command=lambda: self.select_bot("Female Bot 2", "Sad State"))
        menu_female_2.add_separator()
        menu_female_2.add_command(label="Relax State", command=lambda: self.select_bot("Female Bot 2", "Relax State"))
        menu_female_2.add_separator()
        menu_female_2.add_command(label="Angry State", command=lambda: self.select_bot("Female Bot 2", "Angry State"))
        file_menu.add_cascade(label="Female Bot 2", menu=menu_female_2)

        file_menu.add_separator()

        menu_male_2 = Menu(my_menu)
        menu_male_2.add_command(label="Happy State", command=lambda: self.select_bot("Male Bot 2", "Happy State"))
        menu_male_2.add_separator()
        menu_male_2.add_command(label="Sad State", command=lambda: self.select_bot("Male Bot 2", "Sad State"))
        menu_male_2.add_separator()
        menu_male_2.add_command(label="Relax State", command=lambda: self.select_bot("Male Bot 2", "Relax State"))
        menu_male_2.add_separator()
        menu_male_2.add_command(label="Angry State", command=lambda: self.select_bot("Male Bot 2", "Angry State"))
        file_menu.add_cascade(label="Male Bot 2", menu=menu_male_2)

        file_menu.add_separator()

        menu_male_2 = Menu(my_menu)
        menu_male_2.add_command(label="Neutral 1", command=lambda: self.select_bot("Neutral", "Neutral 1"))
        menu_male_2.add_separator()
        menu_male_2.add_command(label="Neutral 2", command=lambda: self.select_bot("Neutral", "Neutral 2"))
        menu_male_2.add_separator()
        menu_male_2.add_command(label="Neutral 3", command=lambda: self.select_bot("Neutral", "Neutral 3"))
        file_menu.add_cascade(label="Neutral", menu=menu_male_2)

        button_close = Button(text="Done !", command=self.close_app)
        button_close.grid(column=1, row=0, sticky='e', padx=100, pady=2)
        button_close.pack()


# root = Tk()
# root.title("LabLeni BOT")
# root.geometry("400x400")

# app = Interface(master=root)

# app.mainloop()

# print(app.bot_config)
