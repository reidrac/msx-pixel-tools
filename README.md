# MSX Pixel Tools

These are few simple tools I used to make [Night Knight](https://www.usebox.net/jjm/night-knight/).

Convert PNG images into sprites and tilesets to be used by the MSX in screen 2 mode.

* `png2sprites.py`
* `png2tileset.py`
* `png2scr.py`

Each tool has help in the `CLI` with `-h`.

The output is dumped in `stdout`, so you can redirect it to a file:
```
./png2sprites.py examples/sprites.png > sprites.h
```

The expected colours are those of the Thoshiba palette. See
[this file](https://github.com/reidrac/8-bit-gimp-palettes/blob/master/MSX.gpl) for
further info about the RGB values.

When the output is a C include file, it is wrapped and `ifdef` block with a
`LOCAL` define to specify when the data is extern or not.

```C
/* in the file including the data */
#define LOCAL
#include "sprites.h"
#undef LOCAL

...
/* in any other file */
#include "sprite.h"
```

The ASM output can be easily modified in case your assambler doesn't support the
same syntax.

## Requirements

* Python 3
* Pillow

## png2sprites

Converts a RGB PNG image to MSX Screen 2 16x16 pixels sprite data.

RGB(28, 28, 28) is used for transparent and any other colour will be expanded
to its own sprite. See the example: it has two frames with two colors and the
end result is 4 frames (2 for each color).

## png2tiles

Converts a RGB PNG image to a MSX Screen 2 tileset.

The output is limited to 256 tiles.

## png2scr

Converts a RGB 256x192 PNG image to a SCR file to be loaded on an MSX in Screen
2 mode.

The output is a binary file (to stdout) with the tile data followed by the
colour information.

