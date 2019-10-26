#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of GQRCode
#
# Copyright (c) 2012-2019 Lorenzo Carbonell Cerezo <a.k.a. atareao>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
