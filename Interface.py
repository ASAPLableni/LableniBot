from tkinter import *
import json
import os


class Interface(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.names_personalities_dict = {}
        self.get_chatbots_names()

        self.master = master
        self.bot_config = "Neutral"
        self.subject_name = ""
        self.subject_id = ""
        self.change_avatar_name = False
        self.avatar_name = ""
        self.create_menus()

    def get_chatbots_names(self):

        all_folders_list = ["Female_Bot_1", "Female_Bot_2", "Male_Bot_1", "Male_Bot_2", "Neutral"]
        for f in all_folders_list:

            f_space = f.replace("_", " ")
            self.names_personalities_dict[f_space] = {}

            all_personalities = os.listdir("LableniBotConfig/Personalities/" + f)
            for per in all_personalities:
                root_to_parameters = "LableniBotConfig/Personalities/" + f + "/" + per
                with open(root_to_parameters, "r", encoding='utf-8') as read_file:
                    personalities_dict = json.load(read_file)

                per_space = per.split(".")[0].replace("_", " ")

                self.names_personalities_dict[f_space][per_space] = personalities_dict["BOT_NAME"]

    def select_bot(self, bot_txt, bot_state):
        Label(self.master, text="You select " + bot_txt + " with state " + bot_state).pack()
        text = bot_txt + " ; " + bot_state
        my_label = Label(self.master, text=text)
        self.bot_config = my_label.cget("text")

    def create_menus(self):
        my_menu = Menu(self.master)
        self.master.config(menu=my_menu)

        file_menu = Menu(my_menu)
        my_menu.add_cascade(label="Select a Bot", menu=file_menu)

        # ###################
        # ### Happy state ###
        # ###################
        state_name = "Happy State"
        happy_female_1 = self.names_personalities_dict["Female Bot 1"][state_name]
        happy_female_2 = self.names_personalities_dict["Female Bot 2"][state_name]
        happy_male_1 = self.names_personalities_dict["Male Bot 1"][state_name]
        happy_male_2 = self.names_personalities_dict["Male Bot 2"][state_name]

        menu_happy = Menu(my_menu)
        menu_happy.add_command(label="Female C (" + happy_female_1 + ")",
                               command=lambda: self.select_bot("Female Bot 1", "Happy State"))
        menu_happy.add_separator()
        menu_happy.add_command(label="Female SF (" + happy_female_2 + ")",
                               command=lambda: self.select_bot("Female Bot 2", "Happy State"))
        menu_happy.add_separator()
        menu_happy.add_command(label="Male C (" + happy_male_1 + ")",
                               command=lambda: self.select_bot("Male Bot 1", "Happy State"))
        menu_happy.add_separator()
        menu_happy.add_command(label="Male SF (" + happy_male_2 + ")",
                               command=lambda: self.select_bot("Male Bot 2", "Happy State"))
        menu_happy.add_separator()
        file_menu.add_cascade(label="Happy State", menu=menu_happy)

        file_menu.add_separator()

        # #################
        # ### Sad state ###
        # #################
        state_name = "Sad State"
        sad_female_1 = self.names_personalities_dict["Female Bot 1"][state_name]
        sad_female_2 = self.names_personalities_dict["Female Bot 2"][state_name]
        sad_male_1 = self.names_personalities_dict["Male Bot 1"][state_name]
        sad_male_2 = self.names_personalities_dict["Male Bot 2"][state_name]

        menu_sad = Menu(my_menu)
        menu_sad.add_command(label="Female C (" + sad_female_1 + ")",
                             command=lambda: self.select_bot("Female Bot 1", "Sad State"))
        menu_sad.add_separator()
        menu_sad.add_command(label="Female SF (" + sad_female_2 + ")",
                             command=lambda: self.select_bot("Female Bot 2", "Sad State"))
        menu_sad.add_separator()
        menu_sad.add_command(label="Male C (" + sad_male_1 + ")",
                             command=lambda: self.select_bot("Male Bot 1", "Sad State"))
        menu_sad.add_separator()
        menu_sad.add_command(label="Male SF (" + sad_male_2 + ")",
                             command=lambda: self.select_bot("Male Bot 2", "Sad State"))
        menu_sad.add_separator()
        file_menu.add_cascade(label="Sad State", menu=menu_sad)

        file_menu.add_separator()

        # ###################
        # ### Relax state ###
        # ###################
        state_name = "Relax State"
        relax_female_1 = self.names_personalities_dict["Female Bot 1"][state_name]
        relax_female_2 = self.names_personalities_dict["Female Bot 2"][state_name]
        relax_male_1 = self.names_personalities_dict["Male Bot 1"][state_name]
        relax_male_2 = self.names_personalities_dict["Male Bot 2"][state_name]

        menu_relax = Menu(my_menu)
        menu_relax.add_command(label="Female C (" + relax_female_1 + ")",
                               command=lambda: self.select_bot("Female Bot 1", "Relax State"))
        menu_relax.add_separator()
        menu_relax.add_command(label="Female SF (" + relax_female_2 + ")",
                               command=lambda: self.select_bot("Female Bot 2", "Relax State"))
        menu_relax.add_separator()
        menu_relax.add_command(label="Male C (" + relax_male_1 + ")",
                               command=lambda: self.select_bot("Male Bot 1", "Relax State"))
        menu_relax.add_separator()
        menu_relax.add_command(label="Male SF (" + relax_male_2 + ")",
                               command=lambda: self.select_bot("Male Bot 2", "Relax State"))
        menu_relax.add_separator()
        file_menu.add_cascade(label="Relax State", menu=menu_relax)

        file_menu.add_separator()

        # ###################
        # ### Angry state ###
        # ###################
        state_name = "Angry State"
        angry_female_1 = self.names_personalities_dict["Female Bot 1"][state_name]
        angry_female_2 = self.names_personalities_dict["Female Bot 2"][state_name]
        angry_male_1 = self.names_personalities_dict["Male Bot 1"][state_name]
        angry_male_2 = self.names_personalities_dict["Male Bot 2"][state_name]

        menu_angry = Menu(my_menu)
        menu_angry.add_command(label="Female C (" + angry_female_1 + ")",
                               command=lambda: self.select_bot("Female Bot 1", "Angry State"))
        menu_angry.add_separator()
        menu_angry.add_command(label="Female SF (" + angry_female_2 + ")",
                               command=lambda: self.select_bot("Female Bot 2", "Angry State"))
        menu_angry.add_separator()
        menu_angry.add_command(label="Male C (" + angry_male_1 + ")",
                               command=lambda: self.select_bot("Male Bot 1", "Angry State"))
        menu_angry.add_separator()
        menu_angry.add_command(label="Male SF (" + angry_male_2 + ")",
                               command=lambda: self.select_bot("Male Bot 2", "Angry State"))
        menu_angry.add_separator()
        file_menu.add_cascade(label="Angry State", menu=menu_angry)

        file_menu.add_separator()

        '''
        chatbot_label = "Female Bot 1"
        name_happy = self.names_personalities_dict[chatbot_label]["Happy State"]
        name_sad = self.names_personalities_dict[chatbot_label]["Sad State"]
        name_relax = self.names_personalities_dict[chatbot_label]["Relax State"]
        name_angry = self.names_personalities_dict[chatbot_label]["Angry State"]

        menu_female_1 = Menu(my_menu)
        menu_female_1.add_command(label="Happy State (" + name_happy + ")",
                                  command=lambda: self.select_bot("Female Bot 1", "Happy State"))
        menu_female_1.add_separator()
        menu_female_1.add_command(label="Sad State (" + name_sad + ")",
                                  command=lambda: self.select_bot("Female Bot 1", "Sad State"))
        menu_female_1.add_separator()
        menu_female_1.add_command(label="Relax State (" + name_relax + ")",
                                  command=lambda: self.select_bot("Female Bot 1", "Relax State"))
        menu_female_1.add_separator()
        menu_female_1.add_command(label="Angry State (" + name_angry + ")",
                                  command=lambda: self.select_bot("Female Bot 1", "Angry State"))
        file_menu.add_cascade(label="Female Bot C", menu=menu_female_1)

        file_menu.add_separator()

        chatbot_label = "Male Bot 1"
        name_happy = self.names_personalities_dict[chatbot_label]["Happy State"]
        name_sad = self.names_personalities_dict[chatbot_label]["Sad State"]
        name_relax = self.names_personalities_dict[chatbot_label]["Relax State"]
        name_angry = self.names_personalities_dict[chatbot_label]["Angry State"]

        menu_male_1 = Menu(my_menu)
        menu_male_1.add_command(label="Happy State (" + name_happy + ")",
                                command=lambda: self.select_bot("Male Bot 1", "Happy State"))
        menu_male_1.add_separator()
        menu_male_1.add_command(label="Sad State (" + name_sad + ")",
                                command=lambda: self.select_bot("Male Bot 1", "Sad State"))
        menu_male_1.add_separator()
        menu_male_1.add_command(label="Relax State (" + name_relax + ")",
                                command=lambda: self.select_bot("Male Bot 1", "Relax State"))
        menu_male_1.add_separator()
        menu_male_1.add_command(label="Angry State (" + name_angry + ")",
                                command=lambda: self.select_bot("Male Bot 1", "Angry State"))
        file_menu.add_cascade(label="Male Bot C", menu=menu_male_1)

        file_menu.add_separator()

        chatbot_label = "Female Bot 2"
        name_happy = self.names_personalities_dict[chatbot_label]["Happy State"]
        name_sad = self.names_personalities_dict[chatbot_label]["Sad State"]
        name_relax = self.names_personalities_dict[chatbot_label]["Relax State"]
        name_angry = self.names_personalities_dict[chatbot_label]["Angry State"]

        menu_female_2 = Menu(my_menu)
        menu_female_2.add_command(label="Happy State (" + name_happy + ")",
                                  command=lambda: self.select_bot("Female Bot 2", "Happy State"))
        menu_female_2.add_separator()
        menu_female_2.add_command(label="Sad State (" + name_sad + ")",
                                  command=lambda: self.select_bot("Female Bot 2", "Sad State"))
        menu_female_2.add_separator()
        menu_female_2.add_command(label="Relax State (" + name_relax + ")",
                                  command=lambda: self.select_bot("Female Bot 2", "Relax State"))
        menu_female_2.add_separator()
        menu_female_2.add_command(label="Angry State (" + name_angry + ")",
                                  command=lambda: self.select_bot("Female Bot 2", "Angry State"))
        file_menu.add_cascade(label="Female Bot SF", menu=menu_female_2)

        file_menu.add_separator()

        chatbot_label = "Male Bot 2"
        name_happy = self.names_personalities_dict[chatbot_label]["Happy State"]
        name_sad = self.names_personalities_dict[chatbot_label]["Sad State"]
        name_relax = self.names_personalities_dict[chatbot_label]["Relax State"]
        name_angry = self.names_personalities_dict[chatbot_label]["Angry State"]

        menu_male_2 = Menu(my_menu)
        menu_male_2.add_command(label="Happy State (" + name_happy + ")",
                                command=lambda: self.select_bot("Male Bot 2", "Happy State"))
        menu_male_2.add_separator()
        menu_male_2.add_command(label="Sad State (" + name_sad + ")",
                                command=lambda: self.select_bot("Male Bot 2", "Sad State"))
        menu_male_2.add_separator()
        menu_male_2.add_command(label="Relax State (" + name_relax + ")",
                                command=lambda: self.select_bot("Male Bot 2", "Relax State"))
        menu_male_2.add_separator()
        menu_male_2.add_command(label="Angry State (" + name_angry + ")",
                                command=lambda: self.select_bot("Male Bot 2", "Angry State"))
        file_menu.add_cascade(label="Male Bot SF", menu=menu_male_2)

        file_menu.add_separator()
        '''

        # #####################
        # ### Neutral state ###
        # #####################
        chatbot_label = "Neutral"
        female_neutral_1 = self.names_personalities_dict[chatbot_label]["Female Neutral C 1"]
        female_neutral_2 = self.names_personalities_dict[chatbot_label]["Female Neutral SF 2"]
        male_neutral_1 = self.names_personalities_dict[chatbot_label]["Male Neutral C 1"]
        male_neutral_2 = self.names_personalities_dict[chatbot_label]["Male Neutral SF 2"]

        menu_neutral = Menu(my_menu)
        menu_neutral.add_command(label="Female Neutral C 1 (" + female_neutral_1 + ")",
                                 command=lambda: self.select_bot("Neutral", "Female Neutral C 1"))
        menu_neutral.add_separator()
        menu_neutral.add_command(label="Female Neutral SF 1 (" + female_neutral_1 + ")",
                                 command=lambda: self.select_bot("Neutral", "Female Neutral SF 1"))
        menu_neutral.add_separator()
        menu_neutral.add_command(label="Female Neutral C 2 (" + female_neutral_2 + ")",
                                 command=lambda: self.select_bot("Neutral", "Female Neutral C 2"))
        menu_neutral.add_separator()
        menu_neutral.add_command(label="Female Neutral SF 2 (" + female_neutral_2 + ")",
                                 command=lambda: self.select_bot("Neutral", "Female Neutral SF 2"))
        menu_neutral.add_separator()
        menu_neutral.add_command(label="Male Neutral C 1 (" + male_neutral_1 + ")",
                                 command=lambda: self.select_bot("Neutral", "Male Neutral C 1"))
        menu_neutral.add_separator()
        menu_neutral.add_command(label="Male Neutral SF 1 (" + male_neutral_1 + ")",
                                 command=lambda: self.select_bot("Neutral", "Male Neutral SF 1"))
        menu_neutral.add_separator()
        menu_neutral.add_command(label="Male Neutral C 2 (" + male_neutral_2 + ")",
                                 command=lambda: self.select_bot("Neutral", "Male Neutral C 2"))
        menu_neutral.add_separator()
        menu_neutral.add_command(label="Male Neutral SF 2 (" + male_neutral_2 + ")",
                                 command=lambda: self.select_bot("Neutral", "Male Neutral SF 2"))
        file_menu.add_cascade(label="Neutral", menu=menu_neutral)

        # To write name and ID of the subject.
        Label(self.master, text="Please enter subject's name").pack()
        entry_name = Entry(self.master)
        entry_name.pack()

        Label(self.master, text="Please enter subject's Id").pack()
        entry_id = Entry(self.master)
        entry_id.pack()

        Label(self.master, text="Write only if you want to change Avatar name").pack()
        entry_avatar_name = Entry(self.master)
        entry_avatar_name.pack()

        button_close = Button(self.master,
                              text="Done !",
                              command=lambda: self.close_app(entry_name, entry_id, entry_avatar_name))
        # button_close.grid(column=1, row=0, sticky='e', padx=100, pady=2)
        button_close.pack()

    def close_app(self, entry_name, entry_id, entry_avatar_name):
        self.subject_name = entry_name.get()
        self.subject_id = entry_id.get()
        self.avatar_name = entry_avatar_name.get()
        if len(self.avatar_name) > 1:
            self.change_avatar_name = True
        self.master.destroy()


if __name__ == "__main__":
    root = Tk()
    root.title("LabLeni BOT")
    root.geometry("400x400")

    app = Interface(master=root)

    app.mainloop()

    print(app.bot_config)
