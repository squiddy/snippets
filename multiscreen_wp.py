#!/usr/bin/env python

"""
Composite multiple wallpapers on one image that fits the current screen size.
Each wallpaper will be centered on each screen, scaling it down if needed.
"""

import argparse
import os
import random
import re
import subprocess


def find_screens():
    stdout, stdin = subprocess.Popen(["xrandr"], stdout=subprocess.PIPE).communicate()
    screen_size = map(int, re.findall(r'current (\d+) x (\d+)', stdout)[0])
    screens = re.findall(r'(\d+x\d+)\+(\d+\+\d+)', stdout)
    return screen_size, screens


def find_wallpapers_recursive(path):
    wallpapers = []
    for root, dirs, files in os.walk(path):
        for f in files:
            wallpapers.append(os.path.join(root,f))
    return wallpapers


def find_wallpapers(path):
    return map(lambda x: os.path.join(path, x), os.listdir(path))


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

    args = ["convert", "-size", "%dx%d" % tuple(screen_size), "xc:%s" % options.background]

    for dimensions, offset in screens:
        image = random.choice(wallpapers)
        args += ["(", image, "-resize", "%s>" % dimensions,
                 "-gravity", "center", "-background", options.background,
                 "-extent", dimensions, ")", "-gravity", "west",
                 "-geometry", "+%s" % offset, "-composite"]

    args += [options.outfile]

    subprocess.call(args)


if __name__ == '__main__':
    main()

