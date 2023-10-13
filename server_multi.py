"""
codes d'arrêt:
 - err -> Une erreur est apparue : seulement close()
 - vol -> Fermeture volotaire du jeu :
							si idd == 0 -> STOP+close() (fermeture client+serveur)
							sinon       -> STOP+close() (fermeture client)
 -per -> Le joueur a perdu/gagné : STOP+close() (fermeture client dans tous les cas)
"""
import socket
from math import sqrt
import threading, time, random


host              = ''
port              = 8080
s                 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
nb_j              = 0
coos              = {}
bouffe            = {} #Dictionnaire des bouffes à mettre à jour par ID de j
tab_bouffe        = set() #Répertoire de toutes les bouffes de la map
dict_flags        = {} #clefs : id_flag ; value : (x,y),[r,b]
dict_team         = {} #clef : idd; values : couleur (r ou b)
last_sent_flag    = {} #key : idd, values : [r,b]
tab_joueur_actif  = [] #idd des joueurs non-deconnectés
TAILLE_MAX_X      = 720*2
TAILLE_MAX_Y      = 480*2
DISTANCE_FLAGS    = 100
AUGMENTATION_FLAG = 0.2
WAIT              = 0
kill              = {}
end 			  = {}	
server_running    = True

lock_nb_j             = threading.Lock()
lock_tab_bouffe       = threading.Lock()
lock_bouffe           = threading.Lock()
lock_coos             = threading.Lock()
lock_WAIT             = threading.Lock()
lock_dict_flags       = threading.Lock()
lock_last_sent_flag   = threading.Lock()
lock_dict_team        = threading.Lock()
lock_tab_joueur_actif = threading.Lock()

def worker(c,addr,s):
	"""
	Permet de gérer une connexion au serveur : Réceptionne, traite et réponds aux requêtes
	Entrée : c (connexion), addr (tuple, ip et port du client)
	Sortie : None
	"""
	global WAIT, server_running
	lock_nb_j.acquire()
	idd = nb_j 
	lock_nb_j.release()
	thread_running = True

	while thread_running:
		#Réception et traitement infos
		data = b''
		while data[-1:] != b'|':
			try:
				buff = c.recv(1)
			except (ConnectionResetError,KeyboardInterrupt) as err:
				print('Réception : Connexion rompue zzz ')
				close(c, idd,addr[0],'err')
				print("Closed")
				return None
			else:
				if buff == b'':
					print('Réception : Connexion rompue zzz ')
					close(c, idd, addr[0],'err')
					print("Closed")
					return None
			data+= buff
		data = data.decode('utf-8')
		if not data:
			print(f"Connexion avec {addr[0]}:{addr[1]} rompue")
			close(c,idd,addr[0],'err')
			break
		else:

			data = data[:-1]
			message_a_envoyer = ''

			if data.startswith('STOP:'):
				data = data.split(':')[1]
				thread_running = False
				if data == 'vol' and idd == 0:
					server_running = False
					s.shutdown(0)
					s.close()				
					c.sendall('END|'.encode('utf-8'))
				close(c,idd,addr[0],data)

			elif data == 'INIT':
				if WAIT != 1:
					message_a_envoyer = 'SB;'
					lock_tab_joueur_actif.acquire()
					for j in tab_joueur_actif:
						message_a_envoyer += f'{j[0]},{j[1]}:'
					lock_tab_joueur_actif.release()
					message_a_envoyer+='|'
					message_a_envoyer = message_a_envoyer.encode('utf-8') 

				else:
					str_id_ennemis = ",".join([str(i) for i in list(coos.keys()) if i != idd])

					tab_coos_bouffe = []

					for i in tab_bouffe:
						tab_coos_bouffe.append(','.join([str(j) for j in i]))

					str_coos_bouffe = ':'.join(tab_coos_bouffe)
					str_flags = ''
					for f in dict_flags:
						str_flags += f'{f},{dict_flags[f][0][0]},{dict_flags[f][0][1]}:'
					str_flags = str_flags[:-1]

					str_teams = ""
					for t in dict_team:
						str_teams += f'{t},{dict_team[t]}:'
					message_a_envoyer = f'{idd};{coos[idd][0]},{coos[idd][1]};{str_id_ennemis};{str_coos_bouffe};{str_flags};{str_teams}|'.encode('utf-8')
				
			elif data.startswith('POS:'):
				#Traitement
				data = data.split(':')[1]
				data = [int(i) for i in data.split(',')]
				lock_coos.acquire()
				coos[idd] = tuple(data) #Tuple - lourd que list (sys.getsizeof)
				lock_coos.release()

				#Réponse
				if len(bouffe[idd][0]) != 0 or len(bouffe[idd][1]) != 0:
					message_a_envoyer = f"{':'.join([','.join([str(j) for j in i]) for i in bouffe[idd][0]])};{':'.join([','.join([str(j) for j in i]) for i in bouffe[idd][1]])}|".encode('utf-8')
					lock_bouffe.acquire()
					bouffe[idd] = ([],[])
					lock_bouffe.release()

				else:
					message_a_envoyer = "OK|".encode('utf-8')
				

			elif data == 'UPDATE':
				if idd in kill:
					message_a_envoyer = f'KILLED,{kill[idd]};|'.encode('utf-8')
					del kill[idd]
				elif idd in end:
					message_a_envoyer = f'{end[idd]},{end[idd]};|'.encode('utf-8')
				else:
					rep = ''
					for i in coos:

						if i != idd:
							
							rep+= f'{i},{coos[i][0]},{coos[i][1]},{coos[i][2]}:'
					if rep == '' : 
						rep = 'OK'
					else:
						pass#rep = rep[:-1]
					rep+=';'

					str_flags = ''
					for id_f in dict_flags:
						lock_last_sent_flag.acquire()
						if dict_flags[id_f][1] != last_sent_flag[idd]:
							str_flags+=f'{id_f},{round(dict_flags[id_f][1][0],2)},{round(dict_flags[id_f][1][1],2)}:'
							last_sent_flag[idd] = [dict_flags[id_f][1][0],dict_flags[id_f][1][1]]
						lock_last_sent_flag.release()
					str_flags = str_flags

					if str_flags == '':
						rep+='OK'
					else:
						rep+=str_flags

					rep+='|'
					
					message_a_envoyer = rep.encode('utf-8')

			elif data.startswith('FOOD:'):

				data = data.split(':')[1]
				data = data.split(',')
				x,y = int(data[0]), int(data[1])

				nx,ny = random.randint(-TAILLE_MAX_X,TAILLE_MAX_X),random.randint(-TAILLE_MAX_Y,TAILLE_MAX_Y)
				while (nx,ny) in tab_bouffe:
					nx,ny = random.randint(-TAILLE_MAX_X,TAILLE_MAX_X),random.randint(-TAILLE_MAX_Y,TAILLE_MAX_Y)

				#Évite l'apparition de la nourriture au même endroit qu'avant (pas accidentel mais presque)
				lock_tab_bouffe.acquire()
				tab_bouffe.add((nx,ny))
				tab_bouffe.discard((x,y))
				lock_tab_bouffe.release()

				lock_bouffe.acquire()
				for i in bouffe:
					if True: 
						bouffe[i][0].append((x,y))
						bouffe[i][1].append((nx,ny))
				lock_bouffe.release()

				#message_a_envoyer = f'{nx};{ny}|'.encode('utf-8')

			elif data == 'GO':
				lock_tab_joueur_actif.acquire()
				mid = round(len(tab_joueur_actif)/2)
				if mid < 1:
					mid = 1
				nb_b = 0
				nb_r = 0
				for j in tab_joueur_actif:
					team = random.choice(['r','b'])
					ok = False
					while not ok:
						if team == 'r' and nb_r < mid:
							lock_dict_team.acquire()
							dict_team[j[0]] = 'r'
							lock_dict_team.release()
							nb_r +=1
							ok = True
						elif team == 'b' and nb_b < mid:
							lock_dict_team.acquire()
							dict_team[j[0]] = 'b'
							lock_dict_team.release()
							nb_b +=1
							ok = True
						else:
							team = random.choice(['r','b'])
				lock_tab_joueur_actif.release()

				lock_WAIT.acquire()
				WAIT += 0.5
				lock_WAIT.release()
				message_a_envoyer = 'OK|'.encode('utf-8')
			
			elif data.startswith('KILL:'):
				data = data.split(':')[1]
				kill[int(data)] = idd
				lock_coos.acquire()
				coos[int(data)] = (0,0,coos[int(data)][2])
				lock_coos.release()
				message_a_envoyer = 'OK|'.encode('utf-8')

			elif data.startswith("FLAG:"):
				data = data.split(':')[1].split(',')
				id_flag = int(data[0])
				if dict_team[idd] == 'r':
					couleur = 0
				else:
					couleur = 1
				
				lock_dict_flags.acquire()
				if dict_flags[id_flag][1][(couleur+1)%2] > 0:

					if dict_flags[id_flag][1][(couleur+1)%2] - AUGMENTATION_FLAG < 0:
						dict_flags[id_flag][1][(couleur+1)%2] = 0
					else:
						dict_flags[id_flag][1][(couleur+1)%2] -= AUGMENTATION_FLAG

				else:

					if dict_flags[id_flag][1][couleur]+AUGMENTATION_FLAG >= 100:
						dict_flags[id_flag][1][couleur] = 100
						nb_flags = len(dict_flags)
						nb_ok = 0
						for id_f in dict_flags:
							if dict_flags[id_f][1][couleur] == 100:
								nb_ok += 1
						if nb_ok == nb_flags:
							for j in dict_team:
								if dict_team[j] == dict_team[idd]:
									end[j] = 'WON'
								else:
									end[j] = 'LOST'
					else:
						dict_flags[id_flag][1][couleur] += AUGMENTATION_FLAG

				lock_dict_flags.release()
				

				#message_a_envoyer = 'OK|'.encode('utf-8')

			if message_a_envoyer!= '':
				c.sendall(message_a_envoyer)
					


		time.sleep(0.01)
	print(f"{addr[0]}:{addr[1]} (id : {idd}) déconnecté")
	
def close(c,idd, addr_ip,code):
	"""
	Permets de fermer la connexion c ainsi que la socket du serveur (voir codes d'arrêt ci-dessus)
	Entrée : c (connexion)
	Sortie : None
	"""

	global s
	#Ferme la connexion
	lock_tab_joueur_actif.acquire()
	if idd in tab_joueur_actif:
		del tab_joueur_actif[tab_joueur_actif.index((idd))]
	lock_tab_joueur_actif.release()
	lock_coos.acquire()
	coos[idd] = ('','','')
	lock_coos.release()

	if code != 'err':
		time.sleep(0.05)
		c.shutdown(0)
		c.close()
	if idd == 0:
		s.shutdown(0)
		s.close()

def gen():
	"""
	Génère les nourritures et les drapeaux
	Entrée : None
	Sortie : None
	"""
	global tab_bouffe,lock_tab_bouffe,lock_WAIT, WAIT,lock_dict_flags, dict_flags,DISTANCE_FLAGS
	lock_tab_bouffe.acquire()

	for i in range(-TAILLE_MAX_X,TAILLE_MAX_X):
		for j in range(-TAILLE_MAX_Y,TAILLE_MAX_Y):
			if random.randint(0,5000) == 1:
				tab_bouffe.add((i,j))


	lock_tab_bouffe.release()

	lock_dict_flags.acquire()

	dict_flags[0] = ((-1400,100),[0,0])
	dict_flags[1] = ((0,-920),[0,0])
	dict_flags[2] = ((500,100),[0,0])
	lock_dict_flags.release()

	lock_WAIT.acquire()
	WAIT += 0.5
	lock_WAIT.release()
	print("OK")


def start_serv():
	"""
	Permet de lancer un serveur permettant à toutes les personnes d'un réseau local de se connecter pour jouer
	Entrée : None
	Sortie : None
	"""
	global nb_j,tab_bouffe,lock_tab_bouffe,lock_nb_j, coos, lock_coos, server_running,s
	#Remplissage tab_bouffe

	generation_bouffe = threading.Thread(target = gen)
	generation_bouffe.start()
	
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((host, port))
	print("Serveur démarré\nEn attente de requêtes...")
	while WAIT != 1:
		s.listen(1)
		try:
			conn, addr = s.accept()

			
		except :
			print("Le serveur ne peut pas accepter une connexion !")
			break
		
		print(f"Nouvelle connexion avec {addr[0]}:{addr[1]}, id : {nb_j}")

		lock_coos.acquire()
		coos[nb_j] = [random.randint(-TAILLE_MAX_X,TAILLE_MAX_X),random.randint(-TAILLE_MAX_Y,TAILLE_MAX_Y),44]
		lock_coos.release()

		lock_bouffe.acquire()
		bouffe[nb_j] = ([],[])
		lock_bouffe.release()

		new_thread = threading.Thread(target = worker, args=(conn,addr,s))
		new_thread.start()

		tab_joueur_actif.append((nb_j,addr[0]))

		lock_last_sent_flag.acquire()
		last_sent_flag[nb_j] = [0,0]
		lock_last_sent_flag.release()

		lock_nb_j.acquire()
		nb_j += 1
		lock_nb_j.release()



	print("Serveur éteint")

if __name__ == '__main__':
	start_serv()
