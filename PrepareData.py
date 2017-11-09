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
from nameresolver import resolveNames


def parseProgramArgs(argv):
    """Parse cmd."""
    inputFolder = ''
    outputFolder = './out'
    showPlot = False
    processTails = ()  # process only image pointed in QCONF
    outSize = None
    useBckg = False  # use cell background from image (not 0)
    randomizeFileNames = False
    try:
        opts, args = getopt.getopt(argv, "hpgrt:i:o:s:", ["indir=", "outdir=", "size="])
    except getopt.GetoptError as err:
        print("preparedata.py -i <inputfolder> -o <outputfolder>")
        print(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("preparedata.py -i <inputfolder> -o <outputfolder>")
            print("\t -h\tShow help")
            print("\t -p\tShow size distribution and exit")
            print("\t -t\tProcess all images within one QCONF that end with list of tails (comma separated)")
            print("\t -s,--size=\tSize of output images")
            print("\t -g\tDo not pad by zeros, try to use background from image (cell surroundings)")
            print("\t -r\tRandomize output file name (e.g XXX_Y.png, where XXX is global number and Y tail number)")
            print("By default program processes images referenced in QCONFs (everything must be in the same folder)")
            print("and saves cut cells in output folder (default ./out). If there are more images related to one QCONF")
            print("e.g. masks, other channels etc. they can be processed all together. Naming convenction in important")
            print("All images must have common basename and they can differ only in last characters.")
            print("User should use -t option providing all endings (for image referenced in QCONF as well).")
            print("python PrepareData.py -s 256 -i \"FLU+DIC\" -o \"FLU+DIC/out\" -t '_CH_1,_CH_1_snakemask,_CH_DIC'")
            sys.exit()
        elif opt in ("-i", "--indir"):
            inputFolder = arg
        elif opt in ("-o", "--outdir"):
            outputFolder = arg
        elif opt == "-p":
            showPlot = True
        elif opt == "-g":
            useBckg = True
        elif opt == "-t":
            processTails = tuple(arg.split(','))
        elif opt == "-r":
            randomizeFileNames = True
        elif opt in ("-s", "--size"):
            outSize = arg
    if not inputFolder:
        print("No <indir> option")
        sys.exit(2)
    return inputFolder, outputFolder, showPlot, processTails, outSize, useBckg, randomizeFileNames


def main(argv):
    """
    Run program.

    see: preparedata.py -h

    """
    inputFolder, outputFolder, showPlot, processTails, outSize, useBckg, randomizeFileNames = parseProgramArgs(argv)

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
        b, c, n, f = sq.getAll()  # outputs are dicts and lists
        allBounds.extend(b)  # collect bounds for this file (all snakes)
        allCentroids.extend(c)  # colect centroids
        # colect image name from Qconf (repeated for each QCONF)
        allImages.extend(n)
        allFrameId.extend(f)  # frame range 1...N

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

    # %% Compute range of data
    ranges = pandas.DataFrame(pbounds.min(), columns=['min'])
    ranges['max'] = pandas.DataFrame(pbounds.max(), columns=['max'])
    ranges = ranges.T  # transpose to have same orientation as med
    if showPlot:
        pbounds.plot.box()
        print(pmed)
        print(ranges)
        plt.show()
        sys.exit(0)

    # %% Process images
    recWidth = pmed['Width']['75']  # use 75% quartile size
    recHeight = pmed['Height']['75']
    if not outSize:
        # length of edge of all images (square) - larger one among selected quartile for width and height
        edge = np.round(np.max([recWidth, recHeight]))
    else:
        print("Use provided size", outSize)
        edge = int(outSize)
    print("Selected image size: ", edge)
    counters = {'rescaled': 0, 'padded': 0}  # number of rescaled and padded frames
    prevProcessed = None  # skip loading same stack many times
    # iterate over collected frames, boundaries, cells
    for count, image in enumerate(allImages):
        # compute indexes of bounding box from QCONF data
        frame = allFrameId[count]
        # check is there are more images to process for one QCONF (user conf)
        subimages = resolveNames(path.basename(image), processTails)  # use qconf image to get base name
        # load stacks only once (image from all Images is repeated fro each frame)
        if path.basename(image) != prevProcessed:  # load only if new image appears
            print("Load next stacks")
            prevProcessed = path.basename(image)
            # assumes images in the same folder as QCONF regardless path in QCONF
            im = []  # all images within one qconf will be loaded
            for subimage in subimages:
                absImagePath = path.join(inputFolder, subimage)
                im.append(io.imread(absImagePath))  # im is ordered [slices x y]
        # process all images (or only original if processTails was empty)
        for countsubimage, subimage in enumerate(subimages):
            print("Processing", path.basename(subimage), im[countsubimage].shape, "frame", frame,  sep=' ', end='', flush=True)
            # main image processing - cutting and scalling cels
            cutCell = process(im[countsubimage][frame - 1],
                              (allBounds[count]['x'],
                               allBounds[count]['y'],
                               allBounds[count]['width'],
                               allBounds[count]['height']),
                              counters,
                              edge,
                              useBckg)
            if randomizeFileNames is True:
                outFileName = path.join(outputFolder, str(count) + "_" + str(countsubimage) + ".png")
            else:
                outFileName = path.join(outputFolder, path.basename(subimage) + "_" + str(count) + ".png")
            io.imsave(outFileName, cutCell)
            print("")
    processedTails = 1 if len(processTails) == 0 else len(processTails)
    print(repr(int(counters['rescaled'] / processedTails)) + '/' + repr(count + 1) + " were rescaled, " +
          repr(int(counters['padded'] / processedTails)) + '/' + repr(count + 1) + " were padded")
    print("Selected image size: ", edge)
    print("Subimages processed: ", processTails)


if __name__ == "__main__":
    main(sys.argv[1:])
