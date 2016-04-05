# -*- coding: utf-8 -*-
import telegram
import pickle


class Player:
    telegramid = int()
    username = str()
    role = 0  # 0 normale | 1 rryg | 2 resistenza
    alive = True
    votedfor = str()
    special = False

    def message(self, text):
        """Manda un messaggio al giocatore
        :param text: Testo del messaggio
        """
        telegram.sendmessage(text, self.telegramid)


class Game:
    groupid = int()
    adminid = int()
    players = list()

    def message(self, text):
        """Manda un messaggio alla chat generale del gioco
        :param text: Testo del messaggio
        """
        telegram.sendmessage(text, self.chat)

    def adminmessage(self, text):
        """Manda un messaggio all'admin del gioco
        :param text: Testo del messaggio
        """
        telegram.sendmessage(text, self.adminid)

    def evilmessage(self, text):
        """Manda un messaggio al team dei nemici del gioco
        :param text: Testo del messaggio
        """
        for player in self.players:
            if player.role == 1:
                telegram.sendmessage(text, player.telegramid)

    def status(self) -> str:
        """Restituisci lo stato attuale della partita in una stringa unicode"""
        tosend = "Stato attuale del gioco: \n"
        for player in self.players:
            if not player.alive:
                tosend += "\U0001F480 "
            else:
                tosend += "\U0001F636 "
            tosend += player.username + "\n"
        return tosend

    def fullstatus(self) -> str:
        """Restituisci lo stato attuale della partita (per admin?) in una stringa unicode"""
        tosend = "Stato attuale del gioco: \n"
        for player in self.players:
            if not player.alive:
                tosend += "\U0001F480 "
            elif player.role == 1:
                tosend += "RRYG "
            else:
                tosend += "\U0001F636 "
            tosend += player.username + "\n"
        return tosend

    def findusername(self, username) -> Player:
        """Trova un giocatore con un certo nome utente
        :param username: Nome utente da cercare
        """
        for player in self.players:
            if player.username == username:
                return player
        else:
            return None

    def findid(self, telegramid) -> Player:
        """Trova un giocatore con un certo ID di telegram
        :param telegramid: ID da cercare
        """
        for player in self.players:
            if player.telegramid == telegramid:
                return player
        else:
            return None

    def addplayer(self, player):
        """Aggiungi un giocatore alla partita
        :param player: Oggetto del giocatore da aggiungere
        """
        self.players.append(player)

    def mostvoted(self) -> Player:
        """Trova il giocatore più votato"""
        votelist = dict()
        for player in self.players:
            if player.votedfor != str():
                if player.votedfor not in votelist:
                    votelist[player.votedfor] = 1
                else:
                    votelist[player.votedfor] += 1
        mostvoted = str()
        mostvotes = int()
        for player in votelist:
            if mostvoted == str():
                mostvoted = player
                mostvotes = votelist[player]
            else:
                if votelist[player] > mostvotes:
                    mostvoted = player
                    mostvotes = votelist[player]
        return self.findusername(mostvoted)

    def save(self):
        """Salva in un file di testo con il numero del gruppo lo stato attuale del gioco"""
        try:
            file = open(str(self.groupid) + ".txt", "w")
        except OSError:
            file = open(str(self.groupid) + ".txt", "x")
        pickle.dump(self, file)

    def endday(self):
        for player in self.players:
            player.votedfor = str()
            if player.role != 0:
                player.special = True
            killed = self.mostvoted()
            killed.alive = False
            self.message(killed.username + " è stato il più votato del giorno.")


def load(filename) -> Game:
    """Restituisci da un file di testo con il numero del gruppo lo stato del gioco (Funzione non sicura, non importare
    file a caso pls)
    :param filename: Nome del file da cui caricare lo stato"""
    try:
        file = open(str(filename) + ".txt", "r")
    except OSError:
        return None
    else:
        return pickle.load(file)


partiteincorso = list()


def findgame(chatid) -> Game:
    for game in partiteincorso:
        if game.groupid == chatid:
            return game
    else:
        return None


while True:
    t = telegram.getupdates()
    if 'text' in t:
        if t['text'].startswith("/newgame"):
            g = findgame(t['chat']['id'])
            if g is None:
                g = Game()
                g.groupid = t['chat']['id']
                g.adminid = t['from']['id']
                partiteincorso.append(g)
            else:
                telegram.sendmessage("Una partita è già in corso qui.", t['chat']['id'], t['message_id'])
        elif t['text'].startswith("/loadgame"):
            # Facendo così mi sovrascrive il Game dentro la lista o no?
            g = findgame(t['chat']['id'])
            add = False
            if g is None:
                add = True
            g = load(t['chat']['id'])
            if add:
                partiteincorso.append(g)
        if t['text'].startswith("/echo"):
            g = findgame(t['chat']['id'])
            if g is None:
                telegram.sendmessage("Nessuna partita in corso.", t['chat']['id'], t['message_id'])
            else:
                g.message(g.fullstatus())