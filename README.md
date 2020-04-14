# Focus Stacking

Focus Stacking in Python

I wrote `focusstack`, a image simple focus stacking tool, for creating fun images with my microscope.

Per [Wikipedia](https://en.wikipedia.org/wiki/Focus_stacking): Focus stacking is a digital image processing technique which combines multiple images taken at different focus distances to give a resulting image with a greater depth of field (DOF) than any of the individual source images.

See [below](#how-it-works) for a longer explanation of the algorithm.

The ThoughtEmporium has a great explainer video [on Youtube](https://www.youtube.com/watch?v=3wfI_rEGyDw).

---
## Installation

`focusstack` can be installed by running `pip install focus-stack`. It requires Python 3.6.0+, OpenCV<3.4.2, and numpy.

You can use OpenCV 4.X+, but since the SIFT algorithm is proprietary, you must set `use_sift` in the source code to False.

Alternatively, you can install from source:
```bash
git clone https://github.com/momonala/focus-stack
cd focus-stack
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
                        Name of output image.
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
## How it Works:
The focus stacking algorithm works by preferentially selecting the most in-focus regions from a set of images, and combining them into an output image.

The user must first create a set of images with different focus planes, all taken from a fixed vantage point. The software will read all the images in, and align them, since changing focus can add some warping, or [perspective distortion](https://en.wikipedia.org/wiki/Perspective_distortion_(photography)), to the image. This tool uses the [SIFT](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_sift_intro/py_sift_intro.html) algorithm in OpenCV to find key-points in all the images, relative to the first in the set. A homography matrix is computed and used to warp the images and align those key points (and therefore the whole image, in theory).

Next we must find which parts of each image are most in-focus. This is done using the LaPlacian gradient. The LaPlacian gradient can be thought of as the second-order derivative of the image (where as the Sobel gradient would be the first order). It is measure of **how intensely** the pixels are changing. You can view the [Khan Academy's](https://www.youtube.com/watch?v=EW08rD-GFh0) video, or [PyImageSearch's blog](https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/) to get an intution for this concept.

![alt text](https://www.bogotobogo.com/python/OpenCV_Python/images/EdgeDetect/EdgeDetection.png)

All the images are blurred, using a Gaussian blur filter, to make some of the estimations easier. And the LaPlacian gradient is calculated. The maxiuum of the absolute value of the gradient is taken, and this is used as the proxy for the focus region.

All the images are stacked, and for each x,y location in the image, the maximum value of the stack is sent to the output image. And there we have it, a focus stacked image!

---

## License

MIT

This code and algorithm was inspired and adapted from the following sources:
- [StackOverflow thread](http://stackoverflow.com/questions/15911783/what-are-some-common-focus-stacking-algorithms)
- [Charles McGuinness' implementation on Github](https://github.com/cmcguinness/focusstack)
