#./ngrok http 8080

import os, sys
from flask import Flask, request
from pymessenger import Bot
import requests
import json
from lyrics_api import *
import pickle

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "PAGE_ACCESS_TOKEN"

bot = Bot(PAGE_ACCESS_TOKEN)

@app.route('/', methods=['GET'])
def verify():
	#Verificacion WebHook
	# cuando el endpoint este registrado como webhook, debe mandar de vuelta
    # el valor de 'hub.challenge' que recibe en los argumentos de la llamada
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return '<!DOCTYPE html>\
			<html>\
			<head>\
				<title>Estadisticas</title>\
			</head>\
			<body>\
				<p style="background-color: gray;">Hola</p>\
			</body>\
			</html>', 200



@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # alguien envia un mensaje

                    sender_id = messaging_event["sender"]["id"]        # el facebook ID de la persona enviando el mensaje
                    recipient_id = messaging_event["recipient"]["id"]  # el facebook ID de la pagina que recibe (tu pagina)

                    if sender_id!='798920460252131':
                    	
	                    if messaging_event.get('message'):
	                    	if 'text' in messaging_event['message']:
	                    		message_text = messaging_event["message"]["text"]  # el texto del mensaje
	                    	else:
	                    		message_text = "Sin Texto"

	                    #Respuesta
	                    primeraVez = True
	                   
	                    try:
	                    	data_estado = leerData(sender_id)
	                    	log(data_estado)
	                    	primeraVez = False
	                    except:
	                    	primeraVez = True
	                    


	                    if primeraVez:
	                    	mensaje = "Bienvenido!!! \nOpción 1: Buscar canción por concidencia."
	                    	guardardata(sender_id, "Esperando1")

	                    else:

	                    	entroEsperando = False

	                    	if message_text != "Sin Texto":

	                    		if data_estado=="Esperando1" and message_text.isdigit():
	                    			if message_text=="1":
	                    				mensaje = "Escribe parte de la letra"
	                    				guardardata(sender_id, "Esperando2")
	                    				entroEsperando = True

	                    			if message_text=="2":

	                    				guardardata(sender_id, "Esperando1")
	                    				entroEsperando = True
	                    				mensaje = mostrarFavoritos(sender_id)
	                    				mensaje = mensaje + "\n \n (1) Buscar canción por concidencia. \n (2) Ver canciones favoritas."


	                    		if data_estado=="Esperando2":
	                    			mensaje, ids, nameTracks, nameArtist = buscarCoincidencia(message_text)
	                    			guardardata(sender_id, "Esperando3")
	                    			guardardata("ids"+sender_id, ids)
	                    			guardardata("nameTracks"+sender_id, nameTracks)
	                    			guardardata("nameArtist"+sender_id, nameArtist)
	                    			entroEsperando = True

	                    		if data_estado=="Esperando3" and message_text.isdigit():
	                    			correcto, mensaje = buscarCancion(message_text, sender_id)
	                    			if correcto:
	                    				guardardata(sender_id, "Esperando1")
	                    				mensaje = mensaje + "\n \n (1) Buscar canción por concidencia. \n (2) Ver canciones favoritas."
	                    			
	                    			entroEsperando = True

	                    		


	                    		if False==entroEsperando:
	                    			mensaje = "Bienvenido!!! \n (1) Buscar canción por concidencia. \n (2) Ver canciones favoritas."
	                    			guardardata(sender_id, "Esperando1")


	                    	else:
	                    		mensaje = "Bienvenido!!! \n (1) Buscar canción por concidencia. \n (2) Ver canciones favoritas."
	                    		guardardata(sender_id, "Esperando1")


	                    response = mensaje

	                    bot.send_text_message(sender_id, response)

                    



    return "ok", 200

def buscarCoincidencia(track_name):

	mensaje = ""

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

		mensaje = mensaje + "----------------\nOpción: " + str(i) + \
			"\n----------------\n-Nombre de la canción: " + dataTrack['track_name'] +\
			"\n-Nombre del artista: " + dataTrack['artist_name'] + "\n"

		i = i + 1

	mensaje = mensaje + "\nElija una opción"

	return mensaje, ids, nameTracks, nameArtist

def buscarCancion(track_select, sender_id):
	ids = leerData("ids"+sender_id, )
	nameTracks = leerData("nameTracks"+sender_id, )
	nameArtist = leerData("nameArtist"+sender_id, )
	cantRespuestas = len(ids)

	mensaje = ""

	track_select = int(track_select)-1

	correcto = False

	if track_select<0 or track_select>=cantRespuestas:
		mensaje = "Elija opción valida"
		correcto = False

	else:
		correcto = True
		api_call = base_url + lyrics_track_matcher + format_url + track_id_parameter + str(ids[track_select]) + api_key
		request = requests.get(api_call)
		data = request.json()

		data = data['message']['body']['lyrics']['lyrics_body']

		mensaje = "Nombre de la canción: " +  nameTracks[track_select] + "\n"
		mensaje = mensaje + "Nombre del artista: " + nameArtist[track_select] + "\n"
		mensaje = mensaje + "Letra: \n"
		mensaje = mensaje + data + "\n"

		try:
			data_favoritos = leerData("favoritos"+sender_id)
		except:
			data_favoritos = []

		data_favoritos.append([ids[track_select], nameTracks[track_select], nameArtist[track_select]])

		guardardata("favoritos"+sender_id, data_favoritos)




		mensaje = mensaje + "\nAgregado a favoritos"


	return correcto, mensaje

def mostrarFavoritos(sender_id):
	mensaje = "Favoritos \n"

	try:
		data_favoritos = leerData("favoritos"+sender_id)
	except:
		data_favoritos = []

	if len(data_favoritos)<=0:
		mensaje = "No tiene favoritos"
	else:
		for i in range(len(data_favoritos)):
			idT = data_favoritos[i][0]
			nameT = data_favoritos[i][1]
			artistT = data_favoritos[i][2]

			mensaje = mensaje + "- (" + str(i+1) + ") \nTítulo: " + nameT + "\nArtista: " + artistT + "\n"


	return mensaje


def guardardata(id, data):
	# Escritura en modo binario, vacía el fichero si existe
	fichero = open(str(id)+'.pckl','wb')
	# Escribe la colección en el fichero 
	pickle.dump(data, fichero) 
	fichero.close()

def leerData(id_M):
	# Lectura en modo binario 
	fichero = open(id_M+'.pckl','rb') 
	# Cargamos los datos del fichero
	data = pickle.load(fichero)
	fichero.close()
	
	return data
	

def log(message): 
    print(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True, port = 80)
    #app.run(debug=True)