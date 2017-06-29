# -*- coding: utf-8 -*-
import gi
try:
    gi.require_version('GLib', '2.0')
    gi.require_version('GdkPixbuf', '2.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import GLib
from gi.repository import GdkPixbuf
from PIL import Image
import os


def image2pixbuf(image):
    data = image.tobytes()
    w, h = image.size
    data = GLib.Bytes.new(data)
    if image.mode == 'RGB':
        return GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                               False, 8, w, h, w * 3)
    elif image.mode == '1':
        print(5)
        image = image.convert('RGBA')
        data = image.tobytes()
        w, h = image.size
        data = GLib.Bytes.new(data)
        return GdkPixbuf.Pixbuf.new_from_bytes(data,
                                               GdkPixbuf.Colorspace.RGB,
                                               True, 8, w, h, w * 4)
    else:
        print(3)
        print(image.mode)
        print(type(image), image.mode, '----')
        print(4)
        return GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                               True, 8, w, h, w * 4)


def pixbuf2image(pixbuf):
    data = pixbuf.get_pixels()
    w = pixbuf.props.width
    h = pixbuf.props.height
    stride = pixbuf.props.rowstride
    if pixbuf.props.has_alpha is True:
        mode = 'RGBA'
    else:
        mode = 'RGB'
    return Image.frombytes(mode, (w, h), data, 'raw', mode, stride)


def draw_qrcode_to_pilimage(qrmatrix):
    unit_len = 10
    x = y = 4*unit_len
    pic = Image.new('1', [(len(qrmatrix)+8)*unit_len]*2, 'white')

    for line in qrmatrix:
        for module in line:
            if module:
                draw_a_black_unit(pic, x, y, unit_len)
            x += unit_len
        x, y = 4*unit_len, y+unit_len
    return pic


def draw_qrcode(abspath, qrmatrix):
    unit_len = 3
    x = y = 4*unit_len
    pic = Image.new('1', [(len(qrmatrix)+8)*unit_len]*2, 'white')

    for line in qrmatrix:
        for module in line:
            if module:
                draw_a_black_unit(pic, x, y, unit_len)
            x += unit_len
        x, y = 4*unit_len, y+unit_len

    saving = os.path.join(abspath, 'qrcode.png')
    pic.save(saving)
    return saving


def draw_a_black_unit(p, x, y, ul):
    for i in range(ul):
        for j in range(ul):
            p.putpixel((x + i, y + j), 0)
