import config


class Position(tuple):

    ATTR_MAP = {
        'x': 0,
        'y': 1,
        'z': 2
    }

    def __getattr__(self, attr):
        """Allow reading with x, y, z as arguments."""
        return self[self.ATTR_MAP[attr]]


class Piece:
    """Represent a Rubik cube piece."""

    def __init__(self, colors):
        """Initializator."""
        self.x, self.y, self.z = colors
    
    def __repr__(self):
        """Representation of the piece."""
        return f"{self.x}, {self.y}, {self.z}"

    def rotate(self, axis):
        """Rotate a piece around axis."""
        if axis == config.x:
            self.x, self.y, self.z = self.x, self.z, self.y
        elif axis == config.y:
            self.x, self.y, self.z = self.z, self.y, self.x
        elif axis == config.z:
            self.x, self.y, self.z = self.y, self.x, self.z


class Rubik:
    """Represent a Rubik cube."""

    def __init__(self, size):
        """Initializator."""
        self._size = size
        self._coord_limit = self._size // 2
        self._pieces = {}
        self._generate_init_pieces()

    def __getitem__(self, position):
        """Get the piece at given position."""
        return self.pieces[position]

    def _get_init_piece_color(self, position):
        """Get initial piece color based on its position."""
        color_x, color_y, color_z = None, None, None
        # x - orange/red
        if position.x == self.coord_limit:
            color_x = config.ORANGE
        elif position.x == -self.coord_limit:
            color_x = config.RED
        # y - yellow/white
        if position.y == self.coord_limit:
            color_y = config.YELLOW
        elif position.y == -self.coord_limit:
            color_y = config.WHITE
        # z - green/blue
        if position.z == self.coord_limit:
            color_z = config.GREEN
        elif position.z == -self.coord_limit:
            color_z = config.BLUE
        return color_x, color_y, color_z

    def _generate_init_pieces(self):
        """Generate pieces at their initial position."""
        coordinate_range = range(-self.coord_limit, self.coord_limit + 1)
        for x in coordinate_range:
            for y in coordinate_range:
                for z in coordinate_range:
                    position = Position((x, y, z))
                    self._pieces[position] = Piece(self._get_init_piece_color(position))

    def _make_rotation(self, rotation, inverse=False):
        """Make a rotation on a signed axis."""
        axis = (config.x, config.y, config.z)[list(map(abs, rotation)).index(1)]
        sign = sum(rotation)
        new_pieces = {}
        for position, piece in self.pieces.items():
            if getattr(position, axis) == sign * self.coord_limit:
                x, y, z = position
                direction = tuple(map(lambda x: x * (-1)**inverse, rotation))
                if direction == (1, 0, 0):
                    new_position = Position((x, z, -y))
                elif direction == (-1, 0, 0):
                    new_position = Position((x, -z, y))
                elif direction == (0, 1, 0):
                    new_position = Position((-z, y, x))
                elif direction == (0, -1, 0):
                    new_position = Position((z, y, -x))
                elif direction == (0, 0, 1):
                    new_position = Position((y, -x, z))
                elif direction == (0, 0, -1):
                    new_position = Position((-y, x, z))
                new_pieces[new_position] = piece
                piece.rotate(getattr(config, axis))
                continue
            new_pieces[position] = piece
        self._pieces = new_pieces

    @property
    def coord_limit(self):
        """Get the coordination limit of the cube."""
        return self._coord_limit

    @property
    def size(self):
        """Get the size of the cube."""
        return self._size

    @property
    def pieces(self):
        """Get the pieces of the cube."""
        return self._pieces

    def R(self): self._make_rotation((1, 0, 0))
    def Ri(self): self._make_rotation((1, 0, 0), inverse=True)
    def R2(self):
        self.R()
        self.R()

    def L(self): self._make_rotation((-1, 0, 0))
    def Li(self): self._make_rotation((-1, 0, 0), inverse=True)
    def L2(self):
        self.L()
        self.L()

    def F(self): self._make_rotation((0, 0, 1))
    def Fi(self): self._make_rotation((0, 0, 1), inverse=True)
    def F2(self):
        self.F()
        self.F()

    def B(self): self._make_rotation((0, 0, -1))
    def Bi(self): self._make_rotation((0, 0, -1), inverse=True)
    def B2(self):
        self.B()
        self.B()

    def U(self): self._make_rotation((0, 1, 0))
    def Ui(self): self._make_rotation((0, 1, 0), inverse=True)
    def U2(self):
        self.U()
        self.U()

    def D(self): self._make_rotation((0, -1, 0))
    def Di(self): self._make_rotation((0, -1, 0), inverse=True)
    def D2(self):
        self.D()
        self.D()
