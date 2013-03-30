#!/usr/bin/env python

from Tkinter import *
import logic

root = Tk()
root.geometry('800x600')
root.title('Logic.py')

controls = Frame(root)

v = StringVar()
s = StringVar()

def ev():
    s.set((logic.parse(v.get())))

fun = Entry(controls, textvariable=v, font=("Helvetica", 24))
fun.pack(side=LEFT)

run = Button(controls, text="Evaluate", command=ev, font=("Helvetica", 24))
run.pack(side=LEFT)

r = Label(root, textvariable=s, font=("Helvetica", 24))

controls.pack(side=TOP, padx=40, pady=40)
r.pack(side=TOP)


root.mainloop()
