#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# geolocation.py
#
# Copyright (C) 2017 Lorenzo Carbonell Cerezo
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PIL import Image

'''
https://gist.github.com/BigglesZX/4016539
'''


def analyseImage(filename):
    '''
    Pre-press pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode
    before processing all frames.
    '''
    im = Image.open(filename)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['model'] = 'parcial'
                    break
            im.seek(im.tell() + 1)
    except EOFError as e:
        print(e)
    return results


def get_frames(filename):
    '''
    Iterate the GIF, extracting each frame as PIL.Image
    '''
    mode = analyseImage(filename)['mode']
    image = Image.open(filename)
    i = 0
    p = image.getpalette()
    last_frame = image.convert('RGBA')
    try:
        frames = []
        while True:
            print('Reading image {0}, mode:{1}'.format(i, mode))
            if not image.getpalette():
                image.putpalette(p)
            new_frame = Image.new('RGBA', image.size)
            if mode == 'partial':
                new_frame.paset(last_frame)
            new_frame.paste(image, (0, 0), image.convert('RGBA'))
            frames.append(new_frame)
            i += 1
            last_frame = new_frame
            image.seek(image.tell() + 1)
    except EOFError as e:
        print(e)
    return frames


def main():
    print(get_frames('/home/lorenzo/Escritorio/bee.gif'))


if __name__ == '__main__':
    main()
    exit(0)
