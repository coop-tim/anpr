# import the necessary packages
import cv2
from fastanpr import FastANPR
import uk_numplate_regex

fast_anpr = FastANPR()

async def getRegInSpaces(camera):
    spaces = {};
    for spaceId in camera["spaces"]:
        space = camera["spaces"][spaceId]
        cam = cv2.VideoCapture(0)
        
        img = cam.read()[1]
        files=[img]
        images = [cv2.cvtColor(i, cv2.COLOR_BGR2RGB) for i in files]
        plates = (await fast_anpr.run(images))[0]
        str = ""
        if len(plates) > 0:
            for plate in plates:
                if plate.rec_text == None: 
                    continue

                if not uk_numplate_regex.isUkNumberplate(plate.rec_text):
                    str = uk_numplate_regex.cleanAnpr(plate.rec_text)
                else:
                    str = plate.rec_text

        if str == "": 
            spaces[spaceId] = {
                "spaceId": spaceId,
                "reg":None
            } 
        else: 
            spaces[spaceId] = {
                "spaceId": spaceId,
                "reg": str
            }
    return spaces