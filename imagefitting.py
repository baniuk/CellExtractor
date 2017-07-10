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

    if (rows, cols) < (0, 0):
        print("Warning, image larger than requested box, scale first")
        return image

    rowsup = int(numpy.round(rows / 2))  # rows above
    rowsdown = int(rows - rowsup)  # rows below - may be different that above

    colsup = int(numpy.round(cols / 2))
    colsdown = int(cols - colsup)

    return numpy.pad(image, ((rowsup, rowsdown), (colsup, colsdown)),
                     'constant', constant_values=(0))


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
