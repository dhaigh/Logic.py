#!/usr/bin/env python

from Tkinter import *
import tkMessageBox
import tkSimpleDialog
import logic

def error(message):
    tkMessageBox.showerror(message=message)

class Heading(Label):
    def __init__(self, parent, **kwargs):
        Label.__init__(self, parent, font=('Sans-serif', 16, 'bold'), **kwargs)

class OperationChar(Frame):
    def __init__(self, parent, character, operation, **kwargs):
        Frame.__init__(self, parent, pady=2, **kwargs)
        operation = ' is for ' + operation
        Label(self, text=character, bg='gray', width=3).pack(side=LEFT)
        Label(self, text=operation).pack(side=LEFT)

class HelpWindow(Toplevel):
    def __init__(self, **kwargs):
        Toplevel.__init__(self, **kwargs)
        self.minsize(420, 460)
        self.title('PyLogic Help')

        Label(self, text='PyLogic is a utility for propositional logic.').pack(fill=X)
        Heading(self, text='Characters for connectives').pack(fill=X, pady=(20, 5))
        operations = Frame(self)
        OperationChar(operations, '~', 'NOT').pack(fill=X)
        OperationChar(operations, '^', 'AND').pack(fill=X)
        OperationChar(operations, 'v', 'OR').pack(fill=X)
        OperationChar(operations, 'xor', 'XOR').pack(fill=X)
        OperationChar(operations, '|', 'NAND').pack(fill=X)
        OperationChar(operations, 'nor', 'NOR').pack(fill=X)
        OperationChar(operations, '->', 'the material conditional').pack(fill=X)
        OperationChar(operations, '<->', 'the logical biconditional').pack(fill=X)
        operations.pack()
        Heading(self, text='Example expressions').pack(fill=X, pady=(20, 5))
        Label(self, text='~p').pack(fill=X)
        Label(self, text='p -> q').pack(fill=X)
        Label(self, text='p ^ ~q').pack(fill=X)
        Label(self, text='p v (p ^ q)').pack(fill=X)

TRUTH_TABLE, CIRCUIT_BUILDER = range(2)

class ButtonRowFrame(Frame):
    def __init__(self, app, **kwargs):
        Frame.__init__(self, app, **kwargs)
        self.app = app
        self.mode = TRUTH_TABLE
        self.mode_swap_text = StringVar()
        self.update_mode_swap_text()

        Button(self, text='Exit', command=app.exit).pack(side=RIGHT)
        Button(self, width=12, textvariable=self.mode_swap_text,
               command=self.toggle_mode).pack(side=RIGHT)

    def update_mode_swap_text(self):
        if self.mode == TRUTH_TABLE:
            self.mode_swap_text.set('Circuit Builder')
        else:
            self.mode_swap_text.set('Truth Table')

    def toggle_mode(self):
        self.app.main_frame.pack_forget()

        if self.mode == TRUTH_TABLE:
            self.app.main_frame = CircuitBuilder(self.app)
            self.mode = CIRCUIT_BUILDER
        else:
            self.app.main_frame = TruthTableFrame(self.app)
            self.mode = TRUTH_TABLE

        self.app.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.update_mode_swap_text()

class CircuitCanvasFrame(Frame):
    def __init__(self, parent, app, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.canvas = Canvas(self, width=1, height=1)
        self.canvas.bind('<Button-1>', self.button_1)
        self.canvas.bind('<ButtonRelease-1>', self.button_1_release)
        self.canvas.bind('<B1-Motion>', self.button_1_motion)
        self.canvas.pack(fill=BOTH, expand=True)

        self.canvas.create_rectangle(10, 10, 100, 100, width=2, fill='gray90')
        self.canvas.create_rectangle(110, 10, 200, 100, width=2, fill='gray90')

    def button_1(self, event):
        self.startx = event.x
        self.starty = event.y
        self.move_id = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)

    def button_1_release(self, event):
        pass

    def button_1_motion(self, event):
        dx = event.x - self.startx
        dy = event.y - self.starty
        self.startx = event.x
        self.starty = event.y

        if self.move_id == ():
            for item in self.canvas.find_all():
                self.canvas.move(item, dx, dy)
        else:
            self.canvas.move(self.move_id, dx, dy)

class CircuitButtons(Frame):
    def __init__(self, parent, app, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.app = app
        Button(self, text='Add variable', command=self.add_variable).pack(side=LEFT)

    def add_variable(self):
        variable_name = tkSimpleDialog.askstring('Add variable', 'Name of new variable:')
        if variable_name is None:
            return

        if logic.isvar(variable_name):
            pass
        else:
            error('Invalid variable name')


class CircuitBuilder(Frame):
    def __init__(self, app, **kwargs):
        Frame.__init__(self, app, **kwargs)
        self.app = app
        CircuitCanvasFrame(self, app, relief=SUNKEN, bd=2).pack(fill=BOTH, expand=True)
        CircuitButtons(self, app).pack(fill=X, pady=(10, 0))

class ControlFrame(Frame):
    def __init__(self, parent, app, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.app = app
        self.parent = parent
        self.expr = StringVar()
        self.output = StringVar()
        self.expr_entry = Entry(self, textvariable=self.expr)
        self.expr_entry.bind('<Return>', self.evaluate)
        self.expr_entry.focus_set()
        self.expr_entry.pack(side=LEFT)
        Button(self, text="Evaluate", command=self.evaluate).pack(side=LEFT)

    def evaluate(self, event=None):
        try:
            tt = str(logic.truth_table(self.expr.get()))
            self.parent.output(tt)
        except logic.TooManyVariablesError as e:
            error('Cannot generate truth table: ' + str(e))
        except SyntaxError as e:
            error('Syntax error: ' + str(e))
        self.expr_entry.select_range(0, END)

class OutputFrame(Frame):
    def __init__(self, parent, app, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.app = app
        self.output = StringVar()
        Label(self, textvariable=self.output, font=('Courier', 16)).pack()

class TruthTableFrame(Frame):
    def __init__(self, app, **kwargs):
        Frame.__init__(self, app, **kwargs)
        ControlFrame(self, app).pack(pady=20)
        self.output_frame = OutputFrame(self, app)
        self.output_frame.pack()

    def output(self, output):
        self.output_frame.output.set(output)

class App(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.root = root
        root.title('PyLogic')
        root.minsize(720, 480)

        menu = Menu(root)
        file_menu = Menu(menu, tearoff=0)
        file_menu.add_command(label='Exit', command=self.exit)
        menu.add_cascade(label='File', menu=file_menu)
        help_menu = Menu(menu, tearoff=0)
        help_menu.add_command(label='PyLogic Help', command=self.help)
        menu.add_cascade(label='Help', menu=help_menu)
        root.config(menu=menu)

        ButtonRowFrame(self).pack(fill=X)
        self.main_frame = TruthTableFrame(self)
        self.main_frame.pack()

    def exit(self):
        self.root.destroy()

    def help(self):
        HelpWindow(padx=20, pady=20)

def main():
    root = Tk()
    App(root).pack(fill=BOTH, expand=True)
    root.mainloop()

if  __name__ == '__main__':
    main()
