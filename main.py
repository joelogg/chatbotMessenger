# Ian Annase
# 1/24/18

import requests
import json
from lyrics_api import *

# example call: base_url + lyrics_matcher + format_url + artist_search_parameter + artist_variable + track_search_parameter + track_variable + api_key
# example json print: print(json.dumps(api_call, sort_keys=True, indent=2))

while True:
    print()
    print("Bienvenido a Musixmatch API!")
    print()

    
  
    print("Escribe parte de la letra?")
    track_name = input("> ")
    print()
    api_call = base_url + track_search + format_url + word_in_lyrics_parameter + track_name + api_key


    
    request = requests.get(api_call)
    data = request.json()
    tracks = data['message']['body']['track_list']
    cantRespuestas = len(tracks)

    ids = []
    nameTracks = []
    nameArtist = []

    i = 1
    for track in tracks:
    	dataTrack = track['track']
    	ids.append(dataTrack['track_id'])
    	nameTracks.append(dataTrack['track_name'])
    	nameArtist.append(dataTrack['artist_name'])

    	print("Opción: ", i)    	
    	print("-Nombre de la canción: ", dataTrack['track_name'])
    	print("-Nombre del artista: ", dataTrack['artist_name'])
    	print()

    	i = i + 1


    print("Elija una opcion")
    track_select = input("> ")

    track_select = int(track_select)-1

    while track_select<0 or track_select>=cantRespuestas:
    	print("Elija opción valida")
    	track_select = input("> ")

    api_call = base_url + lyrics_track_matcher + format_url + track_id_parameter + str(ids[track_select]) + api_key
    request = requests.get(api_call)
    data = request.json()

    data = data['message']['body']['lyrics']['lyrics_body']

    print("Nombre de la canción: ", nameTracks[track_select])
    print("Nombre del artista: ", nameArtist[track_select])
    print("Letra: ")
    print(data)
    
    

    break

    
#Ella durmió al calor de las masas