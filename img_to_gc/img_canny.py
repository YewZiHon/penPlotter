import cv2 as cv
TARGET_RATIO = 0.01 #target pixels to 2%

def getImage(image):
    image = cv.blur(image,(3,3))
    image = getCanny(image)
    return image

def getCanny(image):
    image = cv.blur(image,(3,3))

    INCREMENT = 10
    thresholdVal = 10
    tries = 0
    closestMin = [0.00,10]
    closestMax = [1.00, 250]
    while(1):
        tries+=1
        print("trying:", thresholdVal)
        image2 = cv.Canny(image,thresholdVal,thresholdVal*2)
        pixelRatio = cv.countNonZero(image2)/image2.shape[0]/image2.shape[1]
        print(pixelRatio)
        if pixelRatio < TARGET_RATIO: #less than target
            if thresholdVal == closestMax[1]:

                if INCREMENT != 1:
                    INCREMENT = 1
                else:
                    print("Found best match")
                    break
            thresholdVal-=INCREMENT
            if closestMin[0] < pixelRatio:
                closestMin[0] = pixelRatio
                closestMin[1] = thresholdVal
        
        else:
            thresholdVal+=INCREMENT
            if closestMax[0] > pixelRatio:
                closestMax[0] = pixelRatio
                closestMax[1] = thresholdVal
        print("min:", closestMin)
        print("max:", closestMax)
        if thresholdVal>500 or thresholdVal<10 or tries>60:
            print("Error determining best pixel ratio, using defaults")
            return cv.Canny(image,50,100)
    if abs(closestMin[0]-TARGET_RATIO)>abs(closestMax[0]-TARGET_RATIO):
        print("best match is", closestMin[1])
        if thresholdVal == closestMin[1]:
            return image2
        else:
            thresholdVal = closestMin[1]
    else:
        print("best match is", closestMax[1])
        if thresholdVal == closestMax[1]:
            return image2
        else:
            thresholdVal = closestMax[1]
    print("Recomputing image")
    return cv.Canny(image,thresholdVal,thresholdVal*2)
