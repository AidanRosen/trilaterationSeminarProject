"""
Author	: Aidan Rosen

Much of this code came from Muhammad Arifin's trilateration code, also found on Github.
This version is heavily modified though, and the dbClass.py was built by the CSE 191 IoT team in 2023.
"""

import os
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import math 
import sys
import random
from datetime import *
#
from heapq import nsmallest #https://stackoverflow.com/questions/22117834/how-do-i-return-a-list-of-the-3-lowest-values-in-another-list

######## Function to calculate trilateration parameters ########

def trilat_params(xi,yi,xj,yj,ri,rj):
	a = -2*xi + 2*xj
	b = -2*yi + 2*yj
	c = ri**2 - rj**2 - xi**2 + xj**2 - yi**2 + yj**2

	return a,b,c


######## Implementation of trilateration calculation process ########
# Function of Trilateration Calculation Process
# Data to be processed is stored as csv file. 
# Data is processed entirely using pandas dataframe

from dbClass import dbClass
cse191db = dbClass()


def rssiToFeet(rssi):
		#Note: Adding our custom model for RSSI to feet 
	return (0.0119446 * math.exp(-0.106191 * rssi))

def getXY(deviceName):
	match deviceName: #Largely depends on how the CSV api sends back is handled 
		case "A":
			return [236.1,353.54]
		case "B":
			return [499.2,456.35]
		case "C":
			return [411.93,247.5]
		case "F":
			return [561,330]
		case "G":
			return [266.3,374.7]
		case "V":
			return [34.64,297.9]
		case "R":
			return [207.3,160.3]
		case "Q":
			return [228.7,470.6]
		case "P":
			return [379.93,443.47]
		case "L":
			return [468.3,497.4]
		case "I":
			return [526.7,360.26]
		case "K":
			return [560.54,232.65]
		case "T":
			return [637.2,451.8]
		case "X":
			return [755.7,172.4]
		case "M":
			return [700,555]
		case "H":
			return [51.1,814.2]
		case "W":
			return [29.63,724.56]
		case "E":
			return [71.3,675.35]
		case "O":
			return [35.4,946.1]
		case "U":
			return [35.3,771.95]
		case "D":
			return [14,944]
		case other:
			return "error :("
		
def getFloor(deviceName):
	if deviceName == "X" or deviceName == "M":
		return "RIMAC 1st Floor"
	elif deviceName == "B" or deviceName == "C" or deviceName == "F" or deviceName == "G":
		return "RIMAC 2nd Floor" 
	elif deviceName == "A" or deviceName == "V" or deviceName == "R" or deviceName == "Q" or deviceName == "P" or deviceName == "L" or deviceName == "I" or deviceName == "K" or deviceName == "T":
		return "RIMAC 3rd Floor" 
	elif deviceName == "O":
		return "Annex Lower Floor"
	elif deviceName == "U" or deviceName == "D" or deviceName == "N":
		return "Annex 1st Floor"
	elif deviceName == "H" or deviceName == "W" or deviceName == "E" or deviceName == "E" or deviceName == "E" or deviceName == "J":
		return "Annex 2nd Floor"
	else:
		return "error :("


def trilateration_process(topDevices, rssi):
	# # Read csv file as panda data frame
	# df = pd.read_csv(path+case)
	# #Note: just string concatenation

	# #Note: change this to whatever the API team hands us 
	# # Drop 'Time' column
	# df = df.drop(columns=["Time"])

	# # Drop NaN values
	# df = df.dropna()



	# #Start of the x-y coordinate calculating
	# rowArray = df.iloc[i].to_numpy()
	# #Don't want to include start index, so starting at index 1 
	# rowArray = rowArray[1:len(rowArray)-1] #Want to exclude the end index (timestamp)

	# #Now the array is ready to be iterated through
	# rssiArray = nlargest(3, rowArray)

	# topDevices = []
	# for idx, rssi in enumerate(rssiArray):
	# 	topDevices.append(df.columns()[rowArray.index(rssiArray[idx]) + 1])
	# #To know which devices were the top three beacons 
	# #Will use to triangulate
	# #TopDevices[0] should be the closest device
	# #Expect: an array of letters like a, b, c

	# #ok so now we have our three top RSSI values and the closest device it beaconed to 

	# for idx, rssi in enumerate(rssiArray):
	# 	rssiArray[idx] = rssiToFeet(rssi)
	# 	#Convert the rssi to feet distances
	
	# # Setting APs coordinates
	# # AP1

	# #
	# #Top devices is the letternames of the devices 
	# #AP coordinates is a list of pairs. 
	ap_coordinates = []
	for device in topDevices:
		ap_coordinates.append(getXY(device))

	
	#To be returned 
	detectedFloor = getFloor(topDevices[0])



	# Trilateration parameters calculation
	# Calculate A, B, C, D, E, and F 
	A, B, C = trilat_params(ap_coordinates[0][0], ap_coordinates[0][1], ap_coordinates[1][0], ap_coordinates[1][1], rssi[0], rssi[1])
	#Note: works because rssi[0] is the distance to the device associated with ap_coordinates[0]. True for indices 1 and 2 as well
	D, E, F = trilat_params(ap_coordinates[1][0], ap_coordinates[1][1], ap_coordinates[2][0], ap_coordinates[2][1], rssi[1], rssi[2])

	# Calculate x and y using trilateration
	# x = CE - BF / AE - BD; y = CD - AF / BD - AE
	if (A*E - B*D != 0):
		xtr = (C*E - B*F) / (A*E - B*D) #A bandaid for division by zero
	else :
		xtr = 411 #center them by default 
	if (B*D - A*E != 0):
		ytr = (C*D - A*F) / (B*D - A*E)
	else: 
		ytr = 247

#Deleting sqrt error and such, redundant.

	# Return the trilateration df and MSE
	return [xtr, ytr, detectedFloor] #<--- need to turn these into a CSV and make a floor loop outta all dis!


def randomBeacon(letterClosest):

	xyArray = getXY(letterClosest)

	#Random going down 
	if letterClosest=="Q" or letterClosest=="P" or letterClosest=="L" or letterClosest=="O" or letterClosest=="D":
		y = xyArray[1] + random.randint(-160,0)
		   #Small y range 
	elif letterClosest=="H" or letterClosest=="W" or letterClosest=="E" or letterClosest=="U":
		y = xyArray[1] + random.randint(-100,100)
	#elif random going up
	elif letterClosest=="R" or letterClosest=="X":
		y = xyArray[1] + random.randint(0,160)
	else:
		y = xyArray[1] + random.randint(-160,160)
	
	if letterClosest=="K" or letterClosest=="T":
		x = xyArray[0] + random.randint(-160,0)
	elif letterClosest=="V" or letterClosest=="G":
		x = xyArray[0] + random.randint(0,160)
	elif letterClosest=="H" or letterClosest=="W" or letterClosest=="E" or letterClosest=="U":
		x = xyArray[0] + random.randint(0,100)
	elif letterClosest=="O":
		x = xyArray[0] + random.randint(0,100)
	else:
		x = xyArray[0] + random.randint(-160,160)

	#If neither, just do a range of +- 160 for y first, then for x 

	#Random going left

	#Random going right 

	return [x,y]
	
def innerLoopFunction(datetime):
	# """ Run the program """
	# # Data Paths
	# # path = 'D:/Skripsweetku/Raw Data/Pengukuran Variasi Jarak Ulangan/'
	# path = 'D:/Skripsweetku/Raw Data/Pengukuran Variasi Jarak dan Manusia/'
	# cases = os.listdir(path)

	filepath = sys.argv
	

	df = cse191db.getDF(datetime)
	if df.empty:
		return 
	#print(df)
	#Note: just string concatenation

	#Note: change this to whatever the API team hands us 
	# Drop 'Time' column
	#df = df.drop(columns=["Time"])

	# Drop NaN values
	#df = df.dropna()

	dataFrame = {"floor":[], 'x': [], 'y': [], "timestamp":[]}
	xyDataFrame = pd.DataFrame.from_dict(dataFrame)
	for i in range(0, len(df.index)):
		rowArray = df.iloc[i].to_numpy().tolist()
		#Don't want to include start index, so starting at index 1 
		timeStamp = rowArray[-1]
		#print(timeStamp)
		rssiArray = rowArray[1:len(rowArray)-1]
		rssiArray.sort(reverse=True)
		rssiArray = rssiArray[0:3]
		#print(rssiArray)

		lettersOfClosest = []
		columnsArray = df.columns.tolist()
		copyRow = rowArray #Need this copy to pop from here as well to line up with letter row
		for i in range(0,3):
			foundIndex = copyRow.index(rssiArray[i])
			lettersOfClosest.append(columnsArray[foundIndex].upper())
			columnsArray.pop(foundIndex) #To do deal with duplicate detections
			copyRow.pop(foundIndex)
		
		multipleDefaults = -90 in rssiArray

		# for i in rssiArray:
		# 	if i == -90: #if any of the values are default, then we'll default on going to the nearest device 
		# 		multipleDefaults = True
		
		if multipleDefaults:
			# #Ned to set location to some random area around the detected letter rssi device
			# xyArray = getXY(lettersOfClosest[0]) #index 0 is the closest letter 
			floorName = getFloor(lettersOfClosest[0])
			# x = xyArray[0] + random.randint(-60,60)
			# y = xyArray[1] + random.randint(-60,60)
			newRow = randomBeacon(lettersOfClosest[0])
			newRow.append(floorName)
			newRow.insert(0,timeStamp)
			# print("Running multiple defaults")
			# print(newRow)
			cse191db.sendToDF(newRow)
		
		else:

		#print(rssiArray)
			for idx, rssi in enumerate(rssiArray):
				rssi = rssiToFeet(rssi) #THOUSANDS of feet of distance? Doesn't make sense. Need to check my algorithm
				rssiArray[idx] = rssi
			
			#print(rssiArray)
			#print(lettersOfClosest)

			#Now we have the two arrays we can work with. 

			#Will now construct a row of x,y, and floor from the trilaterate function. Then directly insput the timestamp

			

			newRow = trilateration_process(lettersOfClosest, rssiArray)
			newRow = [timeStamp] + newRow
			#print(newRow)

			# print("Sending row without defaults.")
			# print(newRow)
			cse191db.sendToDF(newRow)
		#xyDataFrame = xyDataFrame.append({"x": newRow[0], "y": newRow[1], "floor": newRow[2], "timestamp": newRow[3]}, ignore_index = True)
	
	#print(xyDataFrame)
	#xyDataFrame.to_csv(r'C:\Users\aidan\Downloads\result.csv')
	## Fix this up by turning into a responsive saved name, like taking the path of the original and adding -result to say its the result of processing the data for that day
	return 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~ Main Program ~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def main():
	#Will update from may 5 to may 7th towards may 29th
	print("hello")
	d = datetime(2023, 5, 15, 18, 0, 0)
	#print(d)
	
	#print(d)

	while(d <= datetime(2023, 5, 31, 23, 0, 0)):
		print(d)
		if (d.hour == 23):
				innerLoopFunction(d)
				d = d + timedelta(days=1)
				d = d.replace(hour = 6, minute = 0, second = 0)
		else:
			innerLoopFunction(d)
			d = d + timedelta(minutes=30)

			#Add 5-8-12-45 manually because of the fricking minutes=5 at line 297
		

	

		
		

if __name__ == '__main__':
	main()


'''
if (point.floor_name == "RIMAC 1st Floor"):
	if ((380 <= x) && (x <= 1120)) && ((100 <= y) && (y <= 780)):
		#plot the point
		
if (point.floor_name == "RIAMC 2nd Floor"):
	if ((160 <= x) && (x <= 1120)) && ((100 <= y) && (y <= 740)):
		#plot the point
	
if (point.floor_name == "RIAMC 3rd Floor"):
	if ((0 <= x) && (x <= 700)) && ((100 <= y) && (y <= 550)):
		#plot the point
	
if (point.floor_name == "Annex Lower Floor"):
	if ((0 <= x) && (x <= 250)) && ((600 <= y) && (y <= 1100)):
		#plot the point
	
if (point.floor_name == "Annex 1st Floor"):
	if ((0 <= x) && (x <= 260)) && ((520 <= y) && (y <= 1100)):
		#plot the point
	
if (point.floor_name == "Annex 2nd Floor"):
	if ((0 <= x) && (x <= 180)) && ((560 <= y) && (y <= 1000)):
		#plot the point

'''
