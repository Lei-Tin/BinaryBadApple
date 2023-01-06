import PIL.ImageQt

from config import *

import cv2
import os
import shutil
from PIL import Image
from PIL import ImageDraw, ImageFont

import ffmpeg
from typing import List
from math import ceil


def import_file() -> None:
    """Imports the file and creates a directory filled with the frames from the video
    """
    video = cv2.VideoCapture(FILENAME)

    success, image = video.read()
    count = 0

    # Deletes origFrames if exist
    shutil.rmtree('origFrames', ignore_errors=True)
    os.makedirs('origFrames')

    path = os.getcwd() + '/origFrames'

    while success:
        cv2.imwrite(os.path.join(path, "frame%d.jpg" % count), image)  # save frame as JPEG file
        success, image = video.read()
        count += 1


def resize(image: Image, new_width: int = 120) -> Image:
    old_width, old_height = image.size
    new_height = new_width * old_height / old_width
    return image.resize((int(new_width), int(new_height)))


def to_grayscale(image: Image) -> Image:
    return image.convert("L")


def pixel_to_ascii(image):
    pixels = image.getdata()
    ascii_str = ""

    for pixel in pixels:
        light_or_dark = 0 if pixel > 127 else 1
        ascii_str += CHARS[light_or_dark]

    return ascii_str


def convert_frame(image: Image) -> str:
    image = to_grayscale(image)
    return pixel_to_ascii(image)


def font_points_to_pixels(pt: int) -> int:
    return round(pt * 96 / 72)


def textfile_to_image(lst: List[str]):
    lst = tuple(lst)

    # choose a font (you can see more detail in the linked library on github)
    font = ImageFont.truetype(FONT, size=FONT_SIZE)
    margin_pixels = font_points_to_pixels(FONT_SIZE)

    # Figuring out the side length depending on the size of 0
    # 0 is the index of width of font and 1 is index of height of font
    side_length = max(font.getsize('0')[0], font.getsize('0')[1])

    # height of the background image
    image_height = int(ceil(side_length * len(lst) + 2 * margin_pixels))

    # width of the background image
    image_width = int(ceil(side_length * len(lst[0]) + 2 * margin_pixels))

    # draw the background
    background_color = 255  # white
    image = Image.new('L', (image_width, image_height), color=background_color)
    draw = ImageDraw.Draw(image)

    # draw each line of text
    font_color = 0  # black

    for i in range(len(lst)):
        vertical_position = int(i * side_length + margin_pixels)
        for j in range(len(lst[i])):
            horizontal_position = int(j * side_length + margin_pixels)
            draw.text((horizontal_position, vertical_position), lst[i][j],
                      fill=font_color,
                      font=font)

    return image


if __name__ == '__main__':
    # IMPORT FILE
    # The import_file() method should only be called once with the current video
    # After we have generated at least once, we can work with the frames inside
    import_file()

    # CREATE FRAMES
    if not os.path.exists('origFrames'):
        Exception('Error: Cannot find originalFrames to convert')
    else:
        shutil.rmtree('finalFrames', ignore_errors=True)

        os.makedirs('finalFrames')

        for frame in os.listdir('origFrames'):
            pic = PIL.Image.open(os.path.join('origFrames/', frame))

            # This 6 is an arbitrary number that I chose
            # The higher the number, the lower the resolution
            pic = resize(pic, new_width=pic.width // 6)

            img_width = pic.width

            ascii_str = convert_frame(pic)

            ascii_img = []

            for i in range(0, len(ascii_str), img_width):
                ascii_img.append(ascii_str[i:i + img_width])

            out_img = textfile_to_image(ascii_img)
            out_img.save(os.path.join('finalFrames/', frame))

            print(f'Converting {frame}...')

    # GENERATE VIDEO
    (
        ffmpeg
        .input('/finalFrames/*.jpg', pattern_type='glob', framerate=24)
        .output('final.mp4')
        .run()
    )
