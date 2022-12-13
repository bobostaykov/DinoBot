import os
import time
import webbrowser

import numpy as numpy
import pyautogui as pyautogui
from PIL import Image
from pynput.keyboard import Key, Controller

keyboard = Controller()


def main():
    # with Listener(on_press=on_press) as listener:
    #     listener.join()

    orchestrator()


# def on_press(key):
#     if key == Key.alt_r:
#         orchestrator()
#         return False
#     elif key == Key.ctrl_r:
#         return False


def orchestrator():
    """
    Decides, using screenshots, when the dino should jump
    or duck and sends the corresponding events
    """

    url = "https://dino-chrome.com/en"
    game_region = ()
    # line of pixels that crosses the dino and the cactuses
    lower_line = 260 - 35
    # line of pixels that crosses the birds
    upper_line = 260 - 65
    dino_right_border = 140
    # part of screenshot to skip while searching for the next cactus
    skip_region = 220
    # ratio between the dino speed and its jump length
    jump_space_ratio = 3

    webbrowser.open(url)
    # wait for the game to load and get its coordinates on screen
    while True:
        game_region = pyautogui.locateOnScreen('game_initial.png', confidence=0.95)
        if game_region is not None:
            break
    keyboard.press(Key.space)

    def halve_coordinates(region):
        new_region = (
            int(region[0] / 2),
            int(region[1] / 2),
            int(region[2] / 2),
            int(region[3] / 2),
        )
        return str(new_region).replace(' ', '')[1:-1]

    def screenshot():
        """ Makes a screenshot and updates the cactus positions """
        os.system(f'screencapture -x -R {halve_coordinates(game_region)} screenshot.png')
        image = Image.open('screenshot.png')
        image = numpy.array(image, dtype=numpy.uint8)
        pixels = [list(pixel[:3]) for pixel in image[lower_line]]
        for pos, pixel in enumerate(pixels[skip_region:]):
            if pixel[0] == 83:
                cactus_positions.append(skip_region + pos)
                break

    while True:
        # stores multiple positions of the same cactus to compute the speed of the dino
        cactus_positions = []
        # stores at what times the screenshots were taken, to calculate `time_delta`
        screenshot_time_array = []
        # time between the two screenshots
        time_delta = 0

        for i in range(2):
            screenshot_time_array.append(time.time())
            screenshot()
        if len(cactus_positions) == 2:
            time_delta = screenshot_time_array[1] - screenshot_time_array[0]
        elif len(cactus_positions) == 1:
            screenshot_time_array.append(time.time())
            screenshot()
            time_delta = screenshot_time_array[2] - screenshot_time_array[1]

        if len(cactus_positions) != 2:
            continue

        pos_delta = cactus_positions[0] - cactus_positions[1]
        if pos_delta == 0:
            # the dino stopped moving -> Game Over
            return
        # dino speed in pixels/sec
        speed = pos_delta / time_delta
        # number of pixels the cactus has to move before the dino has to jump
        pixels_to_jump = cactus_positions[1] - dino_right_border - speed / jump_space_ratio
        time_to_jump = pixels_to_jump / speed if speed != 0 else 0
        if time_to_jump > 0:
            time.sleep(time_to_jump)
        keyboard.press(Key.space)


if __name__ == '__main__':
    main()
