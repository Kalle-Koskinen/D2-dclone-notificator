# Diablo 2 diablo clone tracker notifier

# Data courtesy of diablo2.io
# Special thanks to diablo2.io for all the work for the community!

# Author: Kalle "Apo" Koskinen

import requests
import datetime
import time
import os
import platform
if platform.system() == "Windows":
	import winsound

## Constants and initialization

# url to the diablo2.io public API for Diablo Clone/Uber Diablo progress tracker 
# (See here for more information: https://diablo2.io/forums/diablo-clone-uber-diablo-tracker-public-api-t906872.html)
league = "2" # softcore. change to 1 for hardcore
ladder = "2" # Non-ladder. change to 1 for ladder
d2api = "https://diablo2.io/dclone_api.php?hc=" + league + "&ladder=" + ladder + "&sk=r&sd=a"

# Delay between calls in seconds (IMPORTANT: MUST BE OVER 60 SECONDS)
delay = 90

# Total number of progressions 
totprogs = '6'

# Name strings for different progression levels
progressionstrs = {\
'1':'Terror gazes upon Sanctuary.', \
'2':'Terror approaches Sanctuary.', \
'3':'Terror begins to form within Sanctuary.', \
'4':'Terror spreads across Sanctuary.', \
'5':'Terror is about to be unleashed upon Sanctuary.', \
'6':'Terror has invaded Sanctuary.'}

# Name strings for regions
regionstrs = {'1':'America','2':'Europe','3':'Asia'}

# Threshold at which the alert is potentially triggered.
# Threshold is inclusive, i.e., progress value of alert threshold or higher can raise alert
alert_threshold = 4 

# Sound parameters for the alert
duration = 350  # milliseconds
freq = 440  # Hz

# Length of the log used for alert verification
log_length = 3
# Initialization of the log
templog = []
for regionidx in range(len(regionstrs)):
	templog.append([])


## Main program loop

while(True):

	try:
		# Call data from the API
		call = requests.get(d2api).json()
	except requests.exceptions.HTTPError as e:
		print("HTTP Error. Trying again after %d seconds." % delay)
		time.sleep(delay)
		continue
	except requests.exceptions.JSONDecodeError as e:
		print("JSON Error. Trying again after %d seconds." % delay)
		time.sleep(delay)
		continue

	# Initialize alert flag as false
	alert = [False]

	# Print header
	if platform.system() == "Windows":
		os.system('cls')
	else:
		os.system('clear')
	print("D2clone progression:")
	print("Data courtesy of diablo2.io")
	print()

	# Print dclone progression for each region
	for regionidx in range(len(regionstrs)):
		
		## Parse API response and format data

		# Region name string for current region
		regstr = regionstrs[call[regionidx]['region']]
		# Progression (number) for current region
		prog = call[regionidx]['progress']
		# Progression (message) for current region
		progstr = progressionstrs[prog]
		# Timestamp of the latest report for current region
		tstamp = datetime.datetime.fromtimestamp(int(call[regionidx]['timestamped']))

		# Get a list of timestamps from the log for this region
		logstamps = [ sub['timestamped'] for sub in templog[regionidx] ]

		## Add progress report to the log if it is new
		
		# Check whether timestamp is new
		if not call[regionidx]['timestamped'] in logstamps:

			# Add entry to the log 
			templog[regionidx].append(call[regionidx])

			# Check whether the log exceeds the length limit
			if len(templog[regionidx]) > log_length:
				# If the log is too long, delete oldest entry
				del templog[regionidx][0]
		
		## Print report information

		# Region
		print(regstr + ':')
		# Progression ("[current]/[max]: [message]")
		print(prog + '/' + totprogs + ": " + progstr)
		# Timestamp ("Timestamp: [timestamp]")
		print('Timestamp: ' + str(tstamp))
		print()

		## Alert trigger logic

		# Get a list of timestamps and progress values from the log for this region
		logstamps = [ sub['timestamped'] for sub in templog[regionidx] ]
		logprogs = [ int(sub['progress']) for sub in templog[regionidx] ]

		# Check whether the log is full-length and whether all progress values are
		# equal or higher than the alert threshold
		if len(logprogs) == log_length and min(logprogs) >= alert_threshold:
			# Set alert flag to true and save the region in question
			# NOTE: cannot handle simulaneous alerts in multiple regions (should be rare)
			alert = [True, regionidx]

	
	## Alert execution

	# Check whether alert was raised
	if alert[0]:

		# Print alert line including the region in question and play an alert sound
		print('  *** ALERT! Terror has invaded ' + regionstrs[call[alert[1]]['region']] + '! ***  ')
		if platform.system() == "Windows":
			winsound.Beep(freq, duration)
		elif platform.system() == "Linux":
			try:
				os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga')
			except:
				print('\a')
		elif platform.system() == "Darwin":
			try:
				os.system('afplay /System/Library/Sounds/Pong.aiff')
			except:
				print('\a')
		else:
			print('\a')

	
	## Wait [delay] seconds until next execution
	time.sleep(delay)
