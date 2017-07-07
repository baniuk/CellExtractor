"""Extract information from QCONF file."""

import json


class ScanQconf:
    """Extract information from QCONF file."""

    keyMap = {'QDATE': ['createdOn'],
              'QIMAGE': ['obj', 'BOAState', 'boap', 'orgFile', 'path'],
              'QFRAME': ['obj', 'BOAState', 'boap', 'FRAMES'],
              'QSNAKES': ['obj', 'BOAState', 'nest', 'sHs'],
              'FINALS': 'finalSnakes',
              'BOUNDS': 'bounds',
              'CENTROID': 'centroid'}

    def __init__(self, fileName):
        """Initialize object Taking QCONF file name."""
        self.fileName = fileName
        self.qconf = open(fileName, 'r')
        self.js = json.load(self.qconf)

    def __del__(self):
        """Close QCONF file opened in constructor."""
        self.qconf.close()

    def getFileInfo(self):
        """Print object file name and parameters."""
        print(self.fileName, "at", self.__iteratreOver(self.keyMap["QDATE"]))
        print("Image:", self.__iteratreOver(self.keyMap["QIMAGE"]))
        print("Frames:", self.getNumFrames())

    def getNumFrames(self):
        """Return number of frames."""
        return self.__iteratreOver(self.keyMap["QFRAME"])

    def getSnakeHandler(self):
        """Return SnakeHandler."""
        sHs = self.__iteratreOver(self.keyMap["QSNAKES"])
        return sHs

    def getFinalSnakes(self):
        """
        Collect all final snakes into one list.

        Parse all cells on frame and concentrate them.
        """
        fs = []
        sHs = self.getSnakeHandler()

        for idx, val in enumerate(sHs):
            for sdx, sval in enumerate(val[self.keyMap["FINALS"]]):
                fs.append(sval)

        # print("\tProcessed", idx + 1, "handlers and", sdx + 1, "snakes")
        return fs

    def getBounds(self):
        """Return list of bounds for all final snakes."""
        b = []
        fs = self.getFinalSnakes()
        for sdx, sval in enumerate(fs):
            b.append(sval[self.keyMap["BOUNDS"]])
        return b

    def getCentroid(self):
        """Return list of cell centroids in the same order as getBounds."""
        c = []
        fs = self.getFinalSnakes()
        for sdx, sval in enumerate(fs):
            c.append(sval[self.keyMap["CENTROID"]])
        return c

    def __iteratreOver(self, key):
        """
        Return value for given key.

        Args:
            key: List of following subkeys to reach demanded parameter.
            Should start from root.

        Returns:
            Parmaeter under last provided key.

        """
        ans = self.js
        for k in key:
            ans = ans[k]

        return ans
