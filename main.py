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
	
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
#                                  MAIN LOOP                             |
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
init()
while 1:
	# USER INPUT
	deltat = clock.tick(50)
	
	# Check user input
	for event in pygame.event.get():
		if event.type is pygame.QUIT: sys.exit()
		if hasattr(event, 'key'):
			if event.key is K_ESCAPE: 
				if event.type is pygame.KEYDOWN: sys.exit()
			if event.key is K_a:
				if event.type is pygame.KEYDOWN: background.rect[0] -= 1
			if event.key is K_d:
				if event.type is pygame.KEYDOWN: background.rect[0] += 1
				
	
	screen.blit(background.image, background.rect)
						
	pygame.display.flip()