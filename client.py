import socket,time
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)

def connect(host, port):
	"""
	Permet de conneceter la socket s au server host:port
	Entrée : host (str, adresse ip du server), port (int, port de connexion server)
	Sortir : (socket)
	"""
	global s
	try:
		s.connect((host,port))
	except:
		print("Impossible de se connecter !") #Message d'erreur à faire en graphique
		return None
	else:
		print(f"Connexion établie avec le serveur") 
		return s

def envoie(s,m):
	"""
	Permet d'envoyer une requête au server et d'attendre sa réponse
	Entrée : s (socket), m (str, contenu de la requête)
	Sortie : (str, réponse du serveur)
	"""
	message = m
	#print("client envoie : ",m)
	len_message = len(message)
	sent = 0
	while sent < len_message:
		sent += s.send(message.encode('utf-8'))
		if sent == 0:
			print('Envoi : Connexion rompue')
			break
		message = m[:sent]

	
	result = b''
	while result[-1:] != b'|':
		buff = s.recv(1)
		if not buff:
			print('Réception : Connexion rompue')
			return None
		result+= buff
	result = result.decode('utf-8')
	#print("client reçu :",result)
	return result

def envoie_sans_reponse(s,m):
	"""
	Permet d'envoyer une requête au server sans attendre de réponse
	Entrée : s (socket), m (str, contenu de la requête)
	Sortie : (bool)
	"""
	message = m
	len_message = len(message)
	sent = 0
	while sent < len_message:
		sent += s.send(message.encode('utf-8'))
		if sent == 0:
			print('Envoi : Connexion rompue')
			break
		message = m[:sent]

	return True

def close(code):
	"""
	Permet de fermer la socket en spécifiant un code d'arrêt
	Entrée : code (str)
	Sortie : None
	"""
	global s
	envoie(s,f'STOP:{code}|')
	time.sleep(0.1)
	s.shutdown(0)
	s.close()
	print('FINI')

