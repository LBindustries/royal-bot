﻿# -*- coding: utf-8 -*-
import requests
import filemanager

##Per far funzionare questa libreria serve un file "lastid.txt" contenente l'update ID dell'ultimo messaggio non letto e un file "telegramapi.txt" contenente il token di accesso del bot assegnato da @BotFather.
telegramtoken = filemanager.readFile('telegramapi.txt')

#definiamo la variabile globale chat se no si blocca tutto? forse?
chat = 0

def getUpdates():
	"""Ricevi gli ultimi aggiornamenti dal server di Telegram e restituisci l'ultimo messaggio non letto."""
	parametri = {
		'offset': filemanager.readFile("lastid.txt"), #Update ID del messaggio da leggere
		'limit': 1, #Numero di messaggi da ricevere alla volta, lasciare 1
		'timeout': 1800, #Secondi da mantenere attiva la richiesta se non c'e' nessun messaggio
	}
	while(True):	
		data = requests.get("https://api.telegram.org/bot" + telegramtoken + "/getUpdates", params=parametri).json()
		if(data['ok'] == True):
			if(data['result'] != []):
				writeFile("lastid.txt", str(data['result'][0]['update_id'] + 1))
				#sporco hack per non far crashare il bot ogni 10 secondi; prima o poi capirò il senso di certe risposte nell'api di telegram
				if(data['result'][0]['message'] != None):
					if(data['result'][0]['message']['text'] != ""):
						return data['result'][0]['message']

def sendMessage(content, to=chat, tastiera=""):
	"""Manda un messaggio a una chat."""
	#Parametri del messaggio
	parametri = {
		'chat_id': to, #L'ID della chat a cui mandare il messaggio, Royal Games: -2141322
		'text': content, #Il messaggio da mandare
		'reply_markup': tastiera,
		'parse_mode': 'Markdown', #Formattare il messaggio?
		'disable_web_page_preview': True,
		
	}
	#Manda il messaggio
	r = requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendMessage", params=parametri)
	
def forwardMessage(msg, sentby, to=chat):
	"""Inoltra un messaggio mandato in un'altra chat."""
	#Parametri del messaggio
	parametri = {
		'chat_id': to,
		'from_chat_id': sentby,
		'message_id': msg,
	}
	#Manda la richiesta ai server di Telegram.
	requests.get("https://api.telegram.org/bot" + telegramtoken + "/forwardMessage", params=parametri)

def sendLocation(lat, long, to=chat):
	"""Manda una posizione sulla mappa."""
	#Parametri del messaggio
	parametri = {
		'chat_id': to,
		'latitude': lat,
		'longitude': long,
	}
	#Manda la richiesta ai server di Telegram.
	requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendLocation", params=parametri)

def sendChatAction(type='typing', to=chat):
	"""Visualizza lo stato "sta scrivendo" del bot."""
	#Parametri del messaggio
	parametri = {
		'chat_id': to,
		'action': type,
	}
	#Manda la richiesta ai server di Telegram.
	requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendChatAction", params=parametri)