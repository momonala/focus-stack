# -*- coding: utf-8 -*-
"""
This code and algorithm was inspired and adapted from the following sources:
http://stackoverflow.com/questions/15911783/what-are-some-common-focus-stacking-algorithms
https://github.com/cmcguinness/focusstack

"""

import logging
from typing import List

import cv2
import numpy as np

DEBUG = False

# use SIFT or ORB for feature detection.
# SIFT generally produces better results, but it is not FOSS (OpenCV 4.X does not support it).
USE_SIFT = False if cv2.__version__ > "3.4.2" else True

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)


class FocusStacker(object):
    def __init__(
        self, laplacian_kernel_size: int = 5, gaussian_blur_kernel_size: int = 5,
    ) -> None:
        """Focus stacking class.
        Args:
            laplacian_kernel_size: Size of the laplacian window. Must be odd.
            gaussian_blur_kernel_size: How big of a kernel to use for the gaussian blur. Must be odd.
        """
        self._laplacian_kernel_size = laplacian_kernel_size
        self._gaussian_blur_kernel_size = gaussian_blur_kernel_size

    def focus_stack(self, image_files: List[str]) -> np.ndarray:
        """Pipeline to focus stack a list of images."""
        image_matrices = self._read_images(image_files)
        images = self._align_images(image_matrices)
        laplacian = self._compute_laplacian(images)
        focus_stacked = self._find_focus_regions(images, laplacian)
        return focus_stacked

    @staticmethod
    def _read_images(image_files: List[str]) -> List[np.ndarray]:
        """Read the images into numpy arrays using OpenCV."""
        logger.info("reading images")
        return [cv2.imread(img) for img in image_files]

    @staticmethod
    def _align_images(images: List[np.ndarray]) -> List[np.ndarray]:
        """Align the images.  Changing the focus on a lens, even if the camera remains fixed,
         causes a mild zooming on the images. We need to correct the images so they line up perfectly on top
        of each other.

        Args:
            images: list of image data
        """

        def _find_homography(
            _img1_key_points: np.ndarray, _image_2_kp: np.ndarray, _matches: List
        ):
            image_1_points = np.zeros((len(_matches), 1, 2), dtype=np.float32)
            image_2_points = np.zeros((len(_matches), 1, 2), dtype=np.float32)

            for j in range(0, len(_matches)):
                image_1_points[j] = _img1_key_points[_matches[j].queryIdx].pt
                image_2_points[j] = _image_2_kp[_matches[j].trainIdx].pt

            homography, mask = cv2.findHomography(
                image_1_points, image_2_points, cv2.RANSAC, ransacReprojThreshold=2.0
            )

            return homography

        logger.info("aligning images")
        aligned_imgs = []

        detector = cv2.xfeatures2d.SIFT_create() if USE_SIFT else cv2.ORB_create(1000)

        # Assume that image 0 is the "base" image and align all the following images to it
        aligned_imgs.append(images[0])
        img0_gray = cv2.cvtColor(images[0], cv2.COLOR_BGR2GRAY)
        img1_key_points, image1_desc = detector.detectAndCompute(img0_gray, None)

        for i in range(1, len(images)):
            img_i_key_points, image_i_desc = detector.detectAndCompute(images[i], None)

            if USE_SIFT:
                bf = cv2.BFMatcher()
                # This returns the top two matches for each feature point (list of list)
                pair_matches = bf.knnMatch(image_i_desc, image1_desc, k=2)
                raw_matches = []
                for m, n in pair_matches:
                    if m.distance < 0.7 * n.distance:
                        raw_matches.append(m)
            else:
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                raw_matches = bf.match(image_i_desc, image1_desc)

            sort_matches = sorted(raw_matches, key=lambda x: x.distance)
            matches = sort_matches[0:128]

            homography_matrix = _find_homography(
                img_i_key_points, img1_key_points, matches
            )
            aligned_img = cv2.warpPerspective(
                images[i],
                homography_matrix,
                (images[i].shape[1], images[i].shape[0]),
                flags=cv2.INTER_LINEAR,
            )

            aligned_imgs.append(aligned_img)
            if DEBUG:
                # If you find that there's a large amount of ghosting,
                # it may be because one or more of the input images gets misaligned.
                cv2.imwrite(f"aligned_{i}.png", aligned_img)

        return aligned_imgs

    def _compute_laplacian(self, images: List[np.ndarray],) -> np.ndarray:
        """Gaussian blur and compute the gradient map of the image. This is proxy for finding the focus regions.

        Args:
            images: image data
        """
        logger.info("Computing the laplacian of the blurred images")
        laplacians = []
        for image in images:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(
                gray,
                (self._gaussian_blur_kernel_size, self._gaussian_blur_kernel_size),
                0,
            )
            laplacian_gradient = cv2.Laplacian(
                blurred, cv2.CV_64F, ksize=self._laplacian_kernel_size
            )
            laplacians.append(laplacian_gradient)
        laplacians = np.asarray(laplacians)
        logger.debug(f"Shape of array of laplacian gradient: {laplacians.shape}")
        return laplacians

    @staticmethod
    def _find_focus_regions(
        images: List[np.ndarray], laplacian_gradient: np.ndarray
    ) -> np.ndarray:
        """Take the absolute value of the Laplacian (2nd order gradient) of the Gaussian blur result.
        This will quantify the strength of the edges with respect to the size and strength of the kernel (focus regions).

        Then create a blank image, loop through each pixel and find the strongest edge in the LoG
        (i.e. the highest value in the image stack) and take the RGB value for that
        pixel from the corresponding image.

        Then for each pixel [x,y] in the output image, copy the pixel [x,y] from
        the input image which has the largest gradient [x,y]

        Args:
            images: list of image data to focus and stack.
            laplacian_gradient: the laplacian of the stack. This is the proxy for the focus region.
                Should be size: (len(images), images.shape[0], images.shape[1])

        Returns:
            np.array image data of focus stacked image, size of orignal image

        """
        logger.info("Using laplacian gradient to find regions of focus, and stack.")
        output = np.zeros(shape=images[0].shape, dtype=images[0].dtype)
        abs_laplacian = np.absolute(laplacian_gradient)
        maxima = abs_laplacian.max(axis=0)
        bool_mask = np.array(abs_laplacian == maxima)
        mask = bool_mask.astype(np.uint8)

        for i, img in enumerate(images):
            output = cv2.bitwise_not(img, output, mask=mask[i])

        return 255 - output
