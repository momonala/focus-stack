# -*- coding: utf-8 -*-
"""Makes the focus_stack directory executable as a script."""

import logging
import os
from glob import glob
from argparse import ArgumentParser

import cv2

from .focus_stack import FocusStacker

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)


def main():
    _parser = ArgumentParser(prog="Tool to focus stack a list of images.")
    _parser.add_argument(
        "-i",
        "--input",
        help="directory of images to focus stack",
        required=True,
        type=str,
    )
    _parser.add_argument(
        "-o", "--output", help="Name of output image.", required=True, type=str,
    )
    _parser.add_argument(
        "-d", "--debug", help="Debug mode.", default=False, required=False, type=bool,
    )
    _parser.add_argument(
        "-g",
        "--gaussian",
        help="Size of gaussian blur kernel.",
        default=5,
        required=False,
        type=int,
    )
    _parser.add_argument(
        "-l",
        "--laplacian",
        help="Size of laplacian gradient kernel.",
        default=5,
        required=False,
        type=int,
    )

    args = _parser.parse_args()
    image_files = sum(
        [glob(f"{args.input}/*.{ext}") for ext in ["jpg", "png", "jpeg", "JPG"]], []
    )
    logger.debug(f"Processing files {image_files}")
    stacker = FocusStacker(
        laplacian_kernel_size=args.laplacian, gaussian_blur_kernel_size=args.gaussian
    )
    stacked = stacker.focus_stack(image_files)

    if os.path.exists(args.output):
        logger.info(f"overwriting image {args.output}")
    else:
        logger.info(f"writing image {args.output}")
    cv2.imwrite(args.output, stacked)

    os.system(f"open { args.output}")
