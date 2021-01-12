"""
	Guilherme Batalheiro
	12/01/2021
	Free Class Rooms

	IMPORTED LIBS:
		requests
"""

import ast
import requests

from datetime import datetime

fenix_api = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/"
fenix_api_space = fenix_api + "spaces/"

file = open("rooms.txt", "r")
contents = file.read()
rooms = ast.literal_eval(contents)
file.close()

def api_availability():
	try:
		response = requests.get(fenix_api_space)
	except Timeout:
		return str("The request timed out!")
	except HTTPError as http_err:
		return str(f"HTTP error occurred: {http_err}")
	except Exception as err:
		return str(f"Other error occurred: {err}")

	if "Serviço em Manutenção" in response.text:
		return False
	else:
		return True

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

	if not(api_availability()):
		print("Api is unavalable")
		return

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