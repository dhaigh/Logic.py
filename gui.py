#!/usr/bin/env python2

from Tkinter import *
import logic

root = Tk()
root.geometry('800x600')
root.title('Logic.py')

v = StringVar()
s = StringVar()

def ev():
    z = unicode(logic.parse(v.get()))
    z = z.replace('~', u'\u00ac')
    z = z.replace(' ^ ', u' \u2227 ')
    z = z.replace(' v ', u' \u2228 ')
    z = z.replace(' XOR ', u' \u2295 ')
    z = z.replace(' NAND ', u' \u2191 ')
    z = z.replace(' NOR ', u' \u2193 ')
    z = z.replace(' -> ', u' \u2192 ')
    z = z.replace(' <-> ', u' \u2194 ')
    s.set(z)

controls = Frame(root)

fun = Entry(controls, textvariable=v, font=("Helvetica", 24))
fun.pack(side=LEFT)

run = Button(controls, text="Evaluate", command=ev, font=("Helvetica", 24))
run.pack(side=LEFT)

r = Label(root, textvariable=s, font=("Helvetica", 24))

controls.pack(side=TOP, padx=40, pady=40)
r.pack(side=TOP)


root.mainloop()
