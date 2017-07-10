"""Prepare training data."""


import numpy as np
import matplotlib.pyplot as plt
import pandas
import sys
import getopt
from getQconfs import scanFolder
from imagefitting import pad, rescale
from scanqconf import ScanQconf
from os import path
from skimage import io


def parseProgramArgs(argv):
    """Parse cmd."""
    inputFolder = ''
    outputFolder = ''
    showPlot = False
    try:
        opts, args = getopt.getopt(argv, "hpi:o:", ["indir=", "outdir="])
    except getopt.GetoptError as err:
        print("preparedata.py -i <inputfolder> -o <outputfolder>")
        print(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("preparedata.py -i <inputfolder> -o <outputfolder>")
            print("\t -h\tShow help")
            print("\t -p\tShow size distribution")
            sys.exit()
        elif opt in ("-i", "--indir"):
            inputFolder = arg
        elif opt in ("-o", "--outdir"):
            outputFolder = arg
        elif opt == "-p":
            showPlot = True
    if not inputFolder:
        print("No <indir> option")
        sys.exit(2)
    elif not outputFolder:
        print("No <outdir> option")
        sys.exit(2)
    return inputFolder, outputFolder, showPlot


def main(argv):
    """Execute all."""
    inputFolder, outputFolder, showPlot = parseProgramArgs(argv)

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
        allFrameId.extend(np.linspace(1, sq.getNumFrames(), sq.getNumFrames(), dtype="int"))

    # convert bounds to array [x y width height]
    bounds = []
    for b in allBounds:
        bounds.append([b["x"], b["y"], b["width"], b["height"]])
    bounds = np.array(bounds)  # convert to numpy

    # %% compute basic stats - 1st 2nd and 3rd quartile
    med = np.percentile(bounds[:, (2, 3)], (25, 50, 75), axis=0)
    pmed = pandas.DataFrame(med, columns=['Width', 'Height'], index=['25', '50', '75'])
    pbounds = pandas.DataFrame(bounds[:, (2, 3)], columns=['Width', 'Height'])
    pbounds.plot.box()
    if showPlot:
        plt.show()

    # %% Compute range of data
    ranges = pandas.DataFrame(pbounds.min(), columns=['min'])
    ranges['max'] = pandas.DataFrame(pbounds.max(), columns=['max'])
    ranges = ranges.T  # transpose to have same orientation as med

    # %% Process images
    recWidth = pmed['Width']['75']  # use 75% quartile size
    recHeight = pmed['Height']['75']
    # length of edge of all images (square)
    edge = np.round(np.max([recWidth, recHeight]))
    rescaled = 0  # number of rescaled
    padded = 0  # number of padded
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
        print("Processing", path.basename(image), im.shape, "frame", frame,  sep=' ', end='', flush=True)
        cutCell = im[frame - 1][starty:height, startx:width]
        # compare with pattern
        if cutCell.shape > (edge, edge):
            cutCell = rescale(cutCell, edge)
            print(" [RESCALED]", sep=' ', end='', flush=True)
            rescaled += 1
        else:
            cutCell = pad(cutCell, edge)
            print(" [PADDED]", sep=' ', end='', flush=True)
            padded += 1
        print("")
        outFileName = path.join(outputFolder, path.basename(image) + "_" + str(count) + ".png")
        io.imsave(outFileName, cutCell)

    print(pmed)
    print(ranges)
    print("Selected image size: ", edge)
    print(repr(rescaled) + '/' + repr(count + 1) + " were rescaled, " +
          repr(padded) + '/' + repr(count + 1) + " were padded")


if __name__ == "__main__":
    main(sys.argv[1:])
