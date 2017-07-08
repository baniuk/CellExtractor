"""Prepare training data."""

from getQconfs import scanFolder
import pprint
from scanqconf import ScanQconf
import numpy as np
import matplotlib.pyplot as plt
import pandas

pp = pprint.PrettyPrinter(indent=4)
allBounds = []  # will store bounds dictionary
allCentroids = []  # centroids in order of bounds

# folder to scan
fileList = scanFolder("c:\\Users\\baniu\\OneDrive\\CellExtractor_Test")

# iterate over QCONF files and extract bounds
for qconf in fileList:
    sq = ScanQconf(qconf)  # analyse qconf
    sq.getFileInfo()  # print info
    allBounds.extend(sq.getBounds())  # collect bounds for thi file (all nakes)
    allCentroids.extend(sq.getCentroid())  # colect centroids

# convert bounds to array [x y width height]
bounds = []
for b in allBounds:
    bounds.append([b["x"], b["y"], b["width"], b["height"]])
bounds = np.array(bounds)  # convert to numpy

# %% compute basic stats - 1st 2nd and 3rd quartile
med = np.percentile(bounds[:, (2, 3)], (25, 50, 75), axis=0)
pmed = pandas.DataFrame(
    med, columns=['Width', 'Height'], index=['25', '50', '75'])
pmed.plot.box()
print(pmed)
plt.show()
# %% Compute range of data
ranges = pandas.DataFrame(pmed.min(), columns=['min'])
ranges['max'] = pandas.DataFrame(pmed.max(), columns=['max'])
ranges = ranges.T  # transpose to have same orientation as med
print(ranges)
