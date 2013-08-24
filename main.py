""" 
LUDUM DARE 27 ENTRY
8/23/2013 - 8/26/2013
THEME: 10 Seconds
BY: Thomas Steinke, Elliot Fiske, Eli Backer

May be uploaded to http://thomassteinke.net
or another domain later, if decided.

Bring it on, LD.

"""

# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
#                      INITIALIZE CLASSES AND GAME                       |
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
exec(open('init.py'))
exec(open('ui_class.py'))

pygame.display.flip()

def init():
	global font				# Font
	global background		# Sprites
	global Popup_sprite,Modify_sprite	# RenderPlains
	global Import_sprite,interface		# RenderPlains
	global background			# RenderPlains
	global State,Modify,needInit,popup	# Global Variables
	global timer,client,SERVER		# Global Variables

	font = pygame.font.Font("fonts/ka1.ttf", 30)
	
	background = Back("background")
	
	raw_input()
	
init()