"""Scale and pad cell images."""

import numpy
import scipy.misc
import unittest

def_pad_value = 0


def rescale(image, edge):
    """Rescale and pads image to get [edge, edge] size."""
    # Find largest edge
    largest = numpy.max(image.shape)

    res = scipy.misc.imresize(image, edge / largest)
    return pad(res, edge)


def pad(image, edge, mode, **kwargs):
    """
    Pad smaller image to get [edge, edge] size.

    mode, **kwargs - see numpy.pad

    Pads with zeros.
    """
    rows = edge - image.shape[0]
    cols = edge - image.shape[1]
    if any(i < 0 for i in (rows, cols)):
        print("\nWarning, image larger than requested box, scale first")
        return image
    rowsup = int(numpy.round(rows / 2))  # rows above
    rowsdown = int(rows - rowsup)  # rows below - may be different that above
    colsup = int(numpy.round(cols / 2))
    colsdown = int(cols - colsup)
    return numpy.pad(image, ((rowsup, rowsdown), (colsup, colsdown)), mode, **kwargs)


def cut(image, size, edge):
    """Cut object from image.

    Args:
        image - original image to process
        size - four element tuple (startx, starty, width, height) with coordinates to cut.
               If any is negative or larger than size of image, output image can be smaller than requested.
               endx, endy are ignored, edge parameter is used
        edge - requested width and height, if empty size[2] and size[3] are used. Cell is centered

    Returns:
        Cut image of size as given in nput or smaller if object was close to edge.

    """
    startx = size[0]
    starty = size[1]
    if edge:  # recentre and cut wit background
        startx -= (round((edge - size[2]) / 2) - 1)
        starty -= (round((edge - size[3]) / 2) - 1)
        endx = startx + edge
        endy = starty + edge
    else:  # cut as bounding box says
        endx = startx + size[2]
        endy = starty + size[3]

    if startx < 0:
        startx = 0
    elif startx >= image.shape[1]:
        startx = image.shape[1] - 1

    if starty < 0:
        starty = 0
    elif starty >= image.shape[0]:
        starty = image.shape[0] - 1

    if endx > image.shape[1]:  # not included then in slicing
        endx = image.shape[1]

    if endy > image.shape[0]:
        endy = image.shape[0]

    return image[starty:endy, startx:endx]


def process(im, size, counters, edge, trueBackground=False):
    """Process image cutting cells and adjusting size of them.

    If trueBackground==True, mean value is used for padding.

    Args:
        im - full image to process
        size - (startx, starty, width, height) - bounding box for cell, coordinates can lay outside image dimensions
        counters - {'padded':, 'rescaled'} - numbers that are increased during method call. Dict is referenced.
                    Use None if not needed.
        edge - demanded size of output image
        trueBackground - if True, natural object background from image is also taken (if requested size is bigger than
                         object)

    Returns:
        (cell)


    """
    # cut cell (not scaled yet, only QCONF data)
    if trueBackground:
        cutCell = cut(im, size, edge)  # with background surrounding cell (if on edge, output will be smaller)
    else:
        cutCell = cut(im, size, None)  # just BBox
    # compare with demanded size
    if any(i > edge for i in cutCell.shape):
        cutCell = rescale(cutCell, edge)
        if counters:
            counters["rescaled"] += 1
        print(" [RESCALED]", sep=' ', end='', flush=True)
    elif any(i < edge for i in cutCell.shape):  # if trueBackground==True output can be smaller and then is padded
        if trueBackground:
            cutCell = pad(cutCell, edge, 'edge')
        else:
            cutCell = pad(cutCell, edge, 'constant', constant_values=def_pad_value)
        if counters:
            counters['padded'] += 1
        print(" [PADDED]", sep=' ', end='', flush=True)
    return cutCell


class PadTests(unittest.TestCase):
    """
    Test of pad and rescale methods.

    These are very bad tests, just to check unittest.
    """

    def testOne(self):
        """Test if larger input is produced on output."""
        rr = numpy.random.rand(10, 11)
        out = pad(rr, 10, 'constant', constant_values=def_pad_value)
        self.assertTupleEqual(rr.shape, out.shape)

    def testTwo(self):
        """Test if smaller input is padded on output."""
        rr = numpy.random.rand(7, 6)
        out = pad(rr, 10, 'constant', constant_values=def_pad_value)
        self.assertTupleEqual(out.shape, (10, 10))

    def testRescale(self):
        """Test of reshape method."""
        rr = numpy.random.rand(10, 6) * 255
        out = rescale(rr, 5)
        self.assertTupleEqual(out.shape, (5, 5))

    def testCut(self):
        """Test of cut method."""
        rr = numpy.random.rand(10, 6) * 255
        out = cut(rr, (2, 2, 0, 0), 6)
        self.assertTupleEqual(out.shape, (6, 6))

    def testCut1(self):
        """Ending do not fit."""
        rr = numpy.random.rand(10, 6) * 255
        out = cut(rr, (3, 3, 0, 0), 7)
        self.assertTupleEqual(out.shape, (7, 6))  # cell inside image

    def testCut2(self):
        """Begining zero."""
        rr = numpy.random.rand(10, 6) * 255
        out = cut(rr, (0, 0, 0, 0), 7)
        self.assertTupleEqual(out.shape, (4, 4))  # cell on corner, output smaller, only existing pixels taken

    def testCut3(self):
        """One ending do not fit."""
        rr = numpy.random.rand(10, 6) * 255
        out = cut(rr, (1, 1, 0, 0), 10)
        self.assertTupleEqual(out.shape, (7, 6))

    def testCut4(self):
        """Fit perfectly."""
        rr = numpy.random.rand(10, 6) * 255
        out = cut(rr, (0, 0, 0, 0), 20)  # do not forget that cell is recentered
        self.assertTupleEqual(out.shape, (10, 6))  # whole image, but still smaller than 10x10

    def testCut5(self):
        """Fit."""
        rr = numpy.random.rand(10, 6) * 255
        out = cut(rr, (1, 1, 0, 0), 4)
        self.assertTupleEqual(out.shape, (4, 4))


if __name__ == '__main__':
    unittest.main()
