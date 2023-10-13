# Cell Crusade
Jeu inspiré du jeu Agar.io permettant de jouer sur un réseaux local (2022-2023)

## Règles du jeu

*Inspiré du jeu Agar.io*

Ce jeu se joue en équipe.

Il y a deux équipes tirées aléatoirement (rouge et bleu) de tailles égales.

Sur le terrain de jeu il y a trois zones.

La première équipe à capturer les trois zones a gagné.

Pour faire progresser la barre de capture de la zone, il suffit qu'un membre de l'équipe se trouve dedans, mais si un membre de l'équipe adverse s'y rends, votre barre de capture va baisser et la sienne commencera à se remplir.

Tout comme dans Agar.io, des particules de nourriture se trouvent sur le terrain, les consommer vous fera grandir et vous rendra moins vulnérable aux adversaires, cependant, cela aura également pour effet de faire baisser votre vitesse.

Vous pouvez également absorber les adversaires plus petits que vous, ce qui aura pour effet de vous faire grandir et de les renvoyer au spawn avec leur taille de départ.

## Informations techniques
Programmé avec Python 3

Modules : socket, pygame, time, math, threading, random

Le serveur écouter automatiquement sur le port 8080, modifiable dans le fichier `server_multi.py`

Le client se connecte autmoatiquement sur le port 8080, modifiable dans le fichier `cell_crusade_ctf.py`

## Crédits
Codé en projet de NSI avec [@Pedalo](https://github.com/pedalo) 


