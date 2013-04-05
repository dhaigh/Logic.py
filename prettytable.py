TOP, MIDDLE, BOTTOM = range(3)

BORDER_H = '\xe2\x94\x80'
BORDER_V = '\xe2\x94\x82'
BORDERS = {
    TOP:    ['\xe2\x94\x8c', '\xe2\x94\xac', '\xe2\x94\x90'],
    MIDDLE: ['\xe2\x94\x9c', '\xe2\x94\xbc', '\xe2\x94\xa4'],
    BOTTOM: ['\xe2\x94\x94', '\xe2\x94\xb4', '\xe2\x94\x98']
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

def ulen(s):
    return len(s.decode('utf-8'))

class Table(object):
    def __init__(self, header):
        self.header = map(cell_str, header)
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
        row = map(cell_str, row)
        self.rows.append(row)
        self.update()

    def render_border(self, border_name):
        row = map(lambda w: BORDER_H * w, self.column_widths)
        return self.render_row(row, border_name)

    def render_row(self, row, border_name=None):
        left, right = get_sides(border_name)
        row = get_separator(border_name).join(row)
        return left + row + right + '\n'

    def pad_cells(self, row):
        row = row[:]
        for i, cell in enumerate(row):
            width = self.column_widths[i]
            cell = ' ' * ((width - ulen(cell))/2) + cell
            cell = cell + ' ' * (width - ulen(cell))
            row[i] = cell
        return row

    def update(self):
        widths = map(ulen, self.header)

        for row in self.rows:
            for i, cell in enumerate(row):
                if ulen(cell) > widths[i]:
                    widths[i] = ulen(cell)

        self.column_widths = widths
