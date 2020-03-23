# Focus Stacking

Focus Stacking in Python

I wrote `focusstack` for creating fun images with my microscope.

Per [Wikipedia](https://en.wikipedia.org/wiki/Focus_stacking): Focus stacking is a digital image processing technique which combines multiple images taken at different focus distances to give a resulting image with a greater depth of field (DOF) than any of the individual source images.

The ThoughtEmporium has a great explainer video [on Youtube](https://www.youtube.com/watch?v=3wfI_rEGyDw).

---
## Installation

`focusstack` can be installed by running `pip install focusstack`. It requires Python 3.6.0+, OpenCV<3.4.2, and numpy.

You can use OpenCV 4.X+, but since the SIFT algorithm is proprietary, you must set `use_sift` in the source code to False.

Alternatively, you can install from source:
```bash
git clone https://github.com/momonala/focus_stack
cd focus_stack
pip install  -e .
```

## Usage
```bash
focusstack -i input_dir -o output.png
```

Options:
```bash
$focusstack --help

usage: Tool to focus stack a list of images. [-h] -i INPUT -o OUTPUT
                                             [-d DEBUG] [-g GAUSSIAN]
                                             [-l LAPLACIAN]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        directory of images to focus stack
  -o OUTPUT, --output OUTPUT
                        Name of output image. Will be stored in /output.
  -d DEBUG, --debug DEBUG
                        Debug mode.
  -g GAUSSIAN, --gaussian GAUSSIAN
                        Size of gaussian blur kernel.
  -l LAPLACIAN, --laplacian LAPLACIAN
                        Size of laplacian gradient kernel.

```

`focusstack` is a well-behaved Unix-style command-line tool:

- it does nothing if no sources are passed to it;

- it will read images from the stated input directory, and write the output image relative to the current working directory.

- exits with code 0 unless an internal error occurred.


---

### License

MIT

This code and algorithm was inspired and adapted from the following sources:
- [StackOverflow thread](http://stackoverflow.com/questions/15911783/what-are-some-common-focus-stacking-algorithms)
- [Charles McGuinness' implementation on Github](https://github.com/cmcguinness/focusstack)