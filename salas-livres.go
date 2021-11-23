/*
	Guilherme Batalheiro
	22/11/2021
	Available Class Rooms
*/

package main

import (
	"bufio"
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)

type Room struct {
	name string
	id   string
}

func printAvailability(room Room) {
	_, response := room.getAvailability()
	println(room.name + ":" + response)
}

func (room Room) getAvailability() (bool, string) {

	type JsonResponse struct {
		Events []struct {
			Type   string `json:"type"`
			Start  string `json:"start"`
			End    string `json:"end"`
			Day    string `json:"day"`
			Period struct {
				Start string `json:"start"`
				End   string `json:"end"`
			} `json:"period"`
		} `json:"events"`
	}

	getSecondsFromString := func(str string) int {
		return ((int(str[0])-48)*10+(int(str[1])-48))*3600 + ((int(str[3])-48)*10 + (int(str[4])-48)*60)
	}

	resp, err := http.Get("https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/" + room.id)
	if err != nil {
		log.Fatal(err)
	}

	if resp.StatusCode != 200 {
		b, _ := ioutil.ReadAll(resp.Body)
		return false, room.name + string(b)
	}

	dec := json.NewDecoder(resp.Body)
	var jsonResp JsonResponse

	if err := dec.Decode(&jsonResp); err != nil {
		log.Fatal(err)
	}

	currentDate := time.Now()

	for _, x := range jsonResp.Events {
		if currentDate.Format("02/01/2006") == x.Day &&
			getSecondsFromString(x.Start) <= getSecondsFromString(currentDate.Format("15:04")) &&
			getSecondsFromString(currentDate.Format("15:04")) <= getSecondsFromString(x.End) {

			return false, "not available until " + x.End + " because of " + x.Type
		}
	}

	return true, "available"
}

func APIAvailable() bool {
	type JsonResponse struct {
		InstitutionName string `json:"institutionName"`
	}

	resp, err := http.Get("https://fenix.tecnico.ulisboa.pt/api/fenix/v1/about")
	if err != nil {
		log.Fatal(err)
	}

	if resp.StatusCode != 200 {
		b, _ := ioutil.ReadAll(resp.Body)
		log.Fatal(string(b))
	}

	dec := json.NewDecoder(resp.Body)
	var jsonResp JsonResponse

	if err := dec.Decode(&jsonResp); err != nil {
		log.Fatal(err)
	}

	return jsonResp.InstitutionName == "Instituto Superior Técnico"
}

func main() {
	if APIAvailable() {

		file, err := os.Open("rooms.txt")
		if err != nil {
			log.Fatal(err)
		}
		defer file.Close()

		var rooms []Room

		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			words := strings.Fields(scanner.Text())

			room := Room{
				name: words[0],
				id:   words[1],
			}

			rooms = append(rooms, room)
		}

		if err := scanner.Err(); err != nil {
			log.Fatal(err)
		}

		var wg sync.WaitGroup

		for _, room := range rooms {
			wg.Add(1)
			go func(room Room) {
				defer wg.Done()
				printAvailability(room)
			}(room)
		}

		wg.Wait()
	}
}
