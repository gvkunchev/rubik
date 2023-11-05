import abc
import os
import tkinter as tk

import config


class Interface(abc.ABC):
    """Rubik cube interface."""

    def __init__(self, cube):
        """Initializator."""
        self._cube = cube

    @abc.abstractmethod
    def start(self):
        """Start interactive mode, allowing the user to make moves."""
        ...


class Cli(Interface):
    """Command line interface for a Rubik cube."""

    def _get_piece_position_in_matrix(self, side, x, y):
        """Get piece position in the cross matrix."""
        if side == config.FRONT:
            start_x = self._cube.size
            start_y = self._cube.size
        if side == config.BACK:
            start_x = self._cube.size
            start_y = self._cube.size * 3
        if side == config.UP:
            start_x = self._cube.size
            start_y = 0
        if side == config.DOWN:
            start_x = self._cube.size
            start_y = self._cube.size * 2
        if side == config.LEFT:
            start_x = 0
            start_y = self._cube.size
        if side == config.RIGHT:
            start_x = self._cube.size * 2
            start_y = self._cube.size
        return (start_x + x + self._cube.coord_limit,
                start_y + y + self._cube.coord_limit)

    def _clear_screen(self):
        """Clear terminal screen."""
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def refresh_cube(self):
        """Print the current state of the cube as a cross."""
        self._clear_screen()

        # Init empty matrix to be printed
        char_matrix = []
        for _ in range(self._cube.size * 4):
            char_matrix.append([])
            for _ in range(self._cube.size * 3):
                char_matrix[-1].append(config.BLACK)

        # Populate color tiles in the matrix
        for position, piece in self._cube.pieces.items():
            x, y, z = position
            if z == self._cube.coord_limit:
                col, row = self._get_piece_position_in_matrix(config.FRONT, x, -y)
                char_matrix[row][col] = piece.z
            if z == -self._cube.coord_limit:
                col, row = self._get_piece_position_in_matrix(config.BACK, x, y)
                char_matrix[row][col] = piece.z
            if y == self._cube.coord_limit:
                col, row = self._get_piece_position_in_matrix(config.UP, x, z)
                char_matrix[row][col] = piece.y
            if y == -self._cube.coord_limit:
                col, row = self._get_piece_position_in_matrix(config.DOWN, x, -z)
                char_matrix[row][col] = piece.y
            if x == -self._cube.coord_limit:
                col, row = self._get_piece_position_in_matrix(config.LEFT, z, -y)
                char_matrix[row][col] = piece.x
            if x == self._cube.coord_limit:
                col, row = self._get_piece_position_in_matrix(config.RIGHT, -z, -y)
                char_matrix[row][col] = piece.x

        # Print the matrix
        for row in char_matrix:
            print('')
            for col in row:
                print(col, end='')
        print('')
    
    def invalid_instruction(self):
        """Report an invalid isntruction."""
        input('Not a valid command. Press Enter to continue.')

    def input_move(self):
        """Wait for a move to be requested by the user."""
        move = input('Enter a move or "q" to quit: ')
        if move in ('q', 'Q'):
            return None
        return move

    def start(self, make_move, exit):
        """Start interactive mode, allowing the user to make moves."""
        try:
            while True:
                self.refresh_cube()
                move = self.input_move()
                if move is None:
                    raise KeyboardInterrupt
                if not make_move(move):
                    self.invalid_instruction()
        except KeyboardInterrupt:
            exit()


class Gui(Interface):
    """Graphical user interface for a Rubik cube."""

    TILE_SIZE = 80

    BUTTON_FONT = 'sans 20 bold'

    COLOR_MAP = {
        config.RED: 'red',
        config.GREEN: 'green',
        config.BLUE: 'blue',
        config.ORANGE: 'orange',
        config.YELLOW: 'yellow',
        config.WHITE: 'white',
    }

    def __init__(self, cube):
        """Initializator."""
        self._cube = cube
        self._window = None
        self._canvas = None
        self._last_tile = None
        self._make_move_cb = None
        self._side = config.FRONT
        self._init_window()
        self._init_canvas()
        self._init_controls()

    def _exit(self, callback):
        """Handle exit of window."""
        callback()
        self._window.destroy()

    def _init_window(self):
        """Set up main window."""
        self._window = tk.Tk()
        self._window.title('Rubik cube')
        self._window.bind("<ButtonRelease-1>", self._on_mouse_up_global)

    def _init_canvas(self):
        """Create empty canvas for drawing the cube."""
        self._canvas = tk.Canvas(self._window,
                                 width=self.TILE_SIZE * self._cube.size,
                                 height=self.TILE_SIZE * self._cube.size)
        self._canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self._canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self._canvas.pack()
    
    def _init_controls(self):
        """Initiate controls."""
        tk.Button(self._window, text="Up", font=self.BUTTON_FONT,
                  command=lambda: self._on_change_side(config.UP)).pack(fill=tk.X)
        tk.Button(self._window, text="Down", font=self.BUTTON_FONT,
                  command=lambda: self._on_change_side(config.DOWN)).pack(fill=tk.X)
        tk.Button(self._window, text="Front", font=self.BUTTON_FONT,
                  command=lambda: self._on_change_side(config.FRONT)).pack(fill=tk.X)
        tk.Button(self._window, text="Back", font=self.BUTTON_FONT,
                  command=lambda: self._on_change_side(config.BACK)).pack(fill=tk.X)
        tk.Button(self._window, text="Left", font=self.BUTTON_FONT,
                  command=lambda: self._on_change_side(config.LEFT)).pack(fill=tk.X)
        tk.Button(self._window, text="Right", font=self.BUTTON_FONT,
                  command=lambda: self._on_change_side(config.RIGHT)).pack(fill=tk.X)

    def _get_tile_at_position(self, x, y):
        """Get a tile tuple at certain position."""
        for tile_x in range(self._cube.size):
            for tile_y in range(self._cube.size):
                if (tile_x * self.TILE_SIZE < x < tile_x * self.TILE_SIZE + self.TILE_SIZE and 
                    tile_y * self.TILE_SIZE < y < tile_y * self.TILE_SIZE + self.TILE_SIZE):
                    return (tile_x, tile_y)

    def _on_mouse_down(self, event):
        """Handle mouse down event."""
        self._last_tile = self._get_tile_at_position(event.x, event.y)

    def _on_mouse_up_global(self, _):
        """Handle mouse up event."""
        x, y = self._window.winfo_pointerxy()
        target = self._window.winfo_containing(x, y)
        if target and target is not self._canvas:
            self._last_tile = None

    def _on_mouse_up(self, event):
        """Handle mouse up event."""
        if self._last_tile is None:
            return
        this_tile = self._get_tile_at_position(event.x, event.y)
        if (self._last_tile == (0, 0) and this_tile in [(1, 0), (2, 0)] or
            self._last_tile == (1, 0) and this_tile == (2, 0)):
            if self._side in (config.FRONT, config.BACK, config.LEFT, config.RIGHT):
                self._make_move_cb('Ui')
            if self._side in (config.UP, ):
                self._make_move_cb('Bi')
            if self._side in (config.DOWN, ):
                self._make_move_cb('Fi')
        elif (self._last_tile == (2, 0) and this_tile in [(1, 0), (0, 0)] or
              self._last_tile == (1, 0) and this_tile == (0, 0)):
            if self._side in (config.FRONT, config.BACK, config.LEFT, config.RIGHT):
                self._make_move_cb('U')
            if self._side in (config.UP, ):
                self._make_move_cb('B')
            if self._side in (config.DOWN, ):
                self._make_move_cb('F')
        elif (self._last_tile == (0, 0) and this_tile in [(0, 1), (0, 2)] or
              self._last_tile == (0, 1) and this_tile == (0, 2)):
            if self._side in (config.FRONT, config.UP, config.BACK, config.DOWN):
                self._make_move_cb('L')
            if self._side in (config.LEFT, ):
                self._make_move_cb('B')
            if self._side in (config.RIGHT, ):
                self._make_move_cb('F')
        elif (self._last_tile == (0, 2) and this_tile in [(0, 1), (0, 0)] or
              self._last_tile == (0, 1) and this_tile == (0, 0)):
            if self._side in (config.FRONT, config.UP, config.BACK, config.DOWN):
                self._make_move_cb('Li')
            if self._side in (config.LEFT, ):
                self._make_move_cb('Bi')
            if self._side in (config.RIGHT, ):
                self._make_move_cb('Fi')
        elif (self._last_tile == (0, 2) and this_tile in [(1, 2), (2, 2)] or
              self._last_tile == (1, 2) and this_tile == (2, 2)):
            if self._side in (config.FRONT, config.LEFT, config.RIGHT, config.BACK):
                self._make_move_cb('D')
            if self._side in (config.UP, ):
                self._make_move_cb('F')
            if self._side in (config.DOWN, ):
                self._make_move_cb('B')
        elif (self._last_tile == (2, 2) and this_tile in [(1, 2), (0, 2)] or
              self._last_tile == (1, 2) and this_tile == (0, 2)):
            if self._side in (config.FRONT, config.LEFT, config.RIGHT, config.BACK):
                self._make_move_cb('Di')
            if self._side in (config.UP, ):
                self._make_move_cb('Fi')
            if self._side in (config.DOWN, ):
                self._make_move_cb('Bi')
        elif (self._last_tile == (2, 0) and this_tile in [(2, 1), (2, 2)] or
              self._last_tile == (2, 1) and this_tile == (2, 2)):
            if self._side in (config.FRONT, config.UP, config.DOWN):
                self._make_move_cb('Ri')
            if self._side in (config.BACK, ):
                self._make_move_cb('Li')
            if self._side in (config.LEFT, ):
                self._make_move_cb('Fi')
            if self._side in (config.RIGHT, ):
                self._make_move_cb('Bi')
        elif (self._last_tile == (2, 2) and this_tile in [(2, 1), (2, 0)] or
              self._last_tile == (2, 1) and this_tile == (2, o)):
            if self._side in (config.FRONT, config.UP, config.DOWN):
                self._make_move_cb('R')
            if self._side in (config.BACK, ):
                self._make_move_cb('L')
            if self._side in (config.LEFT, ):
                self._make_move_cb('F')
            if self._side in (config.RIGHT, ):
                self._make_move_cb('B')
        self.refresh_cube()
        self._last_tile = None

    def _on_change_side(self, side):
        """Change side of cube view."""
        self._side = side
        self.refresh_cube()

    def _draw_rect(self, x, y, color):
        """Draw a rectange at given position with given color."""
        x = x + self._cube.coord_limit
        y = y + self._cube.coord_limit
        self._canvas.create_rectangle(x * self.TILE_SIZE, y * self.TILE_SIZE,
                                      x * self.TILE_SIZE + self.TILE_SIZE,
                                      y * self.TILE_SIZE + self.TILE_SIZE,
                                      fill=color)

    def refresh_cube(self):
        """Refresh the cube on screen."""
        for position, piece in self._cube.pieces.items():
            x, y, z = position
            if self._side == config.FRONT and z == self._cube.coord_limit:
                self._draw_rect(x, -y, self.COLOR_MAP[piece.z])
                continue
            if self._side == config.BACK and z == -self._cube.coord_limit:
                self._draw_rect(-x, -y, self.COLOR_MAP[piece.z])
                continue
            if self._side == config.UP and y == self._cube.coord_limit:
                self._draw_rect(x, z, self.COLOR_MAP[piece.y])
                continue
            if self._side == config.DOWN and y == -self._cube.coord_limit:
                self._draw_rect(x, -z, self.COLOR_MAP[piece.y])
                continue
            if self._side == config.LEFT and x == -self._cube.coord_limit:
                self._draw_rect(z, -y, self.COLOR_MAP[piece.x])
                continue
            if self._side == config.RIGHT and x == self._cube.coord_limit:
                self._draw_rect(-z, -y, self.COLOR_MAP[piece.x])
                continue

    def start(self, make_move, exit):
        """Start interactive mode, allowing the user to make moves."""
        self._make_move_cb = make_move
        self._window.protocol("WM_DELETE_WINDOW", lambda *args: self._exit(exit))
        self.refresh_cube()
        tk.mainloop()
