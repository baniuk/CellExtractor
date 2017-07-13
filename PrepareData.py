"""Prepare training data."""


import numpy as np
import matplotlib.pyplot as plt
import pandas
import sys
import getopt
from getQconfs import scanFolder
from imagefitting import process
from scanqconf import ScanQconf
from os import path
from skimage import io


def parseProgramArgs(argv):
    """Parse cmd."""
    inputFolder = ''
    outputFolder = ''
    showPlot = False
    processMasks = False
    outSize = None
    try:
        opts, args = getopt.getopt(argv, "hpmi:o:s:", ["indir=", "outdir=", "size="])
    except getopt.GetoptError as err:
        print("preparedata.py -i <inputfolder> -o <outputfolder>")
        print(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("preparedata.py -i <inputfolder> -o <outputfolder>")
            print("\t -h\tShow help")
            print("\t -p\tShow size distribution")
            print("\t -m\tProcess snakemasks")
            print("\t -s,--size=\tSize of output images")
            sys.exit()
        elif opt in ("-i", "--indir"):
            inputFolder = arg
        elif opt in ("-o", "--outdir"):
            outputFolder = arg
        elif opt == "-p":
            showPlot = True
        elif opt == "-m":
            processMasks = True
        elif opt in ("-s", "--size"):
            outSize = arg
    if not inputFolder:
        print("No <indir> option")
        sys.exit(2)
    elif not outputFolder:
        print("No <outdir> option")
        sys.exit(2)
    return inputFolder, outputFolder, showPlot, processMasks, outSize


def main(argv):
    """Execute all."""
    inputFolder, outputFolder, showPlot, processMasks, outSize = parseProgramArgs(argv)

    allBounds = []  # will store bounds dictionary
    allCentroids = []  # centroids in order of bounds
    allImages = []  # paths to images
    allFrameId = []  # frame indexes

    # folder to scan
    fileList = scanFolder(inputFolder)

    # iterate over QCONF files and extract information. Produce lists of the same lengths that contain data on related
    # indexes. Some data are simply repeated along one QCONF
    for qconf in fileList:
        sq = ScanQconf(qconf)  # analyse qconf
        sq.getFileInfo()  # print info
        b, c, n = sq.getAll()  # outputs are dicts
        allBounds.extend(b)  # collect bounds for this file (all snakes)
        allCentroids.extend(c)  # colect centroids
        # colect image name from Qconf (repeated for each QCONF)
        allImages.extend(n)
        allFrameId.extend(np.linspace(1, sq.getNumFrames(),
                                      sq.getNumFrames(), dtype="int"))  # frame range 1...N

    # convert bounds to array [x y width height]
    bounds = []
    for b in allBounds:
        bounds.append([b["x"], b["y"], b["width"], b["height"]])  # unwrap dict
    bounds = np.array(bounds)  # convert to numpy

    # %% compute basic stats - 1st 2nd and 3rd quartile
    # quartiles from width and height
    med = np.percentile(bounds[:, (2, 3)], (25, 50, 75), axis=0)
    pmed = pandas.DataFrame(med, columns=['Width', 'Height'], index=[
                            '25', '50', '75'])  # convert to tables
    pbounds = pandas.DataFrame(bounds[:, (2, 3)], columns=['Width', 'Height'])
    if showPlot:
        pbounds.plot.box()
        plt.show()

    # %% Compute range of data
    ranges = pandas.DataFrame(pbounds.min(), columns=['min'])
    ranges['max'] = pandas.DataFrame(pbounds.max(), columns=['max'])
    ranges = ranges.T  # transpose to have same orientation as med

    # %% Process images
    recWidth = pmed['Width']['75']  # use 75% quartile size
    recHeight = pmed['Height']['75']
    if not outSize:
        # length of edge of all images (square) - larger one among selected quartile for width and height
        edge = np.round(np.max([recWidth, recHeight]))
    else:
        print("Use provided size", outSize)
        edge = int(outSize)
    counters = {'rescaled': 0, 'padded': 0}  # number of rescaled and padded frames
    for count, image in enumerate(allImages):
        # compute indexes of bounding box from QCONF data
        frame = allFrameId[count]
        startx = allBounds[count]['x']
        width = startx + allBounds[count]['width']
        starty = allBounds[count]['y']
        height = starty + allBounds[count]['height']
        # assumes images in the same folder as QCONF regardless path in QCONF
        absImagePath = path.join(inputFolder, path.basename(image))
        im = io.imread(absImagePath)  # im is ordered [slices x y]
        print("Processing", path.basename(image), im.shape, "frame", frame,  sep=' ', end='', flush=True)
        # main image processing - cutting and scalling cels
        cutCell = process(im[frame - 1], (startx, starty, width, height), counters, edge)
        outFileName = path.join(outputFolder, path.basename(image) + "_" + str(count) + ".png")
        io.imsave(outFileName, cutCell)
        # optional processing of _snakemask
        if processMasks:
            absMaskPath = path.join(inputFolder, path.splitext(path.basename(image))[0] + "_snakemask.tif")
            ma = io.imread(absMaskPath)
            cutMask = process(ma[frame - 1], (startx, starty, width, height), None, edge)
            outFileName = path.join(outputFolder, "mask_" + path.basename(image) + "_" + str(count) + ".png")
            io.imsave(outFileName, cutMask)
        print("")
    print(pmed)
    print(ranges)
    print("Selected image size: ", edge)
    print(repr(counters['rescaled']) + '/' + repr(count + 1) + " were rescaled, " +
          repr(counters['padded']) + '/' + repr(count + 1) + " were padded")


if __name__ == "__main__":
    main(sys.argv[1:])
