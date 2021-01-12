"""
	Guilherme Batalheiro
	01/01/2021
	Free Class Rooms

	IMPORTED LIBS:
		requests
"""

import requests

from datetime import datetime

fenix_api = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/"
fenix_api_space = fenix_api + "spaces/" 

rooms = {
	"0 - 16": "2448131365167",
	"0 - 32": "2448131373043",
	"0 - 71": "2448131373038",
	"0 - 73": "2448131373039",
	"0 - 75": "2448131373037",
	"0 - 13": "2448131365126",
	"0 - 15": "2448131365127",
	"0 - 17": "2448131365128",
	"0 - 19": "2448131365129",
	"0 - 21": "2448131365130",
	"0 - 23": "2448131365131",
	"0 - 25": "2448131365132",
	"0 - 27": "2448131365133",
	"0 - 5": "2448131365116",
	"0 - 9": "2448131365119",
	"A1": "2448131365113",
	"A2": "2448131365117",
	"A3": "2448131365134",
	"A4": "2448131365135",
	"A5": "2448131365136",
	"1 - 4.8": "2448131365243",
	"1 - 75": "2448131365299",
	"1 - 60": "2448131373040",
	"1 - 62": "2448131373041",
	"1 - 64": "2448131373042",
	"1 - 1": "2448131365194",
	"1 - 11": "2448131365204",
	"1 - 2": "2448131365195",
	"1 - 17": "2448131365221",
	"1 - 19": "2448131365222",
	"1 - 22": "2448131365224",
	"1 - 24": "2448131365225",
	"1 - 3": "2448131365196",
	"1 - 4": "2448131365197",
	"2 - N 8.2": "2448131365407"
}

def clean_data_room(data):
	"""Clean the data
		
		:param data: dict
		:return:	 dict
	"""
	clean_data = {}
	for i in data:
		if i["day"] not in clean_data:
			clean_data[i["day"]] = [i["weekday"], {"type": i["type"], \
										  		   "start": i["start"], \
										  		   "end": i["end"]}]
		else:
			clean_data[i["day"]].append({"type": i["type"], \
						 				 "start": i["start"], \
						 				 "end": i["end"]})
	return clean_data

def get_room_week_data(day, room):
	"""Get room data

		:param day:  str
		:param room: str
		:return:     dict
	"""
	#HTTP GET request
	try:
		response = requests.get(fenix_api_space + rooms[room], \
								params={'day': day}, timeout = 10)
	except Timeout:
		return str("The request timed out!")
	except HTTPError as http_err:
		return str(f"HTTP error occurred: {http_err}")
	except Exception as err:
		return str(f"Other error occurred: {err}")

	json_response = response.json()

	if "error" in json_response: 
		return str(json_response["error"] + ": " + json_response["description"])
	elif "events" not in json_response:
		return str(": No info :( sorry!!")
	else:
		room_week_data = clean_data_room(json_response["events"])
		return room_week_data

def free_rooms(date):
	"""Get free rooms

		:param date: datetime 
		:return:     dict
	"""
	day = date.strftime("%d/%m/%Y")

	time = datetime.strptime(date.strftime("%H:%M"), "%H:%M")
	
	for room in rooms.keys():
		week_schedule = get_room_week_data(day, room)
		if day in week_schedule:
			free = True
			for lesson in week_schedule[day]:
				if isinstance(lesson, dict):
					start = datetime.strptime(lesson["start"], "%H:%M")
					end = datetime.strptime(lesson["end"], "%H:%M")
					if start <= time <= end:
						free = False
						print(room, ": Room not free!")
						break
			if free:
				print(room, ": Room free!")

		elif isinstance(week_schedule, str):
			print(room, week_schedule)
		else:
			print(room, ": Free all day or closed")
	pass

now = datetime.now()
free_rooms(now)