#Nvx designs


import pygame
import time, random
import client, threading, server_multi
from math import sqrt,log
pygame.init()

#CONSTANTES !

TAILLE_MAX_X = 720*2
TAILLE_MAX_Y = 480*2
TAILLE_SCREEN_X = 720
TAILLE_SCREEN_Y = 480
DIAMETRE_BOUFFE = 10
DEPLACEMENT = 10
DISTANCE_FLAG = 100 #SI le joueur est à cette distance d'un drapeau il commence à le prendre
running = True



lock_dict_badguys = threading.Lock()
lock_x_y = threading.Lock()
lock_dict_flags = threading.Lock()
lock_joueur = threading.Lock()
lock_s = threading.Lock()
lock_dict_bouffe = threading.Lock()
lock_a_ajouter_supprimer = threading.Lock()
lock_score = threading.Lock()

screen = pygame.display
screen.set_caption("Mattyéo i Ioudés - Cell Crusade CTF")
titre = pygame.image.load("titre.png")
screen.set_icon(titre)
screen = screen.set_mode((TAILLE_SCREEN_X,TAILLE_SCREEN_Y))

fleche = pygame.image.load("enter.png")
fleche_rect = fleche.get_rect()
fleche_rect.x,fleche_rect.y = 240,300
oui = pygame.image.load("oui.png")
non = pygame.image.load("non.png")
oui_rect = oui.get_rect()
non_rect = non.get_rect()
oui_rect.x,oui_rect.y = 100,250
non_rect.x,non_rect.y = 400,250
besoin_texte = pygame.image.load("texte.png")
input_box = pygame.Rect(265,224, 165, 32)
text = ''
font_accueil = pygame.font.SysFont(None, 32)

bouton_go = pygame.image.load('04.png')
bouton_go = pygame.transform.scale(bouton_go,(75,75))
bouton_go_rect = bouton_go.get_rect()
bouton_go_rect.x, bouton_go_rect.y = 645,405


def conversion(elt):
	"""
	Convertit elt en int, float ou le laisse comme il est
	Entrée : elt (n'importe quel type)
	Sortie : (int ou float ou type de base de elt)
	"""
	if elt == 'OK':
		return True
	try:
		int(elt)
	except:
		try:
			float(elt)
		except:
			return elt
		else:
			return float(elt)
	else:
		return int(elt)
def parse(r):
	"""
	Convertis le résultat d'une requête en un tableau (list)
	Entrée : r (str, résultat de requête sans '|')
	Sortie : (list, les chiffres sont convertis en Int et les nombres flottants en Float)
	"""
	if r == 'OK':
		return True
	resultat_final = []
	var_prov = r.split(';')
	for elt in var_prov:
		if ':' in elt:
			var_prov_nv1 = elt.split(':')
			resultat_prov_nv1 = []
			for elt_nv1 in var_prov_nv1:
				var_prov_nv2 = elt_nv1.split(',')
				resultat_prov_nv2 = []
				for elt_nv2 in var_prov_nv2:

					resultat_prov_nv3 = conversion(elt_nv2)
					resultat_prov_nv2.append(resultat_prov_nv3)

				resultat_prov_nv1.append(resultat_prov_nv2)

		elif ',' in elt:
			var_prov_nv1 = elt.split(',')
			resultat_prov_nv1 = []
			for elt_nv1 in var_prov_nv1:

				resultat_prov_nv2 = conversion(elt_nv1)
				resultat_prov_nv1.append(resultat_prov_nv2)
		else:
			resultat_prov_nv1 = conversion(elt)


		resultat_final.append(resultat_prov_nv1)
	return resultat_final


assert parse("21.6,34:23,56:45,34;21,34:23,56:45,34;1,2,3;4;banane") == [[[21.6, 34], [23, 56], [45, 34]], [[21, 34], [23, 56], [45, 34]], [1, 2, 3], 4, 'banane']

class Player:
	"""
	Classe des joueurs et des ennemis
	"""

	def __init__(self, identifiant, taille=-1,team='',x=0,y=0):
		"""
		Initialise une instance de Joueur permettant de gérer un joueur ou un ennemi
		Entrée : identifiant (int >= 0), taille (float > 0), team (str, 'r' ou 'b'), x (int), y (int)
		Sortie : None
		"""
		if team != '':
			self.team = team
			if team == 'r':
				self.cercle = pygame.image.load("00.png")
			else:
				self.cercle = pygame.image.load("01.png")
		else:
			self.team = ''
			self.cercle = pygame.image.load("03.png")
		self.cercle_rect = self.cercle.get_rect()
		self.cercle_rect.x = 0
		self.cercle_rect.y = 0
		self.taille = taille
		self.ralentissement = 0
		self.x = x
		self.y = y

class Bouffe:
	"""
	Permet de gérer les nourritures présentent sur la carte et de les afficher
	"""
	def __init__(self,x,y):
		"""
		Initialise une instance de Bouffe
		Entrée : x (int), y(int)
		Sortie : None
		"""
		self.cercle = pygame.image.load("miam.png")
		self.cercle_rect = self.cercle.get_rect()
		self.cercle_rect.x = x
		self.cercle_rect.y = y

class Flag:
	"""
	Permet de gérer les drapeaux présents sur la carte
	"""
	def __init__(self,x,y,r,b,id_f):
		"""
		Initialise une instance de Flag
		Entrée : x (int), y (int), r (float >= 0), b (float >= 0), id_f (int >= 0)
		Sortie : None
		"""
		self.flag = pygame.image.load(f'{id_f}_flag_gris.png')
		self.flag_rect = self.flag.get_rect()
		self.x = x
		self.y = y
		self.rouge = r
		self.bleu = b
		self.modele = 'g'
	def __str__(self):
		"""
		Décris l'instance de Flag grâce à un str
		Entrée : None
		Sortie : (str)
		"""
		return f'x -> {self.x}, y -> {self.y}\nRouge -> {self.rouge}, bleu -> {self.bleu}\nModele -> {self.modele}'

class Barre:
	"""
	Permet de gérer la barre de score (en-haut de l'écran)
	"""
	def __init__(self,score_b, score_r, screen):
		"""
		Initialise une instance de Barre
		Entrée : score_b (float >= 0), score_r (float >= 0), screen (pygame.Surface)
		Sortie : None
		"""
		self.score_bleu = score_b
		self.score_rouge = score_r
		self.ecran = screen

		self.surface_bleu = pygame.Surface((0,10))
		self.rect_bleu = self.surface_bleu.get_rect()
		self.rect_bleu.x,self.rect_bleu.y = 10,10
		self.width_bleu = 0

		self.surface_rouge = pygame.Surface((0,10))
		self.rect_rouge = self.surface_rouge.get_rect()
		self.width_rouge = 0

	def afficher_score(self):
		"""
		Affiche l'instance de Barre sur le screen (pygame.Surface)
		Entrée : None
		Sortie : None
		"""
		#Bleus :
		if self.width_bleu != int(((TAILLE_SCREEN_X-20)//2)*(self.score_bleu/100)):
			self.width_bleu = int(((TAILLE_SCREEN_X-20)//2)*(self.score_bleu/100))

			self.surface_bleu = pygame.Surface((self.width_bleu,10))

			self.surface_bleu.fill((0,0,255))
	


		#Rouge :
		if self.width_rouge != int(((TAILLE_SCREEN_X-20)//2)*(self.score_rouge/100)):
			
			self.width_rouge = int(((TAILLE_SCREEN_X-20)//2)*(self.score_rouge/100))

			self.surface_rouge = pygame.Surface((self.width_rouge,10))
			self.surface_rouge.fill((255,0,0))

			
			self.rect_rouge.x, self.rect_rouge.y = (TAILLE_SCREEN_X-10)- self.width_rouge ,10
			

		self.ecran.blit(self.surface_bleu,self.rect_bleu)
		self.ecran.blit(self.surface_rouge,self.rect_rouge)

	def maj(self,flags):
		"""
		Mets à jour l'instance Barre grâce aux information de flags
		Entrée : flags (list)
		Sortie : None
		"""
		lock_dict_flags.acquire()
		diviseur = len(flags)
		if diviseur == 0:
			diviseur = 1
		rouge  = 0
		bleu   = 0
		for f in flags:
			rouge += f.rouge
			bleu  += f.bleu


		lock_dict_flags.release()
		self.score_rouge = round(rouge /diviseur, 3)
		self.score_bleu  = round(bleu  /diviseur, 3)



#Initialisation de la connexion avec le serveur
running_choix_serv = True
in_enter = True
serv_ou_pas = False
serv = False
pas_serv = False
idd0 = False
while running_choix_serv:
	screen.fill((0,0,0))
	if in_enter:
		screen.blit(titre,(225,20))
		screen.blit(fleche,fleche_rect)
	if serv_ou_pas:
		screen.blit(besoin_texte ,(150,150))
		screen.blit(oui,oui_rect)
		screen.blit(non,non_rect)
	if pas_serv:
		pygame.draw.rect(screen, (106,43,224), input_box, 2)
		text_surface = font_accueil.render(text, True, (106,43,224))
		text_rect = text_surface.get_rect(center=input_box.center)
		screen.blit(text_surface, text_rect)
	if serv:
		info_init = parse(client.envoie(s,"INIT|")[:-1])
		if info_init[0] == 'SB':
			info_init = info_init[1]
			pseudos = []
			for duo in info_init:
				if duo != ['']:
					pseudos.append(f'{duo[1]} (id : {duo[0]})')
			for i, pseudo in enumerate(pseudos):
				text_surface = font_accueil.render(pseudo, True, (255,255,255))
				text_rect = text_surface.get_rect(center=(360, 50 + i * 40))
				screen.blit(text_surface, text_rect)
			if idd0:
				screen.blit(bouton_go, bouton_go_rect)
		else:
			running_choix_serv = False

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
				running_choix_serv = False

		if event.type == pygame.MOUSEBUTTONDOWN:
			if fleche_rect.collidepoint(event.pos) and in_enter:
				in_enter = False
				serv_ou_pas = True
			elif oui_rect.collidepoint(event.pos) and serv_ou_pas:
				idd0=True
				server = threading.Thread(target = server_multi.start_serv)
				server.start()
				time.sleep(0.5)
				s = client.connect('localhost',8080)
				if s is None:
					serv = False
					pas_serv= True
					print("On n'arrive pas à se connecter ! Veuillez réessayer")
				else:
					pass
					#running_choix_serv = False
				serv = True
				serv_ou_pas = False
			elif non_rect.collidepoint(event.pos) and serv_ou_pas:
				pas_serv = True
				serv_ou_pas = False
			elif bouton_go_rect.collidepoint(event.pos) and serv and idd0:
				lezgo = parse(client.envoie(s,"GO|")[:-1])
				if lezgo != True:
					print("Pb lancement")
			
		if event.type == pygame.KEYDOWN:

			if event.key == pygame.K_RETURN and pas_serv:
				s = client.connect(text,8080)
				text = ''
				if s is None:
					print("On n'arrive pas à se connecter ! Veuillez-réessayer")
				else:
					print("Connexion réussie")
					pas_serv = False
					serv     = True 

			elif event.key == pygame.K_BACKSPACE:

				text = text[:-1]
			else:

				text += event.unicode

			if event.key == pygame.K_SPACE:
				new_pseudo = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5))
				pseudos.append(new_pseudo)
	pygame.display.flip()
	time.sleep(0.01)
idd = info_init[0]
joueur = Player(idd,40)

x,y = info_init[1][0],info_init[1][1] #Coordonnées absolues (serveur) du joueur
background_x, background_y = info_init[1][0],info_init[1][1]

dict_badguys = {}
cache_bg = {}
if isinstance(info_init[2], int):
	dict_badguys[info_init[2]] = Player(info_init[2])
	cache_bg[info_init[2]] = (0,0,40)
else:
	for id_badguys in info_init[2]:
		dict_badguys[id_badguys] = Player(id_badguys)
		cache_bg[id_badguys] = 40 #taille

dict_bouffe  = {}
a_ajouter = []
a_supprimer = []
for coos_bouffe in info_init[3]:
	dict_bouffe[(coos_bouffe[0], coos_bouffe[1])] = Bouffe(coos_bouffe[0], coos_bouffe[1])

cache_flag = {}
dict_flags = {}
a_maj = ()
for flag in info_init[4]:
	dict_flags[flag[0]] = Flag(flag[1],flag[2],0,0,flag[0])
	cache_flag[flag[0]] = (0,0) #(r,b)


for team in info_init[5]:
	if team != ['']:
		if team[0] == idd:
			joueur.team = team[1]
			if joueur.team == 'r':
				joueur.cercle = pygame.image.load("00.png")
			else:
				joueur.cercle = pygame.image.load("01.png")
		else:
			dict_badguys[team[0]].team = team[1]
			if team[1] == 'r':
				dict_badguys[team[0]].cercle = pygame.image.load("00.png")
			else:
				dict_badguys[team[0]].cercle = pygame.image.load("01.png")


#Fonctions pour les THREADS

def update():
	global dict_badguys, s, joueur,x,y,a_ajouter,a_supprimer,dict_flags,running,score
	
	while running:
		deb = round(time.time(),3)

		lock_s.acquire()
		if running:
			infos_update = parse(client.envoie(s,f"UPDATE|")[:-1])
			lock_s.release()
		else:
			lock_s.release()
			return
		


		#Les BADGUYS
		if infos_update != True:
			infos_adv = infos_update[0]
			infos_flags = infos_update[1]
		else:
			infos_adv = True
			infos_flags == True
		
		if infos_adv not in (True,''):
			if infos_adv[0] == 'KILLED':
				print("Tu t'es fait manger par", infos_adv[1])
				lock_x_y.acquire()
				x,y = 0,0
				lock_x_y.release()
				lock_score.acquire()
				score = 0
				lock_score.release()
				lock_joueur.acquire()
				joueur.taille = int(round(30 * log(score+21),0))
				lock_joueur.release()
				
			elif infos_adv[0] == 'LOST':
				running = False
				lock_s.acquire()
				client.close('per')
				lock_s.release()
				print('Vous avez perdu !')
			elif infos_adv[0] == 'WON':
				running = False
				lock_s.acquire()
				client.close('per')
				lock_s.release()
				print('Vous avez gagné !')
			else:
				for adv in infos_adv:
					if adv != [""]:
						lock_dict_badguys.acquire()

						id_adv = adv[0]
						if not(id_adv in dict_badguys):

							dict_badguys[id_adv] = Player(id_adv)

						if dict_badguys[id_adv].x != adv[1]:
							dict_badguys[id_adv].x = adv[1]

						if dict_badguys[id_adv].y != adv[2]:
							dict_badguys[id_adv].y = adv[2]

						if dict_badguys[id_adv].taille != adv[3]:
							dict_badguys[id_adv].taille = adv[3]

						lock_dict_badguys.release()

		#Les DRAPEAUX
		if infos_flags!= True:
			
			
			for elt in infos_flags:
				if elt != ['']:
					

					lock_dict_flags.acquire()

					dict_flags[elt[0]].rouge = elt[1]
					dict_flags[elt[0]].bleu = elt[2]

					lock_dict_flags.release()

			
		
		if running:
			lock_s.acquire()
			lock_x_y.acquire()
			lock_joueur.acquire()
			infos_pos = parse(client.envoie(s, f'POS:{x},{y},{joueur.taille}|')[:-1])
			lock_s.release()
			lock_x_y.release()
			lock_joueur.release()
		else:
			return None

		#La BOUFFE
		if infos_pos != True:
			lock_a_ajouter_supprimer.acquire()
			if isinstance(infos_pos[0][0],int):
				a_supprimer.append(tuple(infos_pos[0]))
				a_ajouter.append(tuple(infos_pos[1]))
			else:
				for coos in infos_pos[0]:
					a_supprimer.append(tuple(coos))
	
	
				for coos in infos_pos[1]:
					a_ajouter.append(tuple(coos))
			lock_a_ajouter_supprimer.release()

		lock_a_ajouter_supprimer.acquire()
		
		lock_dict_bouffe.acquire()
		for old_coos in a_supprimer:
			if old_coos in dict_bouffe:
				del dict_bouffe[old_coos]

		for nv_coos in a_ajouter:
			if not(nv_coos in dict_bouffe):
				dict_bouffe[(nv_coos[0],nv_coos[1])] = Bouffe(nv_coos[0],nv_coos[1])
		lock_dict_bouffe.release()
		
		a_supprimer = []
		a_ajouter = []
		lock_a_ajouter_supprimer.release()

		temps_d_ex = round(time.time(),3)-deb
		if temps_d_ex < 0.02:
			time.sleep(0.02-temps_d_ex)
	print('Fin updt')

def near_flags():
	
	global dict_flags,x,y, running
	while running:
		
		lock_dict_flags.acquire()
		for f_id in dict_flags:
			flag = dict_flags[f_id]
			dist_joueur = sqrt((x - flag.x)**2 + (y - flag.y)**2)
			if dist_joueur <= DISTANCE_FLAG:
				lock_s.acquire()
				if running:
					client.envoie_sans_reponse(s, f"FLAG:{f_id}|")	
					lock_s.release()
				else:
					lock_s.release()
					return
		lock_dict_flags.release()

		time.sleep(0.02)

	print("Fin flags")




#Initialisation des THREADS

thread_update = threading.Thread(target = update)
thread_near_flags = threading.Thread(target = near_flags)

thread_update.start()
thread_near_flags.start()

#Environnement graphique
pygame.init()
score = 0

#Hitbox
joueur.cercle_rect.x = TAILLE_SCREEN_X//2 #Pygame
joueur.cercle_rect.y = TAILLE_SCREEN_Y//2 #Pygame
joueur.cercle_rect.h = joueur.taille//sqrt(2)
joueur.cercle_rect.w = joueur.taille//sqrt(2)

#Surface
joueur.cercle = pygame.transform.scale(joueur.cercle,(joueur.taille,joueur.taille))
font = pygame.font.SysFont(None, 24)

background = pygame.image.load('background.png')
background_rect = background.get_rect()

#Affichages des coordonnées et du score
affichage_coos = font.render(f'{x},{y}', True,(0,0,0))
affichage_score = font.render(f'{score}', True,(0,0,0))
affichage_taille = font.render(f'{joueur.taille}', True,(0,0,0))

#Affichage de la barre de score
barre_score = Barre(0,0,screen)



#^^Initialisation de la partie (Pygame/GUI)^^
#Temps moyen pour une itération
duree = 0
itera = 0 

while running:
	start = time.time()
	#Nettoie l'écran
	if background_x > background_rect.width:
		background_x=0
		
	elif background_x < 0:
		background_x = background_rect.width


	if background_y > background_rect.height:
		background_y = 0

	elif background_y < 0:
		background_y = background_rect.height

	screen.blit(background, (background_x,background_y))
	screen.blit(background,(background_x, background_y-background_rect.height))
	screen.blit(background,(background_x, background_y+background_rect.height))
	screen.blit(background,(background_x-background_rect.width, background_y))
	screen.blit(background,(background_x+background_rect.width, background_y))
	screen.blit(background,(background_x+background_rect.width, background_y+background_rect.height))
	screen.blit(background,(background_x+background_rect.width, background_y-background_rect.height))
	screen.blit(background,(background_x-background_rect.width, background_y-background_rect.height))
	screen.blit(background,(background_x-background_rect.width, background_y+background_rect.height))

	#Déplacement
	if idd == 0 or 1:
		coordonne  = pygame.mouse.get_pos()
		vitesse  = DEPLACEMENT-joueur.ralentissement
		diff_x = coordonne[0]- TAILLE_SCREEN_X//2
		diff_y = coordonne[1]- TAILLE_SCREEN_Y//2

		lock_x_y.acquire()
		mouvement_x = round((diff_x/(TAILLE_SCREEN_X//2)) * vitesse)
		x = int(x+mouvement_x)
		background_x -= mouvement_x

		if x < -TAILLE_MAX_X-(TAILLE_SCREEN_X//2): 
			x = TAILLE_MAX_X
			background_x = background_rect.width
		elif x > TAILLE_MAX_X+(TAILLE_SCREEN_X//2):
				x = -TAILLE_MAX_X-(TAILLE_SCREEN_X//2)
				background_x = 0

		mouvement_y = round((diff_y/(TAILLE_SCREEN_Y//2)) * vitesse,2)
		y = int(y+mouvement_y)
		background_y -= mouvement_y
		if y < -TAILLE_MAX_Y-(TAILLE_SCREEN_Y//2): 
			y = TAILLE_MAX_Y
			background_y = background_rect.height
		elif y > TAILLE_MAX_Y+(TAILLE_SCREEN_Y//2):
				y = -TAILLE_MAX_Y-(TAILLE_SCREEN_Y//2)
				background_y = 0

		lock_x_y.release()
	



	#Affichage BOUFFE
	lock_dict_bouffe.acquire()

	for coos in dict_bouffe:

		if coos[0] >= x-TAILLE_SCREEN_X-DIAMETRE_BOUFFE and coos[0] <= x+TAILLE_SCREEN_X+DIAMETRE_BOUFFE and coos[1] >= y-TAILLE_SCREEN_Y-DIAMETRE_BOUFFE and coos[1] <= y+TAILLE_SCREEN_Y+DIAMETRE_BOUFFE:
			
			rel_x = coos[0]-x
			rel_y = coos[1]-y

			rel_x =  coos[0]-(x-TAILLE_SCREEN_X)-(TAILLE_SCREEN_X//2)-(DIAMETRE_BOUFFE//2) 
			rel_y =  coos[1]-(y-TAILLE_SCREEN_Y)-(TAILLE_SCREEN_Y//2)-(DIAMETRE_BOUFFE//2)
			
			if joueur.cercle_rect.collidepoint(rel_x,rel_y): 
				lock_score.acquire()
				score+=1
				lock_score.release()
				#Envoie de l'info au serveur
				if running:
					lock_s.acquire()
					client.envoie_sans_reponse(s,f"FOOD:{coos[0]},{coos[1]}|")
					lock_s.release()
					
				


				#Changer taille
				
				if joueur.taille != int(round(3*sqrt(score + 169),0)):
					lock_joueur.acquire()
					joueur = Player(idd,taille = joueur.taille,team = joueur.team)
					joueur.taille = int(round(3*sqrt(score + 169),0))
					if joueur.taille > 400:
						joueur.taille = 400
					joueur.cercle_rect.w = (joueur.taille)//sqrt(2)
					joueur.cercle_rect.h = (joueur.taille)//sqrt(2)
												
					joueur.cercle = pygame.transform.scale(joueur.cercle,(joueur.taille,joueur.taille))
					lock_joueur.release()
				
				
				#Changer vitesse
				lock_joueur.acquire()
				if round(0.15*sqrt(score),3) != joueur.ralentissement:
					joueur.ralentissement = round(0.15*sqrt(score),3)
					if joueur.ralentissement > 4:
						joueur.ralentissement = 4

				lock_joueur.release()
				
				
			else:
				

				dict_bouffe[coos].cercle_rect.x = rel_x
				dict_bouffe[coos].cercle_rect.y = rel_y
					
				screen.blit(dict_bouffe[coos].cercle,dict_bouffe[coos].cercle_rect)
			

	lock_dict_bouffe.release()

	#Affichage BADGUYS
	for id_bg in dict_badguys:
		if dict_badguys[id_bg].x != '':
			if dict_badguys[id_bg].x >= x-TAILLE_SCREEN_X-dict_badguys[id_bg].taille and dict_badguys[id_bg].x <= x+TAILLE_SCREEN_X+dict_badguys[id_bg].taille and dict_badguys[id_bg].y >= y-TAILLE_SCREEN_Y-dict_badguys[id_bg].taille and dict_badguys[id_bg].y <= y+TAILLE_SCREEN_Y+dict_badguys[id_bg].taille:
				
				rel_x =  dict_badguys[id_bg].x-(x-TAILLE_SCREEN_X)-(TAILLE_SCREEN_X//2)-(dict_badguys[id_bg].taille//2)
				rel_y =  dict_badguys[id_bg].y-(y-TAILLE_SCREEN_Y)-(TAILLE_SCREEN_Y//2)-(dict_badguys[id_bg].taille//2)

				if joueur.cercle_rect.collidepoint(rel_x,rel_y) and joueur.taille > dict_badguys[id_bg].taille: 
					dist_spaw = sqrt((dict_badguys[id_bg].x - 0)**2 + (dict_badguys[id_bg].y - 0)**2)
					if dist_spaw > 100:

						score += int(round(((dict_badguys[id_bg].taille/3)**2)-169,0))

						joueur.taille = int(round(3*sqrt(score + 169),0))
						if joueur.taille > 400:
							joueur.taille = 400

						joueur = Player(idd,taille = joueur.taille, team = joueur.team)
						joueur.cercle_rect.w = (joueur.taille)//sqrt(2)
						joueur.cercle_rect.h = (joueur.taille)//sqrt(2)
						
						joueur.cercle = pygame.transform.scale(joueur.cercle,(joueur.taille,joueur.taille))

						#Changer vitesse

						joueur.ralentissement = round(0.15*sqrt(score),3)
						if joueur.ralentissement > 4:
							joueur.ralentissement = 4
						lock_s.acquire()
						if parse(client.envoie(s, f'KILL:{id_bg}|')[:-1]) != True:
							print("Pb KILL")
						lock_s.release()


				#Changement de taille
				
				if dict_badguys[id_bg].taille != cache_bg[id_bg]:
					dict_badguys[id_bg] = Player(id_bg,dict_badguys[id_bg].taille,dict_badguys[id_bg].team,x = dict_badguys[id_bg].x, y = dict_badguys[id_bg].y)
					dict_badguys[id_bg].cercle_rect.w = dict_badguys[id_bg].taille//sqrt(2)
					dict_badguys[id_bg].cercle_rect.h = dict_badguys[id_bg].taille//sqrt(2)
					dict_badguys[id_bg].cercle = pygame.transform.scale(dict_badguys[id_bg].cercle,(dict_badguys[id_bg].taille,dict_badguys[id_bg].taille))

					cache_bg[id_bg] = dict_badguys[id_bg].taille

				
				dict_badguys[id_bg].cercle_rect.x = rel_x
				dict_badguys[id_bg].cercle_rect.y = rel_y
				screen.blit(dict_badguys[id_bg].cercle, dict_badguys[id_bg].cercle_rect)




	#Affichage FLAG + SCOREBOARD
	duree_flag = time.time()
	lock_dict_flags.acquire()
	a_maj = [dict_flags[i] for i in dict_flags]
	lock_dict_flags.release()
	barre_score.maj(a_maj)

	lock_dict_flags.acquire()
	
	for f_id in dict_flags:
		flag = dict_flags[f_id]
		if flag.x >= x-TAILLE_SCREEN_X-flag.flag_rect.width and flag.x <= x+TAILLE_SCREEN_X+flag.flag_rect.width and flag.y >= y-TAILLE_SCREEN_Y-flag.flag_rect.height and flag.y <= y+TAILLE_SCREEN_Y+flag.flag_rect.height:
			rel_x =  flag.x-(x-TAILLE_SCREEN_X)-(TAILLE_SCREEN_X//2)-(flag.flag_rect.width//2)
			rel_y = flag.y-(y-TAILLE_SCREEN_Y)-(TAILLE_SCREEN_Y//2)-(flag.flag_rect.height//2)

			flag.flag_rect.x = rel_x
			flag.flag_rect.y = rel_y
			if flag.rouge != cache_flag[f_id][0] or flag.bleu != cache_flag[f_id][1]:

				if flag.rouge > flag.bleu and flag.modele != 'rouge':
					flag.flag = pygame.image.load(f'{f_id}_flag_rouge.png')
					flag.modele = 'rouge'
				elif flag.rouge == 0 and flag.bleu == 0 and flag.modele != 'gris':
					flag.flag = pygame.image.load(f'{f_id}_flag_gris.png')
					flag.modele = 'gris'
				elif flag.bleu > flag.rouge and flag.modele != 'bleu':
					flag.flag = pygame.image.load(f'{f_id}_flag_bleu.png')
					flag.modele = 'bleu'

				cache_flag[f_id] = (flag.rouge,flag.bleu)
			screen.blit(flag.flag,flag.flag_rect)
	#print("duree flag ->",time.time()-start)
	lock_dict_flags.release()


	#Recentre le joueur sur l'écran 
	lock_joueur.acquire()
	hitbox = joueur.cercle.get_rect()
	joueur.cercle_rect.centerx = TAILLE_SCREEN_X//2
	joueur.cercle_rect.centery = TAILLE_SCREEN_Y// 2
	hitbox.center = (joueur.cercle_rect.centerx, joueur.cercle_rect.centery) 
	lock_joueur.release()
	
	#Mise à jour des coordonnées et du score
	affichage_coos = font.render(f'{round(x,0)},{round(y,0)}', True,(255,255,255))
	affichage_score = font.render(f'{score}', True,(255,255,255))
	affichage_taille = font.render(f'{joueur.taille}', True,(255,255,255))

	#Mise en page des élèments sur le screen
	screen.blit(joueur.cercle,hitbox)
	screen.blit(affichage_coos, (20, 20))
	screen.blit(affichage_score, (40, 40))
	screen.blit(affichage_taille, (40, 60))

	barre_score.afficher_score()
	pygame.display.update()
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			lock_s.acquire()
			client.close('vol')
			lock_s.release()
		
	
	itera += 1
	duree += time.time()-start


	diff = time.time() - start
	#print('diff ->',diff)
	if diff < 0.02:
		time.sleep(0.02-diff)
	else:
		pass

print("Moyenne ->",duree/itera)

pygame.quit()



