

class Cell:
    def __init__(self, width, height, x_align, y_align, x, y):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.data = []
        self.x_align = x_align
        self.y_align = y_align

    def set_data(self):
        pass

    def __str__(self):
        return f'<cell of pos:{self.x, self.y} size:{self.width, self.height}, align:{self.x_align, self.y_align}, data{self.data}>'


class Table:
    def __init__(self, n_row, n_column):
        self._cells = []
        for i in range(n_row):
            for ii in range(n_column):
                c = Cell(None, None, 'r', 't', i, ii)
                self._cells.append(c)

    def get_cell_bypos(self, x, y):
        for c in self._cells:
            if c.x == x and c.y == y:
                return c
        raise

    def set_equal_cell_width(self, width):
        for i in self._cells:
            i.width = width

    def set_cells_data(self, pos, data):
        if isinstance(pos, (list, tuple)):
            if not all([isinstance(i, (list, tuple)) for i in pos]):
                pos = [pos, ]
        else:
            raise

        if isinstance(data, (list, tuple)):
            if not all([isinstance(i, str) for i in data]):
                raise
        elif isinstance(data, str):
            data = [data, ]
        else:
            raise

        if len(pos) != len(data):
            raise

        for x, y, line in zip(pos, data):
            cell = self.get_cell_bypos(x, y)
            cell.set_data(line)

    def set_cell_data(self, x, y, data):
        cell = self.get_cell_bypos(x, y)
        if isinstance(data, (list, tuple)):
            pass
        elif isinstance(data, str):
            pass
        else:
            raise

    def set_equal_cell_height(self, height):
        for i in self._cells:
            i.height = height