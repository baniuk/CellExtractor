"""
Resolve names of QuimP files.

By default QuimP is run on certain file and then outputted configuration file (QCONF) inherits that name. Image is also
remembered inside QCONF. But there is still possibility to use configuration file with other images from the same
experiment (e.g different dye) if they have the same geometry.

This package generates possible names of images using base name and expected tails given by user. Base name must contain
one of tails already. Typically base name should be the QCONF filename or name of image referenced in it. E.g: There are
following files in folder:
KZ4-220214-ABD-GFP-dev6h-agar2+TRITC-2.lsm
KZ4-220214-ABD-GFP-dev6h-agar2+TRITC-2.lsm_CH_1.pgQP
KZ4-220214-ABD-GFP-dev6h-agar2+TRITC-2.lsm_CH_1.QCONF
KZ4-220214-ABD-GFP-dev6h-agar2+TRITC-2.lsm_CH_1.tif
KZ4-220214-ABD-GFP-dev6h-agar2+TRITC-2.lsm_CH_1_0.stQP.csv
KZ4-220214-ABD-GFP-dev6h-agar2+TRITC-2.lsm_CH_1_snakemask.tif
KZ4-220214-ABD-GFP-dev6h-agar2+TRITC-2.lsm_CH_2.tif
KZ4-220214-ABD-GFP-dev6h-agar2+TRITC-2.lsm_CH_DIC.tif

resolveNames(KZ4-220214-ABD-GFP-dev6h-agar2+TRITC-2.lsm_CH_1.QCONF, ("_CH_1","_CH_DIC")) will return names:
KZ4-220214-ABD-GFP-dev6h-agar2+TRITC-2.lsm_CH_1.tif
KZ4-220214-ABD-GFP-dev6h-agar2+TRITC-2.lsm_CH_DIC.tif

All image files should inherit common base and different endings: _CH_1, _CH_2, _CH_1_snakemask,....
User must provide all expected endings and (obligatory) that one that is contained in basename passed to method.
Providing empty tail list will return full base name as passed to method.
"""

import os
import unittest

imageExt = ".tif"


def resolveNames(qconfname, tails):
    """Reslove file names using common core and expected tails.

    Args:
        qconfname - name of original file with extension or without.
        tails - list of expected tails. If they contain extensions, output list will contain them as well.
                If there is no extension, .tif is added

    Return:
        List of file names coreTail.tif (in order as they appeared in tails) or qconfname if tails are empty
    """
    if not tails:
        return (qconfname,)
    # remove extension if exist
    qconfname = os.path.splitext(qconfname)[0]
    # Get core name
    # iterate over tails
    basename = None
    for tail in tails:
        # deconstruct for name.ext
        tailext = os.path.splitext(tail)
        # check if there is common name with qconfname
        if qconfname.find(tailext[0]) != -1:
            basename = qconfname[0:qconfname.find(tailext[0])]
            break
    # check if one tail can be found in base name
    if not basename:
        raise ValueError("One of tails should be the same as given base name.")
    # form output
    ret = []
    for tail in tails:
        if not os.path.splitext(tail)[1]:
            ext = imageExt
        else:
            ext = ''
        ret.append(basename + tail + ext)

    return tuple(ret)


class ResolveNamesTest(unittest.TestCase):
    """Test unit for resolveNames."""

    def testOne(self):
        """Test if original tail is given as first."""
        ret = resolveNames("qconfname_CH_1.QCONF", ("_CH_1", "_CH_2", "_CH_1_snakemask"))
        self.assertTupleEqual(ret, ("qconfname_CH_1.tif", "qconfname_CH_2.tif", "qconfname_CH_1_snakemask.tif"))

    def testTwo(self):
        """Test if original tail is given as not first."""
        ret = resolveNames("qconfname_CH_1.QCONF", ("_CH_2", "_CH_1", "_CH_1_snakemask"))
        self.assertTupleEqual(ret, ("qconfname_CH_2.tif", "qconfname_CH_1.tif", "qconfname_CH_1_snakemask.tif"))

    def testTwo1(self):
        """Test if original tail is given as not first. No extension in basename."""
        ret = resolveNames("qconfname_CH_1", ("_CH_2", "_CH_1", "_CH_1_snakemask"))
        self.assertTupleEqual(ret, ("qconfname_CH_2.tif", "qconfname_CH_1.tif", "qconfname_CH_1_snakemask.tif"))

    def testThree(self):
        """Test if original tail is given as not first. Tails with extensions."""
        ret = resolveNames("qconfname_CH_1.QCONF", ("_CH_2.tif", "_CH_1.tif", "_CH_1_snakemask.tif"))
        self.assertTupleEqual(ret, ("qconfname_CH_2.tif", "qconfname_CH_1.tif", "qconfname_CH_1_snakemask.tif"))

    def testFour(self):
        """No original tail given."""
        with self.assertRaises(ValueError):
            resolveNames("qconfname_CH_1.QCONF", ("_CH_2", "_CH_3", "_CH_1_snakemask"))

    def testFive(self):
        """Test if full original name is returned."""
        ret = resolveNames("qconfname_CH_1.QCONF", ())
        self.assertTupleEqual(ret, ("qconfname_CH_1.QCONF",))


if __name__ == '__main__':
    unittest.main()
