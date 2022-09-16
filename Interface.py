from tkinter import *

global bot, bot_state
bot, bot_state = "", ""


def our_command(text):
    global bot
    my_label = Label(root, text="You select " + text)
    print("the label is", my_label.cget("text"))
    bot = my_label.cget("text")
    print(bot)


def close_app():
    root.destroy()


root = Tk()
root.title("LabLeni BOT")
root.geometry("400x400")

my_menu = Menu(root)
root.config(menu=my_menu)

file_menu = Menu(my_menu)
my_menu.add_cascade(label="Select a Bot", menu=file_menu)
file_menu.add_command(label="Male Bot 1", command=lambda: our_command("Male 1"))
file_menu.add_separator()
file_menu.add_command(label="Male Bot 2", command=lambda: our_command("Male 2"))

button_close = Button(text="Close", command=close_app)
button_close.grid(column=1, row=0, sticky='e', padx=100, pady=2)
button_close.pack()

root.mainloop()

print(bot)
