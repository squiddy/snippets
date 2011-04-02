#!/usr/bin/env python

"""
Composite multiple wallpapers on one image that fits the current total screen
size. Each wallpaper will be centered on each screen, scaling it down if needed.
"""

from __future__ import division

import argparse
import os
import random
import re
import subprocess
from collections import defaultdict


def subprocess_output(args):
    stdout, stdin = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
    return stdout


def find_screens():
    data = subprocess_output(["xrandr"])
    screen_size = map(int, re.findall(r'current (\d+) x (\d+)', data)[0])
    matches = re.findall(r'(\d+x\d+)\+(\d+\+\d+)', data)
    screens = []
    for dimensions, offset in matches:
        # Calculate aspect ratio. Used to find the wallpaper from the sample
        # that fits this screen best.
        width, height = map(int, dimensions.split('x'))
        screens.append((dimensions, offset, width / height))

    return screen_size, screens


def get_image_size(path):
    data = subprocess_output(["identify", path])
    width, height = map(int, re.findall(r'(\d+)x(\d+)\s', data)[0])
    return width, height


def find_wallpapers_recursive(path):
    wallpapers = []
    for root, dirs, files in os.walk(path):
        for f in files:
            wallpapers.append(os.path.join(root,f))
    return wallpapers


def find_wallpapers(path):
    return map(lambda x: os.path.join(path, x), os.listdir(path))


def find_best_fit(wallpapers, screens):
    mappings = defaultdict(list)
    for dimensions, offset, aspect_ratio in screens:
        for image in wallpapers:
            width, height = get_image_size(image)
            mappings[offset].append((abs(aspect_ratio - width / height), image))

    for screen in mappings:
        mappings[screen] = [image for (difference, image) in sorted(mappings[screen])]

    for screen in mappings:
        for screen2 in mappings:
            if screen == screen2:
                continue
            mappings[screen2].remove(mappings[screen][0])
    return mappings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-b", "--background", help="Background color to use.", default="black")
    parser.add_argument("-r", "--recursive", help="Search recursivly.", action="store_true")
    parser.add_argument("-f", "--folder", help="Where to look for images.", required=True)
    parser.add_argument("outfile", help="Filename the wallpaper will be saved as.")
    options = parser.parse_args()

    if options.recursive:
        wallpapers = find_wallpapers_recursive(options.folder)
    else:
        wallpapers = find_wallpapers(options.folder)

    screen_size, screens = find_screens()
    chosen_wallpapers = random.sample(wallpapers, len(screens))

    mappings = find_best_fit(chosen_wallpapers, screens)

    args = ["convert", "-size", "%dx%d" % tuple(screen_size), "xc:%s" % options.background]

    for dimensions, offset, aspect_ratio in screens:
        image = mappings[offset][0]
        args += ["(", image, "-resize", "%s" % dimensions,
                 "-gravity", "center", "-background", options.background,
                 "-extent", dimensions, ")", "-gravity", "west",
                 "-geometry", "+%s" % offset, "-composite"]

    args += [options.outfile]

    subprocess.call(args)


if __name__ == '__main__':
    main()

