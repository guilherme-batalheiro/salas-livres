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

FENIX_API = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/"
FENIX_API_SPACES = FENIX_API + "spaces/"
FENIX_API_SPACES_TAGUS = FENIX_API_SPACES + "2448131365084"					#"2448131365084" is the id of the building TagusPark

def get_request(url):
	"""Simple get request
		
		:param url:  str
		:return:	 HTTP response
	"""
	try:
		response = requests.get(url, timeout=10)
		response.raise_for_status()
	except requests.exceptions.Timeout:
		return str("The request timed out!")
	except requests.exceptions.ConnectionError as errc:
		return str(f"Error Connecting: {errc}")
	except requests.exceptions.HTTPError as http_err:
		return str(f"HTTP error occurred: {http_err}")
	except requests.exceptions.RequestException as err:
		return str(f"Other error occurred: {err}")
	return response

def get_room_id(room, floor, group):
	"""Gets the room id
		
		:param room:  str
		:param floor: str
		:param group: str
		:return:	  str
	"""
	#HTTP GET request
	response = get_request(FENIX_API_SPACES_TAGUS)
	for i in response.json()['containedSpaces']:
		if isinstance(floor, str) and i['name'] == floor:
			response_1 = get_request(FENIX_API_SPACES + i['id'])
			for j in response_1.json()['containedSpaces']:
				if isinstance(group, str) and j['name'] == group:
					response_2 = get_request(FENIX_API_SPACES + j['id'])
					for k in response_2.json()['containedSpaces']:
						if k['name'] == room:
							return k['id']
						else:
							raise ValueError('get_room_id: room argument invalid')
				else:
					raise ValueError('get_room_id: group argument invalid')
		else:
			raise ValueError('get_room_id: floor argument invalid')

def api_availability():
	"""Check api
		
		:return:	 bool or str
	"""
	#HTTP GET request
	response = get_request(FENIX_API_SPACES)

	if "Serviço em Manutenção" in response.text or isinstance(response, str):
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
	response = get_request(FENIX_API_SPACES + room)
	json_response = response.json()

	if "error" in json_response: 
		return str(json_response["error"] + ": " + json_response["description"])
	elif "events" not in json_response:
		return str(": No info :( sorry!!! or it is closed all week.")
	else:
		room_week_data = clean_data_room(json_response["events"])
		return room_week_data

def free_rooms(date, rooms):
	"""Get free rooms from the rooms.txt on a specific date

		:param date:  datetime
		:param rooms: dict 
		:return:      dict
	"""

	day = date.strftime("%d/%m/%Y")
	time = datetime.strptime(date.strftime("%H:%M"), "%H:%M")

	results = { i: "" for i in rooms.keys()}

	for room in rooms.keys():
		week_schedule = get_room_week_data(day, rooms[room])
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

if __name__ == '__main__':
	if not(api_availability()):
		print("Api is unavalable")
	else:
		file = open("rooms.txt", "r")
		contents = file.read()
		rooms = ast.literal_eval(contents)
		file.close()

		now = datetime.now()
		data = free_rooms(now, rooms)
		for i in data.keys():
			print(i, data[i])