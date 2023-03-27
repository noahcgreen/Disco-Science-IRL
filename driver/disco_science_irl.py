import itertools
import os
import pathlib
import time

import serial
from serial.tools import list_ports


class Game:

    """Interface for receiving color data from the in-game mod."""

    # Ingredient-to-color map
    INGREDIENT_COLORS = {
        'automation-science-pack': (1.0, 0.1, 0.1),
        'logistic-science-pack':   (0.1, 1.0, 0.1),
        'chemical-science-pack':   (0.2, 0.2, 1.0),
        'production-science-pack': (0.8, 0.1, 0.8),
        'military-science-pack':   (1.0, 0.5, 0.0),
        'utility-science-pack':    (1.0, 0.9, 0.1),
        'space-science-pack':      (0.8, 0.8, 0.8),
    }
    # Convert from [0, 1] to [0, 254]
    # 255 is not used since it is the serial delimiter.
    INGREDIENT_COLORS = {
        k: tuple(int(c * 254) for c in v)
        for k, v in INGREDIENT_COLORS.items()
    }

    # Colors to show when the game is inactive or there is no active research
    DEFAULT_COLORS = [(0.0, 0.0, 1.0)]
    DEFAULT_COLORS = [tuple(int(c * 254) for c in t) for t in DEFAULT_COLORS]

    # Time to wait for a heartbeat before declaring the game inactive
    PULSE = 1

    # In-game mod paths
    APPDATA_PATH = pathlib.Path(os.getenv('APPDATA'))
    SCRIPT_OUTPUT_PATH = APPDATA_PATH / 'Factorio/script-output/disco-science-irl'
    INGREDIENTS_FILE = SCRIPT_OUTPUT_PATH / 'ingredients.txt'
    HEARTBEAT_FILE = SCRIPT_OUTPUT_PATH / 'heartbeat'

    # Get the colors of the currently active research, or the default colors.
    def get_current_colors(self):
        try:
            text = self.INGREDIENTS_FILE.read_text()
        except FileNotFoundError:
            return self.DEFAULT_COLORS
        
        colors = [
            self.INGREDIENT_COLORS[ingredient]
            for ingredient in sorted(text.split())
            if ingredient in self.INGREDIENT_COLORS  # Ignore unknown ingredients
        ]

        return colors if colors else self.DEFAULT_COLORS
    
    # Check if the game is running.
    # Note: This will return true if the game is in a state where mods don't run,
    # e.g. if the tech tree is being viewed.
    def is_running(self):
        try:
            mtime = os.path.getmtime(self.HEARTBEAT_FILE)
        except FileNotFoundError:
            return False
        
        return time.time() - mtime < self.PULSE


class USBSerialConnection:

    """Interface for sending serial data over USB to the board."""

    # USB vendor and product ID's (Adafruit Flora)
    BOARD_VID = 9114
    BOARD_PID = 32772

    BAUD_RATE = 9600

    # Byte to denote the end of a color sequence
    DELIMITER = 255

    def __init__(self):
        self._serial = serial.Serial(baudrate=self.BAUD_RATE)
        self.is_connected = False
    
    def _get_port(self):
        """Get the port to which the board is attached.
        Throws a StopIteration if no such port is found."""
        return next(port for port in list_ports.comports() if port.vid == self.BOARD_VID and port.pid == self.BOARD_PID)
    
    def check_disconnect(self):
        """Check if the board has been disconnected."""
        try:
            self._get_port()
        except StopIteration:
            self.is_connected = False
    
    def connect(self):
        """Attempt to connect to the board.

        Sets is_connected, which should be queried to determine
        if the attempt was successful."""
        try:
            port = self._get_port()
        except StopIteration:
            self.is_connected = False
            return
    
        try:
            self._serial.port = port.device
        except serial.SerialException:
            self.is_connected = False
            return
        
        if not self._serial.is_open:
            try:
                self._serial.open()
            except serial.SerialException:
                self.is_connected = False
                return
        
        self.is_connected = True
        # Some delay is necessary between connecting and sending serial data
        time.sleep(1)
    
    def write(self, data):
        """Send a sequence of bytes to the board."""
        b = bytearray(data + [self.DELIMITER])
        try:
            self._serial.write(b)
        except serial.SerialException as e:
            self.is_connected = False
            print(e)


# Utility function to check if two lists have the same elements.
# This is used to check if the ingredient colors have changed and
# avoid unnecessary board writes if so.
def _same_contents(list_1, list_2):
    return len(list_1) == len(list_2) and all(x == y for x, y in zip(list_1, list_2))


class Driver:

    """High-level abstraction responsible for querying the game state and
    sending data to the board."""

    # Time to wait between actions (querying game, writing data, etc.)
    DELAY = 1

    def __init__(self):
        self.game = Game()
        self.usb_serial_connection = USBSerialConnection()
        self.colors = []
    
    def write_colors(self):
        """Send the current colors to the board."""
        self.usb_serial_connection.write(list(itertools.chain.from_iterable(self.colors)))
        
    def run(self):
        """Main loop."""
        connected = False
        game_running = False

        while True:
            # Check if the board has been disconnected (e.g. unplugged from USB)
            self.usb_serial_connection.check_disconnect()

            # Handle disconnection
            if connected and not self.usb_serial_connection.is_connected:
                connected = False
                print('Disconnected')
            
            while not self.usb_serial_connection.is_connected:
                self.colors = []  # Force a color write after connection
                self.usb_serial_connection.connect()
            
            # Handle connection
            if not connected and self.usb_serial_connection.is_connected:
                connected = True
                print('Connected')
            
            new_colors = self.colors

            if not self.game.is_running():
                if game_running:
                    game_running = False
                    print('Game stopped')
                new_colors = self.game.DEFAULT_COLORS
            else:
                if not game_running:
                    game_running = True
                    print('Game started')
            
                new_colors = self.game.get_current_colors()

            if not _same_contents(new_colors, self.colors):
                self.colors = new_colors
                print('Writing colors:', self.colors)
                self.write_colors()
            
            time.sleep(self.DELAY)


def main():
    Driver().run()


if __name__ == '__main__':
    main()
