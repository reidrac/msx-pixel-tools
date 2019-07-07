#!/usr/bin/env python3
#
# Copyright (C) 2019 by Juan J. Martinez <jjm@usebox.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from argparse import ArgumentParser
from PIL import Image
from collections import defaultdict

__version__ = "1.0"

DEF_W = 8
DEF_H = 8

# TOSHIBA palette
MSX_COLS = [
    (255,   0, 255),
    (0,   0,   0),
    (102, 204, 102),
    (136, 238, 136),
    (68,  68, 221),
    (119, 119, 255),
    (187,  85,  85),
    (119, 221, 221),
    (221, 102, 102),
    (255, 119, 119),
    (204, 204,  85),
    (238, 238, 136),
    (85, 170,  85),
    (187,  85, 187),
    (204, 204, 204),
    (238, 238, 238),
]


def to_hex_list_str(src):
    out = ""
    for i in range(0, len(src), 8):
        out += ', '.join(["0x%02x" % b for b in src[i:i + 8]]) + ",\n"
    return out


def to_hex_list_str_asm(src):
    out = ""
    for i in range(0, len(src), 8):
        out += '\tdb ' + ', '.join(["#%02x" % b for b in src[i:i + 8]])
        out += '\n'
    return out


def main():

    parser = ArgumentParser(description="PNG to MSX tiles",
                            epilog="Copyright (C) 2019 Juan J Martinez <jjm@usebox.net>",
                            )

    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__)
    parser.add_argument("-i", "--id", dest="id", default="tileset", type=str,
                        help="variable name (default: tileset)")
    parser.add_argument("-a", "--asm", dest="asm", action="store_true",
                        help="ASM output (default: C header)")
    parser.add_argument("--no-colors", dest="no_colors", action="store_true",
                        help="don't include colors")

    parser.add_argument("image", help="image to convert")

    args = parser.parse_args()

    try:
        image = Image.open(args.image)
    except IOError:
        parser.error("failed to open the image")

    if image.mode != "RGB":
        parser.error("not a RGB image")

    (w, h) = image.size

    if w % DEF_W or h % DEF_H:
        parser.error("%s size is not multiple of tile size (%s, %s)" %
                     (args.image, DEF_W, DEF_H))

    data = image.getdata()

    color_idx = defaultdict(list)
    color = []
    out = []
    ntiles = 0
    for y in range(0, h, DEF_H):
        for x in range(0, w, DEF_W):
            # tile data
            tile = [data[x + i + ((y + j) * w)]
                    for j in range(DEF_H) for i in range(DEF_W)]

            # get the attibutes of the tile
            # FIXME: this may not be right
            for i in range(0, len(tile), DEF_W):
                cols = list(set(tile[i:i + DEF_W]))

                if len(cols) > 2:
                    parser.error(
                        "tile %d (%d, %d) has more than two colors: %r" % (
                            ntiles, x, y, cols))
                elif len(cols) == 1:
                    cols.append(MSX_COLS[1])

                for c in cols:
                    if c not in MSX_COLS:
                        parser.error(
                            "tile %d (%d, %d) has a color not in the"
                            " expected MSX palette: %r" % (ntiles, x, y, c))

                # each tile has two color attributes per row
                color_idx[ntiles * DEF_H + i // DEF_W] = cols
                color.append(
                    (MSX_COLS.index(cols[1]) << 4) | MSX_COLS.index(cols[0]))

            frame = []
            for i in range(0, len(tile), 8):
                byte = 0
                p = 7
                for k in range(8):
                    # 0 or 1 is determined by the order in the color attributes
                    # for that row
                    byte |= color_idx[
                        ntiles * DEF_H + i // DEF_W].index(tile[i + k]) << p
                    p -= 1

                frame.append(byte)
            ntiles += 1
            out.extend(frame)

    if ntiles > 256:
        parser.error("more than 256 tiles")

    if args.asm:
        print(";; %d tiles\n" % ntiles)
        print("%s:" % args.id)
        print(to_hex_list_str_asm(out))

        if not args.no_colors:
            print("%s_col:" % args.id)
            print(to_hex_list_str_asm(color))
    else:
        print("#ifndef _%s_H" % args.id.upper())
        print("#define _%s_H\n" % args.id.upper())
        print("/* %d tiles */\n" % ntiles)

        data_out = to_hex_list_str(out)
        print("#ifdef LOCAL")
        print("const unsigned char %s[%d] = {\n%s\n};\n" %
              (args.id, len(out), data_out))

        if not args.no_colors:
            color_out = to_hex_list_str(color)
            print("const unsigned char %s_colors[%d] = {\n%s\n};\n" % (
                args.id, len(color), color_out))

        print("#else\n")
        print("extern const unsigned char %s[%d];" % (args.id, len(out)))

        if not args.no_colors:
            print("extern const unsigned char %s_colors[%d];" % (
                args.id, len(color)))

        print("#endif // LOCAL\n")
        print("#endif // _%s_H\n" % args.id.upper())


if __name__ == "__main__":
    main()
