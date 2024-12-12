from tkinter import *
from tkinter import ttk


# ---------------------- UI -----------------------------
# Initialize the main window
window = Tk()
window.title("Apollp Hunter")
window.config(padx=30, pady=10, bg="BLACK")
window.minsize(width=300, height=300)

#Title
title_label = Label(window, text="Ap0ll0 Hunter", bg="BLACK", fg="LIME", font=("Courier", 30), pady=20)
title_label.grid(row=0, column=0, columnspan=2)


# delay
delay_label = Label(window, text="Enter delay time:", bg="BLACK", fg="WHITE", font=("Arial", 12))
delay_label.grid(row=1, column=0)
delay_box = Spinbox(from_=0, to=100)
delay_box.grid(row=1, column=1)

#divider
divider = Label(window, text="", bg="BLACK", fg="WHITE",pady=10)
divider.grid(row=2, column=0, columnspan=2)

# start button
start_btn = Button(text="Start", bg="YELLOW", fg="BLACK", font=("Arial", 14), height=1, width=10)
start_btn.grid(row=6, column=0)
# stop button
stop_btn = Button(text="Stop", bg="YELLOW", fg="BLACK", font=("Arial",14), height=1, width=10)
stop_btn.grid(row=6, column=1)


# recovered label
recovered_label = Label(window, text="Recovered:", bg="BLACK", fg="WHITE", font=("Arial", 15) ,pady=20)
recovered_label.grid(row=7, column=0)
recovered_item = Label(window, text="0", bg="BLACK", fg="RED", font=("Arial", 14), pady=20)
recovered_item.grid(row=7, column=1)


# run main loop for windows
window.mainloop()

#
