"""Prepare training data."""

from getQconfs import scanFolder
import pprint
from scanqconf import ScanQconf
import numpy as np
import matplotlib.pyplot as plt
import pandas
from os import path
from scipy import ndimage
from scipy import misc
from skimage import io

# where cut images land in
outputFolder = "c:\\Users\\baniu\\OneDrive\\CellExtractor_Test\out"
# folder with QCONF and images
inputFolder = "c:\\Users\\baniu\\OneDrive\\CellExtractor_Test"

pp = pprint.PrettyPrinter(indent=4)
allBounds = []  # will store bounds dictionary
allCentroids = []  # centroids in order of bounds
allImages = []  # paths to images
allFrameId = []  # frame indexes

# folder to scan
fileList = scanFolder(inputFolder)

# iterate over QCONF files and extract bounds
for qconf in fileList:
    sq = ScanQconf(qconf)  # analyse qconf
    sq.getFileInfo()  # print info
    b, c, n = sq.getAll()
    allBounds.extend(b)  # collect bounds for thi file (all nakes)
    allCentroids.extend(c)  # colect centroids
    allImages.extend(n)  # colect images from Qconf
    allFrameId.extend(np.linspace(1, sq.getNumFrames(),
                                  sq.getNumFrames(), dtype="int"))

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

# %% Process images
for count, image in enumerate(allImages):
    # assumes images in the same folder as QCONF regardless path in QCONF
    absImagePath = path.join(inputFolder, path.basename(image))
    im = io.imread(absImagePath)
    # im is ordered [slices x y]
    # compute indexes
    frame = allFrameId[count]
    startx = allBounds[count]['x']
    width = startx + allBounds[count]['width']
    starty = allBounds[count]['y']
    height = starty + allBounds[count]['height']

    print("Processing", path.basename(image), im.shape, "frame", frame)
    cutCell = im[frame - 1][starty:height, startx:width]
    outFileName = path.join(
        outputFolder, path.basename(image) + "_" + str(count) + ".png")
    io.imsave(outFileName, cutCell)

    # plt.subplot(1, 2, 1)
    # plt.imshow(im[199], cmap=plt.cm.gray)
    #  plt.axis('off')
    # plt.subplot(1, 2, 2)
    # plt.imshow(cutCell, cmap=plt.cm.gray)
    # plt.axis('off')
    # plt.show()
