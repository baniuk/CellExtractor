"""Scale and pad cell images."""

import numpy
import scipy.misc
import unittest


def rescale(image, edge):
    """Rescale and pads image to get [edge, edge] size."""
    # Find largest edge
    largest = numpy.max(image.shape)

    res = scipy.misc.imresize(image, edge / largest)
    return pad(res, edge)


def pad(image, edge):
    """
    Pad smaller image to get [edge, edge] size.

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
    return numpy.pad(image, ((rowsup, rowsdown), (colsup, colsdown)), 'constant', constant_values=(0))


def process(im, size, counters, edge):
    """Process image cutting cells and adjusting size of of them.

    Args:
        im - full image to process
        size - (startx, starty, width, height) - bounding box for cell
        counters - {'padded': , 'rescaled'} - numbers that are increased during method call. Dict is referenced.
                    Use None if not needed.
        edge - demanded size of output image

    Returns:
        (cell)

    """
    # cut cell (not scaled yet, only QCONF data)
    cutCell = im[size[1]:size[3], size[0]:size[2]]
    # compare with demanded size
    if any(i > edge for i in cutCell.shape):
        cutCell = rescale(cutCell, edge)
        if counters:
            counters["rescaled"] += 1
        print(" [RESCALED]", sep=' ', end='', flush=True)
    else:
        cutCell = pad(cutCell, edge)
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
        out = pad(rr, 10)
        self.assertTupleEqual(rr.shape, out.shape)

    def testTwo(self):
        """Test if smaller input is padded on output."""
        rr = numpy.random.rand(7, 6)
        out = pad(rr, 10)
        self.assertTupleEqual(out.shape, (10, 10))

    def testRescale(self):
        """Test of reshape method."""
        rr = numpy.random.rand(10, 6) * 255
        out = rescale(rr, 5)
        self.assertTupleEqual(out.shape, (5, 5))


if __name__ == '__main__':
    unittest.main()
