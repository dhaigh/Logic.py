#!/usr/bin/env python

from Tkinter import *
import tkMessageBox
import tkSimpleDialog
import logic
import math

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
            self.mode_swap_text.set('Truth Tabler')

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

VARIABLE_DIMENSIONS = (120, 80)
OPERATION_DIMENSIONS = (60, 40)

def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

class CircuitItem(object):
    def __init__(self, x, y, item_id, label_id):
        self.x = x
        self.y = y
        self.on = True
        self.item_id = item_id
        self.label_id = label_id
        self.selected = True

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def get_fill(self):
        if self.on:
            fill = 'springgreen3' if self.selected else 'springgreen2'
        else:
            fill = 'firebrick3' if self.selected else 'firebrick2'
        return fill

    def get_outline(self):
        return 'black' if self.selected else 'gray'

    def get_colors(self):
        return (self.get_fill(), self.get_outline())

class CircuitOperation(CircuitItem):
    def __init__(self, x, y, item_id, label_id, op_class, *variables):
        super(CircuitOperation, self).__init__(x, y, item_id, label_id)
        self.op_class = op_class
        self.variables = variables
        self.reevaluate()

    def reevaluate(self):
        terms = map(lambda i: (logic.F, logic.T)[i.on], self.variables)
        self.on = self.op_class(*terms).evaluate({})

class CircuitVariable(CircuitItem):
    def __init__(self, x, y, item_id, label_id, name):
        super(CircuitVariable, self).__init__(x, y, item_id, label_id)
        self.name = name

    def toggle(self):
        self.on = not self.on

class CircuitCanvasFrame(Frame):
    def __init__(self, parent, app, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.canvas = Canvas(self, width=1, height=1)
        self.canvas.bind('<Button-1>', self.button_1)
        self.canvas.bind('<ButtonRelease-1>', self.button_1_release)
        self.canvas.bind('<B1-Motion>', self.button_1_motion)
        self.canvas.pack(fill=BOTH, expand=True)
        self.operations = []
        self.items = []
        self.down = False
        self.item_id = None
        self.line_ids = []

    def move(self, item_id, dx, dy):
        item = self.get_item(item_id)
        item.move(dx, dy)
        self.canvas.move(item_id, dx, dy)
        self.canvas.move(item.label_id, dx, dy)

    def button_1(self, event):
        self.down = True
        self.startx = event.x
        self.starty = event.y
        item_ids = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item_id in sorted(item_ids):
            if self.get_item(item_id):
                self.item_id = item_id

    def button_1_motion(self, event):
        self.down = False
        dx = event.x - self.startx
        dy = event.y - self.starty
        self.startx = event.x
        self.starty = event.y

        if self.item_id:
            self.move(self.item_id, dx, dy)
        else:
            for item in self.items:
                self.move(item.item_id, dx, dy)
        self.draw_lines()

    def button_1_release(self, event):
        if self.down:
            # toggle selection on item
            if self.item_id:
                if self.get_item(self.item_id).selected:
                    self.deselect(self.item_id)
                else:
                    self.select(self.item_id)

            # deselect all items
            else:
                for item in self.items:
                    item.selected = False
                    self.update_item(item.item_id)

        self.item_id = None


    def get_item(self, item_id=None):
        # return LogicItem object corresponding to item with ID of `item_id`
        if item_id is None:
            item_id = self.item_id
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    def update_item(self, item):
        if isinstance(item, int):
            return self.update_item(self.get_item(item))
        fill, outline = item.get_colors()
        self.canvas.itemconfig(item.item_id, fill=fill, outline=outline)

    def select(self, item):
        if isinstance(item, int):
            return self.select(self.get_item(item))
        item.selected = True
        self.update_item(item)

    def deselect(self, item):
        if isinstance(item, int):
            return self.deselect(self.get_item(item))
        item.selected = False
        self.update_item(item)

    def add_item(self, label, dimensions):
        # place items in the center of the canvas
        x, y = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2

        width, height = dimensions
        x1 = x - width/2
        x2 = x + width/2
        y1 = y - height/2
        y2 = y + height/2

        item_id = self.canvas.create_rectangle(x1, y1, x2, y2, width=2)
        label_id = self.canvas.create_text(x, y, anchor=CENTER, text=label)
        return (x, y, item_id, label_id)

    def add_variable(self, name):
        x, y, item_id, label_id = self.add_item(name, VARIABLE_DIMENSIONS)
        self.items.append(CircuitVariable(x, y, item_id, label_id, name))
        self.update_item(item_id)

    def add_operation(self, op_class, name=None):
        name = name if name else op_class.__name__
        variables = []
        for item in self.items:
            if item.selected:
                variables.append(item)

        # validate operation
        if op_class is logic.Not and len(variables) != 1:
            return error('Not expressions can only have 1 term')
        if issubclass(op_class, logic.BinaryOperation):
            if len(variables) < 2:
                return error('Logical connectives require at least 2 terms')
            if op_class.two_args and len(variables) > 2:
                return error('%s expressions can only have 2 terms' % name)

        for item in variables:
            self.deselect(item)

        x, y, item_id, label_id = self.add_item(name.upper(), OPERATION_DIMENSIONS)
        operation = CircuitOperation(x, y, item_id, label_id, op_class, *variables)
        self.items.append(operation)
        self.operations.append((operation, variables))
        self.update_item(operation)
        self.draw_lines()

    def draw_lines(self):
        # remove all lines
        while self.line_ids:
            self.canvas.delete(self.line_ids.pop())

        # draw shortest line between each of the variables in each operation
        for operation, variables in self.operations:
            for variable in variables:
                vw, vh = VARIABLE_DIMENSIONS if isinstance(variable, CircuitVariable) else OPERATION_DIMENSIONS
                vw_half, vh_half = vw/2, vh/2

                ow, oh = OPERATION_DIMENSIONS
                ow_half, oh_half = ow/2, oh/2

                vx, vy = variable.x, variable.y
                ox, oy = operation.x, operation.y

                v_points = ((vx, vy+vh_half),
                            (vx, vy-vh_half),
                            (vx+vw_half, vy),
                            (vx-vw_half, vy))

                o_points = ((ox, oy+oh_half),
                            (ox, oy-oh_half),
                            (ox+ow_half, oy),
                            (ox-ow_half, oy))

                dist = distance(v_points[0], o_points[0])
                line = (v_points[0], o_points[0])
                for v_point in v_points:
                    for o_point in o_points:
                        if distance(v_point, o_point) < dist:
                            dist = distance(v_point, o_point)
                            line = (v_point, o_point)

                line_id = self.canvas.create_line(line[0][0], line[0][1],
                                                  line[1][0], line[1][1],
                                                  arrow=LAST)
                self.line_ids.append(line_id)

    def reevaluate(self):
        # reevaluate each operation
        for op, _ in self.operations:
            op.reevaluate()
            self.update_item(op)

    def toggle(self):
        names = []
        for item in self.items:
            # don't toggle operations
            if isinstance(item, CircuitOperation):
                if item.selected:
                    self.deselect(item)
                continue

            # toggle selected items
            if item.selected:
                if item.name not in names:
                    names.append(item.name)

        for item in self.items:
            if isinstance(item, CircuitVariable) and item.name in names:
                item.toggle()
                self.update_item(item)

        # reevaluate everything (this is lazy)
        self.reevaluate()

    def remove(self):
        for item in self.items:
            # only removing items we've selected
            if not item.selected:
                continue

            for op, variables in self.operations:
                if item in variables and len(variables) <= 2:
                    if isinstance(item, CircuitVariable):
                        item_noun = "The variable '%s'" % item.name
                    else:
                        item_noun = 'That operation'
                    error('%s is part of an expression that cannot be reduced'
                              % item_noun)
                    break

            # haven't encountered any conflicts
            else:
                self.items.remove(item)
                for i, (op, variables) in enumerate(self.operations):
                    if item in variables:
                        variables.remove(item)
                    if op is item:
                        self.operations.pop(i)

                # clear the rectangle and text from the canvas
                self.canvas.delete(item.item_id)
                self.canvas.delete(item.label_id)

        # redraw the lines (lazy again, just removing now-obsolete lines)
        self.draw_lines()

class CircuitButtons(Frame):
    def __init__(self, parent, app, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.app = app
        self.parent = parent

        def command(op_class, name=None):
            def command_():
                parent.canvas_frame.add_operation(op_class, name)
            return command_

        Button(self, text='Add Variable', command=self.add_variable).pack(side=LEFT)
        Button(self, text='On/Off', command=parent.canvas_frame.toggle).pack(side=LEFT)
        Button(self, text='Remove', command=parent.canvas_frame.remove).pack(side=LEFT)
        Button(self, text='XNOR', command=command(logic.Biconditional, 'Xnor')).pack(side=RIGHT)
        Button(self, text='NOR', command=command(logic.Nor)).pack(side=RIGHT)
        Button(self, text='NAND', command=command(logic.Nand)).pack(side=RIGHT)
        Button(self, text='XOR', command=command(logic.Xor)).pack(side=RIGHT)
        Button(self, text='OR', command=command(logic.Or)).pack(side=RIGHT)
        Button(self, text='AND', command=command(logic.And)).pack(side=RIGHT)
        Button(self, text='NOT', command=command(logic.Not)).pack(side=RIGHT)

    def add_variable(self):
        name = tkSimpleDialog.askstring('Add variable', 'Name of new variable:')
        if name is None:
            return
        if logic.isvar(name):
            self.parent.canvas_frame.add_variable(name)
        else:
            error('Invalid variable name')

class CircuitBuilder(Frame):
    def __init__(self, app, **kwargs):
        Frame.__init__(self, app, **kwargs)
        self.app = app
        self.canvas_frame = CircuitCanvasFrame(self, app, relief=SUNKEN, bd=2)
        self.canvas_frame.pack(fill=BOTH, expand=True)
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
        Button(self, text='Evaluate', command=self.evaluate).pack(side=LEFT)

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
