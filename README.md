# Disco Science IRL

Disco Science IRL pulls the active research ingredients from a Factorio
game and lights up an LED lamp with their colors. This repository contains
all of the material used in the project (source code and 3D models).

For a more detailed writeup and video, [read about this project on my website](https://noahc.green/projects/disco_science_irl/).

The rest of this README describes how to get the project up and running.

## Requirements

This project assumes the board is an Adafruit Flora v3 and Factorio is
running on Windows. Other Arduino-compatible boards should be usable;
just make sure to update the USB VID/PID in the driver as well as the
LED pin in the board code. To run on Linux, mod paths in the driver will
need to be changed.

## Installation

There are three components which need to be installed individually:

1. Install the Factorio mod.

    Copy the `mod\disco-science-irl` folder into `%APPDATA%\Factorio\mods`.
    Start the game and ensure that the mod is enabled.

    Since this is a one-off project, there is no mod in the in-game mod
    portal.

2. Flash the board.

    Upload `board\disco_science_irl.ino` to the Flora using Arduino IDE or similar.

3. Install the driver.

    The driver for this project requires Python 3. Execute the following,
    preferably in a virtual environment:
    ```bash
    $ pip install -r driver/requirements.txt
    $ python driver/build.py
    ```
    This will create an executable `dist\disco_science_irl.exe`. Run this
    program, or create a shortcut to it in your startup folder so it will
    run automatically on login.

## Usage

After following the steps above, just run the driver executable
(double-click `dist\disco_science_irl.exe`), plug the board into your
computer, and play the game!
