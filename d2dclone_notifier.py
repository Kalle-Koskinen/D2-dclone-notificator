# Diablo 2 diablo clone tracker notifier

# Data courtesy of diablo2.io
# Special thanks to diablo2.io for all the work for the community!

# Author: Kalle "Apo" Koskinen

#####################################################################

## Import modules

# Default modules
import datetime
import time
import os
import platform
if platform.system() == "Windows":
	import winsound

# External modules
import requests
import tkinter as tk


## Constants and initialization

## True constants

# Delay between calls in seconds (IMPORTANT: MUST BE OVER 60 SECONDS)
delay = 70

# Default dropdown values
alertdefault = 4
leaguedefault = "Softcore"
ladderdefault = "Ladder"

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

# Dictionaries for leagues and ladder
leaguedict = {'Hardcore':'1', 'Softcore':'2'}
ladderdict = {'Ladder':'1', 'Non-ladder':'2'}

# Sound parameters for the alert
duration = 350  # milliseconds
freq = 440  # Hz

# GUI size
HEIGHT = 400
WIDTH = 600

# Initialization
start = False

templog = []
for regionidx in range(len(regionstrs)):
	templog.append([])


## Program run loop

def runloop():

	## Check whether start is pressed

	if(start):
		
		## Initialize and get parameters from GUI

		printframe = tk.Frame(uiroot, bg='white')
		printframe.place({'relx':0.1, 'rely':0.1, 'relw':0.5, 'relh':0.7, 'anchor':'nw'}) 

		# Initialize alert flag as false
		alert = [False]

		# Get league and ladder from GUI
		leaguestr = leaguevar.get()
		ladderstr = laddervar.get()

		# url to the diablo2.io public API for Diablo Clone/Uber Diablo progress tracker 
		# (See here for more information: https://diablo2.io/forums/diablo-clone-uber-diablo-tracker-public-api-t906872.html)
		d2api = "https://diablo2.io/dclone_api.php?hc=" + leaguedict[leaguestr] + "&ladder=" + ladderdict[ladderstr] + "&sk=r&sd=a"

		# Threshold at which the alert is potentially triggered.
		# Threshold is inclusive, i.e., progress value of alert threshold or higher can raise alert
		alert_threshold = int(alertvar.get())

		# Length of the log used for alert verification
		log_length = 3


		## Call data

		# Initialize print string
		printstring = "\n"

		# Call data from the API
		
		try: 
			call = requests.get(d2api).json()
			
			## Construct feedback

			# Construct header
			if platform.system() == "Windows":
				os.system('cls')
			else:
				os.system('clear')

			# Append print header
			printstring = "".join((printstring, \
				"D2clone progression:" + "\n", \
				"Data courtesy of diablo2.io" + "\n", \
				"League: " + leaguestr + ", " + ladderstr + "\n\n"))

			# Prepare report of dclone progression for each region
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
				
				
				## Compose report string: Region, progression, timestamp

				printstring = "".join((printstring, \
				regstr + ':\n', \
				prog + '/' + totprogs + ": " + progstr + "\n", \
				'Timestamp: ' + str(tstamp) + "\n\n"))

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

				# Compose alert print string
				printstring = "".join((printstring, \
				'  *** ALERT! Terror has invaded ' + regionstrs[call[alert[1]]['region']] + '! ***  ' + '\n'))
				
				# Play alert sound
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

		except:
			printstring = "ERROR: Could not retrieve data!" + "\n" + "Retrying..."


		## Print report

		printtext=tk.Label(printframe, text=printstring, bg='white')
		printtext.pack()


		## Wait [delay] seconds until next execution
		uiroot.after(1000,scheduler)

	else:
		uiroot.after(1000,runloop)


## Scheduler for the interval for calling new data
def scheduler():
	global timestep

	# Check whether delay is fulfilled and update timer 
	if(timestep<delay):
		timerstring = timertemplate + str(timestep) + "/" + str(delay) + " seconds."
		timerlabel['text'] = timerstring
		timestep = timestep + 1
		uiroot.after(1000,scheduler)
	else:
		timestep = 1
		uiroot.after(1000,runloop)


## Button switch
def gobutton():
	global start 

	# Button / running status switch
	if(start_button['text'] == 'Start'):
		start_button['text'] = 'Stop'
		start = True
		blight['bg'] = 'green'
	else:
		start_button['text'] = 'Start'
		start = False
		blight['bg'] = 'red'


## GUI setup

# Main window
timestep = 1
uiroot = tk.Tk()
uiroot.title("D2 clone notifier")

bgcanvas = tk.Canvas(uiroot, height=HEIGHT, width=WIDTH)
bgcanvas.pack()

# Initialize rectangle

initframe = tk.Frame(uiroot, bg='white')
initframe.place({'relx':0.1, 'rely':0.1, 'relw':0.5, 'relh':0.7, 'anchor':'nw'}) 

# League dropdown menu

leaguevar = tk.StringVar()
leaguevar.set(leaguedefault)
leaguemenuname = tk.Label(bgcanvas, text='League:', anchor='w')
leaguemenuname.place({'relx':0.7, 'rely':0.10, 'relw':0.2, 'relh':0.05, 'anchor':'nw'})
leaguemenu = tk.OptionMenu(bgcanvas, leaguevar, *list(leaguedict.keys()))
leaguemenu.place({'relx':0.7, 'rely':0.15, 'relw':0.2, 'relh':0.07, 'anchor':'nw'})

# Ladder dropdown menu

laddervar = tk.StringVar()
laddervar.set(ladderdefault)
laddermenuname = tk.Label(bgcanvas, text='Ladder?', anchor='w')
laddermenuname.place({'relx':0.7, 'rely':0.25, 'relw':0.2, 'relh':0.05, 'anchor':'nw'})
laddermenu = tk.OptionMenu(bgcanvas, laddervar, *list(ladderdict.keys()))
laddermenu.place({'relx':0.7, 'rely':0.30, 'relw':0.2, 'relh':0.07, 'anchor':'nw'})

# Alert threshold dropdown menu

alertvar = tk.StringVar()
alertvar.set(alertdefault)
alertmenuname = tk.Label(bgcanvas, text='Alert Threshold', anchor='w')
alertmenuname.place({'relx':0.7, 'rely':0.40, 'relw':0.2, 'relh':0.05, 'anchor':'nw'})
alertmenu = tk.OptionMenu(bgcanvas, alertvar, *[2,3,4,5])
alertmenu.place({'relx':0.7, 'rely':0.45, 'relw':0.2, 'relh':0.07, 'anchor':'nw'})

# Go button

start_button = tk.Button(bgcanvas, text='Start', command=gobutton)
start_button.place({'relx':0.7, 'rely':0.6, 'relw':0.14, 'relh':0.07, 'anchor':'nw'})
blight = tk.Canvas(bgcanvas, bg='red')
blight.place({'relx':0.85, 'rely':0.61, 'relw':0.04, 'relh':0.05, 'anchor':'nw'})

# Timer indicator

timertemplate = 'Time until next call: '
timerlabel = tk.Label(bgcanvas, text=timertemplate, anchor='w')
timerlabel.place({'relx':0.2, 'rely':0.8, 'relw':0.3, 'relh':0.1, 'anchor':'nw'})


## Run main program loop

runloop()
uiroot.mainloop()


