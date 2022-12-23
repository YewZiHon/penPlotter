import img_canny
import cv2 as cv
import sys
import subprocess
import os
from pathlib import Path
import time
import svgtoGcode

def img_to_svg(img_path):
    image = cv.imread(img_path)

    canny = img_canny.getImage(image)

    canny = cv.bitwise_not(canny)

    #save holding image
    cv.imwrite(sys.path[0]+"\\rufusCanny.bmp", canny)

    #delete file if exists
    if os.path.exists(sys.path[0]+"\\tmp\\rufus.svg"):
        os.remove(sys.path[0]+"\\tmp\\rufus.svg")

    #scale image
    imageWidth = canny.shape[1]
    imageHeight = canny.shape[0]

    MAXWIDTH = 150
    MAXHEIGHT = 140

    if MAXHEIGHT/MAXWIDTH > imageHeight/imageWidth:
        scaling = "-W "+str(MAXWIDTH)+"pt"
    else:
        scaling = "-H "+str(MAXHEIGHT)+"pt"


    #convert bitmap to png
    subprocess.Popen("\""+sys.path[0]+"\\potrace\\potrace.exe\" "+"\""+sys.path[0]+"\\rufusCanny.bmp\" -o \""+sys.path[0]+"\\rufus.svg\" -b svg "+scaling)
    print("\""+sys.path[0]+"\\potrace\\potrace.exe\" "+"\""+sys.path[0]+"\\rufusCanny.bmp\" -o \""+sys.path[0]+"\\rufus.svg\" -b svg "+scaling)

    #wait for svg to be saved
    while os.path.exists(sys.path[0]+"\\rufus.svg") != True:
        pass

    #wait for file write to be done
    lastsize = 0
    size = -1
    while lastsize !=size:
        size = Path(sys.path[0]+"\\rufus.svg").stat().st_size
        lastsize = size
        time.sleep(0.1)
    return canny

def generate_gcode():
    svgtoGcode.gcodeGenerate(sys.path[0]+"\\rufus.gcode")

