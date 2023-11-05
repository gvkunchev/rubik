import logging

import config
from model import Rubik
from view import Cli, Gui


class Controller:
    """Controller for a Rubik cube."""

    def __init__(self, size, interface=config.CLI):
        """Initializator."""
        assert interface in (config.CLI, config.GUI)
        self._cube = Rubik(size)
        if interface == config.CLI:
            self._view = Cli(self._cube)
        elif interface == config.GUI:
            self._view = Gui(self._cube)
        self._logger = None
        self._assign_logger()
    
    def _assign_logger(self):
        """Assign a file logger."""
        file_handler = logging.FileHandler(filename='rubik.log')
        logging.basicConfig(
            level=logging.DEBUG, 
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            handlers=[file_handler]
        )
        self._logger = logging.getLogger(name=__name__)
        self._logger.info('Starting new session.')
    
    def apply_notation(self, notation):
        """Apply a string defined notation."""
        for move in notation.split():
            getattr(self._cube, move)()
    
    def chess_pattern(self):
        """Apply a chess pattern."""
        self.apply_notation('R2 L2 B2 F2 U2 D2')

    def make_move_callback(self, move):
        """Callback for making a move."""
        try:
            self._logger.info(f'Calling instruction: {move}')
            getattr(self._cube, move)()
        except AttributeError:
            self._logger.error(f'Invalid instruction: {move}')
            return False
        return True

    def exit_callback(self):
        """Callback for exiting the app."""
        self._logger.info('Exit')
        return True

    def start(self):
        """Enter interactive mode for the user to make turns."""
        self._view.start(make_move=self.make_move_callback,
                         exit=self.exit_callback)



if __name__ == '__main__':
    #controller = Controller(size=3, interface=config.GUI)
    controller = Controller(size=3, interface=config.CLI)
    controller.start()
