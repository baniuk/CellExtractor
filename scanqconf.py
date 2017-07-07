"""Extract information from QCONF file."""


class ScanQconf:
    """Extract information from QCONF file."""

    def __init__(self, fileName):
        """Initialize object Taking QCONF file name."""
        self.fileName = fileName

    def getFileName(self):
        """Print object file name."""
        print(self.fileName)

    def getNumFrmaes(self):
        """Return number of frames"""
