#############################################################################################
# Code to read weight measurements fom Xiaomi Scale V2
#############################################################################################

import os
from datetime import datetime

from .Xiaomi_Scale_Body_Metrics import BodyMetrics

# User Variables...

USER1_GT = int(os.getenv('USER1_GT', '70'))  # If the weight is greater than this number, we're weighing User #1
USER1_SEX = os.getenv('USER1_SEX', 'male')
USER1_NAME = os.getenv('USER1_NAME', 'David')
USER1_HEIGHT = int(os.getenv('USER1_HEIGHT', '175'))  # Height (in cm)
USER1_DOB = os.getenv('USER1_DOB', '1988-09-30')  # DOB (in yyyy-mm-dd format)

USER2_LT = int(os.getenv('USER2_LT', '55'))  # If the weight is greater than this number, we're weighing User #2
USER2_SEX = os.getenv('USER2_SEX', 'female')
USER2_NAME = os.getenv('USER2_NAME', 'Joanne')
USER2_HEIGHT = int(os.getenv('USER2_HEIGHT', '155'))  # Height (in cm)
USER2_DOB = os.getenv('USER2_DOB', '1988-10-20')  # DOB (in yyyy-mm-dd format)


class ScanProcessor:
	def __init__(self):
		self.connected = False

	def getAge(self, d1):
		d1 = datetime.strptime(d1, "%Y-%m-%d")
		d2 = datetime.strptime(datetime.today().strftime('%Y-%m-%d'),'%Y-%m-%d')
		return abs((d2 - d1).days)/365

	def handleDiscovery(self, dev, isNewDev, isNewData):
		pass


def get_scale_data(sdid, desc, data):
	### Xiaomi V2 Scale ###
	if data.startswith('1b18') and sdid == 22:
		measunit = data[4:6]
		measured = int((data[28:30] + data[26:28]), 16) * 0.01
		unit = ''

		if measunit == "03": unit = 'lbs'
		if measunit == "02": unit = 'kg' ; measured = measured / 2
		mitdatetime = datetime.strptime(str(int((data[10:12] + data[8:10]), 16)) + " " + str(int((data[12:14]), 16)) +" "+ str(int((data[14:16]), 16)) +" "+ str(int((data[16:18]), 16)) +" "+ str(int((data[18:20]), 16)) +" "+ str(int((data[20:22]), 16)), "%Y %m %d %H %M %S")
		miimpedance = str(int((data[24:26] + data[22:24]), 16))

		if unit:
			print('')
			_publish(round(measured, 2), unit, str(mitdatetime), miimpedance)
		else:
			print("Scale is sleeping.")


def _publish(self, weight, unit, mitdatetime, miimpedance):
	if int(weight) > USER1_GT:
		user = USER1_NAME
		height = USER1_HEIGHT
		age = self.getAge(USER1_DOB)
		sex = USER1_SEX
	elif int(weight) < USER2_LT:
		user = USER2_NAME
		height = USER2_HEIGHT
		age = self.getAge(USER2_DOB)
		sex = USER2_SEX
	lib = BodyMetrics(weight, height, age, sex, 0)
	message = '{'
	message += '"Weight":"' + "{:.2f}".format(weight) + '"'
	message += ',"BMI":"' + "{:.2f}".format(lib.getBMI()) + '"'
	message += ',"Basal Metabolism":"' + "{:.2f}".format(lib.getBMR()) + '"'
	message += ',"Visceral Fat":"' + "{:.2f}".format(lib.getVisceralFat()) + '"'

	if miimpedance:
		lib = BodyMetrics(weight, height, age, sex, int(miimpedance))
		message += ',"Lean Body Mass":"' + "{:.2f}".format(lib.getLBMCoefficient()) + '"'
		message += ',"Body Fat":"' + "{:.2f}".format(lib.getFatPercentage()) + '"'
		message += ',"Water":"' + "{:.2f}".format(lib.getWaterPercentage()) + '"'
		message += ',"Bone Mass":"' + "{:.2f}".format(lib.getBoneMass()) + '"'
		message += ',"Muscle Mass":"' + "{:.2f}".format(lib.getMuscleMass()) + '"'
		message += ',"Protein":"' + "{:.2f}".format(lib.getProteinPercentage()) + '"'

	message += ',"TimeStamp":"' + mitdatetime + '"'
	message += '}'
	return '\tUser data %s: %s' % ('/' + user + '/weight', message)
