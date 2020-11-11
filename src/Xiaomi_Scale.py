#############################################################################################
# Code to read weight measurements fom Xiaomi Scale V2
#############################################################################################

import os
from datetime import datetime

from .Xiaomi_Scale_Body_Metrics import BodyMetrics

# User Variables...

USER1_GT = int(os.getenv('USER1_GT', '70'))  # If the weight is greater than this number, we're weighing User #1
USER1_SEX = os.getenv('USER1_SEX', 'male')
USER1_NAME = os.getenv('USER1_NAME', 'Mateusz')
USER1_HEIGHT = int(os.getenv('USER1_HEIGHT', '177'))  # Height (in cm)
USER1_DOB = os.getenv('USER1_DOB', '1988-09-30')  # DOB (in yyyy-mm-dd format)

USER2_LT = int(os.getenv('USER2_LT', '65'))  # If the weight is greater than this number, we're weighing User #2
USER2_SEX = os.getenv('USER2_SEX', 'female')
USER2_NAME = os.getenv('USER2_NAME', 'Ania')
USER2_HEIGHT = int(os.getenv('USER2_HEIGHT', '170'))  # Height (in cm)
USER2_DOB = os.getenv('USER2_DOB', '1988-10-20')  # DOB (in yyyy-mm-dd format)

LBS = "03"
KG = "02"


class ScanProcessor:
    def __init__(self):
        self.connected = False

    def handleDiscovery(self, dev, isNewDev, isNewData):
        pass


def getAge(d1):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(datetime.today().strftime('%Y-%m-%d'),'%Y-%m-%d')
    return abs((d2 - d1).days)/365


def get_scale_data(sdid, data):
    ### Xiaomi V2 Scale ###
    if data.startswith('1b18') and sdid == 22:
        measunit = data[4:6]
        measured = int((data[28:30] + data[26:28]), 16) * 0.01
        if measunit == LBS:
            pass
        elif measunit == KG:
            measured = measured / 2
        else:
            raise Exception("Scale is sleeping")

        mitdatetime = datetime.strptime(str(int((data[10:12] + data[8:10]), 16)) + " " + str(int((data[12:14]), 16)) +" "+ str(int((data[14:16]), 16)) +" "+ str(int((data[16:18]), 16)) +" "+ str(int((data[18:20]), 16)) +" "+ str(int((data[20:22]), 16)), "%Y %m %d %H %M %S")
        miimpedance = str(int((data[24:26] + data[22:24]), 16))

        return _evaluate_body_parameters(round(measured, 2), str(mitdatetime), miimpedance)


def _evaluate_body_parameters(weight, mitdatetime, miimpedance):
    if int(weight) > USER1_GT:
        user = USER1_NAME
        height = USER1_HEIGHT
        age = getAge(USER1_DOB)
        sex = USER1_SEX
    elif int(weight) < USER2_LT:
        user = USER2_NAME
        height = USER2_HEIGHT
        age = getAge(USER2_DOB)
        sex = USER2_SEX
    lib = BodyMetrics(weight, height, age, sex, miimpedance)
    parameters = {"user": user, "weight": weight, "bmi": lib.getBMI(), "basal_metabolism": lib.getBMR(),
                  "visceral_fat": lib.getVisceralFat(), "lean_body_mass": lib.getLBMCoefficient(),
                  "body_fat": lib.getFatPercentage(), "water": lib.getWaterPercentage(), "bone_mass": lib.getBoneMass(),
                  "muscle_mass": lib.getMuscleMass(), "protein": lib.getProteinPercentage(), "timestamp": mitdatetime}
    return parameters
