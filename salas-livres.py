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
fenix_api_space_Tagus_Park = fenix_api_space + "2448131365084"

def simple_get_request(url):
	try:
		response = requests.get(url)
	except Timeout:
		return str("The request timed out!")
	except HTTPError as http_err:
		return str(f"HTTP error occurred: {http_err}")
	except Exception as err:
		return str(f"Other error occurred: {err}")
	return response

def get_room_id(room, floor, group):
	"""Gets the room id
		
		:param room: str
		:param floor: str
		:param group: str
		:return:	 str
	"""
	#HTTP GET request
	response = simple_get_request(fenix_api_space_Tagus_Park)
	for i in response.json()['containedSpaces']:
		if isinstance(floor, str) and i['name'] == floor:
			response_1 = simple_get_request(fenix_api_space + i['id'])
			for j in response_1.json()['containedSpaces']:
				if isinstance(group, str) and j['name'] == group:
					response_2 = simple_get_request(fenix_api_space + j['id'])
					for k in response_2.json()['containedSpaces']:
						if k['name'] == room:
							return k['id']
						else:
							return 'wrong room or room invalid'
				else:
					return 'wrong group or group invalid'
		else:
			return 'invalid floor'

def api_availability():
	"""Check the api
		
		:return:	 bool or str
	"""
	#HTTP GET request
	response = simple_get_request(fenix_api_space)

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
		:return:     dict or a str
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
	"""Get free rooms in specific date

		:param date: datetime 
		:return:     dict
	"""

	day = date.strftime("%d/%m/%Y")
	time = datetime.strptime(date.strftime("%H:%M"), "%H:%M")

	results = { i: "" for i in rooms.keys()}

	for room in rooms.keys():
		week_schedule = get_room_week_data(day, room)
		if day in week_schedule:
			free = True
			for lesson in week_schedule[day]:
				if isinstance(lesson, dict):
					start, end = datetime.strptime(lesson["start"], "%H:%M"), \
								 datetime.strptime(lesson["end"], "%H:%M")
					if start <= time <= end:
						free = False
						results[room] = ": Room not free!"
						break
			if free:
				results[room] = ": Room free!"
		elif isinstance(week_schedule, str):
			results[room] = week_schedule
		else:
			results[room] = ": Free all day or closed"
	return results

file = open("rooms.txt", "r")
contents = file.read()
rooms = ast.literal_eval(contents)
file.close()

if not(api_availability()):
	print("Api is unavalable")
else:
	now = datetime.now()
	data = free_rooms(now)
	for i in data.keys():
		print(i, data[i]) 
