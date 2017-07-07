"""Prepare training data."""

from getQconfs import scanFolder
import pprint
from scanqconf import ScanQconf

list = scanFolder("/home/baniuk/Documents/Kay-copy/FLU+DIC")

sq = ScanQconf(list[0])

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(list)

sq.getFileName()
