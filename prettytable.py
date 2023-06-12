TOP, MIDDLE, BOTTOM = range(3)

BORDER_H = '─'
BORDER_V = '│'

BORDERS = {
    TOP:    ['┌', '┬', '┐'],
    MIDDLE: ['├', '┼', '┤'],
    BOTTOM: ['└', '┴', '┘']
}

def get_sides(border_name):
    if border_name is None:
        return (BORDER_V + ' ', ' ' + BORDER_V)

    border = BORDERS[border_name]
    left, right = border[0], border[2]
    return (left + BORDER_H, BORDER_H + right)

def get_separator(border_name):
    if border_name is None:
        return ' ' + BORDER_V + ' '

    return BORDER_H + BORDERS[border_name][1] + BORDER_H

def cell_str(cell):
    tf = {True: 'T', False: 'F'}
    cell = tf.get(cell, cell)
    return str(cell)

class Table(object):
    def __init__(self, header):
        self.header = list(map(cell_str, header))
        self.rows = []
        self.width = len(header)
        self.column_widths = []
        self.update()

    def __str__(self):
        output = ''
        output += self.render_border(TOP)
        output += self.render_row(self.pad_cells(self.header))
        output += self.render_border(MIDDLE)
        for row in self.rows:
            row = self.pad_cells(row)
            output += self.render_row(row)
        output += self.render_border(BOTTOM)
        return output

    def append(self, row):
        if len(row) != self.width:
            raise Exception
        row = list(map(cell_str, row))
        self.rows.append(row)
        self.update()

    def render_border(self, border_name):
        row = list(map(lambda w: BORDER_H * w, self.column_widths))
        return self.render_row(row, border_name)

    def render_row(self, row, border_name=None):
        left, right = get_sides(border_name)
        row = get_separator(border_name).join(row)
        return left + row + right + '\n'

    def pad_cells(self, row):
        row = list(row)
        for i, cell in enumerate(row):
            width = self.column_widths[i]
            cell = ' ' * ((width - len(cell)) // 2) + cell
            cell = cell + ' ' * (width - len(cell))
            row[i] = cell
        return row

    def update(self):
        widths = list(map(len, self.header))

        for row in self.rows:
            for i, cell in enumerate(row):
                if len(cell) > widths[i]:
                    widths[i] = len(cell)

        self.column_widths = widths
